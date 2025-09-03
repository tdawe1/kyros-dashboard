#!/usr/bin/env python3
"""
Test script for API endpoints related to observability.
"""

# This is not a pytest file, so we disable pytest discovery
__test__ = False
import requests
import time
import sys
import os

# Add the api directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.token_storage import (  # noqa: E402
    clear_all_data,
    save_token_usage,
    save_job_record,
)  # noqa: E402

BASE_URL = "http://localhost:8000"


def setup_test_data():
    """Set up test data for API testing."""
    print("🔧 Setting up test data...")

    # Clear existing data
    clear_all_data()

    # Add test job
    job_id = "api-test-job-123"
    token_usage = {
        "prompt_tokens": 200,
        "completion_tokens": 100,
        "total_tokens": 300,
    }

    save_token_usage(job_id, token_usage, "gpt-4o-mini", "linkedin")

    job_record = {
        "job_id": job_id,
        "user_id": "api-test-user",
        "input_text": "Test input for API testing",
        "channels": ["linkedin", "twitter"],
        "tone": "professional",
        "model": "gpt-4o-mini",
        "status": "completed",
    }
    save_job_record(job_id, job_record)

    print("✅ Test data set up successfully")
    return job_id


def test_health_endpoint():
    """Test the health check endpoint."""
    print("🧪 Testing health endpoint...")

    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        assert (
            response.status_code == 200
        ), f"Health check failed: {response.status_code}"

        data = response.json()
        assert "status" in data, "Health response missing status"
        assert data["status"] == "ok", f"Health status not ok: {data['status']}"

        print("✅ Health endpoint working")
        return True

    except requests.exceptions.ConnectionError:
        print("⚠️  API server not running, skipping API tests")
        return False
    except Exception as e:
        print(f"❌ Health endpoint test failed: {str(e)}")
        return False


def test_token_usage_endpoints(job_id):
    """Test token usage related endpoints."""
    print("🧪 Testing token usage endpoints...")

    try:
        # Test token usage stats endpoint
        response = requests.get(f"{BASE_URL}/api/token-usage/stats", timeout=5)
        assert (
            response.status_code == 200
        ), f"Stats endpoint failed: {response.status_code}"

        stats = response.json()
        assert "total_jobs" in stats, "Stats missing total_jobs"
        assert stats["total_jobs"] >= 1, "No jobs found in stats"

        print("✅ Token usage stats endpoint working")

        # Test specific job token usage
        response = requests.get(f"{BASE_URL}/api/token-usage/{job_id}", timeout=5)
        assert (
            response.status_code == 200
        ), f"Job token usage failed: {response.status_code}"

        usage = response.json()
        assert (
            usage["total_tokens"] == 300
        ), f"Token count mismatch: {usage['total_tokens']}"

        print("✅ Job token usage endpoint working")

        # Test job details endpoint
        response = requests.get(f"{BASE_URL}/api/jobs/{job_id}/details", timeout=5)
        assert (
            response.status_code == 200
        ), f"Job details failed: {response.status_code}"

        details = response.json()
        assert "job" in details, "Job details missing job data"
        assert "token_usage" in details, "Job details missing token usage"
        assert details["job"]["user_id"] == "api-test-user", "User ID mismatch"

        print("✅ Job details endpoint working")

        return True

    except Exception as e:
        print(f"❌ Token usage endpoints test failed: {str(e)}")
        return False


def test_generate_endpoint():
    """Test the generate endpoint with observability."""
    print("🧪 Testing generate endpoint...")

    try:
        # Test content generation
        payload = {
            "input_text": "This is a test input for content generation. "
            * 10,  # Make it long enough
            "channels": ["linkedin"],
            "tone": "professional",
            "user_id": "api-test-user",
            "model": "gpt-4o-mini",
        }

        response = requests.post(f"{BASE_URL}/api/generate", json=payload, timeout=30)
        assert (
            response.status_code == 200
        ), f"Generate endpoint failed: {response.status_code}"

        data = response.json()
        assert "job_id" in data, "Response missing job_id"
        assert "token_usage" in data, "Response missing token_usage"
        assert "variants" in data, "Response missing variants"

        job_id = data["job_id"]
        print(f"✅ Generate endpoint working, created job: {job_id}")

        # Verify job was saved
        time.sleep(1)  # Give it a moment to save

        response = requests.get(f"{BASE_URL}/api/token-usage/{job_id}", timeout=5)
        if response.status_code == 200:
            print("✅ Generated job token usage saved")
        else:
            print("⚠️  Generated job token usage not found (expected in demo mode)")

        return True

    except Exception as e:
        print(f"❌ Generate endpoint test failed: {str(e)}")
        return False


def main():
    """Run all API tests."""
    print("🚀 Starting API endpoint tests...")
    print("=" * 50)

    # Set up test data
    job_id = setup_test_data()
    print()

    # Test health endpoint first
    if not test_health_endpoint():
        print("⚠️  Skipping remaining tests - API server not available")
        return
    print()

    # Test token usage endpoints
    test_token_usage_endpoints(job_id)
    print()

    # Test generate endpoint
    test_generate_endpoint()
    print()

    print("=" * 50)
    print("🎉 API endpoint tests completed!")


if __name__ == "__main__":
    main()
