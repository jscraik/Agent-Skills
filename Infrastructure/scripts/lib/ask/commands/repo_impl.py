from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, List
from ask.bootstrap import run_bootstrap_checks
from ask.envelope import CallResult, ErrorCode, ErrorObject
from ask.catalog_parity import compute_catalog_parity
from ask.commands.skills import skills_budget, skills_events, skills_handles, skills_memory, skills_package, skills_profiles
from ask.commands.skills_impl import _subprocess_env_with_uv_cache
from ask.golden_path import build_golden_path_payload

SCRIPT_TIMEOUT_SECONDS = 60
DOCTOR_SIGNAL_PRIORITY = {
    "repo_status": 10,
    "ask_bootstrap": 15,
    "projection_sync": 20,
    "catalog_parity": 30,
    "runtime_budget": 40,
    "sdk_handles": 50,
    "command_handles": 50,
    "capability_readiness": 55,
    "memory_readiness": 56,
    "package_readiness": 57,
    "repo_surface": 60,
}
# Plugin router skills are intentionally hidden from SDK-flat public handle
# resolution, so closeout must validate package readiness through source truth.
PACKAGE_READINESS_SENTINEL = "Plugins/skill-factory/skills/code_quality_review/skill-builder"
SDK_HANDLE_CHECK_COMMAND = "./bin/ask skills list --json --robot"
COMMAND_HANDLE_CHECK_COMMAND = SDK_HANDLE_CHECK_COMMAND
SKILLS_SYNC_COMMAND = "./bin/ask skills sync --scope workspace --projection flat --json --robot"
GENERATED_SURFACE_PREFIXES = (
    ".agents/skills/",
    ".skillsets/",
    ".skill-telemetry/",
)
CANONICAL_SKILL_PREFIXES = (
    "Skills/",
)
RUNTIME_EVIDENCE_ROOT = ".harness/evidence/runtime-proof"
RUNTIME_EVIDENCE_VALIDATOR = Path("Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py")


def _repo_validation_command(action: str, *args: str, **flags: bool) -> str:
    """Build a shell-quoted repository command with machine-readable output."""
    parts = ["./bin/ask", "repo", action, *args]
    for flag, enabled in flags.items():
        if enabled:
            parts.append(f"--{flag.replace('_', '-')}")
    parts.extend(["--json", "--robot"])
    return " ".join(shlex.quote(part) for part in parts)


def repo_status(repo_root: Path, verbose: bool = False, baseline_path: str | None = None) -> CallResult:
    """Return repository identity and the non-mutating workspace projection state."""
    result = CallResult()
    result.data["validation_commands"] = [_repo_validation_command("status", verbose=verbose)]
    result.data["repo_root"] = "."
    result.data["repo_root_resolved"] = str(repo_root.resolve())
    result.data["is_git"] = (repo_root / ".git").exists()

    skills_dir = repo_root / ".agents" / "skills"
    projection_state, is_synced = _skills_projection_state(repo_root, skills_dir)
    result.data["skills_synced"] = is_synced
    result.data["skills_projection_state"] = projection_state

    if baseline_path is not None:
        try:
            result.data["shape_baseline"] = _shape_baseline(repo_root, baseline_path)
        except RuntimeError as exc:
            result.status = "error"
            result.errors.append(ErrorObject(code=ErrorCode.ERR_VALIDATION, message=str(exc)))
            return result

    result.status = "success"
    return result


def _skills_projection_state(repo_root: Path, skills_dir: Path) -> tuple[str, bool]:
    """Classify the workspace runtime projection without creating or repairing it."""
    if skills_dir.is_dir():
        try:
            return ("synced", True) if any(skills_dir.iterdir()) else ("empty", False)
        except OSError:
            return "corrupt", False
    if skills_dir.exists() or skills_dir.is_symlink():
        return "corrupt", False
    if _is_linked_worktree(repo_root):
        return "unmaterialized_linked_worktree", False
    return "missing", False


def _is_linked_worktree(repo_root: Path) -> bool:
    """Return whether Git represents this checkout with a gitdir pointer file."""
    git_path = repo_root / ".git"
    if not git_path.is_file():
        return False
    try:
        return git_path.read_text(encoding="utf-8").startswith("gitdir: ")
    except OSError:
        return False


def _can_import_yaml_with(command: List[str]) -> bool:
    try:
        completed = subprocess.run(
            [*command, "-c", "import yaml"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
            env=_subprocess_env_with_uv_cache(),
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return completed.returncode == 0


def _managed_pyyaml_python_command() -> List[str]:
    candidates: List[List[str]] = []
    python_bin = os.environ.get("PYTHON_BIN")
    if python_bin:
        candidates.append([python_bin])
    candidates.append([sys.executable])

    preferred = Path.home() / ".venvs" / "pyyaml" / "bin" / "python"
    if preferred.exists():
        candidates.append([str(preferred)])

    seen: set[tuple[str, ...]] = set()
    for candidate in candidates:
        key = tuple(candidate)
        if key in seen:
            continue
        seen.add(key)
        if _can_import_yaml_with(candidate):
            return candidate

    return ["uv", "run", "--no-project", "--with", "PyYAML", "python"]


def repo_yaml_inspect(repo_root: Path, path: str, query: str | None = None) -> CallResult:
    """Parse a repo YAML file through the managed PyYAML interpreter.

    This command exists so agents do not reach for ad hoc system-python snippets
    that depend on the system interpreter having PyYAML installed.
    """
    result = CallResult()
    target = (repo_root / path).resolve()
    try:
        target.relative_to(repo_root.resolve())
    except ValueError:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code=ErrorCode.ERR_PATH_TRAVERSAL,
                message=f"YAML path must stay inside the repository: {path}",
                fix_suggestion="Pass a repo-relative YAML file path.",
            )
        )
        return result
    if not target.exists() or not target.is_file():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code=ErrorCode.ERR_VALIDATION,
                message=f"YAML file not found: {path}",
                fix_suggestion="Pass an existing repo-relative YAML file path.",
            )
        )
        return result

    python_cmd = _managed_pyyaml_python_command()
    command_display = " ".join(shlex.quote(part) for part in [*python_cmd, "-"])
    result.data["validation_commands"] = [
        " ".join(
            [
                "./bin/ask",
                "repo",
                "yaml-inspect",
                shlex.quote(path),
                *( ["--query", shlex.quote(query)] if query else [] ),
                "--json",
                "--robot",
            ]
        )
    ]
    result.data["python_command"] = command_display
    result.data["path"] = str(target.relative_to(repo_root.resolve()))

    inspector = '''
import json
import sys
from pathlib import Path
import yaml

path = Path(sys.argv[1])
query = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else None

def project(value, query):
    current = value
    if not query:
        return current
    for raw_part in query.split("."):
        if not raw_part:
            raise KeyError("empty query segment")
        part = raw_part
        if isinstance(current, dict):
            if part not in current:
                raise KeyError(part)
            current = current[part]
            continue
        if isinstance(current, list):
            try:
                index = int(part)
            except ValueError as exc:
                raise KeyError(part) from exc
            current = current[index]
            continue
        raise KeyError(part)
    return current

def to_jsonable(value):
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)

payload = yaml.safe_load(path.read_text(encoding="utf-8"))
selected = project(payload, query)
summary = {
    "root_type": type(payload).__name__,
    "query": query,
    "query_type": type(selected).__name__,
    "query_value": to_jsonable(selected),
}
if isinstance(payload, dict):
    summary["top_level_keys"] = sorted(str(key) for key in payload.keys())
if isinstance(payload, list):
    summary["item_count"] = len(payload)
if isinstance(selected, dict):
    summary["query_keys"] = sorted(str(key) for key in selected.keys())
if isinstance(selected, list):
    summary["query_item_count"] = len(selected)
print(json.dumps(summary, ensure_ascii=False))
'''
    try:
        completed = subprocess.run(
            [*python_cmd, "-", str(target), query or ""],
            input=inspector,
            capture_output=True,
            text=True,
            check=False,
            timeout=SCRIPT_TIMEOUT_SECONDS,
            env=_subprocess_env_with_uv_cache(),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code=ErrorCode.ERR_DEPENDENCY,
                message=f"Unable to inspect YAML with managed PyYAML interpreter: {exc}",
                fix_suggestion="Run ./bin/ask repo doctor --json --robot and verify uv or a PyYAML-capable Python is available.",
            )
        )
        return result

    if completed.returncode != 0:
        result.status = "error"
        result.data["stderr"] = completed.stderr
        result.errors.append(
            ErrorObject(
                code=ErrorCode.ERR_VALIDATION,
                message=f"YAML inspection failed for {path}.",
                fix_suggestion=completed.stderr.strip() or "Check YAML syntax and query path.",
            )
        )
        return result

    try:
        result.data["yaml"] = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        result.status = "error"
        result.data["stdout"] = completed.stdout
        result.errors.append(
            ErrorObject(
                code=ErrorCode.ERR_RUNTIME,
                message=f"YAML inspector returned non-JSON output: {exc}",
                fix_suggestion="Inspect the managed Python command output and rerun repo yaml-inspect.",
            )
        )
        return result

    result.status = "success"
    return result

def repo_validate(
    repo_root: Path,
    ephemeral: bool = False,
    fail_fast: bool = False,
    scope: str = "all",
    changed_files: List[str] | None = None,
) -> CallResult:
    """Run the repository validation wrapper and return its parsed result."""
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
    """Run catalog parity diagnostics and expose the full report in a CallResult."""
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
            "next_command": _repo_validation_command("status"),
        }
    if not status_result.data.get("is_git"):
        return {
            "state": "block",
            "severity": "blocker",
            "summary": "Repository root is not a git repository.",
            "source": "repo_status",
            "next_command": _repo_validation_command("status"),
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
            "next_command": _repo_validation_command("status"),
        }
    if not status_result.data.get("is_git"):
        return {
            "state": "skipped",
            "severity": "warning",
            "summary": "Projection sync not checked because the repository root is not a git repository.",
            "source": "repo_status",
            "next_command": _repo_validation_command("status"),
            "details": {"is_git": False},
        }
    return _workspace_projection_signal(
        status_result.data.get("skills_projection_state", "missing"),
        bool(status_result.data.get("skills_synced")),
    )


def _workspace_projection_signal(projection_state: str, skills_synced: bool) -> dict[str, Any]:
    """Render a projection verdict without treating an absent projection as healthy."""
    if skills_synced:
        return {
            "state": "pass", "severity": "info", "summary": "Workspace skill runtime appears synced.",
            "source": "repo_status", "details": {"skills_synced": True, "projection_state": projection_state},
        }
    unmaterialized = projection_state == "unmaterialized_linked_worktree"
    summaries = {
        "corrupt": "Workspace skill runtime projection is corrupted or unreadable.",
        "empty": "Workspace skill runtime projection is present but empty.",
        "unmaterialized_linked_worktree": "Workspace skill runtime is intentionally unmaterialized in this linked worktree.",
    }
    signal: dict[str, Any] = {
        "state": "warn" if unmaterialized else "block",
        "severity": "warning" if unmaterialized else "blocker",
        "summary": summaries.get(projection_state, "Workspace skill runtime does not appear synced."),
        "source": "repo_status",
        "details": {"skills_synced": False, "projection_state": projection_state},
    }
    if unmaterialized:
        signal["details"]["runtime_verification"] = "not_run"
        signal["next_command"] = SKILLS_SYNC_COMMAND
    else:
        signal["next_command"] = SKILLS_SYNC_COMMAND
    return signal


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
            "next_command": _repo_validation_command("doctor-catalog"),
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
        "next_command": _repo_validation_command("doctor-catalog"),
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


def _sdk_handles_signal(handles_result: CallResult) -> dict[str, Any]:
    report = handles_result.data.get("sdk_handles") or handles_result.data.get("command_surface", {})
    violations = report.get("violations") or []
    details = {
        "status": report.get("status"),
        "handle_count": report.get("handle_count"),
        "violation_count": len(violations),
    }
    if report.get("status") == "pass" and not violations:
        return {
            "state": "pass",
            "severity": "info",
            "summary": "SDK skill handles validate cleanly.",
            "source": "skills_handles",
            "details": details,
        }
    if violations:
        summary = f"SDK handle validation found {len(violations)} violation(s)."
    else:
        summary = _error_summary(handles_result, "SDK handle validation failed.")
    details["failure_code"] = "sdk_handle_validation_failed"
    return {
        "state": "block",
        "severity": "blocker",
        "summary": summary,
        "source": "skills_handles",
        "next_command": SDK_HANDLE_CHECK_COMMAND,
        "details": details,
    }


def _capability_readiness_signal(
    profiles_result: CallResult,
    events_result: CallResult,
) -> dict[str, Any]:
    profiles = profiles_result.data.get("skill_profiles", {})
    events = events_result.data.get("skill_events", {})
    profile_overview = profiles.get("readiness_overview", {})
    event_overview = events.get("readiness_overview", {})
    eval_blocker_classes = sorted(
        set(profiles.get("eval_blocker_classes", {})) | set(events.get("eval_blocker_classes", {}))
    )
    profile_gaps = int(profile_overview.get("contract_gap_count") or 0)
    event_gaps = int(event_overview.get("contract_gap_count") or 0)
    details = {
        "profile_status": profiles.get("status"),
        "profile_contract_status": profile_overview.get("contract_status"),
        "profile_contract_gap_count": profile_gaps,
        "profile_ready_sections": profile_overview.get("ready_contract_sections", []),
        "profile_blocked_sections": profile_overview.get("blocked_contract_sections", []),
        "event_status": events.get("status"),
        "event_contract_status": event_overview.get("contract_status"),
        "event_contract_gap_count": event_gaps,
        "event_ready_sections": event_overview.get("ready_contract_sections", []),
        "event_blocked_sections": event_overview.get("blocked_contract_sections", []),
        "eval_blocker_classes": eval_blocker_classes,
        "eval_blocker_class_count": len(eval_blocker_classes),
    }
    if profiles_result.status != "success":
        return {
            "state": "error",
            "severity": "blocker",
            "summary": _error_summary(profiles_result, "Skill profile readiness failed."),
            "source": "skills_profiles",
            "next_command": "./bin/ask skills profiles --json --robot",
            "details": details,
        }
    if events_result.status != "success":
        return {
            "state": "error",
            "severity": "blocker",
            "summary": _error_summary(events_result, "Skill lifecycle event readiness failed."),
            "source": "skills_events",
            "next_command": "./bin/ask skills events --json --robot",
            "details": details,
        }
    gap_count = profile_gaps + event_gaps
    if gap_count:
        return {
            "state": "block",
            "severity": "blocker",
            "summary": f"Skill capability readiness has {gap_count} contract gap(s).",
            "source": "skills_profiles+skills_events",
            "next_command": "./bin/ask skills profiles --json --robot",
            "details": details,
        }
    return {
        "state": "pass",
        "severity": "info",
        "summary": "Skill capability readiness contracts are ready.",
        "source": "skills_profiles+skills_events",
        "details": details,
    }


def _memory_readiness_signal(memory_result: CallResult) -> dict[str, Any]:
    memory = memory_result.data.get("skill_memory", {})
    source_summary = memory.get("source_summary", {})
    entry_summary = memory.get("entry_summary", {})
    entry_count = int(memory.get("entry_count") or 0)
    available_sources = source_summary.get("available_sources", [])
    details = {
        "status": memory.get("status"),
        "schema_version": memory.get("schema_version"),
        "provider_model": memory.get("provider_model"),
        "mode": memory.get("mode"),
        "query": memory.get("query"),
        "entry_count": entry_count,
        "total_count": int(memory.get("total_count") or entry_count),
        "source_count": source_summary.get("source_count", 0),
        "available_sources": available_sources,
        "missing_sources": source_summary.get("missing_sources", []),
        "by_source": entry_summary.get("by_source", {}),
        "by_freshness": entry_summary.get("by_freshness", {}),
        "validation_command": "./bin/ask skills memory search projection --json --robot",
    }
    if memory_result.status != "success":
        return {
            "state": "error",
            "severity": "blocker",
            "summary": _error_summary(memory_result, "Skill memory readiness failed."),
            "source": "skills_memory",
            "next_command": "./bin/ask skills memory search projection --json --robot",
            "details": details,
        }
    if not available_sources:
        return {
            "state": "warn",
            "severity": "warning",
            "summary": "Skill memory provider has no available source roots.",
            "source": "skills_memory",
            "next_command": "./bin/ask skills memory list --json --robot",
            "details": details,
        }
    if entry_count == 0:
        return {
            "state": "warn",
            "severity": "warning",
            "summary": "Skill memory provider is available but returned no projection evidence.",
            "source": "skills_memory",
            "next_command": "./bin/ask skills memory search projection --json --robot",
            "details": details,
        }
    return {
        "state": "pass",
        "severity": "info",
        "summary": "Skill memory provider returned searchable readiness evidence.",
        "source": "skills_memory",
        "details": details,
    }


def _package_readiness_signal(package_result: CallResult) -> dict[str, Any]:
    package = package_result.data.get("skill_package", {})
    package_contract = package.get("package_contract", {})
    required_fields = package_contract.get("required_fields", {})
    gate_summary = package.get("gate_summary", {})
    promotion_gate = package_contract.get("promotion_gate", {})
    install_gate = package_contract.get("install_gate", {})
    details = {
        "status": package.get("status"),
        "schema_version": package.get("schema_version"),
        "target": package.get("query"),
        "handle": package.get("handle"),
        "readiness_level": package_contract.get("readiness_level"),
        "present_fields": required_fields.get("present", []),
        "missing_fields": required_fields.get("missing", []),
        "missing_field_count": len(required_fields.get("missing", [])),
        "install_ready": gate_summary.get("install_ready"),
        "promotion_status": gate_summary.get("promotion_status"),
        "promotion_ready": gate_summary.get("promotion_ready"),
        "checkout_test_status": gate_summary.get("checkout_test_status"),
        "blocked_reasons": gate_summary.get("blocked_reasons", []),
        "share_ready": promotion_gate.get("share_ready"),
        "compatible_roles_declared": package_contract.get("role_compatibility", {}).get("declared"),
        "runtime_contract_declared": package_contract.get("runtime_contract", {}).get("declared"),
        "checkout_test_required": install_gate.get("checkout_test", {}).get("required"),
        "validation_command": (
            f"./bin/ask skills package {PACKAGE_READINESS_SENTINEL} "
            "--checkout-test --json --robot"
        ),
    }
    if package_result.status != "success":
        return {
            "state": "error",
            "severity": "blocker",
            "summary": _error_summary(package_result, "Skill package readiness failed."),
            "source": "skills_package",
            "next_command": details["validation_command"],
            "details": details,
        }
    if package.get("status") == "blocked":
        return {
            "state": "block",
            "severity": "blocker",
            "summary": package.get("agent_summary") or "Skill package readiness is blocked.",
            "source": "skills_package",
            "next_command": details["validation_command"],
            "details": details,
        }
    if package.get("status") == "warning" or details["blocked_reasons"]:
        return {
            "state": "warn",
            "severity": "warning",
            "summary": package.get("agent_summary") or "Skill package readiness has metadata gaps.",
            "source": "skills_package",
            "next_command": details["validation_command"],
            "details": details,
        }
    return {
        "state": "pass",
        "severity": "info",
        "summary": "Skill package readiness contract is ready.",
        "source": "skills_package",
        "details": details,
    }


def _repo_surface_signal(surface_result: CallResult) -> dict[str, Any]:
    report = surface_result.data.get("repo_surface", {})
    summary = report.get("summary", {})
    blocking_findings = summary.get("blocking_findings", 0)
    diagnostic_summary = _repo_surface_diagnostic_summary(summary)
    details = {
        "status": report.get("status"),
        "total_paths": summary.get("total_paths"),
        "blocking_findings": blocking_findings,
        "counts_by_code": summary.get("counts_by_code", {}),
        "blocking_counts_by_code": summary.get("blocking_counts_by_code", {}),
        "blocking_counts_by_classification": summary.get("blocking_counts_by_classification", {}),
        "diagnostic_summary": diagnostic_summary,
    }
    if surface_result.status != "success":
        return {
            "state": "error",
            "severity": "blocker",
            "summary": _error_summary(surface_result, "Repo surface inventory failed."),
            "source": "repo_surface",
            "next_command": _repo_validation_command("surface"),
            "details": details,
        }
    if report.get("status") == "warning" or blocking_findings:
        return {
            "state": "warn",
            "severity": "warning",
            "summary": _repo_surface_warning_summary(blocking_findings, diagnostic_summary),
            "source": "repo_surface",
            "next_command": _repo_validation_command("surface"),
            "details": details,
        }
    return {
        "state": "pass",
        "severity": "info",
        "summary": "Repo surface inventory has no diagnostic debt.",
        "source": "repo_surface",
        "details": details,
    }


def _top_count_items(counts: dict[str, Any], *, limit: int = 3) -> list[dict[str, int]]:
    normalized: list[dict[str, int]] = []
    for code, count in counts.items():
        if isinstance(code, str) and isinstance(count, int) and count > 0:
            normalized.append({"code": code, "count": count})
    return sorted(normalized, key=lambda item: (-item["count"], item["code"]))[:limit]


def _repo_surface_diagnostic_summary(summary: dict[str, Any]) -> dict[str, Any]:
    blocking_counts = summary.get("blocking_counts_by_code", {})
    if not isinstance(blocking_counts, dict) or not blocking_counts:
        blocking_counts = summary.get("counts_by_code", {})
    if not isinstance(blocking_counts, dict):
        blocking_counts = {}
    top_codes = _top_count_items(blocking_counts)
    return {
        "diagnostic_class": "repo_surface_ownership_debt",
        "top_blocking_codes": top_codes,
        "next_action": "classify_allowlist_or_cleanup_tracked_surface",
        "operator_rule": (
            "Do not flatten high-count repo-surface findings into generic "
            "nonblocking debt; report dominant categories, owner decision, "
            "and the next classification command."
        ),
    }


def _repo_surface_warning_summary(blocking_findings: int, diagnostic_summary: dict[str, Any]) -> str:
    top_codes = diagnostic_summary.get("top_blocking_codes", [])
    if isinstance(top_codes, list) and top_codes:
        formatted = ", ".join(
            f"{item['code']}={item['count']}"
            for item in top_codes
            if isinstance(item, dict) and item.get("code") and item.get("count")
        )
        if formatted:
            return (
                f"Repo surface has {blocking_findings} ownership diagnostic finding(s); "
                f"top categories: {formatted}."
            )
    return f"Repo surface has {blocking_findings} ownership diagnostic finding(s)."


def _unknown_signal_error_signal(exc: Exception) -> dict[str, Any]:
    return {
        "state": "error",
        "severity": "blocker",
        "summary": f"Repo doctor failed while composing signals: {type(exc).__name__}.",
        "source": "repo_doctor",
        "next_command": _repo_validation_command("status"),
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
    sdk_handles = _skipped_signal(
        f"SDK handle validation skipped {reason}.",
        "repo_status",
    )
    return {
        "catalog_parity": _skipped_signal(
            f"Catalog parity skipped {reason}.",
            "repo_status",
        ),
        "runtime_budget": _skipped_signal(
            f"Runtime budget skipped {reason}.",
            "repo_status",
        ),
        "sdk_handles": sdk_handles,
        "command_handles": sdk_handles,
        "capability_readiness": _skipped_signal(
            f"Capability readiness skipped {reason}.",
            "repo_status",
        ),
        "memory_readiness": _skipped_signal(
            f"Memory readiness skipped {reason}.",
            "repo_status",
        ),
        "package_readiness": _skipped_signal(
            f"Package readiness skipped {reason}.",
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


def _projection_skip_reason(signal_state: str | None, projection_state: str | None) -> str | None:
    if signal_state == "block":
        return "until workspace skill runtime projection is synced"
    if projection_state == "unmaterialized_linked_worktree":
        return "because this linked worktree intentionally has no runtime projection"
    return None


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
        elif skip_reason := _projection_skip_reason(
            projection_sync_signal.get("state"), status_result.data.get("skills_projection_state")
        ):
            signals.update(_repo_status_skipped_downstream_signals(skip_reason))
        else:
            sdk_handles_signal = _safe_signal(
                lambda: _sdk_handles_signal(
                    skills_handles(
                        repo_root,
                        check=True,
                        include_handles=False,
                    )
                )
            )
            signals.update(
                {
                    "catalog_parity": _safe_signal(
                        lambda: _catalog_parity_signal(doctor_catalog(repo_root))
                    ),
                    "runtime_budget": _safe_signal(
                        lambda: _runtime_budget_signal(skills_budget(repo_root))
                    ),
                    "sdk_handles": sdk_handles_signal,
                    "command_handles": sdk_handles_signal,
                    "capability_readiness": _safe_signal(
                        lambda: _capability_readiness_signal(
                            skills_profiles(repo_root),
                            skills_events(repo_root),
                        )
                    ),
                    "memory_readiness": _safe_signal(
                        lambda: _memory_readiness_signal(
                            skills_memory(repo_root, "search", query="projection", limit=3)
                        )
                    ),
                    "package_readiness": _safe_signal(
                        lambda: _package_readiness_signal(
                            skills_package(
                                repo_root,
                                PACKAGE_READINESS_SENTINEL,
                                checkout_test=True,
                            )
                        )
                    ),
                    "repo_surface": _safe_signal(
                        lambda: _repo_surface_signal(repo_surface(repo_root))
                    ),
                }
            )
    golden_path_signals = dict(signals)
    if "command_handles" in golden_path_signals:
        golden_path_signals.pop("sdk_handles", None)
    payload = build_golden_path_payload(
        signals=golden_path_signals,
        normal_next_command=_repo_validation_command("status"),
        signal_priorities=DOCTOR_SIGNAL_PRIORITY,
    )
    payload["signals"] = signals
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


def _git_output_text(repo_root: Path, args: list[str]) -> str:
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
    return process.stdout


def _git_output_lines(repo_root: Path, args: list[str]) -> list[str]:
    return [line.strip() for line in _git_output_text(repo_root, args).splitlines() if line.strip()]


def _shape_baseline(repo_root: Path, baseline_path: str | None) -> dict[str, Any]:
    deleted = [
        path
        for path in _git_output_lines(repo_root, ["diff", "--name-only", "--diff-filter=D", "HEAD", "--"])
        if path.endswith(".py")
    ]
    siblings: list[str] = []
    if baseline_path:
        relative = Path(baseline_path).resolve().relative_to(repo_root.resolve()).as_posix()
        parent = Path(relative).parent.as_posix()
        siblings = [
            path
            for path in _git_output_lines(repo_root, ["ls-files", "--", f"{parent}/*.py"])
            if path.endswith(".py")
        ]
    paths = list(dict.fromkeys([*deleted, *siblings]))
    head_text = {path: _git_output_text(repo_root, ["show", f"HEAD:{path}"]) for path in paths}
    return {"deleted_python_paths": deleted, "sibling_python_paths": siblings, "head_text": head_text}


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


def _validation_command_for_changed_files(changed_files: list[str]) -> str:
    if not changed_files:
        return _repo_validation_command("validate")
    return _repo_validation_command("validate", "--changed-files", *changed_files)


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
    if canonical_skill_changed and not generated_changed:
        commands.append(SKILLS_SYNC_COMMAND)
    flat_source_projection_present = False
    projection_update_present = bool(canonical_skill_changed and generated_changed)
    if canonical_skill_changed or generated_changed:
        validation_commands.append(SDK_HANDLE_CHECK_COMMAND)
    return {
        "needed": bool(commands),
        "commands": commands,
        "validation_commands": validation_commands,
        "generated_changed_files": generated_changed,
        "canonical_skill_changed_files": canonical_skill_changed,
        "projection_update_present": projection_update_present,
        "flat_source_projection_present": flat_source_projection_present,
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
        "blocking_counts_by_code": details.get("blocking_counts_by_code", {}),
        "blocking_counts_by_classification": details.get("blocking_counts_by_classification", {}),
        "diagnostic_summary": details.get("diagnostic_summary", {}),
    }


def _closeout_capability_readiness(doctor_payload: dict[str, Any]) -> dict[str, Any]:
    signal = doctor_payload.get("signals", {}).get("capability_readiness", {})
    details = signal.get("details", {})
    profile_gap_count = int(details.get("profile_contract_gap_count") or 0)
    event_gap_count = int(details.get("event_contract_gap_count") or 0)
    return {
        "status": signal.get("state"),
        "summary": signal.get("summary"),
        "profile_contract_status": details.get("profile_contract_status"),
        "profile_contract_gap_count": profile_gap_count,
        "profile_ready_sections": details.get("profile_ready_sections", []),
        "profile_blocked_sections": details.get("profile_blocked_sections", []),
        "event_contract_status": details.get("event_contract_status"),
        "event_contract_gap_count": event_gap_count,
        "event_ready_sections": details.get("event_ready_sections", []),
        "event_blocked_sections": details.get("event_blocked_sections", []),
        "eval_blocker_classes": details.get("eval_blocker_classes", []),
        "eval_blocker_class_count": int(details.get("eval_blocker_class_count") or 0),
        "contract_gap_count": profile_gap_count + event_gap_count,
    }


def _closeout_memory_readiness(doctor_payload: dict[str, Any]) -> dict[str, Any]:
    signal = doctor_payload.get("signals", {}).get("memory_readiness", {})
    details = signal.get("details", {})
    return {
        "status": signal.get("state"),
        "summary": signal.get("summary"),
        "provider_model": details.get("provider_model"),
        "schema_version": details.get("schema_version"),
        "entry_count": int(details.get("entry_count") or 0),
        "total_count": int(details.get("total_count") or 0),
        "available_sources": details.get("available_sources", []),
        "missing_sources": details.get("missing_sources", []),
        "by_source": details.get("by_source", {}),
        "by_freshness": details.get("by_freshness", {}),
        "validation_command": details.get("validation_command"),
    }


def _closeout_package_readiness(doctor_payload: dict[str, Any]) -> dict[str, Any]:
    """
    Extract package readiness information from a doctor payload into a normalized closeout report.
    
    Parameters:
        doctor_payload (dict[str, Any]): The payload returned by `repo_doctor` (typically `result.data`), expected to contain `signals.package_readiness`.
    
    Returns:
        dict[str, Any]: A mapping with the following keys:
            - status: The signal state (`"pass"`, `"warning"`, `"block"`, `"skipped"`, etc.).
            - summary: Short human-readable summary of package readiness.
            - target: The package target identifier or path the readiness report refers to.
            - schema_version: Declared package schema/version when present.
            - readiness_level: Contract-readiness classification from the package report.
            - missing_fields: List of contract fields that are missing.
            - missing_field_count: Integer count of missing contract fields (0 when absent).
            - install_ready: Boolean indicating whether the package is installable.
            - promotion_status: Current promotion classification or status string.
            - promotion_ready: Boolean indicating whether the package is ready for promotion.
            - checkout_test_status: Result of any checkout/test performed for the package.
            - blocked_reasons: List of strings explaining why the package is blocked.
            - validation_command: A recommended command string to run package readiness validation.
    """
    signal = doctor_payload.get("signals", {}).get("package_readiness", {})
    details = signal.get("details", {})
    return {
        "status": signal.get("state"),
        "summary": signal.get("summary"),
        "target": details.get("target"),
        "schema_version": details.get("schema_version"),
        "readiness_level": details.get("readiness_level"),
        "missing_fields": details.get("missing_fields", []),
        "missing_field_count": int(details.get("missing_field_count") or 0),
        "install_ready": details.get("install_ready"),
        "promotion_status": details.get("promotion_status"),
        "promotion_ready": details.get("promotion_ready"),
        "checkout_test_status": details.get("checkout_test_status"),
        "blocked_reasons": details.get("blocked_reasons", []),
        "validation_command": details.get("validation_command"),
    }


def _closeout_focused_validation(repo_root: Path, changed_files: list[str]) -> list[dict[str, Any]]:
    """
    Builds a prioritized list of validation commands to run for a focused closeout.
    
    Includes a core set of readiness checks (doctor, profiles, events, memory, package) and conditionally appends:
    - an SDK handle check when any changed path is within generated surface prefixes,
    - a runtime-evidence schema validation when any changed path points under the repository's runtime evidence root,
    - a scoped `repo validate` invocation when changed files are present, or a `repo status` check when none are present.
    
    Parameters:
        repo_root (Path): Repository root used to normalize and evaluate runtime-evidence paths.
        changed_files (list[str]): Changed-file paths (absolute or repo-relative) used to determine which conditional checks to include.
    
    Returns:
        list[dict[str, Any]]: Ordered list of validation command descriptors, each containing `id`, `reason`, and `command`.
    """
    commands = [
        {
            "id": "repo_doctor",
            "reason": "Confirm golden-path health before claiming completion.",
            "command": _repo_validation_command("doctor"),
        },
        {
            "id": "skill_profiles_readiness",
            "reason": "Validate skill operation-profile readiness contracts directly.",
            "command": "./bin/ask skills profiles --json --robot",
        },
        {
            "id": "skill_events_readiness",
            "reason": "Validate skill lifecycle-event readiness contracts directly.",
            "command": "./bin/ask skills events --json --robot",
        },
        {
            "id": "skill_memory_readiness",
            "reason": "Validate searchable skill memory provider evidence directly.",
            "command": "./bin/ask skills memory search projection --json --robot",
        },
        {
            "id": "skill_package_readiness",
            "reason": "Validate version and role-aware package readiness directly.",
            "command": (
                f"./bin/ask skills package {PACKAGE_READINESS_SENTINEL} "
                "--checkout-test --json --robot"
            ),
        }
    ]
    if any(path.startswith(GENERATED_SURFACE_PREFIXES) for path in changed_files):
        commands.append(
            {
                "id": "skill_handles",
                "reason": "Validate SDK handle projection for changed projection files.",
                "command": SDK_HANDLE_CHECK_COMMAND,
            }
        )
    if any(_is_runtime_evidence_path(repo_root, path) for path in changed_files):
        commands.append(
            {
                "id": "runtime_evidence_cards",
                "reason": "Validate changed shared-workspace runtime evidence artifacts.",
                "command": _runtime_evidence_validation_command(repo_root),
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
                "command": _repo_validation_command("status"),
            }
        )
    return commands


def _runtime_evidence_validation_command(repo_root: Path, card_paths: list[Path] | None = None) -> str:
    """
    Builds the shell command to validate runtime evidence cards for the given repository.
    
    Parameters:
        repo_root (Path): Repository root used as the workspace root argument in the command; it will be resolved to an absolute path.
    
    Returns:
        command (str): A single shell command string that invokes validate_runtime_cards.py with the evidence directory, `--require-shared-workspace`, the resolved workspace root, and `--json`. The command tokens are shell-quoted where appropriate.
    """
    validator_path = RUNTIME_EVIDENCE_VALIDATOR
    if not (repo_root / validator_path).exists():
        validator_path = Path(__file__).resolve().parents[4] / "scripts" / "validation-and-linting" / "validate_runtime_cards.py"
    parts = ["python3", str(validator_path)]
    if card_paths:
        for card_path in card_paths:
            try:
                parts.append(str(card_path.relative_to(repo_root)))
            except ValueError:
                parts.append(str(card_path))
    else:
        parts.extend(["--evidence-dir", RUNTIME_EVIDENCE_ROOT])
    parts.extend(["--require-shared-workspace", "--workspace-root", str(repo_root.resolve()), "--json"])
    return " ".join(shlex.quote(part) for part in parts)


def _runtime_evidence_schema_validation(repo_root: Path, card_paths: list[Path]) -> dict[str, Any]:
    command = _runtime_evidence_validation_command(repo_root, card_paths)
    existing_cards = [path for path in card_paths if path.exists() and not path.is_symlink()]
    if not existing_cards:
        return {
            "status": "not_run",
            "command": command,
            "reason": "No existing changed RuntimeCard files to schema-validate.",
        }
    process = subprocess.run(
        shlex.split(command),
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        timeout=SCRIPT_TIMEOUT_SECONDS,
        check=False,
    )
    try:
        payload = json.loads(process.stdout) if process.stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {"raw_stdout": process.stdout}
    return {
        "status": "pass" if process.returncode == 0 else "fail",
        "command": command,
        "returncode": process.returncode,
        "findings": payload.get("findings", []) if isinstance(payload, dict) else [],
        "checked": payload.get("checked", []) if isinstance(payload, dict) else [],
        "stderr": process.stderr.strip(),
    }


def _normalize_changed_path(repo_root: Path, path: str) -> str:
    """
    Normalize a changed-file path to a repository-relative POSIX path when possible.
    
    Parameters:
        repo_root (Path): Repository root used to compute a relative path.
        path (str): File path to normalize; may be absolute or relative.
    
    Returns:
        str: If `path` is inside `repo_root`, a repository-relative POSIX path is returned.
             If `path` is an absolute path not under `repo_root`, the original absolute path string is returned.
             For relative inputs, a leading "./" is removed if present.
    """
    path_obj = Path(path)
    if path_obj.is_absolute():
        try:
            return path_obj.resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            return str(path_obj)
    return path.removeprefix("./")


def _is_runtime_evidence_path(repo_root: Path, path: str) -> bool:
    """
    Determine whether a changed-file path falls under the runtime evidence root.
    
    Parameters:
        repo_root (Path): Repository root used to normalize absolute paths.
        path (str): Changed-file path (absolute or relative) to normalize and test.
    
    Returns:
        True if the normalized repo-relative path starts with '.harness/evidence/runtime-proof/', False otherwise.
    """
    return _normalize_changed_path(repo_root, path).startswith(RUNTIME_EVIDENCE_ROOT + "/")


def _changed_runtime_card_paths(repo_root: Path, changed_files: list[str]) -> list[Path]:
    """
    Return the list of runtime-card.json file paths that are affected by a set of changed files under the runtime evidence root.
    
    Parameters:
        repo_root (Path): Repository root used to resolve relative changed-file paths.
        changed_files (list[str]): Changed file paths (absolute or relative) to inspect.
    
    Returns:
        list[Path]: Sorted, unique Paths for changed files whose normalized repo-relative path starts with
        RUNTIME_EVIDENCE_ROOT + "/" and ends with "/runtime-card.json".
    """
    paths = []
    for changed_file in changed_files:
        normalized = _normalize_changed_path(repo_root, changed_file)
        if normalized.startswith(RUNTIME_EVIDENCE_ROOT + "/") and normalized.endswith("/runtime-card.json"):
            paths.append(repo_root / normalized)
    return sorted(set(paths))


def _runtime_card_summary(repo_root: Path, path: Path) -> dict[str, Any]:
    """
    Summarizes a runtime-card.json file located under the repository root.
    
    Reads and parses the JSON file at `path` (relative to `repo_root`) and classifies its read status. Handles these cases:
    - If `path` is a symlink: marks the card as invalid with an explanatory error.
    - If the file cannot be read because it no longer exists: marks the card as deleted.
    - If the file cannot be read for other I/O reasons or contains invalid JSON or is not a JSON object: marks the card as invalid and includes an error message.
    - Otherwise extracts common card fields and counts `evidence_receipts`.
    
    Parameters:
        repo_root (Path): Repository root used to produce a repo-relative `path` string in the summary.
        path (Path): Absolute or resolved path to a runtime-card.json file.
    
    Returns:
        dict: A summary dictionary containing at least:
            - "path" (str): Repo-relative path to the file.
            - "read_status" (str): One of "readable", "deleted", or "invalid".
            - If "invalid" or "deleted": may include "error" (str) with a human-readable message.
            - If "readable": may include the extracted card fields:
                - "card_id"
                - "created_at"
                - "skill_handle"
                - "sdk_skill_name"
                - "runtime_target"
                - "runtime_status"
                - "workspace_root"
                - "receipt_count" (int): number of items in `evidence_receipts` when present.
    """
    relative_path = str(path.relative_to(repo_root))
    if path.is_symlink():
        return {
            "path": relative_path,
            "read_status": "invalid",
            "error": "RuntimeCard path must not be a symlink.",
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        if not path.exists():
            return {
                "path": relative_path,
                "read_status": "deleted",
                "error": "RuntimeCard path no longer exists.",
            }
        return {
            "path": relative_path,
            "read_status": "invalid",
            "error": f"RuntimeCard read failed: {exc}",
        }
    except json.JSONDecodeError as exc:
        return {
            "path": relative_path,
            "read_status": "invalid",
            "error": f"invalid JSON: {exc}",
        }
    if not isinstance(payload, dict):
        return {
            "path": relative_path,
            "read_status": "invalid",
            "error": "RuntimeCard payload is not a JSON object.",
        }
    receipts = payload.get("evidence_receipts")
    receipt_count = len(receipts) if isinstance(receipts, list) else 0
    return {
        "path": relative_path,
        "read_status": "readable",
        "card_id": payload.get("card_id"),
        "created_at": payload.get("created_at"),
        "skill_handle": payload.get("skill_handle"),
        "sdk_skill_name": payload.get("sdk_skill_name") or payload.get("skill_handle"),
        "runtime_target": payload.get("runtime_target"),
        "runtime_status": payload.get("runtime_status"),
        "workspace_root": payload.get("workspace_root"),
        "receipt_count": receipt_count,
    }


def _runtime_card_scope_summary(runtime_cards: list[dict[str, Any]], *, empty_status: str) -> dict[str, Any]:
    """
    Builds an aggregate summary of a collection of runtime card summaries and classifies their overall scope status.
    
    Parameters:
        runtime_cards (list[dict[str, Any]]): Per-card summaries each containing at least a `read_status` key.
        empty_status (str): Status to use when `runtime_cards` is empty.
    
    Returns:
        dict[str, Any]: Summary containing:
            - `status` (str): One of `empty_status` (when no cards), `invalid` (any card not `readable` or `deleted`), `deleted` (all cards are `deleted`), or `present` (at least one readable card).
            - `runtime_card_count` (int): Total number of cards examined.
            - `invalid_runtime_card_count` (int): Number of cards whose `read_status` is neither `readable` nor `deleted`.
            - `deleted_runtime_card_count` (int): Number of cards with `read_status == "deleted"`.
            - `runtime_cards` (list[dict[str, Any]]): The original list of card summaries.
    """
    invalid_cards = [
        card for card in runtime_cards if card.get("read_status") not in {"readable", "deleted"}
    ]
    deleted_cards = [card for card in runtime_cards if card.get("read_status") == "deleted"]
    status = empty_status
    if runtime_cards:
        if invalid_cards:
            status = "invalid"
        elif len(deleted_cards) == len(runtime_cards):
            status = "deleted"
        else:
            status = "present"
    return {
        "status": status,
        "runtime_card_count": len(runtime_cards),
        "invalid_runtime_card_count": len(invalid_cards),
        "deleted_runtime_card_count": len(deleted_cards),
        "runtime_cards": runtime_cards,
    }


def _closeout_runtime_evidence(repo_root: Path, *, include_cards: bool, changed_files: list[str]) -> dict[str, Any]:
    """
    Summarize runtime-evidence ("runtime-card.json") files for closeout and optionally report only the changed subset.
    
    Parameters:
        repo_root (Path): Repository root used to locate the runtime evidence directory.
        include_cards (bool): When True, discover and summarize runtime-card files; when False, skip discovery and return a skipped report.
        changed_files (list[str]): List of changed paths used to determine the changed-scope subset.
    
    Returns:
        dict: A closeout report containing:
            - status (str): One of "present", "invalid", "deleted", "not_applicable", or "skipped" describing the changed-scope outcome.
            - evidence_root (str): Relative evidence root path constant used for discovery.
            - runtime_card_count (int): Number of runtime cards in the reported (changed) scope.
            - invalid_runtime_card_count (int): Number of runtime cards in the reported scope with invalid read/parse status.
            - deleted_runtime_card_count (int): Number of runtime cards in the reported scope marked deleted.
            - runtime_cards (list[dict]): List of per-card summaries for the reported (changed) scope.
            - changed_scope (dict): Scope summary for changed cards (counts, status, and the `runtime_cards` list).
            - workspace_scope (dict): Scope summary for all workspace cards discovered under the evidence root.
            - schema_validation (dict): Contains `status` ("not_run") and the `command` string to validate runtime card schema.
            - truth_boundaries (dict): Indicators describing which proofs are considered by closeout (e.g., command_proof, schema_proof, pr_truth, tracker_truth, docs_truth).
    """
    evidence_root = repo_root / RUNTIME_EVIDENCE_ROOT
    validation_command = _runtime_evidence_validation_command(repo_root)
    if not include_cards:
        skipped_scope = _runtime_card_scope_summary([], empty_status="skipped")
        return {
            "status": "skipped",
            "reason": "Runtime evidence discovery runs only for changed closeout.",
            "evidence_root": RUNTIME_EVIDENCE_ROOT,
            "runtime_card_count": 0,
            "invalid_runtime_card_count": 0,
            "deleted_runtime_card_count": 0,
            "runtime_cards": [],
            "changed_scope": skipped_scope,
            "workspace_scope": skipped_scope,
            "schema_validation": {
                "status": "not_run",
                "command": validation_command,
            },
            "truth_boundaries": {
                "command_proof": "not_checked_by_repo_closeout",
                "schema_proof": "not_run_by_closeout_use_schema_validation_command",
                "pr_truth": "not_checked_by_repo_closeout",
                "tracker_truth": "not_checked_by_repo_closeout",
                "docs_truth": "not_checked_by_repo_closeout",
            },
        }
    workspace_cards = (
        [_runtime_card_summary(repo_root, path) for path in sorted(evidence_root.rglob("runtime-card.json"))]
        if evidence_root.exists()
        else []
    )
    changed_card_paths = _changed_runtime_card_paths(repo_root, changed_files)
    changed_cards = [_runtime_card_summary(repo_root, path) for path in changed_card_paths]
    changed_scope = _runtime_card_scope_summary(changed_cards, empty_status="not_applicable")
    schema_validation = _runtime_evidence_schema_validation(repo_root, changed_card_paths)
    if changed_scope["status"] == "present" and schema_validation["status"] == "fail":
        changed_scope = {
            **changed_scope,
            "status": "invalid",
            "invalid_runtime_card_count": changed_scope["runtime_card_count"],
        }
    workspace_scope = _runtime_card_scope_summary(workspace_cards, empty_status="missing")
    return {
        "status": changed_scope["status"],
        "evidence_root": RUNTIME_EVIDENCE_ROOT,
        "runtime_card_count": changed_scope["runtime_card_count"],
        "invalid_runtime_card_count": changed_scope["invalid_runtime_card_count"],
        "deleted_runtime_card_count": changed_scope["deleted_runtime_card_count"],
        "runtime_cards": changed_scope["runtime_cards"],
        "changed_scope": changed_scope,
        "workspace_scope": workspace_scope,
        "schema_validation": schema_validation,
        "truth_boundaries": {
            "command_proof": "workspace_runtime_evidence",
            "schema_proof": "checked_by_repo_closeout" if schema_validation["status"] in {"pass", "fail"} else "not_run_by_closeout_use_schema_validation_command",
            "pr_truth": "not_checked_by_repo_closeout",
            "tracker_truth": "not_checked_by_repo_closeout",
            "docs_truth": "not_checked_by_repo_closeout",
        },
    }


def _diagnostic_debt_next_command(diagnostic_debt: list[dict[str, Any]]) -> str | None:
    """
    Select the first non-empty `next_command` from a diagnostic-debt list.
    
    Parameters:
        diagnostic_debt (list[dict[str, Any]]): Ordered diagnostic-debt entries; each entry may include a `next_command` string.
    
    Returns:
        str | None: The first `next_command` that is a non-empty string, or `None` if none are present.
    """
    for debt in diagnostic_debt:
        next_command = debt.get("next_command") if isinstance(debt, dict) else None
        if isinstance(next_command, str) and next_command.strip():
            return next_command
    return None


def repo_closeout(repo_root: Path, changed: bool = False, strict: bool = False) -> CallResult:
    """
    Build a closeout readiness report describing detected blockers and a recommended next command.
    
    Parameters:
        repo_root (Path): Repository root to analyze.
        changed (bool): When True, detect changed files and run changed-scope validations including runtime-evidence checks.
        strict (bool): When True, treat existing diagnostic debt as a blocker for closeout.
    
    Returns:
        CallResult: Result whose `data["repo_closeout"]` contains the closeout payload with at least the following keys:
            - agent_summary: human-readable readiness summary.
            - changed_files, changed_file_count, changed_mode_requested, changed_files_error
            - sync: sync report and suggested sync/validation commands.
            - runtime_budget, capability_readiness, memory_readiness, package_readiness, surface_policy
            - runtime_evidence: runtime-evidence closeout report (changed and workspace scope).
            - focused_validation: list of focused validation commands for closeout.
            - diagnostic_debt: diagnostic debt entries from the doctor payload.
            - commit_readiness: { ready (bool), blockers (list[str]), strict (bool) }.
            - doctor: original doctor payload used to build the report.
            - next_command: suggested command to address the highest-priority blocker (or status command if ready).
    
        The CallResult `status` is set to "success" when ready (no blockers) and "error" otherwise; when blocked an ErrorObject with code `ERR_VALIDATION` is appended describing the blocking summary and suggested fix.
    """
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
    focused_validation = _closeout_focused_validation(repo_root, changed_files)
    runtime_evidence = _closeout_runtime_evidence(repo_root, include_cards=changed, changed_files=changed_files)
    if strict and diagnostic_debt:
        blockers.append("strict_diagnostic_debt")
    runtime_evidence_status = runtime_evidence.get("changed_scope", {}).get("status")
    if runtime_evidence_status == "invalid":
        blockers.append("runtime_evidence_invalid")
    if runtime_evidence_status == "deleted":
        blockers.append("runtime_evidence_deleted")
    ready = not blockers
    next_command: str | None
    if changed_files_error:
        next_command = _repo_validation_command("status")
    elif doctor_payload.get("blocking"):
        next_command = doctor_payload.get("next_command")
    elif sync_report["needed"]:
        next_command = sync_report["commands"][0]
    elif strict and diagnostic_debt:
        next_command = (
            _diagnostic_debt_next_command(diagnostic_debt)
            or doctor_payload.get("next_command")
            or _repo_validation_command("doctor")
        )
    elif "runtime_evidence_invalid" in blockers or "runtime_evidence_deleted" in blockers:
        next_command = runtime_evidence["schema_validation"]["command"]
    elif sync_report["validation_commands"]:
        next_command = sync_report["validation_commands"][0]
    elif changed_files:
        next_command = _validation_command_for_changed_files(changed_files)
    else:
        next_command = _repo_validation_command("status")

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
        "capability_readiness": _closeout_capability_readiness(doctor_payload),
        "memory_readiness": _closeout_memory_readiness(doctor_payload),
        "package_readiness": _closeout_package_readiness(doctor_payload),
        "surface_policy": _closeout_surface_policy(doctor_payload),
        "runtime_evidence": runtime_evidence,
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
    result.data["validation_commands"] = [_repo_validation_command("provider-audit")]
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
    result.data["validation_commands"] = [_repo_validation_command("surface", strict=strict)]
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
    validation_args = ["--changed-files", *changed_files] if changed_files else []
    result.data["validation_commands"] = [_repo_validation_command("check-stability", *validation_args)]

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
