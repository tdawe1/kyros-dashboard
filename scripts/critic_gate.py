#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path
from urllib.request import urlopen, Request


def load_tasks(root: Path):
    p = root / "collaboration/state/tasks.json"
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    return data.get("tasks", [])


def fail(msg: str):
    print(f"CRITIC GATE FAILED: {msg}", file=sys.stderr)
    sys.exit(1)


def check_tasks(tasks):
    # Fail if any review-blocking statuses exist on PR-related tasks
    blockers = [
        t
        for t in tasks
        if t.get("status") in ("changes_requested",)
        and ("review" in (t.get("labels") or []) or "pr" in (t.get("labels") or []))
    ]
    if blockers:
        ids = ", ".join(t.get("id") for t in blockers)
        fail(f"Tasks require changes: {ids}")
    # Optionally fail on blocked
    if os.getenv("EXPECT_NO_BLOCKED") == "1":
        bl = [t for t in tasks if t.get("status") == "blocked"]
        if bl:
            ids = ", ".join(t.get("id") for t in bl)
            fail(f"Blocked tasks present: {ids}")


def check_health():
    api = os.getenv("API_HEALTH_URL")
    if api:
        try:
            with urlopen(
                Request(api, headers={"User-Agent": "critic-gate"}), timeout=10
            ) as r:
                if r.status != 200:
                    fail(f"API health returned {r.status}")
                body = r.read().decode()
                if '"status": "ok"' not in body and '"status":"ok"' not in body:
                    fail("API health not ok")
        except Exception as e:
            fail(f"API health check failed: {e}")
    front = os.getenv("FRONTEND_URL")
    if front:
        try:
            with urlopen(
                Request(front, headers={"User-Agent": "critic-gate"}), timeout=10
            ) as r:
                if r.status >= 400:
                    fail(f"Frontend returned {r.status}")
        except Exception as e:
            fail(f"Frontend health check failed: {e}")


def main():
    root = Path(os.getenv("GITHUB_WORKSPACE", Path.cwd()))
    tasks = load_tasks(root)
    check_tasks(tasks)
    if os.getenv("REQUIRE_DEPLOY_HEALTH") == "1":
        check_health()
    print("CRITIC GATE PASSED")


if __name__ == "__main__":
    main()
