#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"

cd "$REPO_ROOT"

source "$REPO_ROOT/scripts/hooks/_sandbox_env.sh"

changed_files_file="$(mktemp "$TMPDIR/agent-skills-pre-commit.XXXXXX")"
trap 'rm -f "$changed_files_file"' EXIT

git diff --cached --name-only --diff-filter=ACMR -- >"$changed_files_file"
changed_file_count="$(wc -l <"$changed_files_file" | tr -d " ")"

if [[ "$changed_file_count" -eq 0 ]]; then
	bash Infrastructure/scripts/validate_all.sh --ephemeral
elif [[ "$changed_file_count" -gt 1000 ]]; then
	echo "Large staged change set ($changed_file_count files); running full validation instead of argv-heavy changed-files mode"
	bash Infrastructure/scripts/validate_all.sh --ephemeral
else
	bash Infrastructure/scripts/validate_all.sh --ephemeral --changed-files-from "$changed_files_file"
fi
