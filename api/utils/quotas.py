import os
import redis
from datetime import date
from typing import Optional
import logging

logger = logging.getLogger(__name__)


# Redis connection
def get_redis_client():
    """Get Redis client connection"""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    return redis.from_url(redis_url, decode_responses=True)


def can_create_job(user_id: str, daily_limit: int = 10) -> tuple[bool, int]:
    """
    Check if user can create a job based on daily quota.

    Args:
        user_id: User identifier
        daily_limit: Maximum jobs per day (default: 10)

    Returns:
        tuple: (can_create: bool, current_count: int)
    """
    try:
        r = get_redis_client()
        today = date.today().isoformat()
        key = f"jobs:{user_id}:{today}"

        # Atomic increment-first approach
        new_count = r.incr(key)

        # Set expiration only when the returned counter equals 1 (first increment sets TTL)
        if new_count == 1:
            r.expire(key, 86400)  # 24 hours

        # Check if limit exceeded after increment
        if new_count > daily_limit:
            logger.warning(
                f"User {user_id} exceeded daily limit: {new_count}/{daily_limit}"
            )
            return False, new_count

        logger.info(f"User {user_id} job count: {new_count}/{daily_limit}")
        return True, new_count

    except Exception as e:
        logger.error(f"Error checking quota for user {user_id}: {e}")
        # Fail open - allow job creation if Redis is down
        return True, 0


def get_user_quota_status(user_id: str, daily_limit: int = 10) -> dict:
    """
    Get current quota status for a user.

    Args:
        user_id: User identifier
        daily_limit: Maximum jobs per day

    Returns:
        dict: Quota status information
    """
    try:
        r = get_redis_client()
        today = date.today().isoformat()
        key = f"jobs:{user_id}:{today}"

        count = r.get(key)
        current_count = int(count) if count else 0

        return {
            "user_id": user_id,
            "date": today,
            "current_count": current_count,
            "daily_limit": daily_limit,
            "remaining": max(0, daily_limit - current_count),
            "can_create": current_count < daily_limit,
        }

    except Exception as e:
        logger.error(f"Error getting quota status for user {user_id}: {e}")
        return {
            "user_id": user_id,
            "date": date.today().isoformat(),
            "current_count": 0,
            "daily_limit": daily_limit,
            "remaining": daily_limit,
            "can_create": True,
            "error": str(e),
        }


def reset_user_quota(user_id: str, date_str: Optional[str] = None) -> bool:
    """
    Reset user quota for a specific date (admin function).

    Args:
        user_id: User identifier
        date_str: Date string (YYYY-MM-DD), defaults to today

    Returns:
        bool: Success status
    """
    try:
        r = get_redis_client()
        target_date = date_str or date.today().isoformat()
        key = f"jobs:{user_id}:{target_date}"

        r.delete(key)
        logger.info(f"Reset quota for user {user_id} on {target_date}")
        return True

    except Exception as e:
        logger.error(f"Error resetting quota for user {user_id}: {e}")
        return False
