#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"

# usage prints the script's usage/help text, including the `--repair` option.
usage() {
	cat <<'USAGE'
Usage: scripts/check-git-common-config.sh [--repair]

Fail when shared Git config contains values that break linked worktrees.

Options:
  --repair   Remove shared non-bare core.worktree from the common Git config.
USAGE
}

repair=0
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
	usage
	exit 0
fi

while (( $# > 0 )); do
	case "$1" in
		--repair)
			repair=1
			shift
			;;
		*)
			echo "[check-git-common-config] unknown argument: $1" >&2
			usage >&2
			exit 2
			;;
	esac
done

# resolve_git_dir determines the effective Git directory for the repository's metadata (resolving a .git file or directory) and echoes its absolute physical path, returning non-zero on error.
resolve_git_dir() {
	local git_marker="$REPO_ROOT/.git"
	local git_dir=""

	if [[ -d "$git_marker" ]]; then
		cd -- "$git_marker"
		pwd -P
		return
	fi

	if [[ -f "$git_marker" ]]; then
		git_dir="$(sed -n 's/^gitdir: //p' "$git_marker" | head -n 1)"
		if [[ -z "$git_dir" ]]; then
			echo "[check-git-common-config] malformed .git file at $git_marker" >&2
			return 1
		fi
		case "$git_dir" in
			/*) ;;
			*) git_dir="$REPO_ROOT/$git_dir" ;;
		esac
		cd -- "$git_dir"
		pwd -P
		return
	fi

	echo "[check-git-common-config] missing Git metadata at $git_marker" >&2
	return 1
}

resolve_common_git_dir() {
	local git_dir="$1"
	local common_dir="$git_dir"
	local common_dir_value=""

	if [[ -f "$git_dir/commondir" ]]; then
		common_dir_value="$(head -n 1 "$git_dir/commondir")"
		case "$common_dir_value" in
			/*) common_dir="$common_dir_value" ;;
			*) common_dir="$git_dir/$common_dir_value" ;;
		esac
	fi

	cd -- "$common_dir"
	pwd -P
}

git_dir="$(resolve_git_dir)"
common_git_dir="$(resolve_common_git_dir "$git_dir")"
common_config="$common_git_dir/config"

if [[ ! -f "$common_config" ]]; then
	echo "[check-git-common-config] no shared Git config found at $common_config"
	exit 0
fi

core_bare="$(git config --file "$common_config" --bool --get core.bare 2>/dev/null || true)"
core_worktree="$(git config --file "$common_config" --get core.worktree 2>/dev/null || true)"

if [[ "$core_bare" != "true" && -n "$core_worktree" ]]; then
	if [[ "$repair" -eq 1 ]]; then
		git config --file "$common_config" --unset-all core.worktree
		echo "[check-git-common-config] removed shared core.worktree from $common_config"
		exit 0
	fi

	cat >&2 <<EOF
Error: shared Git config contains core.worktree=$core_worktree

This repository uses linked worktrees. A non-bare common .git/config must not
pin core.worktree, because one temp worktree can poison normal Git commands for
the main checkout and sibling worktrees.

Fix:
  bash scripts/check-git-common-config.sh --repair

Manual equivalent:
	git config --file "$common_config" --unset-all core.worktree

Common Git config:
  $common_config
EOF
	exit 1
fi

echo "[check-git-common-config] ok"
