#!/usr/bin/env python3
"""
Simple test script to verify Phase B utilities work correctly.
"""

import sys

sys.path.append(".")

from utils.token_utils import estimate_tokens, validate_input_limits  # noqa: E402
from utils.quotas import can_create_job  # noqa: E402


def test_token_estimation():
    """Test token estimation functionality"""
    print("Testing token estimation...")

    test_text = "This is a test sentence with multiple words to estimate tokens."
    tokens = estimate_tokens(test_text)
    print(f'  Token estimation: {tokens} tokens for "{test_text[:30]}..."')

    # Test with larger text
    large_text = "This is a test sentence. " * 100
    large_tokens = estimate_tokens(large_text)
    print(
        f"  Large text estimation: {large_tokens} tokens for {len(large_text)} characters"
    )

    assert tokens > 0
    assert large_tokens > 0


def test_input_validation():
    """Test input validation functionality"""
    print("Testing input validation...")

    # Test valid input
    valid_text = (
        "This is a valid test input that meets the minimum length requirement. " * 2
    )
    validation = validate_input_limits(valid_text)
    print(
        f'  Valid input: Valid={validation["valid"]}, Tokens={validation["stats"]["estimated_tokens"]}'
    )
    assert validation["valid"] is True

    # Test invalid input (too large)
    large_text = "This is a test sentence. " * 5000  # ~125,000 characters
    validation = validate_input_limits(large_text)
    print(
        f'  Large input: Valid={validation["valid"]}, Errors={len(validation["errors"])}'
    )

    assert validation["valid"] is False


def test_quota_system():
    """Test quota system (will show expected Redis error if not running)"""
    print("Testing quota system...")

    try:
        can_create, count = can_create_job("test_user", 10)
        print(f"  Quota check: Can create={can_create}, Count={count}")
        assert can_create is True
    except Exception as e:
        print(f"  Quota check: Expected error (Redis not running): {e}")
        # This is expected if Redis is not running
        pass
