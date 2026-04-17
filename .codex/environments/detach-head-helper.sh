#!/usr/bin/env bash
# shellcheck shell=bash

# Attach detached HEAD checkouts to a stable codex/<repo>-worktree-<sha> branch.
codex_attach_detached_head() {
	if ! command -v git >/dev/null 2>&1; then
		return 0
	fi

	if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
		return 0
	fi

	local current_branch
	current_branch="$(git symbolic-ref --short -q HEAD || true)"
	if [[ -n "$current_branch" ]]; then
		return 0
	fi

	local repo_slug short_sha branch_base branch_name suffix
	repo_slug="$(basename "$PWD" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')"
	if [[ -z "$repo_slug" ]]; then
		repo_slug="worktree"
	fi

	short_sha="$(git rev-parse --short HEAD)"
	branch_base="codex/$repo_slug-worktree-$short_sha"
	branch_name="$branch_base"
	suffix=1
	while git show-ref --verify --quiet "refs/heads/$branch_name"; do
		branch_name="$branch_base-$suffix"
		suffix=$((suffix + 1))
	done

	echo "[codex] detached HEAD detected; creating branch $branch_name"
	git switch -c "$branch_name"

	if git ls-remote --exit-code --heads origin main >/dev/null 2>&1; then
		git fetch --quiet origin main
		git branch --set-upstream-to=origin/main "$branch_name" >/dev/null 2>&1 || true
		echo "[codex] tracking origin/main for $branch_name"
	fi
}
