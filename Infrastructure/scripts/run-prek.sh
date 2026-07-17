#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/lib/secure-hook-cache.sh"

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
secure_hook_cache_dir "$CODEX_HOOK_CACHE_ROOT"
secure_hook_cache_dir "$PREK_HOME"

exec prek "$@"
