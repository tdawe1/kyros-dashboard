# Collaboration Summary (Codex)

Layout:
- `collaboration/state/`: tasks.json, locks.json, agents.json — small files; optimistic concurrency with ETag; atomic writes.
- `collaboration/events/events.jsonl`: append‑only event log; generate human `collaboration/logs/log.md`.
- `collaboration/plans/inbox/`: incoming PlanSpecs.
- `collaboration/tasks/<ID>/`: task scaffolds with acceptance and brief.

Leases:
- Use leases (TTL ~900s) only for files you will write; heartbeat every 300s; reclaim stale leases.

Events:
- Emit `status_changed`, `file_locked`, `lease_renewed`, `tests_run`, `pr_opened`, `approved`, `merged`, etc.

DoD:
- Tests updated/passing; static checks clean; docs updated; secret scan; critic review.

Refer to `agents.md` and `collaboration/architecture.md` for full details.

