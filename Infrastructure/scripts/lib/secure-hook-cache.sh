#!/usr/bin/env bash

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
