#!/usr/bin/env bash
set -euo pipefail

# push-plan-to-gdrive.sh <plan.yml> [remote:path]
# Pushes a PlanSpec YAML to Google Drive using rclone.
# Default remote:path is gdrive:/kyros/Plan Inbox

if [[ ${1:-} == "-h" || ${1:-} == "--help" || $# -lt 1 ]]; then
  echo "Usage: scripts/push-plan-to-gdrive.sh <plan.yml> [remote:path]" >&2
  exit 0
fi

SRC="$1"
DST="${2:-gdrive:/kyros/Plan Inbox}"

if [[ ! -f "$SRC" ]]; then
  echo "Error: plan file not found: $SRC" >&2
  exit 1
fi

if ! command -v rclone >/dev/null 2>&1; then
  echo "Error: rclone is not installed. See https://rclone.org/install/" >&2
  exit 1
fi

echo "Uploading $SRC → $DST ..."
rclone copy --progress "$SRC" "$DST"
echo "Done."

