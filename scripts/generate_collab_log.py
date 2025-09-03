#!/usr/bin/env python3
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

EVENTS = Path("collaboration/events/events.jsonl")
OUT = Path("collaboration/logs/log.md")


def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def load_events(path: Path):
    items = []
    if not path.exists():
        return items
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                items.append(obj)
            except json.JSONDecodeError:
                continue
    return items


def render(tasks):
    lines = ["# Collaboration Log", "", f"Generated: {iso(datetime.utcnow())}", ""]
    for task_id, evs in tasks.items():
        evs.sort(key=lambda e: e.get("ts", ""))
        latest_status = None
        assignee = None
        branch = None
        for e in evs:
            if e.get("event") == "status_changed":
                latest_status = e.get("new_status")
            if e.get("assignee"):
                assignee = e.get("assignee")
            if e.get("branch"):
                branch = e.get("branch")
        lines.append(f"## {task_id}")
        lines.append("")
        if latest_status:
            lines.append(f"- Status: {latest_status}")
        if assignee:
            lines.append(f"- Assignee: {assignee}")
        if branch:
            lines.append(f"- Branch: {branch}")
        lines.append("")
        lines.append("### Timeline")
        for e in evs:
            ts = e.get("ts", "")
            event = e.get("event", "")
            notes = e.get("notes")
            line = f"- {ts} {event}"
            if notes:
                line += f": {notes}"
            lines.append(line)
        lines.append("")
    return "\n".join(lines) + "\n"


def main():
    events = load_events(EVENTS)
    grouped = defaultdict(list)
    for e in events:
        task = e.get("task", "(none)")
        grouped[task].append(e)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(grouped), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
