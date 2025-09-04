import sys
from pathlib import Path
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

    # Ensure imports resolve when running pytest from repo root
    backend_root = str(Path(__file__).resolve().parents[2])
    if backend_root not in sys.path:
        sys.path.insert(0, backend_root)
    # Provide a safe dummy API key to satisfy code paths requiring it
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

    # Patch the bound OpenAI symbol used inside core.openai_client
    import core.openai_client as _mod

    monkeypatch.setattr(_mod, "OpenAI", lambda api_key=None: _StubClient())
