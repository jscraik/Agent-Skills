from __future__ import annotations

import hashlib
import stat
from pathlib import Path


def is_approved_op_binary(value: str) -> bool:
    return value == "op" or (Path(value).is_absolute() and Path(value).name == "op")


def is_actual_opaque_env_reference(value: str) -> bool:
    """Return whether value names the one runtime stream an op process may open."""
    if value.startswith("~"):
        return False
    try:
        path = Path(value).expanduser()
        expected = Path.home() / ".codex" / ".env"
        return path == expected and not expected.parent.is_symlink() and stat.S_ISFIFO(path.lstat().st_mode)
    except OSError:
        return False


def is_opaque_env_reference(value: str) -> bool:
    """Accept either a runtime stream or its closed receipt-only redaction."""
    return value == "<operator-approved-opaque-env-stream>" or is_actual_opaque_env_reference(value)


def opaque_env_identity_digest(value: str | Path) -> str | None:
    """Return a non-secret identity for the exact approved FIFO inode."""
    try:
        path = Path(value).expanduser()
        metadata = path.lstat()
    except OSError:
        return None
    if not stat.S_ISFIFO(metadata.st_mode):
        return None
    identity = f"{metadata.st_dev}:{metadata.st_ino}:{metadata.st_mode & 0o7777}"
    return f"sha256:{hashlib.sha256(identity.encode('ascii')).hexdigest()}"


def redact_opaque_env_reference(value: str) -> str:
    if not is_opaque_env_reference(value):
        raise ValueError("cloud execution requires an operator-approved opaque environment stream")
    return "<operator-approved-opaque-env-stream>"
