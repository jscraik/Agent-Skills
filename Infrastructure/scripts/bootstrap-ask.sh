#!/usr/bin/env bash
set -euo pipefail

script_source="${BASH_SOURCE[0]}"
while [[ -L "${script_source}" ]]; do
  script_dir="$(cd -- "$(dirname -- "${script_source}")" && pwd)"
  script_source="$(readlink "${script_source}")"
  if [[ "${script_source}" != /* ]]; then
    script_source="${script_dir}/${script_source}"
  fi
done

script_dir="$(cd -- "$(dirname -- "${script_source}")" && pwd)"
if git_root="$(git -C "${script_dir}" rev-parse --show-toplevel 2>/dev/null)"; then
  repo_root="${git_root}"
elif [[ -d "${script_dir}/../Infrastructure" ]]; then
  repo_root="$(cd -- "${script_dir}/.." && pwd)"
else
  repo_root="$(cd -- "${script_dir}/../.." && pwd)"
fi

export PYTHONPATH="${repo_root}/Infrastructure/scripts/lib${PYTHONPATH:+:${PYTHONPATH}}"
export PATH="${repo_root}/bin${PATH:+:${PATH}}"

cd "${repo_root}"
exec python3 -m ask.bootstrap "$@"
