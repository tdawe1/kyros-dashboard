"""
Pydantic schemas for the scheduler API.
"""

import re
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from uuid import UUID


def validate_cron_expression(cron_expr: str) -> bool:
    """
    Validate a cron expression format.

    Args:
        cron_expr: The cron expression to validate

    Returns:
        True if valid, False otherwise
    """
    # Remove 'cron:' prefix if present
    if cron_expr.startswith("cron:"):
        cron_expr = cron_expr[5:]

    # Split into 5 parts (minute, hour, day, month, weekday)
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        return False

    # Basic validation for each part
    for part in parts:
        if not re.match(r"^[\d\*\/\-\,]+$", part):
            return False

        # Check for valid ranges
        if "*" in part and len(part) > 1:
            return False

        # Check for valid numbers and ranges
        if part != "*":
            for subpart in part.split(","):
                if "/" in subpart:
                    range_part, step = subpart.split("/", 1)
                    if not step.isdigit():
                        return False
                    if range_part != "*" and "-" in range_part:
                        start, end = range_part.split("-", 1)
                        if not (start.isdigit() and end.isdigit()):
                            return False
                elif "-" in subpart:
                    start, end = subpart.split("-", 1)
                    if not (start.isdigit() and end.isdigit()):
                        return False
                elif not subpart.isdigit():
                    return False

    return True


class JobStatus(str, Enum):
    """Job status enumeration."""

    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class RunStatus(str, Enum):
    """Job run status enumeration."""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class RecurrenceType(str, Enum):
    """Recurrence type enumeration."""

    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"  # For cron expressions


# Request schemas
class CreateScheduleRequest(BaseModel):
    """Request schema for creating a scheduled job."""

    tool: str = Field(..., description="Tool name (e.g., 'hello', 'translator')")
    name: Optional[str] = Field(None, description="Human-readable name for the job")
    input_source: Dict[str, Any] = Field(..., description="Input data or URL reference")
    options: Optional[Dict[str, Any]] = Field(None, description="Tool-specific options")
    timezone: str = Field("UTC", description="Timezone for scheduling")
    run_at: Optional[datetime] = Field(
        None, description="When to run the job (for one-time jobs)"
    )
    recurrence: Optional[str] = Field(
        None, description="Recurrence pattern (daily, weekly, monthly, or cron)"
    )
    max_runs: Optional[int] = Field(
        None, description="Maximum number of runs (optional)"
    )
    idempotency_key: Optional[str] = Field(
        None, description="Idempotency key to prevent duplicates"
    )

    @field_validator("tool")
    def validate_tool(cls, v):
        """Validate that the tool exists in the registry."""
        from tools.registry import is_tool_enabled

        if not is_tool_enabled(v):
            raise ValueError(f"Tool '{v}' is not available or enabled")
        return v

    @field_validator("recurrence")
    def validate_recurrence(cls, v):
        """Validate recurrence pattern."""
        if v is None:
            return v

        valid_patterns = ["daily", "weekly", "monthly"]
        if v in valid_patterns:
            return v

        if v.startswith("cron:"):
            if not validate_cron_expression(v):
                raise ValueError("Invalid cron expression format")
            return v

        raise ValueError(
            f"Invalid recurrence pattern. Must be one of {valid_patterns} or a valid cron expression starting with 'cron:'"
        )


class UpdateScheduleRequest(BaseModel):
    """Request schema for updating a scheduled job."""

    name: Optional[str] = None
    input_source: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = None
    next_run_at: Optional[datetime] = None
    recurrence: Optional[str] = None
    status: Optional[JobStatus] = None
    max_runs: Optional[int] = None

    @field_validator("recurrence")
    def validate_recurrence(cls, v):
        """Validate recurrence pattern."""
        if v is None:
            return v

        valid_patterns = ["daily", "weekly", "monthly"]
        if v in valid_patterns:
            return v

        if v.startswith("cron:"):
            if not validate_cron_expression(v):
                raise ValueError("Invalid cron expression format")
            return v

        raise ValueError(
            f"Invalid recurrence pattern. Must be one of {valid_patterns} or a valid cron expression starting with 'cron:'"
        )


class RunNowRequest(BaseModel):
    """Request schema for running a job immediately."""

    idempotency_key: Optional[str] = Field(
        None, description="Idempotency key to prevent duplicates"
    )


# Response schemas
class CreateScheduleResponse(BaseModel):
    """Response schema for creating a scheduled job."""

    scheduled_job_id: UUID
    next_run_at: Optional[datetime]
    status: str
    message: str


class ScheduledJobResponse(BaseModel):
    """Response schema for a scheduled job."""

    id: UUID
    tool: str
    name: Optional[str]
    owner_user_id: Optional[str]
    input_source: Dict[str, Any]
    options: Optional[Dict[str, Any]]
    next_run_at: Optional[datetime]
    timezone: str
    recurrence: Optional[str]
    status: str
    max_runs: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobRunResponse(BaseModel):
    """Response schema for a job run."""

    id: UUID
    scheduled_job_id: UUID
    status: str
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    run_payload: Optional[Dict[str, Any]]
    run_result: Optional[Dict[str, Any]]
    token_usage: Optional[int]
    error: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ScheduleListResponse(BaseModel):
    """Response schema for listing scheduled jobs."""

    jobs: List[ScheduledJobResponse]
    total: int
    page: int
    page_size: int


class JobRunsListResponse(BaseModel):
    """Response schema for listing job runs."""

    runs: List[JobRunResponse]
    total: int
    page: int
    page_size: int


class ScheduleDetailResponse(BaseModel):
    """Response schema for detailed job information."""

    job: ScheduledJobResponse
    recent_runs: List[JobRunResponse]
    total_runs: int
    successful_runs: int
    failed_runs: int
    total_tokens_used: int


class RunNowResponse(BaseModel):
    """Response schema for running a job immediately."""

    run_id: UUID
    status: str
    message: str
    estimated_completion: Optional[datetime]


# Error schemas
class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
