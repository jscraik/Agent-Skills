#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

unset_git_context_env() {
	local git_env_name
	while IFS= read -r git_env_name; do
		[[ -n "$git_env_name" ]] && unset "$git_env_name"
	done < <(compgen -v GIT_)
}

bash ./scripts/check-validation-locks.sh

base_ref="$(git merge-base HEAD '@{upstream}' 2>/dev/null || git merge-base HEAD origin/main 2>/dev/null || git merge-base HEAD main 2>/dev/null || true)"
if [[ -z "$base_ref" ]]; then
	echo "Error: unable to resolve a base ref for pre-push changed-file gates." >&2
	echo "Set an upstream branch or ensure origin/main is available before pushing." >&2
	exit 1
fi

changed_files=""
changed_files="$(git diff --name-only --diff-filter=ACMRDT "$base_ref"...HEAD --)"

only_environment_change=false
if [[ -n "$changed_files" ]]; then
	only_environment_change=true
	while IFS= read -r changed_file; do
		[[ -z "$changed_file" ]] && continue
		if [[ "$changed_file" != ".codex/environments/environment.toml" ]]; then
			only_environment_change=false
			break
		fi
	done <<< "$changed_files"
fi

if [[ "$only_environment_change" == true ]]; then
	echo "Environment-only push detected; running check-environment only."
	bash ./scripts/check-environment.sh
	exit 0
fi

bash ./scripts/run-harness-gate.sh docs-gate --mode required --json

tmp_changed_files="$(mktemp)"
trap 'rm -f "$tmp_changed_files"' EXIT
git diff --name-only --diff-filter=ACMRDT "$base_ref"...HEAD -- > "$tmp_changed_files"
bash ./scripts/check-diagram-freshness.sh --changed-files "$tmp_changed_files"

bash ./scripts/run-harness-gate.sh tooling-audit --path . --json
bash ./scripts/check-environment.sh
make semgrep-changed
if [[ "${HARNESS_PRE_PUSH_FULL_CODESTYLE:-0}" == "1" ]]; then
	make codestyle
else
	echo "Skipping broad make codestyle in pre-push; run HARNESS_PRE_PUSH_FULL_CODESTYLE=1 git push to enable it."
fi
unset_git_context_env
bash ./scripts/run-package-command.sh npm run build
