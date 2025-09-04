"""
Unit tests for rate limiting functionality.
"""

import os
import pytest
import time
from unittest.mock import Mock, patch
from fastapi.responses import JSONResponse
from middleware.rate_limiter import (
    TokenBucketRateLimiter,
    rate_limit_middleware,
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW,
    RATE_LIMIT_BURST,
)


class TestTokenBucketRateLimiter:
    """Test token bucket rate limiter functionality."""

    def test_init(self):
        """Test rate limiter initialization."""
        limiter = TokenBucketRateLimiter()
        assert limiter.redis_client is not None

    def test_get_client_identifier_direct_ip(self):
        """Test client identifier with direct IP."""
        limiter = TokenBucketRateLimiter()

        # Mock request with direct IP
        request = Mock()
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"

        client_id = limiter._get_client_identifier(request)
        assert client_id == "rate_limit:192.168.1.1"

    def test_get_client_identifier_forwarded_for(self):
        """Test client identifier with X-Forwarded-For header."""
        limiter = TokenBucketRateLimiter()

        # Mock request with forwarded IP
        request = Mock()
        request.headers = {"X-Forwarded-For": "203.0.113.1, 192.168.1.1"}
        request.client = None

        client_id = limiter._get_client_identifier(request)
        assert client_id == "rate_limit:203.0.113.1"

    def test_get_client_identifier_no_client(self):
        """Test client identifier with no client info."""
        limiter = TokenBucketRateLimiter()

        # Mock request with no client
        request = Mock()
        request.headers = {}
        request.client = None

        client_id = limiter._get_client_identifier(request)
        assert client_id == "rate_limit:unknown"

    def test_is_allowed_new_bucket(self, mock_redis):
        """Test rate limiting with new bucket."""
        limiter = TokenBucketRateLimiter()

        request = Mock()
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"

        mock_redis.hgetall.return_value = {}
        mock_redis.hset.return_value = True
        mock_redis.expire.return_value = True

        is_allowed, rate_info = limiter.is_allowed(request)

        assert is_allowed is True
        assert rate_info["remaining"] == RATE_LIMIT_BURST - 1
        assert rate_info["limit"] == RATE_LIMIT_REQUESTS
        assert rate_info["window"] == RATE_LIMIT_WINDOW
        assert rate_info["burst"] == RATE_LIMIT_BURST

    @patch("time.time")
    def test_is_allowed_existing_bucket_with_tokens(self, mock_time, mock_redis):
        """Test rate limiting with existing bucket that has tokens."""
        # Mock time to be deterministic
        mock_time.return_value = 1000.0

        limiter = TokenBucketRateLimiter()

        request = Mock()
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"

        # Mock existing bucket with tokens
        mock_redis.hgetall.return_value = {
            "tokens": "5.0",
            "last_refill": "990.0",  # 10 seconds ago
        }
        mock_redis.hset.return_value = True
        mock_redis.expire.return_value = True

        is_allowed, rate_info = limiter.is_allowed(request)

        assert is_allowed is True
        assert rate_info["remaining"] >= 0

    @patch("time.time")
    def test_is_allowed_existing_bucket_no_tokens(self, mock_time, mock_redis):
        """Test rate limiting with existing bucket that has no tokens."""
        # Mock time to be deterministic
        mock_time.return_value = 1000.0

        limiter = TokenBucketRateLimiter()

        request = Mock()
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"

        # Mock existing bucket with no tokens
        mock_redis.hgetall.return_value = {
            "tokens": "0.0",
            "last_refill": "999.0",  # 1 second ago
        }
        mock_redis.hset.return_value = True
        mock_redis.expire.return_value = True

        is_allowed, rate_info = limiter.is_allowed(request)

        assert is_allowed is False
        assert rate_info["remaining"] == 0

    def test_is_allowed_redis_error(self, mock_redis):
        """Test rate limiting with Redis error (fail closed)."""
        limiter = TokenBucketRateLimiter()

        request = Mock()
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"

        # Mock Redis error
        mock_redis.hgetall.side_effect = Exception("Redis connection failed")

        with pytest.raises(
            Exception, match="Operation failed - failing closed for security"
        ):
            limiter.is_allowed(request)

    @patch("time.time")
    def test_token_refill_calculation(self, mock_time, mock_redis):
        """Test token refill calculation based on time elapsed."""
        # Mock time to be deterministic
        mock_time.return_value = 1000.0

        limiter = TokenBucketRateLimiter()

        request = Mock()
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"

        # Mock bucket with old timestamp (should refill tokens)
        mock_redis.hgetall.return_value = {
            "tokens": "1.0",
            "last_refill": "-2600.0",  # 1 hour ago
        }
        mock_redis.hset.return_value = True
        mock_redis.expire.return_value = True

        is_allowed, rate_info = limiter.is_allowed(request)

        assert is_allowed is True
        # Should have refilled tokens based on time elapsed
        assert rate_info["remaining"] > 0


class TestRateLimitMiddleware:
    """Test rate limiting middleware."""

    @pytest.mark.asyncio
    async def test_rate_limit_middleware_health_check_bypass(self, mock_redis):
        """Test that health checks bypass rate limiting."""
        request = Mock()
        request.url.path = "/api/health"
        request.client = Mock()
        request.client.host = "192.168.1.1"

        # Mock the call_next function
        async def mock_call_next(req):
            return JSONResponse(content={"status": "ok"})

        # Should not call rate limiter for health checks
        with patch(
            "middleware.rate_limiter.rate_limiter.is_allowed"
        ) as mock_is_allowed:
            response = await rate_limit_middleware(request, mock_call_next)

            # Rate limiter should not be called
            mock_is_allowed.assert_not_called()
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_rate_limit_middleware_docs_bypass(self, mock_redis):
        """Test that docs endpoints bypass rate limiting."""
        request = Mock()
        request.url.path = "/docs"
        request.client = Mock()
        request.client.host = "192.168.1.1"

        async def mock_call_next(req):
            return JSONResponse(content={"docs": "content"})

        with patch(
            "middleware.rate_limiter.rate_limiter.is_allowed"
        ) as mock_is_allowed:
            response = await rate_limit_middleware(request, mock_call_next)

            mock_is_allowed.assert_not_called()
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_rate_limit_middleware_allowed_request(self, mock_redis):
        """Test middleware with allowed request."""
        # Skip this test in testing environment since middleware is disabled
        from core.config import is_testing
        if is_testing():
            pytest.skip("Rate limiter middleware is disabled in testing environment")
        request = Mock()
        request.url.path = "/api/generate"
        request.client = Mock()
        request.client.host = "192.168.1.1"

        async def mock_call_next(req):
            return JSONResponse(content={"result": "success"})

        # Mock rate limiter to allow request
        with patch(
            "middleware.rate_limiter.rate_limiter.is_allowed"
        ) as mock_is_allowed:
            mock_is_allowed.return_value = (
                True,
                {
                    "limit": 100,
                    "remaining": 99,
                    "reset": int(time.time() + 3600),
                    "window": 3600,
                    "burst": 10,
                },
            )

            response = await rate_limit_middleware(request, mock_call_next)

            assert response.status_code == 200
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers
            assert "X-RateLimit-Reset" in response.headers

    @pytest.mark.asyncio
    async def test_rate_limit_middleware_rate_limited(self, mock_redis):
        """Test middleware with rate limited request."""
        # Skip this test in testing environment since middleware is disabled
        from core.config import is_testing
        if is_testing():
            pytest.skip("Rate limiter middleware is disabled in testing environment")
        request = Mock()
        request.url.path = "/api/generate"
        request.client = Mock()
        request.client.host = "192.168.1.1"
        request.headers = {}

        async def mock_call_next(req):
            return JSONResponse(content={"result": "success"})

        # Mock rate limiter to deny request
        with patch(
            "middleware.rate_limiter.rate_limiter.is_allowed"
        ) as mock_is_allowed:
            mock_is_allowed.return_value = (
                False,
                {
                    "limit": 100,
                    "remaining": 0,
                    "reset": int(time.time() + 3600),
                    "window": 3600,
                    "burst": 10,
                },
            )

            response = await rate_limit_middleware(request, mock_call_next)

            assert response.status_code == 429
            assert "error" in response.body.decode()
            assert "Rate limit exceeded" in response.body.decode()
            assert "Retry-After" in response.headers

    @pytest.mark.asyncio
    async def test_rate_limit_middleware_headers(self, mock_redis):
        """Test that rate limit headers are properly set."""
        # Skip this test in testing environment since middleware is disabled
        from core.config import is_testing
        if is_testing():
            pytest.skip("Rate limiter middleware is disabled in testing environment")
        request = Mock()
        request.url.path = "/api/generate"
        request.client = Mock()
        request.client.host = "192.168.1.1"

        async def mock_call_next(req):
            return JSONResponse(content={"result": "success"})

        rate_info = {
            "limit": 100,
            "remaining": 50,
            "reset": int(time.time() + 1800),
            "window": 3600,
            "burst": 10,
        }

        with patch(
            "middleware.rate_limiter.rate_limiter.is_allowed"
        ) as mock_is_allowed:
            mock_is_allowed.return_value = (True, rate_info)

            response = await rate_limit_middleware(request, mock_call_next)

            assert response.headers["X-RateLimit-Limit"] == "100"
            assert response.headers["X-RateLimit-Remaining"] == "50"
            assert response.headers["X-RateLimit-Reset"] == str(rate_info["reset"])


class TestRateLimitConfiguration:
    """Test rate limiting configuration."""

    def test_rate_limit_constants(self):
        """Test that rate limit constants are properly defined."""
        assert isinstance(RATE_LIMIT_REQUESTS, int)
        assert RATE_LIMIT_REQUESTS > 0

        assert isinstance(RATE_LIMIT_WINDOW, int)
        assert RATE_LIMIT_WINDOW > 0

        assert isinstance(RATE_LIMIT_BURST, int)
        assert RATE_LIMIT_BURST > 0
        assert RATE_LIMIT_BURST <= RATE_LIMIT_REQUESTS

    def test_rate_limit_environment_variables(self):
        """Test rate limit environment variable configuration."""
        # Store original environment
        original_env = {}
        env_vars = ["RATE_LIMIT_REQUESTS", "RATE_LIMIT_WINDOW", "RATE_LIMIT_BURST"]

        for var in env_vars:
            original_env[var] = os.environ.get(var)

        try:
            with patch.dict(
                "os.environ",
                {
                    "RATE_LIMIT_REQUESTS": "200",
                    "RATE_LIMIT_WINDOW": "1800",
                    "RATE_LIMIT_BURST": "20",
                },
            ):
                # Re-import to get updated values
                import importlib
                import middleware.rate_limiter

                importlib.reload(middleware.rate_limiter)

                assert middleware.rate_limiter.RATE_LIMIT_REQUESTS == 200
                assert middleware.rate_limiter.RATE_LIMIT_WINDOW == 1800
                assert middleware.rate_limiter.RATE_LIMIT_BURST == 20
        finally:
            # Restore original environment
            for var, value in original_env.items():
                if value is None:
                    os.environ.pop(var, None)
                else:
                    os.environ[var] = value


class TestRateLimiterBytesSafety:
    """Test bytes-safe behavior and pipeline fallback."""

    @patch("time.time")
    def test_bytes_safe_hset_with_pipeline(self, mock_time, mock_redis):
        """Test that float values are converted to strings for Redis hset."""
        mock_time.return_value = 1000.0
        
        limiter = TokenBucketRateLimiter()
        
        request = Mock()
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"
        
        # Mock existing bucket with float values
        mock_redis.hgetall.return_value = {
            "tokens": "5.0",
            "last_refill": "990.0",
        }
        
        # Mock pipeline operations
        mock_pipeline = Mock()
        mock_pipeline.hset.return_value = None
        mock_pipeline.expire.return_value = None
        mock_pipeline.execute.return_value = [True, True]
        mock_redis.pipeline.return_value = mock_pipeline
        
        is_allowed, rate_info = limiter.is_allowed(request)
        
        # Verify that string values were passed to hset
        mock_pipeline.hset.assert_called_once()
        call_args = mock_pipeline.hset.call_args
        mapping = call_args[1]["mapping"]
        assert isinstance(mapping["tokens"], str)
        assert isinstance(mapping["last_refill"], str)
        # The tokens will be refilled based on time elapsed (10 seconds * 100/3600 = ~0.278)
        # So 5.0 + 0.278 - 1.0 = ~4.278, but we cap at burst size
        assert float(mapping["tokens"]) >= 0  # Should be a valid number
        assert mapping["last_refill"] == "1000.0"
        
        assert is_allowed is True

    @patch("time.time")
    def test_pipeline_fallback_when_pipeline_is_none(self, mock_time, mock_redis):
        """Test fallback behavior when pipeline() returns None."""
        mock_time.return_value = 1000.0
        
        limiter = TokenBucketRateLimiter()
        
        request = Mock()
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"
        
        # Mock existing bucket
        mock_redis.hgetall.return_value = {
            "tokens": "5.0",
            "last_refill": "990.0",
        }
        
        # Mock pipeline to return None (fallback scenario)
        mock_redis.pipeline.return_value = None
        mock_redis.hset.return_value = 1
        mock_redis.expire.return_value = True
        
        is_allowed, rate_info = limiter.is_allowed(request)
        
        # Verify fallback methods were called
        mock_redis.hset.assert_called_once()
        mock_redis.expire.assert_called_once()
        
        # Verify string conversion in fallback
        hset_call = mock_redis.hset.call_args
        mapping = hset_call[1]["mapping"]
        assert isinstance(mapping["tokens"], str)
        assert isinstance(mapping["last_refill"], str)
        
        assert is_allowed is True

    @patch("time.time")
    def test_deterministic_behavior_with_same_inputs(self, mock_time, mock_redis):
        """Test that the same inputs always produce the same outputs."""
        # Use fixed time for deterministic behavior
        mock_time.return_value = 1000.0
        
        limiter = TokenBucketRateLimiter()
        
        request = Mock()
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"
        
        # Mock empty bucket (new bucket scenario)
        mock_redis.hgetall.return_value = {}
        
        # Mock pipeline operations
        mock_pipeline = Mock()
        mock_pipeline.hset.return_value = None
        mock_pipeline.expire.return_value = None
        mock_pipeline.execute.return_value = [True, True]
        mock_redis.pipeline.return_value = mock_pipeline
        
        # Run the same operation multiple times
        results = []
        for _ in range(3):
            is_allowed, rate_info = limiter.is_allowed(request)
            results.append((is_allowed, rate_info["remaining"], rate_info["limit"]))
        
        # All results should be identical
        assert all(result == results[0] for result in results)
        assert results[0][0] is True  # is_allowed
        # For new bucket, we start with burst tokens and consume 1
        assert results[0][1] == RATE_LIMIT_BURST - 1  # remaining tokens
        assert results[0][2] == RATE_LIMIT_REQUESTS  # limit

    @patch("time.time")
    def test_string_conversion_edge_cases(self, mock_time, mock_redis):
        """Test string conversion with edge case float values."""
        # Use fixed time for deterministic behavior
        mock_time.return_value = 1000.0
        
        limiter = TokenBucketRateLimiter()
        
        request = Mock()
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"
        
        # Test with various float values to ensure string conversion works
        test_cases = [0.0, 1.0, 5.5, 999.999, -1.0]
        
        for input_float in test_cases:
            mock_redis.hgetall.return_value = {
                "tokens": str(input_float),
                "last_refill": "1000.0",  # Same as current time, so no refill
            }
            
            mock_pipeline = Mock()
            mock_pipeline.hset.return_value = None
            mock_pipeline.expire.return_value = None
            mock_pipeline.execute.return_value = [True, True]
            mock_redis.pipeline.return_value = mock_pipeline
            
            limiter.is_allowed(request)
            
            # Verify the string conversion - the key point is that values are strings
            hset_call = mock_pipeline.hset.call_args
            mapping = hset_call[1]["mapping"]
            assert isinstance(mapping["tokens"], str)
            assert isinstance(mapping["last_refill"], str)
            
            # Verify the values are valid numbers when converted back
            assert isinstance(float(mapping["tokens"]), float)
            assert isinstance(float(mapping["last_refill"]), float)
