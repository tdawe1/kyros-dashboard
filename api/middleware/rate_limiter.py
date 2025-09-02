import os
import time
import redis
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

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

    def __init__(self):
        self.redis_client = self._get_redis_client()

    def _get_redis_client(self):
        """Get Redis client connection"""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        return redis.from_url(redis_url, decode_responses=True)

    def _get_client_identifier(self, request: Request) -> str:
        """
        Get client identifier for rate limiting.
        In production, this should use user authentication.
        For now, we'll use IP address.
        """
        # Get real IP address (considering proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        return f"rate_limit:{client_ip}"

    def is_allowed(self, request: Request) -> tuple[bool, dict]:
        """
        Check if request is allowed based on token bucket algorithm.

        Args:
            request: FastAPI request object

        Returns:
            tuple: (is_allowed: bool, rate_limit_info: dict)
        """
        try:
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

            # Update bucket state
            self.redis_client.hset(
                bucket_key, mapping={"tokens": tokens, "last_refill": current_time}
            )

            # Set expiration (cleanup old buckets)
            self.redis_client.expire(bucket_key, RATE_LIMIT_WINDOW * 2)

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

        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Fail open - allow request if Redis is down
            return True, {
                "limit": RATE_LIMIT_REQUESTS,
                "remaining": RATE_LIMIT_REQUESTS,
                "reset": int(time.time() + RATE_LIMIT_WINDOW),
                "window": RATE_LIMIT_WINDOW,
                "burst": RATE_LIMIT_BURST,
                "error": "Rate limiting temporarily disabled",
            }


# Global rate limiter instance
rate_limiter = TokenBucketRateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """
    FastAPI middleware for rate limiting.
    """
    # Skip rate limiting for health checks and static files
    if request.url.path in ["/api/health", "/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)

    # Check rate limit
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
