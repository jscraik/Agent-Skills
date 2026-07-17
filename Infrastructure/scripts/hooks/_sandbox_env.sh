#!/usr/bin/env bash
# Shared sandbox-safe cache/state setup for git hook adapters.

# Git hook processes may inherit repository-location variables from Git or a
# hook runner. They are execution context, not authority for locating this
# checkout, and projected hook invocations can otherwise resolve a nested
# directory as the repository root.
unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE
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
export UV_CACHE_DIR="${UV_CACHE_DIR:-$TMPDIR/agent-skills-uv-cache}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$TMPDIR/agent-skills-xdg-cache}"
export XDG_STATE_HOME="${XDG_STATE_HOME:-$TMPDIR/agent-skills-xdg-state}"
export MISE_CACHE_DIR="${MISE_CACHE_DIR:-$TMPDIR/agent-skills-mise-cache}"
export MISE_STATE_DIR="${MISE_STATE_DIR:-$TMPDIR/agent-skills-mise-state}"
if [[ -n "${REPO_ROOT:-}" ]]; then
	export MISE_TRUSTED_CONFIG_PATHS="${MISE_TRUSTED_CONFIG_PATHS:-$REPO_ROOT}"
fi
