#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
if REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)"; then
	:
else
	REPO_ROOT="$(cd -- "$SCRIPT_DIR/../../.." && pwd -P)"
fi

# usage prints the help message describing usage and supported options for prepare-worktree.sh.
usage() {
	cat <<'USAGE'
Usage: scripts/prepare-worktree.sh [options]

Prepare a freshly created git worktree for local hooks and pre-push checks.

Options:
  --force-install   Run npm install even if node_modules already exists
  -h, --help        Show this help text
USAGE
}

force_install=0
while (( $# > 0 )); do
	case "$1" in
		--force-install)
			force_install=1
			shift
			;;
		-h|--help)
			usage
			exit 0
			;;
		*)
			echo "[prepare-worktree] unknown argument: $1" >&2
			usage >&2
			exit 2
			;;
	esac
done

cd "$REPO_ROOT"

if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
	echo "[prepare-worktree] not inside a git work tree" >&2
	exit 1
fi
git_common_dir="$(git rev-parse --git-common-dir)"

echo "[prepare-worktree] repo: $REPO_ROOT"

if [[ -f package.json ]]; then
	if ! command -v npm >/dev/null 2>&1; then
		echo "[prepare-worktree] npm is required but not on PATH" >&2
		exit 1
	fi

	if ! command -v node >/dev/null 2>&1; then
		echo "[prepare-worktree] node is required but not on PATH" >&2
		exit 1
	fi

	if [[ "$force_install" -eq 1 || ! -d node_modules ]]; then
		echo "[prepare-worktree] installing dependencies (npm install)"
		npm install
	else
		echo "[prepare-worktree] node_modules already present; skipping install"
	fi
else
	echo "[prepare-worktree] package.json not found; skipping package install"
fi

echo "[prepare-worktree] syncing git hooks"
git config --local core.hooksPath "$git_common_dir/hooks"
if [[ -f "$REPO_ROOT/scripts/install-prek-hooks.sh" ]]; then
	bash "$REPO_ROOT/scripts/install-prek-hooks.sh"
else
	echo "[prepare-worktree] scripts/install-prek-hooks.sh is missing" >&2
	exit 1
fi

echo "[prepare-worktree] ready"
echo "[prepare-worktree] next: bash scripts/verify-work.sh --fast"
