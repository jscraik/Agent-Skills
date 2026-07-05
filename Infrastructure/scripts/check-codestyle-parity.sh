#!/usr/bin/env bash
set -euo pipefail

# Ensure realpath is available before using it
command -v realpath >/dev/null || { echo "[codestyle-parity] error: realpath is required but not found" >&2; exit 1; }

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT_DEFAULT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"

repo_root="$REPO_ROOT_DEFAULT"
manifest_path=""

# usage prints the help/usage text for scripts/check-codestyle-parity.sh, describing the --repo-root, --manifest, and -h/--help options.
usage() {
	cat <<'USAGE'
Usage: scripts/check-codestyle-parity.sh [options]

Fail if the repo-local codestyle pack drifts from the pinned checksum manifest.

Options:
  --repo-root PATH  Repo root to validate (default: script parent)
  --manifest PATH   Manifest file path (default: <repo-root>/codestyle/CHECKSUMS.sha256)
  -h, --help        Show this help text
USAGE
}

while (( $# > 0 )); do
	case "$1" in
		--repo-root)
			repo_root="${2:-}"
			if [[ -z "$repo_root" ]]; then
				echo "[codestyle-parity] error: --repo-root requires a non-empty value" >&2
				usage >&2
				exit 2
			fi
			shift 2
			;;
		--manifest)
			manifest_path="${2:-}"
			if [[ -z "$manifest_path" ]]; then
				echo "[codestyle-parity] error: --manifest requires a non-empty value" >&2
				usage >&2
				exit 2
			fi
			shift 2
			;;
		-h|--help)
			usage
			exit 0
			;;
		*)
			echo "[codestyle-parity] unknown argument: $1" >&2
			usage >&2
			exit 2
			;;
	esac
done

# Validate and resolve repo_root before use (portable across GNU/BSD realpath)
if [[ ! -d "$repo_root" ]]; then
	echo "[codestyle-parity] error: repo-root does not exist or is not accessible: $repo_root" >&2
	exit 1
fi
if ! resolved_repo_root="$(realpath "$repo_root" 2>/dev/null)"; then
	echo "[codestyle-parity] error: repo-root does not exist or is not accessible: $repo_root" >&2
	exit 1
fi
repo_root="$resolved_repo_root"

if [[ -z "$manifest_path" ]]; then
	manifest_path="$repo_root/codestyle/CHECKSUMS.sha256"
fi

if [[ ! -f "$manifest_path" ]]; then
	echo "[codestyle-parity] missing checksum manifest: $manifest_path" >&2
	exit 1
fi

if command -v shasum >/dev/null 2>&1; then
	# hash_file computes the SHA-256 checksum of the given file path and echoes the hexadecimal digest.
	hash_file() {
		shasum -a 256 "$1" | awk '{print $1}'
	}
elif command -v sha256sum >/dev/null 2>&1; then
	# hash_file extracts the SHA-256 hex digest of the given file path and echoes it.
	hash_file() {
		sha256sum "$1" | awk '{print $1}'
	}
else
	echo "[codestyle-parity] missing required hash command: shasum or sha256sum" >&2
	exit 1
fi

checked=0
while IFS= read -r raw_line || [[ -n "$raw_line" ]]; do
	line="${raw_line%%#*}"
	line="$(printf '%s' "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
	if [[ -z "$line" ]]; then
		continue
	fi

	expected_hash="${line%% *}"
	relative_path="${line#"${expected_hash}"}"
	relative_path="${relative_path# }"
	relative_path="${relative_path# }"

	if [[ -z "$expected_hash" || -z "$relative_path" ]]; then
		echo "[codestyle-parity] malformed manifest entry: $raw_line" >&2
		exit 1
	fi

	target_path="$repo_root/$relative_path"

	if [[ ! -f "$target_path" ]]; then
		echo "[codestyle-parity] missing codestyle file: $relative_path" >&2
		exit 1
	fi

	# Resolve to absolute path and verify containment within repo_root
	if ! resolved_path="$(realpath "$target_path" 2>/dev/null)"; then
		echo "[codestyle-parity] missing codestyle file: $relative_path" >&2
		exit 1
	fi

	# repo_root is already resolved at this point
	if [[ "$resolved_path" != "$repo_root"/* && "$resolved_path" != "$repo_root" ]]; then
		echo "[codestyle-parity] path traversal detected: $relative_path resolves outside repo root" >&2
		exit 1
	fi

	actual_hash="$(hash_file "$resolved_path")"
	if [[ "$actual_hash" != "$expected_hash" ]]; then
		echo "[codestyle-parity] checksum mismatch: $relative_path" >&2
		echo "  expected: $expected_hash" >&2
		echo "  actual:   $actual_hash" >&2
		exit 1
	fi

	checked=$((checked + 1))
done < "$manifest_path"

if [[ "$checked" -eq 0 ]]; then
	echo "[codestyle-parity] checksum manifest is empty: $manifest_path" >&2
	exit 1
fi

echo "[codestyle-parity] verified $checked codestyle file(s)"
