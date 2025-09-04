#!/usr/bin/env python3
import sys, pathlib, yaml, textwrap, re

if len(sys.argv) < 2:
    print("Usage: split_plan.py <plan.yml>")
    sys.exit(1)

# Resolve paths relative to repo root (script is in scripts/)
repo_root = pathlib.Path(__file__).resolve().parent.parent
plan_path = pathlib.Path(sys.argv[1])
plan = yaml.safe_load(plan_path.read_text())

# Standardized output locations
tasks_root = repo_root / "collaboration" / "tasks"
cursor_rules_root = repo_root / ".cursor" / "rules" / "tasks"
tasks_root.mkdir(parents=True, exist_ok=True)
cursor_rules_root.mkdir(parents=True, exist_ok=True)

# Lane → globs mapping for Cursor rule scoping
LANE_GLOBS = {
    "frontend": ["frontend/**"],
    "backend": ["backend/**"],
    "docs": ["docs/**"],
    "ci": [".github/**", "scripts/**"],
}

generated = []

for t in plan.get("tasks", []):
    tid, title, lane = t["id"], t["title"], t.get("lane", "frontend")
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40]
    task_dir = tasks_root / tid
    task_dir.mkdir(parents=True, exist_ok=True)

    acceptance = t.get("acceptance", [])
    (task_dir / "ACCEPTANCE.md").write_text(
        "# Acceptance\n" + "\n".join(f"- {a}" for a in acceptance) + "\n"
    )

    (task_dir / "BRIEF.md").write_text(
        textwrap.dedent(
            f"""\
            # {tid}: {title}
            Lane: {lane}
            Plan: {plan.get('plan_id','')}
            Baseline: {plan.get('baseline_branch','develop')}

            ## Scope
            Implement only what is necessary to satisfy ACCEPTANCE.md.

            ## Deliverables
            - Code + tests
            - PR titled "[{tid}] {title}"
            - PR body includes how you validated acceptance

            ## Blockers
            (Write here if blocked; 1–2 lines)
            """
        )
    )

    # Task-local Cursor rules stub for reference in the task directory
    (task_dir / ".cursor.rules.md").write_text(
        textwrap.dedent(
            f"""\
            You are the Implementer for {tid}: "{title}" in lane {lane}.
            Work ONLY on files required for this task. Do NOT edit collaboration/**.
            Create and use branch: feat/{tid}-{slug}
            Keep changes under 300 lines if possible.
            Update/add tests to satisfy collaboration/tasks/{tid}/ACCEPTANCE.md.
            When done: open a PR titled "[{tid}] {title}" and include validation steps.
            If blocked, write a single line under "## Blockers" in collaboration/tasks/{tid}/BRIEF.md.
            """
        )
    )

    # Generate a Cursor rule that auto-applies when working on this task
    # Assemble globs: task folder + lane-specific + optional changescope from plan
    changescope = t.get("changescope", []) or []
    lane_globs = LANE_GLOBS.get(lane, ["frontend/**", "backend/**"])  # sensible defaults
    # De-duplicate while preserving order
    globs = [f"collaboration/tasks/{tid}/**"]
    for patt in lane_globs + list(changescope):
        if patt not in globs:
            globs.append(patt)

    cursor_rule = textwrap.dedent(
        """\
        ---
        description: Task {tid} — {title} (auto-applied)
        globs:
        {globs_yaml}
        ---

        Context Reset: New subtask
        Task: {tid} — {title}
        Lane: {lane}
        Branch: feat/{tid}-{slug}

        DoD:
        - Satisfy acceptance; tests updated/passing
        - Static checks clean; no secrets
        - PR reviewed by a critic

        Acceptance:
        {acceptance_md}

        Changescope:
        {changescope_md}

        Output: code changes only; summarize what changed and suggest next subtask.
        """
    ).format(
        tid=tid,
        title=title,
        lane=lane,
        slug=slug,
        globs_yaml="\n".join(f"  - \"{g}\"" for g in globs),
        acceptance_md="\n".join(f"- {a}" for a in (acceptance or ["(none specified)"])),
        changescope_md="\n".join(f"- {c}" for c in (changescope or globs[1:])),
    )

    (cursor_rules_root / f"{tid}.mdc").write_text(cursor_rule)

    generated.append(tid)

print("Generated task folders for:", ", ".join(generated))
