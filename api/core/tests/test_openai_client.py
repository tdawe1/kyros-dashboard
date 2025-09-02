import pytest
from unittest.mock import patch, MagicMock
from ..openai_client import OpenAIClient, OpenAIError, VALID_MODELS


class TestOpenAIClient:
    """Test cases for the OpenAI client wrapper."""

    def test_init_with_api_key(self):
        """Test client initialization with API key."""
        client = OpenAIClient(api_key="test-key")
        assert client.api_key == "test-key"

    @patch.dict("os.environ", {"OPENAI_API_KEY": "env-key"})
    def test_init_with_env_key(self):
        """Test client initialization with environment variable."""
        client = OpenAIClient()
        assert client.api_key == "env-key"

    def test_init_without_key(self):
        """Test client initialization without API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(OpenAIError, match="OpenAI API key not provided"):
                OpenAIClient()

    def test_validate_model_valid(self):
        """Test model validation with valid models."""
        client = OpenAIClient(api_key="test-key")
        for model in VALID_MODELS:
            assert client.validate_model(model) is True

    def test_validate_model_invalid(self):
        """Test model validation with invalid models."""
        client = OpenAIClient(api_key="test-key")
        invalid_models = ["gpt-3.5-turbo", "invalid-model", "claude-3"]
        for model in invalid_models:
            assert client.validate_model(model) is False

    @patch("api.core.openai_client.OpenAI")
    def test_chat_completion_success(self, mock_openai_class):
        """Test successful chat completion."""
        # Mock the OpenAI client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        client = OpenAIClient(api_key="test-key")
        result = client.chat_completion(
            messages=[{"role": "user", "content": "Test prompt"}],
            model="gpt-4o-mini",
            job_id="test-job",
            tool_name="test-tool",
        )

        assert result["content"] == "Test response"
        assert result["usage"]["total_tokens"] == 150
        assert result["model"] == "gpt-4o-mini"
        assert result["job_id"] == "test-job"

    def test_chat_completion_invalid_model(self):
        """Test chat completion with invalid model."""
        client = OpenAIClient(api_key="test-key")
        with pytest.raises(OpenAIError, match="Invalid model"):
            client.chat_completion(
                messages=[{"role": "user", "content": "Test prompt"}],
                model="invalid-model",
            )

    @patch("api.core.openai_client.OpenAI")
    def test_chat_completion_retry_logic(self, mock_openai_class):
        """Test retry logic on API failures."""
        # Mock the OpenAI client to fail twice then succeed
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Success after retry"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150

        # First two calls fail, third succeeds
        mock_client.chat.completions.create.side_effect = [
            Exception("API Error 1"),
            Exception("API Error 2"),
            mock_response,
        ]
        mock_openai_class.return_value = mock_client

        client = OpenAIClient(api_key="test-key")
        result = client.chat_completion(
            messages=[{"role": "user", "content": "Test prompt"}],
            model="gpt-4o-mini",
        )

        assert result["content"] == "Success after retry"
        assert mock_client.chat.completions.create.call_count == 3

    @patch("api.core.openai_client.OpenAI")
    def test_chat_completion_max_retries_exceeded(self, mock_openai_class):
        """Test behavior when max retries are exceeded."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception(
            "Persistent API Error"
        )
        mock_openai_class.return_value = mock_client

        client = OpenAIClient(api_key="test-key")
        with pytest.raises(OpenAIError, match="OpenAI request failed after"):
            client.chat_completion(
                messages=[{"role": "user", "content": "Test prompt"}],
                model="gpt-4o-mini",
            )

    def test_estimate_cost(self):
        """Test cost estimation for different models."""
        client = OpenAIClient(api_key="test-key")

        # Test gpt-4o-mini
        cost = client.estimate_cost(1000, 500, "gpt-4o-mini")
        expected_cost = (1000 / 1000) * 0.00015 + (500 / 1000) * 0.0006
        assert abs(cost - expected_cost) < 0.0001

        # Test gpt-4o
        cost = client.estimate_cost(1000, 500, "gpt-4o")
        expected_cost = (1000 / 1000) * 0.005 + (500 / 1000) * 0.015
        assert abs(cost - expected_cost) < 0.0001

    def test_estimate_cost_unknown_model(self):
        """Test cost estimation for unknown model."""
        client = OpenAIClient(api_key="test-key")
        cost = client.estimate_cost(1000, 500, "unknown-model")
        assert cost == 0.0
