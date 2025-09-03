"""
Business logic service for the scheduler system.
"""

from datetime import datetime, timedelta, timezone
import calendar
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, case
from uuid import UUID

from .models import ScheduledJob, JobRun, IdempotencyKey
from .schemas import (
    CreateScheduleRequest,
    UpdateScheduleRequest,
    JobStatus,
    RunStatus,
    ScheduledJobResponse,
    JobRunResponse,
    ScheduleDetailResponse,
)
from tools.registry import is_tool_enabled
from utils.token_utils import validate_input_limits
from utils.quotas import can_create_job


class SchedulerService:
    """Service class for scheduler operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_scheduled_job(
        self, user_id: str, request: CreateScheduleRequest
    ) -> Tuple[ScheduledJob, Optional[str]]:
        """
        Create a new scheduled job.

        Returns:
            Tuple of (ScheduledJob, error_message)
        """
        # Check idempotency key if provided
        if request.idempotency_key:
            existing_key = (
                self.db.query(IdempotencyKey)
                .filter(IdempotencyKey.key == request.idempotency_key)
                .first()
            )
            if existing_key:
                # Find the existing job created with this idempotency key
                existing_job = (
                    self.db.query(ScheduledJob)
                    .filter(
                        and_(
                            ScheduledJob.owner_user_id == user_id,
                            func.json_extract(ScheduledJob.options, "$.idempotency_key")
                            == request.idempotency_key,
                        )
                    )
                    .first()
                )
                if existing_job:
                    return existing_job, None
                else:
                    return None, "Job with this idempotency key already exists"

        # Validate tool exists
        if not is_tool_enabled(request.tool):
            return None, f"Tool '{request.tool}' is not available"

        # Validate input limits if input_source contains text
        if isinstance(request.input_source, dict) and "text" in request.input_source:
            validation_result = validate_input_limits(request.input_source["text"])
            if not validation_result["valid"]:
                return (
                    None,
                    f"Input validation failed: {'; '.join(validation_result['errors'])}",
                )

        # Check user quota
        daily_limit = 10  # TODO: Get from config
        can_create, current_count = can_create_job(user_id, daily_limit)
        if not can_create:
            return (
                None,
                f"Daily quota exceeded. Current count: {current_count}/{daily_limit}",
            )

        # Calculate next run time
        next_run_at = None
        if request.run_at:
            next_run_at = request.run_at
        elif request.recurrence and request.recurrence != "none":
            next_run_at = self._calculate_next_run_time(
                request.recurrence, request.timezone
            )

        # Create the scheduled job
        options = request.options or {}
        if request.idempotency_key:
            options["idempotency_key"] = request.idempotency_key

        job = ScheduledJob(
            tool=request.tool,
            name=request.name,
            owner_user_id=user_id,
            input_source=request.input_source,
            options=options,
            next_run_at=next_run_at,
            timezone=request.timezone,
            recurrence=request.recurrence,
            status=JobStatus.ACTIVE.value,
            max_runs=request.max_runs,
        )

        self.db.add(job)
        self.db.flush()  # Get the ID

        # Store idempotency key if provided
        if request.idempotency_key:
            idempotency_key = IdempotencyKey(
                owner_user_id=user_id, key=request.idempotency_key
            )
            self.db.add(idempotency_key)

        self.db.commit()
        return job, None

    def get_scheduled_jobs(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
    ) -> Tuple[List[ScheduledJob], int]:
        """Get paginated list of scheduled jobs for a user."""
        query = self.db.query(ScheduledJob).filter(
            ScheduledJob.owner_user_id == user_id
        )

        if status:
            query = query.filter(ScheduledJob.status == status)

        total = query.count()
        jobs = (
            query.order_by(desc(ScheduledJob.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return jobs, total

    def get_scheduled_job(self, job_id: UUID, user_id: str) -> Optional[ScheduledJob]:
        """Get a specific scheduled job."""
        return (
            self.db.query(ScheduledJob)
            .filter(
                and_(ScheduledJob.id == job_id, ScheduledJob.owner_user_id == user_id)
            )
            .first()
        )

    def update_scheduled_job(
        self, job_id: UUID, user_id: str, request: UpdateScheduleRequest
    ) -> Tuple[Optional[ScheduledJob], Optional[str]]:
        """Update a scheduled job."""
        job = self.get_scheduled_job(job_id, user_id)
        if not job:
            return None, "Job not found"

        # Update fields
        if request.name is not None:
            job.name = request.name
        if request.input_source is not None:
            job.input_source = request.input_source
        if request.options is not None:
            job.options = request.options
        if request.timezone is not None:
            job.timezone = request.timezone
        if request.next_run_at is not None:
            job.next_run_at = request.next_run_at
        if request.recurrence is not None:
            job.recurrence = request.recurrence
            # Recalculate next run time if recurrence changed
            if request.recurrence != "none":
                job.next_run_at = self._calculate_next_run_time(
                    request.recurrence, job.timezone
                )
        if request.status is not None:
            job.status = request.status.value
        if request.max_runs is not None:
            job.max_runs = request.max_runs

        job.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        return job, None

    def delete_scheduled_job(self, job_id: UUID, user_id: str) -> bool:
        """Delete a scheduled job."""
        job = self.get_scheduled_job(job_id, user_id)
        if not job:
            return False

        self.db.delete(job)
        self.db.commit()
        return True

    def run_job_now(
        self, job_id: UUID, user_id: str, idempotency_key: Optional[str] = None
    ) -> Tuple[Optional[JobRun], Optional[str]]:
        """Run a scheduled job immediately."""
        job = self.get_scheduled_job(job_id, user_id)
        if not job:
            return None, "Job not found"

        if job.status != JobStatus.ACTIVE.value:
            return None, "Job is not active"

        # Check idempotency key if provided
        if idempotency_key:
            existing_run = (
                self.db.query(JobRun)
                .join(ScheduledJob)
                .filter(
                    and_(
                        ScheduledJob.id == job_id,
                        func.json_extract(JobRun.run_payload, "$.idempotency_key")
                        == idempotency_key,
                    )
                )
                .first()
            )
            if existing_run:
                return existing_run, None

        # Create job run record
        run = JobRun(
            scheduled_job_id=job.id,
            status=RunStatus.QUEUED.value,
            run_payload={
                "input_source": job.input_source,
                "options": job.options,
                "idempotency_key": idempotency_key,
            },
        )

        self.db.add(run)
        self.db.commit()

        # TODO: Queue the job for execution via Celery
        # This will be implemented when we add Celery integration

        return run, None

    def get_job_runs(
        self, job_id: UUID, user_id: str, page: int = 1, page_size: int = 20
    ) -> Tuple[List[JobRun], int]:
        """Get paginated list of job runs."""
        query = (
            self.db.query(JobRun)
            .join(ScheduledJob)
            .filter(
                and_(ScheduledJob.id == job_id, ScheduledJob.owner_user_id == user_id)
            )
        )

        total = query.count()
        runs = (
            query.order_by(desc(JobRun.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return runs, total

    def get_schedule_detail(
        self, job_id: UUID, user_id: str
    ) -> Optional[ScheduleDetailResponse]:
        """Get detailed information about a scheduled job."""
        job = self.get_scheduled_job(job_id, user_id)
        if not job:
            return None

        # Get recent runs (last 10)
        recent_runs, _ = self.get_job_runs(job_id, user_id, page=1, page_size=10)

        # Get run statistics
        run_stats = (
            self.db.query(
                func.count(JobRun.id).label("total_runs"),
                func.sum(
                    case((JobRun.status == RunStatus.SUCCESS.value, 1), else_=0)
                ).label("successful_runs"),
                func.sum(
                    case((JobRun.status == RunStatus.FAILED.value, 1), else_=0)
                ).label("failed_runs"),
                func.sum(JobRun.token_usage).label("total_tokens"),
            )
            .join(ScheduledJob)
            .filter(
                and_(ScheduledJob.id == job_id, ScheduledJob.owner_user_id == user_id)
            )
            .first()
        )

        return ScheduleDetailResponse(
            job=ScheduledJobResponse.model_validate(job),
            recent_runs=[JobRunResponse.model_validate(run) for run in recent_runs],
            total_runs=run_stats.total_runs or 0,
            successful_runs=run_stats.successful_runs or 0,
            failed_runs=run_stats.failed_runs or 0,
            total_tokens_used=run_stats.total_tokens or 0,
        )

    def get_job_run(self, job_id: UUID, run_id: UUID, user_id: str) -> Optional[JobRun]:
        """
        Get a specific job run for a user's job.

        Args:
            job_id: The scheduled job ID
            run_id: The job run ID
            user_id: The user ID

        Returns:
            JobRun if found and belongs to user, None otherwise
        """
        return (
            self.db.query(JobRun)
            .join(ScheduledJob)
            .filter(
                and_(
                    JobRun.id == run_id,
                    JobRun.scheduled_job_id == job_id,
                    ScheduledJob.owner_user_id == user_id,
                )
            )
            .first()
        )

    def _calculate_next_run_time(self, recurrence: str, user_timezone: str) -> datetime:
        """Calculate the next run time based on recurrence pattern."""
        now = datetime.now(timezone.utc)

        if recurrence == "daily":
            return now + timedelta(days=1)
        elif recurrence == "weekly":
            return now + timedelta(weeks=1)
        elif recurrence == "monthly":
            # Proper monthly calculation - add one month
            year = now.year
            month = now.month
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1

            # Handle cases where the day doesn't exist in the next month (e.g., Jan 31 -> Feb 31)
            try:
                next_month = now.replace(year=year, month=month)
            except ValueError:
                # Day doesn't exist in next month, use last day of month
                last_day = calendar.monthrange(year, month)[1]
                next_month = now.replace(year=year, month=month, day=last_day)

            return next_month
        elif recurrence.startswith("cron:"):
            # Basic cron parsing - for now just extract common patterns
            cron_expr = recurrence[5:].strip()
            if cron_expr == "0 9 * * *":  # Daily at 9 AM
                next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
                return next_run
            elif cron_expr == "0 9 * * 1":  # Weekly on Monday at 9 AM
                days_ahead = 0 - now.weekday()  # Monday is 0
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                next_run = now + timedelta(days=days_ahead)
                next_run = next_run.replace(hour=9, minute=0, second=0, microsecond=0)
                return next_run
            else:
                # For complex cron expressions, default to daily for now
                return now + timedelta(days=1)
        else:
            return now + timedelta(days=1)
