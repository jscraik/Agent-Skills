#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
source "$SCRIPT_DIR/_sandbox_env.sh"
if REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)"; then
	:
else
	REPO_ROOT="$(cd -- "$SCRIPT_DIR/../../.." && pwd -P)"
fi
export MISE_TRUSTED_CONFIG_PATHS="${MISE_TRUSTED_CONFIG_PATHS:-$REPO_ROOT}"

cd "$REPO_ROOT"

# Git legitimately holds the current index lock while invoking pre-commit.
# The leaf proves that the lock owner is a Git ancestor before waiving it.
# Other metadata locks and write failures remain fail-closed.
python3 Infrastructure/scripts/validation-and-linting/git_metadata_preflight.py --repo-root "$REPO_ROOT" --allow-current-index-lock --json

changed_files_file="$(mktemp "$TMPDIR/agent-skills-pre-commit.XXXXXX")"
trap 'rm -f "$changed_files_file"' EXIT

git diff --cached --name-only --diff-filter=ACMR -- >"$changed_files_file"
changed_file_count="$(wc -l <"$changed_files_file" | tr -d " ")"

if [[ "$changed_file_count" -eq 0 ]]; then
	bash Infrastructure/scripts/validate_all.sh --ephemeral --staged-source
elif [[ "$changed_file_count" -gt 1000 ]]; then
	echo "Large staged change set ($changed_file_count files); running full validation instead of argv-heavy changed-files mode"
	bash Infrastructure/scripts/validate_all.sh --ephemeral --staged-source
else
	bash Infrastructure/scripts/validate_all.sh --ephemeral --staged-source --changed-files-from "$changed_files_file"
fi
