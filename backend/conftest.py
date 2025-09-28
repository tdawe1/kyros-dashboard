import sys
from pathlib import Path
import types
import pytest

# Ensure imports resolve regardless of cwd; executed at import time
_backend_root = str(Path(__file__).resolve().parent)
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)

# Provide a lightweight stub for the optional 'redis' dependency so importing
# core.security does not fail in environments without redis installed.
import types as _types
if 'redis' not in sys.modules:
    _redis_mod = _types.SimpleNamespace()

    class _FakeRedis:
        def __init__(self, *args, **kwargs):
            pass

        def ping(self):
            return True

        def pipeline(self):
            return _types.SimpleNamespace()

        # Common operations used behind circuit breaker
        def incr(self, *args, **kwargs):
            return 1

        def get(self, *args, **kwargs):
            return None

        def set(self, *args, **kwargs):
            return True

        def expire(self, *args, **kwargs):
            return True

        def delete(self, *args, **kwargs):
            return 1

        def hset(self, *args, **kwargs):
            return 1

        def hgetall(self, *args, **kwargs):
            return {}

    def _from_url(*args, **kwargs):
        return _FakeRedis()

    class _RedisExceptions:
        class RedisError(Exception):
            pass

    _redis_mod.from_url = _from_url
    _redis_mod.Redis = _FakeRedis
    _redis_mod.exceptions = _RedisExceptions
    sys.modules['redis'] = _redis_mod
    sys.modules['redis.exceptions'] = _RedisExceptions


@pytest.fixture(autouse=True)
def configure_test_env(monkeypatch):
    """Project-wide backend test config for imports and OpenAI stubbing.

    - Ensure the backend root is on sys.path so tests can import modules
      like `utils`, `middleware`, `main`, `generator` when pytest runs from
      repository root or with custom testpaths.
    - Provide a safe dummy `OPENAI_API_KEY` and stub the OpenAI client used
      by `core.openai_client` to prevent any real network calls.
    """
    # Safe dummy API key for code paths that require it
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-openai-api-key")

    # 3) Stub OpenAI client symbol used in core.openai_client
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
