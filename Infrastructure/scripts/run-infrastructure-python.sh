#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/../.." && pwd)"

cd "$repo_root/Infrastructure"
export PYTHONDONTWRITEBYTECODE="${PYTHONDONTWRITEBYTECODE:-1}"
temp_base="${TMPDIR:-/tmp}"
export UV_CACHE_DIR="${UV_CACHE_DIR:-${temp_base%/}/agent-skills-uv-cache}"

exec uv run --frozen --group test --group lint python "$@"
