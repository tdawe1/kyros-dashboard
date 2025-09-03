#!/usr/bin/env python3
"""
Simple test script for observability features that doesn't require external dependencies.
"""

import os
import sys
import logging

from utils.token_storage import (
    save_token_usage,
    get_token_usage,
    save_job_record,
    get_job_record,
    get_token_usage_stats,
    clear_all_data,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_token_usage_logging():
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


def test_multiple_jobs():
    """Test handling multiple jobs."""
    print("🧪 Testing multiple jobs...")

    # Clear data
    clear_all_data()

    # Add multiple jobs
    for i in range(3):
        job_id = f"test-job-{i}"
        token_usage = {
            "prompt_tokens": 100 + i * 10,
            "completion_tokens": 50 + i * 5,
            "total_tokens": 150 + i * 15,
        }

        save_token_usage(job_id, token_usage, "gpt-4o-mini", "linkedin")

        job_record = {
            "job_id": job_id,
            "user_id": f"test-user-{i}",
            "input_text": f"Test input {i}",
            "channels": ["linkedin"],
            "tone": "professional",
            "model": "gpt-4o-mini",
            "status": "completed",
        }
        save_job_record(job_id, job_record)

    # Check statistics
    stats = get_token_usage_stats()
    assert stats["total_jobs"] == 3, f"Expected 3 jobs, got {stats['total_jobs']}"
    assert stats["total_tokens"] == 150 + 165 + 180, (
        f"Token count mismatch: {stats['total_tokens']}"
    )

    print("✅ Multiple jobs handled correctly")
    print("🎉 Multiple jobs tests passed!")


def test_sentry_configuration():
    """Test Sentry configuration without actually sending data."""
    print("🧪 Testing Sentry configuration...")

    # Check environment variables
    sentry_dsn = os.getenv("SENTRY_DSN")
    environment = os.getenv("ENVIRONMENT", "development")
    release = os.getenv("RELEASE_VERSION", "1.0.0")

    print(f"📊 Sentry DSN configured: {'Yes' if sentry_dsn else 'No'}")
    print(f"📊 Environment: {environment}")
    print(f"📊 Release: {release}")

    if sentry_dsn:
        print("✅ Sentry configuration found")
    else:
        print("⚠️  Sentry DSN not configured (expected in development)")

    print("🎉 Sentry configuration tests passed!")


def main():
    """Run all observability tests."""
    print("🚀 Starting observability tests...")
    print("=" * 50)

    try:
        test_token_usage_logging()
        print()

        test_multiple_jobs()
        print()

        test_sentry_configuration()
        print()

        print("=" * 50)
        print("🎉 All observability tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
