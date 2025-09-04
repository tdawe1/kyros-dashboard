#!/usr/bin/env python3
"""
Import GitHub PR feedback into collaboration tasks via MCP servers.

Usage:
  python scripts/import_coderabbit_feedback.py --owner ORG --repo REPO --pr 123 [--assign] [--roadmap-id RID]

Requirements:
  - mcp package installed (-e mcp)
  - Optional: GITHUB_TOKEN for higher rate limits
  - Optional: COLLAB_ROOT to point at a different collaboration root
"""

import argparse
import yaml
from pathlib import Path
from textwrap import shorten


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--owner", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pr", type=int, required=True)
    ap.add_argument("--assign", action="store_true", help="Auto-assign based on labels")
    ap.add_argument("--roadmap-id", help="Link created tasks to this roadmap id", default=None)
    args = ap.parse_args()

    # Import server modules directly to avoid process orchestration
    from mcp import coderabbit_server as cr
    from mcp import kyros_collab_server as collab

    fb = cr.fetch_feedback({"owner": args.owner, "repo": args.repo, "pr": args.pr})
    suggestions = fb.get("suggestions", [])
    created = []
    for s in suggestions:
        typ = s.get("type")
        title = f"CR: {typ} from {s.get('author', 'unknown')}"
        body = s.get("body") or ""
        path = s.get("file")
        line = s.get("line")
        desc_lines = []
        if path:
            desc_lines.append(f"File: {path}")
        if line:
            desc_lines.append(f"Line: {line}")
        if body:
            desc_lines.append("")
            desc_lines.append(body)
        description = "\n".join(desc_lines)
        # Create task with labels that route to critic/backend by default
        labels = ["review", "coderabbit"]
        if path and path.startswith("frontend/"):
            labels.append("frontend")
        elif path and path.startswith("backend/"):
            labels.append("backend")
        res = collab.create_task(
            {
                "title": shorten(title, width=80, placeholder="…"),
                "description": description,
                "labels": labels,
                "priority": "P2",
            }
        )
        tid = res.get("id")
        if tid:
            # Link PR number
            collab.link_external(
                {"id": tid, "provider": "github", "key": "pr", "value": str(args.pr)}
            )
            if args.assign:
                collab.auto_assign({"id": tid, "labels": labels})
            # Optionally link to roadmap
            if args.roadmap_id:
                try:
                    rp = Path("project/roadmap.yml")
                    doc = yaml.safe_load(rp.read_text(encoding="utf-8")) or {}
                    def find(n, rid):
                        if n.get("id") == rid:
                            return n
                        for c in n.get("children", []) or []:
                            got = find(c, rid)
                            if got:
                                return got
                        return None
                    target = None
                    for root in (doc.get("nodes") or []):
                        target = find(root, args.roadmap_id)
                        if target:
                            break
                    if target:
                        links = target.get("links") or {}
                        links["task_id"] = tid
                        target["links"] = links
                        rp.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
                except Exception:
                    pass
            created.append(tid)
    print(f"Created tasks: {', '.join(created) if created else '(none)'}")


if __name__ == "__main__":
    main()
