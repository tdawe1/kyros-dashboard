#!/usr/bin/env python3
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

try:
    from .base_jsonrpc import JSONRPCServer
    from .env import load_dotenvs
except ImportError:
    # Fallback for when running as console script
    from base_jsonrpc import JSONRPCServer
    from env import load_dotenvs

# Load .env files early (no override)
load_dotenvs()

ROOT = Path(os.getenv("COLLAB_ROOT", Path.cwd()))
BASE = Path(ROOT) / "collaboration"
STATE = BASE / "state"
EVENTS_DIR = BASE / "events"
EVENTS = EVENTS_DIR / "events.jsonl"
LOCKS = STATE / "locks.json"
TASKS = STATE / "tasks.json"
AGENTS = STATE / "agents.json"
LOGS = BASE / "logs" / "log.md"

TTL_SECONDS = int(os.getenv("COLLAB_TTL", "900"))
HEARTBEAT_SECONDS = int(os.getenv("COLLAB_HEARTBEAT", "300"))

# Task lifecycle definitions
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


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json_with_etag(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        return {"version": 1}, sha256_hex(b"")
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8")), sha256_hex(raw)


def write_json_atomic(path: Path, data: dict, expected_etag: str | None = None) -> dict:
    current, cur_etag = read_json_with_etag(path)
    if expected_etag and expected_etag != cur_etag:
        raise RuntimeError(
            f"ETag mismatch for {path}: expected {expected_etag}, got {cur_etag}"
        )
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    os.replace(tmp, path)
    new, new_etag = read_json_with_etag(path)
    return {"data": new, "etag": new_etag, "prev_etag": cur_etag}


# Schemas (optional validation if jsonschema available)
def _load_schema(kind: str):
    schema_map = {
        "tasks": BASE / "schema" / "tasks.schema.json",
        "locks": BASE / "schema" / "locks.schema.json",
        "agents": BASE / "schema" / "agents.schema.json",
    }
    p = schema_map.get(kind)
    if p and p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _validate(kind: str, data: dict):
    schema = _load_schema(kind)
    if not schema:
        return
    try:
        import jsonschema

        jsonschema.validate(instance=data, schema=schema)
    except Exception as e:
        raise RuntimeError(f"Schema validation failed for {kind}: {e}")


def emit_event(ev: dict):
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    ev = {**ev}
    ev.setdefault("ts", now_iso())
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(ev, ensure_ascii=False) + "\n")


srv = JSONRPCServer()


@srv.method("collab.get_state")
def get_state(params):
    kind = params.get("kind")
    path_map = {
        "tasks": TASKS,
        "locks": LOCKS,
        "agents": AGENTS,
        "events": EVENTS,
        "log": LOGS,
    }
    if kind not in path_map:
        raise ValueError("kind must be one of tasks|locks|agents|events|log")
    p = path_map[kind]
    if kind in ("events", "log"):
        text = p.read_text(encoding="utf-8") if p.exists() else ""
        etag = sha256_hex(text.encode("utf-8"))
        return {"text": text, "etag": etag}
    data, etag = read_json_with_etag(p)
    return {"data": data, "etag": etag}


@srv.method("collab.list_tasks")
def list_tasks(params):
    data, _ = read_json_with_etag(TASKS)
    tasks = data.get("tasks", [])
    status = params.get("status")
    assignee = params.get("assignee")
    if status:
        tasks = [t for t in tasks if t.get("status") == status]
    if assignee:
        tasks = [t for t in tasks if t.get("assignee") == assignee]
    return {"tasks": tasks}


@srv.method("collab.create_task")
def create_task(params):
    title = params["title"]
    description = params.get("description", "")
    labels = params.get("labels", [])
    priority = params.get("priority")
    assignee = params.get("assignee")
    data, etag = read_json_with_etag(TASKS)
    tasks = data.get("tasks", [])
    new_id = params.get("id") or f"task-{len(tasks) + 1:03d}"
    task = {
        "id": new_id,
        "title": title,
        "description": description,
        "status": "queued",
        "assignee": assignee,
        "priority": priority,
        "labels": labels,
        "dependencies": [],
        "blockers": [],
        "branch": None,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "dod": [],
        "needs": None,
    }
    tasks.append(task)
    new_data = {"version": data.get("version", 1), "tasks": tasks}
    _validate("tasks", new_data)
    result = write_json_atomic(TASKS, new_data, expected_etag=etag)
    emit_event(
        {
            "event": "task_created",
            "task": new_id,
            "prev_etag": result["prev_etag"],
            "new_etag": result["etag"],
        }
    )
    return {"id": new_id}


@srv.method("collab.update_task")
def update_task(params):
    task_id = params["id"]
    fields = {k: v for k, v in params.items() if k != "id"}
    data, etag = read_json_with_etag(TASKS)
    tasks = data.get("tasks", [])
    for t in tasks:
        if t.get("id") == task_id:
            if "status" in fields and fields["status"] not in ALLOWED_STATUSES:
                raise RuntimeError("Invalid status")
            t.update(fields)
            t["updated_at"] = now_iso()
            new_data = {"version": data.get("version", 1), "tasks": tasks}
            _validate("tasks", new_data)
            result = write_json_atomic(TASKS, new_data, expected_etag=etag)
            emit_event(
                {
                    "event": "task_updated",
                    "task": task_id,
                    "prev_etag": result["prev_etag"],
                    "new_etag": result["etag"],
                }
            )
            return {"ok": True}
    raise RuntimeError("Task not found")


@srv.method("collab.transition_task")
def transition_task(params):
    task_id = params["id"]
    new_status = params["new_status"]
    reason = params.get("reason")
    if new_status not in ALLOWED_STATUSES:
        raise RuntimeError("Invalid status")
    data, etag = read_json_with_etag(TASKS)
    tasks = data.get("tasks", [])
    for t in tasks:
        if t.get("id") == task_id:
            old_status = t.get("status")
            allowed = ALLOWED_TRANSITIONS.get(old_status, [])
            if new_status not in allowed:
                raise RuntimeError(f"Invalid transition {old_status} -> {new_status}")
            t["status"] = new_status
            t["updated_at"] = now_iso()
            new_data = {"version": data.get("version", 1), "tasks": tasks}
            _validate("tasks", new_data)
            result = write_json_atomic(TASKS, new_data, expected_etag=etag)
            emit_event(
                {
                    "event": "status_changed",
                    "task": task_id,
                    "old_status": old_status,
                    "new_status": new_status,
                    "reason": reason,
                    "prev_etag": result["prev_etag"],
                    "new_etag": result["etag"],
                }
            )
            return {"ok": True}
    raise RuntimeError("Task not found")


@srv.method("collab.suggest_assignee")
def suggest_assignee(params):
    labels = set(params.get("labels", []))
    data_tasks, _ = read_json_with_etag(TASKS)
    data_agents, _ = read_json_with_etag(AGENTS)
    backend_pool = ["codex-cli-1", "codex-cli-2"]
    frontend_pool = ["cursor-ide", "cursor-ide-2"]
    docs_pool = ["gemini-cli-1"]
    if {"backend", "devops", "ci"} & labels:
        pool = backend_pool
    elif {"frontend", "e2e"} & labels:
        pool = frontend_pool
    elif {"docs", "review"} & labels:
        pool = docs_pool
    else:
        pool = backend_pool + frontend_pool
    load = {a["id"]: 0 for a in data_agents.get("agents", []) if a.get("id") in pool}
    for t in data_tasks.get("tasks", []):
        if t.get("status") == "in_progress" and t.get("assignee") in load:
            load[t["assignee"]] += 1
    if not load:
        return {"assignee": None}
    assignee = sorted(load.items(), key=lambda kv: kv[1])[0][0]
    return {"assignee": assignee}


@srv.method("collab.auto_assign")
def auto_assign(params):
    """
    Auto-suggest an assignee based on labels and set it on the task.
    Params: { id: str, labels?: [str] }
    """
    task_id = params["id"]
    labels = params.get("labels")
    # If labels not provided, read them from the task
    if labels is None:
        data, _ = read_json_with_etag(TASKS)
        for t in data.get("tasks", []):
            if t.get("id") == task_id:
                labels = t.get("labels", [])
                break
        if labels is None:
            labels = []
    sug = suggest_assignee({"labels": labels})
    assignee = sug.get("assignee")
    if not assignee:
        return {"assignee": None, "updated": False}
    # Update the task's assignee
    update_task({"id": task_id, "assignee": assignee})
    return {"assignee": assignee, "updated": True}


@srv.method("collab.link_external")
def link_external(params):
    """
    Link an external reference to a task.
    Params: { id: str, provider: str, key?: str, value: str }
    Stores under task.external_ids[provider][key] = value (key defaults to "id").
    """
    task_id = params["id"]
    provider = params["provider"]
    key = params.get("key", "id")
    value = params["value"]
    data, etag = read_json_with_etag(TASKS)
    tasks = data.get("tasks", [])
    for t in tasks:
        if t.get("id") == task_id:
            ext = t.get("external_ids") or {}
            prov = ext.get(provider) or {}
            prov[key] = value
            ext[provider] = prov
            t["external_ids"] = ext
            t["updated_at"] = now_iso()
            new_data = {"version": data.get("version", 1), "tasks": tasks}
            _validate("tasks", new_data)
            result = write_json_atomic(TASKS, new_data, expected_etag=etag)
            emit_event(
                {
                    "event": "task_linked",
                    "task": task_id,
                    "provider": provider,
                    "key": key,
                    "value": value,
                    "prev_etag": result["prev_etag"],
                    "new_etag": result["etag"],
                }
            )
            return {"ok": True}
    raise RuntimeError("Task not found")


@srv.method("collab.emit_event")
def rpc_emit_event(params):
    emit_event(params)
    return {"ok": True}


@srv.method("collab.acquire_lease")
def rpc_acquire_lease(params):
    path = params["path"]
    owner = params["owner"]
    purpose = params.get("purpose", "")
    data, etag = read_json_with_etag(LOCKS)
    locks = data.get("locks", [])
    # prune stale
    now = datetime.now(timezone.utc)
    fresh = []
    for lease in locks:
        acq = lease.get("acquired_at")
        hb = lease.get("heartbeat_at", acq)
        ttl = int(lease.get("ttl_seconds", TTL_SECONDS))
        try:
            acq_t = datetime.fromisoformat(acq.replace("Z", "+00:00")) if acq else now
            hb_t = datetime.fromisoformat(hb.replace("Z", "+00:00")) if hb else now
        except Exception:
            continue
        if (now - acq_t).total_seconds() <= ttl and (now - hb_t).total_seconds() <= ttl:
            fresh.append(lease)
    locks = fresh
    for lease in locks:
        if lease["path"] == path:
            raise RuntimeError(f"Active lease exists for {path}: {lease['lock_id']}")
    lock_id = f"L-{hashlib.sha1((path + owner + now_iso()).encode()).hexdigest()[:8]}"
    new_lease = {
        "path": path,
        "owner": owner,
        "purpose": purpose,
        "lock_id": lock_id,
        "acquired_at": now_iso(),
        "ttl_seconds": TTL_SECONDS,
        "heartbeat_at": now_iso(),
    }
    locks.append(new_lease)
    new_data = {"version": 1, "locks": locks}
    _validate("locks", new_data)
    result = write_json_atomic(LOCKS, new_data, expected_etag=etag)
    emit_event(
        {
            "event": "file_locked",
            "path": path,
            "lock_id": lock_id,
            "owner": owner,
            "task": purpose,
            "prev_etag": result["prev_etag"],
            "new_etag": result["etag"],
        }
    )
    return {"lock_id": lock_id}


@srv.method("collab.release_lease")
def rpc_release_lease(params):
    lock_id = params["lock_id"]
    owner = params["owner"]
    data, etag = read_json_with_etag(LOCKS)
    before = len(data.get("locks", []))
    data["locks"] = [
        lock
        for lock in data.get("locks", [])
        if not (lock.get("lock_id") == lock_id and lock.get("owner") == owner)
    ]
    if len(data["locks"]) == before:
        raise RuntimeError("Lease not found or ownership mismatch")
    _validate("locks", data)
    result = write_json_atomic(LOCKS, data, expected_etag=etag)
    emit_event(
        {
            "event": "lease_released",
            "lock_id": lock_id,
            "owner": owner,
            "prev_etag": result["prev_etag"],
            "new_etag": result["etag"],
        }
    )
    return {"ok": True}


@srv.method("collab.generate_log")
def rpc_generate_log(params):
    # Simple log: dump tasks by id and last events
    from scripts.generate_collab_log import main as gen

    gen()
    text = LOGS.read_text(encoding="utf-8") if LOGS.exists() else ""
    return {"path": str(LOGS), "text": text}


@srv.method("collab.list_agents")
def rpc_list_agents(params):
    data, _ = read_json_with_etag(AGENTS)
    return data


@srv.method("collab.update_agent")
def rpc_update_agent(params):
    agent_id = params["id"]
    fields = {k: v for k, v in params.items() if k != "id"}
    data, etag = read_json_with_etag(AGENTS)
    agents = data.get("agents", [])
    found = False
    for a in agents:
        if a.get("id") == agent_id:
            a.update(fields)
            found = True
            break
    if not found:
        agents.append({"id": agent_id, **fields})
    new_agents = {"version": data.get("version", 1), "agents": agents}
    _validate("agents", new_agents)
    result = write_json_atomic(AGENTS, new_agents, expected_etag=etag)
    emit_event(
        {
            "event": "agent_updated",
            "agent": agent_id,
            "prev_etag": result["prev_etag"],
            "new_etag": result["etag"],
        }
    )
    return {"ok": True}


def main():
    srv.serve()


if __name__ == "__main__":
    main()
