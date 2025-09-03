"""
Unit tests for content generator functionality.
"""

import pytest
import os
from unittest.mock import patch, Mock, AsyncMock
from generator import (
    get_demo_variants,
    generate_content_real,
    generate_content,
    VALID_MODELS,
)


class TestDemoVariants:
    """Test demo variant generation."""

    @pytest.mark.asyncio
    async def test_get_demo_variants_linkedin(self, sample_input_text):
        """Test LinkedIn demo variants generation."""
        variants = await get_demo_variants(
            sample_input_text, ["linkedin"], "professional"
        )

        assert "linkedin" in variants
        assert len(variants["linkedin"]) == 3

        for variant in variants["linkedin"]:
            assert "id" in variant
            assert "text" in variant
            assert "length" in variant
            assert "readability" in variant
            assert "tone" in variant
            assert variant["tone"] == "professional"
            assert variant["id"].startswith("demo_linkedin_")

    @pytest.mark.asyncio
    async def test_get_demo_variants_twitter(self, sample_input_text):
        """Test Twitter demo variants generation."""
        variants = await get_demo_variants(sample_input_text, ["twitter"], "engaging")

        assert "twitter" in variants
        assert len(variants["twitter"]) == 5

        for variant in variants["twitter"]:
            assert "id" in variant
            assert "text" in variant
            assert "length" in variant
            assert "readability" in variant
            assert "tone" in variant
            assert variant["tone"] == "engaging"
            assert variant["id"].startswith("demo_twitter_")

    @pytest.mark.asyncio
    async def test_get_demo_variants_newsletter(self, sample_input_text):
        """Test newsletter demo variants generation."""
        variants = await get_demo_variants(
            sample_input_text, ["newsletter"], "professional"
        )

        assert "newsletter" in variants
        assert len(variants["newsletter"]) == 1

        variant = variants["newsletter"][0]
        assert variant["id"] == "demo_newsletter_1"
        assert variant["tone"] == "professional"
        assert variant["length"] > 0

    @pytest.mark.asyncio
    async def test_get_demo_variants_blog(self, sample_input_text):
        """Test blog demo variants generation."""
        variants = await get_demo_variants(sample_input_text, ["blog"], "formal")

        assert "blog" in variants
        assert len(variants["blog"]) == 1

        variant = variants["blog"][0]
        assert variant["id"] == "demo_blog_1"
        assert variant["tone"] == "formal"
        assert variant["length"] > 0

    @pytest.mark.asyncio
    async def test_get_demo_variants_multiple_channels(self, sample_input_text):
        """Test demo variants for multiple channels."""
        channels = ["linkedin", "twitter", "newsletter"]
        variants = await get_demo_variants(sample_input_text, channels, "professional")

        for channel in channels:
            assert channel in variants
            assert len(variants[channel]) > 0

    @pytest.mark.asyncio
    async def test_get_demo_variants_unknown_channel(self, sample_input_text):
        """Test demo variants for unknown channel."""
        variants = await get_demo_variants(
            sample_input_text, ["unknown_channel"], "professional"
        )

        # Should not crash, and unknown channel will have variants
        assert "unknown_channel" in variants
        assert len(variants["unknown_channel"]) > 0


class TestGenerateContentReal:
    """Test real content generation with OpenAI API."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @pytest.mark.asyncio
    async def test_generate_content_real_success(self, mock_openai, sample_input_text):
        """Test successful real content generation."""
        result = await generate_content_real(
            sample_input_text, ["linkedin"], "professional", "gpt-4o-mini", "test_job_1"
        )

        assert "linkedin" in result
        assert len(result["linkedin"]) > 0

        variant = result["linkedin"][0]
        assert "id" in variant
        assert "text" in variant
        assert "length" in variant
        assert "readability" in variant
        assert "tone" in variant

    @pytest.mark.asyncio
    async def test_generate_content_real_no_api_key(self, sample_input_text):
        """Test real content generation without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
                await generate_content_real(
                    sample_input_text,
                    ["linkedin"],
                    "professional",
                    "gpt-4o-mini",
                    "test_job_1",
                )

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @pytest.mark.asyncio
    async def test_generate_content_real_invalid_model(self, sample_input_text):
        """Test real content generation with invalid model."""
        with pytest.raises(ValueError, match="Invalid model"):
            await generate_content_real(
                sample_input_text,
                ["linkedin"],
                "professional",
                "invalid-model",
                "test_job_1",
            )

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @pytest.mark.asyncio
    async def test_generate_content_real_api_error(self, sample_input_text):
        """Test real content generation with API error (AsyncOpenAI mock)."""
        with patch("generator.AsyncOpenAI") as mock_openai_class:
            mock_client = Mock()
            mock_client.chat.completions.create = AsyncMock(
                side_effect=Exception("API Error")
            )
            mock_openai_class.return_value = mock_client

            # Should fallback to demo content
            result = await generate_content_real(
                sample_input_text,
                ["linkedin"],
                "professional",
                "gpt-4o-mini",
                "test_job_1",
            )

            assert "linkedin" in result
            assert len(result["linkedin"]) > 0

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @pytest.mark.asyncio
    async def test_generate_content_real_token_usage_logging(
        self, mock_openai, sample_input_text
    ):
        """Test that token usage is properly logged."""
        with patch("generator.save_token_usage") as mock_save_tokens:
            await generate_content_real(
                sample_input_text,
                ["linkedin"],
                "professional",
                "gpt-4o-mini",
                "test_job_1",
            )

            # Verify token usage was saved
            mock_save_tokens.assert_called_once()
            call_args = mock_save_tokens.call_args
            assert call_args[0][0] == "test_job_1"  # job_id
            assert call_args[0][2] == "gpt-4o-mini"  # model
            assert call_args[0][3] == "linkedin"  # channel


class TestGenerateContent:
    """Test main content generation function."""

    @patch.dict(os.environ, {"API_MODE": "demo"})
    @pytest.mark.asyncio
    async def test_generate_content_demo_mode(self, sample_input_text):
        """Test content generation in demo mode."""
        result = await generate_content(
            sample_input_text, ["linkedin", "twitter"], "professional"
        )

        assert "linkedin" in result
        assert "twitter" in result
        assert len(result["linkedin"]) == 3
        assert len(result["twitter"]) == 5

    @patch.dict(os.environ, {"API_MODE": "real", "OPENAI_API_KEY": "test_key"})
    @pytest.mark.asyncio
    async def test_generate_content_real_mode(self, mock_openai, sample_input_text):
        """Test content generation in real mode."""
        result = await generate_content(
            sample_input_text, ["linkedin"], "professional", "gpt-4o-mini", "test_job_1"
        )

        assert "linkedin" in result
        assert len(result["linkedin"]) > 0

    @patch.dict(os.environ, {"API_MODE": "demo"})
    @pytest.mark.asyncio
    async def test_generate_content_invalid_model(self, sample_input_text):
        """Test content generation with invalid model."""
        with pytest.raises(ValueError, match="Invalid model"):
            await generate_content(
                sample_input_text, ["linkedin"], "professional", "invalid-model"
            )

    @patch.dict(os.environ, {"API_MODE": "invalid"})
    @pytest.mark.asyncio
    async def test_generate_content_invalid_api_mode(self, sample_input_text):
        """Test content generation with invalid API mode."""
        with pytest.raises(ValueError, match="Invalid API_MODE"):
            await generate_content(sample_input_text, ["linkedin"], "professional")

    @patch.dict(os.environ, {"API_MODE": "demo", "DEFAULT_MODEL": "gpt-4o"})
    @pytest.mark.asyncio
    async def test_generate_content_default_model(self, sample_input_text):
        """Test content generation with default model."""
        result = await generate_content(sample_input_text, ["linkedin"], "professional")

        assert "linkedin" in result
        assert len(result["linkedin"]) > 0

    @patch.dict(os.environ, {"API_MODE": "demo"})
    @pytest.mark.asyncio
    async def test_generate_content_all_valid_models(self, sample_input_text):
        """Test content generation with all valid models."""
        for model in VALID_MODELS:
            result = await generate_content(
                sample_input_text, ["linkedin"], "professional", model
            )
            assert "linkedin" in result
            assert len(result["linkedin"]) > 0


class TestValidModels:
    """Test valid models configuration."""

    def test_valid_models_list(self):
        """Test that valid models list is properly defined."""
        assert isinstance(VALID_MODELS, list)
        assert len(VALID_MODELS) > 0
        assert "gpt-4o-mini" in VALID_MODELS
        assert "gpt-4o" in VALID_MODELS
