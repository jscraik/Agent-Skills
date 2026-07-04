#!/usr/bin/env bash
set -euo pipefail

GH_BIN="${GH_BIN:-gh}"
check_name="${HARNESS_CIRCLECI_PR_REF_CHECK_NAME:-pull request context}"
max_attempts="${HARNESS_CIRCLECI_PR_REF_MAX_ATTEMPTS:-18}"
sleep_seconds="${HARNESS_CIRCLECI_PR_REF_SLEEP_SECONDS:-10}"

if [[ ! "$max_attempts" =~ ^[0-9]+$ || "$max_attempts" -lt 1 ]]; then
	max_attempts=18
fi

if [[ ! "$sleep_seconds" =~ ^[0-9]+$ ]]; then
	sleep_seconds=10
fi

normalize_github_slug() {
	local slug="$1"
	slug="${slug#https://github.com/}"
	slug="${slug#git@github.com:/}"
	slug="${slug#git@github.com:}"
	slug="${slug%.git}"
	printf '%s' "$slug"
}

resolve_repo_slug() {
	local slug=""
	if [[ -n "${CIRCLE_PROJECT_USERNAME:-}" && -n "${CIRCLE_PROJECT_REPONAME:-}" ]]; then
		slug="${CIRCLE_PROJECT_USERNAME}/${CIRCLE_PROJECT_REPONAME}"
	fi
	if [[ -z "$slug" && -n "${CIRCLE_REPOSITORY_URL:-}" ]]; then
		slug="$(normalize_github_slug "$CIRCLE_REPOSITORY_URL")"
	fi
	if [[ -z "$slug" ]]; then
		local remote_url=""
		remote_url="$(git config --get remote.origin.url 2>/dev/null || true)"
		if [[ -n "$remote_url" ]]; then
			slug="$(normalize_github_slug "$remote_url")"
		fi
	fi
	if [[ -z "$slug" ]]; then
		local gh_path=""
		if [[ -x "$GH_BIN" ]]; then
			gh_path="$GH_BIN"
		else
			gh_path="$(command -v "$GH_BIN" 2>/dev/null || true)"
		fi
		if [[ -n "$gh_path" ]]; then
			slug="$("$gh_path" repo view --json nameWithOwner --jq '.nameWithOwner // ""' 2>/dev/null || true)"
		fi
	fi
	printf '%s' "$slug"
}

resolve_direct_pr_ref() {
	if [[ -n "${CIRCLE_PULL_REQUEST:-}" ]]; then
		printf '%s' "$CIRCLE_PULL_REQUEST"
		return 0
	fi
	if [[ -n "${CIRCLE_PULL_REQUESTS:-}" ]]; then
		printf '%s' "${CIRCLE_PULL_REQUESTS%%,*}"
		return 0
	fi
	return 1
}

resolve_github_pr_ref() {
	local repo_slug="$1"
	local resolved=""
	local gh_repo_args=()
	if [[ -n "$repo_slug" ]]; then
		gh_repo_args=(--repo "$repo_slug")
	fi
	if [[ -n "${CIRCLE_BRANCH:-}" && -n "${CIRCLE_PROJECT_USERNAME:-}" ]]; then
		resolved="$("$GH_BIN" pr list "${gh_repo_args[@]}" --head "${CIRCLE_PROJECT_USERNAME}:${CIRCLE_BRANCH}" --state open --json url --jq '.[0].url // ""' 2>/dev/null || true)"
	fi
	if [[ -z "$resolved" && -n "${CIRCLE_BRANCH:-}" ]]; then
		resolved="$("$GH_BIN" pr list "${gh_repo_args[@]}" --head "$CIRCLE_BRANCH" --state open --json url --jq '.[0].url // ""' 2>/dev/null || true)"
	fi
	if [[ -z "$resolved" && -n "${CIRCLE_SHA1:-}" && -n "$repo_slug" ]]; then
		resolved="$("$GH_BIN" api -H "Accept: application/vnd.github+json" "/repos/${repo_slug}/commits/${CIRCLE_SHA1}/pulls" --jq '[.[] | select(.state == "open")] | .[0].html_url // ""' 2>/dev/null || true)"
	fi
	printf '%s' "$resolved"
}

repo_slug="$(resolve_repo_slug)"

attempt=1
while [[ "$attempt" -le "$max_attempts" ]]; do
	if pr_ref="$(resolve_direct_pr_ref)"; then
		printf '%s' "$pr_ref"
		exit 0
	fi

	pr_ref="$(resolve_github_pr_ref "$repo_slug")"
	if [[ -n "$pr_ref" ]]; then
		printf '%s' "$pr_ref"
		exit 0
	fi

	if [[ "$attempt" -lt "$max_attempts" ]]; then
		echo "PR context not available yet for ${check_name}; retrying (${attempt}/${max_attempts})." >&2
		if [[ "$sleep_seconds" -gt 0 ]]; then
			sleep "$sleep_seconds"
		fi
	fi
	attempt=$(( attempt + 1 ))
done

echo "Error: unable to resolve pull request context for ${check_name}." >&2
echo "This can happen on branch-only pipelines or immediately after PR creation before CircleCI/GitHub PR metadata is visible." >&2
exit 1
