# agents.md — LLM Agent Collaboration (v2)

This document defines how multiple LLM coding agents coordinate work. It replaces the earlier simple lock/log flow with **lease-based locks**, a **task state machine**, and **structured events** so collaboration scales without deadlocks.

---

## Core principles

* **Single writer, many readers**: Agents read shared state freely, but writes use optimistic concurrency (ETag/hash) and atomic renames.
* **Leases, not locks**: File locks expire automatically (TTL + heartbeat). Stale work can be reclaimed.
* **Small, reviewable steps**: Branch per task, PR review by a separate critic role, definition-of-done enforced by gates.
* **Append-only events**: `events.jsonl` is the source of truth for history. Human logs are generated from events.

---

## Repository collaboration layout

```
collaboration/
  state/
    tasks.json          # task lifecycle, dependencies, DoD, priorities
    locks.json          # file/resource leases with TTL + heartbeat
    agents.json         # known agents, roles, capabilities, status
  events/
    events.jsonl        # append-only machine log (JSON Lines)
  logs/
    log.md              # human-readable summary (generated from events)
```

> Keep `state/*` small and focused to reduce merge conflicts.

---

## Roles

* **Planner** – decomposes work, defines acceptance criteria, sets dependencies.
* **Implementer** – writes code, tests, docs.
* **Critic** – reviews PRs, runs quality gates, enforces DoD.
* **Integrator** – merges approved work, updates changelog, tags releases.
* **Watchdog** – reclaims stale leases, re-queues blocked tasks, heals state.

> One physical agent can hold multiple roles. The role determines gates and permissions.

---

## Quickstart (TL;DR)

1. Sync repo and read state: pull latest `main`, inspect `collaboration/state/*` and prune stale leases if required.
2. Claim a task: pick highest‑priority `queued`, set `status: claimed`, set `assignee`, create branch `feat/<task-id>-slug`.
3. Acquire leases: add leases only for files you will edit (TTL ≈ 15m; heartbeat every 5m).
4. Implement: small commits; run gates (format, lint, type, unit tests, secret scan) locally.
5. Open PR: set task `status: review`, assign a critic; release unneeded leases.
6. Integrate: on approval → `approved → merging → done`, release all leases, regenerate logs.

IDs: Current repo uses IDs like `task-00x`. Examples here also show `T-142` style. Either is acceptable; be consistent per task/thread and include the chosen ID in branches/commits.

---

## Task Slicing & Commits

- Smallest viable steps: Aim for 10–60 minute subtasks that can be code‑reviewed independently and rolled back safely.
- Commit cadence: Commit after every coherent change (1–5 files, ~10–200 LOC). Don’t batch unrelated edits.
- Message format: Keep the template, but be specific to the subtask.
  - `feat(task-007-01): add MCP env autoload`
  - Why/Touches/Tests/Risks sections stay concise and focused.
- Change size guardrails: Prefer ≤200 LOC per commit and ≤400 LOC per PR unless mechanical.
- Branching: One branch per task; subtasks are sequential commits. If a subtask becomes large, branch off a temporary sub-branch and squash back before PR.

Subtask IDs
- Use `task-<parent>-NN` (e.g., `task-007-01`, `task-007-02`) or `task-007-a/b`.
- Record subtask IDs in commit messages and events for traceability.

Events to emit
- `subtask_started` / `subtask_completed` with `{task, subtask, notes}`.
- `commit_pushed` with `{task, subtask, sha, summary}` when applicable.
- Continue emitting `tests_run`, `file_locked`, `lease_renewed`, etc.

---

## Context Reset Protocol

Goal: minimize drift by clearing conversational context between subtasks.

At every subtask boundary:
- End the chat/session and start a new one (Cursor/Claude: open a fresh chat).
- Rehydrate only minimal context:
  - Task ID, title, acceptance criteria (DoD), and any blockers/dependencies.
  - Current state from `collab.get_state(kind="tasks")` for the specific task.
  - Open leases relevant to the next change (if any).
- Post the following handoff snippet to kick off the next subtask:

```
Context Reset: New subtask
Task: <task-id> — <title>
Subtask: <task-id-NN> — <one-line goal>
DoD: <bulleted acceptance criteria>
Constraints: small diff, tests updated, no secrets, follow agents.md
Plan: <3–5 steps>
Output: code changes only; summarize what changed and next subtask suggestion
```

Operational notes
- Don’t carry forward prior chat content. If needed, paste a one‑paragraph summary only.
- Emit `context_reset` event with `{task, subtask, reason: "boundary"}`.
- If an agent needs broader context, read the code/state again; avoid long free‑form recap.

## Task lifecycle (state machine)

Statuses and transitions:

```
queued → claimed → in_progress → review → approved → merging → done
            ↘ blocked ↘ failed ↘ abandoned
            ↘ changes_requested → in_progress
```

Rules:

* Transitions must be recorded as events with `old_status`, `new_status`, and `reason` when relevant.
* A task in `blocked` must include a `needs` field (what’s required to unblock).

---

## Definition of Done (DoD)

A task is **not** `approved` until all are true:

* Unit tests added/updated and passing locally.
* Static checks: formatter, linter, type checker (if applicable).
* Secret scan clean (no tokens/keys).
* Docs updated (README/architecture/ADR if design changed).
* Backwards-compatibility considered (document any breaks).
* Reviewed by a **critic** agent (not the implementer).

Include the DoD checklist as an array on each task in `tasks.json`.

---

## Locking model (leases)

Defaults and behaviour:

* A lock is a **lease** with: `owner`, `purpose` (task id), `acquired_at` (ISO-8601 UTC), `ttl_seconds`, and `heartbeat_at`.
* Baselines: `ttl_seconds = 900` (15 minutes), heartbeat every `300` seconds (5 minutes). A lease is stale if `now > acquired_at + ttl_seconds` or `now - heartbeat_at > ttl_seconds`.
* Lock **only** files you intend to write. Reads don’t need locks.
* Prefer optimistic `git` merges to locking. Use locks for non-mergeable edits or mechanical refactors.

---

## Events (append-only)

* File: `collaboration/events/events.jsonl`
* Each line is a JSON object with a `ts` (ISO-8601 UTC), `event`, and contextual fields.
* Recommended fields: `agent`, `task`, `old_status`, `new_status`, `path`, `lock_id`, `branch`, `prev_etag`, `new_etag`, `notes`.
* Typical events: `task_created`, `task_claimed`, `status_changed`, `file_locked`, `lease_renewed`, `locks_reclaimed`, `tests_run`, `pr_opened`, `review_requested`, `review_feedback`, `approved`, `merged`, `released`, `error`.
* To reduce conflicts, agents may append to per-agent files under `collaboration/events/agents/<agent>.jsonl` and periodically consolidate.
* Human-readable `logs/log.md` is generated from these events.

---

## State write protocol (atomic + optimistic)

1. Read `state/*` and compute an ETag as `sha256` of the file bytes (hex-encoded).
2. Prepare changes; validate against schema.
3. Write to a temp file in the same directory and perform an atomic replace to the target:
   - POSIX/Windows: `os.replace(temp, target)` is atomic.
4. Emit an event including `prev_etag` and `new_etag`. If the current ETag changed since read, abort, re-read, and retry with backoff (jitter 200–800ms).

> Avoid a global `state.json.lock` file. The optimistic approach plus small files reduces contention and deadlocks.

---

## Agent workflow

1. **Sync & Health**

   * Pull latest `main`.
   * Read `state/*`. Identify stale leases; reclaim if necessary (emit `locks_reclaimed`).

2. **Claim a task**

   * Pick highest-priority `queued` task whose dependencies are satisfied.
   * Set status to `claimed`, set `assignee`, create branch `feat/<task-id>-slug`.
   * Write state with ETag; on conflict, re-read and retry.

3. **Acquire leases**

   * Add entries to `locks.json` for files you will edit. TTL ≈ 15 minutes. Start heartbeat.

4. **Implement**

   * Small commits with message: `feat(T-142): short summary`.
   * Run gates locally: format, lint, type check, unit tests, secret scan.
   * Emit `tests_run` events with summary.

5. **Request review**

   * Open PR, set task `status: review`, assign a **critic**.
   * Release locks you no longer need; keep leases if you expect changes.

6. **Critic pass**

   * Run checks. Emit `review_feedback` with status `changes_requested` or `approved`.

7. **Integrate**

   * `approved → merging → done`. Merge/rebase after green gates.
   * Release all locks, update changelog, emit `merged`.

8. **Failure & recovery**

   * If blocked or stalled, set `blocked` with a `reason` and `needs`.
   * Watchdog re-queues or splits the task after a grace period.

---

## RPC Cheat Sheet (collab.*)

- `collab.get_state` (kind): Return `{data, etag}` for `tasks|locks|agents`, or `{text, etag}` for `events|log`.
  - Params: `{"kind":"tasks"|"locks"|"agents"|"events"|"log"}`
- `collab.list_tasks` (filters): List tasks, optionally by `status` and/or `assignee`.
  - Params: `{status?: string, assignee?: string}`
- `collab.create_task` (create): Create a task, defaults to `queued`.
  - Params: `{title: string, description?: string, labels?: string[], priority?: string, assignee?: string, id?: string}`
- `collab.update_task` (patch): Update fields on a task; validates status.
  - Params: `{id: string, ...fields}`
- `collab.transition_task` (status change): Enforce state machine transitions.
  - Params: `{id: string, new_status: string, reason?: string}`
- `collab.suggest_assignee` (heuristic): Recommend an assignee from agent pools.
  - Params: `{labels?: string[]}`
- `collab.auto_assign` (apply): Suggest and set an assignee on a task.
  - Params: `{id: string, labels?: string[]}`
- `collab.link_external` (refs): Attach external IDs to a task under `external_ids[provider][key]`.
  - Params: `{id: string, provider: string, value: string, key?: string}`
- `collab.emit_event` (append): Append any event to `events.jsonl`.
  - Params: arbitrary event object
- `collab.acquire_lease` / `collab.release_lease` (leases): Manage file leases with TTL + heartbeat.
  - Params: `{path: string, owner: string, purpose?: string}` / `{lock_id: string, owner: string}`
- `collab.list_agents` / `collab.update_agent` (agents): List or upsert agent metadata.
  - Params: none / `{id: string, ...fields}`
- `collab.generate_log` (md): Regenerate `collaboration/logs/log.md` from events.
  - Params: none

Examples (stdio): see `mcp/README.md` for `python -m mcp.kyros_collab_server` piping.

---

## Commit message template

```
<type>(<task-id>): <summary>

Why: <rationale>
Touches: <files or globs>
Tests: <how it’s covered>
Risks/Mitigations: <notes>
```

Allowed `<type>`: feat, fix, refactor, test, docs, chore, perf, build, ci.

---

## JSON schemas (lightweight, enforced by convention)

### `state/tasks.json`

```json
{
  "version": 1,
  "tasks": [
    {
      "id": "T-142",
      "title": "Implement async job runner",
      "description": "Add queue + retry + idempotency.",
      "status": "queued",
      "assignee": null,
      "priority": "P1",
      "labels": ["backend", "infra"],
      "dependencies": ["T-103"],
      "blockers": [],
      "branch": null,
      "created_at": "2025-09-03T10:32:00Z",
      "updated_at": "2025-09-03T10:32:00Z",
      "dod": [
        "Unit tests for success/failure/retry",
        "Docs updated",
        "Secret scan clean"
      ],
      "needs": null
    }
  ]
}
```

**Allowed statuses:** `queued`, `claimed`, `in_progress`, `review`, `changes_requested`, `approved`, `merging`, `done`, `blocked`, `failed`, `abandoned`.

### `state/locks.json`

```json
{
  "version": 1,
  "locks": [
    {
      "path": "src/queue/runner.py",
      "owner": "agent.impl.1",
      "purpose": "T-142",
      "lock_id": "L-673a",
      "acquired_at": "2025-09-03T10:40:00Z",
      "ttl_seconds": 900,
      "heartbeat_at": "2025-09-03T10:50:00Z"
    }
  ]
}
```

### `state/agents.json`

```json
{
  "version": 1,
  "agents": [
    {
      "id": "agent.planner.1",
      "role": "planner",
      "skills": ["task_decomposition", "acceptance_criteria"],
      "status": "idle",
      "last_seen": "2025-09-03T10:55:00Z"
    },
    {
      "id": "agent.impl.1",
      "role": "implementer",
      "skills": ["python", "fastapi", "pytest"],
      "status": "idle",
      "last_seen": "2025-09-03T10:55:00Z"
    },
    {
      "id": "agent.critic.1",
      "role": "critic",
      "skills": ["tests", "coverage", "security"],
      "status": "idle",
      "last_seen": "2025-09-03T10:55:00Z"
    },
    {
      "id": "agent.integrator.1",
      "role": "integrator",
      "skills": ["git", "release", "changelog"],
      "status": "idle",
      "last_seen": "2025-09-03T10:55:00Z"
    },
    {
      "id": "agent.watchdog.1",
      "role": "watchdog",
      "skills": ["lease_recovery", "queue_management"],
      "status": "idle",
      "last_seen": "2025-09-03T10:55:00Z"
    }
  ]
}
```

### `events/events.jsonl` (example lines)

```json
{"ts":"2025-09-03T10:41:00Z","event":"task_claimed","task":"T-142","agent":"agent.impl.1","branch":"feat/T-142-async-runner","state_etag":"d9c1"}
{"ts":"2025-09-03T10:44:12Z","event":"file_locked","path":"src/queue/runner.py","lock_id":"L-673a","ttl":900}
{"ts":"2025-09-03T11:02:33Z","event":"tests_run","task":"T-142","result":"pass","report":"reports/unit.xml"}
{"ts":"2025-09-03T11:05:01Z","event":"review_requested","task":"T-142","agent":"agent.critic.1","pr":"#87"}
{"ts":"2025-09-03T11:14:45Z","event":"review_feedback","task":"T-142","status":"changes_requested","notes":"Add idempotency test for network timeout"}
{"ts":"2025-09-03T11:40:27Z","event":"merged","task":"T-142","sha":"a1b2c3d","branch":"feat/T-142-async-runner"}
```

---

## Quickdrop stubs

Create these files with the content above:

* `collaboration/state/tasks.json`
* `collaboration/state/locks.json`
* `collaboration/state/agents.json`
* `collaboration/events/events.jsonl` (can start empty)
* `collaboration/logs/log.md` (generated from events)

Optional extras:

* `CHANGELOG.md` (maintained by Integrator)
* `decisions/adr-0001-template.md` (ADR template)
* `rules.md` (DoD + coding standards + secret policy)

---

## Minimal generator for `logs/log.md`

Implementation-agnostic algorithm:

1. Read `events.jsonl`.
2. Group by `task`, then order by `ts`.
3. Summarize: latest status, assignee, branch, last test result, open PR, merged sha.
4. Render a Markdown section per task, include a compact timeline of events.

> Any agent can own this; run on demand or after merges.

---

## Helper CLI

This repo ships a minimal helper at `scripts/collab_cli.py`:

Examples:

```
# Append an event
python scripts/collab_cli.py emit-event '{"event":"tests_run","task":"task-001","result":"pass"}'

# Acquire / renew / release a lease (15-minute TTL)
python scripts/collab_cli.py acquire-lease frontend/playwright.config.js codex-cli task-004
python scripts/collab_cli.py renew-lease L-1234abcd codex-cli
python scripts/collab_cli.py release-lease L-1234abcd codex-cli

# Generate human log from events
python scripts/collab_cli.py generate-log
```

The helper implements ETag-checked atomic writes to `state/*`, lease management with TTL + heartbeat, and event emission.

---

## MCP servers: env and launch

- Env loading: MCP servers auto-load `.env` and `collaboration/.env` at startup without overriding existing variables. Keep real tokens in those files (never commit them) or inject via your IDE/runner.
- IDE/clients: `.cursor/environment.json` defines per-server env for Cursor; other MCP clients can pass env similarly.
- Launch commands (preferred):
  - `python -m mcp.kyros_collab_server`
  - `python -m mcp.linear_server`
  - `python -m mcp.railway_server`
  - `python -m mcp.vercel_server`
  - `python -m mcp.coderabbit_server`
  These use stdio JSON-RPC as described in `mcp/README.md`.

---

## Local commands

- Run tests:
  - Full: `./scripts/run-tests.sh`
  - Frontend: `cd frontend && npm test` (unit), `npm run test:e2e` (Playwright)
  - Backend: `cd backend && python -m pytest`
- Pre-commit (format, lint, checks): `pre-commit run -a` (install hooks with `pre-commit install`)
- Regenerate human log: `python scripts/collab_cli.py generate-log` or RPC `collab.generate_log`

---

## Client config

- Cursor: `.cursor/environment.json` contains MCP server commands and env mapping.
- Generic clients: use `mcp/mcp.config.example.json` as a template; point commands to `python -m mcp.<server>` and pass env as needed.

---

## Migration plan (from v1 state.json)

1. Create the new `collaboration/state/*.json`, `collaboration/events/events.jsonl`, and `collaboration/logs/log.md` files.
2. Migrate tasks from the legacy `collaboration/state.json` to `state/tasks.json`, mapping statuses to the new state machine.
3. Register agents in `state/agents.json` (codex-cli, gemini-cli, plus any additional agents) with role and skills.
4. Stop using the legacy `state.json.lock`; rely on the ETag protocol and `state/locks.json`.
5. Start emitting events for every state transition and lease action; regenerate `logs/log.md` as needed.

---

## Conflict resolution rules

* **ETag mismatch on state write** → re-read, re-evaluate action, retry with backoff.
* **Concurrent lease request** → if an active lease exists, wait or request a glob/directory lease only if performing a mechanical refactor.
* **Stale lease** → any agent may reclaim; must emit `locks_reclaimed` with details.

---

## Security notes

* Do not log secrets or PII. Redact known patterns (API keys, tokens) in event emission.
* Run secret scans in pre-commit and in critic checks; block merges on findings.

---

## Adoption checklist

* [ ] Create the `collaboration/` tree with the stubs in this doc.
* [ ] Point all agents to use this workflow.
* [ ] Add pre-commit hooks (format, lint, type, unit, secrets).
* [ ] Define planner → implementer → critic → integrator assignments in `agents.json`.
* [ ] Enforce PR review before merge.

---

**End of agents.md**
