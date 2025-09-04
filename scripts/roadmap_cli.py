#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


ROOTMAP = Path("project/roadmap.yml")


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Roadmap file not found: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def save_yaml(path: Path, data: Dict[str, Any]):
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def find_node(node: Dict[str, Any], node_id: str) -> Optional[Dict[str, Any]]:
    if node.get("id") == node_id:
        return node
    for c in node.get("children", []) or []:
        got = find_node(c, node_id)
        if got:
            return got
    return None


def find_node_and_parent(
    nodes: list, node_id: str, parent: Optional[Dict[str, Any]] = None
):
    for n in nodes:
        if n.get("id") == node_id:
            return n, parent
        child = find_node(n, node_id)
        if child:
            # We need to also find actual direct parent
            stack = [(n, None)]
            while stack:
                cur, par = stack.pop()
                if cur.get("id") == node_id:
                    return cur, par
                for ch in cur.get("children", []) or []:
                    stack.append((ch, cur))
    return None, None


def ensure_links(n: Dict[str, Any]) -> Dict[str, Any]:
    links = n.get("links")
    if links is None:
        links = {}
        n["links"] = links
    return links


def cmd_set_status(doc: Dict[str, Any], node_id: str, status: str):
    for n in doc.get("nodes", []) or []:
        target = find_node(n, node_id)
        if target:
            target["status"] = status
            return True
    return False


def cmd_set_owner(doc: Dict[str, Any], node_id: str, owner: str):
    for n in doc.get("nodes", []) or []:
        target = find_node(n, node_id)
        if target:
            target["owner"] = owner
            return True
    return False


def cmd_set_title(doc: Dict[str, Any], node_id: str, title: str):
    for n in doc.get("nodes", []) or []:
        target = find_node(n, node_id)
        if target:
            target["title"] = title
            return True
    return False


def cmd_add_node(
    doc: Dict[str, Any],
    node_id: str,
    title: str,
    parent_id: Optional[str],
    status: str,
    owner: Optional[str],
):
    new_node = {"id": node_id, "title": title, "status": status}
    if owner:
        new_node["owner"] = owner
    if parent_id:
        # attach under parent
        for n in doc.get("nodes", []) or []:
            p = find_node(n, parent_id)
            if p:
                p.setdefault("children", []).append(new_node)
                return True
        return False
    else:
        # top-level
        doc.setdefault("nodes", []).append(new_node)
        return True


def cmd_move_node(doc: Dict[str, Any], node_id: str, new_parent_id: Optional[str]):
    nodes = doc.get("nodes", []) or []
    # Remove from current parent
    target, parent = find_node_and_parent(nodes, node_id)
    if not target:
        return False

    # Remove from existing location
    def remove_from_parent(par, child):
        if par is None:
            # top-level
            nodes.remove(child)
        else:
            par_children = par.get("children", [])
            par_children.remove(child)

    remove_from_parent(parent, target)
    if new_parent_id:
        # attach to new parent
        for n in nodes:
            p = find_node(n, new_parent_id)
            if p:
                p.setdefault("children", []).append(target)
                return True
        # if parent not found, put back where it was (end)
        nodes.append(target)
        return False
    else:
        # move to top-level
        nodes.append(target)
        return True


def cmd_link_task(doc: Dict[str, Any], node_id: str, task_id: str):
    for n in doc.get("nodes", []) or []:
        target = find_node(n, node_id)
        if target:
            links = ensure_links(target)
            links["task_id"] = task_id
            return True
    return False


def cmd_sync_from_task(doc: Dict[str, Any], node_id: str):
    import json

    tasks_path = Path("collaboration/state/tasks.json")
    if not tasks_path.exists():
        raise SystemExit("tasks.json not found; cannot sync")
    tasks = json.loads(tasks_path.read_text(encoding="utf-8")).get("tasks", [])
    task_map = {t.get("id"): t for t in tasks}
    for n in doc.get("nodes", []) or []:
        target = find_node(n, node_id)
        if target:
            tid = (target.get("links") or {}).get("task_id")
            if not tid:
                raise SystemExit(f"Node {node_id} is not linked to a task")
            t = task_map.get(tid)
            if not t:
                raise SystemExit(f"Linked task not found: {tid}")
            st = t.get("status", "queued")
            # Map task status to roadmap status
            if st in ("done", "approved", "merging"):
                target["status"] = "done"
            elif st in ("in_progress", "review", "changes_requested"):
                target["status"] = "in_progress"
            elif st == "blocked":
                target["status"] = "blocked"
            else:
                target["status"] = "queued"
            return True
    return False


def regenerate_markdown():
    # Best-effort; keep failure non-fatal
    try:
        import subprocess

        subprocess.run(
            [
                sys.executable,
                "scripts/roadmap_tree.py",
                "project/roadmap.yml",
                "ROADMAP.md",
            ],
            check=True,
        )
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser(description="Roadmap CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sst = sub.add_parser("set-status")
    sst.add_argument("id")
    sst.add_argument(
        "status", choices=["queued", "in_progress", "approved", "done", "blocked"]
    )

    sso = sub.add_parser("set-owner")
    sso.add_argument("id")
    sso.add_argument("owner")

    sstt = sub.add_parser("set-title")
    sstt.add_argument("id")
    sstt.add_argument("title")

    addp = sub.add_parser("add")
    addp.add_argument("id")
    addp.add_argument("title")
    addp.add_argument("--parent")
    addp.add_argument("--status", default="queued")
    addp.add_argument("--owner")

    mov = sub.add_parser("move")
    mov.add_argument("id")
    mov.add_argument("--parent")

    lnk = sub.add_parser("link-task")
    lnk.add_argument("id")
    lnk.add_argument("task_id")

    sync = sub.add_parser("sync-from-task")
    sync.add_argument("id")

    args = ap.parse_args()
    doc = load_yaml(ROOTMAP)
    ok = False
    if args.cmd == "set-status":
        ok = cmd_set_status(doc, args.id, args.status)
    elif args.cmd == "set-owner":
        ok = cmd_set_owner(doc, args.id, args.owner)
    elif args.cmd == "set-title":
        ok = cmd_set_title(doc, args.id, args.title)
    elif args.cmd == "add":
        ok = cmd_add_node(
            doc, args.id, args.title, args.parent, args.status, args.owner
        )
    elif args.cmd == "move":
        ok = cmd_move_node(doc, args.id, args.parent)
    elif args.cmd == "link-task":
        ok = cmd_link_task(doc, args.id, args.task_id)
    elif args.cmd == "sync-from-task":
        ok = cmd_sync_from_task(doc, args.id)

    if not ok:
        raise SystemExit("Operation failed (id not found or invalid parent)")

    save_yaml(ROOTMAP, doc)
    regenerate_markdown()
    print("Updated roadmap and regenerated ROADMAP.md")


if __name__ == "__main__":
    main()
