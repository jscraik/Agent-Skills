#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"

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

if [[ ! -f package.json ]]; then
	echo "[prepare-worktree] package.json not found; nothing to bootstrap for this repo shape"
	exit 0
fi

if ! command -v npm >/dev/null 2>&1; then
	echo "[prepare-worktree] npm is required but not on PATH" >&2
	exit 1
fi

if ! command -v node >/dev/null 2>&1; then
	echo "[prepare-worktree] node is required but not on PATH" >&2
	exit 1
fi

echo "[prepare-worktree] repo: $REPO_ROOT"

if [[ "$force_install" -eq 1 || ! -d node_modules ]]; then
	echo "[prepare-worktree] installing dependencies (npm install)"
	npm install
else
	echo "[prepare-worktree] node_modules already present; skipping install"
fi

echo "[prepare-worktree] syncing git hooks"
git config --local core.hooksPath "$git_common_dir/hooks"
node scripts/setup-git-hooks.js
if [[ -x "$REPO_ROOT/node_modules/.bin/simple-git-hooks" ]]; then
	"$REPO_ROOT/node_modules/.bin/simple-git-hooks"
else
	echo "[prepare-worktree] simple-git-hooks binary not found under node_modules/.bin" >&2
	echo "[prepare-worktree] rerun npm install and retry" >&2
	exit 1
fi

echo "[prepare-worktree] ready"
echo "[prepare-worktree] next: bash scripts/verify-work.sh --fast"
