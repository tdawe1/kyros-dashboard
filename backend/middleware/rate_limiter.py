import os
import time
from fastapi import Request
from fastapi.responses import JSONResponse
import logging
from core.security import get_secure_redis_client, secure_operation, SecurityMode

logger = logging.getLogger(__name__)

# Rate limiting configuration
RATE_LIMIT_REQUESTS = int(
    os.getenv("RATE_LIMIT_REQUESTS", "100")
)  # requests per window
RATE_LIMIT_WINDOW = int(
    os.getenv("RATE_LIMIT_WINDOW", "3600")
)  # window in seconds (1 hour)
RATE_LIMIT_BURST = int(os.getenv("RATE_LIMIT_BURST", "10"))  # burst allowance


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter implementation using Redis.
    """

    def __init__(self, redis_client=None):
        self.redis_client = redis_client or get_secure_redis_client()

    def _get_client_identifier(self, request: Request) -> str:
        """
        Get client identifier for rate limiting.
        In production, this should use user authentication.
        For now, we'll use IP address.
        """
        # Get real IP address (considering proxies)
        client_ip = "unknown"

        # Check X-Forwarded-For header (case-insensitive)
        forwarded_for = None
        for header_name, header_value in request.headers.items():
            if header_name.lower() == "x-forwarded-for":
                forwarded_for = header_value
                break

        if forwarded_for:
            # Split on commas, trim whitespace and quotes, take first non-empty token
            ips = [ip.strip().strip("\"'") for ip in forwarded_for.split(",")]
            for ip in ips:
                if ip and ip.lower() != "unknown":
                    client_ip = ip
                    break
        else:
            # Check X-Real-IP header
            real_ip = None
            for header_name, header_value in request.headers.items():
                if header_name.lower() == "x-real-ip":
                    real_ip = header_value
                    break

            if real_ip and real_ip.lower() != "unknown":
                client_ip = real_ip
            else:
                # Fall back to request.client.host
                client_ip = request.client.host if request.client else "unknown"

        # Normalize IP string (strip surrounding brackets/zone if present)
        if client_ip.startswith("[") and "]" in client_ip:
            client_ip = client_ip[1 : client_ip.index("]")]
        elif "%" in client_ip:
            client_ip = client_ip.split("%")[0]

        return f"rate_limit:{client_ip}"

    @secure_operation(security_mode=SecurityMode.FAIL_CLOSED)
    def is_allowed(self, request: Request) -> tuple[bool, dict]:
        """
        Check if request is allowed based on token bucket algorithm.
        FAILS CLOSED - denies requests if Redis is unavailable.

        Args:
            request: FastAPI request object

        Returns:
            tuple: (is_allowed: bool, rate_limit_info: dict)
        """
        client_id = self._get_client_identifier(request)
        current_time = time.time()

        # Token bucket key
        bucket_key = f"token_bucket:{client_id}"

        # Get current bucket state
        bucket_data = self.redis_client.hgetall(bucket_key)

        if not bucket_data:
            # Initialize bucket
            tokens = RATE_LIMIT_BURST
            last_refill = current_time
        else:
            tokens = float(bucket_data.get("tokens", RATE_LIMIT_BURST))
            last_refill = float(bucket_data.get("last_refill", current_time))

        # Calculate tokens to add based on time elapsed
        time_elapsed = current_time - last_refill
        tokens_to_add = time_elapsed * (RATE_LIMIT_REQUESTS / RATE_LIMIT_WINDOW)

        # Refill bucket (cap at burst size)
        tokens = min(RATE_LIMIT_BURST, tokens + tokens_to_add)

        # Check if request can be processed
        if tokens >= 1:
            # Consume one token
            tokens -= 1
            is_allowed = True
        else:
            is_allowed = False

        # Use pipeline for atomic operations
        pipe = self.redis_client._client.pipeline()
        pipe.hset(bucket_key, mapping={"tokens": tokens, "last_refill": current_time})
        pipe.expire(bucket_key, RATE_LIMIT_WINDOW * 2)
        pipe.execute()

        # Calculate reset time
        reset_time = current_time + (
            (1 - tokens) * (RATE_LIMIT_WINDOW / RATE_LIMIT_REQUESTS)
        )

        rate_limit_info = {
            "limit": RATE_LIMIT_REQUESTS,
            "remaining": max(0, int(tokens)),
            "reset": int(reset_time),
            "window": RATE_LIMIT_WINDOW,
            "burst": RATE_LIMIT_BURST,
        }

        logger.debug(
            f"Rate limit check for {client_id}: allowed={is_allowed}, tokens={tokens:.2f}"
        )

        return is_allowed, rate_limit_info


async def rate_limit_middleware(request: Request, call_next):
    """
    FastAPI middleware for rate limiting.
    """
    # Skip rate limiting for health checks and static files
    if request.url.path in ["/api/health", "/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)

    # Check rate limit
    rate_limiter = TokenBucketRateLimiter()
    is_allowed, rate_info = rate_limiter.is_allowed(request)

    if not is_allowed:
        logger.warning(f"Rate limit exceeded for {request.client.host}")
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Limit: {rate_info['limit']} requests per {rate_info['window']} seconds.",
                "retry_after": rate_info["reset"] - int(time.time()),
                "rate_limit_info": rate_info,
            },
            headers={
                "X-RateLimit-Limit": str(rate_info["limit"]),
                "X-RateLimit-Remaining": str(rate_info["remaining"]),
                "X-RateLimit-Reset": str(rate_info["reset"]),
                "Retry-After": str(rate_info["reset"] - int(time.time())),
            },
        )

    # Add rate limit headers to response
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
    response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])

    return response
