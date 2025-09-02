from fastapi import FastAPI, HTTPException
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
from middleware.rate_limiter import rate_limit_middleware
from generator import generate_content

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

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class GenerateRequest(BaseModel):
    input_text: str
    channels: List[str] = ["linkedin", "twitter"]
    tone: str = "professional"
    preset: str = "default"
    user_id: str = "anonymous"  # Default for demo purposes
    model: str = None  # Optional model parameter


class GenerateResponse(BaseModel):
    job_id: str
    status: str
    variants: Dict[str, List[Dict[str, Any]]]
    token_usage: Dict[str, int]
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
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/api/config")
async def get_config():
    """Get API configuration for frontend"""
    return {
        "api_mode": os.getenv("API_MODE", "demo"),
        "default_model": os.getenv("DEFAULT_MODEL", "gpt-4o-mini"),
        "valid_models": ["gpt-4o-mini", "gpt-4o", "gpt-4.1", "gpt-4.1-mini"],
    }


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
async def generate_content_endpoint(request: GenerateRequest):
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
    daily_limit = int(os.getenv("DAILY_JOB_LIMIT", "10"))
    can_create, current_count = can_create_job(request.user_id, daily_limit)

    if not can_create:
        quota_status = get_user_quota_status(request.user_id, daily_limit)
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
    logger.info(f"Processing job {job_id} for user {request.user_id}")

    # Set Sentry context for this job
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("job_id", job_id)
        scope.set_tag("user_id", request.user_id)
        scope.set_tag(
            "model", request.model or os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
        )
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
        variants = await generate_content(
            input_text=request.input_text,
            channels=request.channels,
            tone=request.tone,
            model=request.model,
        )

        # Update variant IDs to include job_id
        for channel, channel_variants in variants.items():
            for i, variant in enumerate(channel_variants):
                variant["id"] = f"{job_id}_{channel}_{i+1}"

    except Exception as e:
        logger.error(f"Content generation failed for job {job_id}: {str(e)}")
        sentry_sdk.capture_exception(e)
        raise HTTPException(
            status_code=500,
            detail={"error": "Content generation failed", "message": str(e)},
        )

    # 5. Calculate actual token usage (mock for now)
    token_stats = get_token_usage_stats(request.input_text)
    estimated_input_tokens = token_stats["estimated_tokens"]

    # Mock output tokens (in real implementation, this would come from OpenAI response)
    estimated_output_tokens = len(request.channels) * 150  # Rough estimate

    # Get the actual model used
    api_mode = os.getenv("API_MODE", "demo")
    default_model = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
    used_model = request.model or default_model

    return GenerateResponse(
        job_id=job_id,
        status="completed",
        variants=variants,
        token_usage={
            "input_tokens": estimated_input_tokens,
            "output_tokens": estimated_output_tokens,
            "total_tokens": estimated_input_tokens + estimated_output_tokens,
            "total_cost": (estimated_input_tokens + estimated_output_tokens)
            * 0.0001,  # Mock cost
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


@app.get("/api/quota/{user_id}")
async def get_user_quota(user_id: str):
    """
    Get current quota status for a user.
    """
    daily_limit = int(os.getenv("DAILY_JOB_LIMIT", "10"))
    quota_status = get_user_quota_status(user_id, daily_limit)
    return quota_status


@app.post("/api/quota/{user_id}/reset")
async def reset_user_quota_endpoint(user_id: str, date_str: str = None):
    """
    Reset user quota for a specific date (admin function).
    """
    success = reset_user_quota(user_id, date_str)
    if success:
        return {"message": f"Quota reset successfully for user {user_id}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to reset quota")


@app.post("/api/token-stats")
async def get_token_statistics(request: GenerateRequest):
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
