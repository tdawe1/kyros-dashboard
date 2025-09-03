"""
Pytest configuration and fixtures for the Kyros API tests.
"""

import os
import sys
from unittest.mock import Mock, patch, MagicMock, AsyncMock

import pytest
from fastapi.testclient import TestClient

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def pytest_configure(config):
    """
    Pytest hook to configure and patch settings before tests are run.
    This is used to mock the Redis client at the earliest point possible
    to prevent connection attempts during module import.

    Updated to fix CI compatibility issues with pytest 8.4.1.
    """
    # Create a mock Redis client that can be used by SecureRedisClient
    mock_redis_instance = MagicMock()
    mock_redis_instance.ping.return_value = True
    mock_redis_instance.get.return_value = None
    mock_redis_instance.incr.return_value = 1
    mock_redis_instance.expire.return_value = True
    mock_redis_instance.delete.return_value = True
    mock_redis_instance.hgetall.return_value = {}
    mock_redis_instance.hset.return_value = True

    # The rate limiter uses a pipeline, so we need to mock that too
    mock_pipeline = MagicMock()
    mock_pipeline.hset.return_value = mock_pipeline
    mock_pipeline.expire.return_value = mock_pipeline
    mock_pipeline.execute.return_value = []
    mock_redis_instance.pipeline.return_value = mock_pipeline

    # Patch the from_url function in core.security where the client is created
    patcher = patch("core.security.redis.from_url", return_value=mock_redis_instance)

    # Start the patcher - it will be automatically stopped when the process ends
    patcher.start()

    # Store the patcher in config for cleanup if needed
    config._redis_patcher = patcher

    # Force CI cache refresh - this line ensures the latest version is used


# Import the app after the patch has been applied
from main import app  # noqa: E402
from utils.token_storage import clear_all_data  # noqa: E402


@pytest.fixture(scope="function")
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(scope="function")
def clean_storage():
    """Clear all storage data before each test."""
    clear_all_data()
    yield
    clear_all_data()


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    with patch("utils.quotas.get_secure_redis_client") as mock_redis_client, patch(
        "middleware.rate_limiter.get_secure_redis_client"
    ) as mock_redis_url:
        # Create a mock Redis instance
        mock_redis_instance = Mock()
        mock_redis_instance.get.return_value = None
        mock_redis_instance.incr.return_value = 1
        mock_redis_instance.expire.return_value = True
        mock_redis_instance.delete.return_value = True
        mock_redis_instance.hgetall.return_value = {}
        mock_redis_instance.hset.return_value = True
        mock_redis_instance.expire.return_value = True

        # Mock the pipeline
        mock_pipeline = Mock()
        mock_pipeline.get.return_value = mock_pipeline
        mock_pipeline.incr.return_value = mock_pipeline
        mock_pipeline.expire.return_value = mock_pipeline
        mock_pipeline.execute.side_effect = lambda: [
            mock_redis_instance.get.return_value,
            mock_redis_instance.incr.return_value,
        ]
        mock_redis_instance._client.pipeline.return_value = mock_pipeline

        mock_redis_client.return_value = mock_redis_instance
        mock_redis_url.return_value = mock_redis_instance

        yield mock_redis_instance


@pytest.fixture
def mock_openai():
    """Mock OpenAI client for testing."""
    with patch("generator.AsyncOpenAI") as mock_openai_class:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[
            0
        ].message.content = '{"text": "Test content", "length": 100}'
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 100
        mock_response.usage.total_tokens = 150

        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai_class.return_value = mock_client

        yield mock_client


@pytest.fixture
def sample_input_text():
    """Sample input text for testing."""
    return """
    Artificial intelligence is transforming the way we work and live.
    From machine learning algorithms that power recommendation systems
    to natural language processing that enables chatbots, AI is becoming
    increasingly integrated into our daily lives. Companies are leveraging
    AI to improve efficiency, reduce costs, and enhance customer experiences.
    However, with these benefits come challenges around ethics, privacy,
    and the future of work. As we continue to develop and deploy AI systems,
    it's crucial that we consider the broader implications and ensure that
    these technologies are developed responsibly.
    """


@pytest.fixture
def sample_generate_request():
    """Sample generate request for testing."""
    return {
        "input_text": "This is a test article about artificial intelligence and its impact on modern business. The technology is rapidly evolving and changing how we approach problem-solving.",
        "channels": ["linkedin", "twitter"],
        "tone": "professional",
        "preset": "default",
        "user_id": "test_user_123",
        "model": "gpt-4o-mini",
    }


@pytest.fixture
def sample_variants():
    """Sample variants response for testing."""
    return {
        "linkedin": [
            {
                "id": "test_linkedin_1",
                "text": "🚀 Exciting insights from our latest research on AI...",
                "length": 150,
                "readability": "Good",
                "tone": "professional",
            }
        ],
        "twitter": [
            {
                "id": "test_twitter_1",
                "text": "Thread: AI is transforming business... 1/5",
                "length": 280,
                "readability": "Good",
                "tone": "professional",
            }
        ],
    }
