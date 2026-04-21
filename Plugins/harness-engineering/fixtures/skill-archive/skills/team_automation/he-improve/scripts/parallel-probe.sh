#!/bin/bash

# Parallel-readiness probe for he-improve.
#
# Usage: parallel-probe.sh <project_directory> [measurement_command] [measurement_workdir] [shared_file ...]

set -euo pipefail

PROJECT_DIR="${1:?Error: project_directory argument required}"
MEASUREMENT_CMD="${2:-}"
MEASUREMENT_WORKDIR="${3:-.}"

shift 3 2>/dev/null || shift $# 2>/dev/null || true
SHARED_FILES=()
if [[ $# -gt 0 ]]; then
  SHARED_FILES=("$@")
fi

cd "$PROJECT_DIR" || {
  echo '{"mode":"serial","blockers":[{"type":"error","description":"Cannot access project directory","suggestion":"Check path"}]}'
  exit 0
}

if ! command -v python3 >/dev/null 2>&1; then
  echo '{"mode":"serial","blockers":[{"type":"missing_dependency","description":"python3 is required for structured probe output","suggestion":"Install python3 or run serially"}],"blocker_count":1}'
  exit 0
fi

BLOCKERS="[]"
SCAN_PATHS=()

add_blocker() {
  local type="$1"
  local desc="$2"
  local suggestion="$3"
  BLOCKERS=$(echo "$BLOCKERS" | python3 -c "
import json, sys
b = json.load(sys.stdin)
b.append({'type': '$type', 'description': '''$desc''', 'suggestion': '''$suggestion'''})
print(json.dumps(b))
" 2>/dev/null || echo "$BLOCKERS")
}

add_scan_path() {
  local candidate="$1"
  if [[ -n "$candidate" && -e "$candidate" ]]; then
    SCAN_PATHS+=("$candidate")
  fi
}

add_scan_path "$MEASUREMENT_WORKDIR"
if [[ ${#SHARED_FILES[@]} -gt 0 ]]; then
  for shared_file in "${SHARED_FILES[@]}"; do
    add_scan_path "$shared_file"
  done
fi
if [[ ${#SCAN_PATHS[@]} -eq 0 ]]; then
  SCAN_PATHS=(".")
fi

if [[ -n "$MEASUREMENT_CMD" ]] && echo "$MEASUREMENT_CMD" | grep -qE '(--port(?:\s+|=)[0-9]+|PORT=[0-9]+|localhost:[0-9]+)'; then
  add_blocker "port" "Measurement command contains a hardcoded port reference." "Parameterize port via environment variable."
fi

SQLITE_FILES=$(find "${SCAN_PATHS[@]}" -maxdepth 4 -type f \( -name '*.db' -o -name '*.sqlite' -o -name '*.sqlite3' \) ! -path '*/.git/*' ! -path '*/node_modules/*' ! -path '*/.context/*' ! -path '*/.worktrees/*' 2>/dev/null | head -10 || true)
if [[ -n "$SQLITE_FILES" ]]; then
  FILE_COUNT=$(echo "$SQLITE_FILES" | wc -l | tr -d ' ')
  add_blocker "shared_file" "Found $FILE_COUNT SQLite file(s) in probe scope." "Copy DB files into each experiment worktree."
fi

LOCK_FILES=$(find "${SCAN_PATHS[@]}" -maxdepth 4 -type f \( -name '*.lock' -o -name '*.pid' \) ! -path '*/.git/*' ! -path '*/node_modules/*' ! -path '*/.context/*' ! -path '*/.worktrees/*' ! -name 'package-lock.json' ! -name 'yarn.lock' ! -name 'bun.lock' ! -name 'bun.lockb' ! -name 'Gemfile.lock' ! -name 'poetry.lock' ! -name 'Cargo.lock' 2>/dev/null | head -10 || true)
if [[ -n "$LOCK_FILES" ]]; then
  FILE_COUNT=$(echo "$LOCK_FILES" | wc -l | tr -d ' ')
  add_blocker "lock_file" "Found $FILE_COUNT lock/PID file(s) that may cause contention." "Clean lock files or run serial mode."
fi

if [[ -n "$MEASUREMENT_CMD" ]] && echo "$MEASUREMENT_CMD" | grep -qiE '(cuda|gpu|tensorflow|torch|nvidia-smi|CUDA_VISIBLE_DEVICES)'; then
  add_blocker "exclusive_resource" "Measurement command appears to use exclusive accelerator resources." "Prefer serial mode or explicit device partitioning."
fi

BLOCKER_COUNT=$(echo "$BLOCKERS" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

if [[ "$BLOCKER_COUNT" == "0" ]]; then
  MODE="parallel"
elif echo "$BLOCKERS" | python3 -c "import json,sys; b=json.load(sys.stdin); exit(0 if any(x['type']=='exclusive_resource' for x in b) else 1)" 2>/dev/null; then
  MODE="serial"
else
  MODE="user-decision"
fi

python3 -c "
import json
print(json.dumps({
  'mode': '$MODE',
  'blockers': $BLOCKERS,
  'blocker_count': $BLOCKER_COUNT
}, indent=2))
"
