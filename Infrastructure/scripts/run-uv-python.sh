#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"

if [[ $# -eq 0 ]]; then
	echo "Usage: bash scripts/run-uv-python.sh <command> [args...]" >&2
	exit 2
fi

if ! command -v uv >/dev/null 2>&1; then
	echo "[run-uv-python] missing required binary: uv" >&2
	exit 1
fi

export UV_CACHE_DIR="${UV_CACHE_DIR:-$REPO_ROOT/.cache/uv-python-types-cache}"
export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-$REPO_ROOT/.cache/uv-python-types}"

exec uv run --python 3.12 --group dev "$@"
