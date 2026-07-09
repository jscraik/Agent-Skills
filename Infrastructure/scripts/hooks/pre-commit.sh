#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"

cd "$REPO_ROOT"

hook_tmp_dir="${TMPDIR:-}"
if [[ -z "$hook_tmp_dir" || ! -d "$hook_tmp_dir" || ! -w "$hook_tmp_dir" ]]; then
	hook_tmp_dir="/private/tmp"
fi
export TMPDIR="$hook_tmp_dir"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$TMPDIR/agent-skills-uv-cache}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$TMPDIR/agent-skills-xdg-cache}"
export XDG_STATE_HOME="${XDG_STATE_HOME:-$TMPDIR/agent-skills-xdg-state}"
export MISE_CACHE_DIR="${MISE_CACHE_DIR:-$TMPDIR/agent-skills-mise-cache}"
export MISE_STATE_DIR="${MISE_STATE_DIR:-$TMPDIR/agent-skills-mise-state}"
export MISE_TRUSTED_CONFIG_PATHS="${MISE_TRUSTED_CONFIG_PATHS:-$REPO_ROOT}"

changed_files_file="$(mktemp "$TMPDIR/agent-skills-pre-commit.XXXXXX")"
trap 'rm -f "$changed_files_file"' EXIT

git diff --cached --name-only --diff-filter=ACMR -- >"$changed_files_file"
changed_file_count="$(wc -l <"$changed_files_file" | tr -d " ")"

if [[ "$changed_file_count" -eq 0 ]]; then
	bash Infrastructure/scripts/validate_all.sh --ephemeral
elif [[ "$changed_file_count" -gt 1000 ]]; then
	echo "Large staged change set ($changed_file_count files); running full validation instead of argv-heavy changed-files mode"
	bash Infrastructure/scripts/validate_all.sh --ephemeral
else
	bash Infrastructure/scripts/validate_all.sh --ephemeral --changed-files-from "$changed_files_file"
fi
