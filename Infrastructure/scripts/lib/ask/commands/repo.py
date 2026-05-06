import subprocess
import json
import re
import sys
from pathlib import Path
from typing import Any, List
from ask.envelope import CallResult, ErrorCode, ErrorObject
from ask.catalog_parity import compute_catalog_parity
from ask.commands.skills import skills_budget, skills_handles
from ask.golden_path import build_golden_path_payload

SCRIPT_TIMEOUT_SECONDS = 60

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
        
    stdout_chunks: List[str] = []
    with subprocess.Popen(
        cmd,
        cwd=str(repo_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    ) as process:
        assert process.stdout is not None
        for line in process.stdout:
            stdout_chunks.append(line)
            # Preserve machine-readable stdout for the final envelope while still
            # showing long-running validation progress to operators in real time.
            print(line, end="", file=sys.stderr)
        process.wait()
    
    # Parse output for summary
    stdout = "".join(stdout_chunks)
    required_failures = 0
    warn_only_issues = 0

    # Handle early exit case where validation script fails before producing summary
    if "- required_failures:" not in stdout and "- warn_only_issues:" not in stdout:
        result.data["required_failures"] = 1  # Assume failure if no summary lines
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
    
    if process.returncode == 0:
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


def repo_doctor(repo_root: Path) -> CallResult:
    """Compose repo health checks into one compact agent-facing doctor payload."""
    result = CallResult()
    try:
        status_result = repo_status(repo_root)
        signals = {
            "repo_status": _repo_status_signal(status_result),
            "projection_sync": _projection_sync_signal(status_result),
            "catalog_parity": _catalog_parity_signal(doctor_catalog(repo_root)),
            "runtime_budget": _runtime_budget_signal(skills_budget(repo_root)),
            "command_handles": _command_handles_signal(
                skills_handles(repo_root, check=True, include_handles=False)
            ),
            "repo_surface": _repo_surface_signal(repo_surface(repo_root)),
        }
    except Exception as exc:
        signals = {
            "unknown_signal_error": _unknown_signal_error_signal(exc),
        }
    payload = build_golden_path_payload(
        signals=signals,
        normal_next_command="./bin/ask repo status --json --robot",
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


def check_hub_stability(repo_root: Path, changed_files: List[str] = None) -> CallResult:
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
        except Exception:
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
                            errors.append(
                                f"STABLE SKILL DELETED: '{skill}' is marked stable and was deleted "
                                f"without a deprecation notice. Add a ## Deprecation section to the "
                                f"last committed version before removal."
                            )
                    except Exception as e:
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
            except Exception:
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
