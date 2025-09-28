#!/usr/bin/env python3
"""
Collaboration helper CLI: ETag-based atomic writes, leases, and events.

Usage examples:
  python scripts/collab_cli.py emit-event '{"event":"tests_run","task":"task-001","result":"pass"}'
  python scripts/collab_cli.py acquire-lease frontend/playwright.config.js codex-cli task-004
  python scripts/collab_cli.py renew-lease <lock_id> codex-cli
  python scripts/collab_cli.py release-lease <lock_id> codex-cli
  python scripts/collab_cli.py generate-log

  # Tasks management
  python scripts/collab_cli.py list-tasks --status in_progress
  python scripts/collab_cli.py create-task --title "Add healthcheck" --labels backend,ci --priority P2 --assignee thomas [--roadmap-id R2.1.1]
  python scripts/collab_cli.py update-task task-010 --assignee codex-cli
  python scripts/collab_cli.py transition-task task-010 review
"""

import argparse
import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List
import yaml

BASE = Path("collaboration")
STATE = BASE / "state"
EVENTS_DIR = BASE / "events"
EVENTS = EVENTS_DIR / "events.jsonl"
LOCKS = STATE / "locks.json"
TASKS = STATE / "tasks.json"

TTL_SECONDS = 900
HEARTBEAT_SECONDS = 300

# Task lifecycle
ALLOWED_STATUSES = [
    "queued",
    "claimed",
    "in_progress",
    "review",
    "changes_requested",
    "approved",
    "merging",
    "done",
    "blocked",
    "failed",
    "abandoned",
]

ALLOWED_TRANSITIONS = {
    "queued": ["claimed", "in_progress", "abandoned"],
    "claimed": ["in_progress", "blocked", "abandoned"],
    "in_progress": ["review", "blocked", "failed"],
    "review": ["approved", "changes_requested", "failed"],
    "changes_requested": ["in_progress", "failed"],
    "approved": ["merging"],
    "merging": ["done", "failed"],
    "blocked": ["in_progress", "abandoned"],
    "failed": ["in_progress", "abandoned"],
    "abandoned": [],
    "done": [],
}


def utcnow_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json_with_etag(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        return {}, sha256_hex(b"")
    raw = path.read_bytes()
    etag = sha256_hex(raw)
    return json.loads(raw.decode("utf-8")), etag


def write_json_atomic(path: Path, data: dict, expected_etag: str | None = None) -> str:
    current, cur_etag = read_json_with_etag(path)
    if expected_etag and expected_etag != cur_etag:
        raise RuntimeError(
            f"ETag mismatch for {path}: expected {expected_etag}, got {cur_etag}"
        )
    temp = path.with_name(f".{path.name}.tmp-{uuid.uuid4().hex}")
    temp.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    os.replace(temp, path)
    # return new etag
    return read_json_with_etag(path)[1]


# ---------------------------
# Tasks management helpers
# ---------------------------

def _load_tasks():
    data, etag = read_json_with_etag(TASKS)
    return data.get("version", 1), data.get("tasks", []), etag


def _save_tasks(version: int, tasks: List[dict], etag: str) -> str:
    new = {"version": version, "tasks": tasks}
    return write_json_atomic(TASKS, new, expected_etag=etag)


def list_tasks_cli(status: str | None, assignee: str | None, output: str):
    version, tasks, _ = _load_tasks()
    if status:
        tasks = [t for t in tasks if t.get("status") == status]
    if assignee:
        tasks = [t for t in tasks if t.get("assignee") == assignee]
    if output == "json":
        print(json.dumps({"version": version, "tasks": tasks}, indent=2))
        return
    # default: table-ish
    print(f"# tasks (v{version}) — {len(tasks)} items")
    for t in tasks:
        lid = t.get("id")
        print(
            f"- {lid:>8} | {t.get('status','')} | {t.get('priority','')} | {t.get('assignee') or '-'} | {t.get('title','')}"
        )


def create_task_cli(title: str, description: str, labels: List[str], priority: str | None, assignee: str | None, id_override: str | None):
    version, tasks, etag = _load_tasks()
    new_id = id_override or f"task-{len(tasks) + 1:03d}"
    task = {
        "id": new_id,
        "title": title,
        "description": description or "",
        "status": "queued",
        "assignee": assignee,
        "priority": priority,
        "labels": [l for l in (labels or []) if l],
        "dependencies": [],
        "blockers": [],
        "branch": None,
        "created_at": utcnow_iso(),
        "updated_at": utcnow_iso(),
        "dod": [],
        "needs": None,
    }
    tasks.append(task)
    _save_tasks(version, tasks, etag)
    emit_event({"event": "task_created", "task": new_id})
    print(new_id)


def _link_task_to_roadmap(roadmap_id: str, task_id: str):
    rp = Path("project/roadmap.yml")
    if not rp.exists():
        raise RuntimeError("project/roadmap.yml not found; cannot link task to roadmap")
    doc = yaml.safe_load(rp.read_text(encoding="utf-8")) or {}

    def find(n: dict, rid: str):
        if n.get("id") == rid:
            return n
        for c in n.get("children", []) or []:
            got = find(c, rid)
            if got:
                return got
        return None

    target = None
    for root in (doc.get("nodes") or []):
        target = find(root, roadmap_id)
        if target:
            break
    if not target:
        raise RuntimeError(f"Roadmap id not found: {roadmap_id}")
    links = target.get("links") or {}
    links["task_id"] = task_id
    target["links"] = links
    rp.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")


def update_task_cli(task_id: str, fields: dict):
    version, tasks, etag = _load_tasks()
    for t in tasks:
        if t.get("id") == task_id:
            if "status" in fields and fields["status"] not in ALLOWED_STATUSES:
                raise RuntimeError("Invalid status")
            t.update({k: v for k, v in fields.items() if v is not None})
            t["updated_at"] = utcnow_iso()
            _save_tasks(version, tasks, etag)
            emit_event({"event": "task_updated", "task": task_id})
            return
    raise RuntimeError("Task not found")


def transition_task_cli(task_id: str, new_status: str):
    if new_status not in ALLOWED_STATUSES:
        raise RuntimeError("Invalid status")
    version, tasks, etag = _load_tasks()
    for t in tasks:
        if t.get("id") == task_id:
            old = t.get("status")
            allowed = ALLOWED_TRANSITIONS.get(old, [])
            if new_status not in allowed:
                raise RuntimeError(f"Invalid transition {old} -> {new_status}")
            t["status"] = new_status
            t["updated_at"] = utcnow_iso()
            _save_tasks(version, tasks, etag)
            emit_event({"event": "status_changed", "task": task_id, "old_status": old, "new_status": new_status})
            return
    raise RuntimeError("Task not found")


def normalize_event_format(event: dict) -> dict:
    """
    Shim to convert old kind/action format to new event format.
    Maps legacy events to the standardized event schema.
    """
    # If it already has an 'event' field, it's already in the new format
    if "event" in event:
        return event
    
    # Convert old format to new format
    kind = event.get("kind")
    action = event.get("action")
    task = event.get("task")
    
    if kind == "task" and action == "in_progress":
        return {
            "event": "status_changed",
            "task": task,
            "old_status": "queued",
            "new_status": "in_progress",
            "actor": event.get("actor", "unknown"),
            "notes": event.get("message", ""),
            "ts": event.get("ts", utcnow_iso())
        }
    elif kind == "pr" and action == "opened":
        return {
            "event": "pr_opened",
            "task": task,
            "pr": event.get("pr_number"),
            "url": event.get("url", ""),
            "actor": event.get("actor", "unknown"),
            "notes": event.get("message", ""),
            "ts": event.get("ts", utcnow_iso())
        }
    elif kind == "test" and action == "completed":
        return {
            "event": "tests_run",
            "task": task,
            "status": event.get("result", "unknown"),
            "actor": event.get("actor", "ci"),
            "notes": event.get("message", ""),
            "ts": event.get("ts", utcnow_iso())
        }
    elif kind == "review" and action == "requested":
        return {
            "event": "review_requested",
            "task": task,
            "actor": event.get("actor", "ci"),
            "notes": event.get("message", ""),
            "ts": event.get("ts", utcnow_iso())
        }
    elif kind == "review" and action == "approved":
        return {
            "event": "approved",
            "task": task,
            "actor": event.get("actor", "critic"),
            "notes": event.get("message", ""),
            "ts": event.get("ts", utcnow_iso())
        }
    elif kind == "merge" and action == "completed":
        return {
            "event": "merged",
            "task": task,
            "actor": event.get("actor", "integrator"),
            "notes": event.get("message", ""),
            "ts": event.get("ts", utcnow_iso())
        }
    
    # If we can't map it, return as-is but add a warning
    print(f"Warning: Unknown event format: {event}", file=sys.stderr)
    return event


def emit_event(event: dict):
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    event = normalize_event_format(event)
    event = {**event}
    event.setdefault("ts", utcnow_iso())
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def acquire_lease(path: str, owner: str, purpose: str):
    data, etag = read_json_with_etag(LOCKS)
    locks = data.get("locks", [])
    now = time.time()
    # prune stale
    fresh_locks = []
    for lease in locks:
        acquired = _parse_ts(lease.get("acquired_at"))
        heartbeat = _parse_ts(lease.get("heartbeat_at", lease.get("acquired_at")))
        if now - acquired > lease.get(
            "ttl_seconds", TTL_SECONDS
        ) or now - heartbeat > lease.get("ttl_seconds", TTL_SECONDS):
            continue
        fresh_locks.append(lease)
    locks = fresh_locks
    # ensure no active lease for same path
    for lease in locks:
        if lease["path"] == path:
            raise RuntimeError(f"Active lease exists for {path}: {lease['lock_id']}")
    lock_id = f"L-{uuid.uuid4().hex[:8]}"
    lease = {
        "path": path,
        "owner": owner,
        "purpose": purpose,
        "lock_id": lock_id,
        "acquired_at": utcnow_iso(),
        "ttl_seconds": TTL_SECONDS,
        "heartbeat_at": utcnow_iso(),
    }
    locks.append(lease)
    new_etag = write_json_atomic(
        LOCKS, {"version": 1, "locks": locks}, expected_etag=etag
    )
    emit_event(
        {
            "event": "file_locked",
            "path": path,
            "lock_id": lock_id,
            "owner": owner,
            "task": purpose,
            "prev_etag": etag,
            "new_etag": new_etag,
        }
    )
    print(lock_id)


def renew_lease(lock_id: str, owner: str):
    data, etag = read_json_with_etag(LOCKS)
    updated = False
    for lease in data.get("locks", []):
        if lease.get("lock_id") == lock_id and lease.get("owner") == owner:
            lease["heartbeat_at"] = utcnow_iso()
            updated = True
            break
    if not updated:
        raise RuntimeError("Lease not found or ownership mismatch")
    new_etag = write_json_atomic(LOCKS, data, expected_etag=etag)
    emit_event(
        {
            "event": "lease_renewed",
            "lock_id": lock_id,
            "owner": owner,
            "prev_etag": etag,
            "new_etag": new_etag,
        }
    )


def release_lease(lock_id: str, owner: str):
    data, etag = read_json_with_etag(LOCKS)
    before = len(data.get("locks", []))
    data["locks"] = [
        lease
        for lease in data.get("locks", [])
        if not (lease.get("lock_id") == lock_id and lease.get("owner") == owner)
    ]
    if len(data["locks"]) == before:
        raise RuntimeError("Lease not found or ownership mismatch")
    new_etag = write_json_atomic(LOCKS, data, expected_etag=etag)
    emit_event(
        {
            "event": "lease_released",
            "lock_id": lock_id,
            "owner": owner,
            "prev_etag": etag,
            "new_etag": new_etag,
        }
    )


def generate_log():
    from generate_collab_log import main as gen

    gen()


def _parse_ts(ts: str | None) -> float:
    if not ts:
        return 0.0
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except Exception:
        return 0.0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    ee = sub.add_parser("emit-event")
    ee.add_argument("json", help="JSON object as string")

    al = sub.add_parser("acquire-lease")
    al.add_argument("path")
    al.add_argument("owner")
    al.add_argument("purpose")

    rl = sub.add_parser("renew-lease")
    rl.add_argument("lock_id")
    rl.add_argument("owner")

    dl = sub.add_parser("release-lease")
    dl.add_argument("lock_id")
    dl.add_argument("owner")

    sub.add_parser("generate-log")

    # Tasks: list/create/update/transition
    lt = sub.add_parser("list-tasks")
    lt.add_argument("--status", choices=ALLOWED_STATUSES)
    lt.add_argument("--assignee")
    lt.add_argument("--output", choices=["table", "json"], default="table")

    ct = sub.add_parser("create-task")
    ct.add_argument("--title", required=True)
    ct.add_argument("--description", default="")
    ct.add_argument("--labels", default="")
    ct.add_argument("--priority")
    ct.add_argument("--assignee")
    ct.add_argument("--id")
    ct.add_argument("--roadmap-id")

    ut = sub.add_parser("update-task")
    ut.add_argument("id")
    ut.add_argument("--title")
    ut.add_argument("--description")
    ut.add_argument("--labels")
    ut.add_argument("--priority")
    ut.add_argument("--assignee")
    ut.add_argument("--status", choices=ALLOWED_STATUSES)

    tt = sub.add_parser("transition-task")
    tt.add_argument("id")
    tt.add_argument("new_status", choices=ALLOWED_STATUSES)

    args = ap.parse_args()
    try:
        if args.cmd == "emit-event":
            obj = json.loads(args.json)
            emit_event(obj)
        elif args.cmd == "acquire-lease":
            acquire_lease(args.path, args.owner, args.purpose)
        elif args.cmd == "renew-lease":
            renew_lease(args.lock_id, args.owner)
        elif args.cmd == "release-lease":
            release_lease(args.lock_id, args.owner)
        elif args.cmd == "generate-log":
            generate_log()
        elif args.cmd == "list-tasks":
            list_tasks_cli(args.status, args.assignee, args.output)
        elif args.cmd == "create-task":
            labels = [s.strip() for s in (args.labels or "").split(",") if s.strip()]
            create_task_cli(args.title, args.description, labels, args.priority, args.assignee, args.id)
            # If roadmap id provided, link it to the last created task id by reading tasks.json
            if args.roadmap_id:
                try:
                    _, tasks, _ = _load_tasks()
                    tid = tasks[-1]["id"] if tasks else None
                    if tid:
                        _link_task_to_roadmap(args.roadmap_id, tid)
                        print(f"Linked roadmap {args.roadmap_id} -> {tid}")
                except Exception as le:
                    print(f"Warning: failed to link roadmap: {le}", file=sys.stderr)
        elif args.cmd == "update-task":
            fields = {
                "title": args.title,
                "description": args.description,
                "priority": args.priority,
                "assignee": args.assignee,
            }
            # labels if present
            if args.labels is not None:
                fields["labels"] = [s.strip() for s in args.labels.split(",") if s.strip()]
            if args.status is not None:
                fields["status"] = args.status
            update_task_cli(args.id, fields)
        elif args.cmd == "transition-task":
            transition_task_cli(args.id, args.new_status)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
