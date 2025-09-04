import sys
from pathlib import Path
import types
import pytest
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def stub_openai_global(monkeypatch):
    """Global autouse stub to avoid real OpenAI calls across backend tests."""
    # Ensure imports resolve when running pytest from repo root (add backend to sys.path)
    backend_root = str(Path(__file__).resolve().parents[1])
    if backend_root not in sys.path:
        sys.path.insert(0, backend_root)
    # Ensure code paths that require an API key find a safe, non-secret value
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-openai-api-key")

    class _StubCompletions:
        @staticmethod
        def create(**kwargs):
            class _Choice:
                def __init__(self):
                    self.message = types.SimpleNamespace(content="ok")

            class _Usage:
                prompt_tokens = 1
                completion_tokens = 1
                total_tokens = 2

            return types.SimpleNamespace(choices=[_Choice()], usage=_Usage())

    class _StubChat:
        completions = _StubCompletions()

    class _StubClient:
        chat = _StubChat()

    import core.openai_client as _mod

    monkeypatch.setattr(_mod, "OpenAI", lambda api_key=None: _StubClient())


@pytest.fixture()
def clean_storage(tmp_path, monkeypatch):
    """Provide a clean, isolated token storage file and state per test.

    - Redirect TOKEN_STORAGE_FILE to a temp path so tests don't write to repo.
    - Reload utils.token_storage to pick up the env var and reset in-memory state.
    - Ensure data cleared before and after the test.
    """
    storage_path = tmp_path / "token_usage.json"
    monkeypatch.setenv("TOKEN_STORAGE_FILE", str(storage_path))

    import importlib
    import utils.token_storage as token_storage

    importlib.reload(token_storage)
    token_storage.clear_all_data()
    try:
        yield
    finally:
        token_storage.clear_all_data()


@pytest.fixture()
def mock_redis(monkeypatch):
    """Mock Redis client for rate limiter tests.

    - Monkeypatch get_secure_redis_client to return a MagicMock with the
      expected interface (hgetall, hset, expire, pipeline.execute).
    - Ensure the module-level rate_limiter instance uses this mock client.
    """
    mock = MagicMock()
    pipe = MagicMock()
    mock.pipeline.return_value = pipe
    pipe.hset.return_value = True
    pipe.expire.return_value = True
    pipe.execute.return_value = True

    # When code constructs a limiter without passing a client, return our mock
    monkeypatch.setattr("middleware.rate_limiter.get_secure_redis_client", lambda: mock)

    # Ensure module-level limiter uses our mock without reloading the module
    import middleware.rate_limiter as rl

    rl.rate_limiter.redis_client = mock
    return mock
