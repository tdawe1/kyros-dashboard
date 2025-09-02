from datetime import date
from typing import Optional
import logging
from core.security import get_secure_redis_client, secure_operation, SecurityMode

logger = logging.getLogger(__name__)


@secure_operation(security_mode=SecurityMode.FAIL_CLOSED)
def can_create_job(user_id: str, daily_limit: int = 10) -> tuple[bool, int]:
    """
    Check if user can create a job based on daily quota using atomic Redis transactions.
    FAILS CLOSED - denies job creation if Redis is unavailable.

    Args:
        user_id: User identifier
        daily_limit: Maximum jobs per day (default: 10)

    Returns:
        tuple: (can_create: bool, current_count: int)
    """
    r = get_secure_redis_client()
    today = date.today().isoformat()
    key = f"jobs:{user_id}:{today}"

    # Safer: use wrapped ops; set TTL only on first increment
    new_count = r.incr(key)
    if new_count == 1:
        r.expire(key, 86400)

    # Check if limit exceeded after increment
    if new_count > daily_limit:
        logger.warning(
            f"User {user_id} exceeded daily limit: {new_count}/{daily_limit}"
        )
        return False, new_count

    logger.info(f"User {user_id} job count: {new_count}/{daily_limit}")
    return True, new_count


@secure_operation(security_mode=SecurityMode.FAIL_CLOSED)
def get_user_quota_status(user_id: str, daily_limit: int = 10) -> dict:
    """
    Get current quota status for a user.
    FAILS CLOSED - raises exception if Redis is unavailable.

    Args:
        user_id: User identifier
        daily_limit: Maximum jobs per day

    Returns:
        dict: Quota status information
    """
    r = get_secure_redis_client()
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


@secure_operation(security_mode=SecurityMode.FAIL_CLOSED)
def reset_user_quota(user_id: str, date_str: Optional[str] = None) -> bool:
    """
    Reset user quota for a specific date (admin function).
    FAILS CLOSED - raises exception if Redis is unavailable.

    Args:
        user_id: User identifier
        date_str: Date string (YYYY-MM-DD), defaults to today

    Returns:
        bool: Success status
    """
    r = get_secure_redis_client()
    target_date = date_str or date.today().isoformat()
    key = f"jobs:{user_id}:{target_date}"

    r.delete(key)
    logger.info(f"Reset quota for user {user_id} on {target_date}")
    return True
