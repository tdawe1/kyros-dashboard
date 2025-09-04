[T-018] Fix security scan failure in backend tests

Summary
- Replace test fixture env usage with safe dummy value via monkeypatch
- Redact local dev persistence file to contain no sensitive data

Changes
- backend/tests/conftest.py: use monkeypatch.setenv('OPENAI_API_KEY', 'dummy-openai-api-key'); keep client fully stubbed to avoid network calls
- token_usage.json: keep schema, remove any values; set saved_at: null

Validation
- grep -R "sk-" "OPENAI_API_KEY" "Bearer " "authorization" shows no secrets
- Backend tests use stubbed OpenAI client; no real API calls
- Pre-commit: detect-secrets expected clean (run: pre-commit run --all-files)

Risk
- Low; modifications limited to test fixture and dev-only JSON file

Next
- Merge once critic confirms pre-commit secrets scan and tests (CI) are green
