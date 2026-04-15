#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -P "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"

exec python3 "$repo_root/Infrastructure/scripts/verify_wrapper_contract_fixtures.py" "$@"
