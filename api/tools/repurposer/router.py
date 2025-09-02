from fastapi import APIRouter, HTTPException
from typing import List
import uuid
import os
import logging
from datetime import datetime
from core.logging import get_job_logger

from .schemas import (
    GenerateRequest,
    GenerateResponse,
    ExportRequest,
    ExportResponse,
    PresetRequest,
    PresetResponse,
)
from .generator import generate_content
from utils.quotas import can_create_job, get_user_quota_status
from utils.token_utils import validate_input_limits, get_token_usage_stats
from utils.token_storage import save_job_record, get_token_usage

logger = logging.getLogger(__name__)
job_logger = get_job_logger()

router = APIRouter()

# Mock data for presets
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


@router.post("/generate", response_model=GenerateResponse)
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

    # Log job start using core logging service
    job_logger.log_job_start(
        job_id=job_id,
        tool_name="repurposer",
        user_id=request.user_id,
        job_details={
            "channels": request.channels,
            "tone": request.tone,
            "input_length": len(request.input_text),
            "model": request.model or os.getenv("DEFAULT_MODEL", "gpt-4o-mini"),
        },
    )

    # Generate content using the repurposer generator
    try:
        variants = await generate_content(
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
            "user_id": request.user_id,
            "input_text": request.input_text,
            "channels": request.channels,
            "tone": request.tone,
            "model": request.model or os.getenv("DEFAULT_MODEL", "gpt-4o-mini"),
            "status": "completed",
            "variants": variants,
            "tool": "repurposer",
        }
        save_job_record(job_id, job_record)

        # Log successful job completion
        job_logger.log_job_success(
            job_id=job_id,
            tool_name="repurposer",
            user_id=request.user_id,
            result_summary={
                "channels_processed": len(variants),
                "total_variants": sum(len(v) for v in variants.values()),
                "model_used": request.model
                or os.getenv("DEFAULT_MODEL", "gpt-4o-mini"),
            },
        )

    except Exception as e:
        logger.error(f"Content generation failed for repurposer job {job_id}: {str(e)}")
        job_logger.log_job_error(
            job_id=job_id,
            tool_name="repurposer",
            user_id=request.user_id,
            error=e,
            error_context={
                "channels": request.channels,
                "tone": request.tone,
                "input_length": len(request.input_text),
            },
        )
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
    api_mode = os.getenv("API_MODE", "demo")
    default_model = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
    used_model = request.model or default_model

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


@router.post("/export", response_model=ExportResponse)
async def export_content(request: ExportRequest):
    """
    Export generated content in various formats.
    """
    # Mock export - in real implementation, this would generate actual files
    filename = f"repurposer_export_{request.job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{request.format}"
    file_url = f"/downloads/{filename}"

    return ExportResponse(file_url=file_url, filename=filename)


@router.get("/presets", response_model=List[PresetResponse])
async def get_presets():
    """
    Get available presets for the repurposer tool.
    """
    return mock_presets


@router.post("/presets", response_model=PresetResponse)
async def create_preset(request: PresetRequest):
    """
    Create a new preset for the repurposer tool.
    """
    new_preset = {
        "id": str(uuid.uuid4()),
        "name": request.name,
        "description": request.description,
        "config": request.config,
    }
    mock_presets.append(new_preset)
    return new_preset


@router.get("/presets/{preset_id}", response_model=PresetResponse)
async def get_preset(preset_id: str):
    """
    Get a specific preset by ID.
    """
    preset = next(
        (preset for preset in mock_presets if preset["id"] == preset_id), None
    )
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    return preset


@router.put("/presets/{preset_id}", response_model=PresetResponse)
async def update_preset(preset_id: str, request: PresetRequest):
    """
    Update an existing preset.
    """
    preset = next(
        (preset for preset in mock_presets if preset["id"] == preset_id), None
    )
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")

    preset["name"] = request.name
    preset["description"] = request.description
    preset["config"] = request.config

    return preset


@router.delete("/presets/{preset_id}")
async def delete_preset(preset_id: str):
    """
    Delete a preset.
    """
    global mock_presets
    mock_presets = [preset for preset in mock_presets if preset["id"] != preset_id]
    return {"message": "Preset deleted successfully"}


@router.get("/config")
async def get_repurposer_config():
    """
    Get repurposer-specific configuration.
    """
    return {
        "tool": "repurposer",
        "name": "Content Repurposer",
        "description": "Transform content into multiple channel formats",
        "supported_channels": ["linkedin", "twitter", "newsletter"],
        "supported_tones": ["professional", "casual", "engaging", "formal"],
        "api_mode": os.getenv("API_MODE", "demo"),
        "default_model": os.getenv("DEFAULT_MODEL", "gpt-4o-mini"),
        "valid_models": ["gpt-4o-mini", "gpt-4o", "gpt-4.1", "gpt-4.1-mini"],
    }
