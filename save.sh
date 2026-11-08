#!/bin/sh
# Save a live.json made by espn_live.py into the NBA Plays board's live/stats document, using Claude Code
# signed in as Dylan (CLAUDE_CODE_OAUTH_TOKEN in GitHub). BOARD_URL is the board's claude.ai link.
# Usage: BOARD_URL=https://claude.ai/artifact/... ./save.sh live.json
set -e
[ -f "$1" ] || { echo "No $1, nothing to save"; exit 0; }
[ -n "$BOARD_URL" ] || { echo "BOARD_URL is not set"; exit 1; }
FILE="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
CLAUDE="${CLAUDE_BIN:-claude}"
"$CLAUDE" -p "Load the ArtifactData tool if it is deferred. Artifact url: $BOARD_URL
Step 1: ArtifactData action \"get\", collection \"live\", doc_id \"stats\", out_dir \"$(dirname "$FILE")/current\" (only to learn its version and two fields; do not print its contents).
Step 2: Check only two fields with Bash, without reading the whole file: grep -m3 -E '\"(cleared|at|checkedAt)\"' on the saved stats.json. If that document exists, has \"cleared\" equal to true, and its \"at\" time is within the last 18 hours, someone removed results on purpose: stop and reply only SKIPPED-CLEARED.
Step 3: Otherwise ArtifactData action \"update\", collection \"live\", doc_id \"stats\", file_path \"$FILE\", with if_version set to the version from step 1 (omit if_version only if the document did not exist). If it reports a version mismatch, repeat steps 1 to 3 once.
Do nothing else. Reply with only OK, SKIPPED-CLEARED, or the exact error text." \
  --model claude-haiku-5-5 --permission-mode bypassPermissions
