#!/usr/bin/env bash
set -euo pipefail

# run-plan-pipeline.sh
# Orchestrates plan import (from Drive via GH Actions or from a local file)
# then runs the task splitter.

usage() {
  cat <<'USAGE'
Usage:
  scripts/run-plan-pipeline.sh --file collaboration/plans/inbox/planspec.yml [--no-split]
  scripts/run-plan-pipeline.sh --drive [--ref develop] [--no-split]

Options:
  --file <path>   Use a local PlanSpec file (skips Drive import)
  --drive         Trigger GitHub workflow "Import Latest Plan from Drive" via gh
  --ref <branch>  Branch/ref for workflow dispatch (default: develop)
  --no-split      Do not run the Python splitter (just import the plan)

Examples:
  scripts/run-plan-pipeline.sh --file collaboration/plans/inbox/planspec.yml
  scripts/run-plan-pipeline.sh --drive --ref develop
USAGE
}

PLAN_FILE=""
MODE=""
REF="develop"
RUN_SPLIT=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file) PLAN_FILE="$2"; MODE="file"; shift 2 ;;
    --drive) MODE="drive"; shift ;;
    --ref) REF="$2"; shift 2 ;;
    --no-split) RUN_SPLIT=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 1 ;;
  esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"

if [[ "$MODE" == "file" ]]; then
  if [[ -z "$PLAN_FILE" || ! -f "$PLAN_FILE" ]]; then
    echo "Error: Plan file not found: $PLAN_FILE" >&2
    exit 1
  fi
  echo "Using local plan: $PLAN_FILE"
elif [[ "$MODE" == "drive" ]]; then
  if ! command -v gh >/dev/null 2>&1; then
    echo "Error: GitHub CLI (gh) is required for --drive mode." >&2
    exit 1
  fi
  echo "Dispatching workflow: Import Latest Plan from Drive (ref: $REF)"
  gh workflow run "Import Latest Plan from Drive" --ref "$REF"
  echo "Waiting for workflow run to start..."
  sleep 5
  echo "Watching latest run..."
  gh run watch --exit-status || {
    echo "Workflow failed. Check GitHub Actions logs." >&2
    exit 1
  }
  # Assume workflow placed the plan at collaboration/plans/inbox/planspec.yml
  PLAN_FILE="$REPO_ROOT/collaboration/plans/inbox/planspec.yml"
  if [[ ! -f "$PLAN_FILE" ]]; then
    echo "Error: expected plan at $PLAN_FILE after workflow completed" >&2
    exit 1
  fi
else
  echo "Error: choose one of --file or --drive" >&2
  usage
  exit 1
fi

if [[ "$RUN_SPLIT" -eq 1 ]]; then
  echo "Running splitter on: $PLAN_FILE"
  python3 "$REPO_ROOT/scripts/split_plan.py" "$PLAN_FILE"
  echo "Split complete. See collaboration/tasks and .cursor/rules/tasks."
else
  echo "Skipping split as requested."
fi
