# Kyros Dashboard — Review Packet

This packet gives external reviewers and assisting agents a fast, accurate understanding of the project’s goals, workflow, CI gates, and the minimum set of context files to read. It also includes the standardized Implementer Handoff Prompt for short, scoped coding tasks.

## Overarching Goals (re‑centered)
1) Build a high‑quality demo project for kyros.solutions.
2) Make it a solid framework that can expand into a full platform for our product offerings.
3) Short term: unify the codebase (reduce drift, align configs, make CI green).

## How To Use This Packet
- Start with “Start Here” and “Collaboration Workflow & State.”
- Skim the “CI & PR Gates” section to understand what must be green.
- Use “Implementation Context” when diving into backend/frontend specifics.
- If you will implement fixes, use the “Implementer Handoff Prompt” verbatim.

---

## Start Here
- README: `README.md` — Project overview and quick start.
- Collaboration Workflow: `agents.md` — Leases, lifecycle, DoD, events, PR gates.
- Architecture Overview: `collaboration/architecture.md` — System + collaboration architecture.
- Project Management: `docs/PROJECT_MANAGEMENT.md` — Tasks/locks/events CLI, roadmap, board, sync.

## Collaboration Workflow & State
- State (source of truth):
  - Tasks: `collaboration/state/tasks.json`
  - Locks: `collaboration/state/locks.json`
  - Agents: `collaboration/state/agents.json`
- Events and Logs:
  - Machine log: `collaboration/events/events.jsonl`
  - Human summary: `collaboration/logs/log.md`
- Per‑task rules (acceptance + change scope): `.cursor/rules/tasks/*.mdc` (e.g., `T-502.mdc`, `T-503.mdc`, `T-504.mdc`)
- Task briefs: `collaboration/tasks/*/BRIEF.md`, `collaboration/tasks/*/ACCEPTANCE.md`

## CI & PR Gates (what must be green)
- Tests matrix and summaries: `.github/workflows/test.yml`
- Quality checks (lint/format/security): `.github/workflows/quality-checks.yml`
- Branch policy and JSON/YAML validation: `.github/workflows/collab-guard.yml`
- Task‑scoped changes (globs) and forbid `collaboration/state/**`: `.github/workflows/agent-validation.yml`
- PR template (acceptance evidence): `.github/pull_request_template.md`

## Implementation Context
- Backend
  - App entry + health: `backend/main.py`
  - Reference tests: `backend/tests/test_healthz.py`
  - Project config: `backend/pyproject.toml`, `backend/pytest.ini`, `backend/.bandit`
- Frontend
  - Package + scripts: `frontend/package.json`
  - Build/test configs: `frontend/vite.config.js`, `frontend/vitest.config.js`, `frontend/playwright.config.js`
  - Failure analysis: `docs/FRONTEND_PR_FAILURE_ANALYSIS.md`
- E2E & audits
  - E2E notes: `E2E_AUDIT.md`

## Agents, Models, and IDE Integration
- Cursor env + MCP servers: `.cursor/environment.json`
- Codex CLI profiles/providers/sandbox: `.codex/config.toml`
- Architect/Planner process: `.codex/context/architect.md`
- MCP servers scaffold: `mcp/README.md`

## CodeRabbit Integration (under‑utilized; should be leveraged)
- MCP server (feedback fetch): `mcp/coderabbit_server.py`
- Auto‑import PR feedback to tasks: `.github/workflows/import_coderabbit_on_pr.yml`
- Task creation from feedback: `scripts/import_coderabbit_feedback.py`
- Proposal (enhanced roles/workflows): `docs/CODERABBIT_INTEGRATION_PROPOSAL.md`

## Deployment (awareness)
- Workflow and environments: `collaboration/DEPLOYMENT_WORKFLOW.md`
- CI deploy step (after green Tests on main): `.github/workflows/deploy.yml`

---

## Implementer Handoff Prompt (Paste into Claude Code or Cursor)

Role: Implementer (Claude 4.1 Sonnet; Cursor Auto allowed).

Before doing anything, read the project workflow and context below, then report your understanding of:
- Your role and gates
- The task’s acceptance criteria and change scope
- Your 3–5 step plan for the first subtask
- Any risks/assumptions
Wait for an explicit APPROVE before making changes.

Context to read (open these files)
- Collaboration workflow:
  - `agents.md` (leases, task lifecycle, DoD, PR gates)
  - `.cursor/environment.json` (env vars, MCP servers)
  - `.cursor/rules/presets/implementer.mdc`, `critic.mdc`, `integrator.mdc`, `planner.mdc`
  - `.cursor/rules/tasks/<TASK_ID>.mdc` (acceptance + globs; your edits must match these)
  - `.codex/config.toml` (profiles, sandbox, providers)
  - `.codex/context/architect.md` (PlanSpec process and DoD for planning)
- Collaboration state and history:
  - `collaboration/state/tasks.json`, `collaboration/state/locks.json`, `collaboration/state/agents.json`
  - `collaboration/events/events.jsonl`, `collaboration/logs/log.md`
  - `collaboration/architecture.md`, `collaboration/CONTRIBUTING.md`
- CI, quality, and PR rules:
  - `.github/workflows/test.yml`, `quality-checks.yml`, `collab-guard.yml`, `agent-validation.yml`, `pull_request_template.md`
- Scripts and tooling:
  - `scripts/collab_cli.py` (leases/events/logs), `scripts/run-plan-pipeline.sh`, `scripts/push-plan-to-gdrive.sh`
  - `scripts/import_coderabbit_feedback.py` (imports CodeRabbit review into tasks)
- Model/agents integration (for awareness):
  - `docs/CLAUDE_PRO_INTEGRATION_PROPOSAL.md`, `docs/CLAUDE_PRO_IMPLEMENTATION_PLAN.md`
  - `docs/CODERABBIT_INTEGRATION_PROPOSAL.md`, `docs/JULES_IMPLEMENTATION_PLAN.md`
  - `mcp/README.md`, `mcp/coderabbit_server.py`, `mcp/kyros_collab_server.py`

Task specifics (fill these in from the plan)
- Task: <TASK_ID> — <short title>
- Lane: <backend|frontend|ci|docs>
- Branch: `feat/<TASK_ID>-<slug>`
- Acceptance: <paste from `.cursor/rules/tasks/<TASK_ID>.mdc`>
- ChangeScope: <paste globs from `.cursor/rules/tasks/<TASK_ID>.mdc`>

Constraints and gates
- Keep diffs small, focused, and within ChangeScope; no edits to `collaboration/state/**`.
- Acquire leases before editing non‑trivial files and heartbeat if needed:
  - `python scripts/collab_cli.py acquire-lease <path> <agent_id> <TASK_ID>`
- Base branch must be `develop` and up‑to‑date (Collab Guard enforces).
- CI must be green:
  - Backend: Python 3.12/3.13 via Poetry, `poetry install`, `poetry run pytest -v`; ruff + bandit run in CI.
  - Frontend: Node 20, `npm ci`, `npm run build`, `npm run test:ci`, `npm run lint`, `npm run format:check`.
  - E2E: Playwright base URL `http://localhost:3001` when required.
- CodeRabbit: request review on PR open/sync; feedback is auto‑imported to tasks via GitHub Action.

First reply (required; do not implement yet)
1) Role understanding: what you will do and won’t do (per agents.md + task rule).
2) Context summary: acceptance, ChangeScope, key CI gates to satisfy.
3) Plan for the first subtask (3–5 steps, 30–60 min).
4) Risks/assumptions + how you’ll validate locally.
5) Leases you intend to acquire (paths).

Budget note
- You are on Claude Code Pro. Keep context usage efficient: open only the files above plus those in the ChangeScope. Prefer minimal diffs and short iterations.

If you are a Cursor Auto agent
- Explicitly confirm you’ve read all the files listed above and `.cursor/rules/tasks/<TASK_ID>.mdc`, restate your role and acceptance, then wait for APPROVE before proceeding.

---

## CI Failure Review — Quick FAQ
**Backend check fails**
- Ensure Poetry install works; run `poetry install --no-interaction --no-ansi --no-root`.
- Run `poetry run ruff check .` and `poetry run bandit -r .` locally.
- Execute tests with `poetry run pytest -v`; match the matrix (3.12, 3.13).

**Frontend build/test fails**
- `npm ci` then `npm run build` and `npm run test:ci`.
- Fix ESLint/Prettier: `npm run lint` and `npm run format:check`.
- Review `frontend/vite.config.js` and `frontend/vitest.config.js`.

**E2E step flaky or failing**
- Ensure backend on 8000 and frontend on 3001; base URL: `http://localhost:3001`.
- Install browsers: `npx playwright install --with-deps`.

**PR blocked by Collab Guard**
- Base must be `develop`, branch up‑to‑date with no behind commits.

**PR blocked by Agent Validation**
- Changes must match task rule globs in `.cursor/rules/tasks/<TASK_ID>.mdc`.
- Do not edit `collaboration/state/**` in PRs.

---

## Next Steps
- Share this packet with reviewers and agents.
- On alignment, the Planner/Architect will draft a short PlanSpec and run the plan pipeline to scaffold tasks and per‑task rules.

