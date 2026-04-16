#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"

TRACKED_ARTIFACT_PATHS=(
	".diagram"
	".diagram/context/diagram-context.md"
	".diagram/context/diagram-context.meta.json"
)

is_ignored_change() {
	local changed_path="$1"

	case "$changed_path" in
		src/*.test.ts|src/*.spec.ts|src/*.test.js|src/*.spec.js)
			return 0
			;;
		*)
			return 1
			;;
	esac
}

is_architecture_sensitive_change() {
	local changed_path="$1"

	case "$changed_path" in
		package.json|tsconfig.json|.diagramrc|scripts/refresh-diagram-context.sh|scripts/check-diagram-freshness.sh)
			return 0
			;;
		.diagram/*)
			return 0
			;;
		src/*)
			if is_ignored_change "$changed_path"; then
				return 1
			fi
			return 0
			;;
		*)
			return 1
			;;
	esac
}

snapshot_artifacts() {
	local path
	for path in "${TRACKED_ARTIFACT_PATHS[@]}"; do
		if [[ -d "$REPO_ROOT/$path" ]]; then
			while IFS= read -r file; do
				local rel_path="${file#$REPO_ROOT/}"
				local checksum
				checksum="$(normalized_checksum "$file" "$rel_path")"
				printf '%s %s
' "$rel_path" "$checksum"
			done < <(find "$REPO_ROOT/$path" -type f | sort)
		elif [[ -f "$REPO_ROOT/$path" ]]; then
			local checksum
			checksum="$(normalized_checksum "$REPO_ROOT/$path" "$path")"
			printf '%s %s
' "$path" "$checksum"
		fi
	done
}

normalized_checksum() {
	local file="$1"
	local rel_path="$2"

	case "$rel_path" in
		*/diagram-context.md)
			sed '/^Generated: /d' "$file" | shasum -a 256 | awk '{print $1}'
			;;
		*/diagram-context.meta.json)
			jq -c 'del(.generated_at, .last_generated_epoch, .changed, .context_sha256)' "$file" | shasum -a 256 | awk '{print $1}'
			;;
		*/manifest.json)
			jq -c 'del(.generatedAt)' "$file" | shasum -a 256 | awk '{print $1}'
			;;
		*)
			shasum -a 256 "$file" | awk '{print $1}'
			;;
	esac
}

resolve_diff_base() {
	if git -C "$REPO_ROOT" rev-parse --verify '@{upstream}' >/dev/null 2>&1; then
		git -C "$REPO_ROOT" merge-base HEAD '@{upstream}'
		return 0
	fi

	if git -C "$REPO_ROOT" rev-parse --verify main >/dev/null 2>&1; then
		git -C "$REPO_ROOT" merge-base HEAD main
		return 0
	fi

	if git -C "$REPO_ROOT" rev-parse --verify HEAD^ >/dev/null 2>&1; then
		git -C "$REPO_ROOT" rev-parse HEAD^
		return 0
	fi

	return 1
}

collect_changed_paths() {
	local base
	if base="$(resolve_diff_base)"; then
		{
			git -C "$REPO_ROOT" diff --name-only "$base...HEAD"
			git -C "$REPO_ROOT" diff --name-only
			git -C "$REPO_ROOT" diff --cached --name-only
		} | awk 'NF { print }' | sort -u
	else
		{
			git -C "$REPO_ROOT" diff --name-only
			git -C "$REPO_ROOT" diff --cached --name-only
		} | awk 'NF { print }' | sort -u
	fi
}

should_refresh=0
while IFS= read -r changed_path; do
	[[ -n "$changed_path" ]] || continue
	if is_architecture_sensitive_change "$changed_path"; then
		should_refresh=1
		break
	fi
done < <(collect_changed_paths)

if [[ "$should_refresh" -ne 1 ]]; then
	echo "Diagram freshness check skipped: no architecture-sensitive implementation paths changed."
	exit 0
fi

echo "Refreshing architecture diagrams for changed sensitive paths..."
before_snapshot="$(snapshot_artifacts)"
bash "$REPO_ROOT/scripts/refresh-diagram-context.sh" --force --quiet
after_snapshot="$(snapshot_artifacts)"

if [[ "$before_snapshot" != "$after_snapshot" ]]; then
	echo "Error: architecture diagram artifacts are stale after refresh."
	echo "Changed tracked files:"
	git -C "$REPO_ROOT" diff --name-only -- "${TRACKED_ARTIFACT_PATHS[@]}"
	echo "Fix: run 'bash scripts/refresh-diagram-context.sh --force' and commit the updated artifacts."
	exit 1
fi

echo "Diagram freshness check passed."
