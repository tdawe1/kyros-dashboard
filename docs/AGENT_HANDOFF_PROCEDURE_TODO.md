# Agent Handoff Procedure — Documentation TODO

Purpose: Capture the steps and standards for creating and assigning implementer prompts to agents, so we can formalize this process in docs.

What to document
- Prompt template: Begin every handoff with: "You are an implementer. Refer to agents.md, .cursor, .codex and other project documentation to understand how to complete this task. Report your understanding to the user, and do not proceed until told to. <task‑specific instructions>".
- Gating rules (Critic): Use `.cursor/rules/presets/critic.mdc` checklist — diff <300 LOC, ≤3 modules, acceptance evidence, CI/tests green, no edits to `collaboration/state/**`.
- PR policy: Base branch `develop`, branch up‑to‑date (behind=0), size/scope limits (≤1000 LOC overall and ≤3 modules), task rule enforcement via `.cursor/rules/tasks/T-xxx.mdc`.
- Workflow: Assign prompts to agents; agents reply with understanding and wait for explicit APPROVE; then implement scoped changes only.
- Posting prompts: Add kickoff comments to the relevant PRs with scope, acceptance, and changescope; include any dependencies (e.g., PR coupling) and request acceptance evidence.
- Required checks: Collab Guard, Tests (backend 3.12/3.13, frontend, e2e as applicable), Quality, Security, Agent Validation (when enabled). Link to `.github/workflows/*`.
- Plan integration (optional): When multiple related fixes exist, add a short PlanSpec lane (CI/Docs) and run the plan pipeline to generate tasks and rules.
- Scaling: When to propose 5‑agent mode, safeguards (locks, validation), and approval step (see `agents.md`, `.cursor/rules/presets/integrator.mdc`).
- Ownership: Docs owner and review path for this procedure.

Next steps
- Create a permanent section in `agents.md` ("Handoff Procedure") and cross‑link from `CONTRIBUTING.md` (PR process) and the PR template.
- Optionally add a brief note in `README.md` under Governance to point to this procedure.

References
- `agents.md`
- `.cursor/rules/presets/critic.mdc`, `.cursor/rules/presets/planner.mdc`, `.cursor/rules/presets/integrator.mdc`
- `.github/pull_request_template.md`
- `.github/workflows/collab-guard.yml`, `agent-validation.yml`, `test.yml`, `quality-checks.yml`
