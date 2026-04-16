#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  Infrastructure/scripts/validate_plan_graphs.sh

Runs plan graph lint against .agent/PLANS.md and Docs/plans/*.md.
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

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if repo_root="$(git -C "$script_dir/../.." rev-parse --show-toplevel 2>/dev/null)"; then
  :
else
  repo_root="$(cd "$script_dir/../.." && pwd)"
fi
lint_python="${PLAN_GRAPH_LINT_PYTHON:-python3}"
LINTER="${PLAN_GRAPH_LINTER:-$repo_root/Infrastructure/scripts/plan_graph_lint.py}"

cd "$repo_root"

if [[ ! -f "$LINTER" ]]; then
  echo "[plan-graph] missing linter: $LINTER" >&2
  exit 1
fi

sanitize_plan_graph_output() {
  python3 -c '
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
' "$repo_root" "${HOME:-}"
}

run_plan_graph_linter() {
  local path="$1"
  "$lint_python" "$LINTER" "$path"
}

paths=(".agent/PLANS.md")
for plans_dir in docs/plans Docs/plans; do
  if [[ -d "$plans_dir" ]]; then
    while IFS= read -r path; do
      paths+=("$path")
    done < <(find "$plans_dir" -maxdepth 1 -type f -name '*.md' | sort)
  fi
done

status=0
failed_plans=()
for path in "${paths[@]}"; do
  echo "[plan-graph] lint $path"
  set +e
  lint_output="$(run_plan_graph_linter "$path" 2>&1 | sanitize_plan_graph_output)"
  lint_rc=$?
  set -e
  if [[ -n "$lint_output" ]]; then
    echo "$lint_output"
  fi
  if [[ "$lint_rc" -ne 0 ]]; then
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
