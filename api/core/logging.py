"""
Centralized Logging Service

This module provides standardized logging across all tools and services.
It includes Sentry integration, structured logging, and job tracking.
"""

import os
import logging
from typing import Dict, Any, Optional
import sentry_sdk

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


class JobLogger:
    """
    Centralized job logging with Sentry integration.
    """

    def __init__(self):
        self.sentry_dsn = os.getenv("SENTRY_DSN")
        if self.sentry_dsn:
            self._init_sentry()

    def _init_sentry(self):
        """Initialize Sentry with proper configuration."""
        sentry_sdk.init(
            dsn=self.sentry_dsn,
            traces_sample_rate=0.1,
            environment=os.getenv("ENVIRONMENT", "development"),
            release=os.getenv("RELEASE_VERSION", "1.0.0"),
        )
        logger.info("Sentry initialized successfully")

    def log_job_start(
        self,
        job_id: str,
        tool_name: str,
        user_id: str,
        job_details: Dict[str, Any],
    ):
        """
        Log the start of a job.

        Args:
            job_id: Unique job identifier.
            tool_name: Name of the tool processing the job.
            user_id: User ID who initiated the job.
            job_details: Additional job details.
        """
        logger.info(
            f"Job started: {job_id} | Tool: {tool_name} | User: {user_id}",
            extra={
                "job_id": job_id,
                "tool_name": tool_name,
                "user_id": user_id,
                "job_details": job_details,
                "event_type": "job_start",
            },
        )

        # Set Sentry context
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("job_id", job_id)
            scope.set_tag("tool_name", tool_name)
            scope.set_tag("user_id", user_id)
            scope.set_context("job_details", job_details)

    def log_job_success(
        self,
        job_id: str,
        tool_name: str,
        user_id: str,
        result_summary: Dict[str, Any],
    ):
        """
        Log successful job completion.

        Args:
            job_id: Unique job identifier.
            tool_name: Name of the tool that processed the job.
            user_id: User ID who initiated the job.
            result_summary: Summary of the job results.
        """
        logger.info(
            f"Job completed successfully: {job_id} | Tool: {tool_name} | User: {user_id}",
            extra={
                "job_id": job_id,
                "tool_name": tool_name,
                "user_id": user_id,
                "result_summary": result_summary,
                "event_type": "job_success",
            },
        )

    def log_job_error(
        self,
        job_id: str,
        tool_name: str,
        user_id: str,
        error: Exception,
        error_context: Optional[Dict[str, Any]] = None,
    ):
        """
        Log job error with full context.

        Args:
            job_id: Unique job identifier.
            tool_name: Name of the tool that encountered the error.
            user_id: User ID who initiated the job.
            error: The exception that occurred.
            error_context: Additional context about the error.
        """
        error_msg = f"Job failed: {job_id} | Tool: {tool_name} | User: {user_id} | Error: {str(error)}"
        logger.error(
            error_msg,
            extra={
                "job_id": job_id,
                "tool_name": tool_name,
                "user_id": user_id,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "error_context": error_context or {},
                "event_type": "job_error",
            },
        )

        # Capture in Sentry
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("job_id", job_id)
            scope.set_tag("tool_name", tool_name)
            scope.set_tag("user_id", user_id)
            scope.set_tag("error_type", type(error).__name__)
            if error_context:
                scope.set_context("error_context", error_context)

        sentry_sdk.capture_exception(error)

    def log_tool_usage(
        self,
        tool_name: str,
        user_id: str,
        usage_stats: Dict[str, Any],
    ):
        """
        Log tool usage statistics.

        Args:
            tool_name: Name of the tool.
            user_id: User ID.
            usage_stats: Usage statistics (tokens, cost, etc.).
        """
        logger.info(
            f"Tool usage: {tool_name} | User: {user_id}",
            extra={
                "tool_name": tool_name,
                "user_id": user_id,
                "usage_stats": usage_stats,
                "event_type": "tool_usage",
            },
        )


class StructuredLogger:
    """
    Structured logging for consistent log format across services.
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def info(self, message: str, **kwargs):
        """Log info message with structured data."""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with structured data."""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with structured data."""
        self.logger.error(message, extra=kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message with structured data."""
        self.logger.debug(message, extra=kwargs)


def get_job_logger() -> JobLogger:
    """
    Get the global job logger instance.

    Returns:
        JobLogger instance.
    """
    global _job_logger
    if "_job_logger" not in globals():
        _job_logger = JobLogger()
    return _job_logger


def get_structured_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger for a specific module.

    Args:
        name: Logger name (usually __name__).

    Returns:
        StructuredLogger instance.
    """
    return StructuredLogger(name)


def log_api_request(
    method: str,
    path: str,
    user_id: Optional[str] = None,
    tool_name: Optional[str] = None,
    response_time: Optional[float] = None,
    status_code: Optional[int] = None,
):
    """
    Log API request details.

    Args:
        method: HTTP method.
        path: Request path.
        user_id: User ID if available.
        tool_name: Tool name if available.
        response_time: Response time in seconds.
        status_code: HTTP status code.
    """
    logger.info(
        f"API Request: {method} {path}",
        extra={
            "method": method,
            "path": path,
            "user_id": user_id,
            "tool_name": tool_name,
            "response_time": response_time,
            "status_code": status_code,
            "event_type": "api_request",
        },
    )


def log_performance_metric(
    metric_name: str,
    value: float,
    unit: str = "ms",
    tool_name: Optional[str] = None,
    job_id: Optional[str] = None,
):
    """
    Log performance metrics.

    Args:
        metric_name: Name of the metric.
        value: Metric value.
        unit: Unit of measurement.
        tool_name: Tool name if applicable.
        job_id: Job ID if applicable.
    """
    logger.info(
        f"Performance metric: {metric_name} = {value} {unit}",
        extra={
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
            "tool_name": tool_name,
            "job_id": job_id,
            "event_type": "performance_metric",
        },
    )
