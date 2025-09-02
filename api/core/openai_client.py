"""
OpenAI Client Wrapper

This module provides a standardized interface for OpenAI API calls across all tools.
It includes retry logic, token logging, and error handling.
"""

import os
import logging
import time
from typing import Dict, List, Any, Optional
from openai import OpenAI
import sentry_sdk

logger = logging.getLogger(__name__)

# Valid models whitelist
VALID_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4.1", "gpt-4.1-mini"]


class OpenAIError(Exception):
    """Custom exception for OpenAI-related errors."""

    pass


class OpenAIClient:
    """
    Wrapper for OpenAI API client with retry logic and standardized error handling.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI client.

        Args:
            api_key: OpenAI API key. If not provided, will use OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise OpenAIError("OpenAI API key not provided")

        self.client = OpenAI(api_key=self.api_key)
        self.max_retries = int(os.getenv("OPENAI_MAX_RETRIES", "3"))
        self.retry_delay = float(os.getenv("OPENAI_RETRY_DELAY", "1.0"))

    def validate_model(self, model: str) -> bool:
        """
        Validate that the model is in the whitelist.

        Args:
            model: Model name to validate.

        Returns:
            True if model is valid, False otherwise.
        """
        return model in VALID_MODELS

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        job_id: Optional[str] = None,
        tool_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Make a chat completion request with retry logic.

        Args:
            messages: List of message dictionaries.
            model: Model to use for completion.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
            job_id: Job ID for logging and tracking.
            tool_name: Name of the tool making the request.

        Returns:
            Dictionary containing the response and usage information.

        Raises:
            OpenAIError: If the request fails after all retries.
        """
        if not self.validate_model(model):
            raise OpenAIError(f"Invalid model: {model}. Must be one of {VALID_MODELS}")

        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                logger.info(
                    f"Making OpenAI request (attempt {attempt + 1}/{self.max_retries + 1}) "
                    f"for job {job_id} using model {model}"
                )

                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

                # Extract response data
                content = response.choices[0].message.content
                usage = response.usage

                # Log successful request
                logger.info(
                    f"OpenAI request successful for job {job_id}: "
                    f"{usage.prompt_tokens} prompt + {usage.completion_tokens} completion tokens"
                )

                # Set Sentry context
                if job_id:
                    with sentry_sdk.configure_scope() as scope:
                        scope.set_tag("openai_model", model)
                        scope.set_tag("openai_tokens", usage.total_tokens)
                        if tool_name:
                            scope.set_tag("tool_name", tool_name)

                return {
                    "content": content,
                    "usage": {
                        "prompt_tokens": usage.prompt_tokens,
                        "completion_tokens": usage.completion_tokens,
                        "total_tokens": usage.total_tokens,
                    },
                    "model": model,
                    "job_id": job_id,
                }

            except Exception as e:
                last_error = e
                logger.warning(
                    f"OpenAI request failed (attempt {attempt + 1}/{self.max_retries + 1}) "
                    f"for job {job_id}: {str(e)}"
                )

                # Capture error in Sentry
                sentry_sdk.capture_exception(e)

                # Don't retry on the last attempt
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * (2**attempt))  # Exponential backoff
                else:
                    break

        # If we get here, all retries failed
        error_msg = f"OpenAI request failed after {self.max_retries + 1} attempts: {str(last_error)}"
        logger.error(error_msg)
        raise OpenAIError(error_msg)

    def estimate_cost(
        self, prompt_tokens: int, completion_tokens: int, model: str
    ) -> float:
        """
        Estimate the cost of a request based on token usage.

        Args:
            prompt_tokens: Number of prompt tokens.
            completion_tokens: Number of completion tokens.
            model: Model used for the request.

        Returns:
            Estimated cost in USD.
        """
        # Pricing per 1K tokens (as of 2024)
        pricing = {
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-4.1": {"input": 0.01, "output": 0.03},
            "gpt-4.1-mini": {"input": 0.0025, "output": 0.01},
        }

        if model not in pricing:
            logger.warning(f"Unknown model {model} for cost estimation")
            return 0.0

        input_cost = (prompt_tokens / 1000) * pricing[model]["input"]
        output_cost = (completion_tokens / 1000) * pricing[model]["output"]

        return input_cost + output_cost


# Global client instance
_client_instance = None


def get_openai_client() -> OpenAIClient:
    """
    Get the global OpenAI client instance.

    Returns:
        OpenAIClient instance.
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = OpenAIClient()
    return _client_instance


def create_openai_client(api_key: Optional[str] = None) -> OpenAIClient:
    """
    Create a new OpenAI client instance.

    Args:
        api_key: OpenAI API key. If not provided, will use OPENAI_API_KEY env var.

    Returns:
        New OpenAIClient instance.
    """
    return OpenAIClient(api_key=api_key)
