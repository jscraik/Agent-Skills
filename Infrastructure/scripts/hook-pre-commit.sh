#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/../.." && pwd -P)"
cd "$repo_root"

bash scripts/validate-codestyle.sh --fast
node scripts/check-code-size.mjs
