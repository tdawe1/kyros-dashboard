# Project Management

This repo already includes a simple, file-based collaboration system under `collaboration/` you can use to stay on track without external tools.

Key pieces:
- `collaboration/state/tasks.json`: single source of truth for tasks.
- `scripts/collab_cli.py`: helper CLI to manage tasks and leases.
- `scripts/generate_tasks_board.py`: generates a Now/Next/Review/Done board.
- `scripts/task-kickoff.sh`: scaffolds Planner/Implementer/Critic prompts for a task.

## Workflow

1) Create a task

```
python scripts/collab_cli.py create-task \
  --title "Add healthcheck endpoint" \
  --description "Expose /healthz with DB and cache checks" \
  --labels backend,ci \
  --priority P2 \
  --assignee thomas
```

2) Move it through statuses

```
python scripts/collab_cli.py transition-task task-008 in_progress
python scripts/collab_cli.py transition-task task-008 review
python scripts/collab_cli.py transition-task task-008 done
```

Allowed statuses: `queued → claimed → in_progress → review → approved → merging → done` with detours to `blocked`, `changes_requested`, or `failed`.

3) See current board

```
python scripts/generate_tasks_board.py
cat collaboration/board.md
```

4) List/filter tasks

```
python scripts/collab_cli.py list-tasks --status in_progress
python scripts/collab_cli.py list-tasks --assignee thomas
python scripts/collab_cli.py list-tasks --output json | jq '.tasks | length'
```

5) Kick off a task (optional prompts)

```
scripts/task-kickoff.sh task-008
```

## Intake via GitHub Issues

The `.github/ISSUE_TEMPLATE` folder includes forms for Task, Bug, and Feature. New issues can be mirrored into `tasks.json` using the `create-task` command (copy title/description/labels). You can link back the GitHub issue using the `external_ids` later if desired.

## Tips

- Keep tasks small (≤ 60–90 minutes of work) and move fast through statuses.
- Prefer `transition-task` over editing JSON by hand to keep events consistent.
- Regenerate the board after notable changes and skim it daily.
- Roadmap: keep an overall direction in `project/roadmap.yml`; render to `ROADMAP.md` with:
  - `python scripts/roadmap_tree.py project/roadmap.yml ROADMAP.md`
  - Update via CLI:
    - `python scripts/roadmap_cli.py set-status R2 in_progress`
    - `python scripts/roadmap_cli.py add R2.3 "Payments MVP" --parent R2 --status queued --owner thomas`
    - Link/sync with tasks: `python scripts/roadmap_cli.py link-task R2.1.1 task-010 && python scripts/roadmap_cli.py sync-from-task R2.1.1`

## GitHub Integration (Issues + Projects)

- Sync to Issues/Project: `.github/workflows/sync_github_project.yml` mirrors roadmap nodes and tasks into Issues and (optionally) adds them to a GitHub Project.
- Configure once:
  - Settings → Secrets and variables → Actions → New repository secret:
    - `PROJECT_URL`: e.g. `https://github.com/orgs/<org>/projects/<number>`
  - Optional: `DISCORD_WEBHOOK_URL` to post roadmap/board updates.
- The sync also updates the Project “Status” single-select field if present (tries to match options like “Queued”, “In Progress”, “Review”, “Done”, “Blocked”).
- Customize field/option mapping via `project/project_mapping.json`:
  - Change `fields.status` or `fields.priority` to match your Project field names exactly.
  - Adjust arrays under `status` and `priority` to include your option names (case-insensitive).
  - The workflow will use this mapping first, then fall back to sensible defaults.

## Online Dashboard

- GitHub Pages workflow (`publish_dashboard.yml`) publishes `site/` fetching `ROADMAP.md` and `collaboration/board.md`.
- Enable Pages: Settings → Pages → Source “GitHub Actions”.
- The Roadmap includes a "Goals" section for overarching direction; agents and automations do not act on it.

## CodeRabbit Import

- Workflow `import_coderabbit_on_pr.yml` imports PR review feedback into small tasks automatically when reviews/comments are submitted.
