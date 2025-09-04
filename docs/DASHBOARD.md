# Project Dashboard

A lightweight static dashboard published via GitHub Pages that renders:
- `ROADMAP.md` (overall direction and progress)
- `collaboration/board.md` (Now/Next/Review/Done summary)

## Live Link
- The Pages workflow publishes on demand. After a run, the workflow prints the URL (e.g., `https://<owner>.github.io/<repo>/`).
- The header shows an “Open GitHub Project” button when `PROJECT_URL` is set as a repo secret.

## How It Works
- Build: `.github/workflows/publish_dashboard.yml` copies `site/` to Pages and includes:
  - `ROADMAP.md` (rendered from `project/roadmap.yml` via `scripts/roadmap_tree.py`)
  - `collaboration/board.md` (rendered via `scripts/generate_tasks_board.py`)
  - Optional `project/links.json` from the sync workflow to auto‑link IDs in the UI.
  - Optional `config.json` with `{\"project_url\": \"...\"}` to show the Project button.

## Updating Content
- Roadmap: edit `project/roadmap.yml`, then run the “Update Roadmap” workflow or `python scripts/roadmap_tree.py project/roadmap.yml ROADMAP.md`.
- Board: modify tasks and run the “Generate Project Board” workflow or `python scripts/generate_tasks_board.py`.
- Publish: run “Publish Project Dashboard (Pages)” in Actions.

## Autolinking Behavior
- The site fetches `links.json` and auto‑links:
  - Roadmap IDs like `R2.1` → corresponding GitHub Issue.
  - Task IDs like `task-010` → corresponding GitHub Issue.
  - Inline `GH#123` and `PR#123` → issue/PR URLs.

## Discord Notifications (Optional)
- Set `DISCORD_WEBHOOK_URL` (general) and/or `DISCORD_PM_WEBHOOK_URL` (project‑management channel).
- Roadmap/Board workflows will post rich messages with links; the publish workflow posts “Dashboard Published”.

## Troubleshooting
- Dashboard doesn’t update: rerun the publish workflow; confirm Actions succeeded.
- Missing Project button: ensure `PROJECT_URL` is set as a repo secret.
- Links not clickable: ensure the sync workflow has run at least once to generate `project/links.json`.
