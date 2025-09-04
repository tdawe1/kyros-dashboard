#!/usr/bin/env python3
"""
Collaboration helper CLI: ETag-based atomic writes, leases, and events.

Usage examples:
  python scripts/collab_cli.py emit-event '{"event":"tests_run","task":"task-001","result":"pass"}'
  python scripts/collab_cli.py acquire-lease frontend/playwright.config.js codex-cli task-004
  python scripts/collab_cli.py renew-lease <lock_id> codex-cli
  python scripts/collab_cli.py release-lease <lock_id> codex-cli
  python scripts/collab_cli.py generate-log
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

BASE = Path("collaboration")
STATE = BASE / "state"
EVENTS_DIR = BASE / "events"
EVENTS = EVENTS_DIR / "events.jsonl"
LOCKS = STATE / "locks.json"
TASKS = STATE / "tasks.json"

TTL_SECONDS = 900
HEARTBEAT_SECONDS = 300


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
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
