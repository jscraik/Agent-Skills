#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"

export PREK_HOME="${PREK_HOME:-$repo_root/.cache/prek}"
mkdir -p "$PREK_HOME"

exec prek "$@"
