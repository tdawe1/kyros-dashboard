import os
import types
import pytest


@pytest.fixture(autouse=True)
def stub_openai(monkeypatch):
    """Ensure OpenAI calls are stubbed and no real API key/network is required.

    This fixture runs for all tests in the core backend test suite, replacing
    the OpenAI client used by core.openai_client with a minimal stub that
    returns deterministic data. It also sets a dummy API key to satisfy code
    paths that validate its presence.
    """

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

    # Patch the bound OpenAI symbol used inside core.openai_client
    import core.openai_client as _mod

    monkeypatch.setattr(_mod, "OpenAI", lambda api_key=None: _StubClient())

