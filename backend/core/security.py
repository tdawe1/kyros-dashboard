"""
Security utilities and fail-closed patterns for Kyros Dashboard.
Implements secure error handling and circuit breaker patterns.
"""

import os
import time
import logging
from typing import Optional, Dict, Any, Callable
from enum import Enum
from functools import wraps
import redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""

    pass


class SecurityMode(Enum):
    """Security operation modes."""

    FAIL_CLOSED = "fail_closed"  # Deny on error
    FAIL_OPEN = "fail_open"  # Allow on error (insecure)
    GRACEFUL = "graceful"  # Graceful degradation


class CircuitBreakerState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service is back


class CircuitBreaker:
    """
    Circuit breaker implementation for external service calls.
    Prevents cascading failures by failing fast when services are down.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
        name: str = "default",
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.name = name

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED

        logger.info(
            f"Circuit breaker '{name}' initialized with threshold {failure_threshold}"
        )

    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info(f"Circuit breaker '{self.name}' entering HALF_OPEN state")
            else:
                raise CircuitBreakerOpenError(f"Circuit breaker '{self.name}' is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        return (
            self.last_failure_time
            and time.time() - self.last_failure_time >= self.recovery_timeout
        )

    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(
                f"Circuit breaker '{self.name}' opened after {self.failure_count} failures"
            )


class SecureRedisClient:
    """
    Secure Redis client with fail-closed behavior.
    """

    def __init__(
        self, redis_url: str, security_mode: SecurityMode = SecurityMode.FAIL_CLOSED
    ):
        self.redis_url = redis_url
        self.security_mode = security_mode
        self._client: Optional[redis.Redis] = None
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=30,
            expected_exception=RedisError,
            name="redis",
        )
        self._connect()

    def _connect(self):
        """Establish Redis connection."""
        try:
            self._client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self._client.ping()
            logger.info("Redis connection established successfully")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            if self.security_mode == SecurityMode.FAIL_CLOSED:
                raise Exception("Redis connection failed - failing closed for security")
            self._client = None

    def _execute_with_circuit_breaker(self, operation: str, *args, **kwargs):
        """Execute Redis operation with circuit breaker protection."""
        if not self._client:
            if self.security_mode == SecurityMode.FAIL_CLOSED:
                raise Exception("Redis not available - failing closed for security")
            return None

        def _operation():
            return getattr(self._client, operation)(*args, **kwargs)

        return self._circuit_breaker.call(_operation)

    def incr(self, key: str) -> int:
        """Increment key with circuit breaker protection."""
        result = self._execute_with_circuit_breaker("incr", key)
        if result is None and self.security_mode == SecurityMode.FAIL_CLOSED:
            raise Exception("Redis operation failed - failing closed for security")
        return result or 0

    def get(self, key: str) -> Optional[str]:
        """Get key with circuit breaker protection."""
        result = self._execute_with_circuit_breaker("get", key)
        if result is None and self.security_mode == SecurityMode.FAIL_CLOSED:
            raise Exception("Redis operation failed - failing closed for security")
        return result

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set key with circuit breaker protection."""
        result = self._execute_with_circuit_breaker("set", key, value, ex=ex)
        if result is None and self.security_mode == SecurityMode.FAIL_CLOSED:
            raise Exception("Redis operation failed - failing closed for security")
        return result or False

    def expire(self, key: str, time: int) -> bool:
        """Set expiration with circuit breaker protection."""
        result = self._execute_with_circuit_breaker("expire", key, time)
        if result is None and self.security_mode == SecurityMode.FAIL_CLOSED:
            raise Exception("Redis operation failed - failing closed for security")
        return result or False

    def delete(self, key: str) -> int:
        """Delete key with circuit breaker protection."""
        result = self._execute_with_circuit_breaker("delete", key)
        if result is None and self.security_mode == SecurityMode.FAIL_CLOSED:
            raise Exception("Redis operation failed - failing closed for security")
        return result or 0

    def hset(self, key: str, mapping: Dict[str, Any]) -> int:
        """Hash set with circuit breaker protection."""
        result = self._execute_with_circuit_breaker("hset", key, mapping=mapping)
        if result is None and self.security_mode == SecurityMode.FAIL_CLOSED:
            raise Exception("Redis operation failed - failing closed for security")
        return result or 0

    def hgetall(self, key: str) -> Dict[str, str]:
        """Hash get all with circuit breaker protection."""
        result = self._execute_with_circuit_breaker("hgetall", key)
        if result is None and self.security_mode == SecurityMode.FAIL_CLOSED:
            raise Exception("Redis operation failed - failing closed for security")
        return result or {}


def secure_operation(
    security_mode: SecurityMode = SecurityMode.FAIL_CLOSED,
    fallback_value: Any = None,
    log_errors: bool = True,
):
    """
    Decorator for secure operations with configurable failure behavior.

    Args:
        security_mode: How to handle failures
        fallback_value: Value to return on failure in graceful mode
        log_errors: Whether to log errors
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(f"Secure operation failed in {func.__name__}: {e}")

                if security_mode == SecurityMode.FAIL_CLOSED:
                    raise Exception(
                        f"Operation failed - failing closed for security: {e}"
                    )
                elif security_mode == SecurityMode.GRACEFUL:
                    return fallback_value
                else:  # FAIL_OPEN
                    logger.warning(f"Operation failed but allowing continuation: {e}")
                    return fallback_value

        return wrapper

    return decorator


def get_secure_redis_client() -> SecureRedisClient:
    """Get secure Redis client with fail-closed behavior."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Validate REDIS_SECURITY_MODE
    mode_str = os.getenv("REDIS_SECURITY_MODE", "fail_closed")
    try:
        security_mode = SecurityMode(mode_str)
    except ValueError:
        logger.warning(
            f"Invalid REDIS_SECURITY_MODE '{mode_str}', defaulting to 'fail_closed'"
        )
        security_mode = SecurityMode.FAIL_CLOSED

    return SecureRedisClient(redis_url, security_mode)


# Global circuit breakers for external services
openai_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=Exception,
    name="openai",
)


def with_circuit_breaker(circuit_breaker: CircuitBreaker):
    """Decorator to apply circuit breaker to function."""

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return circuit_breaker.call(func, *args, **kwargs)

        return wrapper

    return decorator
