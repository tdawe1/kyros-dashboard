"""
Scheduler module for Kyros Dashboard.

This module provides scheduling functionality for running tools at specified times
or on recurring schedules.
"""

from .router import router as scheduler_router
from .models import ScheduledJob, JobRun, IdempotencyKey
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
    JobStatus,
    RunStatus,
)

__all__ = [
    "scheduler_router",
    "ScheduledJob",
    "JobRun",
    "IdempotencyKey",
    "SchedulerService",
    "CreateScheduleRequest",
    "CreateScheduleResponse",
    "UpdateScheduleRequest",
    "ScheduledJobResponse",
    "ScheduleListResponse",
    "JobRunsListResponse",
    "ScheduleDetailResponse",
    "RunNowRequest",
    "RunNowResponse",
    "JobRunResponse",
    "JobStatus",
    "RunStatus",
]
