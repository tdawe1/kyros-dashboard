#!/usr/bin/env python3
"""
Sync roadmap nodes and tasks to GitHub Issues and (optionally) record their issue numbers
back into collaboration/state/tasks.json. Designed for use in GitHub Actions with GITHUB_TOKEN.

Behavior:
- Roadmap: For each node in project/roadmap.yml, ensure an issue exists labeled 'roadmap'.
  The issue title is "[Roadmap] <ID> — <Title>" and body contains a marker <!--ROADMAP_ID:ID-->
  If status == done, the issue is closed; otherwise open.
- Tasks: For each task without external_ids.github.issue, create a new issue titled
  "[Task] <ID>: <Title>" with body marker <!--TASK_ID:ID-->, label 'task', then write the
  issue number back into tasks.json under external_ids.github.issue.

Outputs:
- Writes a newline-separated list of created/updated issue numbers to tmp/created_issues.txt

Note: This is idempotent; re-running updates existing issues instead of creating duplicates.
"""

import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
import yaml


REPO = os.getenv("GITHUB_REPOSITORY", "").split("/")
OWNER = os.getenv("GITHUB_REPOSITORY_OWNER") or (REPO[0] if len(REPO) == 2 else None)
REPO_NAME = (REPO[1] if len(REPO) == 2 else os.getenv("GITHUB_REPO_NAME"))
TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")

API = "https://api.github.com"

ROADMAP = Path("project/roadmap.yml")
TASKS = Path("collaboration/state/tasks.json")
OUT_DIR = Path("tmp")
OUT_DIR.mkdir(parents=True, exist_ok=True)
CREATED_FILE = OUT_DIR / "created_issues.txt"


def gh_headers():
    h = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    return h


def gh(url: str, method: str = "GET", **kwargs):
    resp = requests.request(method, url, headers=gh_headers(), timeout=30, **kwargs)
    if resp.status_code >= 400:
        raise RuntimeError(f"GitHub API {method} {url} failed: {resp.status_code} {resp.text[:200]}")
    return resp


def list_issues_by_label(label: str) -> List[dict]:
    issues = []
    page = 1
    while True:
        r = gh(
            f"{API}/repos/{OWNER}/{REPO_NAME}/issues",
            params={"labels": label, "state": "all", "per_page": 100, "page": page},
        )
        batch = r.json()
        if not batch:
            break
        issues.extend(batch)
        page += 1
        if len(batch) < 100:
            break
    return issues


def upsert_label(name: str, color: str = "0e8a16"):
    # Create if missing; ignore if exists
    r = requests.get(f"{API}/repos/{OWNER}/{REPO_NAME}/labels/{name}", headers=gh_headers(), timeout=15)
    if r.status_code == 200:
        return
    requests.post(
        f"{API}/repos/{OWNER}/{REPO_NAME}/labels",
        headers=gh_headers(),
        json={"name": name, "color": color},
        timeout=15,
    )


def load_tasks() -> Dict:
    if not TASKS.exists():
        return {"version": 1, "tasks": []}
    return json.loads(TASKS.read_text(encoding="utf-8"))


def save_tasks(data: Dict):
    TASKS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def flatten_roadmap_nodes(doc: Dict) -> List[Dict]:
    out: List[Dict] = []
    def walk(n: Dict):
        out.append(n)
        for c in n.get("children", []) or []:
            walk(c)
    for root in doc.get("nodes", []) or []:
        walk(root)
    return out


def sync_roadmap_nodes(created: List[int]):
    if not ROADMAP.exists():
        return
    upsert_label("roadmap", "0366d6")
    doc = yaml.safe_load(ROADMAP.read_text(encoding="utf-8")) or {}
    # Build map of nodes and their children
    def walk_tree(n: Dict, parent: Optional[str] = None, acc: Dict[str, Dict] = None, edges: Dict[str, List[str]] = None):
        acc = acc or {}
        edges = edges or {}
        nid = n.get("id")
        acc[nid] = n
        kids = [c.get("id") for c in (n.get("children") or [])]
        edges[nid] = kids
        for c in (n.get("children") or []):
            walk_tree(c, nid, acc, edges)
        return acc, edges

    all_nodes: Dict[str, Dict] = {}
    edges: Dict[str, List[str]] = {}
    for root in doc.get("nodes", []) or []:
        acc, ed = walk_tree(root)
        all_nodes.update(acc)
        edges.update(ed)

    existing = list_issues_by_label("roadmap")
    by_marker: Dict[str, dict] = {}
    for iss in existing:
        body = iss.get("body") or ""
        m = re.search(r"<!--ROADMAP_ID:([^>]+)-->", body)
        if m:
            by_marker[m.group(1).strip()] = iss

    # First pass: ensure each node has an issue
    roadmap_issue_no: Dict[str, int] = {}
    for nid, n in all_nodes.items():
        title = n.get("title", "")
        status = (n.get("status") or "queued").lower()
        owner = n.get("owner")
        issue_title = f"[Roadmap] {nid} — {title}"
        # minimal body for creation; will enrich later
        base_body = f"<!--ROADMAP_ID:{nid}-->\nStatus: {status}\n" + (f"\nOwner: @{owner}\n" if owner else "")
        exists = by_marker.get(nid)
        if exists:
            number = exists["number"]
            state = "closed" if status == "done" else "open"
            gh(
                f"{API}/repos/{OWNER}/{REPO_NAME}/issues/{number}",
                method="PATCH",
                json={"title": issue_title, "body": base_body, "state": state},
            )
            roadmap_issue_no[nid] = number
            created.append(number)
        else:
            r = gh(
                f"{API}/repos/{OWNER}/{REPO_NAME}/issues",
                method="POST",
                json={"title": issue_title, "body": base_body, "labels": ["roadmap"]},
            )
            number = r.json()["number"]
            roadmap_issue_no[nid] = number
            if status == "done":
                gh(
                    f"{API}/repos/{OWNER}/{REPO_NAME}/issues/{number}",
                    method="PATCH",
                    json={"state": "closed"},
                )
            created.append(number)

    # Second pass: update bodies with child checklists
    for nid, n in all_nodes.items():
        number = roadmap_issue_no.get(nid)
        if not number:
            continue
        status = (n.get("status") or "queued").lower()
        owner = n.get("owner")
        header = f"<!--ROADMAP_ID:{nid}-->\nStatus: {status}\n" + (f"\nOwner: @{owner}\n" if owner else "")
        children = edges.get(nid) or []
        if children:
            lines = [header, "\n### Children", ""]
            for cid in children:
                cnum = roadmap_issue_no.get(cid)
                cnode = all_nodes.get(cid) or {}
                ctitle = cnode.get("title", "")
                cstatus = (cnode.get("status") or "queued").lower()
                checked = "x" if cstatus == "done" else " "
                if cnum:
                    lines.append(f"- [{checked}] {cid} — {ctitle} (#{cnum})")
                else:
                    lines.append(f"- [{checked}] {cid} — {ctitle}")
            body = "\n".join(lines)
        else:
            body = header
        gh(
            f"{API}/repos/{OWNER}/{REPO_NAME}/issues/{number}",
            method="PATCH",
            json={"body": body},
        )


def sync_tasks(created: List[int]):
    upsert_label("task", "a2eeef")
    data = load_tasks()
    tasks = data.get("tasks", [])
    changed = False
    # Build existing mapping for task issues by marker
    existing_tasks = list_issues_by_label("task")
    by_marker: Dict[str, dict] = {}
    for iss in existing_tasks:
        body = iss.get("body") or ""
        m = re.search(r"<!--TASK_ID:([^>]+)-->", body)
        if m:
            by_marker[m.group(1).strip()] = iss

    for t in tasks:
        tid = t.get("id")
        ext = t.get("external_ids") or {}
        ghinfo = ext.get("github") or {}
        issue_num = ghinfo.get("issue")
        # Create or update issue
        title = t.get("title", "")
        issue_title = f"[Task] {tid}: {title}"
        body = f"<!--TASK_ID:{tid}-->\n\n{t.get('description','')}\n"
        # Prepare labels: 'task' + task labels + priority if present
        tlabels = ["task"]
        for lbl in t.get("labels", []) or []:
            if lbl:
                upsert_label(lbl)
                tlabels.append(lbl)
        prio = (t.get("priority") or "").upper()
        if prio in ("P1", "P2", "P3"):
            upsert_label(prio, "ededed")
            tlabels.append(prio)
        # Determine desired state
        tstatus = (t.get("status") or "queued").lower()
        desired_state = "closed" if tstatus in ("done", "cancelled") else "open"
        if issue_num:
            # Update title/body if needed
            gh(
                f"{API}/repos/{OWNER}/{REPO_NAME}/issues/{issue_num}",
                method="PATCH",
                json={"title": issue_title, "body": body, "labels": tlabels, "state": desired_state},
            )
            created.append(int(issue_num))
        else:
            exists = by_marker.get(tid)
            if exists:
                number = exists["number"]
                gh(
                    f"{API}/repos/{OWNER}/{REPO_NAME}/issues/{number}",
                    method="PATCH",
                    json={"title": issue_title, "body": body, "labels": tlabels, "state": desired_state},
                )
                # write back
                ext.setdefault("github", {})["issue"] = number
                t["external_ids"] = ext
                changed = True
                created.append(number)
            else:
                r = gh(
                    f"{API}/repos/{OWNER}/{REPO_NAME}/issues",
                    method="POST",
                    json={"title": issue_title, "body": body, "labels": tlabels},
                )
                number = r.json()["number"]
                ext.setdefault("github", {})["issue"] = number
                t["external_ids"] = ext
                # Close immediately if done/cancelled
                if desired_state == "closed":
                    gh(
                        f"{API}/repos/{OWNER}/{REPO_NAME}/issues/{number}",
                        method="PATCH",
                        json={"state": "closed"},
                    )
                changed = True
                created.append(number)

    if changed:
        save_tasks(data)


def main():
    if not (OWNER and REPO_NAME and TOKEN):
        raise SystemExit("Missing OWNER/REPO or GITHUB_TOKEN in environment")
    created: List[int] = []
    # Collect mapping during sync by peeking tasks.json after task sync
    # First roadmap to build id->issue mapping via side effects
    # Modify functions to store globals? Simpler: re-derive by label markers after sync.
    sync_roadmap_nodes(created)
    sync_tasks(created)
    # Deduplicate and write
    nums = sorted(set(created))
    CREATED_FILE.write_text("\n".join(str(n) for n in nums) + ("\n" if nums else ""), encoding="utf-8")

    # Build links map: roadmap id -> issue URL, task id -> issue URL
    links = {"roadmap": {}, "tasks": {}}
    try:
        road = list_issues_by_label("roadmap")
        for iss in road:
            body = iss.get("body") or ""
            m = re.search(r"<!--ROADMAP_ID:([^>]+)-->", body)
            if m:
                rid = m.group(1).strip()
                links["roadmap"][rid] = iss.get("html_url")
    except Exception:
        pass
    try:
        task_issues = list_issues_by_label("task")
        for iss in task_issues:
            body = iss.get("body") or ""
            m = re.search(r"<!--TASK_ID:([^>]+)-->", body)
            if m:
                tid = m.group(1).strip()
                links["tasks"][tid] = iss.get("html_url")
    except Exception:
        pass
    (Path("project") / "links.json").write_text(json.dumps(links, indent=2), encoding="utf-8")

    print(f"Synced issues: {', '.join(map(str, nums)) if nums else '(none)'}")


if __name__ == "__main__":
    main()
