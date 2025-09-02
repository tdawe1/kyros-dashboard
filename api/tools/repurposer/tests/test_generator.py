import pytest
from unittest.mock import patch, MagicMock
from ..generator import generate_content, get_demo_variants
from core.openai_client import VALID_MODELS


class TestRepurposerGenerator:
    """Test cases for the repurposer generator module."""

    def test_demo_variants_structure(self):
        """Test that demo variants have the correct structure."""
        input_text = "This is a test blog post about AI and productivity."
        channels = ["linkedin", "twitter"]
        tone = "professional"

        variants = get_demo_variants(input_text, channels, tone)

        # Check that all requested channels are present
        assert set(variants.keys()) == set(channels)

        # Check structure of each channel's variants
        for channel, channel_variants in variants.items():
            assert isinstance(channel_variants, list)
            assert len(channel_variants) > 0

            for variant in channel_variants:
                assert "id" in variant
                assert "content" in variant
                assert "channel" in variant
                assert "tone" in variant
                assert "word_count" in variant
                assert "character_count" in variant
                assert "created_at" in variant

                assert variant["channel"] == channel
                assert variant["tone"] == tone
                assert isinstance(variant["word_count"], int)
                assert isinstance(variant["character_count"], int)

    def test_demo_variants_unknown_channel(self):
        """Test that unknown channels get fallback content."""
        input_text = "Test content"
        channels = ["unknown_channel"]
        tone = "professional"

        variants = get_demo_variants(input_text, channels, tone)

        assert "unknown_channel" in variants
        assert len(variants["unknown_channel"]) == 1
        assert (
            "Demo content for unknown_channel channel"
            in variants["unknown_channel"][0]["content"]
        )

    @pytest.mark.asyncio
    async def test_generate_content_demo_mode(self):
        """Test content generation in demo mode."""
        with patch.dict(
            "os.environ", {"API_MODE": "demo", "OPENAI_API_KEY": "test-key"}
        ):
            input_text = "This is a test blog post about AI and productivity."
            channels = ["linkedin", "twitter"]
            tone = "professional"

            variants = await generate_content(
                input_text=input_text,
                channels=channels,
                tone=tone,
                model="gpt-4o-mini",
                job_id="test_job_123",
            )

            # Should return demo variants
            assert set(variants.keys()) == set(channels)
            for channel in channels:
                assert len(variants[channel]) > 0

    @pytest.mark.asyncio
    async def test_generate_content_invalid_model(self):
        """Test that invalid models raise ValueError."""
        with patch.dict(
            "os.environ", {"API_MODE": "demo", "OPENAI_API_KEY": "test-key"}
        ):
            with pytest.raises(ValueError, match="Invalid model"):
                await generate_content(
                    input_text="Test content",
                    channels=["linkedin"],
                    tone="professional",
                    model="invalid-model",
                    job_id="test_job_123",
                )

    @pytest.mark.asyncio
    async def test_generate_content_invalid_api_mode(self):
        """Test that invalid API_MODE raises ValueError."""
        with patch.dict(
            "os.environ", {"API_MODE": "invalid", "OPENAI_API_KEY": "test-key"}
        ):
            with pytest.raises(ValueError, match="Invalid API_MODE"):
                await generate_content(
                    input_text="Test content",
                    channels=["linkedin"],
                    tone="professional",
                    model="gpt-4o-mini",
                    job_id="test_job_123",
                )

    @pytest.mark.asyncio
    async def test_generate_content_real_mode_mock(self):
        """Test content generation in real mode with mocked OpenAI."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test LinkedIn post content"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150

        with patch.dict(
            "os.environ", {"API_MODE": "real", "OPENAI_API_KEY": "test-key"}
        ):
            with patch(
                "tools.repurposer.generator.get_openai_client"
            ) as mock_get_client:
                mock_client = MagicMock()
                mock_client.chat_completion.return_value = {
                    "content": "Test LinkedIn post content",
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 50,
                        "total_tokens": 150,
                    },
                }
                mock_get_client.return_value = mock_client

                with patch("utils.token_storage.save_token_usage"):
                    variants = await generate_content(
                        input_text="Test content for LinkedIn",
                        channels=["linkedin"],
                        tone="professional",
                        model="gpt-4o-mini",
                        job_id="test_job_123",
                    )

                    # Should call OpenAI API
                    mock_client.chat_completion.assert_called_once()

                    # Should return variants
                    assert "linkedin" in variants
                    assert len(variants["linkedin"]) > 0

    def test_valid_models_constant(self):
        """Test that VALID_MODELS contains expected models."""
        expected_models = ["gpt-4o-mini", "gpt-4o", "gpt-4.1", "gpt-4.1-mini"]
        assert VALID_MODELS == expected_models
