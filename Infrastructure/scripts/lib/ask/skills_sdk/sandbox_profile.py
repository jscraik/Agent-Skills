from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
from typing import Any

from ask.skills_sdk.schema_validation import validate_payload_against_schema


SANDBOX_PROFILE_SCHEMA_VERSION = "skills-sdk.sandbox-profile.v0"
SANDBOX_PROFILE_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/sandbox-profile.v0.schema.json"
)
SANDBOX_PROFILE_RECEIPT_SCHEMA_VERSION = "skills-sdk.sandbox-profile-receipt.v0"
SANDBOX_PROFILE_RECEIPT_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/sandbox-profile-receipt.v0.schema.json"
)
SANDBOX_PROFILE_ACCEPTANCE_TRACE = ["FR-008", "FR-010", "SA-004", "SA-007", "SEC-001", "VP-021"]
SANDBOX_PROFILE_SCHEMA_PATH = Path("Infrastructure/config/schemas/skills-sdk/sandbox-profile.v0.schema.json")
RISK_TIERS = {"low", "medium", "high", "privileged", "published"}
DEFAULT_POLICIES = {"deny", "allow"}
_HOME_DIR = os.path.expanduser("~")
_SHELL_PROGRAMS = {"bash", "dash", "fish", "ksh", "pwsh", "powershell", "sh", "tcsh", "zsh"}


class SandboxProfileError(ValueError):
    """Raised when a sandbox profile cannot be loaded or validated."""

    def __init__(self, message: str, *, receipt: dict[str, Any]) -> None:
        super().__init__(message)
        self.message = message
        self.receipt = receipt


def _digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _repo_relative(repo_root: Path, path: Path) -> str:
    resolved_root = repo_root.resolve()
    resolved_path = path.resolve()
    try:
        return resolved_path.relative_to(resolved_root).as_posix()
    except ValueError:
        return resolved_path.as_posix()


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "profile file does not exist"
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"profile file could not be read: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"profile file is not valid JSON: {exc}"
    if not isinstance(payload, dict):
        return None, "profile root must be a JSON object"
    return payload, None


def _check(
    check_id: str,
    status: str,
    severity: str,
    message: str,
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": status,
        "severity": severity,
        "message": message,
        "evidence": evidence or [],
    }


def _path_is_broad(path: str) -> bool:
    normalized_path = path.strip()
    if normalized_path in {"", ".", "./", "*", "/", "/Users", _HOME_DIR, "~"}:
        return True
    if any(marker in normalized_path for marker in ("*", "?", "[")):
        return True
    parsed = PurePosixPath(normalized_path)
    first_part = parsed.parts[0] if parsed.parts else ""
    return parsed.is_absolute() or first_part.startswith("~") or any(part == ".." for part in parsed.parts)


def _object_field(profile: dict[str, Any], key: str) -> dict[str, Any]:
    value = profile.get(key)
    return value if isinstance(value, dict) else {}


def _list_field(parent: dict[str, Any], key: str) -> list[Any]:
    value = parent.get(key)
    return value if isinstance(value, list) else []


def _broad_paths(paths: list[Any]) -> list[str]:
    return [str(path) for path in paths if isinstance(path, str) and _path_is_broad(path)]


def _filesystem_read_check(profile: dict[str, Any]) -> dict[str, Any]:
    broad_reads = _broad_paths(_list_field(_object_field(profile, "filesystem"), "read"))
    return _check(
        "filesystem_read_scope",
        "pass" if not broad_reads else "blocker",
        "blocker",
        "Sandbox profile read paths must be repo-relative and bounded.",
        broad_reads,
    )


def _filesystem_write_check(profile: dict[str, Any]) -> dict[str, Any]:
    filesystem = _object_field(profile, "filesystem")
    write_paths = _list_field(filesystem, "write")
    broad_writes = _broad_paths(write_paths)
    allowed = not broad_writes and write_paths == [] and filesystem.get("temp_write") is True
    return _check(
        "filesystem_write_scope",
        "pass" if allowed else "blocker",
        "blocker",
        "Sandbox profile must not allow persistent writes before an adapter is approved.",
        broad_writes or [f"write_count:{len(write_paths)}", f"temp_write:{filesystem.get('temp_write')!s}"],
    )


def _deny_by_default_check(profile: dict[str, Any]) -> dict[str, Any]:
    return _check(
        "deny_by_default",
        "pass" if profile.get("default_policy") == "deny" else "blocker",
        "blocker",
        "Sandbox profiles must be deny-by-default.",
        [f"default_policy:{profile.get('default_policy')!s}"],
    )


def _network_check(profile: dict[str, Any]) -> dict[str, Any]:
    network = _object_field(profile, "network")
    return _check("network_egress_denied", "pass" if network.get("egress") == "deny" else "blocker", "blocker", "Sandbox profile must deny network egress until a provider adapter is approved.", [f"egress:{network.get('egress')!s}"])


def _environment_check(profile: dict[str, Any]) -> dict[str, Any]:
    environment = _object_field(profile, "environment")
    return _check("environment_inheritance_denied", "pass" if environment.get("inherit") is False else "blocker", "blocker", "Sandbox profile must not inherit ambient environment variables.", [f"inherit:{environment.get('inherit')!s}"])


def _command_allowlist_check(profile: dict[str, Any]) -> dict[str, Any]:
    commands = _object_field(profile, "commands")
    allowlist = _list_field(commands, "allow")
    shell_allowed = commands.get("shell_allowed") is True
    shell_programs = [
        str(command)
        for command in allowlist
        if isinstance(command, str) and PurePosixPath(command.strip()).name.lower() in _SHELL_PROGRAMS
    ]
    allowed = bool(allowlist) and (shell_allowed or not shell_programs)
    evidence = shell_programs if shell_programs else [f"allow_count:{len(allowlist)}"]
    return _check(
        "command_allowlist_present",
        "pass" if allowed else "blocker",
        "blocker",
        "Sandbox profile must name bounded non-shell command programs when shell execution is disabled.",
        evidence,
    )


def _shell_disabled_check(profile: dict[str, Any]) -> dict[str, Any]:
    commands = _object_field(profile, "commands")
    return _check("shell_disabled", "pass" if commands.get("shell_allowed") is False else "blocker", "blocker", "Sandbox profile must disable shell execution until the adapter contract is approved.", [f"shell_allowed:{commands.get('shell_allowed')!s}"])


def _adapter_check(profile: dict[str, Any]) -> dict[str, Any]:
    execution = _object_field(profile, "execution")
    passed = execution.get("provider") == "none" and execution.get("adapter") is None
    return _check("adapter_not_selected", "pass" if passed else "blocker", "blocker", "Sandbox profile validation must not select or invoke a sandbox adapter in this slice.", [f"provider:{execution.get('provider')!s}", f"adapter:{execution.get('adapter')!s}"])


def _semantic_checks(profile: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _deny_by_default_check(profile),
        _filesystem_read_check(profile),
        _filesystem_write_check(profile),
        _network_check(profile),
        _environment_check(profile),
        _command_allowlist_check(profile),
        _shell_disabled_check(profile),
        _adapter_check(profile),
    ]


def _blocked_receipt(
    *,
    profile_path: str,
    profile_digest: str | None,
    message: str,
    checks: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    blockers = checks or [_check("profile_load", "blocker", "blocker", message, [profile_path])]
    return {
        "schema_version": SANDBOX_PROFILE_RECEIPT_SCHEMA_VERSION,
        "schema_uri": SANDBOX_PROFILE_RECEIPT_SCHEMA_URI,
        "status": "blocked",
        "profile_path": profile_path,
        "profile_digest": profile_digest,
        "profile_id": None,
        "risk_tier": None,
        "default_policy": None,
        "checks": blockers,
        "blockers": blockers,
        "warnings": [],
        "execution_performed": False,
        "adapter_selected": False,
        "mutation_performed": False,
        "acceptance_trace": SANDBOX_PROFILE_ACCEPTANCE_TRACE,
    }


def _enum_or_none(value: object, allowed: set[str]) -> str | None:
    if isinstance(value, str) and value in allowed:
        return value
    return None


def _schema_check(
    repo_root: Path,
    *,
    profile: dict[str, Any],
    profile_label: str,
) -> dict[str, Any]:
    schema = json.loads((repo_root / SANDBOX_PROFILE_SCHEMA_PATH).read_text(encoding="utf-8"))
    schema_result = validate_payload_against_schema(
        profile,
        schema,
        {"sandbox-profile": schema},
        schema_path=SANDBOX_PROFILE_SCHEMA_PATH,
        payload_source=profile_label,
        truth_lane="schema_contract",
    )
    if schema_result.status != "pass":
        return _check(
            "profile_schema",
            "blocker",
            "blocker",
            "Sandbox profile does not match the SDK schema.",
            [diagnostic.message for diagnostic in schema_result.diagnostics],
        )
    return _check("profile_schema", "pass", "blocker", "Sandbox profile matches the SDK schema.", [profile_label])


def _receipt_from_profile(
    profile: dict[str, Any],
    *,
    profile_label: str,
    profile_digest: str | None,
    checks: list[dict[str, Any]],
) -> dict[str, Any]:
    blockers = [check for check in checks if check["status"] == "blocker"]
    return {
        "schema_version": SANDBOX_PROFILE_RECEIPT_SCHEMA_VERSION,
        "schema_uri": SANDBOX_PROFILE_RECEIPT_SCHEMA_URI,
        "status": "blocked" if blockers else "pass",
        "profile_path": profile_label,
        "profile_digest": profile_digest,
        "profile_id": str(profile.get("profile_id")) if isinstance(profile.get("profile_id"), str) else None,
        "risk_tier": _enum_or_none(profile.get("risk_tier"), RISK_TIERS),
        "default_policy": _enum_or_none(profile.get("default_policy"), DEFAULT_POLICIES),
        "checks": checks,
        "blockers": blockers,
        "warnings": [],
        "execution_performed": False,
        "adapter_selected": False,
        "mutation_performed": False,
        "acceptance_trace": SANDBOX_PROFILE_ACCEPTANCE_TRACE,
    }


def build_sandbox_profile_receipt(repo_root: Path, *, profile_path: str) -> dict[str, Any]:
    """Validate a sandbox profile without selecting or invoking a provider adapter."""
    requested_path = Path(profile_path)
    absolute_path = requested_path if requested_path.is_absolute() else repo_root / requested_path
    profile_label = _repo_relative(repo_root, absolute_path)
    profile_digest = _digest_file(absolute_path) if absolute_path.is_file() else None
    profile, load_error = _load_json(absolute_path)
    if load_error:
        receipt = _blocked_receipt(profile_path=profile_label, profile_digest=profile_digest, message=load_error)
        raise SandboxProfileError(load_error, receipt=receipt)

    assert profile is not None
    checks = [_schema_check(repo_root, profile=profile, profile_label=profile_label), *_semantic_checks(profile)]
    return _receipt_from_profile(profile, profile_label=profile_label, profile_digest=profile_digest, checks=checks)
