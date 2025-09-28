# Acceptance
- staging.yml runs only on push to `develop` or when required secrets exist
- Tests workflow uses `poetry install --no-root` in all backend install steps
- No CI install/setup failures across required jobs
- No change to production deploy behavior from `main`
