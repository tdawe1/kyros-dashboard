"""
Core Services Module

This module provides shared services and utilities for all tools in the Kyros Dashboard.
It includes OpenAI client wrapper, logging, file handling, and other core functionality.
"""

from .openai_client import (
    OpenAIClient,
    OpenAIError,
    get_openai_client,
    create_openai_client,
    VALID_MODELS,
)
from .logging import (
    JobLogger,
    StructuredLogger,
    get_job_logger,
    get_structured_logger,
    log_api_request,
    log_performance_metric,
)
from .file_handlers import (
    FileHandler,
    FileHandlerError,
    FileHandlerManager,
    get_file_handler_manager,
    extract_text_from_file,
    get_file_info,
)

__all__ = [
    # OpenAI client
    "OpenAIClient",
    "OpenAIError",
    "get_openai_client",
    "create_openai_client",
    "VALID_MODELS",
    # Logging
    "JobLogger",
    "StructuredLogger",
    "get_job_logger",
    "get_structured_logger",
    "log_api_request",
    "log_performance_metric",
    # File handlers
    "FileHandler",
    "FileHandlerError",
    "FileHandlerManager",
    "get_file_handler_manager",
    "extract_text_from_file",
    "get_file_info",
]
