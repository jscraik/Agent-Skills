#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Guard critical hook/lint config from index/worktree drift. Hook runners may
# temporarily stash unstaged changes, which can make pre-commit evaluate an
# older staged config snapshot than the file currently shown in the worktree.
critical_files=("biome.json")
drift_files=()

	for config_path in "${critical_files[@]}"; do
		if ! git ls-files --error-unmatch -- "$config_path" >/dev/null 2>&1; then
			continue
		fi

		index_blob="$(git rev-parse --verify ":${config_path}" 2>/dev/null || true)"
		if [[ -n "$index_blob" && ! -e "$config_path" ]]; then
			drift_files+=("$config_path")
			continue
		fi
		if [[ ! -f "$config_path" ]]; then
			continue
		fi
		worktree_blob="$(git hash-object --path="$config_path" "$config_path" 2>/dev/null || true)"
		if [[ -n "$index_blob" && -n "$worktree_blob" && "$index_blob" != "$worktree_blob" ]]; then
			drift_files+=("$config_path")
		fi
	done

if [[ ${#drift_files[@]} -eq 0 ]]; then
	exit 0
fi

echo "Error: critical hook config differs between index and worktree:" >&2
for config_path in "${drift_files[@]}"; do
	echo "  - $config_path" >&2
done
echo >&2
echo "Why this fails: pre-commit style runners stash unstaged changes, so hooks may read stale staged config." >&2
echo "Fix: stage or stash these files before committing, then retry." >&2
echo "Example: git add ${drift_files[*]}" >&2
exit 1
