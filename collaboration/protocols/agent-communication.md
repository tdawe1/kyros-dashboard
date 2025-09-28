## Inter-Agent Communication Protocol

This protocol defines lightweight, human- and machine-readable messages agents use
to coordinate work without persistent background monitoring.

### Message Types

- `BLOCKED`: Waiting on a dependency or resource.
  - Example: `BLOCKED: Waiting on T-502 for backend-tests green`

- `READY`: Task complete with outputs available.
  - Example: `READY: Task T-503 complete, outputs at collaboration/tasks/T-503/`

- `CONFLICT`: Resource is locked by another agent.
  - Example: `CONFLICT: Resource .github/workflows/test.yml locked by @impl-ci`

### Usage

- Post messages as short PR comments or as events in `collaboration/events/events.jsonl`.
- Include task id, resource path (if applicable), and a one‑line next action.

### Locking

- Use `collaboration/state/locks.json` for fine-grained file leases.
- Use `collaboration/coordination/agent-locks.yml` for coarse-grained domain locks
  (e.g., `backend_core`, `ci_workflows`).

### Retry & Idempotency

- All actions should be safe to retry; avoid non-deterministic side effects.
- Prefer small, atomic commits that are easy to revert.

