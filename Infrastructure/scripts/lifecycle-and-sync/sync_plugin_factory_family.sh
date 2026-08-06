#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
if repo_root="$(git -C "$script_dir" rev-parse --show-toplevel 2>/dev/null)"; then
  :
else
  repo_root="$(cd -P "$script_dir/../../.." && pwd -P)"
fi
cd "$repo_root"

python3 Infrastructure/scripts/lifecycle-and-sync/projection_integrity.py sync --scope plugin-factory "$@"
