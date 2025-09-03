#!/usr/bin/env python3
"""
Test script for observability features:
- Sentry error reporting with job_id context
- Token usage logging and persistence
"""
import asyncio
import logging
import os
import sys

import sentry_sdk

# Add the api directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import after path modification
from generator import generate_content  # noqa: E402
from utils.token_storage import (  # noqa: E402
    clear_all_data,
    get_job_record,
    get_token_usage,
    get_token_usage_stats,
    save_job_record,
    save_token_usage,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_token_usage_logging():
    """Test token usage logging functionality."""
    print("🧪 Testing token usage logging...")

    # Clear any existing data
    clear_all_data()

    # Test data
    job_id = "test-job-123"
    test_token_usage = {
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "total_tokens": 150,
    }

    # Save token usage
    success = save_token_usage(job_id, test_token_usage, "gpt-4o-mini", "linkedin")
    assert success, "Failed to save token usage"
    print("✅ Token usage saved successfully")

    # Retrieve token usage
    retrieved_usage = get_token_usage(job_id)
    assert retrieved_usage is not None, "Failed to retrieve token usage"
    assert retrieved_usage["total_tokens"] == 150, "Token count mismatch"
    print("✅ Token usage retrieved successfully")

    # Test job record saving
    job_record = {
        "job_id": job_id,
        "user_id": "test-user",
        "input_text": "Test input text",
        "channels": ["linkedin"],
        "tone": "professional",
        "model": "gpt-4o-mini",
        "status": "completed",
    }

    success = save_job_record(job_id, job_record)
    assert success, "Failed to save job record"
    print("✅ Job record saved successfully")

    # Retrieve job record
    retrieved_job = get_job_record(job_id)
    assert retrieved_job is not None, "Failed to retrieve job record"
    assert retrieved_job["user_id"] == "test-user", "User ID mismatch"
    print("✅ Job record retrieved successfully")

    # Test statistics
    stats = get_token_usage_stats()
    assert stats["total_jobs"] == 1, "Job count mismatch in stats"
    assert stats["total_tokens"] == 150, "Total tokens mismatch in stats"
    print("✅ Statistics calculated correctly")

    print("🎉 Token usage logging tests passed!")


async def test_sentry_integration():
    """Test Sentry integration with job context."""
    print("🧪 Testing Sentry integration...")

    # Check if Sentry is configured
    sentry_dsn = os.getenv("SENTRY_DSN")
    if not sentry_dsn:
        print("⚠️  SENTRY_DSN not set, skipping Sentry tests")
        return

    # Test job context setting
    job_id = "test-sentry-job-456"

    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("job_id", job_id)
        scope.set_tag("user_id", "test-user")
        scope.set_tag("model", "gpt-4o-mini")
        scope.set_context(
            "job_details",
            {
                "channels": ["linkedin", "twitter"],
                "tone": "professional",
                "input_length": 500,
            },
        )

        # Simulate an error to test Sentry reporting
        try:
            raise ValueError("Test error for Sentry integration")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print("✅ Error captured and sent to Sentry with job context")

    print("🎉 Sentry integration tests passed!")


async def test_content_generation_with_logging():
    """Test content generation with token logging."""
    print("🧪 Testing content generation with logging...")

    # Set API mode to demo for testing
    os.environ["API_MODE"] = "demo"

    try:
        # Generate content
        job_id = "test-generation-789"
        variants = await generate_content(
            input_text="This is a test input for content generation. "
            * 10,  # Make it long enough
            channels=["linkedin", "twitter"],
            tone="professional",
            model="gpt-4o-mini",
            job_id=job_id,
        )

        assert variants is not None, "Content generation failed"
        assert "linkedin" in variants, "LinkedIn variants not generated"
        assert "twitter" in variants, "Twitter variants not generated"
        print("✅ Content generation successful")

        # Check if job record was saved (in demo mode, no real token usage)
        job_record = get_job_record(job_id)
        if job_record:
            print("✅ Job record saved during generation")
        else:
            print("ℹ️  No job record saved (expected in demo mode)")

    except Exception as e:
        print(f"❌ Content generation test failed: {str(e)}")
        raise

    print("🎉 Content generation tests passed!")


async def main():
    """Run all observability tests."""
    print("🚀 Starting observability tests...")
    print("=" * 50)

    try:
        await test_token_usage_logging()
        print()

        await test_sentry_integration()
        print()

        await test_content_generation_with_logging()
        print()

        print("=" * 50)
        print("🎉 All observability tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
