"""
Resilient FastAPI application for Kyros Dashboard.
This version is designed to start even if some modules fail to import.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import logging
import uuid

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create FastAPI app
app = FastAPI(
    title="Kyros Dashboard API",
    description="AI-powered content generation and scheduling platform",
    version="1.0.0",
)


# CRITICAL: Health endpoints at the top - these must always work
@app.get("/")
async def root():
    """Root endpoint for Railway healthcheck."""
    return {"status": "ok", "message": "Kyros Dashboard API"}


@app.get("/health")
async def health_simple():
    """Simple health check without /api prefix."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/api/health")
async def health_check():
    """Simple health check for Railway deployment."""
    try:
        return {"status": "ok", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# Safe imports with error handling
def safe_import(module_name, import_func):
    """Safely import a module and return None if it fails."""
    try:
        return import_func()
    except Exception as e:
        logger.warning(f"Failed to import {module_name}: {e}")
        return None


# Try to import optional modules
sentry_sdk = safe_import("sentry_sdk", lambda: __import__("sentry_sdk"))
FastApiIntegration = safe_import(
    "FastApiIntegration",
    lambda: __import__(
        "sentry_sdk.integrations.fastapi"
    ).integrations.fastapi.FastApiIntegration,
)
LoggingIntegration = safe_import(
    "LoggingIntegration",
    lambda: __import__(
        "sentry_sdk.integrations.logging"
    ).integrations.logging.LoggingIntegration,
)

# Initialize Sentry if available
if sentry_sdk:
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        try:
            sentry_sdk.init(
                dsn=sentry_dsn,
                traces_sample_rate=0.1,
                integrations=[
                    FastApiIntegration(auto_enabling_instrumentations=False),
                    LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
                ],
            )
            logger.info("Sentry initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Sentry: {e}")

# Try to import core modules
try:
    from core.config import get_settings, get_cors_origins

    settings = get_settings()
    cors_origins = get_cors_origins()
except Exception as e:
    logger.warning(f"Failed to import core config: {e}")
    settings = None
    cors_origins = ["*"]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to import and add other modules
try:
    from core.database import check_database_health

    @app.get("/api/health/detailed")
    async def detailed_health_check():
        """Comprehensive health check including database connectivity."""
        try:
            db_healthy = check_database_health()
            status = "ok" if db_healthy else "degraded"
            return {
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "database": "healthy" if db_healthy else "unhealthy",
                "version": "1.0.0",
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

except Exception as e:
    logger.warning(f"Failed to import database health check: {e}")

# Try to import utilities
utils_quotas = safe_import("utils.quotas", lambda: __import__("utils.quotas"))
utils_token_utils = safe_import(
    "utils.token_utils", lambda: __import__("utils.token_utils")
)
utils_token_storage = safe_import(
    "utils.token_storage", lambda: __import__("utils.token_storage")
)

# Try to import middleware
middleware_rate_limiter = safe_import(
    "middleware.rate_limiter", lambda: __import__("middleware.rate_limiter")
)

# Try to import generator
generator = safe_import("generator", lambda: __import__("generator"))

# Try to import auth
core_auth = safe_import("core.auth", lambda: __import__("core.auth"))
core_input_validation = safe_import(
    "core.input_validation", lambda: __import__("core.input_validation")
)
core_error_handling = safe_import(
    "core.error_handling", lambda: __import__("core.error_handling")
)

# Try to import tools
tools_registry = safe_import("tools.registry", lambda: __import__("tools.registry"))

# Try to import scheduler
core_scheduler = safe_import("core.scheduler", lambda: __import__("core.scheduler"))

# Try to import auth router
core_auth_router = safe_import(
    "core.auth_router", lambda: __import__("core.auth_router")
)

# Add routers if they're available
if core_auth_router:
    try:
        from core.auth_router import router as auth_router

        app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
        logger.info("Auth router added successfully")
    except Exception as e:
        logger.warning(f"Failed to add auth router: {e}")

if core_scheduler:
    try:
        from core.scheduler.router import router as scheduler_router

        app.include_router(
            scheduler_router, prefix="/api/scheduler", tags=["scheduler"]
        )
        logger.info("Scheduler router added successfully")
    except Exception as e:
        logger.warning(f"Failed to add scheduler router: {e}")

if tools_registry:
    try:
        from tools.registry import load_tool_routers

        tool_routers = load_tool_routers()
        for router in tool_routers:
            app.include_router(router, prefix="/api/tools", tags=["tools"])
        logger.info("Tool routers added successfully")
    except Exception as e:
        logger.warning(f"Failed to add tool routers: {e}")


# Add basic endpoints that work even without other modules
try:
    from api import router as api_router

    app.include_router(api_router, prefix="/api", tags=["api"])
    logger.info("API router added successfully")
except Exception as e:
    logger.warning(f"Failed to add API router: {e}")


# Add a simple generate endpoint that works without full functionality
@app.post("/api/generate")
async def generate_simple(request: dict):
    """Simple generate endpoint for basic functionality"""
    try:
        if generator:
            from generator import generate_content
            from utils.token_storage import get_token_usage

            input_text = request.get("input_text")
            if not input_text or len(input_text) < 20:
                raise HTTPException(
                    status_code=400, detail={"error": "Input text too short"}
                )
            if len(input_text) > 100000:
                raise HTTPException(
                    status_code=400, detail={"error": "Input text too long"}
                )

            if utils_quotas:
                from utils.quotas import can_create_job

                can_create, _ = can_create_job(request.get("user_id", "anonymous"))
                if not can_create:
                    raise HTTPException(
                        status_code=400, detail={"error": "Quota exceeded"}
                    )

            job_id = f"job_{uuid.uuid4()}"
            variants = await generate_content(
                input_text=input_text,
                channels=request.get("channels", ["linkedin"]),
                tone=request.get("tone", "professional"),
                model=request.get("model"),
                job_id=job_id,
            )
            token_usage = get_token_usage(job_id)
            return {
                "job_id": job_id,
                "status": "completed",
                "variants": variants,
                "token_usage": token_usage,
                "model": request.get("model")
                or os.getenv("DEFAULT_MODEL", "gpt-4o-mini"),
                "api_mode": os.getenv("API_MODE", "demo"),
            }
        else:
            return {"error": "Generator module not available", "status": "demo"}
    except HTTPException as e:
        raise e
    except Exception as e:
        return {"error": str(e), "status": "error"}


# Add error handlers if available
if core_error_handling:
    try:
        from core.error_handling import (
            handle_kyros_exception,
            handle_validation_error,
            handle_http_exception,
            handle_generic_exception,
            KyrosException,
        )
        from fastapi.exceptions import RequestValidationError

        @app.exception_handler(KyrosException)
        async def kyros_exception_handler(request, exc):
            return handle_kyros_exception(request, exc)

        @app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request, exc):
            return handle_validation_error(request, exc)

        @app.exception_handler(HTTPException)
        async def http_exception_handler(request, exc):
            return handle_http_exception(request, exc)

        @app.exception_handler(Exception)
        async def generic_exception_handler(request, exc):
            return handle_generic_exception(request, exc)

        logger.info("Error handlers added successfully")
    except Exception as e:
        logger.warning(f"Failed to add error handlers: {e}")

# Add middleware if available
if middleware_rate_limiter:
    try:
        from middleware.rate_limiter import rate_limit_middleware

        app.middleware("http")(rate_limit_middleware)
        logger.info("Rate limiter middleware added successfully")
    except Exception as e:
        logger.warning(f"Failed to add rate limiter middleware: {e}")

logger.info("Kyros Dashboard API started successfully")
