"""
Standardized error handling for Kyros Dashboard.
Implements consistent error responses and exception hierarchy.
"""

import logging
import os
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger(__name__)


class KyrosException(Exception):
    """Base exception for Kyros Dashboard."""

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(KyrosException):
    """Authentication related errors."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "AUTHENTICATION_ERROR", details)


class AuthorizationError(KyrosException):
    """Authorization related errors."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "AUTHORIZATION_ERROR", details)


class ValidationError(KyrosException):
    """Input validation errors."""

    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "VALIDATION_ERROR", details)


class QuotaExceededError(KyrosException):
    """Quota exceeded errors."""

    def __init__(
        self, message: str = "Quota exceeded", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "QUOTA_EXCEEDED", details)


class ExternalServiceError(KyrosException):
    """External service errors."""

    def __init__(
        self,
        message: str = "External service error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", details)


class DatabaseError(KyrosException):
    """Database related errors."""

    def __init__(
        self, message: str = "Database error", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "DATABASE_ERROR", details)


def create_error_response(
    error_code: str,
    message: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
) -> JSONResponse:
    """Create standardized error response."""

    error_response = {
        "error": {"code": error_code, "message": message, "details": details or {}},
        "timestamp": datetime.utcnow().isoformat(),
        "path": getattr(request.state, "request_path", None) if request else None,
        "request_id": getattr(request.state, "request_id", None) if request else None,
    }

    return JSONResponse(status_code=status_code, content=error_response)


def handle_kyros_exception(request: Request, exc: KyrosException) -> JSONResponse:
    """Handle Kyros-specific exceptions."""

    # Map error codes to HTTP status codes
    status_mapping = {
        "AUTHENTICATION_ERROR": status.HTTP_401_UNAUTHORIZED,
        "AUTHORIZATION_ERROR": status.HTTP_403_FORBIDDEN,
        "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
        "QUOTA_EXCEEDED": status.HTTP_429_TOO_MANY_REQUESTS,
        "EXTERNAL_SERVICE_ERROR": status.HTTP_502_BAD_GATEWAY,
        "DATABASE_ERROR": status.HTTP_503_SERVICE_UNAVAILABLE,
    }

    status_code = status_mapping.get(
        exc.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    logger.error(f"Kyros exception: {exc.error_code} - {exc.message}")

    return create_error_response(
        error_code=exc.error_code,
        message=exc.message,
        status_code=status_code,
        details=exc.details,
        request=request,
    )


def handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""

    logger.warning(f"Validation error: {exc.errors()}")

    # Format validation errors
    formatted_errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        formatted_errors.append(
            {"field": field, "message": error["msg"], "type": error["type"]}
        )

    return create_error_response(
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={"validation_errors": formatted_errors},
        request=request,
    )


def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""

    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")

    return create_error_response(
        error_code="HTTP_ERROR",
        message=str(exc.detail),
        status_code=exc.status_code,
        request=request,
    )


def handle_generic_exception(request: Request, exc: Exception) -> JSONResponse:
    """Handle generic exceptions."""

    logger.error(f"Unhandled exception: {type(exc).__name__} - {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")

    # Don't expose internal details in production
    # Use explicit config flag instead of logger level
    show_tracebacks = os.getenv("SHOW_ERROR_TRACEBACKS", "false").lower() == "true"
    if show_tracebacks:
        details = {"traceback": traceback.format_exc()}
    else:
        details = {}

    return create_error_response(
        error_code="INTERNAL_ERROR",
        message="An internal error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details=details,
        request=request,
    )


# Error response middleware
async def error_response_middleware(request: Request, call_next):
    """Middleware to add common fields to error responses."""
    # Store request info for error handlers
    request.state.request_path = str(request.url.path)
    request.state.request_timestamp = datetime.utcnow().isoformat()

    response = await call_next(request)
    return response


# Utility functions for common error scenarios
def raise_authentication_error(message: str = "Authentication required") -> None:
    """Raise authentication error."""
    raise AuthenticationError(message)


def raise_authorization_error(message: str = "Insufficient permissions") -> None:
    """Raise authorization error."""
    raise AuthorizationError(message)


def raise_validation_error(
    message: str, details: Optional[Dict[str, Any]] = None
) -> None:
    """Raise validation error."""
    raise ValidationError(message, details)


def raise_quota_exceeded_error(
    message: str, details: Optional[Dict[str, Any]] = None
) -> None:
    """Raise quota exceeded error."""
    raise QuotaExceededError(message, details)


def raise_external_service_error(service: str, message: str) -> None:
    """Raise external service error."""
    raise ExternalServiceError(
        f"{service} service error: {message}", {"service": service}
    )


def raise_database_error(
    message: str, details: Optional[Dict[str, Any]] = None
) -> None:
    """Raise database error."""
    raise DatabaseError(message, details)
