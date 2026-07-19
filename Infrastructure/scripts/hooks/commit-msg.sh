#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -lt 1 || -z "${1:-}" ]]; then
	echo "Error: commit message file is required" >&2
	exit 2
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
source "$SCRIPT_DIR/_sandbox_env.sh"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
export MISE_TRUSTED_CONFIG_PATHS="${MISE_TRUSTED_CONFIG_PATHS:-$REPO_ROOT}"
hook_file="$1"

case "$hook_file" in
	/*) ;;
	*) hook_file="$PWD/$hook_file" ;;
esac

if [[ ! -f "$hook_file" && "$(basename -- "$hook_file")" == "COMMIT_EDITMSG" ]]; then
	hook_file="$(git -C "$REPO_ROOT" rev-parse --path-format=absolute --git-path COMMIT_EDITMSG)"
fi

if [[ ! -f "$hook_file" ]]; then
	echo "Error: commit message file not found: $hook_file" >&2
	exit 2
fi

cd "$REPO_ROOT"
node scripts/validate-commit-msg.js "$hook_file"
