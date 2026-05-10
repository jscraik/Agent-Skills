#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ -d "${script_dir}/../Infrastructure" ]]; then
  repo_root="$(cd -- "${script_dir}/.." && pwd)"
else
  repo_root="$(cd -- "${script_dir}/../.." && pwd)"
fi

export PYTHONPATH="${repo_root}/Infrastructure/scripts/lib${PYTHONPATH:+:${PYTHONPATH}}"

cd "${repo_root}"
exec python3 -m ask.bootstrap "$@"
