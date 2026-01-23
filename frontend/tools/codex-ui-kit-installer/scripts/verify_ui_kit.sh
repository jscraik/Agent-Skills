#!/usr/bin/env bash
set -euo pipefail

say() { printf '%s\n' "$*"; }

REPO="${1:-.}"
REPO="$(cd "$REPO" && pwd)"
BIN="$REPO/bin"
PROMPTS_DIR="${HOME}/.codex/prompts"
STATUS=0

check_exist() {
  local label="$1" path="$2"
  if [[ -e "$path" ]]; then
    say "OK: $label -> $path"
  else
    say "MISSING: $label -> $path"
    STATUS=1
  fi
}

check_exec() {
  local label="$1" path="$2"
  if [[ -x "$path" ]]; then
    say "OK: $label executable"
  else
    say "NOT EXECUTABLE: $label ($path)"
    STATUS=1
  fi
}

say "Verifying codex-ui-kit installation in: $REPO"

check_exist "AGENTS.md" "$REPO/AGENTS.md"
check_exist "schema" "$REPO/codex/ui_report.schema.json"
check_exist "ui-codex" "$BIN/ui-codex"
check_exec "ui-codex" "$BIN/ui-codex"

say "If prompts installed, they should be in $PROMPTS_DIR (ui_regression_check.md, draftpr.md)."

exit $STATUS
