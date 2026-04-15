#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v vale >/dev/null 2>&1; then
	echo "Error: required binary 'vale' is not installed or not on PATH"
	exit 1
fi

staged_docs=()
while IFS= read -r -d "" path; do
	[[ -n "$path" ]] || continue
	staged_docs+=("$path")
done < <(
	git diff --cached --name-only --diff-filter=ACMR -z -- \
		README.md \
		CONTRIBUTING.md \
		AGENTS.md \
		":(glob)docs/**/*.md"
)

if [[ ${#staged_docs[@]} -eq 0 ]]; then
	echo "No staged documentation changes detected for Vale."
	exit 0
fi

vale --config .vale.ini "${staged_docs[@]}"
