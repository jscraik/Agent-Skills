#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
if repo_root="$(git -C "$script_dir/../.." rev-parse --show-toplevel 2>/dev/null)"; then
  :
else
  repo_root="$(cd -P "$script_dir/../.." && pwd -P)"
fi

exec python3 "$repo_root/Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py" "$@"
