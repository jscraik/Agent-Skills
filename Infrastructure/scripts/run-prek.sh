#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/lib/secure-hook-cache.sh"
repo_root="$(git -C "$script_dir" rev-parse --show-toplevel)"
git_common_dir="$(git -C "$repo_root" rev-parse --path-format=absolute --git-common-dir)"

hook_tmp_dir="${TMPDIR:-/tmp}"
if [[ ! -d "$hook_tmp_dir" || ! -w "$hook_tmp_dir" ]]; then
	if [[ -d "/private/tmp" && -w "/private/tmp" ]]; then
		hook_tmp_dir="/private/tmp"
	else
		hook_tmp_dir="/tmp"
	fi
fi
export CODEX_HOOK_CACHE_ROOT="${CODEX_HOOK_CACHE_ROOT:-$hook_tmp_dir/agent-skills-hook-cache}"
export PREK_HOME="${PREK_HOME:-$CODEX_HOOK_CACHE_ROOT/prek}"
CODEX_HOOK_CACHE_ROOT="$(validate_hook_cache_path "$CODEX_HOOK_CACHE_ROOT" "$repo_root" "$git_common_dir")"
PREK_HOME="$(validate_hook_cache_path "$PREK_HOME" "$repo_root" "$git_common_dir")"
export CODEX_HOOK_CACHE_ROOT PREK_HOME
if [[ "$PREK_HOME" != "$CODEX_HOOK_CACHE_ROOT/prek" ]]; then
	echo "[run-prek] PREK_HOME must equal CODEX_HOOK_CACHE_ROOT/prek" >&2
	exit 1
fi
secure_hook_cache_dir "$CODEX_HOOK_CACHE_ROOT"
secure_hook_cache_dir "$PREK_HOME"

exec prek "$@"
