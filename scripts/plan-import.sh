#!/usr/bin/env bash
set -euo pipefail

# ---- config (override via env or flags) ----
REPO_DEFAULT="${REPO_DEFAULT:-tdawe1/kyros-dashboard}"
WORKFLOW_REF="${WORKFLOW_REF:-develop}"          # the ref the workflow should act on
WORKFLOW_ID_OR_PATH="${WORKFLOW_ID_OR_PATH:-.github/workflows/plan-import.yml}"
FOLDER_ID="${FOLDER_ID:-}"                        # REQUIRED: your Drive "Plans Inbox" folder ID
OUT_PATH="${OUT_PATH:-collaboration/PlanSpec.yml}"
OPEN_PR="${OPEN_PR:-1}"                           # set to 1 to auto-open the PR in browser

usage() {
  cat <<USAGE
Usage: $(basename "$0") -f <FOLDER_ID> [-r <owner/repo>] [-b <ref>] [-w <workflow>] [-o <out_path>] [--open]
  -f  Google Drive folder ID (required)
  -r  GitHub owner/repo         (default: $REPO_DEFAULT)
  -b  Ref/branch to run against (default: $WORKFLOW_REF)
  -w  Workflow id/path/name     (default: $WORKFLOW_ID_OR_PATH)
  -o  Repo path for PlanSpec    (default: $OUT_PATH)
      --open  Open the resulting PR in your browser
Examples:
  $(basename "$0") -f 1gQp9wFvxI2tjv8D_fFzrEADrbupzqd8L
  REPO_DEFAULT=you/repo $(basename "$0") -f <FOLDER_ID> -b develop
USAGE
}

# ---- parse flags ----
while [[ $# -gt 0 ]]; do
  case "$1" in
    -f) FOLDER_ID="$2"; shift 2 ;;
    -r) REPO_DEFAULT="$2"; shift 2 ;;
    -b) WORKFLOW_REF="$2"; shift 2 ;;
    -w) WORKFLOW_ID_OR_PATH="$2"; shift 2 ;;
    -o) OUT_PATH="$2"; shift 2 ;;
    --open) OPEN_PR=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 1 ;;
  esac
done

if [[ -z "${FOLDER_ID}" ]]; then
  echo "❌ Missing -f <FOLDER_ID>"; usage; exit 1
fi

# ---- deps ----
command -v gh >/dev/null || { echo "❌ gh (GitHub CLI) is required"; exit 1; }
command -v jq >/dev/null || { echo "❌ jq is required"; exit 1; }

# ---- auth + repo sanity ----
if ! gh auth status -h github.com >/dev/null 2>&1; then
  echo "🔐 Logging into GitHub…"
  gh auth login -h github.com -s repo --web
fi

REPO="$REPO_DEFAULT"
echo "📦 Repo: $REPO"
echo "🌿 Ref:  $WORKFLOW_REF"
echo "🧩 Workflow: $WORKFLOW_ID_OR_PATH"
echo "📁 Drive folder: $FOLDER_ID"
echo "📝 Out path: $OUT_PATH"
echo

# ---- resolve workflow identifier robustly ----
# Accepts: numeric ID, file path, or display name
WF_RESOLVED="$WORKFLOW_ID_OR_PATH"
if [[ ! "$WF_RESOLVED" =~ ^[0-9]+$ ]]; then
  # try by path-name first
  if gh workflow view "$WF_RESOLVED" -R "$REPO" >/dev/null 2>&1; then
    :
  else
    # try to match by display name
    WF_JSON="$(gh workflow list -R "$REPO" --limit 200 --json id,name,path)"
    WF_RESOLVED="$(echo "$WF_JSON" | jq -r --arg n "$WORKFLOW_ID_OR_PATH" '
      .[] | select(.name==$n or .path==$n) | .id' | head -n1)"
    if [[ -z "$WF_RESOLVED" ]]; then
      echo "❌ Could not resolve workflow '$WORKFLOW_ID_OR_PATH' on $REPO"
      echo "   Available workflows:"; echo "$WF_JSON" | jq -r '.[] | "\(.id)\t\(.name)\t\(.path)"'
      exit 1
    fi
  fi
fi

# ---- dispatch ----
echo "🚀 Dispatching workflow…"
RUN_URL_JSON="$(gh workflow run "$WF_RESOLVED" -R "$REPO" --ref "$WORKFLOW_REF" \
  -f folder_id="$FOLDER_ID" -f out_path="$OUT_PATH" 2>/dev/null || true)"

# gh doesn't return a run id here; poll for the most recent manual run of this workflow on this ref
echo "⏳ Waiting for run to appear…"
SLEEP=2
for i in {1..15}; do
  RUN="$(gh run list -R "$REPO" --workflow "$WF_RESOLVED" --branch "$WORKFLOW_REF" --event workflow_dispatch \
    --json databaseId,status,conclusion,htmlUrl,headBranch,displayTitle,createdAt,workflowName -q '.[0]' 2>/dev/null || true)"
  if [[ -n "$RUN" && "$RUN" != "null" ]]; then break; fi
  sleep "$SLEEP"
done

if [[ -z "$RUN" || "$RUN" == "null" ]]; then
  echo "❌ Could not find a dispatched run. Check permissions or workflow triggers."
  exit 1
fi

RUN_ID="$(echo "$RUN" | jq -r '.databaseId')"
RUN_URL="$(echo "$RUN" | jq -r '.htmlUrl')"
echo "🔗 Run: $RUN_URL (id: $RUN_ID)"

# ---- watch until completion ----
echo "👀 Streaming logs… (press Ctrl+C to stop watching; the script will still check result)"
set +e
gh run watch "$RUN_ID" -R "$REPO" --exit-status
WATCH_RC=$?
set -e

# fetch final status
FINAL="$(gh run view "$RUN_ID" -R "$REPO" --json conclusion,status,htmlUrl,headSha,headBranch,workflow -q '.')"
CONC="$(echo "$FINAL" | jq -r '.conclusion')"
STATUS="$(echo "$FINAL" | jq -r '.status')"
echo "📊 Status: $STATUS  Conclusion: $CONC"

# ---- try to locate the PR created by the workflow ----
echo "🔎 Locating created PR…"
PR_JSON="$(gh pr list -R "$REPO" --state open --search 'in:title \"Plan: Import latest PlanSpec from Drive\"' \
  --json number,url,headRefName,author,createdAt -q '.[]' 2>/dev/null || true)"

if [[ -z "$PR_JSON" ]]; then
  # Fallback: list recent PRs opened by actions bot with 'plan/import-' head
  PR_JSON="$(gh pr list -R "$REPO" --state open --author github-actions[bot] \
    --json number,url,headRefName,createdAt -q '[.[] | select(.headRefName|startswith("plan/import-"))][0]' 2>/dev/null || true)"
fi

if [[ -n "$PR_JSON" && "$PR_JSON" != "null" ]]; then
  PR_URL="$(echo "$PR_JSON" | jq -r '.url')"
  PR_NUM="$(echo "$PR_JSON" | jq -r '.number')"
  echo "✅ PR created: #$PR_NUM → $PR_URL"
  if [[ "$OPEN_PR" == "1" ]]; then
    gh pr view "$PR_NUM" -R "$REPO" --web >/dev/null 2>&1 || true
  fi
else
  echo "⚠️  Workflow finished, but I couldn't find the PR automatically."
  echo "    Check the workflow logs for the 'create-pull-request' step."
fi

# exit non-zero if the run failed
if [[ "$CONC" != "success" ]]; then
  echo "❌ Workflow concluded: $CONC"
  exit 1
fi

echo "🎉 Done."
