[T-020] Resolve backend test regression (Python 3.13)

Summary
- Ensure tests run clean on Python 3.13 by stabilizing imports and mocks
- Add project-wide backend conftest for sys.path, dummy redis, and OpenAI stub
- Harden tests fixtures: isolated token storage, Redis mock for rate limiter

Changes
- backend/conftest.py: add import-path bootstrap, 'redis' stub, and OpenAI client stub
- backend/tests/conftest.py: add sys.path bootstrap, safe OPENAI key via monkeypatch, clean_storage + mock_redis fixtures
- backend/core/tests/conftest.py: switch to monkeypatch.setenv, add sys.path bootstrap

Validation
- Ran targeted tests locally:
  - core/tests/test_openai_client.py: PASS
  - tests/test_token_utils.py and tests/test_token_storage.py: PASS
  - tests/test_rate_limiter.py: logic passes with sync tests; async tests require pytest-asyncio (present in CI)
- Import errors resolved for utils/middleware/main/generator modules

Notes
- No runtime code changes; all updates are test/config only
- CI should include pytest-asyncio/anyio for async tests (Py3.13 compatible)

Next
- Critic to review; if green, merge into develop
