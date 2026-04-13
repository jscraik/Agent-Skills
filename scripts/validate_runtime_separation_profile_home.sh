#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -P "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
python_bin="${PYTHON_BIN:-}"

if [[ -z "$python_bin" ]]; then
  if [[ -x "/opt/homebrew/bin/python3" ]]; then
    python_bin="/opt/homebrew/bin/python3"
  else
    python_bin="$(command -v python3 || true)"
  fi
fi

if [[ -z "$python_bin" ]]; then
  echo "python3 executable not found; set PYTHON_BIN to override" >&2
  exit 2
fi

exec "$python_bin" "$repo_root/scripts/validate_runtime_separation_profile_home.py" "$@"
