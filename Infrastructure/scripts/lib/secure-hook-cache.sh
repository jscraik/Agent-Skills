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

secure_hook_cache_dir() {
	local cache_dir="$1"
	python3 - "$cache_dir" <<'PY'
import os
import stat
import sys
from pathlib import Path

path = Path(sys.argv[1]).expanduser()
if path.is_symlink():
    raise SystemExit(f"hook cache path must not be a symlink: {path}")
try:
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
except OSError as exc:
    raise SystemExit(f"cannot create hook cache path {path}: {exc}") from exc
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
