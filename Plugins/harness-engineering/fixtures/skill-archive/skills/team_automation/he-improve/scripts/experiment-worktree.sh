#!/bin/bash

# Experiment Worktree Manager for he-improve.
#
# Usage:
#   experiment-worktree.sh create <spec_name> <exp_index> <base_branch> [shared_file ...]
#   experiment-worktree.sh cleanup <spec_name> <exp_index>
#   experiment-worktree.sh cleanup-all <spec_name>
#   experiment-worktree.sh count

set -euo pipefail

GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
  echo "Error: Not in a git repository" >&2
  exit 1
}

WORKTREE_DIR="$GIT_ROOT/.worktrees"

# experiment_branch_name constructs the branch/worktree name used for experiments in the form optimize-exp/<spec_name>/exp-<padded_index>.
experiment_branch_name() {
  local spec_name="${1:?Error: spec_name required}"
  local padded_index="${2:?Error: padded_index required}"
  echo "optimize-exp/${spec_name}/exp-${padded_index}"
}

# ensure_worktree_exclude ensures Git's info/exclude contains the literal ".worktrees" entry so the repository's .worktrees directory is ignored.
ensure_worktree_exclude() {
  local exclude_file
  exclude_file=$(git rev-parse --git-path info/exclude)
  mkdir -p "$(dirname "$exclude_file")"
  if ! grep -q "^\.worktrees$" "$exclude_file" 2>/dev/null; then
    echo ".worktrees" >> "$exclude_file"
  fi
}

# is_registered_worktree checks whether the given path is registered as a Git worktree; exits with status 0 if registered, 1 otherwise.
is_registered_worktree() {
  local worktree_path="${1:?Error: worktree_path required}"
  git worktree list --porcelain | awk -v target="$worktree_path" '
    $1 == "worktree" && $2 == target { found = 1 }
    END { exit(found ? 0 : 1) }
  '
}

# is_branch_checked_out checks whether the given branch is currently checked out in any Git worktree; exits 0 if it is, 1 otherwise.
is_branch_checked_out() {
  local branch_name="${1:?Error: branch_name required}"
  local branch_ref="refs/heads/$branch_name"
  git worktree list --porcelain | awk -v target="$branch_ref" '
    $1 == "branch" && $2 == target { found = 1 }
    END { exit(found ? 0 : 1) }
  '
}

# reset_worktree_to_base resets the specified worktree to the given base branch (hard reset) and removes all untracked and ignored files; it first verifies the worktree is checked out to the expected branch and returns non-zero on mismatch.
reset_worktree_to_base() {
  local worktree_path="${1:?Error: worktree_path required}"
  local branch_name="${2:?Error: branch_name required}"
  local base_branch="${3:?Error: base_branch required}"
  local current_branch

  current_branch=$(git -C "$worktree_path" symbolic-ref --quiet --short HEAD 2>/dev/null || true)
  if [[ "$current_branch" != "$branch_name" ]]; then
    echo "Error: Existing worktree branch mismatch: ${current_branch:-detached} != $branch_name" >&2
    return 1
  fi

  git -C "$worktree_path" reset --hard "$base_branch" >/dev/null
  git -C "$worktree_path" clean -fdx >/dev/null
}

# create_worktree creates or reuses a per-experiment git worktree and branch for a given spec/index, ensures it is reset to the specified base branch, copies repository `.env*` files (excluding `.env.example`) and any provided shared files/directories into the worktree, and echoes the created worktree path.
create_worktree() {
  local spec_name="${1:?Error: spec_name required}"
  local exp_index="${2:?Error: exp_index required}"
  local base_branch="${3:?Error: base_branch required}"
  shift 3

  local padded_index
  padded_index=$(printf "%03d" "$exp_index")
  local worktree_name="optimize-${spec_name}-exp-${padded_index}"
  local branch_name
  branch_name=$(experiment_branch_name "$spec_name" "$padded_index")
  local worktree_path="$WORKTREE_DIR/$worktree_name"

  if [[ -d "$worktree_path" ]]; then
    if ! git -C "$worktree_path" rev-parse --is-inside-work-tree >/dev/null 2>&1 || \
       ! is_registered_worktree "$worktree_path"; then
      echo "Error: Existing path is not a valid registered git worktree: $worktree_path" >&2
      return 1
    fi
    reset_worktree_to_base "$worktree_path" "$branch_name" "$base_branch"
  else
    mkdir -p "$WORKTREE_DIR"
    ensure_worktree_exclude

    if ! git worktree add -b "$branch_name" "$worktree_path" "$base_branch" --quiet 2>/dev/null; then
      if git show-ref --verify --quiet "refs/heads/$branch_name"; then
        if is_branch_checked_out "$branch_name"; then
          echo "Error: Existing experiment branch is already checked out: $branch_name" >&2
          return 1
        fi
        git branch -f "$branch_name" "$base_branch" >/dev/null
        git worktree add "$worktree_path" "$branch_name" --quiet
      else
        echo "Error: Failed to create worktree for $branch_name from $base_branch" >&2
        return 1
      fi
    fi
  fi

  for f in "$GIT_ROOT"/.env*; do
    if [[ -f "$f" ]]; then
      local basename
      basename=$(basename "$f")
      if [[ "$basename" != ".env.example" ]]; then
        cp "$f" "$worktree_path/$basename"
      fi
    fi
  done

  for shared_file in "$@"; do
    if [[ -f "$GIT_ROOT/$shared_file" ]]; then
      local dir
      dir=$(dirname "$worktree_path/$shared_file")
      mkdir -p "$dir"
      cp "$GIT_ROOT/$shared_file" "$worktree_path/$shared_file"
    elif [[ -d "$GIT_ROOT/$shared_file" ]]; then
      local dir
      dir=$(dirname "$worktree_path/$shared_file")
      mkdir -p "$dir"
      rm -rf "$worktree_path/$shared_file"
      cp -R "$GIT_ROOT/$shared_file" "$worktree_path/$shared_file"
    fi
  done

  echo "$worktree_path"
}

# cleanup_worktree removes the worktree directory for the given spec/index and deletes its associated experiment branch.
cleanup_worktree() {
  local spec_name="${1:?Error: spec_name required}"
  local exp_index="${2:?Error: exp_index required}"

  local padded_index
  padded_index=$(printf "%03d" "$exp_index")
  local worktree_name="optimize-${spec_name}-exp-${padded_index}"
  local branch_name
  branch_name=$(experiment_branch_name "$spec_name" "$padded_index")
  local worktree_path="$WORKTREE_DIR/$worktree_name"

  if [[ -d "$worktree_path" ]]; then
    git worktree remove "$worktree_path" --force 2>/dev/null || {
      rm -rf "$worktree_path" 2>/dev/null || true
      git worktree prune 2>/dev/null || true
    }
  fi

  git branch -D "$branch_name" 2>/dev/null || true
}

# cleanup_all removes all experiment worktrees and their associated branches for the given spec.
# It searches WORKTREE_DIR for directories named "optimize-<spec_name>-exp-*" and for each found
# force-removes the worktree directory, deletes the corresponding experiment branch, and then
# runs `git worktree prune`. If WORKTREE_DIR becomes empty it attempts to remove it.
# spec_name: spec identifier used to match worktree names (required).
cleanup_all() {
  local spec_name="${1:?Error: spec_name required}"
  local prefix="optimize-${spec_name}-exp-"

  if [[ ! -d "$WORKTREE_DIR" ]]; then
    return 0
  fi

  for worktree_path in "$WORKTREE_DIR"/${prefix}*; do
    if [[ -d "$worktree_path" ]]; then
      local worktree_name
      worktree_name=$(basename "$worktree_path")
      local index_str="${worktree_name#$prefix}"
      git worktree remove "$worktree_path" --force 2>/dev/null || rm -rf "$worktree_path" 2>/dev/null || true
      local branch_name
      branch_name=$(experiment_branch_name "$spec_name" "$index_str")
      git branch -D "$branch_name" 2>/dev/null || true
    fi
  done

  git worktree prune 2>/dev/null || true
  if [[ -d "$WORKTREE_DIR" ]] && [[ -z "$(ls -A "$WORKTREE_DIR" 2>/dev/null)" ]]; then
    rmdir "$WORKTREE_DIR" 2>/dev/null || true
  fi
}

# count_worktrees counts the number of worktree directories under $WORKTREE_DIR and echoes the numeric count.
count_worktrees() {
  local count=0
  if [[ -d "$WORKTREE_DIR" ]]; then
    for worktree_path in "$WORKTREE_DIR"/*; do
      if [[ -d "$worktree_path" ]] && [[ -e "$worktree_path/.git" ]]; then
        count=$((count + 1))
      fi
    done
  fi
  echo "$count"
}

# main dispatches CLI commands for managing experiment worktrees: create, cleanup, cleanup-all, count, and help.
main() {
  local command="${1:-help}"
  case "$command" in
    create) shift; create_worktree "$@" ;;
    cleanup) shift; cleanup_worktree "$@" ;;
    cleanup-all) shift; cleanup_all "$@" ;;
    count) count_worktrees ;;
    help)
      cat << 'EOF'
Experiment Worktree Manager (he-improve)

Usage:
  experiment-worktree.sh create <spec_name> <exp_index> <base_branch> [shared_file ...]
  experiment-worktree.sh cleanup <spec_name> <exp_index>
  experiment-worktree.sh cleanup-all <spec_name>
  experiment-worktree.sh count
EOF
      ;;
    *)
      echo "Unknown command: $command" >&2
      exit 1
      ;;
  esac
}

main "$@"
