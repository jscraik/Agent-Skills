#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
# The canonical script lives under Infrastructure/scripts and is projected at
# scripts/ through a symlink; resolve the repository root from that physical
# location rather than treating Infrastructure as the checkout root.
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd -P)"

# usage prints help text describing the required <issue-key>-<slug> positional argument and supported options for creating a task-specific git worktree and branch and for optionally bootstrapping it.
usage() {
	cat <<'USAGE'
Usage: scripts/new-task.sh [options] <issue-key>-<slug>

Create a dedicated git worktree and branch for one task, then print the
bootstrap commands to run inside that worktree.

This repository expects one task = one worktree = one branch = one agent thread.

Options:
  --base <ref>            Start the branch from this ref (default: main)
  --branch-prefix <name>  Branch prefix (default: jscraik/feature)
  --path <dir>            Worktree path (default: ../wt-<issue-key>-<slug>)
  --allow-stale-base      Continue from local refs when default remote-base fetch fails
  --bootstrap             Run worktree bootstrap immediately after creation
  -h, --help              Show this help text
USAGE
}

# require_option_value ensures the given option has a non-empty value that does not begin with `-`; on failure it prints an error and usage to stderr and exits with status 2.
require_option_value() {
	local option_name="$1"
	local option_value="${2:-}"
	if [[ -z "$option_value" || "$option_value" == -* ]]; then
		echo "[new-task] $option_name requires a value" >&2
		usage >&2
		exit 2
	fi
}

base_ref="main"
branch_prefix="jscraik/feature"
worktree_path=""
explicit_worktree_path=0
allow_stale_base=0
bootstrap=0
slug=""

while (( $# > 0 )); do
	case "$1" in
		--base)
			require_option_value "$1" "${2:-}"
			base_ref="${2:-}"
			shift 2
			;;
		--branch-prefix)
			require_option_value "$1" "${2:-}"
			branch_prefix="${2:-}"
			shift 2
			;;
		--path)
			require_option_value "$1" "${2:-}"
			worktree_path="${2:-}"
			explicit_worktree_path=1
			shift 2
			;;
		--allow-stale-base)
			allow_stale_base=1
			shift
			;;
		--bootstrap)
			bootstrap=1
			shift
			;;
		-h|--help)
			usage
			exit 0
			;;
		--)
			shift
			break
			;;
		-*)
			echo "[new-task] unknown option: $1" >&2
			usage >&2
			exit 2
			;;
		*)
			slug="$1"
			shift
			break
			;;
	esac
done

if [[ -z "$slug" && $# -gt 0 ]]; then
	slug="$1"
	shift
fi

if [[ -z "$slug" || $# -gt 0 ]]; then
	usage >&2
	exit 2
fi

if [[ ! "$branch_prefix" =~ ^[A-Za-z0-9._/-]+$ ]]; then
	echo "[new-task] invalid branch prefix: $branch_prefix" >&2
	exit 2
fi

if [[ "$branch_prefix" == jscraik/feature* ]]; then
	if [[ ! "$slug" =~ ^[A-Za-z][A-Za-z0-9]*-[0-9]+-[a-z0-9][a-z0-9-]*$ ]]; then
		echo "[new-task] for agent branches, slug must start with an issue key (example: JSC-123-my-task): $slug" >&2
		exit 2
	fi
elif [[ ! "$slug" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
	echo "[new-task] slug must be lower-case kebab-case: $slug" >&2
	exit 2
fi

branch_name="${branch_prefix}/${slug}"
resolved_base_ref="$base_ref"
remote_base_branch=""
remote_name="origin"
explicit_remote_ref=0

if [[ "$base_ref" == refs/remotes/*/* ]]; then
	explicit_remote_ref=1
	remote_name="${base_ref#refs/remotes/}"
	remote_name="${remote_name%%/*}"
elif [[ "$base_ref" == */* ]]; then
	candidate_remote="${base_ref%%/*}"
	candidate_branch="${base_ref#*/}"
	if git -C "$REPO_ROOT" remote get-url "$candidate_remote" >/dev/null 2>&1; then
		explicit_remote_ref=1
		remote_name="$candidate_remote"
		remote_base_branch="$candidate_branch"
	fi
elif [[ "$base_ref" != *"/"* ]]; then
	if git -C "$REPO_ROOT" show-ref --verify --quiet "refs/heads/$base_ref"; then
		remote_base_branch="$base_ref"
	elif ! git -C "$REPO_ROOT" rev-parse --verify --quiet "${base_ref}^{commit}" >/dev/null; then
		remote_base_branch="$base_ref"
	fi
fi

if [[ -z "$worktree_path" ]]; then
	worktree_base_path="${REPO_ROOT}/../wt-${slug}"
	worktree_path="$worktree_base_path"
	path_suffix=1
	while [[ -e "$worktree_path" ]]; do
		worktree_path="${worktree_base_path}-${path_suffix}"
		path_suffix=$((path_suffix + 1))
	done
fi

cd "$REPO_ROOT"

if [[ -x "$REPO_ROOT/scripts/check-git-common-config.sh" ]]; then
	"$REPO_ROOT/scripts/check-git-common-config.sh"
fi

git rev-parse --show-toplevel >/dev/null

if ! git check-ref-format --branch "$branch_name" >/dev/null 2>&1; then
	echo "[new-task] invalid git branch name: ${branch_name}" >&2
	exit 2
fi

if git show-ref --verify --quiet "refs/heads/${branch_name}"; then
	echo "[new-task] local branch already exists: ${branch_name}" >&2
	exit 1
fi

if git remote get-url origin >/dev/null 2>&1 && git ls-remote --exit-code --heads origin "${branch_name}" >/dev/null 2>&1; then
	echo "[new-task] remote branch already exists on origin: ${branch_name}" >&2
	exit 1
fi

if [[ "$explicit_worktree_path" -eq 1 && -e "$worktree_path" ]]; then
	echo "[new-task] worktree path already exists: $worktree_path" >&2
	exit 1
fi

if [[ -n "$remote_base_branch" ]]; then
	if git remote get-url "$remote_name" >/dev/null 2>&1; then
		echo "[new-task] fetching latest $remote_name/$remote_base_branch"
		if ! git fetch --prune "$remote_name" "$remote_base_branch"; then
			if [[ "$explicit_remote_ref" -eq 1 ]]; then
				echo "[new-task] failed to fetch explicit remote base: $base_ref" >&2
				exit 2
			fi
			if [[ "$allow_stale_base" -eq 0 ]]; then
				echo "[new-task] failed to fetch $remote_name/$remote_base_branch" >&2
				echo "[new-task] refusing to create from stale local refs; pass --allow-stale-base to continue intentionally" >&2
				exit 2
			fi
			echo "[new-task] warning: could not fetch $remote_name/$remote_base_branch; continuing with local refs" >&2
		elif git show-ref --verify --quiet "refs/remotes/$remote_name/$remote_base_branch"; then
			resolved_base_ref="refs/remotes/$remote_name/$remote_base_branch"
		elif [[ "$explicit_remote_ref" -eq 1 ]]; then
			echo "[new-task] explicit remote base not found on $remote_name: $base_ref" >&2
			exit 2
		fi
	elif [[ "$explicit_remote_ref" -eq 1 ]]; then
		echo "[new-task] remote '$remote_name' is required for explicit remote base: $base_ref" >&2
		exit 2
	fi
fi

if ! git rev-parse --verify --quiet "${resolved_base_ref}^{commit}" >/dev/null; then
	echo "[new-task] base ref is not a valid commit: $base_ref" >&2
	exit 2
fi

echo "[new-task] repo: $REPO_ROOT"
echo "[new-task] base: $base_ref"
if [[ "$resolved_base_ref" != "$base_ref" ]]; then
	echo "[new-task] resolved base: $resolved_base_ref"
fi
echo "[new-task] branch: ${branch_name}"
echo "[new-task] path: $worktree_path"

git worktree add "$worktree_path" -b "${branch_name}" "$resolved_base_ref"
created_worktree=1

if [[ "$bootstrap" -eq 1 ]]; then
	echo "[new-task] bootstrapping worktree"
	if ! (
		cd "$worktree_path"
		if [[ -f Makefile ]] && rg -q '^worktree-ready:' Makefile; then
			make worktree-ready
		else
			bash scripts/prepare-worktree.sh
		fi
	); then
		echo "[new-task] bootstrap failed; cleaning up created worktree and branch" >&2
		if [[ "${created_worktree:-0}" -eq 1 ]]; then
			git worktree remove --force "$worktree_path" >/dev/null 2>&1 || true
			git branch -D "$branch_name" >/dev/null 2>&1 || true
		fi
		exit 1
	fi
fi

echo
echo "[new-task] next:"
echo "  cd \"$worktree_path\""
if [[ "$bootstrap" -eq 1 ]]; then
	echo "  # bootstrap already ran (--bootstrap)"
elif [[ -f "$worktree_path/Makefile" ]] && rg -q '^worktree-ready:' "$worktree_path/Makefile"; then
	echo "  make worktree-ready"
else
	echo "  bash scripts/prepare-worktree.sh"
fi
echo "  bash scripts/codex-preflight.sh --stack auto --mode required"
