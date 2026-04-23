#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
cd "$repo_root"

scope="workspace"
dry_run=0

print_usage() {
  cat <<USAGE
Usage: bash Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh [--scope workspace|user] [--dry-run]

Codex-only wrapper around \
  ask skills sync --scope <workspace|user> [--dry-run]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope)
      shift
      if [[ $# -eq 0 ]]; then
        echo "Missing value for --scope" >&2
        exit 2
      fi
      scope="$1"
      ;;
    --dry-run)
      dry_run=1
      ;;
    -h|--help)
      print_usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      print_usage
      exit 2
      ;;
  esac
  shift
done

cmd=(python3 Infrastructure/bin/ask skills sync --scope "$scope")
if [[ "$dry_run" -eq 1 ]]; then
  cmd+=(--dry-run)
fi

"${cmd[@]}"
