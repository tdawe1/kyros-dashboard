#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

TASKS_PATH = Path("collaboration/state/tasks.json")
OUT_PATH = Path("collaboration/board.md")


def load_tasks():
    if not TASKS_PATH.exists():
        return {"version": 1, "tasks": []}
    return json.loads(TASKS_PATH.read_text(encoding="utf-8"))


def sort_recent(tasks):
    def key(t):
        return t.get("updated_at") or t.get("created_at") or ""
    return sorted(tasks, key=key, reverse=True)


def render_board(data: dict) -> str:
    tasks = data.get("tasks", [])
    now = [t for t in tasks if t.get("status") == "in_progress"]
    nxt = [t for t in tasks if t.get("status") in ("queued", "claimed")]
    review = [t for t in tasks if t.get("status") in ("review", "changes_requested", "blocked")]
    done = [t for t in tasks if t.get("status") == "done"]

    lines = []
    lines.append("# Project Board")
    lines.append("")
    lines.append(f"Generated: {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append("")

    def external_badges(t: dict) -> str:
        ext = t.get("external_ids") or {}
        bits = []
        gh = ext.get("github") or {}
        if gh.get("issue"):
            bits.append(f"GH#{gh.get('issue')}")
        if gh.get("pr"):
            bits.append(f"PR#{gh.get('pr')}")
        lin = ext.get("linear") or {}
        if lin.get("id"):
            bits.append(f"LIN:{lin.get('id')}")
        return (" [" + ", ".join(bits) + "]") if bits else ""

    def section(title, items):
        lines.append(f"## {title} ({len(items)})")
        if not items:
            lines.append("")
            lines.append("- _None_")
            lines.append("")
            return
        lines.append("")
        for t in items:
            lid = t.get("id")
            pri = t.get("priority") or "-"
            who = t.get("assignee") or "-"
            title = t.get("title","")
            badges = external_badges(t)
            lines.append(f"- {lid} [{pri}] ({who}) — {title}{badges}")
        lines.append("")

    section("Now", sort_recent(now))
    section("Next", sort_recent(nxt))
    section("Review / Blocked", sort_recent(review))
    section("Done (recent 10)", sort_recent(done)[:10])

    return "\n".join(lines) + "\n"


def main():
    data = load_tasks()
    OUT_PATH.write_text(render_board(data), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
