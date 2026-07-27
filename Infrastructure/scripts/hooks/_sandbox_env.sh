#!/usr/bin/env bash
# Shared sandbox-safe cache/state setup for git hook adapters.

# Git hook processes may inherit repository-location variables from Git or a
# hook runner. They are execution context, not authority for locating this
# checkout, and projected hook invocations can otherwise resolve a nested
# directory as the repository root.
unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR
unset GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES

hook_tmp_dir="${TMPDIR:-}"
if [[ -z "$hook_tmp_dir" || ! -d "$hook_tmp_dir" || ! -w "$hook_tmp_dir" ]]; then
	if [[ -d "/private/tmp" && -w "/private/tmp" ]]; then
		hook_tmp_dir="/private/tmp"
	else
		hook_tmp_dir="/tmp"
	fi
fi
export TMPDIR="$hook_tmp_dir"

cache_path_is_usable() {
	local candidate="$1"
	local parent
	[[ -n "$candidate" ]] || return 1
	if [[ -e "$candidate" ]]; then
		[[ -d "$candidate" && -w "$candidate" ]]
		return
	fi
	parent="$candidate"
	while [[ ! -e "$parent" && "$parent" != "/" ]]; do
		parent="$(dirname "$parent")"
	done
	[[ -d "$parent" && -w "$parent" ]]
}

set_hook_cache_path() {
	local variable_name="$1"
	local fallback="$2"
	local current="${!variable_name:-}"
	if ! cache_path_is_usable "$current"; then
		export "$variable_name=$fallback"
	fi
}

set_hook_cache_path UV_CACHE_DIR "$TMPDIR/agent-skills-uv-cache"
set_hook_cache_path XDG_CACHE_HOME "$TMPDIR/agent-skills-xdg-cache"
set_hook_cache_path XDG_STATE_HOME "$TMPDIR/agent-skills-xdg-state"
set_hook_cache_path MISE_CACHE_DIR "$TMPDIR/agent-skills-mise-cache"
set_hook_cache_path MISE_STATE_DIR "$TMPDIR/agent-skills-mise-state"
if [[ -n "${REPO_ROOT:-}" ]]; then
	export MISE_TRUSTED_CONFIG_PATHS="${MISE_TRUSTED_CONFIG_PATHS:-$REPO_ROOT}"
fi
