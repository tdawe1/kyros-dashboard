"""
Pytest configuration and fixtures for the Kyros API tests.
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from utils.token_storage import clear_all_data


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
    with patch("utils.quotas.get_redis_client") as mock_redis_client, patch(
        "middleware.rate_limiter.redis.from_url"
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

        mock_redis_client.return_value = mock_redis_instance
        mock_redis_url.return_value = mock_redis_instance

        yield mock_redis_instance


@pytest.fixture
def mock_openai():
    """Mock OpenAI client for testing."""
    with patch("generator.OpenAI") as mock_openai_class:
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

        mock_client.chat.completions.create.return_value = mock_response
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
