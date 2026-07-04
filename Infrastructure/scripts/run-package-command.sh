#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if [[ "$#" -lt 1 ]]; then
	echo "Usage: bash scripts/run-package-command.sh <command> [args...]" >&2
	exit 2
fi

command_name="$1"
shift

mise_tool_name() {
	case "$1" in
		python3)
			printf '%s\n' "python"
			;;
		*)
			printf '%s\n' "$1"
			;;
	esac
}

mise_tool_is_managed() {
	local tool_name=""
	tool_name="$(mise_tool_name "$1")"
	local line=""
	local key=""
	while IFS= read -r line; do
		line="${line%%#*}"
		[[ "$line" == *"="* ]] || continue
		key="${line%%=*}"
		key="${key#"${key%%[![:space:]]*}"}"
		key="${key%"${key##*[![:space:]]}"}"
		key="${key%\"}"
		key="${key#\"}"
		key="${key%\'}"
		key="${key#\'}"
		if [[ "$key" == "$tool_name" ]]; then
			return 0
		fi
	done <"$repo_root/.mise.toml"
	return 1
}

prepend_mise_tool_paths() {
	[[ -f "$repo_root/.mise.toml" ]] || return 0
	mise_tool_is_managed "$command_name" || return 0
	if ! command -v mise >/dev/null 2>&1; then
		echo "Error: .mise.toml is present but mise is not installed or not on PATH" >&2
		exit 127
	fi

	local node_path=""
	local command_path=""
	if ! node_path="$(mise --cd "$repo_root" which node 2>/dev/null)"; then
		echo "Error: mise could not resolve pinned tool 'node' from .mise.toml" >&2
		echo "Fix: trust this repo with mise and install pinned tools, then retry." >&2
		exit 127
	fi
	if ! command_path="$(mise --cd "$repo_root" which "$command_name" 2>/dev/null)"; then
		echo "Error: mise could not resolve pinned tool '$command_name' from .mise.toml" >&2
		echo "Fix: trust this repo with mise and install pinned tools, then retry." >&2
		exit 127
	fi

	if [[ -z "$node_path" || ! -x "$node_path" ]]; then
		echo "Error: mise resolved node to a non-executable path: $node_path" >&2
		exit 127
	fi
	if [[ -z "$command_path" || ! -e "$command_path" ]]; then
		echo "Error: mise resolved '$command_name' to a missing path: $command_path" >&2
		exit 127
	fi

	PATH="$(dirname "$node_path"):$(dirname "$command_path"):$PATH"
	export PATH
}

prepend_mise_tool_paths

if ! command -v "$command_name" >/dev/null 2>&1; then
	echo "Error: required command '$command_name' is not installed or not on PATH" >&2
	exit 127
fi

exec "$command_name" "$@"
