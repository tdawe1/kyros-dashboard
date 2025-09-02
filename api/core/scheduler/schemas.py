"""
Pydantic schemas for the scheduler API.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator, field_validator
from enum import Enum
import uuid


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

    tool: str = Field(..., description="Tool name (e.g., 'repurposer', 'translator')")
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

    @validator("tool")
    def validate_tool(cls, v):
        """Validate that the tool exists in the registry."""
        from tools.registry import is_tool_enabled

        if not is_tool_enabled(v):
            raise ValueError(f"Tool '{v}' is not available or enabled")
        return v

    @validator("recurrence")
    def validate_recurrence(cls, v):
        """Validate recurrence pattern."""
        if v is None:
            return v

        valid_patterns = ["daily", "weekly", "monthly"]
        if v not in valid_patterns and not v.startswith("cron:"):
            raise ValueError(
                f"Invalid recurrence pattern. Must be one of {valid_patterns} or start with 'cron:'"
            )
        return v


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

    @validator("recurrence")
    def validate_recurrence(cls, v):
        """Validate recurrence pattern."""
        if v is None:
            return v

        valid_patterns = ["daily", "weekly", "monthly"]
        if v not in valid_patterns and not v.startswith("cron:"):
            raise ValueError(
                f"Invalid recurrence pattern. Must be one of {valid_patterns} or start with 'cron:'"
            )
        return v


class RunNowRequest(BaseModel):
    """Request schema for running a job immediately."""

    idempotency_key: Optional[str] = Field(
        None, description="Idempotency key to prevent duplicates"
    )


# Response schemas
class CreateScheduleResponse(BaseModel):
    """Response schema for creating a scheduled job."""

    scheduled_job_id: str
    next_run_at: Optional[datetime]
    status: str
    message: str


class ScheduledJobResponse(BaseModel):
    """Response schema for a scheduled job."""

    id: str
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

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if isinstance(v, uuid.UUID):
            return str(v)
        return v


class JobRunResponse(BaseModel):
    """Response schema for a job run."""

    id: str
    scheduled_job_id: str
    status: str
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    run_payload: Optional[Dict[str, Any]]
    run_result: Optional[Dict[str, Any]]
    token_usage: Optional[int]
    error: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("id", "scheduled_job_id", mode="before")
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if isinstance(v, uuid.UUID):
            return str(v)
        return v


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

    run_id: str
    status: str
    message: str
    estimated_completion: Optional[datetime]


# Error schemas
class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
