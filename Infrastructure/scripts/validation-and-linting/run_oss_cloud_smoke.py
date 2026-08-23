#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib
import stat
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SECRET_OUTPUT_SCAN = SCRIPT_DIR / "check_oss_cloud_secret_output.py"
PUBLIC_RECEIPT_EMITTER = SCRIPT_DIR / "emit_oss_cloud_public_receipt.py"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
LIB_DIR = SCRIPT_DIR.parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

_output_check = importlib.import_module("check_oss_local_smoke_output")
_transport_contracts = importlib.import_module("ask.skills_sdk.ab_transport_contracts")
_findings = _output_check._findings
CONFIGS_AUTH_WRAPPER = _transport_contracts.CONFIGS_AUTH_WRAPPER
CONFIGS_CODEX_EXEC_WRAPPER = _transport_contracts.CONFIGS_CODEX_EXEC_WRAPPER


EXPECTED_MODEL = "deepseek-v4-flash:0731-cloud"
EXPECTED_PROVIDER = "ollama-cloud"
DEFAULT_PROFILE_SOURCE = Path.home() / ".codex" / "oss-cloud.config.toml"
DEFAULT_AUTH_ENV_FILE = Path.home() / ".codex" / ".env"
DEFAULT_AUTH_WRAPPER = CONFIGS_AUTH_WRAPPER
DEFAULT_CODEX_EXEC_WRAPPER = CONFIGS_CODEX_EXEC_WRAPPER
DEFAULT_MARKER = "CODEX_OSS_CLOUD_OK"
CLOUD_SMOKE_MAX_TOKENS_USED = 20000
CLOUD_SMOKE_NON_BLOCKING_CODES = frozenset({"codex_runtime_metadata_fallback"})
VALUE_BLIND_FINDING_MESSAGES = (
    ("oss_cloud_profile_missing", "oss_cloud_profile_missing", "oss-cloud profile source must be a regular file."),
    ("oss_cloud_model_mismatch", "oss_cloud_model_mismatch", "The reviewed oss-cloud model did not match."),
    ("oss_cloud_provider_mismatch", "oss_cloud_provider_mismatch", "The reviewed oss-cloud provider did not match."),
    ("oss_cloud_marker_not_allowlisted", "oss_cloud_marker_not_allowlisted", "The bounded cloud smoke requires its fixed marker."),
    ("oss_cloud_auth_stream_missing", "oss_cloud_auth_stream_missing", "Desktop-owned OLLAMA_API_KEY FIFO is required."),
    ("oss_cloud_auth_wrapper_missing", "oss_cloud_auth_wrapper_missing", "Configs auth wrapper is required for oss-cloud."),
    ("oss_cloud_exec_wrapper_missing", "oss_cloud_exec_wrapper_missing", "Configs Codex wrapper is required for oss-cloud."),
    ("oss_cloud_auth_wrapper_identity_mismatch", "oss_cloud_auth_wrapper_identity_mismatch", "The supplied auth wrapper must be canonical."),
    ("oss_cloud_exec_wrapper_identity_mismatch", "oss_cloud_exec_wrapper_identity_mismatch", "The supplied Codex wrapper must be canonical."),
    ("codex_runtime_metadata_fallback", "codex_runtime_metadata_fallback", "Codex reported fallback metadata."),
    ("codex_runtime_visible_thinking", "codex_runtime_visible_thinking", "Model output exposed a thinking trace."),
    ("codex_runtime_token_budget_exceeded", "codex_runtime_token_budget_exceeded", "The smoke transcript exceeded its token budget."),
    ("oss_cloud_secret_output_observed", "captured_output_scan_blocked", "Captured output failed the value-blind safety check."),
    ("oss_cloud_secret_output_scan_unavailable", "captured_output_scan_unavailable", "Captured output could not be safely scanned."),
    ("oss_cloud_smoke_exit_nonzero", "oss_cloud_smoke_exit_nonzero", "Codex exited with a non-zero status."),
    ("oss_cloud_smoke_marker_mismatch", "oss_cloud_smoke_marker_mismatch", "Cloud smoke marker did not match."),
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
    """Return whether a supplied wrapper names the reviewed identity exactly."""
    try:
        candidate = Path(path).expanduser()
        return candidate == expected and candidate.is_file() and not candidate.is_symlink()
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
    try:
        completed = subprocess.run(
            [sys.executable, str(SECRET_OUTPUT_SCAN), str(paths["stdout"]), str(paths["stderr"])],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {"status": "unavailable", "source": "captured_output_scan", "redacted": True}
    status = {0: "clear", 1: "blocked"}.get(completed.returncode, "unavailable")
    return {
        "status": status,
        "source": "captured_output_scan",
        "redacted": True,
    }


def _receipt(
    args: argparse.Namespace, paths: dict[str, Path], profile: Path, findings: list[dict[str, str]], *,
    command: list[str] | None, exit_code: int | None, duration_seconds: float, provider_invoked: bool,
    runtime_warnings: list[dict[str, str]] | None = None, secret_observation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    observation = secret_observation or _secret_observation(paths, executed=command is not None)
    warnings = runtime_warnings if runtime_warnings is not None else _runtime_findings(
        args, paths, findings, command, exit_code, observation,
    )
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
        "secret_observation": observation,
        "secret_value_observed": observation["status"] == "blocked",
    }


def _runtime_findings(
    args: argparse.Namespace, paths: dict[str, Path], findings: list[dict[str, str]],
    command: list[str] | None, exit_code: int | None, secret_observation: dict[str, Any],
) -> list[dict[str, str]]:
    if command is None:
        return []
    runtime_findings = _findings(
        "\n".join((_read(paths["stdout"]), _read(paths["stderr"]))), CLOUD_SMOKE_MAX_TOKENS_USED,
    )
    if secret_observation.get("status") == "blocked":
        runtime_findings.append({"code": "oss_cloud_secret_output_observed", "message": "Captured smoke output matched a redacted secret-shaped marker."})
    elif secret_observation.get("status") != "clear":
        runtime_findings.append({"code": "oss_cloud_secret_output_scan_unavailable", "message": "Captured smoke output could not be safely scanned."})
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
    for known_code, public_code, message in VALUE_BLIND_FINDING_MESSAGES:
        if any(item.get("code") == known_code for item in items):
            projected.append({"code": public_code, "message": message})
    if items and not projected:
        projected.append({
            "code": "unclassified_smoke_finding",
            "message": "An unclassified smoke finding was observed.",
        })
    return projected


def _value_blind_status(provider_invoked: bool, findings: list[dict[str, str]]) -> str:
    if provider_invoked and not findings:
        return "pass"
    return "blocked"


def _captured_output_scan_status(observation: dict[str, Any]) -> str:
    return {
        "clear": "passed",
        "blocked": "blocked",
        "unavailable": "unavailable",
    }.get(observation.get("status"), "unavailable")


def _value_blind_receipt(
    *,
    env_file: Path,
    findings: list[dict[str, str]],
    warnings: list[dict[str, str]],
    command_present: bool,
    exit_code: int | None,
    duration_seconds: float,
    provider_invoked: bool,
    secret_observation: dict[str, Any],
) -> dict[str, Any]:
    output_scan_status = _captured_output_scan_status(secret_observation)
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
        "captured_output_scan": {
            "status": output_scan_status,
            "source": "captured_output_scan",
            "redacted": True,
        },
        "captured_output_safe": output_scan_status == "passed",
    }


def _run_smoke(
    args: argparse.Namespace,
    paths: dict[str, Path],
    profile: Path,
    findings: list[dict[str, str]],
    env_file: Path,
) -> tuple[dict[str, Any], list[dict[str, str]], list[str] | None, int | None, float, bool, dict[str, Any]]:
    if findings:
        observation = _secret_observation(paths, executed=False)
        receipt = _receipt(args, paths, profile, findings, command=None, exit_code=None, duration_seconds=0.0, provider_invoked=False, secret_observation=observation)
        return receipt, [], None, None, 0.0, False, observation
    command = _command(args, paths, env_file)
    exit_code, duration_seconds = _run(command, paths, args)
    observation = _secret_observation(paths, executed=True)
    runtime_warnings = _runtime_findings(args, paths, findings, command, exit_code, observation)
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
        secret_observation=observation,
    )
    return receipt, runtime_warnings, command, exit_code, duration_seconds, True, observation


def _public_receipt(
    args: argparse.Namespace,
    findings: list[dict[str, str]],
    runtime_warnings: list[dict[str, str]],
    command: list[str] | None,
    exit_code: int | None,
    duration_seconds: float,
    provider_invoked: bool,
    secret_observation: dict[str, Any],
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
        secret_observation=secret_observation,
    )


def _public_receipt_command(receipt: dict[str, Any], *, as_json: bool) -> list[str]:
    """Pass only allowlisted scalar fields to the separate public emission boundary."""
    output_scan = receipt["captured_output_scan"]
    command = [
        sys.executable,
        str(PUBLIC_RECEIPT_EMITTER),
        "--status", receipt["status"],
        "--auth-source", receipt["auth_source"],
        "--provider-invoked", str(receipt["provider_invoked"]).lower(),
        "--command-present", str(receipt["command"] is not None).lower(),
        "--duration-seconds", str(receipt["duration_seconds"]),
        "--findings", ",".join(item["code"] for item in receipt["findings"]),
        "--warnings", ",".join(item["code"] for item in receipt["warnings"]),
        "--captured-output-scan", output_scan["status"],
    ]
    if receipt["exit_code"] is not None:
        command.extend(("--exit-code", str(receipt["exit_code"])))
    if as_json:
        command.append("--json")
    return command


def _emit_public_receipt(receipt: dict[str, Any], *, as_json: bool) -> bool:
    """Delegate stdout emission so the runner never writes captured-output taint."""
    try:
        completed = subprocess.run(
            _public_receipt_command(receipt, as_json=as_json),
            stdin=subprocess.DEVNULL,
            check=False,
            text=True,
        )
    except OSError:
        return False
    return completed.returncode == 0


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
    receipt, runtime_warnings, command, exit_code, duration_seconds, provider_invoked, secret_observation = _run_smoke(
        args, paths, profile, findings, env_file or Path(args.env_file).expanduser()
    )
    # The public emission process accepts only allowlisted scalars and owns the
    # stdout sink. The runner must never write data-flow from captured child
    # stdout or stderr to its own logging boundary.
    public_receipt = _public_receipt(
        args, findings, runtime_warnings, command, exit_code, duration_seconds, provider_invoked, secret_observation,
    )
    if not _emit_public_receipt(public_receipt, as_json=args.json):
        print("oss-cloud public receipt emission failed", file=sys.stderr)
        return 2
    return 0 if receipt["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
