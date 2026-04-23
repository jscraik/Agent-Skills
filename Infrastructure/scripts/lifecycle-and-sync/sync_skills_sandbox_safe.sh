#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  Infrastructure/scripts/lifecycle-and-sync/sync_skills_sandbox_safe.sh

Sandbox-safe companion sync for this environment.
This script intentionally avoids mutating protected runtime paths such as:
  - .agents/skills
  - ~/.codex/skills
It regenerates semantic-skill governance artifacts only.
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

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$repo_root"
index_file="$repo_root/docs/skills-by-type.md"
python3 "$repo_root/Infrastructure/scripts/lifecycle-and-sync/skill_scan.py" write-skill-type-index --output "$index_file"
bash Infrastructure/scripts/validation-and-linting/lint_skill_types.sh
echo "[sandbox-safe-sync] Wrote $index_file"
echo "[sandbox-safe-sync] Completed without touching protected runtime skill paths."
