from __future__ import annotations

import subprocess
import json
import re
import shlex
import sys
from pathlib import Path
from typing import Any, List
from ask.bootstrap import run_bootstrap_checks
from ask.envelope import CallResult, ErrorCode, ErrorObject
from ask.catalog_parity import compute_catalog_parity
from ask.commands.skills import skills_budget, skills_handles
from ask.golden_path import build_golden_path_payload

SCRIPT_TIMEOUT_SECONDS = 60
DOCTOR_SIGNAL_PRIORITY = {
    "repo_status": 10,
    "ask_bootstrap": 15,
    "projection_sync": 20,
    "catalog_parity": 30,
    "runtime_budget": 40,
    "command_handles": 50,
    "repo_surface": 60,
}
GENERATED_SURFACE_PREFIXES = (
    ".agents/skills/",
    ".skillsets/",
    ".skill-telemetry/",
)
CANONICAL_SKILL_PREFIXES = (
    "Skills/",
)

def repo_status(repo_root: Path, verbose: bool = False) -> CallResult:
    """
    Collect basic repository metadata and whether agent skills appear to be synced.

    The returned CallResult's `data` includes:
    - `repo_root` (str): contract-preserving repository root marker (`"."`).
    - `repo_root_resolved` (str): absolute resolved repository root path.
    - `is_git` (bool): `True` if a `.git` directory exists at `repo_root`, `False` otherwise.
    - `skills_synced` (bool): `True` if `.agents/skills` exists and contains at least one entry, `False` otherwise.

    Returns:
        CallResult: A CallResult with `status` set to `"success"` and the metadata above stored in `data`.
    """
    result = CallResult()
    result.data["repo_root"] = "."
    result.data["repo_root_resolved"] = str(repo_root.resolve())
    result.data["is_git"] = (repo_root / ".git").exists()

    # Check if .agents/skills is synced
    skills_dir = repo_root / ".agents" / "skills"
    is_synced = skills_dir.is_dir() and any(skills_dir.iterdir())
    result.data["skills_synced"] = is_synced

    result.status = "success"
    return result

def repo_validate(
    repo_root: Path,
    ephemeral: bool = False,
    fail_fast: bool = False,
    scope: str = "all",
    changed_files: List[str] | None = None,
) -> CallResult:
    """
    Run the repository validation script and collect a structured result.

    Executes the repository's Infrastructure/scripts/validate_all.sh with either `--ephemeral` or `--persistent`, optional fail-fast behavior, and optional changed-file scoping. Parses the script summary from stdout and records the raw output and summary counts in the returned result. If the script fails to emit the expected summary lines or exits with a non-zero code, the result is marked as an error and includes an `ErrorObject` describing the validation failure.

    Parameters:
        repo_root (Path): Path to the repository root where the script will be executed.
        ephemeral (bool): When True run validation with `--ephemeral`; otherwise use `--persistent`.
        fail_fast (bool): When True stop after the first required failure.
        scope (str): Named validation subset to run.
        changed_files (List[str] | None): Optional repo-relative changed files to scope validations.

    Returns:
        CallResult: Contains `data` with keys:
            - `required_failures` (int): Number of required failures reported by the validator.
            - `warn_only_issues` (int): Number of warn-only issues reported by the validator.
            - `raw_output` (str): Full stdout captured from the validation script.
          The result's `status` is `"success"` when the script exits with code 0, otherwise `"error"`.
          On error the result may include one or more `ErrorObject` entries with `code="ERR_VALIDATION"` and a `fix_suggestion`.
    """
    result = CallResult()

    cmd = ["bash", "Infrastructure/scripts/validate_all.sh"]
    if ephemeral:
        cmd.append("--ephemeral")
    else:
        cmd.append("--persistent")
    if fail_fast:
        cmd.append("--fail-fast")
    if scope and scope != "all":
        cmd.extend(["--scope", scope])
    if changed_files:
        cmd.append("--changed-files")
        cmd.extend(changed_files)

    VALIDATE_TIMEOUT = 300  # 5 minutes
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            timeout=VALIDATE_TIMEOUT,
        )
        stdout = completed.stdout or ""
        if stdout:
            print(stdout, end="", file=sys.stderr)
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")
        timeout_msg = f"Validation timed out after {VALIDATE_TIMEOUT} seconds."
        stdout += timeout_msg + "\n"
        print(stdout, end="", file=sys.stderr)
        completed = subprocess.CompletedProcess(cmd, returncode=124, stdout=stdout)
    except OSError as exc:
        result.status = "error"
        result.data["required_failures"] = 1
        result.data["warn_only_issues"] = 0
        result.data["raw_output"] = str(exc)
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Unable to start validation command: {exc}",
            fix_suggestion="Verify bash and Infrastructure/scripts/validate_all.sh are available."
        ))
        return result

    # Parse output for summary
    required_failures = 0
    warn_only_issues = 0

    # Handle early exit case where validation script fails before producing summary
    if "- required_failures:" not in stdout or "- warn_only_issues:" not in stdout:
        result.data["required_failures"] = 1  # Assume failure if any summary field is missing
        result.data["warn_only_issues"] = 0
        result.data["raw_output"] = stdout
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message="Validation script failed before producing summary output.",
            fix_suggestion="Check validation logs for script errors."
        ))
        return result

    for line in stdout.splitlines():
        if "- required_failures:" in line:
            required_failures = int(line.split(":")[-1].strip())
        elif "- warn_only_issues:" in line:
            warn_only_issues = int(line.split(":")[-1].strip())

    result.data["required_failures"] = required_failures
    result.data["warn_only_issues"] = warn_only_issues
    result.data["raw_output"] = stdout
    result.data["ephemeral"] = ephemeral
    result.data["fail_fast"] = fail_fast
    result.data["scope"] = scope
    result.data["changed_files"] = changed_files or []

    if completed.returncode == 0:
        result.status = "success"
    else:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Validation failed with {required_failures} required failures.",
            fix_suggestion="Review the validation logs in Infrastructure/artifacts/validation/latest/"
        ))

    return result


def doctor_catalog(repo_root: Path, strict: bool = False) -> CallResult:
    """
    Run catalog parity diagnostics and record the findings in a CallResult.

    Performs parity checks for the catalog at `repo_root` (optionally using stricter rules when `strict` is True), stores the full parity report under `result.data["catalog_parity"]` and exposes `decision_status` and `policy_identity` in `result.data`. If no drift is detected the returned CallResult has `status` set to `"success"`. If drift is detected the CallResult has `status` set to `"error"` and includes an `ErrorObject` (code `"ERR_VALIDATION"`) whose message contains the detected drift class and whose `fix_suggestion` is taken from the report's `operator_action` or a default instruction.

    Parameters:
        repo_root (Path): Root path of the repository to analyse.
        strict (bool): Apply stricter parity rules when True.

    Returns:
        CallResult: Result object containing:
            - data["catalog_parity"]: full parity report object
            - data["decision_status"]: decision status from the report (if present)
            - data["policy_identity"]: policy identity from the report (if present)
            - status: `"success"` when no drift, `"error"` when drift detected
            - errors: may include an `ErrorObject` with code `"ERR_VALIDATION"` if drift is detected
    """
    result = CallResult()
    report = compute_catalog_parity(repo_root, strict=strict)
    result.data["catalog_parity"] = report
    result.data["decision_status"] = report.get("decision_status")
    result.data["policy_identity"] = report.get("policy_identity")

    drift_detected = report.get("drift_detected")
    if drift_detected is False:
        result.status = "success"
        return result

    if drift_detected is True:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"doctor-catalog detected drift: {report.get('drift_class')}",
                fix_suggestion=report.get("operator_action")
                or "Run sync/projection tooling and rerun doctor-catalog.",
            )
        )
        return result

    result.status = "error"
    result.errors.append(
        ErrorObject(
            code="ERR_RUNTIME",
            message="doctor-catalog report missing required drift_detected boolean.",
            fix_suggestion="Regenerate catalog parity diagnostics and rerun doctor-catalog.",
        )
    )
    return result


def _error_summary(result: CallResult, fallback: str) -> str:
    if result.errors:
        return result.errors[0].message
    return fallback


def _repo_status_signal(status_result: CallResult) -> dict[str, Any]:
    if status_result.status != "success":
        return {
            "state": "error",
            "severity": "blocker",
            "summary": _error_summary(status_result, "Repository status check failed."),
            "source": "repo_status",
            "next_command": "./bin/ask repo status --json --robot",
        }
    if not status_result.data.get("is_git"):
        return {
            "state": "block",
            "severity": "blocker",
            "summary": "Repository root is not a git repository.",
            "source": "repo_status",
            "next_command": "./bin/ask repo status --json --robot",
        }
    return {
        "state": "pass",
        "severity": "info",
        "summary": "Repository status is readable.",
        "source": "repo_status",
        "details": {
            "repo_root": status_result.data.get("repo_root"),
            "is_git": status_result.data.get("is_git"),
        },
    }


def _projection_sync_signal(status_result: CallResult) -> dict[str, Any]:
    if status_result.status != "success":
        return {
            "state": "skipped",
            "severity": "warning",
            "summary": "Projection sync could not be checked because repo status failed.",
            "source": "repo_status",
            "next_command": "./bin/ask repo status --json --robot",
        }
    if not status_result.data.get("is_git"):
        return {
            "state": "skipped",
            "severity": "warning",
            "summary": "Projection sync not checked because the repository root is not a git repository.",
            "source": "repo_status",
            "next_command": "./bin/ask repo status --json --robot",
            "details": {"is_git": False},
        }
    if status_result.data.get("skills_synced"):
        return {
            "state": "pass",
            "severity": "info",
            "summary": "Workspace skill runtime appears synced.",
            "source": "repo_status",
            "details": {"skills_synced": True},
        }
    return {
        "state": "block",
        "severity": "blocker",
        "summary": "Workspace skill runtime does not appear synced.",
        "source": "repo_status",
        "next_command": "./bin/ask skills sync --scope workspace --projection rooted --json --robot",
        "details": {"skills_synced": False},
    }


def _ask_bootstrap_signal(repo_root: Path) -> dict[str, Any]:
    proof = run_bootstrap_checks(repo_root, repair=False)
    entrypoint = proof["checks"]["entrypoint_executable"]
    fallback = proof["checks"]["fallback_command"]
    path_discovery = proof["checks"]["path_discovery"]
    shim = proof["checks"]["shim_smoke"]
    details = {
        "status": proof["status"],
        "entrypoint_status": entrypoint.get("status"),
        "entrypoint_path_type": entrypoint.get("path_type"),
        "safe_to_chmod": entrypoint.get("safe_to_chmod"),
        "fallback_status": fallback.get("status"),
        "fallback_defer_to": fallback.get("defer_to"),
        "path_discovery_status": path_discovery.get("status"),
        "resolved_path": path_discovery.get("resolved_path"),
        "shim_status": shim.get("status"),
        "shim_repo_identity_status": shim.get("repo_identity_status"),
        "manual_remediation": proof.get("remediation", {}).get("manual", []),
        "applied_remediation": proof.get("remediation", {}).get("applied", []),
    }
    if entrypoint.get("status") == "fail" or fallback.get("status") == "fail":
        return {
            "state": "block",
            "severity": "blocker",
            "summary": "Ask bootstrap entrypoint or fallback command is not ready.",
            "source": "ask_bootstrap",
            "next_command": "bash scripts/bootstrap-ask.sh --json",
            "details": details,
        }
    if path_discovery.get("status") != "pass" and shim.get("status") == "skipped":
        return {
            "state": "warn",
            "severity": "warning",
            "summary": "Ask bootstrap fallback is ready; PATH shim is not configured.",
            "source": "ask_bootstrap",
            "next_command": "bash scripts/bootstrap-ask.sh --json",
            "details": details,
        }
    if shim.get("status") != "pass":
        return {
            "state": "warn",
            "severity": "warning",
            "summary": "Ask bootstrap fallback works, but PATH discovery or shim identity is incomplete.",
            "source": "ask_bootstrap",
            "next_command": "bash scripts/bootstrap-ask.sh --json",
            "details": details,
        }
    return {
        "state": "pass",
        "severity": "info",
        "summary": "Ask bootstrap entrypoint, fallback, and PATH shim are ready.",
        "source": "ask_bootstrap",
        "details": details,
    }


def _catalog_parity_signal(catalog_result: CallResult) -> dict[str, Any]:
    report = catalog_result.data.get("catalog_parity", {})
    if catalog_result.status == "success" and report.get("drift_detected") is False:
        return {
            "state": "pass",
            "severity": "info",
            "summary": "Catalog parity is resolved.",
            "source": "doctor_catalog",
            "details": {
                "decision_status": report.get("decision_status"),
                "canonical_count": report.get("canonical_count"),
                "policy_identity": report.get("policy_identity"),
            },
        }
    if report.get("drift_detected") is True:
        return {
            "state": "block",
            "severity": "blocker",
            "summary": f"Catalog parity drift detected: {report.get('drift_class')}.",
            "source": "doctor_catalog",
            "next_command": "./bin/ask repo doctor-catalog --json --robot",
            "details": {
                "decision_status": report.get("decision_status"),
                "drift_class": report.get("drift_class"),
                "operator_action": report.get("operator_action"),
            },
        }
    return {
        "state": "error",
        "severity": "blocker",
        "summary": _error_summary(catalog_result, "Catalog parity check failed."),
        "source": "doctor_catalog",
        "next_command": "./bin/ask repo doctor-catalog --json --robot",
    }


def _runtime_budget_signal(runtime_result: CallResult) -> dict[str, Any]:
    report = runtime_result.data.get("runtime_budget", {})
    violations = report.get("violations") or []
    status = report.get("status")
    details = {
        "status": status,
        "default_visible_count": report.get("default_visible_count"),
        "estimated_description_tokens": report.get("estimated_description_tokens"),
        "violation_count": len(violations),
    }
    if runtime_result.status == "success" and status == "pass":
        return {
            "state": "pass",
            "severity": "info",
            "summary": "Runtime budget is within policy.",
            "source": "skills_budget",
            "details": details,
        }
    if violations:
        return {
            "state": "block",
            "severity": "blocker",
            "summary": f"Runtime budget has {len(violations)} policy violation(s).",
            "source": "skills_budget",
            "next_command": "./bin/ask runtime budget --json --robot",
            "details": details,
        }
    if runtime_result.status != "success":
        return {
            "state": "error",
            "severity": "blocker",
            "summary": _error_summary(runtime_result, "Runtime budget check failed."),
            "source": "skills_budget",
            "next_command": "./bin/ask runtime budget --json --robot",
            "details": details,
        }
    return {
        "state": "warn",
        "severity": "warning",
        "summary": "Runtime budget returned a non-passing advisory status.",
        "source": "skills_budget",
        "next_command": "./bin/ask runtime budget --json --robot",
        "details": details,
    }


def _command_handles_signal(handles_result: CallResult) -> dict[str, Any]:
    report = handles_result.data.get("command_surface", {})
    violations = report.get("violations") or []
    details = {
        "status": report.get("status"),
        "handle_count": report.get("handle_count"),
        "violation_count": len(violations),
    }
    if handles_result.status == "success" and report.get("status") == "pass":
        return {
            "state": "pass",
            "severity": "info",
            "summary": "Command handles validate cleanly.",
            "source": "skills_handles",
            "details": details,
        }
    if violations:
        summary = f"Command-handle validation found {len(violations)} violation(s)."
    else:
        summary = _error_summary(handles_result, "Command-handle validation failed.")
    return {
        "state": "block",
        "severity": "blocker",
        "summary": summary,
        "source": "skills_handles",
        "next_command": "./bin/ask skills handles --check --json --robot",
        "details": details,
    }


def _repo_surface_signal(surface_result: CallResult) -> dict[str, Any]:
    report = surface_result.data.get("repo_surface", {})
    summary = report.get("summary", {})
    blocking_findings = summary.get("blocking_findings", 0)
    details = {
        "status": report.get("status"),
        "total_paths": summary.get("total_paths"),
        "blocking_findings": blocking_findings,
        "counts_by_code": summary.get("counts_by_code", {}),
    }
    if surface_result.status != "success":
        return {
            "state": "error",
            "severity": "blocker",
            "summary": _error_summary(surface_result, "Repo surface inventory failed."),
            "source": "repo_surface",
            "next_command": "./bin/ask repo surface --json --robot",
            "details": details,
        }
    if report.get("status") == "warning" or blocking_findings:
        return {
            "state": "warn",
            "severity": "warning",
            "summary": f"Repo surface has {blocking_findings} diagnostic finding(s).",
            "source": "repo_surface",
            "next_command": "./bin/ask repo surface --json --robot",
            "details": details,
        }
    return {
        "state": "pass",
        "severity": "info",
        "summary": "Repo surface inventory has no diagnostic debt.",
        "source": "repo_surface",
        "details": details,
    }


def _unknown_signal_error_signal(exc: Exception) -> dict[str, Any]:
    return {
        "state": "error",
        "severity": "blocker",
        "summary": f"Repo doctor failed while composing signals: {type(exc).__name__}.",
        "source": "repo_doctor",
        "next_command": "./bin/ask repo status --json --robot",
        "details": {
            "error_type": type(exc).__name__,
        },
    }


def _skipped_signal(summary: str, source: str) -> dict[str, Any]:
    return {
        "state": "skipped",
        "severity": "info",
        "summary": summary,
        "source": source,
    }


def _repo_status_skipped_downstream_signals(reason: str) -> dict[str, dict[str, Any]]:
    return {
        "catalog_parity": _skipped_signal(
            f"Catalog parity skipped {reason}.",
            "repo_status",
        ),
        "runtime_budget": _skipped_signal(
            f"Runtime budget skipped {reason}.",
            "repo_status",
        ),
        "command_handles": _skipped_signal(
            f"Command-handle validation skipped {reason}.",
            "repo_status",
        ),
        "repo_surface": _skipped_signal(
            f"Repo surface inventory skipped {reason}.",
            "repo_status",
        ),
    }


def _safe_signal(builder: Any, *args: Any) -> dict[str, Any]:
    try:
        return builder(*args)
    except (OSError, RuntimeError, ValueError, KeyError, TypeError) as exc:
        return _unknown_signal_error_signal(exc)


def repo_doctor(repo_root: Path) -> CallResult:
    """Compose repo health checks into one compact agent-facing doctor payload."""
    result = CallResult()
    try:
        status_result = repo_status(repo_root)
    except Exception as exc:
        signals = {
            "repo_status": _unknown_signal_error_signal(exc),
            "ask_bootstrap": _skipped_signal(
                "Ask bootstrap skipped because repository status failed.",
                "repo_status",
            ),
            "projection_sync": _skipped_signal(
                "Projection sync skipped because repository status failed.",
                "repo_status",
            ),
            **_repo_status_skipped_downstream_signals(
                "because repository status failed"
            ),
        }
    else:
        repo_status_signal = _safe_signal(_repo_status_signal, status_result)
        projection_sync_signal = _safe_signal(_projection_sync_signal, status_result)
        ask_bootstrap_signal = _safe_signal(_ask_bootstrap_signal, repo_root)
        signals = {
            "repo_status": repo_status_signal,
            "ask_bootstrap": ask_bootstrap_signal,
            "projection_sync": projection_sync_signal,
        }
        if repo_status_signal.get("state") in {"block", "error"}:
            signals.update(
                _repo_status_skipped_downstream_signals(
                    "until repository status is ready"
                )
            )
        elif projection_sync_signal.get("state") == "block":
            signals.update(
                _repo_status_skipped_downstream_signals(
                    "until workspace skill runtime projection is synced"
                )
            )
        else:
            signals.update(
                {
                    "catalog_parity": _safe_signal(
                        lambda: _catalog_parity_signal(doctor_catalog(repo_root))
                    ),
                    "runtime_budget": _safe_signal(
                        lambda: _runtime_budget_signal(skills_budget(repo_root))
                    ),
                    "command_handles": _safe_signal(
                        lambda: _command_handles_signal(
                            skills_handles(repo_root, check=True, include_handles=False)
                        )
                    ),
                    "repo_surface": _safe_signal(
                        lambda: _repo_surface_signal(repo_surface(repo_root))
                    ),
                }
            )
    payload = build_golden_path_payload(
        signals=signals,
        normal_next_command="./bin/ask repo status --json --robot",
        signal_priorities=DOCTOR_SIGNAL_PRIORITY,
    )
    result.data["doctor"] = payload
    result.data.update(payload)
    result.status = "error" if payload["blocking"] else "success"
    if payload["blocking"]:
        result.errors.append(
            ErrorObject(
                code=ErrorCode.ERR_VALIDATION,
                message=payload["agent_summary"],
                fix_suggestion=payload.get("next_command"),
            )
        )
    return result


def _git_output_lines(repo_root: Path, args: list[str]) -> list[str]:
    command = ["git", *args]
    try:
        process = subprocess.run(
            command,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=SCRIPT_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"git command timed out: {' '.join(command)}") from exc
    except OSError as exc:
        raise RuntimeError(
            f"git command could not start: {' '.join(command)} ({exc})"
        ) from exc
    if process.returncode != 0:
        detail = (process.stderr or process.stdout or "").strip()
        raise RuntimeError(
            f"git command failed: {' '.join(command)}"
            + (f" ({detail})" if detail else "")
        )
    return [line.strip() for line in process.stdout.splitlines() if line.strip()]


def collect_changed_files(repo_root: Path) -> list[str]:
    """Return repo-relative staged, unstaged, and untracked file paths."""
    changed = set()
    for args in (
        ["diff", "--name-only", "--diff-filter=ACMRD", "--"],
        ["diff", "--cached", "--name-only", "--diff-filter=ACMRD", "--"],
        ["ls-files", "--others", "--exclude-standard"],
    ):
        changed.update(_git_output_lines(repo_root, args))
    return sorted(changed)


def _quote_paths(paths: list[str]) -> str:
    return " ".join(shlex.quote(path) for path in paths)


def _validation_command_for_changed_files(changed_files: list[str]) -> str:
    if not changed_files:
        return "./bin/ask repo validate --json --robot"
    return (
        "./bin/ask repo validate --changed-files "
        f"{_quote_paths(changed_files)} --json --robot"
    )


def _closeout_sync_report(changed_files: list[str]) -> dict[str, Any]:
    generated_changed = [
        path for path in changed_files
        if path.startswith(GENERATED_SURFACE_PREFIXES)
    ]
    canonical_skill_changed = [
        path for path in changed_files
        if _is_canonical_skill_path(path)
    ]
    commands = []
    validation_commands = []
    projection_update_present = bool(canonical_skill_changed and generated_changed)
    if canonical_skill_changed and not projection_update_present:
        commands.extend(
            [
                "./bin/ask skills sync --scope workspace --projection rooted --json --robot",
                "./bin/ask skills handles --check --json --robot",
            ]
        )
    elif generated_changed:
        validation_commands.append("./bin/ask skills handles --check --json --robot")
    return {
        "needed": bool(commands),
        "commands": commands,
        "validation_commands": validation_commands,
        "generated_changed_files": generated_changed,
        "canonical_skill_changed_files": canonical_skill_changed,
        "projection_update_present": projection_update_present,
    }


def _is_canonical_skill_path(path: str) -> bool:
    if path.startswith(CANONICAL_SKILL_PREFIXES):
        return True
    parts = path.split("/")
    return (
        len(parts) >= 4
        and parts[0] == "Plugins"
        and parts[1] != "cache"
        and parts[2] in {"skills", "Skills"}
    )


def _closeout_runtime_budget(doctor_payload: dict[str, Any]) -> dict[str, Any]:
    details = (
        doctor_payload.get("signals", {})
        .get("runtime_budget", {})
        .get("details", {})
    )
    return {
        "status": details.get("status"),
        "default_visible_count": details.get("default_visible_count"),
        "estimated_description_tokens": details.get("estimated_description_tokens"),
        "violation_count": details.get("violation_count", 0),
    }


def _closeout_surface_policy(doctor_payload: dict[str, Any]) -> dict[str, Any]:
    details = (
        doctor_payload.get("signals", {})
        .get("repo_surface", {})
        .get("details", {})
    )
    return {
        "status": details.get("status"),
        "blocking_findings": details.get("blocking_findings", 0),
        "total_paths": details.get("total_paths"),
        "counts_by_code": details.get("counts_by_code", {}),
    }


def _closeout_focused_validation(changed_files: list[str]) -> list[dict[str, Any]]:
    commands = [
        {
            "id": "repo_doctor",
            "reason": "Confirm golden-path health before claiming completion.",
            "command": "./bin/ask repo doctor --json --robot",
        }
    ]
    if any(path.startswith(GENERATED_SURFACE_PREFIXES) for path in changed_files):
        commands.append(
            {
                "id": "skill_handles",
                "reason": "Validate generated command handles for changed projection files.",
                "command": "./bin/ask skills handles --check --json --robot",
            }
        )
    if changed_files:
        commands.append(
            {
                "id": "changed_validation",
                "reason": "Run validation scoped to the files currently changed.",
                "command": _validation_command_for_changed_files(changed_files),
            }
        )
    else:
        commands.append(
            {
                "id": "repo_status",
                "reason": "No changed files were detected; confirm clean repository state.",
                "command": "./bin/ask repo status --json --robot",
            }
        )
    return commands


def _diagnostic_debt_next_command(diagnostic_debt: list[dict[str, Any]]) -> str | None:
    for debt in diagnostic_debt:
        next_command = debt.get("next_command") if isinstance(debt, dict) else None
        if isinstance(next_command, str) and next_command.strip():
            return next_command
    return None


def repo_closeout(repo_root: Path, changed: bool = False, strict: bool = False) -> CallResult:
    """Report completion readiness without editing, validating, or committing."""
    result = CallResult()
    doctor_result = repo_doctor(repo_root)
    doctor_payload = doctor_result.data.get("doctor", {})
    changed_files_error = None
    changed_files: list[str] = []
    if changed:
        try:
            changed_files = collect_changed_files(repo_root)
        except RuntimeError as exc:
            changed_files_error = str(exc)
    sync_report = _closeout_sync_report(changed_files)
    blockers: list[str] = []
    if changed_files_error:
        blockers.append("changed_file_detection_failed")
    if doctor_payload.get("blocking"):
        blockers.append("repo_doctor_blocking")
    if sync_report["needed"]:
        blockers.append("sync_required")
    diagnostic_debt = doctor_payload.get("diagnostic_debt", [])
    if strict and diagnostic_debt:
        blockers.append("strict_diagnostic_debt")

    focused_validation = _closeout_focused_validation(changed_files)
    ready = not blockers
    next_command: str | None
    if changed_files_error:
        next_command = "./bin/ask repo status --json --robot"
    elif doctor_payload.get("blocking"):
        next_command = doctor_payload.get("next_command")
    elif sync_report["needed"]:
        next_command = sync_report["commands"][0]
    elif strict and diagnostic_debt:
        next_command = (
            _diagnostic_debt_next_command(diagnostic_debt)
            or doctor_payload.get("next_command")
            or "./bin/ask repo doctor --json --robot"
        )
    elif sync_report["validation_commands"]:
        next_command = sync_report["validation_commands"][0]
    elif changed_files:
        next_command = _validation_command_for_changed_files(changed_files)
    else:
        next_command = "./bin/ask repo status --json --robot"

    payload = {
        "agent_summary": (
            "Ready: no closeout blockers detected."
            if ready
            else f"Blocked: closeout has {len(blockers)} blocker(s)."
        ),
        "changed_files": changed_files,
        "changed_file_count": len(changed_files),
        "changed_mode_requested": changed,
        "changed_files_error": changed_files_error,
        "sync": sync_report,
        "runtime_budget": _closeout_runtime_budget(doctor_payload),
        "surface_policy": _closeout_surface_policy(doctor_payload),
        "focused_validation": focused_validation,
        "diagnostic_debt": diagnostic_debt,
        "commit_readiness": {
            "ready": ready,
            "blockers": blockers,
            "strict": strict,
        },
        "doctor": doctor_payload,
        "next_command": next_command,
    }
    result.data["repo_closeout"] = payload
    result.data.update(payload)
    result.status = "success" if ready else "error"
    if not ready:
        result.errors.append(
            ErrorObject(
                code=ErrorCode.ERR_VALIDATION,
                message=payload["agent_summary"],
                fix_suggestion=next_command,
            )
        )
    return result


def provider_audit(repo_root: Path) -> CallResult:
    """Run the OpenAI provider policy audit and return its JSON report."""
    result = CallResult()
    cmd = [
        sys.executable,
        "Infrastructure/scripts/validation-and-linting/verify_provider_policy.py",
        "--json",
    ]
    try:
        process = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
            timeout=SCRIPT_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        result.data["provider_policy"] = {
            "status": "fail",
            "raw_stdout": exc.stdout or "",
            "raw_stderr": exc.stderr or "",
        }
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="OpenAI provider policy audit timed out.",
                fix_suggestion="Run the provider policy script directly, inspect for hangs, and retry.",
            )
        )
        return result
    except OSError as exc:
        result.data["provider_policy"] = {
            "status": "fail",
            "raw_stdout": "",
            "raw_stderr": str(exc),
        }
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="OpenAI provider policy audit could not start.",
                fix_suggestion="Verify the Python interpreter and provider policy script path, then retry.",
            )
        )
        return result
    try:
        report = json.loads(process.stdout)
    except json.JSONDecodeError:
        report = {
            "status": "fail",
            "raw_stdout": process.stdout,
            "raw_stderr": process.stderr,
        }

    result.data["provider_policy"] = report
    result.status = "success" if process.returncode == 0 and report.get("status") == "pass" else "error"
    if result.status == "error":
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="OpenAI provider policy audit failed.",
                fix_suggestion="Remove or archive active legacy provider paths, then rerun ask repo provider-audit.",
            )
        )
    return result


def repo_surface(repo_root: Path, strict: bool = False) -> CallResult:
    """
    Produce a surface-inventory report for the repository.

    Parameters:
        repo_root (Path): Path to the repository root where the inventory check will run.
        strict (bool): When true, require strict inventory validation.

    Returns:
        CallResult: Result containing:
            - data["repo_surface"]: parsed inventory report dictionary (or a fallback error report on parse failure).
            - data["strict"]: the provided `strict` value.
            - status: "success" when the inventory indicates no blocking failures, otherwise "error".
            - errors: on failure, one or more ErrorObject entries describing the problem and suggested fixes.
              Inventory failures use "ERR_VALIDATION"; inventory command timeouts use "ERR_TIMEOUT".
    """
    result = CallResult()
    cmd = [
        sys.executable,
        "Infrastructure/scripts/validation-and-linting/check_repo_surface_inventory.py",
        "--json",
    ]
    if strict:
        cmd.append("--strict")

    try:
        process = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=SCRIPT_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        result.status = "error"
        result.data["repo_surface"] = {
            "status": "error",
            "raw_stdout": exc.stdout or "",
            "raw_stderr": exc.stderr or "",
            "summary": {
                "total_paths": 0,
                "blocking_findings": 1,
            },
        }
        result.data["strict"] = strict
        result.errors.append(
            ErrorObject(
                code=ErrorCode.ERR_TIMEOUT,
                message=(
                    "Repo surface inventory timed out after "
                    f"{SCRIPT_TIMEOUT_SECONDS} seconds."
                ),
                fix_suggestion=(
                    "Run the underlying inventory script directly to identify "
                    "the slow path, then retry repo surface."
                ),
            )
        )
        return result
    except OSError as exc:
        result.status = "error"
        result.data["repo_surface"] = {
            "status": "error",
            "raw_stdout": "",
            "raw_stderr": str(exc),
            "summary": {
                "total_paths": 0,
                "blocking_findings": 1,
            },
        }
        result.data["strict"] = strict
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Repo surface inventory could not start.",
                fix_suggestion="Verify the Python interpreter and inventory script path, then retry repo surface.",
            )
        )
        return result
    parse_ok = True
    try:
        report = json.loads(process.stdout)
    except json.JSONDecodeError:
        parse_ok = False
        report = {
            "status": "error",
            "raw_stdout": process.stdout,
            "raw_stderr": process.stderr,
            "summary": {
                "total_paths": 0,
                "blocking_findings": 1,
            },
        }

    result.data["repo_surface"] = report
    result.data["strict"] = strict
    report_status = report.get("status")
    result.status = (
        "success"
        if process.returncode == 0 and parse_ok and report_status in {"success", "warning"}
        else "error"
    )
    if result.status == "error":
        blocking = report.get("summary", {}).get("blocking_findings", "unknown")
        message = f"Repo surface inventory found {blocking} blocking finding(s)."
        suggestion = (
            "Review data.repo_surface.findings and classify, allowlist, or cleanup "
            "intentional exceptions before relying on strict mode."
        )
        if not parse_ok:
            message = "Repo surface inventory emitted invalid JSON."
            suggestion = "Run the underlying inventory script directly and fix stdout JSON integrity."
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=message,
                fix_suggestion=suggestion,
            )
        )
    return result


def check_hub_stability(repo_root: Path, changed_files: List[str] | None = None) -> CallResult:
    """
    Validate stability-related changes to SKILL.md files and enforce rules for skills marked `stability: stable`.

    Checks the repository for SKILL.md frontmatter that declares a skill as stable and, when a list of changed files is provided, verifies that:
    - stable SKILL.md files include `name:` and `description:` fields in their frontmatter, and
    - deletion of a stable skill is not performed without an existing deprecation notice.

    Parameters:
        repo_root (Path): Repository root directory against which paths and SKILL.md files are resolved.
        changed_files (List[str], optional): Iterable of file paths (typically relative to `repo_root`) to inspect; if omitted, only a global scan is performed.

    Returns:
        CallResult: Contains:
          - `status`: `"success"` if no stability violations were found, `"error"` otherwise.
          - `data.stable_skills` (List[str]): Sorted list of discovered stable skill identifiers.
          - `data.stable_count` (int): Number of discovered stable skills.
          - `data.checked_files` (int): Number of `changed_files` inspected (0 if `changed_files` was not provided).
          - `data.errors` (List[str], optional): When `status` is `"error"`, a list of human-readable error messages describing each violation.
          - `errors` (List[ErrorObject]): For each string in `data.errors`, an `ErrorObject` with `code="ERR_VALIDATION"` is appended to the result's `errors` list.
    """
    result = CallResult()

    # Build list of all SKILL.md files
    stable_skills = []
    errors = []

    FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---", re.DOTALL)
    STABLE_RE = re.compile(r"^stability\s*:\s*stable\s*$", re.MULTILINE)

    for md in sorted(repo_root.rglob("SKILL.md")):
        try:
            content = md.read_text(encoding="utf-8", errors="replace")
            fm = FRONTMATTER_RE.search(content)
            if fm and STABLE_RE.search(fm.group(1)):
                skill = md.parts[-2]
                stable_skills.append(skill)
        except (OSError, UnicodeDecodeError) as exc:
            print(f"Warning: Failed to read or parse {md}: {exc}", file=sys.stderr)
            continue
        except re.error as exc:
            print(f"Warning: Regex error processing {md}: {exc}", file=sys.stderr)
            continue

    # If checking specific changed files
    if changed_files:
        for f in changed_files:
            p = repo_root / f
            if p.name != "SKILL.md":
                continue
            skill = p.parts[-2] if len(p.parts) >= 2 else str(p)

            if not p.exists():
                # File was deleted - check against stable skills list or edges file
                edges_file = repo_root / "ops" / "metrics" / "graph" / "skill-edges.json"
                if edges_file.exists():
                    try:
                        data = json.loads(edges_file.read_text())
                        stable_ids = {n["id"] for n in data.get("nodes", []) if n.get("stability") == "stable"}
                        if skill in stable_ids:
                            previous = subprocess.run(
                                ["git", "show", f"HEAD:{f}"],
                                cwd=str(repo_root),
                                capture_output=True,
                                text=True,
                                check=False,
                                timeout=SCRIPT_TIMEOUT_SECONDS,
                            )
                            if previous.returncode == 0 and re.search(r"^## Deprecation\b", previous.stdout, re.MULTILINE):
                                continue
                            errors.append(
                                f"STABLE SKILL DELETED: '{skill}' is marked stable and was deleted "
                                f"without a deprecation notice. Add a ## Deprecation section to the "
                                f"last committed version before removal."
                            )
                    except (OSError, json.JSONDecodeError, KeyError, TypeError, subprocess.SubprocessError) as e:
                        errors.append(
                            f"Unable to validate stable skill deletion for '{skill}' due to error reading "
                            f"or parsing skill-edges.json: {e}"
                        )
                continue

            try:
                content = p.read_text(encoding="utf-8", errors="replace")
                fm = FRONTMATTER_RE.search(content)
                if not (fm and STABLE_RE.search(fm.group(1))):
                    continue

                # Stable skill exists - check required fields
                if not re.search(r"^name\s*:", fm.group(1), re.MULTILINE):
                    errors.append(f"STABLE SKILL MISSING 'name': {skill}")
                if not re.search(r"^description\s*:", fm.group(1), re.MULTILINE):
                    errors.append(f"STABLE SKILL MISSING 'description': {skill}")
            except (OSError, UnicodeDecodeError) as exc:
                print(f"Warning: Failed to read or parse {p}: {exc}", file=sys.stderr)
                continue
            except re.error as exc:
                print(f"Warning: Regex error processing {p}: {exc}", file=sys.stderr)
                continue

    result.data["stable_skills"] = sorted(stable_skills)
    result.data["stable_count"] = len(stable_skills)
    result.data["checked_files"] = len(changed_files) if changed_files else 0

    if errors:
        result.status = "error"
        result.data["errors"] = errors
        for e in errors:
            result.errors.append(ErrorObject(code="ERR_VALIDATION", message=e))
    else:
        result.status = "success"

    return result
