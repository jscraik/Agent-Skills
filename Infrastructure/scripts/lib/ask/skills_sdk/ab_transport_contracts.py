from __future__ import annotations

import stat
from pathlib import Path


def is_opaque_env_reference(value: str) -> bool:
    if value == "<operator-approved-opaque-env-stream>":
        return True
    try:
        path = Path(value).expanduser()
        return path.name == ".env" and path.parent.name == ".codex" and stat.S_ISFIFO(path.lstat().st_mode)
    except OSError:
        return False

