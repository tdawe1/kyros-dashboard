"""
Token usage storage utilities for tracking OpenAI API usage.
This is a simple in-memory implementation that can be replaced with a real database.
"""

import json
import copy
import os
import threading
from datetime import datetime
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

# In-memory storage for token usage (in production, this would be a database)
_token_usage_storage = {}
_job_storage = {}

# Thread safety
_storage_lock = threading.RLock()

# Configuration
DEFAULT_TOKEN_COST = float(
    os.getenv("TOKEN_COST_PER_1K", "0.0001")
)  # Default cost per 1K tokens
PERSISTENCE_FILE = os.getenv("TOKEN_STORAGE_FILE", "token_usage.json")


def _serialize_datetime(obj):
    """Custom JSON serializer for datetime objects."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _load_persistent_data():
    """Load data from persistent storage."""
    global _token_usage_storage, _job_storage

    if not os.path.exists(PERSISTENCE_FILE):
        return

    try:
        with open(PERSISTENCE_FILE, "r") as f:
            data = json.load(f)
            _token_usage_storage = data.get("token_usage", {})
            _job_storage = data.get("job_records", {})
        logger.info(f"Loaded persistent data from {PERSISTENCE_FILE}")
    except Exception as e:
        logger.error(f"Failed to load persistent data: {str(e)}")


def _save_persistent_data():
    """Save data to persistent storage."""
    try:
        data = {
            "token_usage": _token_usage_storage,
            "job_records": _job_storage,
            "saved_at": datetime.now().isoformat(),
        }

        with open(PERSISTENCE_FILE, "w") as f:
            json.dump(data, f, indent=2, default=_serialize_datetime)
        logger.debug(f"Saved persistent data to {PERSISTENCE_FILE}")
    except Exception as e:
        logger.error(f"Failed to save persistent data: {str(e)}")


# Load persistent data on module import
_load_persistent_data()


def save_token_usage(
    job_id: str, token_usage: Dict[str, Any], model: str, channel: str
) -> bool:
    """
    Save token usage data for a job.

    Args:
        job_id: Unique job identifier
        token_usage: Token usage data from OpenAI response
        model: Model used for generation
        channel: Channel for which content was generated

    Returns:
        bool: True if saved successfully, False otherwise
    """
    with _storage_lock:
        try:
            if job_id not in _token_usage_storage:
                _token_usage_storage[job_id] = {
                    "job_id": job_id,
                    "created_at": datetime.now().isoformat(),
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "channels": {},
                    "model": model,
                }

            # Update total tokens and cost (configurable cost per 1K tokens)
            total_tokens = token_usage.get("total_tokens", 0)
            _token_usage_storage[job_id]["total_tokens"] += total_tokens
            _token_usage_storage[job_id]["total_cost"] += (
                total_tokens * DEFAULT_TOKEN_COST / 1000
            )

            # Store per-channel usage (maintain list of entries per channel)
            if "channels" not in _token_usage_storage[job_id]:
                _token_usage_storage[job_id]["channels"] = {}

            if channel not in _token_usage_storage[job_id]["channels"]:
                _token_usage_storage[job_id]["channels"][channel] = []

            # Create usage dict and append to list
            usage_entry = {
                "prompt_tokens": token_usage.get("prompt_tokens", 0),
                "completion_tokens": token_usage.get("completion_tokens", 0),
                "total_tokens": total_tokens,
                "timestamp": datetime.now().isoformat(),
            }
            _token_usage_storage[job_id]["channels"][channel].append(usage_entry)

            # Save to persistent storage
            _save_persistent_data()

            logger.info(f"Token usage saved for job {job_id}: {token_usage}")
            return True

        except Exception as e:
            logger.error(f"Failed to save token usage for job {job_id}: {str(e)}")
            return False


def get_token_usage(job_id: str) -> Optional[Dict[str, Any]]:
    """
    Get token usage data for a specific job.

    Args:
        job_id: Unique job identifier

    Returns:
        Dict containing token usage data or None if not found
    """
    with _storage_lock:
        data = _token_usage_storage.get(job_id)
        return copy.deepcopy(data) if data else None


def get_all_token_usage() -> Dict[str, Dict[str, Any]]:
    """
    Get all token usage data.

    Returns:
        Dict of all token usage records
    """
    with _storage_lock:
        return copy.deepcopy(_token_usage_storage)


def save_job_record(job_id: str, job_data: Dict[str, Any]) -> bool:
    """
    Save job record with metadata.

    Args:
        job_id: Unique job identifier
        job_data: Job metadata and results

    Returns:
        bool: True if saved successfully, False otherwise
    """
    with _storage_lock:
        try:
            # Preserve original created_at when updating existing job
            if job_id in _job_storage:
                existing_record = _job_storage[job_id]
                created_at = existing_record.get(
                    "created_at", datetime.now().isoformat()
                )
            else:
                created_at = datetime.now().isoformat()

            _job_storage[job_id] = copy.deepcopy(
                {
                    **job_data,
                    "created_at": created_at,
                    "updated_at": datetime.now().isoformat(),
                }
            )

            # Save to persistent storage
            _save_persistent_data()

            logger.info(f"Job record saved for job {job_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save job record for job {job_id}: {str(e)}")
            return False


def get_job_record(job_id: str) -> Optional[Dict[str, Any]]:
    """
    Get job record by ID.

    Args:
        job_id: Unique job identifier

    Returns:
        Dict containing job data or None if not found
    """
    with _storage_lock:
        data = _job_storage.get(job_id)
        return copy.deepcopy(data) if data else None


def get_all_job_records() -> Dict[str, Dict[str, Any]]:
    """
    Get all job records.

    Returns:
        Dict of all job records
    """
    with _storage_lock:
        return copy.deepcopy(_job_storage)


def get_token_usage_stats() -> Dict[str, Any]:
    """
    Get aggregated token usage statistics.

    Returns:
        Dict containing usage statistics
    """
    with _storage_lock:
        total_jobs = len(_token_usage_storage)
        total_tokens = sum(
            record["total_tokens"] for record in _token_usage_storage.values()
        )
        total_cost = sum(
            record["total_cost"] for record in _token_usage_storage.values()
        )

        # Calculate average tokens per job
        avg_tokens_per_job = total_tokens / total_jobs if total_jobs > 0 else 0

        # Get model usage breakdown
        model_usage = {}
        for record in _token_usage_storage.values():
            model = record.get("model", "unknown")
            model_usage[model] = model_usage.get(model, 0) + record["total_tokens"]

        return {
            "total_jobs": total_jobs,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "avg_tokens_per_job": avg_tokens_per_job,
            "model_usage": model_usage,
            "last_updated": datetime.now().isoformat(),
        }


def export_token_usage_data() -> str:
    """
    Export all token usage data as JSON string.

    Returns:
        JSON string containing all data
    """
    with _storage_lock:
        export_data = {
            "token_usage": _token_usage_storage,
            "job_records": _job_storage,
            "statistics": get_token_usage_stats(),
            "exported_at": datetime.now().isoformat(),
        }

        return json.dumps(export_data, indent=2, default=_serialize_datetime)


def clear_all_data() -> bool:
    """
    Clear all stored data (useful for testing).

    Returns:
        bool: True if cleared successfully
    """
    with _storage_lock:
        try:
            _token_usage_storage.clear()
            _job_storage.clear()

            # Save empty state to persistent storage
            _save_persistent_data()

            logger.info("All token usage and job data cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear data: {str(e)}")
            return False
