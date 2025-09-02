#!/usr/bin/env python3
"""
Stress test script for Phase B - Token & Cost Controls
Tests rate limiting, quota enforcement, and input validation.
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Any
import argparse

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "stress_test_user"
LARGE_TEXT = "This is a test sentence. " * 1000  # ~25,000 characters
EXTRA_LARGE_TEXT = (
    "This is a test sentence. " * 5000
)  # ~125,000 characters (exceeds limit)


class StressTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = None
        self.results = {
            "rate_limiting": [],
            "quota_enforcement": [],
            "input_validation": [],
            "token_estimation": [],
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def make_request(
        self, endpoint: str, method: str = "GET", data: Dict = None
    ) -> Dict[str, Any]:
        """Make HTTP request and return response data"""
        url = f"{self.base_url}{endpoint}"

        try:
            if method == "GET":
                async with self.session.get(url) as response:
                    return {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "data": (
                            await response.json()
                            if response.content_type == "application/json"
                            else await response.text()
                        ),
                    }
            elif method == "POST":
                async with self.session.post(url, json=data) as response:
                    return {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "data": (
                            await response.json()
                            if response.content_type == "application/json"
                            else await response.text()
                        ),
                    }
        except Exception as e:
            return {"error": str(e), "status": 0}

    async def test_rate_limiting(self, num_requests: int = 20) -> List[Dict]:
        """Test rate limiting by making many rapid requests"""
        print(f"Testing rate limiting with {num_requests} rapid requests...")

        tasks = []
        start_time = time.time()

        for i in range(num_requests):
            task = self.make_request("/api/health")
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        end_time = time.time()

        # Analyze results
        success_count = sum(1 for r in responses if r.get("status") == 200)
        rate_limited_count = sum(1 for r in responses if r.get("status") == 429)
        error_count = sum(1 for r in responses if r.get("status") not in [200, 429])

        print("Rate limiting test results:")
        print(f"  Total requests: {num_requests}")
        print(f"  Successful: {success_count}")
        print(f"  Rate limited (429): {rate_limited_count}")
        print(f"  Errors: {error_count}")
        print(f"  Duration: {end_time - start_time:.2f}s")

        return responses

    async def test_quota_enforcement(self, user_id: str = TEST_USER_ID) -> List[Dict]:
        """Test quota enforcement by exceeding daily limit"""
        print(f"Testing quota enforcement for user {user_id}...")

        # First, reset quota to start fresh
        await self.make_request(f"/api/quota/{user_id}/reset", "POST")

        # Check initial quota status
        quota_status = await self.make_request(f"/api/quota/{user_id}")
        print(f"Initial quota status: {quota_status.get('data', {})}")

        # Make requests until quota is exceeded
        responses = []
        daily_limit = 10  # Default limit

        for i in range(daily_limit + 3):  # Try to exceed limit
            request_data = {
                "input_text": f"Test content for quota enforcement test {i}. "
                * 10,  # ~500 chars
                "channels": ["linkedin"],
                "user_id": user_id,
            }

            response = await self.make_request("/api/generate", "POST", request_data)
            responses.append(response)

            if response.get("status") == 400:
                error_data = response.get("data", {})
                if "quota exceeded" in str(error_data).lower():
                    print(f"Quota exceeded at request {i + 1}")
                    break

            print(f"Request {i + 1}: Status {response.get('status')}")

        # Check final quota status
        final_quota = await self.make_request(f"/api/quota/{user_id}")
        print(f"Final quota status: {final_quota.get('data', {})}")

        return responses

    async def test_input_validation(self) -> List[Dict]:
        """Test input validation with various text sizes"""
        print("Testing input validation...")

        test_cases = [
            {"name": "Too short", "text": "Short", "expected_status": 400},
            {
                "name": "Valid size",
                "text": "This is a valid test input that meets the minimum length requirement. "
                * 2,
                "expected_status": 200,
            },
            {"name": "Large but valid", "text": LARGE_TEXT, "expected_status": 200},
            {
                "name": "Too large (characters)",
                "text": EXTRA_LARGE_TEXT,
                "expected_status": 400,
            },
        ]

        responses = []

        for test_case in test_cases:
            print(f"Testing: {test_case['name']}")

            request_data = {
                "input_text": test_case["text"],
                "channels": ["linkedin"],
                "user_id": "validation_test_user",
            }

            response = await self.make_request("/api/generate", "POST", request_data)
            responses.append(
                {
                    "test_case": test_case["name"],
                    "response": response,
                    "expected": test_case["expected_status"],
                    "actual": response.get("status"),
                    "passed": response.get("status") == test_case["expected_status"],
                }
            )

            print(
                f"  Expected: {test_case['expected_status']}, Got: {response.get('status')}"
            )

        return responses

    async def test_token_estimation(self) -> List[Dict]:
        """Test token estimation endpoint"""
        print("Testing token estimation...")

        test_texts = [
            "Short text",
            "This is a medium length text that should give us a reasonable token estimate. "
            * 10,
            LARGE_TEXT,
        ]

        responses = []

        for i, text in enumerate(test_texts):
            print(f"Testing text {i + 1} ({len(text)} characters)")

            request_data = {
                "input_text": text,
                "channels": ["linkedin"],
                "user_id": "token_test_user",
            }

            response = await self.make_request("/api/token-stats", "POST", request_data)
            responses.append({"text_length": len(text), "response": response})

            if response.get("status") == 200:
                data = response.get("data", {})
                token_stats = data.get("token_stats", {})
                print(
                    f"  Estimated tokens: {token_stats.get('estimated_tokens', 'N/A')}"
                )
                print(f"  Word count: {token_stats.get('word_count', 'N/A')}")

        return responses

    async def run_all_tests(self):
        """Run all stress tests"""
        print("Starting Phase B stress tests...")
        print("=" * 50)

        # Test 1: Rate limiting
        self.results["rate_limiting"] = await self.test_rate_limiting()
        print()

        # Test 2: Quota enforcement
        self.results["quota_enforcement"] = await self.test_quota_enforcement()
        print()

        # Test 3: Input validation
        self.results["input_validation"] = await self.test_input_validation()
        print()

        # Test 4: Token estimation
        self.results["token_estimation"] = await self.test_token_estimation()
        print()

        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("=" * 50)
        print("STRESS TEST SUMMARY")
        print("=" * 50)

        # Rate limiting summary
        rate_limited = sum(
            1 for r in self.results["rate_limiting"] if r.get("status") == 429
        )
        print(f"Rate Limiting: {rate_limited} requests rate limited")

        # Quota enforcement summary
        quota_exceeded = sum(
            1 for r in self.results["quota_enforcement"] if r.get("status") == 400
        )
        print(f"Quota Enforcement: {quota_exceeded} requests blocked by quota")

        # Input validation summary
        validation_passed = sum(
            1 for r in self.results["input_validation"] if r.get("passed", False)
        )
        total_validation = len(self.results["input_validation"])
        print(f"Input Validation: {validation_passed}/{total_validation} tests passed")

        # Token estimation summary
        token_tests = len(self.results["token_estimation"])
        print(f"Token Estimation: {token_tests} tests completed")

        print("\nAll tests completed!")


async def main():
    parser = argparse.ArgumentParser(description="Stress test Phase B features")
    parser.add_argument("--url", default=BASE_URL, help="API base URL")
    parser.add_argument("--user", default=TEST_USER_ID, help="Test user ID")
    parser.add_argument(
        "--requests", type=int, default=20, help="Number of rate limit test requests"
    )

    args = parser.parse_args()

    async with StressTester(args.url) as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
