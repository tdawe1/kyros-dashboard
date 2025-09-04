# Architect Context (Codex)

This repository uses a multi‑agent workflow defined in `agents.md` and collaboration docs under `collaboration/`.

Key points:
- Roles: Planner, Implementer, Critic, Integrator, Watchdog.
- Task lifecycle: queued → claimed → in_progress → review → approved → merging → done (+ blocked/failed/abandoned).
- DoD: tests updated/passing, static checks, secret scan clean, docs updated, critic review.
- State: `collaboration/state/*.json`; write via ETag + atomic replace; append events to `collaboration/events/events.jsonl`.
- Plans: PlanSpec YAML in `collaboration/plans/inbox/planspec.yml`. Splitter generates `collaboration/tasks/<ID>` scaffolds and `.cursor/rules/tasks/<ID>.mdc`.

Pipelines:
- Import from Drive via GH Actions: `.github/workflows/plan-import.yml` and `create-plan-pr.yml`.
- Local split: `python scripts/split_plan.py collaboration/plans/inbox/planspec.yml`.
- Run helper: `scripts/run-plan-pipeline.sh --file ...` or `--drive` with `gh`.

Cursor integration:
- Always‑on rules live in `.cursor/rules/*.mdc`.
- Per‑task rules in `.cursor/rules/tasks/<ID>.mdc` auto‑apply acceptance, DoD, and changescope.

Use this context when designing plans, slicing tasks, and validating pipelines.

