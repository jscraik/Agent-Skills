#!/usr/bin/env bash
set -euo pipefail

usage() {
	echo "Usage: bash scripts/with-validation-lock.sh <lock-name> -- <command> [args...]" >&2
}

if [[ $# -lt 3 || "$2" != "--" ]]; then
	usage
	exit 2
fi

lock_name="$1"
shift 2

case "$lock_name" in
	*[!a-zA-Z0-9_.-]* | "")
		echo "[validation-lock] invalid lock name: $lock_name" >&2
		exit 2
		;;
esac

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
lock_root="${HARNESS_VALIDATION_LOCK_ROOT:-$repo_root/.cache/validation-locks}"

canonical_repo_root="$(cd -- "$repo_root" && pwd -P)"
if [[ -d "$lock_root" ]]; then
	canonical_lock_root="$(cd -- "$lock_root" && pwd -P)"
else
	lock_parent="$(dirname "$lock_root")"
	if [[ -d "$lock_parent" ]]; then
		canonical_lock_parent="$(cd -- "$lock_parent" && pwd -P)"
		canonical_lock_root="$canonical_lock_parent/$(basename "$lock_root")"
	else
		canonical_lock_root="$lock_root"
	fi
fi

case "$canonical_lock_root" in
	"$canonical_repo_root"/*)
		;;
	*)
		echo "[validation-lock] lock_root is not under repo_root; refusing to acquire validation lock." >&2
		exit 1
		;;
esac

lock_dir="$lock_root/$lock_name.lock"
metadata_path="$lock_dir/metadata.env"

mkdir -p "$lock_root"

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

write_metadata() {
	{
		printf 'pid=%s\n' "$$"
		printf 'repo_root=%q\n' "$repo_root"
		printf 'lock_name=%q\n' "$lock_name"
		printf 'started_at=%q\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
		printf 'command=%q\n' "$*"
	} >"$metadata_path"
}

if mkdir "$lock_dir" 2>/dev/null; then
	write_metadata "$@"
else
	owner_pid=""
	if [[ -f "$metadata_path" ]]; then
		owner_pid="$(metadata_value "$metadata_path" pid)"
	fi
	if [[ "$owner_pid" =~ ^[0-9]+$ ]] && kill -0 "$owner_pid" 2>/dev/null; then
		# Verify process identity to avoid PID recycling false positive
		process_verified=false
		script_basename="$(basename "${BASH_SOURCE[0]}")"

		# Try /proc first (Linux)
		if [[ -r "/proc/$owner_pid/cmdline" ]]; then
			cmdline="$(tr '\0' ' ' < "/proc/$owner_pid/cmdline" 2>/dev/null || echo "")"
			if [[ "$cmdline" == *"$script_basename"* || "$cmdline" == *"$lock_name"* ]]; then
				process_verified=true
			fi
		# Fallback to ps for systems without /proc
		elif command -v ps >/dev/null 2>&1; then
			ps_args="$(ps -p "$owner_pid" -o args= 2>/dev/null || echo "")"
			if [[ "$ps_args" == *"$script_basename"* || "$ps_args" == *"$lock_name"* ]]; then
				process_verified=true
			fi
		else
			# If neither /proc nor ps available, conservatively assume verified
			process_verified=true
		fi

		if [[ "$process_verified" == true ]]; then
			echo "[validation-lock] active $lock_name validation already running for this repository (pid $owner_pid)." >&2
			echo "[validation-lock] Wait for it to finish or stop the stale validation process before starting another $lock_name lane." >&2
			exit 1
		else
			# PID exists but doesn't match expected process - treat as stale/recycled
			echo "[validation-lock] removing stale $lock_name validation lock (pid $owner_pid recycled)." >&2
		fi
	else
		echo "[validation-lock] removing stale $lock_name validation lock." >&2
	fi

	rm -rf "$lock_dir"
	if ! mkdir "$lock_dir" 2>/dev/null; then
		echo "[validation-lock] failed to acquire $lock_name validation lock after stale cleanup." >&2
		exit 1
	fi
	write_metadata "$@"
fi

cleanup() {
	rm -rf "$lock_dir"
}
trap cleanup EXIT INT TERM

"$@"
