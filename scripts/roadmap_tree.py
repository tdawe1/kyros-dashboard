#!/usr/bin/env python3
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple


STATUS_ORDER = {
    "done": 3,
    "approved": 2,
    "in_progress": 1,
    "queued": 0,
    "blocked": -1,
}


def load(path: Path) -> Dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def count(node: Dict) -> Tuple[int, int]:
    total = 1
    done = 1 if node.get("status") == "done" else 0
    for c in node.get("children", []) or []:
        d, t = count(c)
        done += d
        total += t
    return done, total


def status_badge(s: str) -> str:
    s = (s or "queued").lower()
    m = {
        "done": "[x]",
        "approved": "[x]",
        "in_progress": "[~]",
        "blocked": "[!]",
        "queued": "[ ]",
    }
    return m.get(s, "[ ]")


def render_node(node: Dict, prefix: str = "") -> List[str]:
    lines: List[str] = []
    d, t = count(node)
    badge = status_badge(node.get("status"))
    owner = f" @{node.get('owner')}" if node.get("owner") else ""
    title = f"{badge} {node.get('id', '')} — {node.get('title','')} ({d}/{t}){owner}"
    lines.append(prefix + title)

    kids = node.get("children", []) or []
    # stable order: done at bottom, then in_progress, then queued; keep declaration order for equal statuses
    kids_sorted = sorted(
        list(enumerate(kids)),
        key=lambda kv: STATUS_ORDER.get(kv[1].get("status", "queued"), 0),
        reverse=True,
    )
    last_idx = kids_sorted[-1][0] if kids_sorted else -1
    for idx, child in kids_sorted:
        is_last = idx == last_idx
        branch = "└─ " if is_last else "├─ "
        child_prefix = prefix + branch
        # For child children, indent with spacer
        sub_indent = prefix + ("   " if is_last else "│  ")
        lines.extend(render_node_lines(child, child_prefix, sub_indent))
    return lines


def render_node_lines(node: Dict, line_prefix: str, child_prefix: str) -> List[str]:
    # Render this node, then its children with child_prefix
    lines: List[str] = []
    d, t = count(node)
    badge = status_badge(node.get("status"))
    owner = f" @{node.get('owner')}" if node.get("owner") else ""
    title = f"{badge} {node.get('id','')} — {node.get('title','')} ({d}/{t}){owner}"
    lines.append(line_prefix + title)
    kids = node.get("children", []) or []
    for i, k in enumerate(kids):
        last = i == len(kids) - 1
        branch = "└─ " if last else "├─ "
        lp = child_prefix + branch
        cp = child_prefix + ("   " if last else "│  ")
        lines.extend(render_node_lines(k, lp, cp))
    return lines


def render(doc: Dict) -> str:
    title = doc.get("title", "Roadmap")
    nodes = doc.get("nodes", []) or []
    goals = doc.get("goals", []) or []
    # header + summary
    total = sum(count(n)[1] for n in nodes)
    done = sum(count(n)[0] for n in nodes)
    pct = int(round((done / total) * 100)) if total else 0
    lines = [f"# {title}", "", f"Progress: {done}/{total} ({pct}%)", ""]
    # Human-only goals section
    if goals:
        lines.append("## Goals")
        lines.append("")
        for g in goals:
            gid = g.get("id", "")
            title = g.get("title", "")
            lines.append(f"- {gid} — {title}")
            notes = g.get("notes")
            if notes:
                for ln in str(notes).strip().splitlines():
                    lines.append(f"  {ln}")
        lines.append("")
    for n in nodes:
        lines.extend(render_node(n))
        lines.append("")
    return "\n".join(lines)


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("project/roadmap.yml")
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("ROADMAP.md")
    doc = load(src)
    out.write_text(render(doc) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
