# Plan → Split → PR Pipeline (Codex)

Goal: standardize PlanSpec ingestion and task generation.

Sources:
- PlanSpec at `collaboration/plans/inbox/planspec.yml` (from Drive import or local).

Steps:
1) Import PlanSpec
   - Drive: run GH workflow "Import Latest Plan from Drive"; it writes PlanSpec to the repo.
   - Local: place PlanSpec directly at the inbox path.
2) Split tasks
   - `python scripts/split_plan.py collaboration/plans/inbox/planspec.yml`
   - Outputs `collaboration/tasks/<ID>` and `.cursor/rules/tasks/<ID>.mdc`.
3) Kickoff prompts
   - `scripts/task-kickoff.sh <ID>` prints Planner/Implementer/Critic prompts and writes `KICKOFF.md`.
4) Optional: open PR containing plan + generated tasks/state updates.

Utilities:
- `scripts/run-plan-pipeline.sh --file <path>` or `--drive` (uses `gh`).
- `scripts/push-plan-to-gdrive.sh <plan.yml> [remote:path]` (uses `rclone`).

References: `agents.md`, `.cursor/rules/*.mdc`, `collaboration/architecture.md`.

