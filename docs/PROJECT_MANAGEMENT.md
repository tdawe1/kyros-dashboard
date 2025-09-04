# Project Management

This repo includes a comprehensive, file-based collaboration system under `collaboration/` that provides project sync/mapping, issues intake, CLI tools, and Discord webhooks for staying on track without external tools.

## Core Components

- `collaboration/state/tasks.json`: single source of truth for tasks
- `collaboration/state/locks.json`: lease-based locking system
- `collaboration/state/agents.json`: agent registry and status
- `collaboration/events/events.jsonl`: append-only event log
- `scripts/collab_cli.py`: comprehensive CLI to manage tasks, leases, and events
- `scripts/generate_tasks_board.py`: generates a Now/Next/Review/Done board
- `scripts/task-kickoff.sh`: scaffolds Planner/Implementer/Critic prompts for a task
- `project/roadmap.yml`: hierarchical roadmap with status tracking
- `project/project_mapping.json`: GitHub Project field mapping configuration

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

## Project Sync & Mapping

### GitHub Issues Intake
The `.github/ISSUE_TEMPLATE` folder includes forms for Task, Bug, and Feature. New issues can be automatically mirrored into `tasks.json` using the `create-task` command (copy title/description/labels). You can link back the GitHub issue using the `external_ids` later if desired.

### Roadmap Field Integration
Issues can be linked to roadmap items using the `--roadmap-id` parameter:
```bash
python scripts/collab_cli.py create-task \
  --title "Backend: /healthz" \
  --description "Expose /healthz with DB and cache checks" \
  --labels backend,ci \
  --priority P1 \
  --roadmap-id R2.1.1
```

### GitHub Project Synchronization
The system automatically syncs tasks and roadmap items to GitHub Projects via `.github/workflows/sync_github_project.yml`:

- **Status Mapping**: Maps task statuses to GitHub Project status fields
- **Priority Mapping**: Maps task priorities to GitHub Project priority fields  
- **Field Configuration**: Customize field names via `project/project_mapping.json`
- **Auto-linking**: Generates `project/links.json` for dashboard autolinking

### Project Mapping Configuration
Edit `project/project_mapping.json` to customize GitHub Project field mappings:

```json
{
  "fields": {
    "status": "Status",
    "priority": "Priority"
  },
  "status": {
    "queued": ["Queued", "Backlog"],
    "in_progress": ["In Progress", "Active"],
    "review": ["Review", "In Review"],
    "done": ["Done", "Completed"]
  },
  "priority": {
    "P1": ["P1", "High", "Critical"],
    "P2": ["P2", "Medium", "Normal"],
    "P3": ["P3", "Low"]
  }
}
```

## CLI Basics

### Task Management
```bash
# Create a new task
python scripts/collab_cli.py create-task \
  --title "Add healthcheck endpoint" \
  --description "Expose /healthz with DB and cache checks" \
  --labels backend,ci \
  --priority P2 \
  --assignee thomas \
  --roadmap-id R2.1.1

# List tasks with filters
python scripts/collab_cli.py list-tasks --status in_progress
python scripts/collab_cli.py list-tasks --assignee thomas
python scripts/collab_cli.py list-tasks --output json | jq '.tasks | length'

# Transition task status
python scripts/collab_cli.py transition-task task-008 in_progress
python scripts/collab_cli.py transition-task task-008 review
python scripts/collab_cli.py transition-task task-008 done

# Link external IDs (GitHub issues, Linear tickets, etc.)
python scripts/collab_cli.py link-external task-008 github 123
python scripts/collab_cli.py link-external task-008 linear LIN-456
```

### Roadmap Management
```bash
# Render roadmap to markdown
python scripts/roadmap_tree.py project/roadmap.yml ROADMAP.md

# Update roadmap status
python scripts/roadmap_cli.py set-status R2 in_progress

# Add new roadmap items
python scripts/roadmap_cli.py add R2.3 "Payments MVP" --parent R2 --status queued --owner thomas

# Link roadmap items to tasks
python scripts/roadmap_cli.py link-task R2.1.1 task-010
python scripts/roadmap_cli.py sync-from-task R2.1.1
```

### Board Generation
```bash
# Generate Now/Next/Review/Done board
python scripts/generate_tasks_board.py
cat collaboration/board.md
```

### Event Management
```bash
# View recent events
python scripts/collab_cli.py list-events --limit 10

# Generate human-readable log
python scripts/collab_cli.py generate-log
```

## Tips

- Keep tasks small (≤ 60–90 minutes of work) and move fast through statuses.
- Prefer `transition-task` over editing JSON by hand to keep events consistent.
- Regenerate the board after notable changes and skim it daily.
- Use roadmap CLI to maintain hierarchical project structure.
- Link external IDs for better traceability across tools.

## Discord Webhooks

### Configuration
Set up Discord webhooks for automated notifications:

1. **General Channel**: `DISCORD_WEBHOOK_URL` - posts roadmap and board updates
2. **Project Management Channel**: `DISCORD_PM_WEBHOOK_URL` - dedicated PM channel notifications

### Setup Steps
1. Go to Discord Server Settings → Integrations → Webhooks
2. Create webhook and copy URL
3. Add as repository secret: Settings → Secrets and variables → Actions
4. Add both URLs for comprehensive coverage

### Notification Triggers
- **Roadmap Updates**: When `project/roadmap.yml` changes
- **Board Updates**: When tasks change status or new tasks are created
- **Dashboard Publishing**: When dashboard is published to GitHub Pages
- **Project Sync**: When tasks/roadmap sync to GitHub Projects

### Message Format
Discord posts include:
- Rich formatting with titles and descriptions
- Direct links to GitHub issues, PRs, and projects
- Dashboard links for easy access
- Repository context and ownership info

## GitHub Integration (Issues + Projects)

### Automatic Synchronization
- **Sync Workflow**: `.github/workflows/sync_github_project.yml` mirrors roadmap nodes and tasks into Issues and GitHub Projects
- **Field Mapping**: Updates Project "Status" and "Priority" fields automatically
- **Auto-linking**: Generates `project/links.json` for dashboard autolinking

### Configuration
Set up once in repository settings:
- `PROJECT_URL`: GitHub Project URL (e.g., `https://github.com/orgs/<org>/projects/<number>`)
- `DISCORD_WEBHOOK_URL`: General Discord notifications
- `DISCORD_PM_WEBHOOK_URL`: Project management channel notifications

### Field Mapping Customization
Edit `project/project_mapping.json` to match your GitHub Project fields:
- Change `fields.status` or `fields.priority` to match your Project field names exactly
- Adjust arrays under `status` and `priority` to include your option names (case-insensitive)
- The workflow uses this mapping first, then falls back to sensible defaults

## Online Dashboard

- GitHub Pages workflow (`publish_dashboard.yml`) publishes `site/` fetching `ROADMAP.md` and `collaboration/board.md`.
- Enable Pages: Settings → Pages → Source “GitHub Actions”.
- The Roadmap includes a "Goals" section for overarching direction; agents and automations do not act on it.
- See `docs/DASHBOARD.md` for autolinking and config details.

## Quick Start

### 1. Initial Setup
```bash
# Clone and navigate to repository
git clone <repo-url>
cd kyros-dashboard

# Install Python dependencies
pip install -r requirements.txt

# Verify CLI is working
python scripts/collab_cli.py --help
```

### 2. Create Your First Task
```bash
# Create a task linked to roadmap
python scripts/collab_cli.py create-task \
  --title "Backend: /healthz" \
  --description "Expose /healthz with DB and cache checks" \
  --labels backend,ci \
  --priority P1 \
  --roadmap-id R2.1.1 \
  --assignee thomas
```

### 3. Work Through Task Lifecycle
```bash
# Move to in progress
python scripts/collab_cli.py transition-task task-009 in_progress

# Move to review when ready
python scripts/collab_cli.py transition-task task-009 review

# Mark as done when complete
python scripts/collab_cli.py transition-task task-009 done
```

### 4. Generate Project Views
```bash
# Generate the Now/Next board
python scripts/generate_tasks_board.py
cat collaboration/board.md

# Render the roadmap
python scripts/roadmap_tree.py project/roadmap.yml ROADMAP.md
```

### 5. Sync with External Tools
```bash
# Sync to GitHub Issues/Project (requires PROJECT_URL secret)
# Run "Sync Roadmap/Tasks to GitHub Issues + Project" workflow in Actions

# Publish dashboard (posts to Discord if webhooks configured)
# Run "Publish Project Dashboard (Pages)" workflow in Actions
```

### 6. Daily Workflow
```bash
# Check current board
python scripts/generate_tasks_board.py && cat collaboration/board.md

# List your tasks
python scripts/collab_cli.py list-tasks --assignee thomas

# Update roadmap status
python scripts/roadmap_cli.py set-status R2.1 in_progress
```

## Security Configuration

### JWT Secret Key
- **Development**: JWT_SECRET_KEY is automatically generated with 32+ characters if not provided
- **Non-Development**: Should set JWT_SECRET_KEY environment variable (minimum 32 characters) for stability
- **Validation**: The system enforces ≥32 character requirement and generates secure fallback if needed
- **Recommendation**: Always set JWT_SECRET_KEY in non-development environments for stability and security

## CodeRabbit Import

- Workflow `import_coderabbit_on_pr.yml` imports PR review feedback into small tasks automatically when reviews/comments are submitted.
