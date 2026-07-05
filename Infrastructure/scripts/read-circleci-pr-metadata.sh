#!/usr/bin/env bash
set -euo pipefail

GH_BIN="${GH_BIN:-gh}"
pr_ref="${1:-}"

if [[ -z "$pr_ref" ]]; then
	echo "Usage: bash scripts/read-circleci-pr-metadata.sh <pr-ref>" >&2
	exit 2
fi

normalize_github_slug() {
	local slug="$1"
	slug="${slug#https://github.com/}"
	slug="${slug#git@github.com:/}"
	slug="${slug#git@github.com:}"
	slug="${slug%.git}"
	printf '%s' "$slug"
}

repo_slug_from_pr_ref() {
	local ref="${1%%[?#]*}"
	if [[ "$ref" =~ ^https://github[.]com/([^/]+)/([^/]+)/pull/[0-9]+/?$ ]]; then
		printf '%s/%s' "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}"
		return 0
	fi
	return 1
}

resolve_repo_slug() {
	local slug=""
	if slug="$(repo_slug_from_pr_ref "$pr_ref")"; then
		printf '%s' "$slug"
		return 0
	fi
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
	printf '%s' "$slug"
}

resolve_pr_number() {
	local ref="${1%%[?#]*}"
	ref="${ref%/}"
	if [[ "$ref" =~ /pull/([0-9]+)$ ]]; then
		printf '%s' "${BASH_REMATCH[1]}"
		return 0
	fi
	if [[ "$ref" =~ ^[0-9]+$ ]]; then
		printf '%s' "$ref"
		return 0
	fi
	return 1
}

find_executable() {
	local candidate="$1"
	if [[ -x "$candidate" ]]; then
		printf '%s' "$candidate"
		return 0
	fi
	command -v "$candidate" 2>/dev/null || true
}

repo_slug="$(resolve_repo_slug)"
pr_number="$(resolve_pr_number "$pr_ref" || true)"

if [[ -z "$repo_slug" ]]; then
	echo "Error: unable to resolve GitHub repository slug for PR metadata lookup." >&2
	exit 1
fi

gh_path="$(find_executable "$GH_BIN")"
if [[ -n "$gh_path" ]]; then
	if "$gh_path" pr view "$pr_ref" --repo "$repo_slug" --json body,title,headRefName; then
		exit 0
	fi
	echo "GitHub CLI PR metadata lookup failed; falling back to public GitHub REST pull endpoint." >&2
else
	echo "GitHub CLI not available; falling back to public GitHub REST pull endpoint." >&2
fi

if [[ -z "$pr_number" ]]; then
	echo "Error: unable to derive pull request number from '$pr_ref'." >&2
	exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
	echo "Error: curl is required for public GitHub REST pull metadata fallback." >&2
	exit 1
fi
if ! command -v jq >/dev/null 2>&1; then
	echo "Error: jq is required for public GitHub REST pull metadata fallback." >&2
	exit 1
fi

curl -fsSL -H "Accept: application/vnd.github+json" \
	"https://api.github.com/repos/${repo_slug}/pulls/${pr_number}" |
	jq -c '{body:(.body // ""),title:(.title // ""),headRefName:(.head.ref // "")}'
