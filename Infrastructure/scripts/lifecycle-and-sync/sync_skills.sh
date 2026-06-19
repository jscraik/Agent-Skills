#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [[ -x "$SCRIPT_DIR/sync_skills_impl.sh" ]]; then
  exec bash "$SCRIPT_DIR/sync_skills_impl.sh" "$@"
fi

if [[ -x "$SCRIPT_DIR/sync-skills.py" ]]; then
  exec "$SCRIPT_DIR/sync-skills.py" "$@"
fi

echo "sync_skills implementation is not available" >&2
exit 1
