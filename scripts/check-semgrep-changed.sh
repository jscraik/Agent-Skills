#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
RULESET_PATH="$REPO_ROOT/scripts/semgrep-pre-push.yml"
cd "$REPO_ROOT"

if ! command -v semgrep >/dev/null 2>&1; then
	echo "Error: required binary 'semgrep' is not installed or not on PATH"
	exit 1
fi

if [[ ! -f "$RULESET_PATH" ]]; then
	echo "Error: missing Semgrep ruleset at $RULESET_PATH"
	exit 1
fi

base_ref=""
if git rev-parse --verify '@{upstream}' >/dev/null 2>&1; then
	base_ref="$(git merge-base HEAD '@{upstream}')"
else
	for candidate in origin/main origin/master main master; do
		if git rev-parse --verify "$candidate" >/dev/null 2>&1; then
			base_ref="$(git merge-base HEAD "$candidate")"
			break
		fi
	done
fi

if [[ -z "$base_ref" ]]; then
	if git rev-parse --verify HEAD^ >/dev/null 2>&1; then
		base_ref="HEAD^"
	else
		echo "No comparison base available for Semgrep changed-file scan."
		exit 0
	fi
fi

changed_sources=()
while IFS= read -r -d "" path; do
	[[ -n "$path" ]] || continue
	if [[ "$path" =~ ^src/.*\.(ts|tsx|js|jsx|mts|cts)$ ]] && \
		[[ ! "$path" =~ \.d\.ts$ ]] && \
		[[ ! "$path" =~ \.(test|spec)\.(ts|tsx|js|jsx|mts|cts)$ ]]; then
		changed_sources+=("$path")
	fi
done < <(git diff --name-only --diff-filter=ACMR -z "$base_ref"...HEAD --)

if [[ ${#changed_sources[@]} -eq 0 ]]; then
	echo "No changed src/** implementation files detected for Semgrep."
	exit 0
fi

semgrep scan \
	--config "$RULESET_PATH" \
	--disable-version-check \
	--error \
	--jobs 1 \
	"${changed_sources[@]}"
