import os
import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from generator import VALID_MODELS

router = APIRouter()

logger = logging.getLogger(__name__)


def safe_int(value: str, default: int) -> int:
    """Safely convert a string to an integer."""
    try:
        return int(value)
    except (ValueError, TypeError):
        logger.warning(f"Could not convert '{value}' to int, using default {default}")
        return default


@router.get("/config")
async def get_config():
    """Get API configuration for frontend"""
    try:
        return {
            "api_mode": os.getenv("API_MODE", "demo"),
            "default_model": os.getenv("DEFAULT_MODEL", "gpt-4o-mini"),
            "valid_models": VALID_MODELS,
            "max_input_characters": safe_int(
                os.getenv("MAX_INPUT_CHARACTERS", "100000"), 100000
            ),
            "max_tokens_per_job": safe_int(
                os.getenv("MAX_TOKENS_PER_JOB", "50000"), 50000
            ),
            "daily_job_limit": safe_int(os.getenv("DAILY_JOB_LIMIT", "10"), 10),
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/kpis")
async def get_kpis():
    """Get KPI data."""
    return {
        "jobs_processed": 125,
        "hours_saved": 42.5,
        "avg_edit_min": 15,
        "export_bundles": 78,
    }


@router.get("/jobs")
async def get_jobs():
    """Get all jobs."""
    return [
        {
            "id": "job_1",
            "client": "Client A",
            "words": 1200,
            "status": "completed",
            "created_at": "2024-01-01T12:00:00Z",
            "source_url": "http://example.com/blog/1",
        }
    ]


@router.get("/jobs/{job_id}")
async def get_job_by_id(job_id: str):
    """Get job by ID."""
    if job_id == "job_1":
        return {
            "id": "job_1",
            "client": "Client A",
            "words": 1200,
            "status": "completed",
            "created_at": "2024-01-01T12:00:00Z",
            "source_url": "http://example.com/blog/1",
        }
    return JSONResponse(
        status_code=404,
        content={
            "error": {"code": "NOT_FOUND", "message": "Job not found", "details": {}}
        },
    )


class ExportRequest(BaseModel):
    job_id: str
    format: str = "csv"


@router.post("/export")
async def export_content(request: ExportRequest):
    """Export content."""
    filename = f"{request.job_id}.{request.format}"
    return {"file_url": f"http://example.com/{filename}", "filename": filename}


@router.get("/presets")
async def get_presets():
    """Get all presets."""
    return [
        {
            "id": "preset_1",
            "name": "Preset 1",
            "description": "Description 1",
            "config": {},
        }
    ]


class CreatePresetRequest(BaseModel):
    name: str
    description: str
    config: dict


@router.post("/presets")
async def create_preset(request: CreatePresetRequest):
    """Create a preset."""
    return {"id": "preset_2", **request.dict()}


@router.get("/presets/{preset_id}")
async def get_preset_by_id(preset_id: str):
    """Get preset by ID."""
    if preset_id == "preset_1":
        return {
            "id": "preset_1",
            "name": "Preset 1",
            "description": "Description 1",
            "config": {},
        }
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "NOT_FOUND",
                "message": "Preset not found",
                "details": {},
            },
        },
    )


@router.put("/presets/{preset_id}")
async def update_preset(preset_id: str, request: dict):
    """Update a preset."""
    return {"id": preset_id, **request}


@router.delete("/presets/{preset_id}")
async def delete_preset(preset_id: str):
    """Delete a preset."""
    return {"message": "Preset deleted successfully"}


@router.get("/quota/{user_id}")
async def get_user_quota(user_id: str):
    """Get user quota."""
    return {
        "user_id": user_id,
        "current_count": 0,
        "daily_limit": 10,
        "remaining": 10,
        "can_create": True,
        "date": "2024-01-01",
    }


@router.post("/quota/{user_id}/reset")
async def reset_user_quota(user_id: str):
    """Reset user quota."""
    return {"message": f"Quota for user {user_id} reset successfully"}


@router.post("/token-stats")
async def get_token_stats(request: dict):
    """Get token statistics."""
    return {
        "token_stats": {
            "character_count": len(request.get("input_text", "")),
            "word_count": len(request.get("input_text", "").split()),
            "estimated_tokens": len(request.get("input_text", "")) / 4,
            "usage_percentage": {"characters": 10, "tokens": 10},
        },
        "validation": {"valid": True, "errors": [], "stats": {}},
        "recommendations": {
            "can_process": True,
            "estimated_cost": 0,
            "efficiency_tip": "",
        },
    }
