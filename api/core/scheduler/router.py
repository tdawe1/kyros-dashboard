"""
FastAPI router for the scheduler API endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .service import SchedulerService
from .schemas import (
    CreateScheduleRequest,
    CreateScheduleResponse,
    UpdateScheduleRequest,
    ScheduledJobResponse,
    ScheduleListResponse,
    JobRunsListResponse,
    ScheduleDetailResponse,
    RunNowRequest,
    RunNowResponse,
    JobRunResponse,
)
from .models import JobRun
from core.database import get_db

router = APIRouter()


def get_current_user() -> str:
    """
    Mock authentication - in a real app, this would extract user from JWT token.
    For now, we'll use a default user ID.
    """
    return "demo_user"  # TODO: Implement real authentication


@router.post("/", response_model=CreateScheduleResponse)
async def create_schedule(
    request: CreateScheduleRequest,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new scheduled job."""
    service = SchedulerService(db)
    job, error = service.create_scheduled_job(user_id, request)

    if error:
        raise HTTPException(status_code=400, detail=error)

    return CreateScheduleResponse(
        scheduled_job_id=str(job.id),
        next_run_at=job.next_run_at,
        status=job.status,
        message="Scheduled job created successfully",
    )


@router.get("/", response_model=ScheduleListResponse)
async def list_schedules(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    status: Optional[str] = Query(None, description="Filter by status"),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List scheduled jobs for the current user."""
    service = SchedulerService(db)
    jobs, total = service.get_scheduled_jobs(user_id, page, page_size, status)

    return ScheduleListResponse(
        jobs=[ScheduledJobResponse.model_validate(job) for job in jobs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{job_id}", response_model=ScheduleDetailResponse)
async def get_schedule_detail(
    job_id: str, user_id: str = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get detailed information about a scheduled job."""
    service = SchedulerService(db)
    detail = service.get_schedule_detail(job_id, user_id)

    if not detail:
        raise HTTPException(status_code=404, detail="Job not found")

    return detail


@router.patch("/{job_id}", response_model=ScheduledJobResponse)
async def update_schedule(
    job_id: str,
    request: UpdateScheduleRequest,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a scheduled job."""
    service = SchedulerService(db)
    job, error = service.update_scheduled_job(job_id, user_id, request)

    if error:
        raise HTTPException(status_code=400, detail=error)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return ScheduledJobResponse.model_validate(job)


@router.delete("/{job_id}")
async def delete_schedule(
    job_id: str, user_id: str = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Delete a scheduled job."""
    service = SchedulerService(db)
    success = service.delete_scheduled_job(job_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Job not found")

    return {"message": "Job deleted successfully"}


@router.post("/{job_id}/run-now", response_model=RunNowResponse)
async def run_job_now(
    job_id: str,
    request: RunNowRequest,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Run a scheduled job immediately."""
    service = SchedulerService(db)
    run, error = service.run_job_now(job_id, user_id, request.idempotency_key)

    if error:
        raise HTTPException(status_code=400, detail=error)

    if not run:
        raise HTTPException(status_code=404, detail="Job not found")

    return RunNowResponse(
        run_id=str(run.id),
        status=run.status,
        message="Job queued for immediate execution",
        estimated_completion=None,  # TODO: Calculate based on queue length
    )


@router.get("/{job_id}/runs", response_model=JobRunsListResponse)
async def list_job_runs(
    job_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List runs for a specific scheduled job."""
    service = SchedulerService(db)
    runs, total = service.get_job_runs(job_id, user_id, page, page_size)

    return JobRunsListResponse(
        runs=[JobRunResponse.model_validate(run) for run in runs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{job_id}/runs/{run_id}", response_model=JobRunResponse)
async def get_job_run(
    job_id: str,
    run_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get details of a specific job run."""
    service = SchedulerService(db)

    # Verify the job belongs to the user
    job = service.get_scheduled_job(job_id, user_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get the run
    run = (
        db.query(JobRun)
        .filter(and_(JobRun.id == run_id, JobRun.scheduled_job_id == job_id))
        .first()
    )

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return JobRunResponse.model_validate(run)
