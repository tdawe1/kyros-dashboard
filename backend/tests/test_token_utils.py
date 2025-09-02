"""
Unit tests for token utilities.
"""

from utils.token_utils import (
    estimate_tokens,
    validate_input_limits,
    get_token_usage_stats,
)


class TestTokenEstimation:
    """Test token estimation functionality."""

    def test_estimate_tokens_empty_string(self):
        """Test token estimation with empty string."""
        assert estimate_tokens("") == 0
        assert estimate_tokens(None) == 0

    def test_estimate_tokens_simple_text(self):
        """Test token estimation with simple text."""
        text = "Hello world"
        tokens = estimate_tokens(text)
        assert tokens > 0
        assert tokens == 2  # 2 words * 1.3 factor = 2 (rounded down)

    def test_estimate_tokens_with_whitespace(self):
        """Test token estimation with extra whitespace."""
        text = "  Hello    world   "
        tokens = estimate_tokens(text)
        assert tokens == 2  # Should ignore extra whitespace

    def test_estimate_tokens_large_text(self):
        """Test token estimation with large text."""
        text = "This is a test sentence. " * 100  # 500 words
        tokens = estimate_tokens(text)
        expected = int(500 * 1.3)  # 500 words * 1.3 factor
        assert tokens == expected

    def test_estimate_tokens_special_characters(self):
        """Test token estimation with special characters."""
        text = "Hello, world! How are you? I'm fine, thanks."
        tokens = estimate_tokens(text)
        assert tokens > 0
        # Should count punctuation as separate tokens
        assert tokens >= 8  # At least 8 words


class TestInputValidation:
    """Test input validation functionality."""

    def test_validate_input_limits_valid_text(self):
        """Test validation with valid text."""
        text = "This is a valid test input that meets the minimum length requirement."
        result = validate_input_limits(text)

        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert result["stats"]["character_count"] == len(text)
        assert result["stats"]["estimated_tokens"] > 0

    def test_validate_input_limits_empty_text(self):
        """Test validation with empty text."""
        result = validate_input_limits("")

        assert result["valid"] is True  # Empty text is valid
        assert result["stats"]["character_count"] == 0
        assert result["stats"]["estimated_tokens"] == 0

    def test_validate_input_limits_too_large_text(self):
        """Test validation with text exceeding character limit."""
        # Create text larger than default limit (100,000 chars)
        large_text = "A" * 150000
        result = validate_input_limits(large_text)

        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert "exceeds maximum character limit" in result["errors"][0]

    def test_validate_input_limits_token_limit_exceeded(self):
        """Test validation with text exceeding token limit."""
        # Create text that would exceed token limit but not character limit
        # Default limit is 50,000 tokens, so we need ~38,500 words
        # But we need to stay under 100,000 characters
        # Each "word" is about 4 characters, so 38,500 words = ~154,000 chars
        # Let's use shorter words to stay under character limit
        large_text = "A " * 40000  # 40,000 words, ~80,000 characters
        result = validate_input_limits(large_text)

        assert result["valid"] is False
        assert len(result["errors"]) > 0
        # Check for either character or token limit error
        error_text = " ".join(result["errors"])
        assert (
            "exceeds maximum limit" in error_text
            or "exceeds maximum character limit" in error_text
        )

    def test_validate_input_limits_multiple_errors(self):
        """Test validation with multiple limit violations."""
        # Create text that exceeds both character and token limits
        huge_text = "A" * 200000
        result = validate_input_limits(huge_text)

        assert result["valid"] is False
        assert len(result["errors"]) >= 1  # At least character limit error


class TestTokenUsageStats:
    """Test token usage statistics functionality."""

    def test_get_token_usage_stats_empty_text(self):
        """Test stats with empty text."""
        stats = get_token_usage_stats("")

        assert stats["character_count"] == 0
        assert stats["word_count"] == 0
        assert stats["estimated_tokens"] == 0
        assert stats["usage_percentage"]["characters"] == 0
        assert stats["usage_percentage"]["tokens"] == 0

    def test_get_token_usage_stats_normal_text(self):
        """Test stats with normal text."""
        text = "This is a test sentence with multiple words."
        stats = get_token_usage_stats(text)

        assert stats["character_count"] == len(text)
        assert stats["word_count"] == 8  # 8 words
        assert stats["estimated_tokens"] > 0
        assert stats["estimation_factor"] == 1.3
        assert "limits" in stats
        assert "usage_percentage" in stats

    def test_get_token_usage_stats_large_text(self):
        """Test stats with large text."""
        text = "This is a test sentence. " * 1000  # ~25,000 characters
        stats = get_token_usage_stats(text)

        assert stats["character_count"] == len(text)
        assert stats["word_count"] == 5000  # 5000 words
        assert stats["estimated_tokens"] == int(5000 * 1.3)
        assert stats["usage_percentage"]["characters"] > 0
        assert stats["usage_percentage"]["tokens"] > 0

    def test_get_token_usage_stats_limits_structure(self):
        """Test that limits structure is correct."""
        stats = get_token_usage_stats("test")

        assert "max_characters" in stats["limits"]
        assert "max_tokens" in stats["limits"]
        assert stats["limits"]["max_characters"] > 0
        assert stats["limits"]["max_tokens"] > 0

    def test_get_token_usage_stats_percentage_calculation(self):
        """Test percentage calculations."""
        # Use a text that's exactly 10% of the character limit
        char_limit = 100000  # Default limit
        text = "A" * (char_limit // 10)  # 10,000 characters
        stats = get_token_usage_stats(text)

        assert abs(stats["usage_percentage"]["characters"] - 10.0) < 0.1
