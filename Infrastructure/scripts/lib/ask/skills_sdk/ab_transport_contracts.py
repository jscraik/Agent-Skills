from __future__ import annotations

import hashlib
import os
import pwd
import stat
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Sequence


CONFIGS_AUTH_WRAPPER = Path(
    "/Users/jamiecraik/dev/configs/codex/scripts/run-auth-backed.sh"
)
CONFIGS_CODEX_EXEC_WRAPPER = Path(
    "/Users/jamiecraik/dev/configs/codex/scripts/run-codex-exec.sh"
)
OSS_CLOUD_REQUIRED_ENV = "OLLAMA_API_KEY"
OSS_CLOUD_PROFILE = "oss-cloud"
OSS_CLOUD_MODEL = "deepseek-v4-flash:0731-cloud"
OSS_LOCAL_PROFILE = "oss-local"
_OSS_CLOUD_APPROVAL_SETTING = 'approval_policy="on-request"'

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


def configs_auth_wrapper() -> str | None:
    """Return the one reviewed Configs wrapper for Codex secret-bearing children."""
    try:
        # The contract invokes this shell script explicitly through `bash`, so
        # readability as a regular file is sufficient. Requiring an execute
        # bit would reject the canonical checked-in Configs source mode.
        if CONFIGS_AUTH_WRAPPER.is_file() and not CONFIGS_AUTH_WRAPPER.is_symlink():
            return str(CONFIGS_AUTH_WRAPPER)
    except OSError:
        pass
    return None


def is_configs_auth_wrapper(value: str) -> bool:
    return value == str(CONFIGS_AUTH_WRAPPER)


def configs_codex_exec_wrapper() -> str | None:
    """Return the reviewed Configs Codex executor for the OSS-cloud lane."""
    try:
        if CONFIGS_CODEX_EXEC_WRAPPER.is_file() and os.access(CONFIGS_CODEX_EXEC_WRAPPER, os.X_OK):
            return str(CONFIGS_CODEX_EXEC_WRAPPER)
    except OSError:
        pass
    return None


def is_configs_codex_exec_wrapper(value: str) -> bool:
    return value == str(CONFIGS_CODEX_EXEC_WRAPPER)


def configs_oss_cloud_exec_command(command: Sequence[str]) -> list[str]:
    """Translate logical Codex argv into the reviewed cloud executor argv."""
    argv = list(command)
    if argv[:4] != ["codex", "exec", "--profile", OSS_CLOUD_PROFILE]:
        raise ValueError("cloud execution requires the canonical oss-cloud Codex command")
    approval_values = [
        argv[index + 1]
        for index, value in enumerate(argv[:-1])
        if value == "-c" and argv[index + 1] == 'approval_policy="on-request"'
    ]
    legacy_approval = argv.count("--ask-for-approval") == 1 and argv[argv.index("--ask-for-approval") + 1] == "on-request"
    if len(approval_values) + int(legacy_approval) != 1:
        raise ValueError("cloud execution requires on-request approval")
    if argv.count("--sandbox") != 1 or argv[argv.index("--sandbox") + 1] != "read-only":
        raise ValueError("cloud execution requires the read-only sandbox")
    if argv.count("--cd") != 1 or argv.count("--output-last-message") != 1 or argv.count("--json") != 1 or argv[-1] != "-":
        raise ValueError("cloud execution requires canonical SDK evidence arguments")
    return [
        "bash",
        str(CONFIGS_CODEX_EXEC_WRAPPER),
        "--profile",
        OSS_CLOUD_PROFILE,
        "--model",
        OSS_CLOUD_MODEL,
        "--strict-config",
        "-c",
        _OSS_CLOUD_APPROVAL_SETTING,
        "--cd",
        argv[argv.index("--cd") + 1],
        "--sandbox",
        "read-only",
        "--ephemeral",
        "--json",
        "--output-last-message",
        argv[argv.index("--output-last-message") + 1],
        "-",
    ]


def configs_oss_local_exec_command(command: Sequence[str]) -> list[str]:
    """Run the local lane through the disposable Configs executor.

    The installed Codex app-server can reject a direct in-process client from
    the managed sandbox.  Configs' executor retries that exact command in a
    disposable CODEX_HOME while keeping the logical receipt command as
    ``codex exec``.
    """
    argv = list(command)
    if argv[:4] != ["codex", "exec", "--profile", OSS_LOCAL_PROFILE]:
        raise ValueError("local execution requires the canonical oss-local Codex command")
    if argv.count("--sandbox") != 1 or argv[argv.index("--sandbox") + 1] != "read-only":
        raise ValueError("local execution requires the read-only sandbox")
    if argv.count("--cd") != 1 or argv.count("--output-last-message") != 1 or argv.count("--json") != 1 or argv[-1] != "-":
        raise ValueError("local execution requires canonical SDK evidence arguments")
    wrapper = configs_codex_exec_wrapper()
    if wrapper is None:
        raise ValueError("local execution requires the Configs Codex executor")
    return [
        "bash", wrapper,
        "--profile", OSS_LOCAL_PROFILE,
        "--sandbox", "read-only",
        "--ephemeral",
        *argv[4:6],
        "--cd", argv[argv.index("--cd") + 1],
        "--json",
        "--output-last-message", argv[argv.index("--output-last-message") + 1],
        "-",
    ]


@dataclass(frozen=True)
class ConfigsAuthBackedInvocation:
    """Receipt-safe command shape for one Configs-owned FIFO consumption."""

    wrapper: str
    env_file: Path
    auth_stream_identity_digest: str

    def runtime_argv(self, command: Sequence[str]) -> list[str]:
        return [
            "bash",
            self.wrapper,
            "--env-file",
            str(self.env_file),
            "--require-env",
            OSS_CLOUD_REQUIRED_ENV,
            "--",
            *command,
        ]

    def receipt_argv(self, command: Sequence[str]) -> list[str]:
        return self.runtime_argv(command)


@contextmanager
def configs_auth_backed_invocation(
    value: str | Path,
    *,
    expected_identity_digest: str | None = None,
) -> Iterator[ConfigsAuthBackedInvocation]:
    """Bind one child command to the reviewed Configs FIFO wrapper.

    The wrapper validates and consumes the Desktop-owned FIFO itself. This
    consumer checks its non-secret identity immediately before constructing the
    child command so a stale plan cannot silently use a replaced mount.
    """
    path = Path(value)
    if not is_actual_opaque_env_reference(str(path)):
        raise ValueError("cloud execution requires an operator-approved opaque environment stream")
    wrapper = configs_auth_wrapper()
    if wrapper is None:
        raise ValueError("cloud execution requires the Configs auth-backed wrapper")
    identity = opaque_env_identity_digest(path)
    if identity is None or (
        expected_identity_digest is not None and identity != expected_identity_digest
    ):
        raise ValueError("cloud execution auth stream identity changed before wrapper start")
    yield ConfigsAuthBackedInvocation(wrapper, path, identity)


def redact_opaque_env_reference(value: str) -> str:
    if not is_opaque_env_reference(value):
        raise ValueError("cloud execution requires an operator-approved opaque environment stream")
    return "<operator-approved-opaque-env-stream>"
