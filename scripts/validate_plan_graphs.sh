#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/validate_plan_graphs.sh

Runs plan graph lint against .agent/PLANS.md and docs/plans/*.md.
USAGE
}

if [[ $# -gt 0 ]]; then
  case "${1:-}" in
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
fi

CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
LINTER="${PLAN_GRAPH_LINTER:-$CODEX_HOME/scripts/plan-graph-lint.py}"

if [[ ! -f "$LINTER" ]]; then
  echo "[plan-graph] missing linter: $LINTER" >&2
  echo "[plan-graph] skipping (local codex tool not available in this environment)."
  exit 0
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

sanitize_plan_graph_output() {
  python3 - "$repo_root" "${HOME:-}" <<'PY'
import os
import pathlib
import re
import sys

repo_root = pathlib.Path(sys.argv[1]).resolve()
home_raw = sys.argv[2]
home = pathlib.Path(home_raw).resolve() if home_raw else None

for raw_line in sys.stdin:
    line = raw_line.rstrip("\n")
    repo_prefix = str(repo_root)
    line = line.replace(repo_prefix + os.sep, "")
    line = line.replace(repo_prefix, ".")
    if home is not None:
        line = line.replace(str(home), "~")
    line = re.sub(r"/Users/[^/]+", "/Users/<redacted>", line)
    line = re.sub(r"/home/[^/]+", "/home/<redacted>", line)
    print(line)
PY
}

paths=(".agent/PLANS.md")
while IFS= read -r path; do
  paths+=("$path")
done < <(find docs/plans -maxdepth 1 -type f -name '*.md' | sort)

status=0
failed_plans=()
for path in "${paths[@]}"; do
  echo "[plan-graph] lint $path"
  if ! python3 "$LINTER" "$path" 2>&1 | sanitize_plan_graph_output; then
    status=1
    failed_plans+=("$path")
  fi
done

if [[ "$status" -ne 0 ]]; then
  echo "" >&2
  echo "[plan-graph] ⚠️  ${#failed_plans[@]} plan file(s) need task graphs:" >&2
  for fp in "${failed_plans[@]}"; do
    echo "  - $fp" >&2
  done
  exit "$status"
fi

echo "[plan-graph] all plan files passed"
