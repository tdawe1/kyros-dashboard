from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
from datetime import datetime
import os
import logging
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

# Import our new utilities
from utils.quotas import can_create_job, get_user_quota_status, reset_user_quota
from utils.token_utils import validate_input_limits, get_token_usage_stats
from utils.token_storage import save_job_record, get_token_usage
from middleware.rate_limiter import rate_limit_middleware
from generator import generate_content
from core.auth import User, get_current_user
from core.input_validation import SecureGenerateRequest
from core.database import check_database_health
from core.error_handling import (
    handle_kyros_exception,
    handle_validation_error,
    handle_http_exception,
    handle_generic_exception,
    KyrosException,
)
from core.config import get_settings, get_cors_origins
from fastapi.exceptions import RequestValidationError

# Import tools registry
from tools.registry import load_tool_routers, get_tools_metadata, get_tool_metadata

# Import scheduler
from core.scheduler import scheduler_router

# Import authentication
from core.auth_router import router as auth_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Sentry
sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        traces_sample_rate=0.1,
        integrations=[
            FastApiIntegration(auto_enable=True),
            LoggingIntegration(
                level=logging.INFO,  # Capture info and above as breadcrumbs
                event_level=logging.ERROR,  # Send errors as events
            ),
        ],
        environment=os.getenv("ENVIRONMENT", "development"),
        release=os.getenv("RELEASE_VERSION", "1.0.0"),
    )
    logger.info("Sentry initialized successfully")
else:
    logger.warning("SENTRY_DSN not found, Sentry monitoring disabled")

app = FastAPI(title="Kyros Repurposer API", version="1.0.0")

# Add exception handlers
app.add_exception_handler(KyrosException, handle_kyros_exception)
app.add_exception_handler(RequestValidationError, handle_validation_error)
app.add_exception_handler(HTTPException, handle_http_exception)
app.add_exception_handler(Exception, handle_generic_exception)

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Register tool routers dynamically
for name, router in load_tool_routers():
    app.include_router(router, prefix=f"/api/tools/{name}", tags=[name])
    logger.info(f"Registered tool router: {name}")

# Register scheduler router
app.include_router(scheduler_router, prefix="/api/scheduler", tags=["scheduler"])
logger.info("Registered scheduler router")

# Register authentication router
app.include_router(auth_router)
logger.info("Registered authentication router")

# CORS middleware - secure configuration
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)


# Pydantic models
class GenerateRequest(BaseModel):
    input_text: str
    channels: List[str] = ["linkedin", "twitter"]
    tone: str = "professional"
    preset: str = "default"
    model: str = None  # Optional model parameter


class GenerateResponse(BaseModel):
    job_id: str
    status: str
    variants: Dict[str, List[Dict[str, Any]]]
    token_usage: Dict[str, Any]
    model: str
    api_mode: str


class ExportRequest(BaseModel):
    job_id: str
    format: str = "csv"
    selected_variants: List[str] = []


class ExportResponse(BaseModel):
    file_url: str
    filename: str


class PresetRequest(BaseModel):
    name: str
    description: str
    config: Dict[str, Any]


# Mock data
mock_jobs = [
    {
        "id": "1",
        "client": "TechCorp Inc.",
        "words": 1250,
        "status": "completed",
        "created_at": "2024-01-15T10:30:00Z",
        "source_url": "https://techcorp.com/blog/ai-trends",
    },
    {
        "id": "2",
        "client": "StartupXYZ",
        "words": 890,
        "status": "processing",
        "created_at": "2024-01-15T09:15:00Z",
        "source_url": "https://startupxyz.com/news/product-launch",
    },
    {
        "id": "3",
        "client": "Enterprise Ltd.",
        "words": 2100,
        "status": "pending",
        "created_at": "2024-01-15T08:45:00Z",
        "source_url": "https://enterprise.com/insights/market-analysis",
    },
]

mock_presets = [
    {
        "id": "1",
        "name": "Default",
        "description": "Standard repurposing settings",
        "config": {"tone": "professional", "length": "medium"},
    },
    {
        "id": "2",
        "name": "Marketing",
        "description": "Marketing-focused content",
        "config": {"tone": "engaging", "length": "short"},
    },
    {
        "id": "3",
        "name": "Technical",
        "description": "Technical documentation style",
        "config": {"tone": "formal", "length": "long"},
    },
]


# Routes
@app.get("/api/health")
async def health_check():
    """Comprehensive health check including database connectivity."""
    db_healthy = check_database_health()

    status = "ok" if db_healthy else "degraded"

    return {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "database": "healthy" if db_healthy else "unhealthy",
        "version": "1.0.0",
    }


@app.get("/api/config")
async def get_config():
    """Get API configuration for frontend"""
    return {
        "api_mode": settings.api_mode,
        "default_model": settings.default_model,
        "valid_models": ["gpt-4o-mini", "gpt-4o", "gpt-4.1", "gpt-4.1-mini"],
        "environment": settings.environment.value,
        "version": settings.app_version,
    }


@app.get("/api/tools")
async def get_tools():
    """Get list of available tools"""
    return {
        "tools": get_tools_metadata(),
        "total": len(get_tools_metadata()),
    }


@app.get("/api/tools/{tool_name}")
async def get_tool(tool_name: str):
    """Get metadata for a specific tool"""
    tool_metadata = get_tool_metadata(tool_name)
    if not tool_metadata:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool_metadata


@app.get("/api/kpis")
async def get_kpis():
    return {
        "jobs_processed": 12,
        "hours_saved": 24.5,
        "avg_edit_min": 18,
        "export_bundles": 9,
    }


@app.get("/api/jobs")
async def get_jobs():
    return mock_jobs


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    job = next((job for job in mock_jobs if job["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_content_endpoint(
    request: SecureGenerateRequest, current_user: User = Depends(get_current_user)
):
    """
    Generate content variants with token and quota controls.
    """
    # 1. Validate input limits (character count and token estimation)
    validation_result = validate_input_limits(request.input_text)
    if not validation_result["valid"]:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Input validation failed",
                "message": "; ".join(validation_result["errors"]),
                "stats": validation_result["stats"],
            },
        )

    # 2. Check minimum input length
    if len(request.input_text) < 100:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Input too short",
                "message": "Input text must be at least 100 characters",
                "current_length": len(request.input_text),
            },
        )

    # 3. Check user quota
    daily_limit = settings.daily_job_limit
    can_create, current_count = can_create_job(current_user.id, daily_limit)

    if not can_create:
        quota_status = get_user_quota_status(current_user.id, daily_limit)
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Daily quota exceeded",
                "message": f"Daily job limit of {daily_limit} exceeded. Current count: {current_count}",
                "quota_status": quota_status,
            },
        )

    # 4. Generate job ID and process content
    job_id = str(uuid.uuid4())
    logger.info(f"Processing job {job_id} for user {current_user.id}")

    # Set Sentry context for this job
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("job_id", job_id)
        scope.set_tag("user_id", current_user.id)
        scope.set_tag("model", request.model or settings.default_model)
        scope.set_context(
            "job_details",
            {
                "channels": request.channels,
                "tone": request.tone,
                "input_length": len(request.input_text),
            },
        )

    # Generate content using the new generator
    try:
        variants = generate_content(
            input_text=request.input_text,
            channels=request.channels,
            tone=request.tone,
            model=request.model,
            job_id=job_id,
        )

        # Update variant IDs to include job_id
        for channel, channel_variants in variants.items():
            for i, variant in enumerate(channel_variants):
                variant["id"] = f"{job_id}_{channel}_{i+1}"

        # Save job record
        job_record = {
            "job_id": job_id,
            "user_id": current_user.id,
            "input_text": request.input_text,
            "channels": request.channels,
            "tone": request.tone,
            "model": request.model or settings.default_model,
            "status": "completed",
            "variants": variants,
        }
        save_job_record(job_id, job_record)

    except Exception as e:
        logger.error(f"Content generation failed for job {job_id}: {str(e)}")
        sentry_sdk.capture_exception(e)
        raise HTTPException(
            status_code=500,
            detail={"error": "Content generation failed", "message": str(e)},
        )

    # 5. Calculate actual token usage
    token_stats = get_token_usage_stats(request.input_text)
    estimated_input_tokens = token_stats["estimated_tokens"]

    # Get actual token usage from storage if available
    stored_token_usage = get_token_usage(job_id)
    if stored_token_usage:
        actual_output_tokens = (
            stored_token_usage["total_tokens"] - estimated_input_tokens
        )
        total_tokens = stored_token_usage["total_tokens"]
        total_cost = stored_token_usage["total_cost"]
    else:
        # Fallback to estimation
        actual_output_tokens = len(request.channels) * 150  # Rough estimate
        total_tokens = estimated_input_tokens + actual_output_tokens
        total_cost = total_tokens * 0.0001  # Mock cost

    # Get the actual model used
    api_mode = settings.api_mode
    used_model = request.model or settings.default_model

    return GenerateResponse(
        job_id=job_id,
        status="completed",
        variants=variants,
        token_usage={
            "input_tokens": estimated_input_tokens,
            "output_tokens": actual_output_tokens,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "quota_used": current_count,
            "quota_remaining": daily_limit - current_count,
        },
        model=used_model,
        api_mode=api_mode,
    )


@app.post("/api/export", response_model=ExportResponse)
async def export_content(request: ExportRequest):
    # Mock export - in real implementation, this would generate actual files
    filename = f"export_{request.job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{request.format}"
    file_url = f"/downloads/{filename}"

    return ExportResponse(file_url=file_url, filename=filename)


@app.get("/api/presets")
async def get_presets():
    return mock_presets


# New endpoints for Phase B features


@app.get("/api/quota/me")
async def get_user_quota(current_user: User = Depends(get_current_user)):
    """
    Get current quota status for the authenticated user.
    """
    daily_limit = settings.daily_job_limit
    quota_status = get_user_quota_status(current_user.id, daily_limit)
    return quota_status


@app.post("/api/quota/{user_id}/reset")
async def reset_user_quota_endpoint(
    user_id: str, date_str: str = None, current_user: User = Depends(get_current_user)
):
    """
    Reset user quota for a specific date (admin function).
    """
    from core.auth import UserRole

    # Check if user is admin or resetting their own quota
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    success = reset_user_quota(user_id, date_str)
    if success:
        return {"message": f"Quota reset successfully for user {user_id}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to reset quota")


@app.post("/api/token-stats")
async def get_token_statistics(
    request: SecureGenerateRequest, current_user: User = Depends(get_current_user)
):
    """
    Get token usage statistics for input text without creating a job.
    """
    token_stats = get_token_usage_stats(request.input_text)
    validation_result = validate_input_limits(request.input_text)

    return {
        "token_stats": token_stats,
        "validation": validation_result,
        "recommendations": {
            "can_process": validation_result["valid"],
            "estimated_cost": token_stats["estimated_tokens"] * 0.0001,
            "efficiency_tip": "Consider breaking large texts into smaller chunks for better processing",
        },
    }


@app.post("/api/presets")
async def create_preset(request: PresetRequest):
    new_preset = {
        "id": str(uuid.uuid4()),
        "name": request.name,
        "description": request.description,
        "config": request.config,
    }
    mock_presets.append(new_preset)
    return new_preset


@app.get("/api/presets/{preset_id}")
async def get_preset(preset_id: str):
    preset = next(
        (preset for preset in mock_presets if preset["id"] == preset_id), None
    )
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    return preset


@app.put("/api/presets/{preset_id}")
async def update_preset(preset_id: str, request: PresetRequest):
    preset = next(
        (preset for preset in mock_presets if preset["id"] == preset_id), None
    )
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")

    preset["name"] = request.name
    preset["description"] = request.description
    preset["config"] = request.config

    return preset


@app.delete("/api/presets/{preset_id}")
async def delete_preset(preset_id: str):
    global mock_presets
    mock_presets = [preset for preset in mock_presets if preset["id"] != preset_id]
    return {"message": "Preset deleted successfully"}


# Token usage endpoints
@app.get("/api/token-usage/{job_id}")
async def get_job_token_usage(job_id: str):
    """
    Get token usage data for a specific job.
    """
    token_usage = get_token_usage(job_id)
    if not token_usage:
        raise HTTPException(
            status_code=404, detail="Token usage data not found for this job"
        )
    return token_usage


@app.get("/api/token-usage/stats")
async def get_token_usage_statistics():
    """
    Get aggregated token usage statistics.
    """
    from utils.token_storage import get_token_usage_stats

    return get_token_usage_stats()


@app.get("/api/jobs/{job_id}/details")
async def get_job_details(job_id: str):
    """
    Get detailed job information including token usage.
    """
    from utils.token_storage import get_job_record

    job_record = get_job_record(job_id)
    if not job_record:
        raise HTTPException(status_code=404, detail="Job not found")

    token_usage = get_token_usage(job_id)

    return {
        "job": job_record,
        "token_usage": token_usage,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
