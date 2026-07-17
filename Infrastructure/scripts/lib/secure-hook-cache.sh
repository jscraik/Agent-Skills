#!/usr/bin/env bash

validate_hook_cache_path() {
	local cache_dir="$1"
	local repo_root="$2"
	local git_common_dir="$3"
	python3 - "$cache_dir" "$repo_root" "$git_common_dir" <<'PY'
import sys
from pathlib import Path

raw_path = Path(sys.argv[1])
if not raw_path.is_absolute():
    raise SystemExit(f"hook cache path must be absolute: {raw_path}")
path = raw_path.resolve(strict=False)
boundaries = (Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve())
for boundary in boundaries:
    if path == boundary or boundary in path.parents:
        raise SystemExit(f"hook cache path must be outside repository metadata: {path}")
print(path)
PY
}

new_hook_cache_root() {
	local tmp_dir="${1:-${TMPDIR:-/tmp}}"
	if [[ ! -d "$tmp_dir" || ! -w "$tmp_dir" ]]; then
		if [[ -d "/private/tmp" && -w "/private/tmp" ]]; then
			tmp_dir="/private/tmp"
		else
			tmp_dir="/tmp"
		fi
	fi
	local cache_root
	cache_root="$(mktemp -d "${tmp_dir%/}/agent-skills-hook-cache.XXXXXX")" || return
	printf '%s\n' 'agent-skills-hook-cache/v1' > "$cache_root/.agent-skills-hook-cache"
	chmod 0600 "$cache_root/.agent-skills-hook-cache"
	printf '%s\n' "$cache_root"
}

secure_hook_cache_dir() {
	local cache_dir="$1"
	python3 - "$cache_dir" <<'PY'
import os
import stat
import sys
from pathlib import Path

MARKER_NAME = ".agent-skills-hook-cache"
MARKER_CONTENT = "agent-skills-hook-cache/v1\n"
path = Path(sys.argv[1]).expanduser()
if not path.is_absolute():
    raise SystemExit(f"hook cache path must be absolute: {path}")
if path.is_symlink():
    raise SystemExit(f"hook cache path must not be a symlink: {path}")

def marker_root(candidate: Path) -> Path | None:
    for parent in (candidate, *candidate.parents):
        marker = parent / MARKER_NAME
        if marker.is_symlink():
            raise SystemExit(f"hook cache marker must not be a symlink: {marker}")
        if not marker.exists():
            continue
        metadata = marker.lstat()
        if not stat.S_ISREG(metadata.st_mode):
            raise SystemExit(f"hook cache marker must be a regular file: {marker}")
        if metadata.st_uid != os.getuid():
            raise SystemExit(f"hook cache marker must be owned by uid {os.getuid()}: {marker}")
        if marker.read_text(encoding="utf-8") != MARKER_CONTENT:
            raise SystemExit(f"hook cache marker has unexpected contents: {marker}")
        if stat.S_IMODE(metadata.st_mode) != 0o600:
            marker.chmod(0o600)
        return parent
    return None

root = marker_root(path)
path_existed = path.exists()
if path_existed and root is None:
    raise SystemExit(f"existing hook cache path lacks an ownership marker: {path}")
if path_existed and not path.is_dir():
    raise SystemExit(f"hook cache path must be a directory: {path}")
try:
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
except OSError as exc:
    raise SystemExit(f"cannot create hook cache path {path}: {exc}") from exc

if root is None:
    marker = path / MARKER_NAME
    try:
        marker.write_text(MARKER_CONTENT, encoding="utf-8")
        marker.chmod(0o600)
    except OSError as exc:
        raise SystemExit(f"cannot initialize hook cache marker {marker}: {exc}") from exc
    root = path

metadata = path.lstat()
if not stat.S_ISDIR(metadata.st_mode):
    raise SystemExit(f"hook cache path must be a directory: {path}")
if metadata.st_uid != os.getuid():
    raise SystemExit(f"hook cache path must be owned by uid {os.getuid()}: {path}")
path.chmod(0o700)
if stat.S_IMODE(path.lstat().st_mode) != 0o700:
    raise SystemExit(f"hook cache path must have mode 0700: {path}")
PY
}
