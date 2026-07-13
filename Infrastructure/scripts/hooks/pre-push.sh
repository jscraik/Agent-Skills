#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"

cd "$REPO_ROOT"

source "$REPO_ROOT/scripts/hooks/_sandbox_env.sh"

changed_files_file="$(mktemp "$TMPDIR/agent-skills-pre-push.XXXXXX")"
trap 'rm -f "$changed_files_file"' EXIT

if git rev-parse --verify @{upstream} >/dev/null 2>&1; then
	git diff --name-only --diff-filter=ACMR @{upstream}...HEAD -- >"$changed_files_file"
elif git rev-parse --verify HEAD^ >/dev/null 2>&1; then
	git diff --name-only --diff-filter=ACMR HEAD^..HEAD -- >"$changed_files_file"
fi

changed_file_count="$(wc -l <"$changed_files_file" | tr -d " ")"
if [[ "$changed_file_count" -gt 0 ]]; then
	bash Infrastructure/scripts/validate_all.sh --ephemeral --head-source --changed-files-from "$changed_files_file"
else
	bash Infrastructure/scripts/validate_all.sh --ephemeral --head-source
fi

python3 Infrastructure/scripts/lifecycle-and-sync/diagnose_changed_skills.py "$changed_files_file"
