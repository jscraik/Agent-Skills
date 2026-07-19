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
	if ! python3 - "$cache_root" <<'PY'
import os
import sys

marker = os.path.join(sys.argv[1], ".agent-skills-hook-cache")
flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
flags |= getattr(os, "O_NOFOLLOW", 0)
fd = os.open(marker, flags, 0o600)
try:
    os.write(fd, b"agent-skills-hook-cache/v1\n")
    os.fsync(fd)
finally:
    os.close(fd)
PY
	then
		rmdir "$cache_root"
		return 1
	fi
	printf '%s\n' "$cache_root"
}

secure_hook_cache_dir() {
	local cache_dir="$1"
	python3 - "$cache_dir" <<'PY'
import os
import stat
import sys
from pathlib import Path
from typing import Optional

MARKER_NAME = ".agent-skills-hook-cache"
MARKER_CONTENT = "agent-skills-hook-cache/v1\n"
path = Path(sys.argv[1]).expanduser()
if not path.is_absolute():
    raise SystemExit(f"hook cache path must be absolute: {path}")

def validate_parent_chain(candidate: Path) -> None:
    """Reject symlinked or attacker-writable existing path components."""
    current = candidate
    while True:
        try:
            metadata = current.lstat()
        except FileNotFoundError:
            current = current.parent
            if current == current.parent:
                break
            continue
        if stat.S_ISLNK(metadata.st_mode):
            raise SystemExit(f"hook cache path component must not be a symlink: {current}")
        if not stat.S_ISDIR(metadata.st_mode):
            raise SystemExit(f"hook cache path component must be a directory: {current}")
        mode = stat.S_IMODE(metadata.st_mode)
        is_sticky = bool(mode & stat.S_ISVTX)
        if mode & 0o022 and not is_sticky:
            raise SystemExit(
                f"hook cache parent must not be group- or world-writable: {current}"
            )
        if current == current.parent:
            break
        current = current.parent

validate_parent_chain(path)

def marker_root(candidate: Path) -> Optional[Path]:
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
path_existed = path.exists() or path.is_symlink()
if path_existed and root is None:
    raise SystemExit(f"existing hook cache path lacks an ownership marker: {path}")
if path_existed and not path.is_dir():
    raise SystemExit(f"hook cache path must be a directory: {path}")
try:
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
except OSError as exc:
    raise SystemExit(f"cannot create hook cache path {path}: {exc}") from exc
validate_parent_chain(path)

if root is None:
    marker = path / MARKER_NAME
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        flags |= getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(marker, flags, 0o600)
        try:
            os.write(fd, MARKER_CONTENT.encode("utf-8"))
            os.fsync(fd)
        finally:
            os.close(fd)
    except FileExistsError:
        root = marker_root(path)
    except OSError as exc:
        raise SystemExit(f"cannot initialize hook cache marker {marker}: {exc}") from exc
    if root is None:
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
