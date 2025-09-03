# Changelog

All notable changes to this project are documented here.

Format: inspired by Keep a Changelog. Dates use UTC.

## [Unreleased]

- Backend: decouple `core` package imports and make HTML sanitization dependency optional.
  - `backend/core/__init__.py`: keep package init lightweight to avoid import‑time failures from optional deps.
  - `backend/core/input_validation.py`: gracefully fall back when `bleach` is unavailable.
  - Intent: stabilize develop CI post‑merge by preventing missing optional deps from blocking tests.
- Frontend: CI hygiene improvements (landed in prior batch branch, merged to develop).
  - Limit ESLint to `src/`; add `.eslintignore` for artifacts.
  - Fix JobTable skeleton import; remove unused param in Settings.
  - Apply Prettier formatting and ignore Playwright reports/test artifacts in Git.

Known status:
- PR #10 (fix/develop-backend-ci-optional-bleach) open to land backend CI stabilization into `develop`.
- `develop` CI is not fully green yet; PR #10 targets remaining backend build/test issues.

## 2025-09-03 – Batch merge into develop

- Merge: `feat/organize-recent-changes` and `test/ci-fixes` → `develop` (PR #9).
- Highlights:
  - Backend: migrate to Poetry; align CI to Python 3.12; unified test runner; improved code quality and re‑enabled tests.
  - Frontend: standardize dev/E2E on port 3001; Playwright config corrected; component and pages refinements.
  - CI: workflow fixes (format/lint/tests/build/security); reduce phantom prepare issues and cache problems.
  - Collaboration: add state/events scaffolding and docs updates for agent roles and processes.
- Notes:
  - Integrator set auto‑merge; PR merged at commit 21b9f09696ca78ecc5b44bb6e8042e4861eae2e2.
  - Post‑merge follow‑up is tracked under task‑008 stabilization.

