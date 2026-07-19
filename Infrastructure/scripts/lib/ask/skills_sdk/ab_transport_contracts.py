from __future__ import annotations

import hashlib
import os
import pwd
import stat
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator, Sequence, TypeVar


ResultT = TypeVar("ResultT")


def is_approved_op_binary(value: str) -> bool:
    return value == "op" or (Path(value).is_absolute() and Path(value).name == "op")


def approved_op_binary() -> str | None:
    """Resolve the installed 1Password CLI without consulting caller PATH."""
    for candidate in (Path("/opt/homebrew/bin/op"), Path("/usr/local/bin/op")):
        try:
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return str(candidate)
        except OSError:
            continue
    return None


@dataclass(frozen=True)
class ApprovedOpEnvInvocation:
    """A descriptor-bound `op run` boundary for the approved opaque FIFO."""

    op_binary: str
    env_file: Path
    env_fd: int
    auth_stream_identity_digest: str

    @property
    def pass_fds(self) -> tuple[int, ...]:
        return (self.env_fd,)

    def runtime_argv(self, command: Sequence[str]) -> list[str]:
        return [
            self.op_binary,
            "run",
            "--env-file",
            f"/dev/fd/{self.env_fd}",
            "--",
            *command,
        ]

    def receipt_argv(self, command: Sequence[str]) -> list[str]:
        """Return the non-secret shape later redacted into the persisted receipt."""
        return [self.op_binary, "run", "--env-file", str(self.env_file), "--", *command]


def _has_symlink_component(path: Path) -> bool:
    # The account home and its immediate parent define the owned boundary.
    # Do not reject platform-level aliases above that boundary (for example
    # macOS temporary-directory aliases), but never follow an alias into the
    # account home or its `.codex` child.
    return any(candidate.is_symlink() for candidate in (path, path.parent, path.parent.parent))


def _identity_digest(metadata: os.stat_result) -> str:
    identity = f"{metadata.st_dev}:{metadata.st_ino}:{metadata.st_mode & 0o7777}"
    return f"sha256:{hashlib.sha256(identity.encode('ascii')).hexdigest()}"


def operator_account_home() -> Path | None:
    """Return the uid-owned account home without trusting the ambient HOME variable."""
    try:
        return Path(pwd.getpwuid(os.getuid()).pw_dir)
    except (KeyError, OSError):
        return None


def actual_opaque_env_path() -> Path | None:
    """Return the only env stream path an op subprocess may open."""
    home = operator_account_home()
    return None if home is None else home / ".codex" / ".env"


def is_actual_opaque_env_reference(value: str) -> bool:
    """Return whether value names the one runtime stream an op process may open."""
    if value.startswith("~"):
        return False
    try:
        path = Path(value).expanduser()
        expected = actual_opaque_env_path()
        if expected is None:
            return False
        return path == expected and not _has_symlink_component(expected) and stat.S_ISFIFO(path.lstat().st_mode)
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
    return _identity_digest(metadata)


@contextmanager
def approved_op_env_invocation(
    value: str | Path,
    *,
    expected_identity_digest: str | None = None,
) -> Iterator[ApprovedOpEnvInvocation]:
    """Open the approved FIFO once and hand its descriptor to `op`.

    A path-only validation cannot protect the interval between validation and a
    later child opening that path.  Capture a stable FIFO inode with a
    non-blocking, no-follow descriptor instead; any replacement before open is
    rejected by the inode comparison and any replacement after open cannot
    change what the child receives through ``/dev/fd/<n>``.
    """
    path = Path(value)
    if not is_actual_opaque_env_reference(str(path)):
        raise ValueError("cloud execution requires an operator-approved opaque environment stream")
    op_binary = approved_op_binary()
    if op_binary is None:
        raise ValueError("cloud execution requires an approved 1Password CLI binary")

    before = path.lstat()
    flags = os.O_RDONLY | os.O_NONBLOCK
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags)
    try:
        opened = os.fstat(fd)
        if not stat.S_ISFIFO(opened.st_mode):
            raise ValueError("cloud execution auth stream is not a FIFO")
        if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise ValueError("cloud execution auth stream identity changed before descriptor handoff")
        identity = _identity_digest(opened)
        if expected_identity_digest is not None and identity != expected_identity_digest:
            raise ValueError("cloud execution auth stream identity changed before descriptor handoff")
        yield ApprovedOpEnvInvocation(op_binary, path, fd, identity)
    finally:
        os.close(fd)


def run_with_approved_op_env(
    value: str | Path,
    command: Sequence[str],
    operation: Callable[[list[str], tuple[int, ...]], ResultT],
    *,
    expected_identity_digest: str | None = None,
) -> ResultT:
    """Run one operation through a descriptor-bound approved `op` command."""
    with approved_op_env_invocation(
        value, expected_identity_digest=expected_identity_digest,
    ) as invocation:
        return operation(invocation.runtime_argv(command), invocation.pass_fds)


def redact_opaque_env_reference(value: str) -> str:
    if not is_opaque_env_reference(value):
        raise ValueError("cloud execution requires an operator-approved opaque environment stream")
    return "<operator-approved-opaque-env-stream>"
