#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
lock_root="${HARNESS_VALIDATION_LOCK_ROOT:-$repo_root/.cache/validation-locks}"

# Canonicalize paths for safety
canonical_repo_root="$(cd -- "$repo_root" && pwd -P)"
if [[ -d "$lock_root" ]]; then
	canonical_lock_root="$(cd -- "$lock_root" && pwd -P)"
else
	# If lock_root doesn't exist yet, canonicalize its parent
	lock_parent="$(dirname "$lock_root")"
	if [[ -d "$lock_parent" ]]; then
		canonical_lock_parent="$(cd -- "$lock_parent" && pwd -P)"
		canonical_lock_root="$canonical_lock_parent/$(basename "$lock_root")"
	else
		canonical_lock_root="$lock_root"
	fi
fi

# Verify lock_root is under repo_root before iterating
case "$canonical_lock_root" in
	"$canonical_repo_root"/*)
		# Safe: lock_root is a subpath of repo_root
		;;
	*)
		echo "[validation-lock] lock_root is not under repo_root; refusing to validate lock state." >&2
		exit 1
		;;
esac

if [[ ! -d "$lock_root" ]]; then
	echo "[validation-lock] no active validation locks."
	exit 0
fi

metadata_value() {
	local metadata_path="$1"
	local metadata_key="$2"
	python3 - "$metadata_path" "$metadata_key" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
wanted = sys.argv[2]
for raw in path.read_text(encoding="utf-8").splitlines():
    if "=" not in raw:
        continue
    key, value = raw.split("=", 1)
    if key == wanted:
        print(value)
        raise SystemExit(0)
PY
}

status=0
shopt -s nullglob
for lock_dir in "$lock_root"/*.lock; do
	# Skip if not a directory
	if [[ ! -d "$lock_dir" ]]; then
		continue
	fi

	metadata_path="$lock_dir/metadata.env"
	lock_name="$(basename "$lock_dir" .lock)"
	owner_pid=""
	if [[ -f "$metadata_path" ]]; then
		owner_pid="$(metadata_value "$metadata_path" pid)"
	fi
	if [[ "$owner_pid" =~ ^[0-9]+$ ]] && kill -0 "$owner_pid" 2>/dev/null; then
		echo "[validation-lock] active $lock_name validation already running for this repository (pid $owner_pid)." >&2
		status=1
		continue
	fi
	echo "[validation-lock] removing stale $lock_name validation lock."
	# Only call rm -rf on verified directories under canonical_lock_root
	rm -rf "$lock_dir"
done

if [[ "$status" -ne 0 ]]; then
	echo "[validation-lock] stop or wait for active validation lanes before running another pre-push/CI-equivalent gate." >&2
	exit "$status"
fi

echo "[validation-lock] no active validation locks."
