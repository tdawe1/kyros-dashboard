"""
OpenAI Client Wrapper

This module provides a standardized interface for OpenAI API calls across all tools.
It includes retry logic, token logging, and error handling.
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

try:
    # SDK import lives here so tests can patch it or patch get_client()
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # tests can monkeypatch get_client regardless

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
_MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", "3"))
_RETRY_BACKOFF = float(os.getenv("OPENAI_RETRY_BACKOFF", "0.5"))

class OpenAIError(RuntimeError):
    pass

# ---- dependency injection & singleton client ----
_client_singleton: Optional[Any] = None

def get_client() -> Any:
    """
    Returns a singleton OpenAI client. Tests can monkeypatch this function to
    return a fake client object, or set OPENAI_TEST_MODE=1 to bypass network.
    """
    global _client_singleton
    if _client_singleton is None:
        api_key = os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("OPENAI_BASE_URL")  # optional (Azure/self-hosted)
        if OpenAI is None:
            raise OpenAIError("OpenAI SDK not available")
        _client_singleton = OpenAI(api_key=api_key, base_url=base_url)  # type: ignore
    return _client_singleton

# ---- test-mode stub ----
_TEST_MODE = os.getenv("OPENAI_TEST_MODE") == "1" or os.getenv("ENV") == "test"

def _fake_chat_completion(messages: list[dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
    """
    Deterministic stub used when OPENAI_TEST_MODE=1.
    """
    content = "ok"
    # mirror a minimal shape used by callers/tests
    return {
        "id": "chatcmpl_test",
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        "model": kwargs.get("model", DEFAULT_MODEL),
    }

# ---- public API ----
def chat_completion(
    messages: list[dict[str, str]],
    model: str = DEFAULT_MODEL,
    max_tokens: int = 64,
    temperature: float = 0.2,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Thin wrapper that retries transient failures and raises OpenAIError on hard failures.
    In tests (OPENAI_TEST_MODE=1 or ENV=test), returns a deterministic stub and does not
    hit the network.
    """
    if _TEST_MODE:
        return _fake_chat_completion(messages, model=model, max_tokens=max_tokens, temperature=temperature, **kwargs)

    last_exc: Optional[Exception] = None
    for attempt in range(_MAX_RETRIES + 1):
        try:
            client = get_client()
            resp = client.chat.completions.create(  # type: ignore[attr-defined]
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )
            # Normalize to dict for tests that don't import SDK types
            return getattr(resp, "to_dict", lambda: resp)()
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            # simple transient heuristic; tests can still patch get_client()
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_BACKOFF * (2**attempt))
            else:
                break
    raise OpenAIError(f"OpenAI request failed after {_MAX_RETRIES + 1} attempts: {last_exc}")

# ---- legacy compatibility ----
def get_openai_client() -> Any:
    """
    Legacy compatibility function. Returns the singleton client.
    """
    return get_client()

def create_openai_client(api_key: Optional[str] = None) -> Any:
    """
    Legacy compatibility function. Creates a new client with optional API key.
    """
    if api_key:
        return OpenAI(api_key=api_key) if OpenAI else None
    return get_client()
