#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

related_sources=()
while IFS= read -r path; do
	[[ -n "$path" ]] || continue
	if [[ "$path" =~ ^src/.*\.(ts|tsx|js|jsx|mts|cts)$ ]] && \
		[[ ! "$path" =~ \.d\.ts$ ]] && \
		[[ ! "$path" =~ \.(test|spec)\.(ts|tsx|js|jsx|mts|cts)$ ]]; then
		related_sources+=("$path")
	fi
done < <(git diff --cached --name-only --diff-filter=ACMR)

if [[ ${#related_sources[@]} -eq 0 ]]; then
	echo "No staged src/** implementation changes detected for related tests."
	exit 0
fi

pnpm exec vitest related --run --passWithNoTests "${related_sources[@]}"
