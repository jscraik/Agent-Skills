#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import stat
import subprocess
import sys
import tempfile
import time
import tomllib
import re
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
LIB_DIR = SCRIPT_DIR.parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from check_oss_local_smoke_output import _findings  # noqa: E402  # reason: local script-path bootstrap; issue: PR-386; expires: 2026-12-31; ADR: source-checkout imports
from ask.skills_sdk.ab_transport_contracts import (  # noqa: E402
    CONFIGS_AUTH_WRAPPER,
    CONFIGS_CODEX_EXEC_WRAPPER,
)


EXPECTED_MODEL = "deepseek-v4-flash:cloud"
EXPECTED_PROVIDER = "ollama-cloud"
DEFAULT_PROFILE_SOURCE = Path.home() / ".codex" / "oss-cloud.config.toml"
DEFAULT_AUTH_ENV_FILE = Path.home() / ".codex" / ".env"
DEFAULT_AUTH_WRAPPER = CONFIGS_AUTH_WRAPPER
DEFAULT_CODEX_EXEC_WRAPPER = CONFIGS_CODEX_EXEC_WRAPPER
DEFAULT_MARKER = "CODEX_OSS_CLOUD_OK"
CLOUD_SMOKE_MAX_TOKENS_USED = 20000
CLOUD_SMOKE_NON_BLOCKING_CODES = frozenset({"codex_runtime_metadata_fallback"})
VALUE_BLIND_FINDING_MESSAGES = (
    ("oss_cloud_profile_missing", "oss-cloud profile source must be a regular file."),
    ("oss_cloud_model_mismatch", "The reviewed oss-cloud model did not match."),
    ("oss_cloud_provider_mismatch", "The reviewed oss-cloud provider did not match."),
    ("oss_cloud_marker_not_allowlisted", "The bounded cloud smoke requires its fixed marker."),
    ("oss_cloud_auth_stream_missing", "Desktop-owned OLLAMA_API_KEY FIFO is required."),
    ("oss_cloud_auth_wrapper_missing", "Configs auth wrapper is required for oss-cloud."),
    ("oss_cloud_exec_wrapper_missing", "Configs Codex wrapper is required for oss-cloud."),
    ("oss_cloud_auth_wrapper_identity_mismatch", "The supplied auth wrapper must be canonical."),
    ("oss_cloud_exec_wrapper_identity_mismatch", "The supplied Codex wrapper must be canonical."),
    ("codex_runtime_metadata_fallback", "Codex reported fallback metadata."),
    ("codex_runtime_visible_thinking", "Model output exposed a thinking trace."),
    ("codex_runtime_token_budget_exceeded", "The smoke transcript exceeded its token budget."),
    ("oss_cloud_secret_output_observed", "Captured smoke output matched a secret-shaped marker."),
    ("oss_cloud_smoke_exit_nonzero", "Codex exited with a non-zero status."),
    ("oss_cloud_smoke_marker_mismatch", "Cloud smoke marker did not match."),
)
# Match shell, plain-text, and JSON-style diagnostics without capturing or
# printing the value. Provider-prefixed names are matched as a whole key so
# `OPENAI_API_KEY=...` is blocked as well as `token=...`.
SECRET_OUTPUT_RE = re.compile(
    r'(?im)(?:\bauthorization\b\s*:\s*bearer\s+\S+|["\']?(?:[A-Z][A-Z0-9]*(?:_API_KEY|_SECRET(?:_ACCESS_KEY)?|_TOKEN)|\b(?:api|access)[_-]?key|token|secret)'
    r'\b["\']?\s*[:=]\s*["\']?\S+)'
)
ISOLATED_CODEX_CONFIG = f'''model = "{EXPECTED_MODEL}"
model_provider = "{EXPECTED_PROVIDER}"
approval_policy = "on-request"
approvals_reviewer = "auto_review"
default_permissions = "readonly-net"
model_reasoning_effort = "high"
model_reasoning_summary = "concise"
web_search = "cached"

[features]
plugins = false
skill_mcp_dependency_install = false
apps = false
code_mode = false
code_mode_only = false

[permissions.readonly-net]
extends = ":read-only"
description = "Bounded read-only cloud smoke profile."

[permissions.readonly-net.network]
enabled = true
allow_local_binding = false

[permissions.readonly-net.network.domains]
"ollama.com" = "allow"

[model_providers.ollama-cloud]
name = "Ollama Cloud"
base_url = "https://ollama.com/v1"
wire_api = "responses"
env_key = "OLLAMA_API_KEY"
'''


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a bounded oss-cloud Codex marker smoke through 1Password.")
    parser.add_argument("--profile-source", default=str(DEFAULT_PROFILE_SOURCE))
    parser.add_argument("--env-file", default=str(DEFAULT_AUTH_ENV_FILE))
    parser.add_argument("--auth-wrapper", default=str(DEFAULT_AUTH_WRAPPER))
    parser.add_argument("--codex-exec-wrapper", default=str(DEFAULT_CODEX_EXEC_WRAPPER))
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--marker", default=DEFAULT_MARKER)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--json", action="store_true")
    return parser


def _profile_value(path: Path, key: str) -> str | None:
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None
    value = payload.get(key)
    return value if isinstance(value, str) else None


def _profile_findings(path: Path) -> list[dict[str, str]]:
    try:
        profile = path.resolve(strict=True)
    except OSError:
        profile = path
    if not profile.is_file():
        return [{"code": "oss_cloud_profile_missing", "message": "oss-cloud profile source must be a regular file."}]
    findings: list[dict[str, str]] = []
    if _profile_value(profile, "model") != EXPECTED_MODEL:
        findings.append({"code": "oss_cloud_model_mismatch", "message": f"Expected model {EXPECTED_MODEL!r}."})
    if _profile_value(profile, "model_provider") != EXPECTED_PROVIDER:
        findings.append({"code": "oss_cloud_provider_mismatch", "message": f"Expected provider {EXPECTED_PROVIDER!r}."})
    return findings


def _approved_env_file(path: Path) -> Path | None:
    if path.is_symlink():
        return None
    try:
        mode = path.stat().st_mode
    except OSError:
        return None
    return path if stat.S_ISFIFO(mode) else None


def _canonical_wrapper_identity(path: str, expected: Path) -> bool:
    """Return whether a supplied wrapper resolves to the reviewed identity."""
    try:
        return Path(path).expanduser().resolve() == expected.resolve()
    except OSError:
        return False


def _wrapper_findings(args: argparse.Namespace) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path, expected, missing_code, identity_code, label in (
        (Path(args.auth_wrapper), DEFAULT_AUTH_WRAPPER, "oss_cloud_auth_wrapper_missing", "oss_cloud_auth_wrapper_identity_mismatch", "auth"),
        (Path(args.codex_exec_wrapper), DEFAULT_CODEX_EXEC_WRAPPER, "oss_cloud_exec_wrapper_missing", "oss_cloud_exec_wrapper_identity_mismatch", "Codex"),
    ):
        try:
            executable = (
                path.is_file() and bool(path.stat().st_mode & stat.S_IXUSR)
                if label == "Codex"
                else True
            )
        except OSError:
            findings.append({
                "code": missing_code,
                "message": f"Configs {label} wrapper is required for oss-cloud.",
            })
            continue
        if not path.is_file() or path.is_symlink() or not executable:
            findings.append({"code": missing_code, "message": f"Configs {label} wrapper is required for oss-cloud."})
        elif not _canonical_wrapper_identity(str(path), expected):
            findings.append({"code": identity_code, "message": f"The supplied {label} wrapper must be the canonical Configs wrapper."})
    return findings


def _auth_source(path: Path) -> str:
    if _approved_env_file(path) is None:
        return "missing_or_invalid"
    return "1password_desktop_fifo"


def _paths(output_dir: str | None) -> dict[str, Path]:
    root = Path(output_dir) if output_dir else Path(tempfile.mkdtemp(prefix="ask-oss-cloud-smoke."))
    root = root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    return {
        "root": root,
        "codex_home": root / "codex-home",
        "stdout": root / "stdout.txt",
        "stderr": root / "stderr.txt",
        "last_message": root / "last-message.txt",
    }


def _isolated_codex_home(profile: Path, paths: dict[str, Path]) -> Path:
    """Prepare a context-minimal Codex home for the bounded marker call."""
    codex_home = paths["codex_home"]
    codex_home.mkdir(parents=True, exist_ok=True)
    # The operator profile is admission input, not executable context.  Write
    # only the fixed, allowlisted cloud profile so disabled MCPs, project
    # instructions, and other workstation settings cannot cross the boundary.
    profile.resolve(strict=True)
    (codex_home / "oss-cloud.config.toml").write_text(ISOLATED_CODEX_CONFIG, encoding="utf-8")
    (codex_home / "config.toml").write_text(ISOLATED_CODEX_CONFIG, encoding="utf-8")
    return codex_home


def _command(args: argparse.Namespace, paths: dict[str, Path], env_file: Path) -> list[str]:
    codex_home = _isolated_codex_home(Path(args.profile_source).expanduser(), paths)
    return [
        "bash",
        args.auth_wrapper,
        "--env-file",
        str(env_file),
        "--require-env",
        "OLLAMA_API_KEY",
        "--",
        "env",
        "-u",
        "CODEX_CONFIG_HOME",
        f"CODEX_HOME={codex_home}",
        "bash",
        args.codex_exec_wrapper,
        "--profile",
        "oss-cloud",
        "--strict-config",
        "-c",
        'approval_policy="on-request"',
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--ephemeral",
        "--model",
        EXPECTED_MODEL,
        f"Reply exactly {args.marker}",
    ]


def _run(command: list[str], paths: dict[str, Path], args: argparse.Namespace) -> tuple[int, float]:
    started = time.monotonic()
    with (
        paths["stdout"].open("w", encoding="utf-8") as stdout,
        paths["stderr"].open("w", encoding="utf-8") as stderr,
        tempfile.TemporaryDirectory(prefix="ask-oss-cloud-smoke-work.") as work_dir,
    ):
        # Run from an empty temporary directory rather than the consuming
        # repository. Codex discovers AGENTS.md and project context from cwd
        # parents, so honoring the caller's work directory would invalidate
        # the context-minimal smoke claim.
        try:
            completed = subprocess.run(
                command,
                cwd=work_dir,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                check=False,
                text=True,
                timeout=args.timeout_seconds,
            )
            return completed.returncode, round(time.monotonic() - started, 3)
        except subprocess.TimeoutExpired:
            return 124, round(time.monotonic() - started, 3)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def _secret_observation(paths: dict[str, Path], *, executed: bool) -> dict[str, Any]:
    if not executed:
        return {"status": "unavailable", "source": "captured_output_scan", "redacted": True}
    output = "\n".join((_read(paths["stdout"]), _read(paths["stderr"])))
    observed = bool(SECRET_OUTPUT_RE.search(output))
    return {
        "status": "blocked" if observed else "clear",
        "source": "captured_output_scan",
        "redacted": True,
    }


def _receipt(
    args: argparse.Namespace, paths: dict[str, Path], profile: Path, findings: list[dict[str, str]], *,
    command: list[str] | None, exit_code: int | None, duration_seconds: float, provider_invoked: bool,
    runtime_warnings: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    warnings = runtime_warnings if runtime_warnings is not None else _runtime_findings(args, paths, findings, command, exit_code)
    secret_observation = _secret_observation(paths, executed=command is not None)
    return {
        "schema_version": "skills-sdk.oss-cloud-smoke-run.v0",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if provider_invoked and not findings else "blocked",
        "lane": "oss-cloud",
        "codex_profile": "oss-cloud",
        # Keep profile mismatches as typed findings without echoing arbitrary
        # profile values into the value-blind receipt.
        "model": EXPECTED_MODEL,
        "model_provider": EXPECTED_PROVIDER,
        "auth_source": _auth_source(Path(args.env_file).expanduser()),
        "provider_invoked": provider_invoked,
        "command": _redacted_command(executed=command is not None),
        "execution_argv": _redacted_command(executed=command is not None),
        "duration_seconds": duration_seconds,
        "exit_code": exit_code,
        "marker": DEFAULT_MARKER,
        "stdout_path": "<captured-stdout>",
        "stderr_path": "<captured-stderr>",
        "last_message_path": "<captured-last-message>",
        "warnings": warnings,
        "findings": findings,
        "secret_observation": secret_observation,
        "secret_value_observed": secret_observation["status"] == "blocked",
    }


def _runtime_findings(
    args: argparse.Namespace, paths: dict[str, Path], findings: list[dict[str, str]],
    command: list[str] | None, exit_code: int | None,
) -> list[dict[str, str]]:
    if command is None:
        return []
    runtime_findings = _findings(
        "\n".join((_read(paths["stdout"]), _read(paths["stderr"]))), CLOUD_SMOKE_MAX_TOKENS_USED,
    )
    if SECRET_OUTPUT_RE.search("\n".join((_read(paths["stdout"]), _read(paths["stderr"])) )):
        runtime_findings.append({"code": "oss_cloud_secret_output_observed", "message": "Captured smoke output matched a redacted secret-shaped marker."})
    warnings = [item for item in runtime_findings if item["code"] in CLOUD_SMOKE_NON_BLOCKING_CODES]
    # Promote every other runtime finding, including secret-shaped output, into
    # the blocking findings before either raw or public receipts are built.
    runtime_blockers = [item for item in runtime_findings if item["code"] not in CLOUD_SMOKE_NON_BLOCKING_CODES]
    findings.extend(runtime_blockers)
    if exit_code != 0:
        findings.append({"code": "oss_cloud_smoke_exit_nonzero", "message": f"Codex exited with {exit_code}."})
    if _read(paths["stdout"]).strip() != args.marker:
        findings.append({"code": "oss_cloud_smoke_marker_mismatch", "message": "Cloud smoke marker did not match."})
    return warnings


def _redacted_command(*, executed: bool) -> list[str] | None:
    if not executed:
        return None
    # Receipts are evidence, not a replay channel. Emit the fixed reviewed
    # command shape rather than echoing operator-controlled argv values, which
    # could include a secret-shaped marker or path. The actual child still
    # runs ``command``; this projection only governs the persisted receipt.
    return [
        "bash",
        # Keep these receipt tokens literal and non-identifying. The identity
        # contract validates the actual child argv before execution; the public
        # receipt must not carry workstation paths into the logging sink.
        "<configs-auth-wrapper>",
        "--env-file",
        "<operator-approved-opaque-env-stream>",
        "--require-env",
        "OLLAMA_API_KEY",
        "--",
        "env",
        "-u",
        "CODEX_CONFIG_HOME",
        "CODEX_HOME=<isolated-codex-home>",
        "bash",
        "<configs-codex-exec-wrapper>",
        "--profile",
        "oss-cloud",
        "--strict-config",
        "-c",
        'approval_policy="on-request"',
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--ephemeral",
        "--model",
        EXPECTED_MODEL,
        f"Reply exactly {DEFAULT_MARKER}",
    ]


def _value_blind_findings(items: list[dict[str, str]]) -> list[dict[str, str]]:
    """Project findings to fixed messages before JSON reaches stdout."""
    projected: list[dict[str, str]] = []
    for known_code, message in VALUE_BLIND_FINDING_MESSAGES:
        if any(item.get("code") == known_code for item in items):
            projected.append({"code": known_code, "message": message})
    if items and not projected:
        projected.append({
            "code": "unclassified_smoke_finding",
            "message": "An unclassified smoke finding was observed.",
        })
    return projected


def _safe_secret_status(secret_output_observed: bool, command_present: bool) -> str:
    if secret_output_observed:
        return "blocked"
    return "clear" if command_present else "unavailable"


def _value_blind_status(provider_invoked: bool, findings: list[dict[str, str]]) -> str:
    if provider_invoked and not findings:
        return "pass"
    return "blocked"


def _value_blind_receipt(
    *,
    env_file: Path,
    findings: list[dict[str, str]],
    warnings: list[dict[str, str]],
    command_present: bool,
    exit_code: int | None,
    duration_seconds: float,
    provider_invoked: bool,
    secret_output_observed: bool,
) -> dict[str, Any]:
    safe_secret_status = _safe_secret_status(secret_output_observed, command_present)
    return {
        "schema_version": "skills-sdk.oss-cloud-smoke-run.v0",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "status": _value_blind_status(provider_invoked, findings),
        "lane": "oss-cloud",
        "codex_profile": "oss-cloud",
        "model": EXPECTED_MODEL,
        "model_provider": EXPECTED_PROVIDER,
        "auth_source": _auth_source(env_file),
        "provider_invoked": provider_invoked,
        "command": _redacted_command(executed=command_present),
        "execution_argv": _redacted_command(executed=command_present),
        "duration_seconds": duration_seconds,
        "exit_code": exit_code,
        "marker": DEFAULT_MARKER,
        "stdout_path": "<captured-stdout>",
        "stderr_path": "<captured-stderr>",
        "last_message_path": "<captured-last-message>",
        "warnings": warnings,
        "findings": findings,
        "secret_observation": {
            "status": safe_secret_status,
            "source": "captured_output_scan",
            "redacted": True,
        },
        "secret_value_observed": safe_secret_status == "blocked",
    }


def _run_smoke(
    args: argparse.Namespace,
    paths: dict[str, Path],
    profile: Path,
    findings: list[dict[str, str]],
    env_file: Path,
) -> tuple[dict[str, Any], list[dict[str, str]], list[str] | None, int | None, float, bool]:
    if findings:
        receipt = _receipt(args, paths, profile, findings, command=None, exit_code=None, duration_seconds=0.0, provider_invoked=False)
        return receipt, [], None, None, 0.0, False
    command = _command(args, paths, env_file)
    exit_code, duration_seconds = _run(command, paths, args)
    runtime_warnings = _runtime_findings(args, paths, findings, command, exit_code)
    receipt = _receipt(
        args,
        paths,
        profile,
        findings,
        command=command,
        exit_code=exit_code,
        duration_seconds=duration_seconds,
        provider_invoked=True,
        runtime_warnings=runtime_warnings,
    )
    return receipt, runtime_warnings, command, exit_code, duration_seconds, True


def _public_receipt(
    args: argparse.Namespace,
    findings: list[dict[str, str]],
    runtime_warnings: list[dict[str, str]],
    command: list[str] | None,
    exit_code: int | None,
    duration_seconds: float,
    provider_invoked: bool,
) -> dict[str, Any]:
    public_findings = _value_blind_findings(findings)
    return _value_blind_receipt(
        env_file=Path(args.env_file).expanduser(),
        findings=public_findings,
        warnings=_value_blind_findings(runtime_warnings),
        command_present=command is not None,
        exit_code=exit_code,
        duration_seconds=duration_seconds,
        provider_invoked=provider_invoked,
        secret_output_observed=any(
            item.get("code") == "oss_cloud_secret_output_observed"
            for item in public_findings
        ),
    )


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.timeout_seconds < 1:
        raise SystemExit("--timeout-seconds must be positive")
    profile = Path(args.profile_source).expanduser()
    paths = _paths(args.output_dir)
    findings = _profile_findings(profile)
    if args.marker != DEFAULT_MARKER:
        findings.append({
            "code": "oss_cloud_marker_not_allowlisted",
            "message": "The bounded cloud smoke requires its fixed marker.",
        })
    env_file = _approved_env_file(Path(args.env_file).expanduser())
    if env_file is None:
        findings.append({"code": "oss_cloud_auth_stream_missing", "message": "Desktop-owned OLLAMA_API_KEY FIFO is required."})
    findings.extend(_wrapper_findings(args))
    receipt, runtime_warnings, command, exit_code, duration_seconds, provider_invoked = _run_smoke(
        args, paths, profile, findings, env_file or Path(args.env_file).expanduser()
    )
    # The JSON path is a value-blind, fixed-shape receipt. Projecting explicit
    # constants and allowlisted fields keeps captured stdout/stderr out of the
    # logging sink even when a child process emits secret-shaped text.
    public_receipt = _public_receipt(
        args, findings, runtime_warnings, command, exit_code, duration_seconds, provider_invoked,
    )
    # The projection is intentionally value-blind: it contains no captured
    # stdout/stderr bytes or credential values. Suppress the conservative sink
    # alert for this reviewed, redacted evidence boundary.
    # waiver: py/clear-text-logging-sensitive-data; reason: fixed-shape receipt
    # contains only allowlisted, redacted fields; issue: PR-386; expires: 2026-12-31
    # lgtm[py/clear-text-logging-sensitive-data]
    # codeql[py/clear-text-logging-sensitive-data]
    print(json.dumps(public_receipt, sort_keys=True, separators=(",", ":")) if args.json else public_receipt["status"])
    return 0 if receipt["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
