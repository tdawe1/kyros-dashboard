#!/usr/bin/env bash
set -euo pipefail

# task-kickoff.sh <TASK_ID>
# Prints Planner/Implementer/Critic kickoff prompts and writes KICKOFF.md

if [[ ${1:-} == "-h" || ${1:-} == "--help" || $# -ne 1 ]]; then
  echo "Usage: scripts/task-kickoff.sh <TASK_ID>" >&2
  exit 1
fi

TASK_ID="$1"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
TASK_DIR="$REPO_ROOT/collaboration/tasks/$TASK_ID"
RULE_FILE="$REPO_ROOT/.cursor/rules/tasks/${TASK_ID}.mdc"

if [[ ! -d "$TASK_DIR" ]]; then
  echo "Error: Task directory not found: $TASK_DIR" >&2
  exit 1
fi

TITLE=$(sed -n '1p' "$TASK_DIR/BRIEF.md" 2>/dev/null | sed -E 's/^#\s*[^:]+:\s*//')
LANE=$(sed -n '2p' "$TASK_DIR/BRIEF.md" 2>/dev/null | sed -E 's/^Lane:\s*//')
ACCEPTANCE=$(sed -n '2,$p' "$TASK_DIR/ACCEPTANCE.md" 2>/dev/null | sed 's/^/- /')

CHANGESCOPE_GLOBS=""
if [[ -f "$RULE_FILE" ]]; then
  CHANGESCOPE_GLOBS=$(awk '/^globs:/ {flag=1; next} /^---$/ {flag=0} flag && /- / {print $0}' "$RULE_FILE" | sed 's/^/  /')
else
  CHANGESCOPE_GLOBS="  - \"collaboration/tasks/${TASK_ID}/**\""
fi

BRANCH_SLUG=$(echo "$TITLE" | tr 'A-Z' 'a-z' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g' | cut -c1-40)
BRANCH="feat/${TASK_ID}-${BRANCH_SLUG}"

PLANNER_PROMPT=$(printf "%s\n%s\n%s\n%s\n%s\n" \
  "Context Reset: New subtask" \
  "Task: ${TASK_ID} — ${TITLE}" \
  "Role: Planner" \
  "DoD: tests updated/passing; static checks clean; docs updated; critic review" \
  "Acceptance:\n${ACCEPTANCE}\nConstraints: keep scope minimal; align with changescope; branch ${BRANCH}\nPlan: propose 3–5 small subtasks with DoD and dependencies\nOutput: brief plan with subtasks, risks, and next action")

IMPLEMENTER_PROMPT=$(printf "%s\n%s\n%s\n%s\n%s\n" \
  "Context Reset: Start ${TASK_ID}" \
  "Role: Implementer (lane: ${LANE})" \
  "Branch: ${BRANCH}" \
  "Acceptance:\n${ACCEPTANCE}" \
  "Changescope globs:\n${CHANGESCOPE_GLOBS}\nConstraints: small diff; tests updated; no secrets; follow agents.md\nOutput: code changes only; summary and validation steps")

CRITIC_PROMPT=$(printf "%s\n%s\n%s\n%s\n" \
  "Context Reset: Review ${TASK_ID}" \
  "Role: Critic" \
  "Acceptance:\n${ACCEPTANCE}" \
  "Checks: tests pass; lint/format; DoD met; minimal diff; scope adherence\nOutput: approve or list concrete change requests with rationale")

OUT_FILE="$TASK_DIR/KICKOFF.md"
{
  echo "# ${TASK_ID}: ${TITLE} — Kickoff Prompts"
  echo
  echo "## Planner"
  echo "$PLANNER_PROMPT"
  echo
  echo "## Implementer"
  echo "$IMPLEMENTER_PROMPT"
  echo
  echo "## Critic"
  echo "$CRITIC_PROMPT"
} > "$OUT_FILE"

echo "Generated prompts written to $OUT_FILE" >&2
echo
echo "--- Planner ---"; echo "$PLANNER_PROMPT"; echo
echo "--- Implementer ---"; echo "$IMPLEMENTER_PROMPT"; echo
echo "--- Critic ---"; echo "$CRITIC_PROMPT"

