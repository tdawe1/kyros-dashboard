"""
Pytest configuration and fixtures for the backend tests.
"""

import os
import pytest
from unittest.mock import patch
from dotenv import load_dotenv


@pytest.fixture(autouse=True)
def test_environment():
    """Set up test environment variables for all tests."""
    # Load test environment variables
    test_env_path = os.path.join(os.path.dirname(__file__), "env.test")
    if os.path.exists(test_env_path):
        load_dotenv(test_env_path, override=True)
    
    # Set additional test-specific environment variables
    test_env = {
        "ENVIRONMENT": "testing",
        "API_MODE": "demo",
        "DEFAULT_MODEL": "gpt-4o-mini",
        "MAX_INPUT_CHARACTERS": "100000",
        "MAX_TOKENS_PER_JOB": "50000",
        "DAILY_JOB_LIMIT": "50",
        "RATE_LIMIT_REQUESTS": "1000",
        "RATE_LIMIT_WINDOW": "3600",
        "RATE_LIMIT_BURST": "50",
        "API_HOST": "0.0.0.0",
        "API_PORT": "8000",
        "DATABASE_URL": "sqlite:///./test_kyros.db",
        "REDIS_URL": "redis://localhost:6379",
        "RELEASE_VERSION": "1.0.0-test",
        # Ensure no real OpenAI API key is used in tests
        "OPENAI_API_KEY": "",
    }
    
    with patch.dict(os.environ, test_env, clear=False):
        yield


@pytest.fixture(autouse=True)
def mock_openai_calls():
    """Mock OpenAI API calls to prevent real API requests during testing."""
    with patch("openai.OpenAI") as mock_openai:
        # Configure mock to return a default response
        mock_client = mock_openai.return_value
        mock_response = mock_client.chat.completions.create.return_value
        mock_response.choices = [type("Choice", (), {
            "message": type("Message", (), {
                "content": "Mocked response"
            })()
        })()]
        mock_response.usage = type("Usage", (), {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        })()
        
        yield mock_openai


@pytest.fixture(autouse=True)
def mock_redis_calls():
    """Mock Redis calls to prevent real Redis connections during testing."""
    with patch("redis.from_url") as mock_redis:
        mock_redis_instance = mock_redis.return_value
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.hgetall.return_value = {}
        mock_redis_instance.hset.return_value = True
        mock_redis_instance.hdel.return_value = True
        mock_redis_instance.expire.return_value = True
        mock_redis_instance.exists.return_value = False
        
        yield mock_redis
