#!/usr/bin/env python3
import sys
import pathlib
import yaml
import textwrap
import re

if len(sys.argv) < 2:
    print("Usage: split_plan.py <plan.yml>")
    sys.exit(1)

p = pathlib.Path(sys.argv[1])
plan = yaml.safe_load(p.read_text())
pathlib.Path("tasks").mkdir(exist_ok=True)

for t in plan.get("tasks", []):
    tid, title, lane = t["id"], t["title"], t.get("lane", "frontend")
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40]
    task_dir = pathlib.Path("tasks") / tid
    task_dir.mkdir(parents=True, exist_ok=True)

    acceptance = t.get("acceptance", [])
    (task_dir / "ACCEPTANCE.md").write_text(
        "# Acceptance\n" + "\n".join(f"- {a}" for a in acceptance) + "\n"
    )

    (task_dir / "BRIEF.md").write_text(
        textwrap.dedent(f"""\
        # {tid}: {title}
        Lane: {lane}
        Plan: {plan.get("plan_id", "")}
        Baseline: {plan.get("baseline_branch", "develop")}

        ## Scope
        Implement only what is necessary to satisfy ACCEPTANCE.md.

        ## Deliverables
        - Code + tests
        - PR titled "[{tid}] {title}"
        - PR body includes how you validated acceptance

        ## Blockers
        (Write here if blocked; 1–2 lines)
        """)
    )

    (task_dir / ".cursor.rules.md").write_text(
        textwrap.dedent(f"""\
        You are the Implementer for {tid}: "{title}" in lane {lane}.
        Work ONLY on files required for this task. Do NOT edit collaboration/**.
        Create and use branch: feat/{tid}-{slug}
        Keep changes under 300 lines if possible.
        Update/add tests to satisfy tasks/{tid}/ACCEPTANCE.md.
        When done: open a PR titled "[{tid}] {title}" and include validation steps.
        If blocked, write a single line under "## Blockers" in tasks/{tid}/BRIEF.md.
        """)
    )

print("Generated task folders for:", ", ".join(t["id"] for t in plan.get("tasks", [])))
