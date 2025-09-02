"""
Database models for the scheduler system.
"""

import uuid
from typing import Dict, Any
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Text,
    Integer,
    ForeignKey,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class ScheduledJob(Base):
    """
    Model for scheduled jobs.
    """

    __tablename__ = "scheduled_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool = Column(String(100), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    owner_user_id = Column(
        String(255), nullable=True, index=True
    )  # For multi-user support
    input_source = Column(JSON, nullable=False)  # Input data or URL reference
    options = Column(JSON, nullable=True)  # Tool-specific options
    next_run_at = Column(DateTime(timezone=True), nullable=True, index=True)
    timezone = Column(String(50), nullable=True, default="UTC")
    recurrence = Column(String(100), nullable=True)  # cron expression or simple pattern
    status = Column(String(20), nullable=False, default="active", index=True)
    max_runs = Column(Integer, nullable=True)  # Optional limit on number of runs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    runs = relationship(
        "JobRun", back_populates="scheduled_job", cascade="all, delete-orphan"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "tool": self.tool,
            "name": self.name,
            "owner_user_id": self.owner_user_id,
            "input_source": self.input_source,
            "options": self.options,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "timezone": self.timezone,
            "recurrence": self.recurrence,
            "status": self.status,
            "max_runs": self.max_runs,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class JobRun(Base):
    """
    Model for individual job runs.
    """

    __tablename__ = "job_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scheduled_job_id = Column(
        UUID(as_uuid=True),
        ForeignKey("scheduled_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(
        String(20), nullable=False, index=True
    )  # queued, running, success, failed
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    run_payload = Column(JSON, nullable=True)  # Input data used for this run
    run_result = Column(JSON, nullable=True)  # Output data from the run
    token_usage = Column(Integer, nullable=True)  # Token count for this run
    error = Column(Text, nullable=True)  # Error message if failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    scheduled_job = relationship("ScheduledJob", back_populates="runs")

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "scheduled_job_id": str(self.scheduled_job_id),
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "run_payload": self.run_payload,
            "run_result": self.run_result,
            "token_usage": self.token_usage,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class IdempotencyKey(Base):
    """
    Model for idempotency keys to prevent duplicate job creation.
    """

    __tablename__ = "idempotency_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(String(255), nullable=True, index=True)
    key = Column(String(255), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "owner_user_id": self.owner_user_id,
            "key": self.key,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
