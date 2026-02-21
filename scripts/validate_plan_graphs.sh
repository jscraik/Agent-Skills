#!/usr/bin/env bash
set -euo pipefail

CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
LINTER="${PLAN_GRAPH_LINTER:-$CODEX_HOME/scripts/plan-graph-lint.py}"

if [[ ! -f "$LINTER" ]]; then
  echo "[plan-graph] missing linter: $LINTER" >&2
  echo "[plan-graph] skipping (local codex tool not available in this environment)."
  exit 0
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

paths=(".agent/PLANS.md")
while IFS= read -r path; do
  paths+=("$path")
done < <(find docs/plans -maxdepth 1 -type f -name '*.md' | sort)

status=0
for path in "${paths[@]}"; do
  echo "[plan-graph] lint $path"
  if ! python3 "$LINTER" "$path"; then
    status=1
  fi
done

if [[ "$status" -ne 0 ]]; then
  echo "[plan-graph] one or more plan files failed lint" >&2
  exit "$status"
fi

echo "[plan-graph] all plan files passed"
