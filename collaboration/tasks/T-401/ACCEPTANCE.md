# Acceptance
- GitHub Actions `test.yml` passes green on `develop` without external secrets
- Backend tests run with `backend/env.test` loaded and OpenAI calls mocked
- Frontend unit tests run with `frontend/env.test` and no network flakiness
- `scripts/run-tests.sh` exits non-zero on any suite failures
