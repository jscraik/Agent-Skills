#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -P "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo_root"

scope="all"
if [[ "$#" -gt 0 && "${1:0:1}" != "-" ]]; then
  scope="$1"
  shift
fi

python3 scripts/projection_integrity.py sync --scope "$scope" "$@"
