#!/usr/bin/env bash
set -euo pipefail

strict=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --strict)
      strict=1
      shift
      ;;
    -h|--help)
      cat <<'USAGE'
Usage: bash scripts/verify_runtime_separation_writer_mutations.sh [--strict]

Runs ownership guard checks for runtime-separation writer surfaces.
USAGE
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

repo_root="$(cd -P "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo_root"

PATH_OWNERSHIP_GUARD_SCOPE=working bash scripts/check_path_ownership_boundaries.sh

if [[ "$strict" -eq 1 ]]; then
  if git status --porcelain -- .agents .agent runtime skills-antigravity plugins/cache 2>/dev/null | grep -qE '^(A|M|D|R|C|\?\?)'; then
    echo "runtime-separation writer-mutation strict check: detected direct changes in derived/runtime paths" >&2
    exit 1
  fi
fi

echo "runtime-separation writer-mutation checks passed"
