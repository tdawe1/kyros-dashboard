import os
import types
import pytest


@pytest.fixture(autouse=True)
def stub_openai_global(monkeypatch):
    """Global autouse stub to avoid real OpenAI calls across backend tests."""
    os.environ.setdefault("OPENAI_API_KEY", "test-sk")

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

