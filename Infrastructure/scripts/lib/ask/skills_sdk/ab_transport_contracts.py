from __future__ import annotations

import stat
from pathlib import Path


def is_approved_op_binary(value: str) -> bool:
    return value == "op" or (Path(value).is_absolute() and Path(value).name == "op")


def is_opaque_env_reference(value: str) -> bool:
    if value == "<operator-approved-opaque-env-stream>":
        return True
    if value.startswith("~"):
        return False
    try:
        path = Path(value).expanduser()
        return path.name == ".env" and path.parent.name == ".codex" and stat.S_ISFIFO(path.lstat().st_mode)
    except OSError:
        return False


def redact_opaque_env_reference(value: str) -> str:
    if not is_opaque_env_reference(value):
        raise ValueError("cloud execution requires an operator-approved opaque environment stream")
    return "<operator-approved-opaque-env-stream>"
