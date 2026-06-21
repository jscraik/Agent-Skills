from __future__ import annotations

import os
import hashlib
import json
import shlex
import shutil
import subprocess
import re
import sys
import importlib.util
import tempfile
import difflib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional, Protocol

SCRIPTS_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = SCRIPTS_ROOT.parents[1]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.append(str(SCRIPTS_ROOT))
if str(SCRIPTS_ROOT / "lifecycle-and-sync") not in sys.path:
    sys.path.append(str(SCRIPTS_ROOT / "lifecycle-and-sync"))

from ask.envelope import CallResult, ErrorObject  # noqa: E402
from ask.commands.memory import (  # noqa: E402
    MEMORY_SOURCES,
    memory_list as _memory_provider_list,
    memory_read as _memory_provider_read,
    memory_search as _memory_provider_search,
)
from ask.services.plugin_cache import (  # noqa: E402
    PLUGIN_CACHE_PERMISSION_RERUN,
    plugin_cache_permission_declaration,
    prune_command_surface_duplicate_skill_entries,
    refresh_workspace_plugin_caches,
)
from ask.services.plugin_sources import (  # noqa: E402
    copy_directory_contents as _copy_directory_contents,
    load_local_marketplace as _load_local_marketplace,
    materialize_first_level_skill_aliases as _materialize_first_level_skill_aliases,
)
from ask.services.codex_preview import (  # noqa: E402
    CODEX_PREVIEW_MODELED_RULE_VERSION,
    CODEX_PREVIEW_SCHEMA_VERSION,
    CODEX_PREVIEW_SOURCE_FILES,
    build_codex_config_explain,
    build_codex_implicit_preview,
    build_codex_inject_preview,
    build_codex_load_preview,
    build_codex_render_preview,
)
from ask.skills_sdk.contracts import (  # noqa: E402
    DOCTOR_BLOCKER_TAXONOMY,
    DOCTOR_SDK_LAYERS,
    DOCTOR_WARNING_TAXONOMY,
    EVAL_BLOCKER_CLASSES,
    PACKAGE_CONTRACT_FIELDS,
    ask_validation_command as _ask_validation_command,
    doctor_blocker as _doctor_blocker,
    doctor_contract_schema_refs as _doctor_contract_schema_refs,
    doctor_contract_schema_versions as _doctor_contract_schema_versions,
    doctor_sdk_layer_for as _doctor_sdk_layer_for,
    doctor_warning as _doctor_warning,
    read_skill_frontmatter_fields as _read_skill_frontmatter_fields,
    runtime_failure_payload as _runtime_failure_payload,
    skill_doctor_check_summary as _skill_doctor_check_summary,
    skill_target_summary as _skill_target_summary,
    skills_validation_command as _skills_validation_command,
    status_from_bool as _status_from_bool,
)
from ask.skills_sdk.runtime_adapters import (  # noqa: E402
    EVIDENCE_RUNTIME_TARGETS,
    SUPPORTED_RUNTIME_TARGETS,
    build_sdk_skill_proof,
    emit_sdk_skill_runtime_evidence,
    normalize_runtime_target,
)
from ask.skills_sdk.package_contracts import (  # noqa: E402
    SKILL_PACKAGE_READINESS_SCHEMA_PATH,
    SKILL_PACKAGE_READINESS_SCHEMA_VERSION,
    SKILL_PACKAGE_SCHEMA_PATH,
    SKILL_PACKAGE_SCHEMA_VERSION,
    SKILL_OPTIMIZATION_CONTRACT_SCHEMA_PATH,
    SKILL_OPTIMIZATION_CONTRACT_SCHEMA_VERSION,
    SKILLFLOW_SCHEMA_PATH,
    SKILLFLOW_SCHEMA_VERSION,
    capability_metadata_status as _capability_metadata_status,
    empty_skill_package_contract as _empty_skill_package_contract,
    refresh_package_promotion_gate as _refresh_package_promotion_gate,
    sdk_package_contract as _sdk_package_contract,
    skill_package_checkout_test as _skill_package_checkout_test,
    skill_package_compatibility_snapshot as _skill_package_compatibility_snapshot,
    skill_package_contract as _skill_package_contract,
    skill_package_gate_summary as _skill_package_gate_summary,
    skill_package_readiness as _skill_package_readiness,
    skill_package_readiness_summary as _skill_package_readiness_summary,
)
from ask.skills_sdk.conformance import run_skills_conformance as _run_skills_conformance  # noqa: E402
from ask.skills_sdk.package_verify import (  # noqa: E402
    PACKAGE_VERIFY_SCHEMA_VERSION,
    verify_archive_package as _verify_archive_package,
    verify_skill_directory as _verify_skill_directory,
)
from ask.skills_sdk.risk import build_risk_classification as _build_risk_classification  # noqa: E402
from ask.skills_sdk.install_preview import build_install_preview as _build_install_preview  # noqa: E402
from ask.skills_sdk.ir import build_skill_ir as _build_skill_ir  # noqa: E402
from ask.skills_sdk.docs_projection import verify_capability_docs_projection as _verify_capability_docs_projection  # noqa: E402
from ask.skills_sdk.package_build import build_package_digest_receipt as _build_package_digest_receipt  # noqa: E402
from ask.skills_sdk.package_hardening import build_package_hardening_receipt as _build_package_hardening_receipt  # noqa: E402
from ask.skills_sdk.eval_runner import internal_scorecard_quality_gates as _internal_scorecard_quality_gates  # noqa: E402
from ask.skills_sdk.eval_runner import run_deterministic_eval as _run_deterministic_eval  # noqa: E402
from ask.skills_sdk.eval_ab_rubric import build_ab_rubric_preview_receipt as _build_ab_rubric_preview_receipt  # noqa: E402
from ask.skills_sdk.eval_ab_preview import build_ab_preview_receipt as _build_ab_preview_receipt  # noqa: E402
from ask.skills_sdk.eval_ab_plan import build_ab_plan_receipt as _build_ab_plan_receipt  # noqa: E402
from ask.skills_sdk.eval_ab_run import build_ab_run_receipt as _build_ab_run_receipt  # noqa: E402
from ask.skills_sdk.eval_ab_judge import build_ab_judge_preview_receipt as _build_ab_judge_preview_receipt  # noqa: E402
from ask.skills_sdk.eval_ab_judge import build_ab_judge_score_receipt as _build_ab_judge_score_receipt  # noqa: E402
from ask.skills_sdk.eval_profiles import build_eval_profile_preview_receipt as _build_eval_profile_preview_receipt  # noqa: E402
from ask.skills_sdk.sandbox_profile import (  # noqa: E402
    SandboxProfileError as _SandboxProfileError,
    build_sandbox_profile_receipt as _build_sandbox_profile_receipt,
)
from ask.skills_sdk.project_install import (  # noqa: E402
    ProjectInstallError as _ProjectInstallError,
    install_project_skill as _install_project_skill,
)
from ask.skills_sdk.project_cleanup import (  # noqa: E402
    ProjectCleanupError as _ProjectCleanupError,
    rollback_project_install as _rollback_project_install,
    uninstall_project_skill as _uninstall_project_skill,
)
from ask.skills_sdk.project_conformance import (  # noqa: E402
    ProjectConformanceError as _ProjectConformanceError,
    build_project_conformance_receipt as _build_project_conformance_receipt,
)
from ask.skills_sdk.placeholder_lifecycle import (  # noqa: E402
    build_placeholder_lifecycle_receipts as _build_placeholder_lifecycle_receipts,
)
from ask.skills_sdk.capability_status import (  # noqa: E402
    CapabilityStatusError as _CapabilityStatusError,
    build_capability_status as _build_capability_status,
)
from skill_discovery import (  # noqa: E402
    USER_SKILL_SCOPE_PRECEDENCE,
    classify_skill_scope,
    discover_catalog_entries,
    discover_skill_entries,
    get_policy_identity,
    render_index,
)
from selection_policy import REPO_SCAN_ROOTS, SYSTEM_BRIDGE_SKILL_NAMES  # noqa: E402
from projection_engine import (  # noqa: E402
    ProjectionModeDecision,
    ProjectionModeError,
    build_projection_plan_metadata,
    normalize_projection_mode,
)
from command_surface import (  # noqa: E402
    parse_sdk_references,
    resolve_reviewer_handle,
    resolve_skill_handle,
)
from sdk_skill_registry import (  # noqa: E402
    build_sdk_skill_record_candidates,
    build_sdk_skill_records,
    sdk_duplicate_handle_violations,
)
from ask.catalog_parity import compute_catalog_parity  # noqa: E402
from ask.selection_contract import (  # noqa: E402
    EligibleCandidate,
    build_decision_payload,
    build_goal_decision,
    candidate_id,
    canonical_sort_key,
)
from ask.skill_analytics import skill_invocation_analytics  # noqa: E402
from ask.skill_review_dashboard import (  # noqa: E402
    _parse_plugin_eval,
    _parse_tessl_review,
    render_skill_review_dashboard,
)


TESSL_REVIEW_MIN_SCORE = 90
TESSL_REVIEW_TARGET_SCORE = 95
PLUGIN_EVAL_MIN_ACCEPTABLE_GRADE = "B+"


class _EvalCommandsProtocol(Protocol):
    def _scorecard_path_from_output(self, repo_root: Path, raw_output: str) -> Path | None: ...
    def _read_scorecard(self, path: Path | None) -> dict[str, Any]: ...


__all__ = [
    "audit_skill",
    "explain_skill",
    "extract_family_fail_lines",
    "external_review_skill",
    "fold_skills",
    "format_capabilities_human",
    "format_codex_preview_human",
    "goal_skills",
    "improve_skills",
    "init_skill",
    "install_skill",
    "list_skills",
    "reviewers_resolve",
    "route_skills",
    "skills_budget",
    "skills_capabilities",
    "skills_config_explain",
    "skills_codex_preview",
    "skills_implicit_preview",
    "skills_inject_preview",
    "skills_conformance_run",
    "skills_doctor",
    "skills_events",
    "skills_explain_boundary",
    "skills_handles",
    "skills_sdk_install_preview",
    "skills_sdk_docs_verify",
    "skills_sdk_ir_build",
    "skills_sdk_package_build",
    "skills_sdk_package_harden",
    "skills_sdk_package_signing_intent",
    "skills_sdk_trust_decide",
    "skills_sdk_observability_feedback",
    "skills_sdk_observability_promote",
    "skills_sdk_emitter_preview",
    "skills_sdk_ci_policy_preview",
    "skills_sdk_security_adapters_preview",
    "skills_sdk_static_explorer_preview",
    "skills_sdk_eval_scenario_quality",
    "skills_sdk_eval_scorer_quality",
    "skills_sdk_eval_scorer_calibration",
    "skills_sdk_eval_tessl_score",
    "skills_sdk_eval_profiles_preview",
    "skills_sdk_eval_ab_rubric_preview",
    "skills_sdk_eval_ab_preview",
    "skills_sdk_eval_ab_plan",
    "skills_sdk_eval_ab_run",
    "skills_sdk_eval_ab_judge_preview",
    "skills_sdk_eval_ab_judge_score",
    "skills_sdk_eval_run",
    "skills_sdk_placeholder_lifecycle",
    "skills_sdk_project_rollback",
    "skills_sdk_project_uninstall",
    "skills_sdk_status",
    "skills_load_preview",
    "skills_memory",
    "skills_package",
    "skills_package_verify",
    "skills_parse",
    "skills_profiles",
    "skills_proof",
    "skills_prove",
    "skills_render_preview",
    "skills_resolve",
    "sync_skills",
    "validate_openai_skill_format",
    "validate_skill_boundaries",
    "validate_skill_gate",
]


def _get_python_command(with_packages: Optional[List[str]] = None) -> List[str]:
    """
    Constructs a platform-appropriate Python invocation command.

    The returned command is chosen with this observable precedence: a non-empty PYTHON_BIN environment value, a local Python that already satisfies requested packages, a `mise`+`uv` wrapper, an `uv` wrapper, then the system `python3`. Prefer an existing local environment before `uv --with` so offline audits do not try to fetch packages from PyPI.

    Parameters:
        with_packages (Optional[List[str]]): Optional iterable of package names to request via `--with` when using a wrapper that accepts package flags; falsy entries are ignored.

    Returns:
        List[str]: Tokenised command suitable for subprocess invocation to run Python.
    """
    configured = os.environ.get("PYTHON_BIN", "").strip()
    if configured:
        return shlex.split(configured)

    packages = [pkg for pkg in (with_packages or []) if pkg]
    if packages:
        candidates = []
        # Prioritize sys.executable first
        candidates.append([sys.executable])
        # Include virtualenv python if VIRTUAL_ENV is set
        venv = os.environ.get("VIRTUAL_ENV")
        if venv:
            candidates.append([os.path.join(venv, "bin", "python")])
        pyyaml_venv_python = Path.home() / ".venvs" / "pyyaml" / "bin" / "python"
        candidates.append([str(pyyaml_venv_python)])
        # Include discovered python interpreters
        for name in ["python3", "python"]:
            python_path = shutil.which(name)
            if python_path:
                candidates.append([python_path])

        for candidate in candidates:
            if _python_command_supports_packages(candidate, packages):
                return candidate

    if shutil.which("mise") and shutil.which("uv"):
        cmd: List[str] = ["mise", "exec", "--", "uv", "run", "--python", "3.12"]
        for pkg in packages:
            cmd.extend(["--with", pkg])
        cmd.append("python")
        return cmd

    if shutil.which("uv"):
        cmd = ["uv", "run", "--python", "3.12"]
        for pkg in packages:
            cmd.extend(["--with", pkg])
        cmd.append("python")
        return cmd

    return ["python3"]


def _subprocess_env_with_uv_cache() -> dict[str, str]:
    """Return subprocess environment with sandbox-safe validation defaults."""
    env = os.environ.copy()
    if not env.get("UV_CACHE_DIR"):
        tmp_root = env.get("TMPDIR") or "/tmp"
        env["UV_CACHE_DIR"] = str(Path(tmp_root) / "agent-skills-uv-cache")
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    env.setdefault("TESSL_AUTO_UPDATE_INTERVAL_MINUTES", "0")
    return env


def _python_command_supports_packages(command: List[str], packages: List[str]) -> bool:
    """Return true when *command* can import every requested package without installation."""
    executable = Path(command[0]).expanduser()
    if os.sep in command[0] and not executable.exists():
        return False
    if os.sep not in command[0] and not shutil.which(command[0]):
        return False
    module_names = ["yaml" if package == "pyyaml" else package for package in packages]
    if Path(command[0]).resolve() == Path(sys.executable).resolve():
        return all(importlib.util.find_spec(module_name) is not None for module_name in module_names)
    probe = (
        "import importlib.util, sys; "
        "missing=[name for name in sys.argv[1:] if importlib.util.find_spec(name) is None]; "
        "sys.exit(1 if missing else 0)"
    )
    try:
        completed = subprocess.run(
            [*command, "-c", probe, *module_names],
            capture_output=True,
            text=True,
            timeout=5,
            env=_subprocess_env_with_uv_cache(),
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return completed.returncode == 0


def extract_family_fail_lines(stdout: str) -> List[str]:
    """Extract normalized FAIL lines from family benchmark stdout."""
    failures: List[str] = []
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if line.startswith(("- FAIL ", "FAIL ")):
            failures.append(line.lstrip("- "))
    return failures


def _summarize_family_benchmark_failure(stdout: str, stderr: str, limit: int = 3) -> Optional[str]:
    """Return a compact summary of FAIL lines from family benchmark output."""
    fail_lines = extract_family_fail_lines(stdout)

    if fail_lines:
        head = fail_lines[:limit]
        summary = "; ".join(head)
        remainder = len(fail_lines) - len(head)
        if remainder > 0:
            summary += f"; +{remainder} more"
        return summary

    for raw_line in stderr.splitlines():
        line = raw_line.strip()
        if line:
            return line

    return None


def _validate_repo_relative_skill_path(repo_root: Path, skill_path: str) -> tuple[Optional[Path], Optional[CallResult]]:
    """Resolve *skill_path* and block path traversal outside the repository root."""
    result = CallResult()
    try:
        resolved_path = (repo_root / skill_path).resolve()
        resolved_root = repo_root.resolve()
        try:
            if not resolved_path.is_relative_to(resolved_root):
                result.status = "error"
                result.errors.append(
                    ErrorObject(
                        code="ERR_PATH_TRAVERSAL",
                        message=f"Path traversal detected: '{skill_path}' resolves outside repository root.",
                        fix_suggestion="Use a relative path within the repository.",
                    )
                )
                return None, result
        except AttributeError:
            try:
                resolved_path.relative_to(resolved_root)
            except ValueError:
                result.status = "error"
                result.errors.append(
                    ErrorObject(
                        code="ERR_PATH_TRAVERSAL",
                        message=f"Path traversal detected: '{skill_path}' resolves outside repository root.",
                        fix_suggestion="Use a relative path within the repository.",
                    )
                )
                return None, result
    except Exception as exc:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Invalid path: {exc}",
                fix_suggestion="Check the path format and try again.",
            )
        )
        return None, result
    return resolved_path, None


def _normalize_skill_target_path(skill_path: str) -> tuple[Path, str]:
    """Return the directory target and normalized repo-relative path for a skill input."""
    audit_target = Path(skill_path)
    if audit_target.name == "SKILL.md":
        audit_target = audit_target.parent
    return audit_target, audit_target.as_posix()


def _run_validation_command(
    repo_root: Path,
    command: list[str],
    data_key: str,
    failure_message: str,
    fix_suggestion: Optional[str] = None,
) -> CallResult:
    """Run a validation subprocess and return a CallResult with captured output."""
    result = CallResult()
    proc = subprocess.run(
        command,
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=_subprocess_env_with_uv_cache(),
    )
    result.data[data_key] = {
        "command": command,
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }
    if proc.returncode == 0:
        result.status = "success"
        return result

    result.status = "error"
    result.errors.append(
        ErrorObject(
            code="ERR_VALIDATION",
            message=failure_message,
            fix_suggestion=fix_suggestion,
        )
    )
    return result


def _completed_process_payload(proc: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    """Return stable JSON data for a validation subprocess result."""
    return {
        "command": list(proc.args) if isinstance(proc.args, list) else proc.args,
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def _call_result_payload(result: CallResult) -> dict[str, Any]:
    """Return a JSON-serializable in-process command result."""
    return {
        "status": result.status,
        "trace_id": result.trace_id,
        "metadata": result.metadata,
        "data": result.data,
        "telemetry": result.telemetry,
        "errors": [error.__dict__ for error in result.errors],
    }


def _package_verify_rule_evidence(verification: dict[str, Any]) -> list[str]:
    """Return compact, replay-friendly rule evidence strings for package verification."""
    evidence: list[str] = []
    checks = verification.get("checks")
    if isinstance(checks, list):
        for check in checks:
            if not isinstance(check, dict):
                continue
            name = str(check.get("name") or "unknown")
            status = str(check.get("status") or "unknown")
            value = "true" if status == "pass" else "false" if status in {"fail", "blocked"} else status
            evidence.append(f"{name}:{value}")
            if name == "trusted_provenance":
                evidence.append(f"provenance_trusted:{value}")
            check_evidence = check.get("evidence") if isinstance(check.get("evidence"), dict) else {}
            for member in check_evidence.get("unsafe_members") or []:
                if isinstance(member, dict) and member.get("name"):
                    evidence.append(f"unsafe_member:{member['name']}")
            for member in check_evidence.get("unsafe_links") or []:
                if isinstance(member, dict) and member.get("name"):
                    evidence.append(f"symlink_escape:{member['name']}")
        return evidence

    rule_results = verification.get("rule_results")
    if isinstance(rule_results, list):
        blocker_ids = {str(item.get("rule_id")) for item in rule_results if isinstance(item, dict)}
        contract = verification.get("contract") if isinstance(verification.get("contract"), dict) else {}
        missing = contract.get("required_fields", {}).get("missing", []) if contract else []
        evidence.append(f"package_metadata_complete:{str(not missing).lower()}")
        provenance = verification.get("provenance_identity")
        trusted = provenance.get("trusted") if isinstance(provenance, dict) else False
        evidence.append(f"provenance_trusted:{str(bool(trusted)).lower()}")
        if "digest_mismatch" in blocker_ids:
            evidence.append("digest_match:false")
        mutation = verification.get("mutation_status")
        evidence.append(f"no_runtime_mutation:{str(mutation == 'not_mutated').lower()}")
        for blocker in rule_results:
            if not isinstance(blocker, dict):
                continue
            if blocker.get("path"):
                evidence.append(f"{blocker.get('rule_id')}:{blocker.get('path')}")
                if blocker.get("rule_id") in {"absolute_archive_path", "archive_path_traversal"}:
                    evidence.append(f"unsafe_member:{blocker.get('path')}")
                if blocker.get("rule_id") == "archive_symlink_escape":
                    evidence.append(f"symlink_escape:{blocker.get('path')}")
            else:
                evidence.append(str(blocker.get("rule_id") or "blocked_validation"))
    return evidence


def _package_verify_blockers(verification: dict[str, Any]) -> list[dict[str, Any]]:
    blockers = verification.get("blockers")
    if isinstance(blockers, list):
        return [
            {**item, "class": item.get("class") or item.get("rule_id")}
            for item in blockers
            if isinstance(item, dict)
        ]
    rule_results = verification.get("rule_results")
    if isinstance(rule_results, list):
        return [
            {**item, "class": item.get("class") or item.get("rule_id")}
            for item in rule_results
            if isinstance(item, dict)
        ]
    return []


def _package_verify_mutation_status(verification: dict[str, Any]) -> dict[str, Any]:
    runtime_mutation = verification.get("runtime_mutation")
    runtime_mutated = False
    if isinstance(runtime_mutation, dict):
        runtime_mutated = runtime_mutation.get("status") == "fail" or bool(runtime_mutation.get("mutations"))
    mutation_status = verification.get("mutation_status")
    mutation_payload = mutation_status if isinstance(mutation_status, dict) else {}
    status_value = mutation_payload.get("status") if mutation_payload else mutation_status
    return {
        "mutated": runtime_mutated
        or bool(mutation_payload.get("mutated"))
        or status_value not in {None, "not_mutated", "pass"},
        "runtime_roots_mutated": runtime_mutated or bool(mutation_payload.get("runtime_roots_mutated")),
        "install_attempted": bool(mutation_payload.get("install_attempted")),
        "archive_extracted": bool(mutation_payload.get("archive_extracted")),
        "network_used": bool(mutation_payload.get("network_used")),
        "raw": mutation_status or runtime_mutation or "not_mutated",
    }


def _normalize_package_verification(
    *,
    query: str,
    validation_command: str,
    verification: dict[str, Any],
) -> dict[str, Any]:
    archive = verification.get("archive")
    archive_identity = verification.get("archive_identity")
    if isinstance(archive, dict):
        archive_identity = {
            "path": archive.get("path"),
            "sha256": archive.get("sha256"),
            "type": archive.get("type"),
            "member_count": archive.get("member_count"),
        }
    target_kind = verification.get("target_kind") or ("archive" if archive_identity else "skill_directory")
    target_path = verification.get("target_path") or (archive.get("path") if isinstance(archive, dict) else query)
    provenance_identity = verification.get("provenance_identity")
    if not isinstance(provenance_identity, dict):
        provenance = verification.get("provenance")
        source = provenance.get("source") if isinstance(provenance, dict) else None
        provenance_identity = {
            "trusted": "trusted_provenance:true" in _package_verify_rule_evidence(verification),
            "source": source,
        }

    normalized = {
        **verification,
        "schema_version": PACKAGE_VERIFY_SCHEMA_VERSION,
        "query": query,
        "status": verification.get("status", "blocked"),
        "target_identity": {
            "kind": target_kind,
            "path": target_path,
            "query": query,
        },
        "archive_identity": archive_identity,
        "provenance_identity": provenance_identity,
        "rule_evidence": _package_verify_rule_evidence(verification),
        "blockers": _package_verify_blockers(verification),
        "mutation_status": _package_verify_mutation_status(verification),
        "rollback_hint": verification.get("rollback_hint")
        or "No rollback is required because verification did not install, extract, or mutate runtime roots.",
        "validation_commands": [validation_command],
        "next_command": validation_command,
    }
    normalized["agent_summary"] = (
        f"Package verification blocked: {normalized['blockers'][0].get('message', 'validation failed')}"
        if normalized["status"] == "blocked" and normalized["blockers"]
        else "Package verification passed without install, extraction, or runtime-root mutation."
    )
    return normalized


def _run_captured_tool(
    *,
    repo_root: Path,
    command: list[str],
    timeout_seconds: int = 120,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a local validation tool with bounded runtime and captured output."""
    env = _subprocess_env_with_uv_cache()
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        command,
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout_seconds,
    )


def _safe_tessl_skill_key(raw_name: str) -> str:
    """Return a conservative tile skill key for a temporary Tessl wrapper."""
    key = re.sub(r"[^a-z0-9-]+", "-", raw_name.lower()).strip("-")
    return key or "skill"


def _write_tessl_staged_json(path: Path, payload: dict[str, Any], staging_root_real: str, label: str) -> None:
    safe_path = _safe_tessl_staging_path(path, staging_root_real, label)
    safe_path.parent.mkdir(parents=True, exist_ok=True)
    safe_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _safe_tessl_staging_path(path: Path, staging_root_real: str, label: str) -> Path:
    parent_real = os.path.realpath(path.parent)
    if os.path.commonpath([staging_root_real, parent_real]) != staging_root_real:
        raise ValueError(f"Tessl review staging {label} parent escaped the staging root.")
    target_real = os.path.realpath(path)
    if os.path.commonpath([staging_root_real, target_real]) != staging_root_real:
        raise ValueError(f"Tessl review staging {label} path escaped the staging root.")
    return Path(target_real)


def _raise_if_tessl_support_tree_has_symlink(support_dir: Path, label: str) -> None:
    for path in [support_dir, *support_dir.rglob("*")]:
        if path.is_symlink():
            raise ValueError(f"Tessl review staging refuses symlinked support path: {label}")


def _write_tessl_plugin_wrapper(repo_root: Path, audit_target_path: str, stable_parent: Path) -> tuple[Path, dict[str, str]]:
    """Create a stable Tessl plugin-shaped evidence wrapper for a SKILL.md-first local skill."""
    source_skill_dir = repo_root / audit_target_path
    source_skill = source_skill_dir / "SKILL.md"
    if source_skill.is_symlink():
        raise ValueError(f"Tessl review staging refuses symlinked skill source: {audit_target_path}/SKILL.md")
    fields = _read_skill_frontmatter_fields(source_skill)
    skill_key = _safe_tessl_skill_key(fields.get("name") or Path(audit_target_path).name)
    temp_root = stable_parent / "current"
    if temp_root.exists():
        archive_root = stable_parent / "evidence-archive"
        archive_root.mkdir(parents=True, exist_ok=True)
        archive_name = f"plugin-review-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        archive_path = archive_root / archive_name
        counter = 1
        while archive_path.exists():
            counter += 1
            archive_path = archive_root / f"{archive_name}-{counter}"
        shutil.move(str(temp_root), str(archive_path))
    temp_root.mkdir(parents=True, exist_ok=True)
    staged_skill_dir = temp_root / "skills" / skill_key
    staged_skill_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_skill, staged_skill_dir / "SKILL.md")
    for support_dir_name in ("references", "scripts", "assets", "evals"):
        support_dir = source_skill_dir / support_dir_name
        if support_dir.is_dir():
            _raise_if_tessl_support_tree_has_symlink(
                support_dir,
                f"{audit_target_path}/{support_dir_name}",
            )
            shutil.copytree(support_dir, staged_skill_dir / support_dir_name)

    plugin = {
        "schema_version": 1,
        "name": f"local/{skill_key}",
        "description": fields.get("description") or f"Local validation wrapper for {skill_key}.",
        "version": "0.0.0-local",
        "private": True,
        "skills": "./skills/",
    }
    stable_parent_real = os.path.realpath(stable_parent)
    plugin_path = temp_root / ".tessl-plugin" / "plugin.json"
    _write_tessl_staged_json(plugin_path, plugin, stable_parent_real, "manifest")
    tessl_marker_path = temp_root / "tessl.json"
    _write_tessl_staged_json(
        tessl_marker_path,
        {"name": f"agent-skills-{skill_key}", "version": "0.0.0-local"},
        stable_parent_real,
        "marker",
    )
    return temp_root, {
        "plugin_manifest": str(plugin_path),
        "tessl_project_marker": str(tessl_marker_path),
        "staging_root": str(temp_root),
        "review_path": str(staged_skill_dir),
        "skill_key": skill_key,
        "source_skill": audit_target_path,
        "evidence_retention": "stable_tmp_directory_left_for_post-run_inspection",
        "archive_policy": "previous_current_staging_moved_to_evidence_archive_before_refresh",
    }


def _stable_tessl_review_root(audit_target_path: str) -> Path:
    safe_name = audit_target_path.replace("/", "__").replace(" ", "_")
    digest = hashlib.sha256(audit_target_path.encode("utf-8")).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / "ask-tessl-reviews" / f"{safe_name}-{digest}"


def _parse_tessl_review_output(stdout: str, status: str = "") -> dict[str, Any]:
    json_start = stdout.find("{")
    if json_start >= 0:
        try:
            parsed = json.loads(stdout[json_start:])
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            nested_review = parsed.get("review")
            score = parsed.get("reviewScore") or parsed.get("review_score") or parsed.get("score")
            if score is None and isinstance(nested_review, dict):
                score = nested_review.get("reviewScore") or nested_review.get("review_score") or nested_review.get("score")
            return {
                "review_score": score,
                "minimum_score": TESSL_REVIEW_MIN_SCORE,
                "target_score": TESSL_REVIEW_TARGET_SCORE,
                "score_acceptable": isinstance(score, (int, float)) and score >= TESSL_REVIEW_MIN_SCORE,
                "status": status or "reported",
                "raw": parsed,
            }
    parsed_human = _parse_tessl_review(stdout, status)
    parsed_human["minimum_score"] = TESSL_REVIEW_MIN_SCORE
    parsed_human["target_score"] = TESSL_REVIEW_TARGET_SCORE
    parsed_human["score_acceptable"] = parsed_human.get("review_score", 0) >= TESSL_REVIEW_MIN_SCORE
    return parsed_human


@dataclass(frozen=True)
class _RouterSkill:
    name: str
    description: str
    skill_path: str


STARTER_ARCHETYPES = {
    "general": (
        "autofix",
        "testing",
        "simplify",
        "improve-codebase-architecture",
        "docs-expert",
        "context7",
    ),
    "delivery": ("pr-green-sweep", "testing", "autofix", "coding-harness", "docs-expert"),
    "review": ("improve-codebase-architecture", "he-code-review", "autofix", "testing"),
    "docs": ("agents-md", "docs-expert", "context7", "openai-docs"),
}


_SKILL_INSTALLER_SCRIPT_CANDIDATES = (
    "skills-system/skill-installer/scripts/install-skill-from-github.py",
)

_SKILL_BUILDER_SCRIPT_DIR_CANDIDATES = (
    "Plugins/skill-factory/scripts/skill-builder",
    "plugins/skill-factory/scripts/skill-builder",
)


def _resolve_skill_installer_script(repo_root: Path) -> str:
    for rel in _SKILL_INSTALLER_SCRIPT_CANDIDATES:
        candidate = repo_root / rel
        if candidate.is_file():
            return rel
    # Keep canonical path in the error payload for predictable operator guidance.
    return _SKILL_INSTALLER_SCRIPT_CANDIDATES[0]


def _resolve_skill_builder_script(repo_root: Path, module_name: str) -> str:
    filename = f"{module_name}.py"
    for rel_dir in _SKILL_BUILDER_SCRIPT_DIR_CANDIDATES:
        candidate = repo_root / rel_dir / filename
        if candidate.is_file():
            return f"{rel_dir}/{filename}"
    return f"{_SKILL_BUILDER_SCRIPT_DIR_CANDIDATES[0]}/{filename}"


# Explicitly load builder-specific logic using absolute paths to avoid namespace collisions
def _load_builder_module(repo_root: Path, module_name: str):
    """
    Load a skill-builder script from the repository and return it as an imported module.

    Parameters:
        repo_root (Path): Repository root used to locate `<skill-builder>/scripts/<module_name>.py`.
        module_name (str): Script base name (without `.py`) to load.

    Returns:
        module (types.ModuleType | None): The imported module object if the script exists and is loaded, `None` otherwise.
    """
    module_rel = _resolve_skill_builder_script(repo_root, module_name)
    module_path = repo_root / module_rel
    if not module_path.exists():
        return None
    scripts_dir = module_path.parent

    internal_name = f"ask_builder_{module_name}"
    if internal_name in sys.modules:
        return sys.modules[internal_name]

    scripts_dir_str = str(scripts_dir)
    inserted = False
    if scripts_dir_str not in sys.path:
        sys.path.insert(0, scripts_dir_str)
        inserted = True
    try:
        spec = importlib.util.spec_from_file_location(internal_name, str(module_path))
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            sys.modules[internal_name] = mod  # Register BEFORE exec
            spec.loader.exec_module(mod)
            return mod
    finally:
        if inserted and scripts_dir_str in sys.path:
            sys.path.remove(scripts_dir_str)
    return None

def _canonical_entries(
    repo_root: Path,
    *,
    source: str = "auto",
    visibility: str = "default",
) -> list:
    """
    Filter discovered skill entries to those whose source directory is inside the repository root.

    Parameters:
        repo_root (Path): Repository root used to determine whether an entry's `source_dir` is inside the repository.

    Returns:
        entries (list): Discovered skill entries whose `source_dir` is relative to `repo_root`.
    """
    return [
        entry
        for entry in discover_skill_entries(source=source, visibility=visibility)
        if entry.source_dir.is_relative_to(repo_root)
    ]


def _starter_entries(entries: list, archetype: str, limit: int) -> list:
    """
    Selects a deterministic subset of skill entries for starter mode.

    Prefers skills listed in the chosen archetype (in archetype order) and, if needed, appends additional entries from the provided list until a bounded minimum of 1 up to `limit` items is reached. Unknown archetype keys fall back to the "general" archetype.

    Parameters:
        entries (list): Iterable of skill entry objects; each must expose a `name` attribute.
        archetype (str): Archetype key whose ordered starter names guide preferred selection.
        limit (int): Maximum number of entries to return; values below 1 are treated as 1.

    Returns:
        list: Ordered list of selected entries (length >= 1 and <= `limit`), preferring archetype-specified names first and then remaining entries in input order.
    """
    bounded_limit = max(1, int(limit))
    archetype_key = archetype if archetype in STARTER_ARCHETYPES else "general"
    preferred = list(STARTER_ARCHETYPES[archetype_key])
    by_name = {entry.name: entry for entry in entries}
    selected = [by_name[name] for name in preferred if name in by_name]
    if len(selected) >= bounded_limit:
        return selected[:bounded_limit]

    seen = {item.name for item in selected}
    for entry in entries:
        if entry.name in seen:
            continue
        selected.append(entry)
        if len(selected) >= bounded_limit:
            break
    return selected


def _sdk_handle_owner_index(repo_root: Path) -> dict[str, str]:
    """Return SDK skill owners keyed by handle name."""
    try:
        records = build_sdk_skill_records(repo_root_path=repo_root, visibility="advanced")
    except Exception as exc:  # noqa: BLE001 - SDK registry errors must not break skill listing.
        print(f"warning: failed to load SDK skill owner index: {exc}", file=sys.stderr)
        return {}
    owner_by_handle = {}
    for record in records:
        handle = record.handle.strip()
        owner = record.owner.strip()
        if handle and owner:
            owner_by_handle[handle] = owner
    return owner_by_handle


def _entry_matches_category(entry, category_token: str, owner_by_handle: dict[str, str], repo_root: Path) -> bool:
    """Match a skill-list category against path/category plus SDK ownership."""
    searchable = [
        str(getattr(entry, "category", "")),
        str(getattr(entry, "name", "")),
        str(getattr(entry, "description", "")),
        owner_by_handle.get(str(getattr(entry, "name", "")), ""),
    ]
    source_dir = getattr(entry, "source_dir", None)
    if isinstance(source_dir, Path):
        searchable.append(source_dir.as_posix())
        if source_dir.is_relative_to(repo_root):
            searchable.append(source_dir.relative_to(repo_root).as_posix())
    return any(category_token in value.lower() for value in searchable if value)


def _entry_visible_for_picker(entry, repo_root: Path) -> bool:
    """Return whether an entry belongs in the narrow picker-visible inventory."""
    source_dir = getattr(entry, "source_dir", None)
    if not isinstance(source_dir, Path):
        return False
    try:
        rel_parts = source_dir.relative_to(repo_root).parts
    except ValueError:
        return False
    lower_parts = tuple(part.lower() for part in rel_parts)
    if len(lower_parts) >= 4 and lower_parts[0] == "plugins" and lower_parts[2] == "skills":
        return lower_parts[1] == lower_parts[3]
    return True


def _refresh_catalog_projections(repo_root: Path, dry_run: bool = False) -> list[str]:
    """
    Regenerate root catalog projections from the default catalog surface.

    Parameters:
        repo_root (Path): Repository root containing `README.md` and `SKILL.md`.
        dry_run (bool): When `True`, do not write files and only describe planned changes.

    Returns:
        list[str]: Human-readable log lines describing projection updates.
    """
    entries = [
        entry
        for entry in discover_catalog_entries(source="repo")
        if entry.source_dir.is_relative_to(repo_root)
    ]
    catalog_count = len(entries)
    logs: list[str] = []

    skill_index_path = repo_root / "SKILL.md"
    rendered_index = render_index(entries, source="catalog", visibility="default") + "\n"
    if dry_run:
        logs.append(f"Would refresh catalog index: {skill_index_path}")
    else:
        skill_index_path.write_text(rendered_index, encoding="utf-8")
        logs.append(f"Refreshed catalog index: {skill_index_path}")

    readme_path = repo_root / "README.md"
    if readme_path.exists():
        readme_content = readme_path.read_text(encoding="utf-8")
        sdk_owner_counts: dict[str, int] = {}
        for record in build_sdk_skill_records(repo_root_path=repo_root):
            if record.source_path.startswith("Skills/"):
                sdk_owner_counts[record.owner] = sdk_owner_counts.get(record.owner, 0) + 1

        updated_readme, replacements = re.subn(
            r"A governed repository of \*\*\d+(?: canonical)? skills\*\* for AI coding agents",
            f"A governed repository of **{catalog_count} skills** for AI coding agents",
            readme_content,
            count=1,
        )
        if replacements == 0:
            updated_readme, replacements = re.subn(
                r"A governed repository of AI coding skills\.",
                f"A governed repository of **{catalog_count} skills** for AI coding agents.",
                updated_readme,
                count=1,
            )
        updated_readme = re.sub(
            r"A governed repository of \*\*skills\*\* for AI coding agents",
            f"A governed repository of **{catalog_count} skills** for AI coding agents",
            updated_readme,
            count=1,
        )
        updated_readme = re.sub(
            r"A governed \*\*Agent Skills Kit\*\* repository(?: of \*\*\d+(?: canonical)? skills\*\*)? for Codex and AI coding agents",
            "A governed **Agent Skills Kit** repository for Codex and AI coding agents",
            updated_readme,
            count=1,
        )
        updated_readme = re.sub(
            r"(?:A governed \*\*Agent Skills Kit\*\* repository for Codex and AI coding agents\. Author skills once, validate quality, expose `\$`[^.\n]+, and sync routed skills and plugins into runtime projections through the `ask` CLI\.\n\n)+(?=A governed \*\*Agent Skills Kit\*\* repository for Codex and AI coding agents\.\nAuthor skills once)",
            "",
            updated_readme,
        )
        updated_readme = re.sub(
            r"This repository currently exposes \*\*\d+ skills\*\* in the default catalog",
            f"This repository currently exposes **{catalog_count} skills** in the default catalog",
            updated_readme,
            count=1,
        )
        if sdk_owner_counts:
            preferred_order = (
                "agent-ops",
                "backend-platform",
                "content-publishing",
                "frontend-ui",
                "mobile-native",
                "product-strategy",
                "security-ops",
            )
            source_counts = sdk_owner_counts
            cluster_counts = {
                name: count for name, count in source_counts.items() if name in preferred_order
            }
            if cluster_counts:
                first_party_handle_count = sum(cluster_counts.values())
                cluster_summary = ", ".join(
                    f"{name}: {cluster_counts[name]}"
                    for name in preferred_order
                    if name in cluster_counts
                )
                updated_readme = re.sub(
                    r"(?:including \*\*\d+ first-party SDK skill names\*\* backed by canonical skill source|including \*\*\d+ first-party handles\*\* backed by canonical skill source|backed by first-party canonical skill\s+source) across \d+ topic clusters \([^)]*\)",
                    (
                        f"including **{first_party_handle_count} first-party SDK skill names** backed by canonical "
                        f"skill source across {len(cluster_counts)} topic clusters ({cluster_summary})"
                    ),
                    updated_readme,
                    count=1,
                    flags=re.DOTALL,
                )
                for name, count in cluster_counts.items():
                    updated_readme = re.sub(
                        rf"(\| {re.escape(name)}\s+\|)\s*\d+(\s+\|)",
                        lambda match, count=count: f"{match.group(1)} {count}{match.group(2)}",
                        updated_readme,
                        count=1,
                    )
                    updated_readme = re.sub(
                        rf"(\|\s+\|-- {re.escape(name)}/\s+#\s*)\d+(\s+skills?:)",
                        lambda match, count=count: f"{match.group(1)}{count}{match.group(2)}",
                        updated_readme,
                        count=1,
                    )
        updated_readme = re.sub(
            r"currently expects \*\*\d+\*\* skills",
            f"currently expects **{catalog_count}** skills",
            updated_readme,
            count=1,
        )
        if dry_run:
            if updated_readme != readme_content:
                logs.append(f"Would refresh README skill count: {readme_path}")
        elif updated_readme != readme_content:
            readme_path.write_text(updated_readme, encoding="utf-8")
            logs.append(f"Refreshed README skill count: {readme_path}")

    return logs

def list_skills(
    repo_root: Path,
    category: Optional[str] = None,
    *,
    starter: bool = False,
    archetype: str = "general",
    limit: int = 12,
    advanced: bool = False,
    visible_only: bool = False,
) -> CallResult:
    """
    List discovered catalog skills within the repository, optionally filtered by category or reduced to a deterministic starter subset.
    
    Parameters:
        repo_root (Path): Repository root used to filter discovered catalog entries; entries outside this root are excluded.
        category (Optional[str]): Case-insensitive substring applied to each entry's category; omit to include all categories.
        starter (bool): When true, return a deterministic subset selected by `archetype` and limited by `limit`.
        archetype (str): Archetype key used to pick starter skills; unknown keys fall back to "general".
        limit (int): Maximum number of skills to return when `starter` is true; coerced to at least 1.
        advanced (bool): Backward-compatible no-op alias for the full repo inventory.
        visible_only (bool): When true, return only the narrower picker/runtime-visible subset.
    
    Returns:
        CallResult: Result with `status == "success"` and `data` containing:
            - "skills": list of objects with `name`, `path` (repo-relative when possible), `category`, and `description`
            - "policy_identity": current policy identity string
            - "advanced_mode": boolean showing whether full repo inventory discovery was used
            - "inventory_mode": "repo" for the full repo inventory or "visible" for the narrower subset
            - "visible_only": boolean indicating whether the narrower runtime-visible subset was explicitly requested
            - When `starter` is true, also includes:
                - "starter_mode": true
                - "starter_archetype": resolved archetype key
                - "starter_limit": effective integer limit
    """
    result = CallResult()
    category_token = category.lower().strip() if category else ""
    explicit_visible_only = bool(visible_only)
    discovery_advanced = bool(
        (category_token and not explicit_visible_only)
        or (not explicit_visible_only and not starter)
    )
    entries = [
        entry
        for entry in discover_catalog_entries(advanced=discovery_advanced)
        if entry.source_dir.is_relative_to(repo_root)
    ]
    if explicit_visible_only:
        entries = [entry for entry in entries if _entry_visible_for_picker(entry, repo_root)]
    if starter:
        entries = _starter_entries(entries, archetype=archetype, limit=limit)
    skills_data = []
    owner_by_handle = _sdk_handle_owner_index(repo_root) if category_token else {}
    for entry in entries:
        if category_token and not _entry_matches_category(entry, category_token, owner_by_handle, repo_root):
            continue
        skills_data.append({
            "name": entry.name,
            "path": str(entry.source_dir.relative_to(repo_root)) if entry.source_dir.is_relative_to(repo_root) else str(entry.source_dir),
            "category": entry.category,
            "description": entry.description
        })
    result.data["skills"] = skills_data
    result.data["policy_identity"] = get_policy_identity()
    result.data["advanced_mode"] = discovery_advanced
    result.data["inventory_mode"] = "repo" if discovery_advanced else "visible"
    result.data["visible_only"] = explicit_visible_only
    validation_action = "starter" if starter else "list"
    validation_args: list[str] = []
    if category:
        validation_args.extend(["--category", category])
    if advanced and not starter and not explicit_visible_only:
        validation_args.append("--advanced")
    if explicit_visible_only and not starter:
        validation_args.append("--visible-only")
    if starter:
        validation_args.extend(["--archetype", archetype])
        validation_args.extend(["--limit", str(max(1, int(limit)))])
        result.data["starter_mode"] = True
        result.data["starter_archetype"] = archetype if archetype in STARTER_ARCHETYPES else "general"
        result.data["starter_limit"] = max(1, int(limit))
    result.data["validation_commands"] = [_skills_validation_command(validation_action, *validation_args)]
    result.status = "success"
    return result


def skills_budget(repo_root: Path, default_max: int = 30) -> CallResult:
    """Run the default skill runtime-budget audit and return its JSON report."""
    result = CallResult()
    script_args = [
        "Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py",
        "--default-max",
        str(default_max),
        "--json",
    ]
    cmd = _get_python_command() + script_args

    def _run_budget(command: List[str]) -> tuple[Optional[subprocess.CompletedProcess[str]], Optional[OSError]]:
        try:
            process = subprocess.run(
                command,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
            )
            return process, None
        except OSError as exc:
            return None, exc

    process, run_error = _run_budget(cmd)
    wrapper = Path(cmd[0]).name.lower() if cmd else ""
    should_retry_with_sys_python = (
        wrapper in {"uv", "mise"}
        and (
            run_error is not None
            or (process is not None and process.returncode != 0)
        )
    )
    if should_retry_with_sys_python:
        fallback_cmd = [sys.executable] + script_args
        fallback_process, fallback_error = _run_budget(fallback_cmd)
        if fallback_process is not None:
            process = fallback_process
            run_error = None
        elif process is None:
            run_error = fallback_error

    if process is None:
        error_detail = (
            f"Failed to execute runtime budget verifier: {run_error}"
            if run_error is not None
            else "Failed to execute runtime budget verifier."
        )
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_RUNTIME",
                message=error_detail,
                fix_suggestion="Ensure Python is available and rerun `ask skills budget`.",
            )
        )
        return result

    try:
        parsed_report = json.loads(process.stdout)
    except json.JSONDecodeError:
        parsed_report = {
            "status": "fail",
            "raw_stdout": process.stdout,
            "raw_stderr": process.stderr,
        }
    report = (
        parsed_report
        if isinstance(parsed_report, dict)
        else {
            "status": "fail",
            "raw_stdout": process.stdout,
            "raw_stderr": process.stderr,
            "parse_error": "verify_runtime_budget.py did not return a JSON object",
        }
    )

    validation_args: list[str] = []
    if default_max != 30:
        validation_args.extend(["--default-max", str(default_max)])
    report["validation_commands"] = [_skills_validation_command("budget", *validation_args)]
    result.data["runtime_budget"] = report
    result.status = "success" if process.returncode == 0 and report.get("status") == "pass" else "error"
    if result.status == "error":
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Skill runtime budget failed.",
                fix_suggestion="Reduce default-visible skills, hide bridge aliases under .system, or update the explicit budget with evidence.",
            )
        )
    return result


def skills_handles(
    repo_root: Path,
    check: bool = False,
    include_handles: bool = True,
    write_projection: bool = False,
    check_projection: bool = False,
    dry_run: bool = False,
) -> CallResult:
    """Return or validate SDK-visible skill handles."""
    result = CallResult()
    result.metadata["command"] = "skills handles"
    validation_args: list[str] = []
    if check:
        validation_args.append("--check")
    if not include_handles:
        validation_args.append("--no-handles")
    if write_projection:
        validation_args.append("--write-projection")
    if check_projection:
        validation_args.append("--check-projection")
    if dry_run:
        validation_args.append("--dry-run")

    if write_projection or check_projection:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_INVALID_PROJECTION_MODE",
                message="Removed projection flags are not part of the SDK target registry path.",
                fix_suggestion="Use ./bin/ask skills sync --scope workspace --projection flat --json --robot, then rerun ./bin/ask skills list --json --robot.",
            )
        )

    candidates = build_sdk_skill_record_candidates(repo_root_path=repo_root, visibility="advanced")
    records = build_sdk_skill_records(repo_root_path=repo_root, visibility="advanced")
    handles = [record.to_resolution() for record in records] if include_handles else []
    violations = sdk_duplicate_handle_violations(candidates)
    report = {
        "schema_version": "sdk-skill-handles.v1",
        "status": "fail" if violations else "pass",
        "generated_from": "sdk_flat_registry",
        "handle_count": len(records),
        "handles": handles,
        "violations": violations,
        "validation_commands": [_skills_validation_command("handles", *validation_args)],
    }
    result.data["sdk_handles"] = report
    result.data["command_surface"] = {
        **report,
        "schema_version": "command-surface.v1",
        "generated_from": "sdk_flat_registry_compat_alias",
    }
    result.data["handles"] = handles
    result.data["violations"] = violations
    result.data["policy_identity"] = get_policy_identity()
    if check and violations:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="SDK skill target validation failed.",
                fix_suggestion="Inspect data.violations, fix SDK skill metadata, and rerun ./bin/ask skills list --json --robot.",
            )
        )
    return result




def skills_resolve(repo_root: Path, handle: str) -> CallResult:
    """Resolve one SDK-visible skill handle to its canonical source."""
    result = CallResult()
    result.metadata["command"] = "skills resolve"
    payload = resolve_skill_handle(handle, repo_root_path=repo_root)
    normalized = str(payload.get("handle") or handle).lstrip("$")
    payload["validation_commands"] = [
        _skills_validation_command("resolve", normalized),
    ]
    result.data["resolution"] = payload
    if payload.get("status") != "ok":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Could not resolve skill handle '{payload.get('handle', handle)}': {payload.get('error_code')}",
                fix_suggestion=payload.get("operator_action"),
            )
        )
    return result


def skills_parse(repo_root: Path, request_text: str) -> CallResult:
    """Parse a prompt for SDK skill mentions and reviewer roles, then resolve them."""
    result = CallResult()
    result.metadata["command"] = "skills parse"
    payload = parse_sdk_references(request_text, repo_root_path=repo_root)
    payload["validation_commands"] = [
        _skills_validation_command("parse", request_text),
    ]
    result.data["parse"] = payload
    if payload.get("status") != "pass":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="One or more SDK skill handles in the prompt could not be resolved.",
                fix_suggestion="Inspect data.parse.unresolved, then rerun with valid $ skill and @ reviewer handles.",
            )
        )
    return result


def skills_proof(repo_root: Path, handle: str, runtime_target: str = "any") -> CallResult:
    """
    Prove that an SDK skill handle is reachable from the workspace and user runtime targets.
    
    Parameters:
        repo_root (Path): Repository root used to resolve skill sources and workspace context.
        handle (str): Command-visible handle to prove (e.g., "$skill do something").
        runtime_target (str): Runtime target to validate against; normalized values include `"any"` and `"codex"`.
    
    Returns:
        CallResult: Result of the proof operation. On success `status` will be `"success"` and `data["proof"]`
        contains the proof payload produced by `build_sdk_skill_proof`. `data["runtime_evidence"]` will
        contain emitted runtime evidence. If the proof fails `status` will be `"error"`, `errors` will include an
        `ErrorObject` with `code="ERR_VALIDATION"`, and `data["runtime_failure"]` will contain failure details.
    """
    result = CallResult()
    result.metadata["command"] = "skills proof"
    runtime_target = normalize_runtime_target(runtime_target)
    proof = build_sdk_skill_proof(
        repo_root=repo_root,
        handle=handle,
        runtime_target=runtime_target,
        resolve_skill_handle_fn=resolve_skill_handle,
        home_path=Path.home(),
    )
    normalized = proof["handle"]
    runtime_evidence = emit_sdk_skill_runtime_evidence(repo_root=repo_root, proof=proof)
    result.data["runtime_evidence"] = runtime_evidence
    proof["runtime_evidence"] = runtime_evidence
    runtime_evidence_blocks = (
        runtime_target in {"codex", "agents"}
        and runtime_evidence.get("claim_status") in {"blocked", "partial"}
    )
    result.data["proof"] = proof
    if proof["status"] != "pass" or runtime_evidence_blocks:
        failure = (
            proof.get("runtime_failure")
            if isinstance(proof.get("runtime_failure"), dict)
            else _runtime_failure_payload(
                command="skills proof",
                error_code="ERR_RUNTIME",
                failed_check_id=str(runtime_evidence.get("failed_check_id") or "runtime_observation_quality"),
                path="runtime_evidence.claim_status",
                message=str(runtime_evidence.get("blocker") or "Runtime evidence quality is incomplete."),
                recovery_guidance="Rerun the explicit runtime proof after collecting current runtime evidence.",
                validation_commands=[_skills_validation_command("proof", normalized, "--runtime-target", runtime_target)],
            )
        )
        if runtime_evidence_blocks and proof.get("status") == "pass":
            proof["status"] = "fail"
        proof["runtime_failure"] = failure
        result.data["runtime_failure"] = failure
        message = (
            f"Invalid runtime target '{runtime_target}'."
            if failure.get("failed_check_id") == "runtime_target"
            else f"SDK skill proof failed for '{normalized}'."
        )
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=message,
                fix_suggestion=failure["recovery_guidance"],
            )
        )
    return result


def _skill_audit_target(repo_root: Path, resolution: dict[str, Any]) -> str | None:
    source = resolution.get("source_path")
    if not source:
        return None
    target = Path(str(source))
    if not target.is_absolute():
        target = repo_root / target
    if target.name == "SKILL.md":
        target = target.parent
    try:
        return target.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return None


def _skills_sdk_digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _skills_sdk_repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def _skills_sdk_eval_package_identity(repo_root: Path, target: str) -> dict[str, str] | None:
    query = target.strip()
    if not query:
        return None
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    if not isinstance(target_info, dict) or target_info.get("target_kind") == "invalid_path":
        return None
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    if not source_path_value:
        return None
    source_path = Path(str(source_path_value))
    if not source_path.is_absolute():
        source_path = repo_root / source_path
    if source_path.is_dir():
        source_path = source_path / "SKILL.md"
    if not source_path.is_file():
        return None
    receipt = _build_package_digest_receipt(repo_root, source_path=source_path, query=query)
    return {
        "skill_ir_schema_version": str(receipt["manifest"]["skill_ir_schema_version"]),
        "package_id": str(receipt["package_id"]),
        "package_digest": str(receipt["package_digest"]),
    }


def _skill_workout_candidates(repo_root: Path, handle: str) -> list[str]:
    workouts_root = repo_root / ".workouts"
    if not workouts_root.is_dir():
        return []
    normalized = handle.strip().lower().replace("_", "-")

    def _normalized_metadata_values(value: Any) -> set[str]:
        if value is None:
            return set()
        if isinstance(value, str):
            return {value.strip().lower().replace("_", "-")}
        if isinstance(value, dict):
            result: set[str] = set()
            for nested in value.values():
                result.update(_normalized_metadata_values(nested))
            return result
        if isinstance(value, (list, tuple, set)):
            result: set[str] = set()
            for nested in value:
                result.update(_normalized_metadata_values(nested))
            return result
        return {str(value).strip().lower().replace("_", "-")}

    candidates: list[str] = []
    for workout in sorted(workouts_root.glob("**/workout.yaml")):
        workout_id = workout.parent.relative_to(workouts_root).as_posix()
        try:
            from ask.commands.workouts import _load_structured_file

            metadata = _load_structured_file(workout)
        except (OSError, ValueError):
            continue
        explicit_values: set[str] = set()
        for key in (
            "skills",
            "handles",
            "target_skills",
            "target_handles",
            "skill",
            "handle",
            "skill_id",
            "id",
            "target_module",
            "target_skill",
            "target_handle",
        ):
            explicit_values.update(_normalized_metadata_values(metadata.get(key)))
        for value in _normalized_metadata_values(metadata.get("target_source_path")):
            path = Path(value)
            explicit_values.add(path.stem)
            if path.parent.name:
                explicit_values.add(path.parent.name)
        if normalized in explicit_values:
            candidates.append(workout_id)
    return candidates


def _repo_relative_path(repo_root: Path, path: Path) -> str | None:
    """Return a repo-relative POSIX path when *path* is inside *repo_root*."""
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return None


CAPABILITY_LIFECYCLE_EVENT_TYPES: dict[str, str] = {
    "skill_loaded": "A skill source or handle was loaded for inspection or execution.",
    "skill_doctor_completed": "A capability doctor run completed with pass, warning, or blocked status.",
    "package_readiness_checked": "A skill package readiness gate completed with pass, warning, or blocked status.",
    "eval_started": "A workout, smoke eval, or proof run started for a capability.",
    "eval_blocked": "A workout, smoke eval, or proof run stopped on a classified blocker.",
    "eval_completed": "A workout, smoke eval, or proof run completed with pass or fail status.",
    "projection_synced": "A canonical skill source was projected into runtime handles or manifests.",
    "manifest_changed": "A skill or skillset manifest changed and may need validation.",
}


CAPABILITY_LIFECYCLE_EVENT_CONSUMERS: dict[str, dict[str, Any]] = {
    "skill_loaded": {
        "profiles": ["authoring", "package-review", "eval"],
        "producer_commands": ["./bin/ask skills resolve <handle> --json --robot"],
        "observer_commands": [_skills_validation_command("events", "skill_loaded")],
    },
    "skill_doctor_completed": {
        "profiles": ["authoring", "package-review"],
        "producer_commands": ["./bin/ask skills doctor <handle-or-path> --json --robot"],
        "observer_commands": [_skills_validation_command("events", "skill_doctor_completed")],
    },
    "package_readiness_checked": {
        "profiles": ["package-review", "plugin-share"],
        "producer_commands": ["./bin/ask skills package <handle-or-path> --json --robot"],
        "observer_commands": [_skills_validation_command("events", "package_readiness_checked")],
    },
    "eval_started": {
        "profiles": ["eval"],
        "producer_commands": ["./bin/ask skills prove <handle> --json --robot"],
        "observer_commands": [_skills_validation_command("events", "eval_started")],
    },
    "eval_blocked": {
        "profiles": ["eval"],
        "producer_commands": ["./bin/ask skills prove <handle> --json --robot"],
        "observer_commands": [_skills_validation_command("events", "eval_blocked")],
    },
    "eval_completed": {
        "profiles": ["eval"],
        "producer_commands": ["./bin/ask skills prove <handle> --json --robot"],
        "observer_commands": [_skills_validation_command("events", "eval_completed")],
    },
    "projection_synced": {
        "profiles": ["authoring", "live-mutation"],
        "producer_commands": [_skills_validation_command("sync")],
        "observer_commands": [_skills_validation_command("list")],
    },
    "manifest_changed": {
        "profiles": ["authoring", "plugin-share", "live-mutation"],
        "producer_commands": [_skills_validation_command("sync", "--scope", "workspace", "--projection", "flat")],
        "observer_commands": [_skills_validation_command("list")],
    },
}


SKILL_OPERATION_PROFILES: dict[str, dict[str, Any]] = {
    "authoring": {
        "intent": "Create or revise canonical skill sources.",
        "allowed_roots": ["Skills/**", "Plugins/*/skills/**", "Docs/**", "Infrastructure/tests/**"],
        "write_policy": "canonical_source_only",
        "permissions": ["repo_read", "repo_write_canonical_sources", "local_validation"],
        "required_evidence": ["nearest AGENTS.md", "UBIQUITOUS_LANGUAGE.md", "skill audit", "focused tests"],
        "stop_conditions": ["missing canonical owner", "strict audit failure", "runtime projection drift"],
    },
    "package-review": {
        "intent": "Check a skill or plugin package before promotion.",
        "allowed_roots": ["Skills/**", "Plugins/**", "Infrastructure/artifacts/skill-reviews/**"],
        "write_policy": "reports_only_unless_fix_requested",
        "permissions": ["repo_read", "local_validation", "artifact_write"],
        "required_evidence": [
            "compat or strict audit",
            "external review report",
            "Plugin Eval grade B+ or better",
            "Tessl review score >= 90 (95+ target)",
            "metadata contract",
        ],
        "stop_conditions": ["blocked_validation", "blocked_missing_artifact", "blocked_missing_tool"],
    },
    "plugin-share": {
        "intent": "Prepare versioned skill/plugin sharing metadata and install readiness.",
        "allowed_roots": ["Plugins/**", "Skills/**", ".agents/Plugins/marketplace.json", "Docs/**"],
        "write_policy": "versioned_metadata_and_marketplace_only",
        "permissions": ["repo_read", "repo_write_metadata", "local_validation"],
        "required_evidence": ["version", "provenance", "compatible_roles", "runtime_needs", "share_readiness"],
        "stop_conditions": ["missing provenance", "untrusted source", "unpinned external ref"],
    },
    "eval": {
        "intent": "Run smoke, workout, or release evidence for one capability.",
        "allowed_roots": ["Skills/**", "Infrastructure/workouts/**", "Infrastructure/artifacts/**"],
        "write_policy": "artifact_write_only",
        "permissions": ["repo_read", "local_validation", "artifact_write"],
        "required_evidence": [
            "eval_started event",
            "Codex smoke run uses [profiles.fast] via --profile fast",
            f"Tessl eval source staged under {os.path.join(tempfile.gettempdir(), 'ask-tessl-evals')}",
            "staged tessl.json project marker",
            "canonical references/evals.yaml copied into staged input",
            "eval_completed or eval_blocked event",
            "timeout classification",
        ],
        "stop_conditions": list(EVAL_BLOCKER_CLASSES),
    },
    "live-mutation": {
        "intent": "Perform externally visible mutation such as tracker, PR, or runtime sync changes.",
        "allowed_roots": ["Skills/**", "Plugins/**", ".agents/**", ".skillsets/**", "Docs/**"],
        "write_policy": "explicit_request_required",
        "permissions": ["repo_read", "repo_write", "external_write_after_confirmation"],
        "required_evidence": ["operator request", "target identity", "rollback path", "post-mutation validation"],
        "stop_conditions": ["unclear target", "auth mismatch", "unrelated dirty worktree", "rollback unavailable"],
    },
}


def _skill_memory_operation_context() -> dict[str, Any]:
    """Return profile and provenance context for the skill memory facade."""
    return {
        "primary_profile": "authoring",
        "consumer_profiles": ["authoring", "package-review", "eval"],
        "provider_model": "extension-like-read-only",
        "profiles": {
            profile_name: {
                "intent": SKILL_OPERATION_PROFILES[profile_name]["intent"],
                "write_policy": SKILL_OPERATION_PROFILES[profile_name]["write_policy"],
                "required_evidence": SKILL_OPERATION_PROFILES[profile_name]["required_evidence"],
            }
            for profile_name in ("authoring", "package-review", "eval")
        },
        "provider_contract": {
            "required_entry_fields": ["id", "source_id", "path", "title", "snippet", "provenance", "freshness"],
            "read_modes": ["list", "read", "search"],
            "mutation_policy": "read_only",
        },
        "follow_up_commands": [
            _skills_validation_command("memory", "list"),
            "./bin/ask skills memory search <query> --json --robot",
            "./bin/ask skills memory read <entry-id-or-path> --json --robot",
        ],
        "validation_commands": [
            _skills_validation_command("memory", "search", "projection"),
            _ask_validation_command("memory", "search", "projection"),
        ],
    }


def _skill_memory_source_summary(roots: list[dict[str, Any]]) -> dict[str, Any]:
    """Return compact source availability for the skill memory provider."""
    available = [root["provider"] for root in roots if root["exists"]]
    missing = [root["provider"] for root in roots if not root["exists"]]
    return {
        "source_count": len(roots),
        "available_sources": available,
        "missing_sources": missing,
    }


def _skill_memory_freshness_label(value: Any) -> str:
    """Return a stable bucket label for memory freshness metadata."""
    if isinstance(value, str) and value.strip():
        return value
    if isinstance(value, dict):
        status = value.get("status")
        if isinstance(status, str) and status.strip():
            return status
        if value.get("mtime") is not None:
            return "has_mtime"
        if value:
            return "metadata_present"
    return "unknown"


def _skill_memory_entry_summary(entries: list[dict[str, Any]], total_count: int | None = None) -> dict[str, Any]:
    """Return compact memory result counts grouped by provider and freshness."""
    by_source: dict[str, int] = {}
    by_freshness: dict[str, int] = {}
    for entry in entries:
        source_id = str(entry.get("source_id") or "unknown")
        freshness = _skill_memory_freshness_label(entry.get("freshness"))
        by_source[source_id] = by_source.get(source_id, 0) + 1
        by_freshness[freshness] = by_freshness.get(freshness, 0) + 1
    return {
        "returned_count": len(entries),
        "total_count": len(entries) if total_count is None else total_count,
        "by_source": by_source,
        "by_freshness": by_freshness,
    }


def skills_memory(
    repo_root: Path,
    mode: str,
    query: str | None = None,
    limit: int = 8,
    source_id: str | None = None,
) -> CallResult:
    """List, read, or search durable skill memory surfaces as a read-only provider."""
    result = CallResult()
    result.metadata["command"] = f"skills memory {mode}"
    provider_roots = [
        {
            "provider": source.source_id,
            "root": str(source.root),
            "description": source.label,
            "type": source.source_type,
            "exists": (repo_root / source.root).exists(),
        }
        for source in MEMORY_SOURCES
    ]
    mode_key = mode.strip().lower()
    capped_limit = min(limit, 50)
    payload: dict[str, Any] = {
        "schema_version": "skill-memory-provider.v1",
        "status": "pass",
        "mode": mode_key,
        "query": query,
        "provider_model": "extension-like-read-only",
        "contract_schemas": {
            "memory": "skill-memory-provider.v1",
            "provider": "memory-provider.v1",
            "profiles": "skill-operation-profiles.v1",
            "events": "skill-events.v1",
        },
        "operation_context": _skill_memory_operation_context(),
        "roots": provider_roots,
        "source_summary": _skill_memory_source_summary(provider_roots),
        "memory_provider_schema": "memory-provider.v1",
    }

    if mode_key == "list":
        provider_result = _memory_provider_list(repo_root, source_id=source_id, limit=capped_limit)
        memory_payload = provider_result.data.get("memory", {})
        if provider_result.status != "success":
            result.status = "error"
            payload["status"] = "blocked"
            payload["agent_summary"] = memory_payload.get("agent_summary") or (
                provider_result.errors[0].message if provider_result.errors else "Memory list failed."
            )
            result.errors.extend(provider_result.errors)
            result.data["skill_memory"] = payload
            return result
        payload["entries"] = memory_payload.get("entries", [])
        payload["entry_count"] = memory_payload.get("count", len(payload["entries"]))
        payload["total_count"] = memory_payload.get("total_count", len(payload["entries"]))
        payload["entry_summary"] = _skill_memory_entry_summary(payload["entries"], payload["total_count"])
        payload["agent_summary"] = memory_payload.get("agent_summary", "Listed skill memory entries.")
    elif mode_key == "read":
        needle = (query or "").strip()
        if not needle:
            result.status = "error"
            payload["status"] = "blocked"
            payload["agent_summary"] = "Memory read requires an entry id or repo-relative path."
            result.data["skill_memory"] = payload
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=payload["agent_summary"],
                    fix_suggestion="Run ./bin/ask skills memory list --json --robot and pass an entry id.",
                )
            )
            return result
        provider_result = _memory_provider_read(repo_root, needle)
        memory_payload = provider_result.data.get("memory", {})
        if provider_result.status != "success":
            result.status = "error"
            payload["status"] = "blocked"
            payload["requested"] = needle
            payload["agent_summary"] = memory_payload.get("agent_summary") or f"No skill memory entry matched '{needle}'."
            result.errors.extend(provider_result.errors)
            result.data["skill_memory"] = payload
            return result
        payload["entry"] = memory_payload.get("entry")
        payload["entry_summary"] = _skill_memory_entry_summary([payload["entry"]] if payload["entry"] else [], 1 if payload["entry"] else 0)
        payload["agent_summary"] = memory_payload.get("agent_summary", f"Read skill memory entry {needle}.")
    elif mode_key == "search":
        if not (query or "").strip():
            result.status = "error"
            payload["status"] = "blocked"
            payload["agent_summary"] = "Memory search requires a non-empty query."
            result.data["skill_memory"] = payload
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=payload["agent_summary"],
                    fix_suggestion="Run ./bin/ask skills memory search '<keyword>' --json --robot.",
                )
            )
            return result
        provider_result = _memory_provider_search(repo_root, query or "", source_id=source_id, limit=capped_limit)
        memory_payload = provider_result.data.get("memory", {})
        if provider_result.status != "success":
            result.status = "error"
            payload["status"] = "blocked"
            payload["agent_summary"] = memory_payload.get("agent_summary") or (
                provider_result.errors[0].message if provider_result.errors else "Memory search failed."
            )
            result.errors.extend(provider_result.errors)
            result.data["skill_memory"] = payload
            return result
        payload["entries"] = memory_payload.get("results", [])
        payload["entry_count"] = memory_payload.get("count", len(payload["entries"]))
        payload["total_count"] = memory_payload.get("total_count", len(payload["entries"]))
        payload["entry_summary"] = _skill_memory_entry_summary(payload["entries"], payload["total_count"])
        payload["agent_summary"] = memory_payload.get("agent_summary", f"Found skill memory entries matching '{query}'.")
    else:
        result.status = "error"
        payload["status"] = "blocked"
        payload["agent_summary"] = f"Unknown skill memory mode '{mode}'."
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion="Use one of: list, read, search.",
            )
        )

    result.data["skill_memory"] = payload
    return result


def _capability_lifecycle_event(
    *,
    event_type: str,
    query: str,
    target_kind: str,
    handle: Any,
    source_path: Any,
    audit_target: Any,
    status: str,
    blockers: list[dict[str, str]],
    warnings: list[dict[str, str]],
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a structured lifecycle event for capability diagnostics."""
    subject_key = str(handle or audit_target or source_path or query)
    event_consumer = CAPABILITY_LIFECYCLE_EVENT_CONSUMERS.get(event_type, {})
    producer_commands = event_consumer.get("producer_commands", [])
    observer_commands = event_consumer.get("observer_commands", [])
    event = {
        "schema_version": "capability-lifecycle-event.v1",
        "event_type": event_type,
        "event_definition": CAPABILITY_LIFECYCLE_EVENT_TYPES.get(event_type),
        "contract_schemas": {
            "lifecycle_event": "capability-lifecycle-event.v1",
            "events": "skill-events.v1",
            "profiles": "skill-operation-profiles.v1",
        },
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "event_identity": {
            "event_type": event_type,
            "subject_key": subject_key,
            "target_kind": target_kind,
            "status": status,
        },
        "producer_command": producer_commands[0] if producer_commands else None,
        "observer_command": observer_commands[0] if observer_commands else None,
        "subject": {
            "query": query,
            "target_kind": target_kind,
            "handle": handle,
            "canonical_source_path": source_path,
            "audit_target": audit_target,
        },
        "outcome": {
            "status": status,
            "blocker_classes": [blocker["class"] for blocker in blockers],
            "warning_classes": [warning["class"] for warning in warnings],
        },
    }
    if details:
        event["details"] = details
    return event


def _contract_status(has_items: bool, contract_gaps: list[str]) -> str:
    """Return the stable readiness label for a summarized contract."""
    if not has_items:
        return "empty"
    if contract_gaps:
        return "has_gaps"
    return "ready"


def _contract_readiness(has_items: bool, contract_gaps: list[str]) -> dict[str, Any]:
    """Return shared readiness fields for summarized contracts."""
    return {
        "contract_gap_count": len(contract_gaps),
        "has_contract_gaps": bool(contract_gaps),
        "contract_status": _contract_status(has_items, contract_gaps),
        "contract_ready": has_items and not contract_gaps,
    }


def _contract_sections_overview(contract_sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return shared readiness fields for named contract sections."""
    gap_count = sum(int(section["gap_count"]) for section in contract_sections.values())
    contract_ready = bool(contract_sections) and all(section["ready"] for section in contract_sections.values())
    section_statuses = {str(section["status"]) for section in contract_sections.values()}
    if contract_ready:
        contract_status = "ready"
    elif "has_gaps" in section_statuses or gap_count > 0:
        contract_status = "has_gaps"
    else:
        contract_status = "empty"
    return {
        "contract_sections": contract_sections,
        "contract_status_by_section": {
            section_name: section["status"]
            for section_name, section in contract_sections.items()
        },
        "contract_gap_count_by_section": {
            section_name: section["gap_count"]
            for section_name, section in contract_sections.items()
        },
        "contract_section_count": len(contract_sections),
        "ready_contract_sections": sorted(
            section_name
            for section_name, section in contract_sections.items()
            if section["ready"]
        ),
        "blocked_contract_sections": sorted(
            section_name
            for section_name, section in contract_sections.items()
            if not section["ready"]
        ),
        "contract_gap_count": gap_count,
        "has_contract_gaps": gap_count > 0,
        "contract_ready": contract_ready,
        "contract_status": contract_status,
    }


def _skill_event_summary(
    event_consumers: dict[str, dict[str, Any]],
    known_profiles: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Return compact event coverage counts for automation consumers."""
    by_profile: dict[str, int] = {}
    events_by_profile: dict[str, list[str]] = {}
    profiles_by_event: dict[str, list[str]] = {}
    producer_count = 0
    observer_count = 0
    producer_command_count_by_event: dict[str, int] = {}
    observer_command_count_by_event: dict[str, int] = {}
    events_missing_producers: list[str] = []
    events_missing_observers: list[str] = []
    events_missing_profiles: list[str] = []
    events_with_unknown_profiles: dict[str, list[str]] = {}
    known_profile_names = set(known_profiles)
    for event_name, consumer in event_consumers.items():
        producer_commands = consumer.get("producer_commands", [])
        observer_commands = consumer.get("observer_commands", [])
        profiles = consumer.get("profiles", [])
        profiles_by_event[event_name] = sorted(str(profile) for profile in profiles)
        producer_command_count_by_event[event_name] = len(producer_commands)
        observer_command_count_by_event[event_name] = len(observer_commands)
        if not producer_commands:
            events_missing_producers.append(event_name)
        if not observer_commands:
            events_missing_observers.append(event_name)
        if not profiles:
            events_missing_profiles.append(event_name)
        producer_count += len(producer_commands)
        observer_count += len(observer_commands)
        for profile in profiles:
            if profile not in known_profile_names:
                events_with_unknown_profiles.setdefault(event_name, []).append(profile)
            by_profile[profile] = by_profile.get(profile, 0) + 1
            events_by_profile.setdefault(profile, []).append(event_name)
    events_with_contract_gaps = sorted(
        set(
            events_missing_producers
            + events_missing_observers
            + events_missing_profiles
            + list(events_with_unknown_profiles)
        )
    )
    missing_by_contract_dimension = {
        "known_profiles": sorted(events_with_unknown_profiles),
        "observer_commands": sorted(events_missing_observers),
        "producer_commands": sorted(events_missing_producers),
        "profiles": sorted(events_missing_profiles),
    }
    referenced_profile_names = set(by_profile)
    known_profiles_without_events = sorted(known_profile_names - referenced_profile_names)
    known_profiles_with_events = sorted(known_profile_names & referenced_profile_names)
    known_events_by_profile = {
        profile_name: sorted(events_by_profile.get(profile_name, []))
        for profile_name in sorted(known_profiles)
    }
    unknown_profile_reference_count = sum(
        len(profile_names) for profile_names in events_with_unknown_profiles.values()
    )
    return {
        "event_count": len(event_consumers),
        "contract_dimensions": sorted(missing_by_contract_dimension),
        "contract_dimension_count": len(missing_by_contract_dimension),
        "contract_dimension_status": {
            dimension: _contract_status(bool(event_consumers), missing_events)
            for dimension, missing_events in missing_by_contract_dimension.items()
        },
        "missing_events_by_contract_dimension": missing_by_contract_dimension,
        "missing_event_count_by_contract_dimension": {
            dimension: len(missing_events)
            for dimension, missing_events in missing_by_contract_dimension.items()
        },
        "producer_command_count": producer_count,
        "observer_command_count": observer_count,
        "producer_command_count_by_event": dict(sorted(producer_command_count_by_event.items())),
        "observer_command_count_by_event": dict(sorted(observer_command_count_by_event.items())),
        "events_missing_producers": sorted(events_missing_producers),
        "events_missing_observers": sorted(events_missing_observers),
        "events_missing_profiles": sorted(events_missing_profiles),
        "events_missing_profile_count": len(events_missing_profiles),
        "has_missing_producers": bool(events_missing_producers),
        "has_missing_observers": bool(events_missing_observers),
        "has_missing_profiles": bool(events_missing_profiles),
        "events_with_unknown_profile_count": len(events_with_unknown_profiles),
        "unknown_profile_reference_count": unknown_profile_reference_count,
        "events_with_unknown_profiles": {
            event_name: sorted(profile_names)
            for event_name, profile_names in sorted(events_with_unknown_profiles.items())
        },
        "profiles_unknown_to_registry": sorted(
            {
                profile_name
                for profile_names in events_with_unknown_profiles.values()
                for profile_name in profile_names
            }
        ),
        "has_unknown_profiles": bool(events_with_unknown_profiles),
        "known_profile_count": len(known_profiles),
        "known_profile_names": sorted(known_profiles),
        "referenced_profile_count": len(referenced_profile_names),
        "referenced_profile_names": sorted(referenced_profile_names),
        "known_profiles_with_events": known_profiles_with_events,
        "known_profile_event_coverage_count": len(known_profiles_with_events),
        "all_known_profiles_have_events": len(known_profiles_with_events) == len(known_profile_names),
        "known_profiles_without_events": known_profiles_without_events,
        "has_known_profiles_without_events": bool(known_profiles_without_events),
        "known_events_by_profile": known_events_by_profile,
        "known_event_count_by_profile": {
            profile_name: len(event_names)
            for profile_name, event_names in known_events_by_profile.items()
        },
        "events_with_contract_gaps": events_with_contract_gaps,
        **_contract_readiness(bool(event_consumers), events_with_contract_gaps),
        "by_profile": by_profile,
        "events_by_profile": {
            profile_name: sorted(event_names)
            for profile_name, event_names in sorted(events_by_profile.items())
        },
        "event_count_by_profile": {
            profile_name: len(event_names)
            for profile_name, event_names in sorted(events_by_profile.items())
        },
        "profiles_by_event": dict(sorted(profiles_by_event.items())),
        "profile_count_by_event": {
            event_name: len(profile_names)
            for event_name, profile_names in sorted(profiles_by_event.items())
        },
        "profile_count": len(by_profile),
        "profile_names": sorted(by_profile),
        "has_profiles": bool(by_profile),
    }


def _skill_events_readiness_overview(event_summary: dict[str, Any]) -> dict[str, Any]:
    """Return a compact readiness summary for lifecycle event consumers."""
    return _contract_sections_overview({
        "lifecycle_event_contract": {
            "status": event_summary["contract_status"],
            "ready": event_summary["contract_ready"],
            "gap_count": event_summary["contract_gap_count"],
        }
    })


def skills_events(repo_root: Path, event_type: str | None = None) -> CallResult:
    """Return the declared capability lifecycle event contract."""
    result = CallResult()
    result.metadata["command"] = "skills events"
    selected = event_type.strip() if event_type else None
    if selected and selected not in CAPABILITY_LIFECYCLE_EVENT_TYPES:
        result.status = "error"
        result.data["skill_events"] = {
            "schema_version": "skill-events.v1",
            "status": "blocked",
            "requested_event_type": selected,
            "available_event_types": sorted(CAPABILITY_LIFECYCLE_EVENT_TYPES),
        }
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Unknown skill lifecycle event type '{selected}'.",
                fix_suggestion=f"Use one of: {', '.join(sorted(CAPABILITY_LIFECYCLE_EVENT_TYPES))}",
            )
        )
        return result

    event_types = {selected: CAPABILITY_LIFECYCLE_EVENT_TYPES[selected]} if selected else CAPABILITY_LIFECYCLE_EVENT_TYPES
    event_consumers = (
        {selected: CAPABILITY_LIFECYCLE_EVENT_CONSUMERS[selected]}
        if selected
        else CAPABILITY_LIFECYCLE_EVENT_CONSUMERS
    )
    event_summary = _skill_event_summary(event_consumers, SKILL_OPERATION_PROFILES)
    result.data["skill_events"] = {
        "schema_version": "skill-events.v1",
        "status": "pass",
        "repo_root": str(repo_root),
        "selected_event_type": selected,
        "event_schema": "capability-lifecycle-event.v1",
        "event_names": list(event_types),
        "available_event_types": sorted(CAPABILITY_LIFECYCLE_EVENT_TYPES),
        "contract_schemas": {
            "events": "skill-events.v1",
            "lifecycle_event": "capability-lifecycle-event.v1",
            "profiles": "skill-operation-profiles.v1",
            "doctor": "skill-doctor.v1",
            "package": "skill-package-readiness.v1",
            "memory": "skill-memory-provider.v1",
        },
        "event_types": event_types,
        "event_consumers": event_consumers,
        "readiness_overview": _skill_events_readiness_overview(event_summary),
        "event_summary": event_summary,
        "validation_commands": [
            _skills_validation_command("events"),
            "./bin/ask skills events <event-type> --json --robot",
            _skills_validation_command("list"),
        ],
        "eval_blocker_classes": {
            blocker_class: DOCTOR_BLOCKER_TAXONOMY[blocker_class]
            for blocker_class in EVAL_BLOCKER_CLASSES
        },
        "blocker_taxonomy": DOCTOR_BLOCKER_TAXONOMY,
        "warning_taxonomy": DOCTOR_WARNING_TAXONOMY,
        "event_order": list(CAPABILITY_LIFECYCLE_EVENT_TYPES),
        "event_count": len(event_types),
        "agent_summary": (
            f"Lifecycle event '{selected}' is declared."
            if selected
            else f"{len(CAPABILITY_LIFECYCLE_EVENT_TYPES)} capability lifecycle event types are declared."
        ),
    }
    return result


def _skill_profile_workspace_roots(repo_root: Path) -> dict[str, Any]:
    return {
        "repo_root": str(repo_root),
        "canonical_skill_roots": ["Skills", "Plugins"],
        "runtime_projection_roots": [".agents/skills", ".skillsets"],
        "artifact_roots": ["Infrastructure/artifacts", "Infrastructure/workouts"],
        "memory_roots": [".harness/memory", "Wiki/wiki/learnings", "Docs/solutions"],
    }


def _profiles_with_effective_roots(profiles: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    enriched: dict[str, dict[str, Any]] = {}
    for name, profile in profiles.items():
        stop_conditions = list(profile.get("stop_conditions", []))
        enriched_profile = {
            **profile,
            "effective_roots": list(profile.get("allowed_roots", [])),
        }
        blocker_definitions = {
            condition: DOCTOR_BLOCKER_TAXONOMY[condition]
            for condition in stop_conditions
            if condition in DOCTOR_BLOCKER_TAXONOMY
        }
        if blocker_definitions:
            enriched_profile["stop_condition_definitions"] = blocker_definitions
        if name == "eval":
            enriched_profile["eval_blocker_classes"] = {
                blocker_class: DOCTOR_BLOCKER_TAXONOMY[blocker_class]
                for blocker_class in EVAL_BLOCKER_CLASSES
            }
            enriched_profile["eval_profile_contract"] = {
                "codex_profile": "fast",
                "codex_profile_config": "[profiles.fast]",
                "codex_runner_args": ["--profile", "fast"],
                "tessl_eval_staging_root": f"{os.path.join(tempfile.gettempdir(), 'ask-tessl-evals')}/<skill-path>-<sha12>",
                "tessl_project_marker": "tessl.json",
                "staged_inputs": [
                    "SKILL.md",
                    "references/evals.yaml",
                    "references/contract.yaml",
                    "references/task-profile.json",
                    "scenarios/<case-id>/task.md",
                ],
                "evidence_retention": "stable tmp staging is intentionally left for post-run inspection",
            }
        if name == "package-review":
            enriched_profile["external_review_contract"] = {
                "plugin_eval_min_acceptable_grade": PLUGIN_EVAL_MIN_ACCEPTABLE_GRADE,
                "plugin_eval_b_plus_is_acceptable": True,
                "tessl_review_min_score": TESSL_REVIEW_MIN_SCORE,
                "tessl_review_target_score": TESSL_REVIEW_TARGET_SCORE,
                "tessl_review_args": ["skill", "review", "--json", "--threshold", str(TESSL_REVIEW_MIN_SCORE)],
                "tessl_review_staging_root": f"{os.path.join(tempfile.gettempdir(), 'ask-tessl-reviews')}/<skill-path>-<sha12>",
                "tessl_project_marker": "tessl.json",
                "evidence_retention": "stable tmp wrapper is intentionally left for post-run inspection",
            }
        enriched[name] = enriched_profile
    return enriched


def _skill_profile_event_coverage(
    profiles: dict[str, dict[str, Any]],
    event_consumers: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Return lifecycle event coverage grouped by operation profile."""
    events_by_profile = {profile_name: [] for profile_name in profiles}
    for event_name, consumer in event_consumers.items():
        for profile_name in consumer.get("profiles", []):
            if profile_name in events_by_profile:
                events_by_profile[profile_name].append(event_name)
    profiles_missing_events = sorted(
        profile_name
        for profile_name, event_names in events_by_profile.items()
        if not event_names
    )
    profiles_with_events = sorted(
        profile_name
        for profile_name, event_names in events_by_profile.items()
        if event_names
    )
    event_coverage_gaps = profiles_missing_events
    return {
        "profile_count": len(profiles),
        "profile_names": sorted(profiles),
        "events_by_profile": {
            profile_name: sorted(event_names)
            for profile_name, event_names in events_by_profile.items()
        },
        "event_count_by_profile": {
            profile_name: len(event_names)
            for profile_name, event_names in events_by_profile.items()
        },
        "event_reference_count": sum(len(event_names) for event_names in events_by_profile.values()),
        "profiles_with_events": profiles_with_events,
        "profiles_with_event_count": len(profiles_with_events),
        "profiles_missing_events": profiles_missing_events,
        "profiles_missing_event_count": len(profiles_missing_events),
        "has_profiles_missing_events": bool(profiles_missing_events),
        "all_profiles_have_events": bool(profiles) and not profiles_missing_events,
        "profiles_with_event_gaps": event_coverage_gaps,
        "profiles_with_event_gap_count": len(event_coverage_gaps),
        **_contract_readiness(bool(profiles), event_coverage_gaps),
    }


def _skill_profiles_operation_context() -> dict[str, Any]:
    """Return command surfaces that consume operation profiles."""
    return {
        "profile_model": "profile-v2-inspired",
        "contract_schemas": {
            "profiles": "skill-operation-profiles.v1",
            "events": "skill-events.v1",
            "lifecycle_event": "capability-lifecycle-event.v1",
            "doctor": "skill-doctor.v1",
            "package": "skill-package-readiness.v1",
            "memory": "skill-memory-provider.v1",
        },
        "consumer_commands": {
            "doctor": "./bin/ask skills doctor <handle-or-path> --json --robot",
            "package": "./bin/ask skills package <handle-or-path> --json --robot",
            "events": _skills_validation_command("events"),
            "memory": "./bin/ask skills memory search <query> --json --robot",
        },
        "routing_contracts": {
            "doctor": ["authoring", "package-review", "eval"],
            "package": ["package-review", "plugin-share"],
            "memory": ["authoring", "package-review", "eval"],
            "events": ["authoring", "package-review", "plugin-share", "eval", "live-mutation"],
        },
        "validation_commands": [
            _skills_validation_command("list"),
            _skills_validation_command("events"),
        ],
    }


def _skill_profile_summary(profiles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return compact profile coverage counts for automation consumers."""
    by_write_policy: dict[str, int] = {}
    by_permission: dict[str, int] = {}
    root_count = 0
    stop_condition_count = 0
    required_evidence_count = 0
    profiles_missing_write_policy: list[str] = []
    profiles_missing_allowed_roots: list[str] = []
    profiles_missing_permissions: list[str] = []
    profiles_missing_stop_conditions: list[str] = []
    profiles_missing_required_evidence: list[str] = []
    taxonomy_stop_conditions_by_profile: dict[str, list[str]] = {}
    profiles_without_taxonomy_stop_conditions: list[str] = []
    required_evidence_by_profile: dict[str, list[str]] = {}
    permissions_by_profile: dict[str, list[str]] = {}
    allowed_roots_by_profile: dict[str, list[str]] = {}
    write_policy_by_profile: dict[str, str] = {}
    stop_conditions_by_profile: dict[str, list[str]] = {}
    for profile_name, profile in profiles.items():
        write_policy_value = profile.get("write_policy")
        write_policy = str(write_policy_value or "unknown")
        if not write_policy_value:
            profiles_missing_write_policy.append(profile_name)
        write_policy_by_profile[profile_name] = write_policy
        by_write_policy[write_policy] = by_write_policy.get(write_policy, 0) + 1
        roots = profile.get("allowed_roots", [])
        profile_root_count = len(roots) if isinstance(roots, list) else 0
        root_count += profile_root_count
        if profile_root_count == 0:
            profiles_missing_allowed_roots.append(profile_name)
        if isinstance(roots, list):
            allowed_roots_by_profile[profile_name] = sorted(str(root) for root in roots)
        stop_conditions = profile.get("stop_conditions", [])
        profile_stop_condition_count = len(stop_conditions) if isinstance(stop_conditions, list) else 0
        stop_condition_count += profile_stop_condition_count
        if profile_stop_condition_count == 0:
            profiles_missing_stop_conditions.append(profile_name)
        if isinstance(stop_conditions, list):
            stop_conditions_by_profile[profile_name] = sorted(str(condition) for condition in stop_conditions)
        taxonomy_stop_conditions = sorted(
            str(condition)
            for condition in stop_conditions
            if isinstance(condition, str) and condition in DOCTOR_BLOCKER_TAXONOMY
        )
        if taxonomy_stop_conditions:
            taxonomy_stop_conditions_by_profile[profile_name] = taxonomy_stop_conditions
        else:
            profiles_without_taxonomy_stop_conditions.append(profile_name)
        required_evidence = profile.get("required_evidence", [])
        profile_required_evidence_count = len(required_evidence) if isinstance(required_evidence, list) else 0
        required_evidence_count += profile_required_evidence_count
        if profile_required_evidence_count == 0:
            profiles_missing_required_evidence.append(profile_name)
        if isinstance(required_evidence, list):
            required_evidence_by_profile[profile_name] = sorted(str(item) for item in required_evidence)
        permissions = profile.get("permissions", [])
        profile_permission_count = len(permissions) if isinstance(permissions, list) else 0
        if profile_permission_count == 0:
            profiles_missing_permissions.append(profile_name)
        if isinstance(permissions, list):
            permissions_by_profile[profile_name] = sorted(str(permission) for permission in permissions)
            for permission in permissions:
                key = str(permission)
                by_permission[key] = by_permission.get(key, 0) + 1
    profiles_with_contract_gaps = sorted(
        set(
            profiles_missing_write_policy
            + profiles_missing_allowed_roots
            + profiles_missing_permissions
            + profiles_missing_stop_conditions
            + profiles_missing_required_evidence
        )
    )
    missing_by_contract_dimension = {
        "write_policy": sorted(profiles_missing_write_policy),
        "permissions": sorted(profiles_missing_permissions),
        "allowed_roots": sorted(profiles_missing_allowed_roots),
        "stop_conditions": sorted(profiles_missing_stop_conditions),
        "required_evidence": sorted(profiles_missing_required_evidence),
    }
    return {
        "profile_count": len(profiles),
        "profile_names": sorted(profiles),
        "has_profiles": bool(profiles),
        "contract_dimensions": sorted(missing_by_contract_dimension),
        "contract_dimension_count": len(missing_by_contract_dimension),
        "contract_dimension_status": {
            dimension: _contract_status(bool(profiles), missing_profiles)
            for dimension, missing_profiles in missing_by_contract_dimension.items()
        },
        "missing_profiles_by_contract_dimension": missing_by_contract_dimension,
        "missing_profile_count_by_contract_dimension": {
            dimension: len(missing_profiles)
            for dimension, missing_profiles in missing_by_contract_dimension.items()
        },
        "by_write_policy": by_write_policy,
        "write_policy_count": len(by_write_policy),
        "write_policy_by_profile": write_policy_by_profile,
        "profiles_missing_write_policy": sorted(profiles_missing_write_policy),
        "profiles_missing_write_policy_count": len(profiles_missing_write_policy),
        "has_profiles_missing_write_policy": bool(profiles_missing_write_policy),
        "all_profiles_have_write_policy": bool(profiles) and not profiles_missing_write_policy,
        "by_permission": by_permission,
        "permission_count": len(by_permission),
        "permissions_by_profile": permissions_by_profile,
        "permission_count_by_profile": {
            profile_name: len(permission_items)
            for profile_name, permission_items in permissions_by_profile.items()
        },
        "profiles_missing_permissions": sorted(profiles_missing_permissions),
        "profiles_missing_permission_count": len(profiles_missing_permissions),
        "has_profiles_missing_permissions": bool(profiles_missing_permissions),
        "all_profiles_have_permissions": bool(profiles) and not profiles_missing_permissions,
        "allowed_root_count": root_count,
        "allowed_roots_by_profile": allowed_roots_by_profile,
        "allowed_root_count_by_profile": {
            profile_name: len(root_items)
            for profile_name, root_items in allowed_roots_by_profile.items()
        },
        "profiles_missing_allowed_roots": sorted(profiles_missing_allowed_roots),
        "profiles_missing_allowed_root_count": len(profiles_missing_allowed_roots),
        "has_profiles_missing_allowed_roots": bool(profiles_missing_allowed_roots),
        "all_profiles_have_allowed_roots": bool(profiles) and not profiles_missing_allowed_roots,
        "stop_condition_count": stop_condition_count,
        "has_stop_conditions": stop_condition_count > 0,
        "stop_conditions_by_profile": stop_conditions_by_profile,
        "stop_condition_count_by_profile": {
            profile_name: len(condition_items)
            for profile_name, condition_items in stop_conditions_by_profile.items()
        },
        "profiles_missing_stop_conditions": sorted(profiles_missing_stop_conditions),
        "profiles_missing_stop_condition_count": len(profiles_missing_stop_conditions),
        "has_profiles_missing_stop_conditions": bool(profiles_missing_stop_conditions),
        "all_profiles_have_stop_conditions": bool(profiles) and not profiles_missing_stop_conditions,
        "taxonomy_stop_conditions_by_profile": taxonomy_stop_conditions_by_profile,
        "taxonomy_stop_condition_count": sum(
            len(conditions) for conditions in taxonomy_stop_conditions_by_profile.values()
        ),
        "profiles_with_taxonomy_stop_conditions": sorted(taxonomy_stop_conditions_by_profile),
        "profiles_with_taxonomy_stop_condition_count": len(taxonomy_stop_conditions_by_profile),
        "profiles_without_taxonomy_stop_conditions": sorted(profiles_without_taxonomy_stop_conditions),
        "profiles_without_taxonomy_stop_condition_count": len(profiles_without_taxonomy_stop_conditions),
        "has_profiles_without_taxonomy_stop_conditions": bool(profiles_without_taxonomy_stop_conditions),
        "all_profiles_have_taxonomy_stop_conditions": bool(profiles) and not profiles_without_taxonomy_stop_conditions,
        "has_taxonomy_stop_conditions": bool(taxonomy_stop_conditions_by_profile),
        "required_evidence_count": required_evidence_count,
        "has_required_evidence": required_evidence_count > 0,
        "required_evidence_by_profile": required_evidence_by_profile,
        "required_evidence_count_by_profile": {
            profile_name: len(evidence_items)
            for profile_name, evidence_items in required_evidence_by_profile.items()
        },
        "profiles_missing_required_evidence": sorted(profiles_missing_required_evidence),
        "profiles_missing_required_evidence_count": len(profiles_missing_required_evidence),
        "has_profiles_missing_required_evidence": bool(profiles_missing_required_evidence),
        "all_profiles_have_required_evidence": bool(profiles) and not profiles_missing_required_evidence,
        "profiles_with_contract_gaps": profiles_with_contract_gaps,
        **_contract_readiness(bool(profiles), profiles_with_contract_gaps),
    }


def _skill_profiles_readiness_overview(
    profile_summary: dict[str, Any],
    event_coverage: dict[str, Any],
) -> dict[str, Any]:
    """Return a compact cross-contract readiness summary for profile consumers."""
    return _contract_sections_overview({
        "profile_contracts": {
            "status": profile_summary["contract_status"],
            "ready": profile_summary["contract_ready"],
            "gap_count": profile_summary["contract_gap_count"],
        },
        "lifecycle_event_coverage": {
            "status": event_coverage["contract_status"],
            "ready": event_coverage["contract_ready"],
            "gap_count": event_coverage["contract_gap_count"],
        },
    })


def skills_profiles(repo_root: Path, profile: str | None = None) -> CallResult:
    """Return profile-v2-style operation modes for skill lifecycle work."""
    result = CallResult()
    result.metadata["command"] = "skills profiles"
    profile_key = profile.strip() if profile else None
    profiles = SKILL_OPERATION_PROFILES
    if profile_key:
        if profile_key not in profiles:
            result.status = "error"
            result.data["skill_profiles"] = {
                "schema_version": "skill-operation-profiles.v1",
                "status": "blocked",
                "selected_profile": None,
                "requested_profile": profile_key,
                "available_profiles": sorted(profiles),
            }
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=f"Unknown skill operation profile '{profile_key}'.",
                    fix_suggestion=f"Use one of: {', '.join(sorted(profiles))}",
                )
            )
            return result
        selected_profiles = {profile_key: profiles[profile_key]}
    else:
        selected_profiles = profiles

    profile_summary = _skill_profile_summary(selected_profiles)
    event_coverage = _skill_profile_event_coverage(selected_profiles, CAPABILITY_LIFECYCLE_EVENT_CONSUMERS)

    result.data["skill_profiles"] = {
        "schema_version": "skill-operation-profiles.v1",
        "status": "pass",
        "repo_root": str(repo_root),
        "workspace_roots": _skill_profile_workspace_roots(repo_root),
        "profile_model": "profile-v2-inspired",
        "operation_context": _skill_profiles_operation_context(),
        "selected_profile": profile_key,
        "profile_names": list(selected_profiles),
        "available_profiles": sorted(profiles),
        "readiness_overview": _skill_profiles_readiness_overview(profile_summary, event_coverage),
        "profile_summary": profile_summary,
        "event_coverage": event_coverage,
        "eval_blocker_classes": {
            blocker_class: DOCTOR_BLOCKER_TAXONOMY[blocker_class]
            for blocker_class in EVAL_BLOCKER_CLASSES
        },
        "blocker_taxonomy": DOCTOR_BLOCKER_TAXONOMY,
        "warning_taxonomy": DOCTOR_WARNING_TAXONOMY,
        "profiles": _profiles_with_effective_roots(selected_profiles),
        "profile_order": ["authoring", "package-review", "plugin-share", "eval", "live-mutation"],
        "agent_summary": (
            f"Profile '{profile_key}' is declared."
            if profile_key
            else f"{len(profiles)} skill operation profiles are declared."
        ),
    }
    return result


def _doctor_check(status: str, **details: Any) -> dict[str, Any]:
    check_name = str(details.pop("check_name", "") or "")
    payload = {
        "status": status,
        "sdk_layer": _doctor_sdk_layer_for("check", check_name),
    }
    payload.update(details)
    return payload


PROJECT_SKILLS_SDK_MANIFEST = "skills-sdk.json"
PROJECT_SKILLS_SDK_SCHEMA = "Infrastructure/config/schemas/skills-sdk.project.v1.schema.json"
PROJECT_SKILL_ROOT_CLASSIFICATIONS = {
    "canonical_project_source",
    "generated_runtime_projection",
    "client_runtime_config",
    "unknown",
}


def _repo_relative_path_parts(path: str) -> tuple[str, ...]:
    return tuple(part.casefold() for part in Path(path.strip().strip("/")).parts)


def _path_is_under_declared_skill_root(path: str, root: str) -> bool:
    path_parts = _repo_relative_path_parts(path)
    root_parts = _repo_relative_path_parts(root)
    return bool(root_parts) and path_parts[: len(root_parts)] == root_parts


def _load_project_skills_sdk_manifest(repo_root: Path | None) -> dict[str, Any] | None:
    if repo_root is None:
        return None
    manifest_path = repo_root / PROJECT_SKILLS_SDK_MANIFEST
    if not manifest_path.is_file():
        return None
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    if payload.get("schema_version") != "skills-sdk.project.v1":
        return None
    seen_root_paths: set[str] = set()
    for root in payload.get("skill_roots", []):
        if not isinstance(root, dict):
            continue
        root_path = str(root.get("path") or "").strip().strip("/")
        if not root_path:
            continue
        normalized_root = "/".join(_repo_relative_path_parts(root_path))
        if normalized_root in seen_root_paths:
            return None
        seen_root_paths.add(normalized_root)
    return payload


def _manifest_skill_root_ownership(repo_root: Path | None, path: str) -> dict[str, Any] | None:
    manifest = _load_project_skills_sdk_manifest(repo_root)
    if not manifest:
        return None
    matches: list[tuple[int, str, str]] = []
    for root in manifest.get("skill_roots", []):
        if not isinstance(root, dict):
            continue
        root_path = str(root.get("path") or "").strip().strip("/")
        if not root_path or not _path_is_under_declared_skill_root(path, root_path):
            continue
        classification = str(root.get("classification") or "unknown")
        if classification not in PROJECT_SKILL_ROOT_CLASSIFICATIONS:
            continue
        matches.append((len(_repo_relative_path_parts(root_path)), root_path, classification))
    if not matches:
        return None
    _, root_path, classification = max(matches, key=lambda item: item[0])
    editable_source = classification == "canonical_project_source"
    return {
        "path": path,
        "root": root_path,
        "classification": classification,
        "editable_source": editable_source,
        "owner_manifest_required_for_edit": not editable_source,
        "manifest_schema": PROJECT_SKILLS_SDK_SCHEMA,
        "manifest_declared": True,
        "owner_manifest_path": PROJECT_SKILLS_SDK_MANIFEST,
        "owner_manifest_project_id": manifest.get("project_id"),
    }


def _skill_root_ownership_for_path(
    repo_relative_path: str | None,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Classify whether a repo-relative skill path is editable source or projection."""
    if not repo_relative_path:
        return {
            "path": None,
            "root": None,
            "classification": "unknown",
            "editable_source": False,
            "owner_manifest_required_for_edit": False,
        }

    path = repo_relative_path.strip().strip("/")
    parts = Path(path).parts
    normalized_parts = _repo_relative_path_parts(path)
    manifest_ownership = _manifest_skill_root_ownership(repo_root, path)
    if manifest_ownership:
        return manifest_ownership
    if normalized_parts[:2] == (".agents", "skills"):
        return {
            "path": path,
            "root": ".agents/skills",
            "classification": "generated_runtime_projection",
            "editable_source": False,
            "owner_manifest_required_for_edit": True,
            "manifest_schema": PROJECT_SKILLS_SDK_SCHEMA,
            "manifest_declared": False,
        }
    if normalized_parts[:2] == (".codex", "skills"):
        return {
            "path": path,
            "root": ".codex/skills",
            "classification": "client_runtime_config",
            "editable_source": False,
            "owner_manifest_required_for_edit": True,
            "manifest_schema": PROJECT_SKILLS_SDK_SCHEMA,
            "manifest_declared": False,
        }
    if path.startswith("Skills/") or path == "Skills":
        return {
            "path": path,
            "root": "Skills/**",
            "classification": "canonical_project_source",
            "editable_source": True,
            "owner_manifest_required_for_edit": False,
            "owner_kind": "repo_skills",
        }
    if len(parts) >= 3 and parts[0] == "Plugins" and parts[2] == "skills":
        return {
            "path": path,
            "root": "Plugins/*/skills/**",
            "classification": "canonical_project_source",
            "editable_source": True,
            "owner_manifest_required_for_edit": False,
            "owner_kind": "plugin_skills",
        }
    return {
        "path": path,
        "root": None,
        "classification": "unknown",
        "editable_source": False,
        "owner_manifest_required_for_edit": False,
    }


def _skill_doctor_next_command_decision(
    *,
    blockers: list[dict[str, str]],
    warnings: list[dict[str, str]],
    checks: dict[str, Any],
    normalized_handle: Any,
    query: str,
    audit_target: str | None,
    strict: bool,
) -> dict[str, str | None]:
    """Select the most actionable follow-up command from classified doctor evidence."""
    blocker_classes = [blocker.get("class") for blocker in blockers]
    if "blocked_validation" in blocker_classes:
        command = checks.get("structural_audit", {}).get("command")
        if command:
            return {
                "command": str(command),
                "precedence": "blocker",
                "source_class": "blocked_validation",
                "source_check": "structural_audit",
                "reason": "blocked_validation takes precedence; rerun the structural audit that failed.",
            }
        if audit_target:
            return {
                "command": _skills_validation_command("audit", audit_target, "--level", "compat"),
                "precedence": "blocker",
                "source_class": "blocked_validation",
                "source_check": "structural_audit",
                "reason": "blocked_validation takes precedence; no check command was present, so use the compatibility audit fallback.",
            }
    if "blocked_runtime" in blocker_classes:
        command = checks.get("runtime_reachability", {}).get("command")
        if command:
            return {
                "command": str(command),
                "precedence": "blocker",
                "source_class": "blocked_runtime",
                "source_check": "runtime_reachability",
                "reason": "blocked_runtime takes precedence after validation blockers; rerun the runtime reachability proof.",
            }
    if "blocked_missing_source" in blocker_classes:
        return {
            "command": _skills_validation_command("resolve", str(normalized_handle or query)),
            "precedence": "blocker",
            "source_class": "blocked_missing_source",
            "source_check": "canonical_source",
            "reason": "blocked_missing_source requires resolving the target before any runtime or package proof.",
        }
    if "blocked_resolution" in blocker_classes:
        return {
            "command": _skills_validation_command("resolve", str(normalized_handle or query)),
            "precedence": "blocker",
            "source_class": "blocked_resolution",
            "source_check": "resolver",
            "reason": "blocked_resolution requires resolving the requested handle before follow-up checks.",
        }
    if blockers:
        return {
            "command": _skills_validation_command("doctor", str(normalized_handle or query)),
            "precedence": "blocker",
            "source_class": str(blocker_classes[0] or "unclassified_blocker"),
            "source_check": None,
            "reason": "An unclassified blocker remains; rerun doctor to preserve the full diagnostic payload.",
        }

    warning_classes = {warning.get("class") for warning in warnings}
    package_or_metadata_warning = bool(
        {"metadata_incomplete", "capability_contract_incomplete"} & warning_classes
    )
    if package_or_metadata_warning and audit_target and not strict:
        return {
            "command": _skills_validation_command("audit", audit_target, "--level", "strict"),
            "precedence": "warning",
            "source_class": "metadata_incomplete" if "metadata_incomplete" in warning_classes else "capability_contract_incomplete",
            "source_check": "capability_metadata",
            "reason": "Package or metadata warnings should be tightened by strict audit before package proof.",
        }
    if "capability_contract_incomplete" in warning_classes:
        return {
            "command": _skills_validation_command("package", str(normalized_handle or query)),
            "precedence": "warning",
            "source_class": "capability_contract_incomplete",
            "source_check": "package_readiness",
            "reason": "Capability package metadata is incomplete; run the package readiness command.",
        }
    if "outcome_proof_missing" in warning_classes:
        return {
            "command": _skills_validation_command("prove", str(normalized_handle or query)),
            "precedence": "warning",
            "source_class": "outcome_proof_missing",
            "source_check": "outcome_proof",
            "reason": "Outcome proof is missing; run the proof scorecard command.",
        }
    if warnings and audit_target and not strict:
        return {
            "command": _skills_validation_command("audit", audit_target, "--level", "strict"),
            "precedence": "warning",
            "source_class": str(next(iter(warning_classes), "unclassified_warning")),
            "source_check": None,
            "reason": "A warning remains and strict audit has not run; run strict audit before claiming readiness.",
        }
    if normalized_handle:
        return {
            "command": _skills_validation_command("prove", str(normalized_handle)),
            "precedence": "default",
            "source_class": None,
            "source_check": "outcome_proof",
            "reason": "No blockers or warnings remain; run the proof scorecard as the next evidence command.",
        }
    return {
        "command": _skills_validation_command("audit", str(audit_target), "--level", "strict"),
        "precedence": "default",
        "source_class": None,
        "source_check": "structural_audit",
        "reason": "No handle is available; strict audit is the safest remaining source-path evidence command.",
    }


def skills_load_preview(repo_root: Path) -> CallResult:
    """
    Builds a Codex load preview for the repository.
    
    Parameters:
    	repo_root (Path): Path to the repository root used to generate the preview.
    
    Returns:
    	result (CallResult): A CallResult whose `data["codex_load_preview"]` contains the preview payload. The result.metadata includes `command = "skills load-preview"`.
    """
    result = CallResult()
    result.metadata["command"] = "skills load-preview"
    result.data["codex_load_preview"] = build_codex_load_preview(repo_root)
    return result


def skills_codex_preview(repo_root: Path) -> CallResult:
    """
    Builds a Codex-mode preview payload summarizing source-modeled skill discovery and available preview commands.
    
    The returned CallResult contains a `codex_preview` payload with keys such as `schema_version`, `command`, `status`, `source_identity`, `source_basis`, `blocked_checks`, `modeled_rule_version`, `source_files`, `commands` (each with `name`, `purpose`, and `validation_command`), and an `agent_summary`. The CallResult metadata will include `command = "skills codex-preview"`.
    
    Returns:
        CallResult: A result whose `data["codex_preview"]` holds the structured Codex preview payload.
    """
    load_preview = build_codex_load_preview(repo_root)
    result = CallResult()
    result.metadata["command"] = "skills codex-preview"
    result.data["codex_preview"] = {
        "schema_version": CODEX_PREVIEW_SCHEMA_VERSION,
        "command": "skills codex-preview",
        "status": load_preview.get("status"),
        "not_a_validation_result": True,
        "source_identity": load_preview.get("source_identity"),
        "source_basis": load_preview.get("source_basis"),
        "blocked_checks": load_preview.get("blocked_checks", []),
        "modeled_rule_version": CODEX_PREVIEW_MODELED_RULE_VERSION,
        "source_files": list(CODEX_PREVIEW_SOURCE_FILES),
        "commands": [
            {
                "name": "load-preview",
                "purpose": "Model Codex skill-root loading and scan visible SKILL.md metadata.",
                "validation_command": _skills_validation_command("load-preview"),
            },
            {
                "name": "render-preview",
                "purpose": "Model available-skill rendering, source basis, budget, and truncation status.",
                "validation_command": _skills_validation_command("render-preview"),
            },
            {
                "name": "config explain",
                "purpose": "Explain source-backed Codex skills.config rule semantics and blocked live layers.",
                "validation_command": _skills_validation_command("config", "explain"),
            },
            {
                "name": "inject-preview",
                "purpose": "Model explicit skill mention selection from prompt text.",
                "validation_command": _skills_validation_command("inject-preview", "$skill"),
            },
            {
                "name": "implicit-preview",
                "purpose": "Model implicit invocation attribution from a shell command.",
                "validation_command": _skills_validation_command("implicit-preview", "--command", "cat SKILL.md"),
            },
        ],
        "agent_summary": "Use the listed public skills preview commands for source-modeled Codex preview evidence; they do not claim live runtime parity.",
    }
    return result


def skills_capabilities(repo_root: Path, runtime_target: str = "codex") -> CallResult:
    """Report runtime proof-plane capability discovery for agents."""
    target = normalize_runtime_target(runtime_target)
    supported_targets = [runtime_target for runtime_target in ("any", "codex", "agents") if runtime_target in SUPPORTED_RUNTIME_TARGETS]
    result = CallResult()
    result.metadata["command"] = "skills capabilities"
    if target not in supported_targets:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Invalid runtime target '{target}'.",
                fix_suggestion="Use --runtime-target any, --runtime-target codex, or --runtime-target agents.",
            )
        )
        return result
    preview = build_codex_load_preview(repo_root)
    proof_targets = [runtime_target for runtime_target in ("codex", "agents") if runtime_target in EVIDENCE_RUNTIME_TARGETS] if target == "any" else [target]
    live_runtime_parity = "not_applicable_discovery_only" if target == "any" else "not_claimed"
    blockers = list(preview.get("blocked_checks", []))
    readiness = "discovery_only" if target == "any" else ("partial" if blockers else "available")
    proof_commands = [_skills_validation_command("proof", "HANDLE", "--runtime-target", proof_target) for proof_target in proof_targets]
    artifact_paths = [
        f".harness/evidence/runtime-proof/<handle>/{proof_target}/{artifact_name}"
        for proof_target in proof_targets
        for artifact_name in ("runtime-card.json", "evidence-receipt.json", "artifact-record.json", "probe.json")
    ]
    result.data["capability_discovery"] = {
        "schema_version": "capability-discovery.v1",
        "command": "skills capabilities",
        "runtime_target": target,
        "status": readiness,
        "runtime_target_support": {
            "supported_targets": supported_targets,
            "selected": target,
            "evidence_targets": ["codex", "agents"],
        },
        "evidence_modes": [
            {
                "mode": "source_modeled",
                "status": "available",
                "commands": [
                    _skills_validation_command("codex-preview"),
                    _skills_validation_command("render-preview"),
                    _skills_validation_command("conformance", "run", "--suite", "codex-parity"),
                ],
            },
            {
                "mode": "runtime_evidence",
                "status": "available",
                "commands": [*proof_commands, _ask_validation_command("repo", "closeout", "--changed")],
            },
        ],
        "supported_commands": [
            {"name": f"skills proof ({proof_target})", "command": proof_command}
            for proof_target, proof_command in zip(proof_targets, proof_commands)
        ] + [
            {"name": "skills conformance run", "command": _skills_validation_command("conformance", "run", "--suite", "codex-parity")},
            {"name": "skills codex-preview", "command": _skills_validation_command("codex-preview")},
            {"name": "repo closeout", "command": _ask_validation_command("repo", "closeout", "--changed")},
        ],
        "required_artifacts": artifact_paths,
        "known_limitations": [
            {
                "class": "live_runtime_parity_not_claimed",
                "message": "Capability discovery reports available commands; it does not prove live runtime parity."
                if target == "any"
                else f"Capability discovery reports available commands; it does not prove live {target} runtime parity.",
            },
            {
                "class": "explicit_runtime_required_for_artifacts",
                "message": "Use an explicit runtime target before expecting runtime-card artifacts.",
            }
        ],
        "blocked_checks": blockers,
        "source_basis": preview.get("source_basis"),
        "next_actions": [
            _skills_validation_command("proof", "HANDLE", "--runtime-target", proof_targets[0]),
            _ask_validation_command("repo", "closeout", "--changed"),
        ],
        "truth_boundaries": {
            "capability_discovery": "checked",
            "live_runtime_parity": live_runtime_parity,
            "schema_validation": "not_run_use_validate_runtime_cards",
        },
    }
    return result


def format_capabilities_human(discovery: dict[str, object]) -> list[str]:
    """
    Format a human-readable summary of a capability discovery payload.
    
    Parses the given discovery mapping for runtime target/status, truth boundaries (e.g. live_runtime_parity),
    available evidence modes, blocked fidelity checks count, and the first next action, then returns a short
    list of one-line summary strings suitable for display.
    
    Parameters:
        discovery (dict): Capability discovery payload containing keys such as
            'runtime_target', 'status', 'truth_boundaries', 'evidence_modes',
            'blocked_checks', and 'next_actions'.
    
    Returns:
        list[str]: One-line summary strings describing the capability discovery.
    """
    boundaries = discovery.get("truth_boundaries") if isinstance(discovery.get("truth_boundaries"), dict) else {}
    modes = discovery.get("evidence_modes") if isinstance(discovery.get("evidence_modes"), list) else []
    mode_names = [mode.get("mode") for mode in modes if isinstance(mode, dict) and mode.get("mode")]
    lines = [
        "Skills capabilities: "
        f"target={discovery.get('runtime_target')} status={discovery.get('status')}",
        f"Live runtime parity: {boundaries.get('live_runtime_parity')}",
        f"Evidence modes: {', '.join(mode_names) if mode_names else 'none'}",
    ]
    blocked_checks = discovery.get("blocked_checks") if isinstance(discovery.get("blocked_checks"), list) else []
    if blocked_checks:
        lines.append(f"Blocked fidelity checks: {len(blocked_checks)}")
    next_actions = discovery.get("next_actions") if isinstance(discovery.get("next_actions"), list) else []
    if next_actions:
        lines.append(f"Next: {next_actions[0]}")
    return lines


def format_codex_preview_human(preview: dict[str, object]) -> list[str]:
    """
    Format a Codex preview payload into a list of human-readable summary lines.
    
    Parameters:
        preview (dict[str, object]): A Codex preview dictionary containing optional keys:
            - "source_basis" (dict): source-derived metadata such as "live_runtime_parity".
            - "commands" (list): list of command descriptor dicts with "name" and "validation_command".
            - "blocked_checks" (list): list of blocked fidelity checks.
            - "status" (str): overall preview status.
            - "not_a_validation_result" (bool): when true, indicates the preview is source-modeled only.
    
    Returns:
        list[str]: Ordered summary lines including a commands/count/status header, notes about
        source-modeled vs runtime validation, live runtime parity when present, a blocked-checks
        summary when present, and one line per command in the form "- <name>: <validation_command>".
    """
    source_basis = preview.get("source_basis") if isinstance(preview.get("source_basis"), dict) else {}
    commands = preview.get("commands") if isinstance(preview.get("commands"), list) else []
    blocked_checks = preview.get("blocked_checks") if isinstance(preview.get("blocked_checks"), list) else []
    lines = [f"Codex preview commands: {len(commands)} command(s), status={preview.get('status')}"]
    if preview.get("not_a_validation_result"):
        lines.append("Preview basis: source-modeled only; not a runtime validation result")
    if source_basis.get("live_runtime_parity"):
        lines.append(f"Live runtime parity: {source_basis.get('live_runtime_parity')}")
    if blocked_checks:
        lines.append(f"Blocked fidelity checks: {len(blocked_checks)}")
    lines.extend(f"- {command.get('name')}: {command.get('validation_command')}" for command in commands if isinstance(command, dict))
    return lines


def skills_render_preview(repo_root: Path, context_window: int | None = None) -> CallResult:
    """
    Produce a Codex-based render preview payload for the repository.
    
    Parameters:
        repo_root (Path): Repository root used to discover and model skills.
        context_window (int | None): Optional maximum context window size to use when building the preview; when omitted the default sizing is applied.
    
    Returns:
        CallResult: A CallResult whose `data["codex_render_preview"]` contains the render preview payload.
    """
    result = CallResult()
    result.metadata["command"] = "skills render-preview"
    result.data["codex_render_preview"] = build_codex_render_preview(repo_root, context_window)
    return result


def skills_config_explain(repo_root: Path) -> CallResult:
    result = CallResult()
    result.metadata["command"] = "skills config explain"
    result.data["codex_config_explain"] = build_codex_config_explain(repo_root)
    return result


def skills_inject_preview(repo_root: Path, text: str) -> CallResult:
    result = CallResult()
    result.metadata["command"] = "skills inject-preview"
    result.data["codex_inject_preview"] = build_codex_inject_preview(repo_root, text)
    return result


def skills_implicit_preview(repo_root: Path, command: str, workdir: str | None = None) -> CallResult:
    result = CallResult()
    result.metadata["command"] = "skills implicit-preview"
    result.data["codex_implicit_preview"] = build_codex_implicit_preview(repo_root, command, workdir)
    return result


def _skill_package_operation_context() -> dict[str, Any]:
    """Return profile and event routing context for package readiness checks."""
    return {
        "primary_profile": "package-review",
        "promotion_profile": "plugin-share",
        "profiles": {
            profile_name: {
                "intent": SKILL_OPERATION_PROFILES[profile_name]["intent"],
                "write_policy": SKILL_OPERATION_PROFILES[profile_name]["write_policy"],
                "required_evidence": SKILL_OPERATION_PROFILES[profile_name]["required_evidence"],
            }
            for profile_name in ("package-review", "plugin-share")
        },
        "events": {
            "package_readiness_checked": CAPABILITY_LIFECYCLE_EVENT_CONSUMERS["package_readiness_checked"],
        },
        "validation_commands": [
            "./bin/ask skills package <handle-or-path> --json --robot",
            _skills_validation_command("events", "package_readiness_checked"),
        ],
    }


def _skill_doctor_operation_context() -> dict[str, Any]:
    """Return profile and event routing context for capability doctor checks."""
    return {
        "primary_profile": "authoring",
        "review_profile": "package-review",
        "next_profiles": ["package-review", "eval"],
        "profiles": {
            profile_name: {
                "intent": SKILL_OPERATION_PROFILES[profile_name]["intent"],
                "write_policy": SKILL_OPERATION_PROFILES[profile_name]["write_policy"],
                "required_evidence": SKILL_OPERATION_PROFILES[profile_name]["required_evidence"],
            }
            for profile_name in ("authoring", "package-review", "eval")
        },
        "events": {
            "skill_doctor_completed": CAPABILITY_LIFECYCLE_EVENT_CONSUMERS["skill_doctor_completed"],
            "eval_blocked": CAPABILITY_LIFECYCLE_EVENT_CONSUMERS["eval_blocked"],
            "eval_completed": CAPABILITY_LIFECYCLE_EVENT_CONSUMERS["eval_completed"],
        },
        "follow_up_commands": [
            "./bin/ask skills package <handle-or-path> --json --robot",
            "./bin/ask skills prove <handle> --json --robot",
            _skills_validation_command("events"),
        ],
        "validation_commands": [
            "./bin/ask skills doctor <handle-or-path> --json --robot",
            "./bin/ask skills audit <handle-or-path> --level strict --json --robot",
            _skills_validation_command("events", "skill_doctor_completed"),
        ],
    }


def _resolve_doctor_target(repo_root: Path, target: str) -> tuple[dict[str, Any], str | None]:
    """Resolve a doctor target as either an SDK skill handle or a repo-owned path."""
    query = target.strip()
    looks_like_path = "/" in query or query.endswith(".md") or query.startswith(".")
    if looks_like_path:
        target_path, target_path_value = _normalize_skill_target_path(query)
        requested_path_value = Path(query).as_posix()
        resolved_path, path_error = _validate_repo_relative_skill_path(repo_root, query)
        if path_error:
            return {
                "target_kind": "invalid_path",
                "path_error": [error.__dict__ for error in path_error.errors],
            }, None
        assert resolved_path is not None
        source = resolved_path if resolved_path.name == "SKILL.md" else resolved_path / "SKILL.md"
        source_rel = _repo_relative_path(repo_root, source)
        return {
            "target_kind": "canonical_source_path",
            "handle": None,
            "source_path": source_rel,
            "target_path": target_path_value,
            "requested_path": requested_path_value,
            "source_exists": source.is_file(),
            "resolution": None,
        }, Path(source_rel).parent.as_posix() if source_rel else target_path.as_posix()

    resolution = resolve_skill_handle(query, repo_root_path=repo_root)
    audit_target = _skill_audit_target(repo_root, resolution) if resolution.get("status") == "ok" else None
    return {
        "target_kind": "command_handle",
        "handle": resolution.get("handle", query.lstrip("$")),
        "source_path": resolution.get("source_path"),
        "source_exists": bool(audit_target and (repo_root / audit_target / "SKILL.md").is_file()),
        "resolution": resolution,
    }, audit_target


def skills_package(
    repo_root: Path,
    target: str,
    strict: bool = False,
    checkout_test: bool = False,
) -> CallResult:
    """Report version and role-aware package readiness for one skill."""
    result = CallResult()
    result.metadata["command"] = "skills package"
    query = target.strip()
    target_info, audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path")
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path

    blockers: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if not source_path or not source_path.is_file():
        blockers.append(
            _doctor_blocker(
                "blocked_missing_source",
                f"Canonical source is missing for '{query}'.",
            )
        )
        package_contract = {
            "readiness_level": "blocked_missing_source",
            "required_fields": {"present": [], "missing": list(PACKAGE_CONTRACT_FIELDS)},
            "values": {},
            "role_compatibility": {"declared": False, "roles": []},
            "runtime_contract": {"declared": False, "needs": []},
            "install_gate": {
                "install_ready": False,
                "required_checks": list(PACKAGE_CONTRACT_FIELDS),
                "blocked_reasons": list(PACKAGE_CONTRACT_FIELDS),
                "checkout_test": {
                    "required": True,
                    "status": "not_run",
                    "evidence": [],
                },
            },
            "promotion_gate": {
                "status": "blocked_missing_source",
                "promotion_ready": False,
                "share_ready": False,
                "share_readiness": None,
                "checkout_test_status": "not_run",
                "blocked_reasons": list(PACKAGE_CONTRACT_FIELDS),
                "recommended_next_fields": list(PACKAGE_CONTRACT_FIELDS),
            },
            "sdk_contract": _sdk_package_contract(repo_root, None, {}),
        }
        skill_package_contract = _empty_skill_package_contract()
    else:
        try:
            frontmatter = _read_skill_frontmatter_fields(source_path)
        except OSError:
            frontmatter = {}
        skill_package_contract = _skill_package_contract(repo_root, source_path, frontmatter)
        package_contract = _skill_package_readiness(frontmatter, repo_root, source_path)
        missing_fields = package_contract["required_fields"]["missing"]
        gate_blockers = package_contract["install_gate"]["blocked_reasons"]
        if gate_blockers:
            warning_message = (
                "Package readiness metadata is incomplete."
                if missing_fields
                else "Package promotion gate is blocked."
            )
            warnings.append(
                _doctor_warning(
                    "capability_contract_incomplete",
                    warning_message,
                )
            )
            if strict:
                blocker_message = (
                    "Strict package readiness failed; missing package metadata: "
                    f"{', '.join(missing_fields)}."
                    if missing_fields
                    else (
                        "Strict package readiness failed; package gate blockers: "
                        f"{', '.join(gate_blockers)}."
                    )
                )
                blockers.append(
                    _doctor_blocker(
                        "blocked_validation",
                        blocker_message,
                    )
                )

    if checkout_test:
        package_contract["install_gate"]["checkout_test"] = _skill_package_checkout_test(
            repo_root,
            source_path,
            audit_target,
            package_contract,
        )
    _refresh_package_promotion_gate(package_contract)
    gate_summary = _skill_package_gate_summary(package_contract)
    readiness_summary = _skill_package_readiness_summary(package_contract)

    status = "blocked" if blockers else ("warning" if warnings else "pass")
    lifecycle_event = _capability_lifecycle_event(
        event_type="skill_loaded",
        query=query,
        target_kind=str(target_info.get("target_kind") or "unknown"),
        handle=target_info.get("handle"),
        source_path=source_path_value,
        audit_target=audit_target,
        status=status,
        blockers=blockers,
        warnings=warnings,
    )
    readiness_event = _capability_lifecycle_event(
        event_type="package_readiness_checked",
        query=query,
        target_kind=str(target_info.get("target_kind") or "unknown"),
        handle=target_info.get("handle"),
        source_path=source_path_value,
        audit_target=audit_target,
        status=status,
        blockers=blockers,
        warnings=warnings,
        details={"gate_summary": gate_summary},
    )
    lifecycle_events = [lifecycle_event, readiness_event]
    payload = {
        "schema_version": SKILL_PACKAGE_READINESS_SCHEMA_VERSION,
        "query": query,
        "target_kind": target_info.get("target_kind"),
        "handle": target_info.get("handle"),
        "canonical_source_path": source_path_value,
        "audit_target": audit_target,
        "target_summary": _skill_target_summary(
            query=query,
            target_kind=target_info.get("target_kind"),
            handle=target_info.get("handle"),
            source_path=source_path_value,
            audit_target=audit_target,
        ),
        "status": status,
        "strict": strict,
        "package_schema": {
            "schema_version": SKILL_PACKAGE_SCHEMA_VERSION,
            "path": SKILL_PACKAGE_SCHEMA_PATH,
        },
        "package_readiness_schema": {
            "schema_version": SKILL_PACKAGE_READINESS_SCHEMA_VERSION,
            "path": SKILL_PACKAGE_READINESS_SCHEMA_PATH,
        },
        "compatibility_snapshot": _skill_package_compatibility_snapshot(),
        "skill_package_contract": skill_package_contract,
        "package_contract": package_contract,
        "gate_summary": gate_summary,
        "readiness_summary": readiness_summary,
        "contract_schemas": {
            "package": SKILL_PACKAGE_READINESS_SCHEMA_VERSION,
            "skill_package": SKILL_PACKAGE_SCHEMA_VERSION,
            "skillflow": SKILLFLOW_SCHEMA_VERSION,
            "optimization": SKILL_OPTIMIZATION_CONTRACT_SCHEMA_VERSION,
            "events": "skill-events.v1",
            "lifecycle_event": "capability-lifecycle-event.v1",
            "profiles": "skill-operation-profiles.v1",
            "doctor": "skill-doctor.v1",
            "memory": "skill-memory-provider.v1",
        },
        "workflow_schema": {
            "schema_version": SKILLFLOW_SCHEMA_VERSION,
            "path": SKILLFLOW_SCHEMA_PATH,
        },
        "optimization_schema": {
            "schema_version": SKILL_OPTIMIZATION_CONTRACT_SCHEMA_VERSION,
            "path": SKILL_OPTIMIZATION_CONTRACT_SCHEMA_PATH,
        },
        "operation_context": _skill_package_operation_context(),
        "blockers": blockers,
        "warnings": warnings,
        "lifecycle_event": readiness_event,
        "lifecycle_events": lifecycle_events,
        "agent_summary": (
            f"{query} is blocked: {blockers[0]['message']}"
            if blockers
            else (
                f"{query} has package gate blockers: {', '.join(package_contract['install_gate']['blocked_reasons'])}."
                if warnings
                else (
                    f"{query} is package/share ready; run --checkout-test before promotion."
                    if package_contract["promotion_gate"]["status"] == "ready_pending_checkout"
                    else f"{query} is package/share ready with checkout evidence."
                )
            )
        ),
        "next_command": (
            _skills_validation_command("doctor", query)
            if blockers
            else _skills_validation_command("doctor", query, "--strict")
        ),
    }
    result.data["skill_package"] = payload
    if blockers or (strict and warnings):
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion=payload["next_command"],
            )
        )
    return result


def skills_package_verify(
    repo_root: Path,
    target: str,
    expected_sha256: str | None = None,
    trusted_provenance: str | None = None,
    rollback_journal: str | None = None,
) -> CallResult:
    """Verify a package candidate without installing, extracting, or mutating runtime roots."""
    result = CallResult()
    result.metadata["command"] = "skills package verify"
    query = target.strip()
    validation_args = ["verify", query]
    if expected_sha256:
        validation_args.extend(["--expected-sha256", expected_sha256])
    if trusted_provenance:
        validation_args.extend(["--trusted-provenance", trusted_provenance])
    if rollback_journal:
        validation_args.extend(["--rollback-journal", rollback_journal])
    validation_command = _skills_validation_command("package", *validation_args)
    target_path = Path(query)
    candidate_path = target_path if target_path.is_absolute() else repo_root / target_path

    trusted_sources = {
        source.strip()
        for source in (trusted_provenance or "").split(",")
        if source.strip()
    } or None
    is_archive_target = candidate_path.name != "SKILL.md" and (
        candidate_path.is_file() or candidate_path.suffix.lower() == ".zip"
    )

    if is_archive_target:
        journal_path = Path(rollback_journal) if rollback_journal else None
        if journal_path and not journal_path.is_absolute():
            journal_path = repo_root / journal_path
        verification = _verify_archive_package(
            candidate_path,
            expected_sha256=expected_sha256,
            trusted_sources=trusted_sources,
            rollback_journal_path=journal_path,
            repo_root=repo_root,
        )
    else:
        source_path: Path | None = None
        if candidate_path.is_dir():
            source_path = candidate_path / "SKILL.md"
        elif candidate_path.is_file() and candidate_path.name == "SKILL.md":
            source_path = candidate_path
        else:
            target_info, _audit_target = _resolve_doctor_target(repo_root, query)
            source_path_value = target_info.get("source_path")
            if source_path_value:
                source_path = Path(str(source_path_value))
                if not source_path.is_absolute():
                    source_path = repo_root / source_path
        if source_path and source_path.is_file():
            verification = _verify_skill_directory(repo_root, source_path, query, trusted_sources=trusted_sources)
        else:
            missing_path = (source_path or candidate_path).as_posix()
            verification = {
                "schema_version": PACKAGE_VERIFY_SCHEMA_VERSION,
                "target_kind": "missing",
                "target_path": missing_path,
                "archive_identity": None,
                "provenance_identity": {"trusted": False, "values": []},
                "rule_results": [
                    {
                        "rule_id": "blocked_missing_artifact",
                        "status": "blocked",
                        "message": "Package verification target did not resolve to a skill source or archive.",
                        "path": missing_path,
                    }
                ],
                "mutation_status": "not_mutated",
                "rollback_hint": "No rollback is required because verification did not install, extract, or mutate runtime roots.",
                "status": "blocked",
            }
    verification = _normalize_package_verification(
        query=query,
        validation_command=validation_command,
        verification=verification,
    )

    result.data["skill_package_verification"] = verification
    if verification["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=verification["agent_summary"],
                fix_suggestion=verification["next_command"],
            )
        )
    return result


def skills_conformance_run(
    repo_root: Path,
    *,
    suite: str,
    evidence_dir: str,
) -> CallResult:
    """Run deterministic Codex parity conformance checks and write replayable evidence."""
    result = CallResult()
    result.metadata["command"] = "skills conformance run"
    validation_command = _skills_validation_command(
        "conformance",
        "run",
        "--suite",
        suite,
        "--evidence-dir",
        evidence_dir,
    )
    payload = _run_skills_conformance(repo_root, suite=suite, evidence_dir=evidence_dir)
    payload["validation_commands"] = [validation_command]
    payload["agent_summary"] = (
        f"Conformance suite {suite} blocked: {payload['blockers'][0]['message']}"
        if payload.get("blockers")
        else f"Conformance suite {suite} passed with {payload.get('case_count', 0)} fixture cases."
    )
    payload["next_command"] = validation_command
    result.data["skills_conformance"] = payload
    if payload.get("blockers"):
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion=validation_command,
            )
        )
    return result


def skills_doctor(
    repo_root: Path,
    target: str,
    strict: bool = False,
    codex_parity: bool = False,
) -> CallResult:
    """Run a compact per-capability diagnostic for a skill handle or source path."""
    result = CallResult()
    result.metadata["command"] = "skills doctor"
    query = target.strip()
    target_info, audit_target = _resolve_doctor_target(repo_root, query)
    target_kind = str(target_info.get("target_kind") or "unknown")
    normalized_handle = target_info.get("handle")
    source_path_value = target_info.get("source_path")
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path

    checks: dict[str, Any] = {}
    blockers: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    resolution = target_info.get("resolution")
    if target_kind == "skill_handle":
        resolver_pass = isinstance(resolution, dict) and resolution.get("status") == "ok"
        checks["resolver"] = _doctor_check(
            _status_from_bool(resolver_pass),
            check_name="resolver",
            handle=normalized_handle,
            error_code=(resolution or {}).get("error_code") if isinstance(resolution, dict) else None,
            operator_action=(resolution or {}).get("operator_action") if isinstance(resolution, dict) else None,
        )
        if not resolver_pass:
            blockers.append(
                _doctor_blocker(
                    "blocked_resolution",
                    f"Could not resolve skill handle '{normalized_handle}'.",
                )
            )

        proof_runtime_target = "codex" if codex_parity else "any"
        proof_result = skills_proof(repo_root, str(normalized_handle), runtime_target=proof_runtime_target)
        proof = proof_result.data.get("proof", {})
        runtime_failure = (
            proof.get("runtime_failure")
            if isinstance(proof, dict) and isinstance(proof.get("runtime_failure"), dict)
            else proof_result.data.get("runtime_failure")
        )
        proof_command_args = [str(normalized_handle)]
        if codex_parity:
            proof_command_args.extend(["--runtime-target", "codex"])
        checks["runtime_reachability"] = _doctor_check(
            proof.get("status", "fail") if isinstance(proof, dict) else "fail",
            check_name="runtime_reachability",
            command=_skills_validation_command("proof", *proof_command_args),
            codex_parity=codex_parity,
            runtime_target=proof_runtime_target,
            gate_policy=proof.get("gate_policy", {}) if isinstance(proof, dict) else {},
            gates=proof.get("gates", {}) if isinstance(proof, dict) else {},
            runtime_failure=runtime_failure if isinstance(runtime_failure, dict) else None,
            error_code=runtime_failure.get("error_code") if isinstance(runtime_failure, dict) else None,
            failed_check_id=runtime_failure.get("failed_check_id") if isinstance(runtime_failure, dict) else None,
            path=runtime_failure.get("path") if isinstance(runtime_failure, dict) else None,
            recovery_guidance=runtime_failure.get("recovery_guidance") if isinstance(runtime_failure, dict) else None,
        )
        if proof_result.status != "success":
            blockers.append(
                _doctor_blocker(
                    "blocked_runtime",
                    f"Runtime reachability proof failed for '{normalized_handle}'.",
                )
            )
    else:
        checks["resolver"] = _doctor_check(
            "skipped",
            check_name="resolver",
            reason="Path targets are audited as canonical source; runtime proof requires a handle.",
        )
        if codex_parity:
            checks["runtime_reachability"] = _doctor_check(
                "fail",
                check_name="runtime_reachability",
                codex_parity=True,
                runtime_target="codex",
                reason="Codex parity requires an SDK skill handle so Codex runtime proof can run.",
            )
            blockers.append(
                _doctor_blocker(
                    "blocked_runtime",
                    "Codex parity requires an SDK skill handle.",
                )
            )

    source_exists = bool(target_info.get("source_exists"))
    checks["canonical_source"] = _doctor_check(
        _status_from_bool(source_exists),
        check_name="canonical_source",
        source_path=source_path_value,
    )
    if not source_exists:
        blockers.append(
            _doctor_blocker(
                "blocked_missing_source",
                f"Canonical source is missing for '{query}'.",
            )
        )

    projection_path_value = None
    target_path_value = target_info.get("requested_path") or target_info.get("target_path")
    ownership_source_path = target_path_value if target_kind != "skill_handle" else source_path_value
    source_ownership = _skill_root_ownership_for_path(
        str(ownership_source_path) if ownership_source_path else None,
        repo_root=repo_root,
    )
    target_ownership = (
        _skill_root_ownership_for_path(str(target_path_value), repo_root=repo_root)
        if target_kind != "skill_handle" and target_path_value
        else source_ownership
    )
    if (
        target_kind != "skill_handle"
        and not projection_path_value
        and target_ownership.get("classification")
        in {
            "generated_runtime_projection",
            "client_runtime_config",
        }
    ):
        projection_path_value = str(target_path_value)
    projection_ownership = _skill_root_ownership_for_path(
        str(projection_path_value) if projection_path_value else None,
        repo_root=repo_root,
    )
    ownership_status = "pass"
    if target_ownership.get("classification") in {
        "generated_runtime_projection",
        "client_runtime_config",
    }:
        ownership_status = "fail"
        blockers.append(
            _doctor_blocker(
                "blocked_validation",
                (
                    f"Doctor target '{query}' resolves to {target_ownership['classification']}; "
                    "edit canonical source or declare the root as canonical_project_source in an owner-repo "
                    "skills-sdk.json manifest."
                ),
            )
        )
    elif not source_exists:
        ownership_status = "skipped"
    checks["projection_ownership"] = _doctor_check(
        ownership_status,
        check_name="projection_ownership",
        source=source_ownership,
        target=target_ownership,
        target_path=target_path_value,
        projection=projection_ownership,
        projection_path=projection_path_value,
        projection_editable=bool(projection_ownership.get("editable_source")),
        owner_manifest_schema=PROJECT_SKILLS_SDK_SCHEMA,
    )

    audit_level = "strict" if strict else "compat"
    if audit_target and source_exists:
        audit_result = audit_skill(repo_root, audit_target, level=audit_level)
        diagnostics = audit_result.data.get("diagnostics", {})
        checks["structural_audit"] = _doctor_check(
            "pass" if audit_result.status == "success" else "fail",
            check_name="structural_audit",
            level=audit_level,
            command=_skills_validation_command("audit", audit_target, "--level", audit_level),
            diagnostics_exit_code=diagnostics.get("exit_code"),
        )
        if audit_result.status != "success":
            blockers.append(
                _doctor_blocker(
                    "blocked_validation",
                    f"{audit_level} skill audit failed for '{audit_target}'.",
                )
            )
    else:
        checks["structural_audit"] = _doctor_check(
            "skipped",
            check_name="structural_audit",
            level=audit_level,
            reason="No canonical source target available.",
        )

    frontmatter: dict[str, Any] = {}
    source_body = ""
    if source_path and source_path.is_file():
        try:
            frontmatter = _read_skill_frontmatter_fields(source_path)
            source_body = source_path.read_text(encoding="utf-8")
        except OSError:
            frontmatter = {}
            source_body = ""
    risk_classification = _build_risk_classification(
        source_path if source_path and source_path.exists() else None,
        frontmatter,
        source_body,
    )
    checks["risk_classification"] = _doctor_check(
        "pass",
        check_name="risk_classification",
        classification=risk_classification,
        sensor_ids=risk_classification["sensor_ids"],
        risk_tier=risk_classification["risk_tier"],
        source_kind=risk_classification["source_kind"],
        blocking_behavior=risk_classification["blocking_behavior"],
        receipt_required=risk_classification["receipt_required"],
    )
    metadata_status = _capability_metadata_status(frontmatter)
    metadata_status.setdefault("sdk_layer", _doctor_sdk_layer_for("check", "capability_metadata"))
    checks["capability_metadata"] = metadata_status
    if metadata_status["status"] == "warning":
        warnings.append(
            _doctor_warning(
                "metadata_incomplete",
                "Recommended frontmatter fields are incomplete.",
            )
        )
    package_readiness = metadata_status.get("package_readiness", {})
    package_status = "pass"
    if isinstance(package_readiness, dict) and package_readiness.get("required_fields", {}).get("missing"):
        package_status = "warning"
        warnings.append(
            _doctor_warning(
                "capability_contract_incomplete",
                "Package/share readiness metadata is incomplete.",
            )
        )
    checks["package_readiness"] = _doctor_check(
        package_status,
        check_name="package_readiness",
        package_readiness=package_readiness,
        required_fields=package_readiness.get("required_fields", {}) if isinstance(package_readiness, dict) else {},
        install_gate=package_readiness.get("install_gate", {}) if isinstance(package_readiness, dict) else {},
        promotion_gate=package_readiness.get("promotion_gate", {}) if isinstance(package_readiness, dict) else {},
    )

    workout_handle = str(normalized_handle or (Path(audit_target).name if audit_target else "")).strip()
    workouts = _skill_workout_candidates(repo_root, workout_handle) if workout_handle else []
    checks["outcome_proof"] = _doctor_check(
        "available_not_run" if workouts else "missing",
        check_name="outcome_proof",
        workout_candidates=workouts,
        evidence_class="outcome_proof",
    )
    if not workouts:
        warnings.append(
            _doctor_warning(
                "outcome_proof_missing",
                "No matching workout was found for this capability.",
            )
        )
    doctor_status = "blocked" if blockers else ("warning" if warnings else "pass")
    next_command_decision = _skill_doctor_next_command_decision(
        blockers=blockers,
        warnings=warnings,
        checks=checks,
        normalized_handle=normalized_handle,
        query=query,
        audit_target=audit_target,
        strict=strict,
    )
    next_command = str(next_command_decision["command"])

    handle_label = str(normalized_handle) if normalized_handle else query
    lifecycle_event = _capability_lifecycle_event(
        event_type="skill_doctor_completed",
        query=query,
        target_kind=target_kind,
        handle=normalized_handle,
        source_path=source_path_value,
        audit_target=audit_target,
        status=doctor_status,
        blockers=blockers,
        warnings=warnings,
    )
    result.data["skill_doctor"] = {
        "schema_version": "skill-doctor.v1",
        "query": query,
        "target_kind": target_kind,
        "handle": normalized_handle,
        "canonical_source_path": source_path_value,
        "audit_target": audit_target,
        "target_summary": _skill_target_summary(
            query=query,
            target_kind=target_kind,
            handle=normalized_handle,
            source_path=source_path_value,
            audit_target=audit_target,
        ),
        "status": doctor_status,
        "blockers": blockers,
        "warnings": warnings,
        "readiness_taxonomy": {
            "blockers": DOCTOR_BLOCKER_TAXONOMY,
            "warnings": DOCTOR_WARNING_TAXONOMY,
        },
        "sdk_layers": list(DOCTOR_SDK_LAYERS),
        "contract_schemas": _doctor_contract_schema_refs(),
        "contract_schema_versions": _doctor_contract_schema_versions(),
        "operation_context": _skill_doctor_operation_context(),
        "lifecycle_event": lifecycle_event,
        "lifecycle_event_types": CAPABILITY_LIFECYCLE_EVENT_TYPES,
        "checks": checks,
        "check_summary": _skill_doctor_check_summary(checks),
        "agent_summary": (
            f"{handle_label} is blocked: {blockers[0]['message']}"
            if blockers
            else (
                f"{handle_label} is usable with {len(warnings)} readiness warning(s)."
                if warnings
                else f"{handle_label} passed capability doctor checks."
            )
        ),
        "next_command": next_command,
        "next_command_decision": next_command_decision,
    }
    if blockers:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=result.data["skill_doctor"]["agent_summary"],
                fix_suggestion=next_command,
            )
        )
    return result


def skills_sdk_check(
    repo_root: Path,
    target: str,
    strict: bool = False,
    codex_parity: bool = False,
) -> CallResult:
    """Run the Skills SDK check facade through the canonical skills doctor."""
    result = skills_doctor(
        repo_root,
        target=target,
        strict=strict,
        codex_parity=codex_parity,
    )
    doctor = result.data.get("skill_doctor", {})
    doctor_status = doctor.get("status") if isinstance(doctor, dict) else None
    blockers = doctor.get("blockers", []) if isinstance(doctor, dict) else []
    first_blocker = blockers[0] if blockers and isinstance(blockers[0], dict) else {}
    status = {
        "pass": "pass",
        "warning": "warning",
        "blocked": "blocked",
    }.get(str(doctor_status or ""), "degraded")
    failure_class = "none"
    if status in {"blocked", "degraded"}:
        failure_class = "validation_failed"

    doctor_command_args = [target]
    if strict:
        doctor_command_args.append("--strict")
    if codex_parity:
        doctor_command_args.append("--codex-parity")
    command = _skills_validation_command("doctor", *doctor_command_args)
    facade_command = "skills-sdk check"
    result.metadata["command"] = "sdk check"
    receipt = {
        "schema_version": "skills-sdk.check-receipt.v1",
        "schema_uri": "https://jscraik.local/agent-skills/schemas/skills-sdk/check-receipt.v1.schema.json",
        "command": facade_command,
        "command_version": "skills-sdk.v1",
        "status": status,
        "failure_class": failure_class,
        "exit_code": 0 if result.status == "success" else 2,
        "work_mode": "computational",
        "proof": {
            "type": "command_output",
            "evidence_kind": "receipt",
            "evidence_ref": command,
        },
        "sensor": {
            "id": "skills-sdk.check.facade",
            "placement": "preflight",
            "required": True,
        },
        "actor": {"role": "agent"},
        "approval_decision": "not_required",
        "redaction": "not_applicable",
        "acceptance_trace": ["FR-008", "FR-009", "SA-004", "SA-005", "VP-002"],
    }
    payload = {
        "schema_version": "skills-sdk-check.v1",
        "query": target,
        "status": status,
        "failure_class": failure_class,
        "doctor_status": doctor_status,
        "canonical_command": command,
        "facade_command": facade_command,
        "receipt": receipt,
        "skill_doctor": doctor,
        "agent_summary": (
            f"skills-sdk check blocked for {target}: {first_blocker.get('message')}"
            if status == "blocked"
            else (
                f"skills-sdk check completed for {target} with warnings."
                if status == "warning"
                else f"skills-sdk check passed for {target}."
            )
        ),
        "validation_commands": [
            _ask_validation_command("sdk", "check", target),
            command,
        ],
        "next_command": doctor.get("next_command") if isinstance(doctor, dict) else command,
    }
    result.data["skills_sdk_check"] = payload
    return result


def skills_sdk_install_preview(
    repo_root: Path,
    target: str,
    scope: str = "project",
) -> CallResult:
    """Build a read-only Skills SDK install preview for one skill target."""
    result = CallResult()
    result.metadata["command"] = "sdk install --preview"
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path

    preview = _build_install_preview(
        repo_root,
        query=query,
        scope=scope,
        source_path=source_path,
        target_info=target_info,
    )
    status = "blocked" if preview["trust_state"] == "blocked" else "preview"
    payload = {
        "schema_version": "skills-sdk-install-preview.v1",
        "query": query,
        "status": status,
        "scope": scope,
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk install --preview",
        "preview": preview,
        "receipt": {
            "command": "skills-sdk install --preview",
            "status": status,
            "mutation_performed": False,
            "receipt_ref": preview["receipt_ref"],
        },
        "validation_commands": [
            _ask_validation_command("sdk", "install", query, "--preview", "--scope", scope),
        ],
        "agent_summary": (
            f"skills-sdk install preview is blocked for {query}: canonical source is missing."
            if status == "blocked"
            else f"skills-sdk install preview planned {len(preview['target_paths'])} path(s) for {query} without writes."
        ),
    }
    result.data["skills_sdk_install_preview"] = payload
    if status == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion=_ask_validation_command("sdk", "check", query),
            )
        )
    return result


def skills_sdk_ir_build(
    repo_root: Path,
    target: str,
) -> CallResult:
    """Build a read-only SkillIR.v0 payload for one canonical skill target."""
    result = CallResult()
    result.metadata["command"] = "sdk ir build"
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path

    if not source_path or not source_path.is_file():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK IR build is missing a canonical SKILL.md source for '{query}'.",
                fix_suggestion=_ask_validation_command("sdk", "check", query),
            )
        )
        result.data["skills_sdk_ir"] = {
            "schema_version": "skills-sdk-ir-build.v0",
            "query": query,
            "status": "blocked",
            "canonical_source_path": source_path_value,
            "mutation_performed": False,
            "validation_commands": [_ask_validation_command("sdk", "ir", "build", query)],
            "agent_summary": f"skills-sdk ir build is blocked for {query}: canonical source is missing.",
        }
        return result

    ir = _build_skill_ir(repo_root, source_path=source_path, query=query)
    payload = {
        "schema_version": "skills-sdk-ir-build.v0",
        "query": query,
        "status": "built",
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk ir build",
        "ir": ir,
        "receipt": {
            "command": "skills-sdk ir build",
            "status": "built",
            "mutation_performed": False,
            "schema_version": ir["schema_version"],
            "source_path": ir["source"]["skill_md"],
        },
        "validation_commands": [
            _ask_validation_command("sdk", "ir", "build", query),
        ],
        "agent_summary": f"skills-sdk ir build produced SkillIR.v0 for {query} without writes.",
    }
    result.data["skills_sdk_ir"] = payload
    return result


def skills_sdk_docs_verify(
    repo_root: Path,
    artifact: str | None = None,
) -> CallResult:
    """Verify static SDK docs projections against executable capability truth."""
    result = CallResult()
    result.metadata["command"] = "sdk docs verify"
    artifact_path = Path(artifact) if artifact else None
    payload = _verify_capability_docs_projection(repo_root, artifact_path=artifact_path)
    payload["validation_commands"] = [
        _ask_validation_command("sdk", "docs", "verify")
        if not artifact
        else _ask_validation_command("sdk", "docs", "verify", "--artifact", artifact)
    ]
    result.data["skills_sdk_docs_verify"] = payload
    if payload["status"] != "pass":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion="Regenerate or patch the capability projection from Infrastructure/config/skills-sdk/capability-matrix.v1.json.",
            )
        )
    return result


def skills_sdk_package_build(
    repo_root: Path,
    target: str,
) -> CallResult:
    """Build a non-mutating package identity receipt for one skill target."""
    result = CallResult()
    result.metadata["command"] = "sdk package build"
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path

    if not source_path or not source_path.is_file():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK package build is missing a canonical SKILL.md source for '{query}'.",
                fix_suggestion=_ask_validation_command("sdk", "ir", "build", query),
            )
        )
        result.data["skills_sdk_package_build"] = {
            "schema_version": "skills-sdk-package-build.v0",
            "query": query,
            "status": "blocked",
            "canonical_source_path": source_path_value,
            "mutation_performed": False,
            "validation_commands": [_ask_validation_command("sdk", "package", "build", query)],
            "agent_summary": f"skills-sdk package build is blocked for {query}: canonical source is missing.",
        }
        return result

    receipt = _build_package_digest_receipt(repo_root, source_path=source_path, query=query)
    payload = {
        "schema_version": "skills-sdk-package-build.v0",
        "query": query,
        "status": receipt["status"],
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk package build",
        "package_id": receipt["package_id"],
        "version": receipt["version"],
        "source_digest": receipt["source_digest"],
        "manifest_digest": receipt["manifest_digest"],
        "package_digest": receipt["package_digest"],
        "included_files": receipt["included_files"],
        "excluded_files": receipt["excluded_files"],
        "receipt": receipt,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command("sdk", "package", "build", query),
        ],
        "agent_summary": f"skills-sdk package build produced digest identity for {query} without writes.",
    }
    result.data["skills_sdk_package_build"] = payload
    return result


def skills_sdk_package_harden(
    repo_root: Path,
    target: str,
) -> CallResult:
    """Build a read-only package hardening receipt for one skill target."""
    result = CallResult()
    result.metadata["command"] = "sdk package harden"
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path

    if not source_path or not source_path.is_file():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK package harden is missing a canonical SKILL.md source for '{query}'.",
                fix_suggestion=_ask_validation_command("sdk", "package", "harden", query),
            )
        )
        result.data["skills_sdk_package_harden"] = {
            "schema_version": "skills-sdk-package-harden.v0",
            "query": query,
            "status": "blocked",
            "canonical_source_path": source_path_value,
            "receipt": None,
            "mutation_performed": False,
            "validation_commands": [_ask_validation_command("sdk", "package", "harden", query)],
            "agent_summary": f"skills-sdk package harden is blocked for {query}: canonical source is missing.",
        }
        return result

    package_receipt = _build_package_digest_receipt(repo_root, source_path=source_path, query=query)
    hardening_receipt = _build_package_hardening_receipt(package_receipt)
    payload = {
        "schema_version": "skills-sdk-package-harden.v0",
        "query": query,
        "status": hardening_receipt["status"],
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk package harden",
        "package_id": hardening_receipt["package_id"],
        "version": hardening_receipt["version"],
        "package_digest": hardening_receipt["package_digest"],
        "receipt": hardening_receipt,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command("sdk", "package", "harden", query),
        ],
        "agent_summary": f"skills-sdk package harden {hardening_receipt['status']} for {query} without writes.",
    }
    result.data["skills_sdk_package_harden"] = payload
    if hardening_receipt["status"] != "pass":
        result.status = "error"
        message = "Skills SDK package hardening blocked package emission."
        if hardening_receipt["blockers"]:
            message = hardening_receipt["blockers"][0]["message"]
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=message,
                fix_suggestion="Remove forbidden package paths or restore canonical SkillIR/package provenance before hardening.",
            )
        )
    return result


def skills_sdk_package_signing_intent(
    repo_root: Path,
    target: str,
    policy: str,
) -> CallResult:
    """Build a non-mutating signing intent receipt for one skill target."""
    result = CallResult()
    result.metadata["command"] = "sdk package signing-intent"
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path
    policy_path = Path(policy)
    if not policy_path.is_absolute():
        policy_path = repo_root / policy_path

    if not source_path or not source_path.is_file():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK package signing intent is missing a canonical SKILL.md source for '{query}'.",
                fix_suggestion=_ask_validation_command("sdk", "package", "build", query),
            )
        )
        result.data["skills_sdk_package_signing_intent"] = {
            "schema_version": "skills-sdk-package-signing-intent.v0",
            "query": query,
            "status": "blocked",
            "canonical_source_path": source_path_value,
            "receipt": None,
            "mutation_performed": False,
            "signing_performed": False,
            "key_material_accessed": False,
            "artifact_emitted": False,
            "validation_commands": [
                _ask_validation_command("sdk", "package", "signing-intent", query, "--policy", policy)
            ],
            "agent_summary": f"skills-sdk package signing intent is blocked for {query}: canonical source is missing.",
        }
        return result

    from ask.skills_sdk.signing_intent import (  # noqa: PLC0415
        SigningIntentError,
        build_signing_intent_receipt,
    )

    package_receipt = _build_package_digest_receipt(repo_root, source_path=source_path, query=query)
    hardening_receipt = _build_package_hardening_receipt(package_receipt)
    try:
        signing_receipt = build_signing_intent_receipt(
            repo_root=repo_root,
            policy_path=policy_path,
            package_receipt=package_receipt,
            hardening_receipt=hardening_receipt,
        )
    except SigningIntentError as exc:
        signing_receipt = exc.receipt

    payload = {
        "schema_version": "skills-sdk-package-signing-intent.v0",
        "query": query,
        "status": signing_receipt["status"],
        "canonical_source_path": source_path_value,
        "policy_path": policy,
        "facade_command": "skills-sdk package signing-intent",
        "package_id": signing_receipt["package_id"],
        "version": signing_receipt["version"],
        "package_digest": signing_receipt["package_digest"],
        "receipt": signing_receipt,
        "mutation_performed": False,
        "signing_performed": False,
        "key_material_accessed": False,
        "artifact_emitted": False,
        "validation_commands": [
            _ask_validation_command("sdk", "package", "signing-intent", query, "--policy", policy),
        ],
        "agent_summary": signing_receipt["agent_summary"],
    }
    result.data["skills_sdk_package_signing_intent"] = payload
    if signing_receipt["status"] != "ready":
        result.status = "error"
        message = signing_receipt["blockers"][0]["message"] if signing_receipt["blockers"] else payload["agent_summary"]
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=message,
                fix_suggestion=(
                    "Use a v0 signing policy that pins the package id and digest, requires hardening, "
                    "keeps key material external, and does not require archive emission."
                ),
            )
        )
    return result


def skills_sdk_sandbox_validate(
    repo_root: Path,
    profile: str,
) -> CallResult:
    """Validate a sandbox boundary profile without invoking an execution provider."""
    result = CallResult()
    result.metadata["command"] = "sdk sandbox validate"
    try:
        receipt = _build_sandbox_profile_receipt(repo_root, profile_path=profile)
    except _SandboxProfileError as exc:
        receipt = exc.receipt
    payload = {
        "schema_version": "skills-sdk-sandbox-validate.v0",
        "status": receipt["status"],
        "profile": profile,
        "facade_command": "skills-sdk sandbox validate",
        "receipt": receipt,
        "mutation_performed": False,
        "execution_performed": False,
        "validation_commands": [
            _ask_validation_command("sdk", "sandbox", "validate", "--profile", profile),
        ],
        "agent_summary": (
            f"skills-sdk sandbox validate passed for {receipt['profile_path']} without executing a sandbox."
            if receipt["status"] == "pass"
            else f"skills-sdk sandbox validate blocked {receipt['profile_path']} with {len(receipt['blockers'])} blocker(s)."
        ),
    }
    result.data["skills_sdk_sandbox_validate"] = payload
    if receipt["status"] != "pass":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion="Use a deny-by-default profile with no persistent writes, no network egress, no ambient environment, and no selected adapter.",
            )
        )
    return result


def skills_sdk_trust_decide(
    repo_root: Path,
    target: str,
    decision: str,
    reason: str,
    owner: str,
    *,
    preview: bool,
    apply: bool,
    ledger: str | None = None,
    expires_at: str | None = None,
    revoked_package_digest: str | None = None,
) -> CallResult:
    """Preview or append a local trust ledger decision for one skill package."""
    result = CallResult()
    result.metadata["command"] = "sdk trust decide"
    preview_mode = preview and not apply
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path

    if not source_path or not source_path.is_file():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK trust decision is missing a canonical SKILL.md source for '{query}'.",
                fix_suggestion=_ask_validation_command("sdk", "package", "build", query),
            )
        )
        result.data["skills_sdk_trust_decide"] = {
            "schema_version": "skills-sdk-trust-decide.v0",
            "query": query,
            "status": "blocked",
            "canonical_source_path": source_path_value,
            "receipt": None,
            "mutation_performed": False,
            "trust_store_mutated": False,
            "validation_commands": [
                _ask_validation_command(
                    "sdk",
                    "trust",
                    "decide",
                    query,
                    "--decision",
                    decision,
                    "--reason",
                    reason,
                    "--owner",
                    owner,
                    "--preview",
                )
            ],
            "agent_summary": f"skills-sdk trust decide is blocked for {query}: canonical source is missing.",
        }
        return result

    from ask.skills_sdk.trust_ledger import (  # noqa: PLC0415
        TrustLedgerError,
        build_trust_decision_receipt,
    )

    package_receipt = _build_package_digest_receipt(repo_root, source_path=source_path, query=query)
    try:
        trust_receipt = build_trust_decision_receipt(
            repo_root,
            package_receipt=package_receipt,
            decision=decision,
            reason=reason,
            owner=owner,
            apply=apply,
            ledger_path=ledger,
            expires_at=expires_at,
            revoked_package_digest=revoked_package_digest,
        )
    except TrustLedgerError as exc:
        trust_receipt = exc.receipt

    command_args = ["sdk", "trust", "decide", query, "--decision", decision, "--reason", reason, "--owner", owner]
    if expires_at:
        command_args.extend(["--expires-at", expires_at])
    if revoked_package_digest:
        command_args.extend(["--revoked-package-digest", revoked_package_digest])
    if ledger:
        command_args.extend(["--ledger", ledger])
    command_args.append("--apply" if apply else "--preview")

    payload = {
        "schema_version": "skills-sdk-trust-decide.v0",
        "query": query,
        "status": trust_receipt["status"],
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk trust decide",
        "package_id": trust_receipt["package_id"],
        "version": trust_receipt["version"],
        "package_digest": trust_receipt["package_digest"],
        "ledger_path": trust_receipt["ledger_path"],
        "decision": trust_receipt["decision"],
        "preview": preview_mode,
        "receipt": trust_receipt,
        "mutation_performed": trust_receipt["mutation_performed"],
        "trust_store_mutated": False,
        "validation_commands": [_ask_validation_command(*command_args)],
        "agent_summary": trust_receipt["agent_summary"],
    }
    result.data["skills_sdk_trust_decide"] = payload
    if trust_receipt["status"] == "blocked":
        result.status = "error"
        message = trust_receipt["blockers"][0]["message"] if trust_receipt["blockers"] else payload["agent_summary"]
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=message,
                fix_suggestion="Provide a valid decision, reason, owner, ledger path, and revocation digest when decision is revoke.",
            )
        )
    return result


def skills_sdk_observability_feedback(
    repo_root: Path,
    target: str,
    events: str,
) -> CallResult:
    """Mine redacted runtime events into non-mutating feedback candidates."""
    result = CallResult()
    result.metadata["command"] = "sdk observability feedback"
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path
    if not source_path or not source_path.is_file():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK observability feedback is missing a canonical SKILL.md source for '{query}'.",
                fix_suggestion=_ask_validation_command("sdk", "package", "build", query),
            )
        )
        return result

    from ask.skills_sdk.observability_feedback import (  # noqa: PLC0415
        ObservabilityFeedbackError,
        build_observability_feedback_receipt,
    )

    package_receipt = _build_package_digest_receipt(repo_root, source_path=source_path, query=query)
    try:
        feedback_receipt = build_observability_feedback_receipt(
            repo_root,
            package_receipt=package_receipt,
            events_path=events,
        )
    except ObservabilityFeedbackError as exc:
        feedback_receipt = exc.receipt
    payload = {
        "schema_version": "skills-sdk-observability-feedback.v0",
        "query": query,
        "status": feedback_receipt["status"],
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk observability feedback",
        "package_id": feedback_receipt["package_id"],
        "package_digest": feedback_receipt["package_digest"],
        "receipt": feedback_receipt,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command("sdk", "observability", "feedback", "--skill", query, "--events", events, "--preview")
        ],
        "agent_summary": feedback_receipt["agent_summary"],
    }
    result.data["skills_sdk_observability_feedback"] = payload
    if feedback_receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion="Use redacted JSONL event records with digest references and no raw prompt/output fields.",
            )
        )
    return result


def skills_sdk_emitter_preview(
    repo_root: Path,
    target: str,
    projection: str,
    target_root: str,
) -> CallResult:
    """Preview a generated-output write plan without emitting files."""
    result = CallResult()
    result.metadata["command"] = "sdk emitter preview"
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path
    if not source_path or not source_path.is_file():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK emitter preview is missing a canonical SKILL.md source for '{query}'.",
                fix_suggestion=_ask_validation_command("sdk", "package", "build", query),
            )
        )
        return result

    from ask.skills_sdk.emitter_preview import (  # noqa: PLC0415
        EmitterPreviewError,
        build_emitter_preview_receipt,
    )

    package_receipt = _build_package_digest_receipt(repo_root, source_path=source_path, query=query)
    hardening_receipt = _build_package_hardening_receipt(package_receipt)
    try:
        emitter_receipt = build_emitter_preview_receipt(
            repo_root,
            package_receipt=package_receipt,
            hardening_receipt=hardening_receipt,
            projection=projection,
            target_root=target_root,
        )
    except EmitterPreviewError as exc:
        emitter_receipt = exc.receipt
    payload = {
        "schema_version": "skills-sdk-emitter-preview.v0",
        "query": query,
        "status": emitter_receipt["status"],
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk emitter preview",
        "package_id": emitter_receipt["package_id"],
        "package_digest": emitter_receipt["package_digest"],
        "projection": emitter_receipt["projection"],
        "target_root": emitter_receipt["target_root"],
        "receipt": emitter_receipt,
        "mutation_performed": False,
        "artifact_emitted": False,
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "emitter",
                "preview",
                "--skill",
                query,
                "--projection",
                projection,
                "--target-root",
                target_root,
                "--preview",
            )
        ],
        "agent_summary": emitter_receipt["agent_summary"],
    }
    result.data["skills_sdk_emitter_preview"] = payload
    if emitter_receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion="Use --projection runtime-skill with --target-root .agents/skills and a hardened local package.",
            )
        )
    return result


def skills_sdk_ci_policy_preview(
    repo_root: Path,
    risk_tier: str,
) -> CallResult:
    """Preview required CI checks without inspecting or mutating hosted CI."""
    del repo_root
    result = CallResult()
    result.metadata["command"] = "sdk ci policy"
    from ask.skills_sdk.ci_policy_preview import (  # noqa: PLC0415
        CiPolicyPreviewError,
        build_ci_policy_preview_receipt,
    )

    try:
        receipt = build_ci_policy_preview_receipt(risk_tier=risk_tier)
    except CiPolicyPreviewError as exc:
        receipt = exc.receipt
    payload = {
        "schema_version": "skills-sdk-ci-policy-preview.v0",
        "status": receipt["status"],
        "facade_command": "skills-sdk ci policy",
        "risk_tier": receipt["risk_tier"],
        "required_checks": receipt["required_checks"],
        "receipt": receipt,
        "live_ci_evidence_attached": False,
        "branch_protection_mutated": False,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command("sdk", "ci", "policy", "--risk-tier", risk_tier, "--preview")
        ],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_ci_policy_preview"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion="Use a supported SDK risk tier and attach live CI evidence in a separate hosted-check lane.",
            )
        )
    return result


def skills_sdk_security_adapters_preview(repo_root: Path) -> CallResult:
    """Discover configured local security adapters without executing scanners."""
    result = CallResult()
    result.metadata["command"] = "sdk security adapters"
    from ask.skills_sdk.security_adapter_discovery import (  # noqa: PLC0415
        SecurityAdapterDiscoveryError,
        build_security_adapter_discovery_receipt,
    )

    try:
        receipt = build_security_adapter_discovery_receipt(repo_root)
    except SecurityAdapterDiscoveryError as exc:
        receipt = exc.receipt
    payload = {
        "schema_version": "skills-sdk-security-adapter-discovery-receipt.v0",
        "status": receipt["status"],
        "facade_command": "skills-sdk security adapters",
        "adapter_count": receipt["adapter_count"],
        "adapter_candidates": receipt["adapter_candidates"],
        "receipt": receipt,
        "scanner_execution_performed": False,
        "network_accessed": False,
        "credentials_accessed": False,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command("sdk", "security", "adapters", "--preview")
        ],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_security_adapter_discovery"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion=(
                    "Add local scanner workflow or config evidence before approving any scanner execution adapter."
                ),
            )
        )
    return result


def skills_sdk_static_explorer_preview(repo_root: Path) -> CallResult:
    """Preview a JSON-only static explorer index without rendering or publishing HTML."""
    result = CallResult()
    result.metadata["command"] = "sdk explorer static"
    from ask.skills_sdk.static_explorer import (  # noqa: PLC0415
        StaticExplorerError,
        build_static_explorer_receipt,
    )

    try:
        receipt = build_static_explorer_receipt(repo_root)
    except StaticExplorerError as exc:
        receipt = exc.receipt
    payload = {
        "schema_version": "skills-sdk-static-explorer-preview.v0",
        "status": receipt["status"],
        "facade_command": "skills-sdk explorer static",
        "capability_count": receipt["capability_count"],
        "skill_count": receipt["skill_count"],
        "projection_inputs": receipt["projection_inputs"],
        "receipt": receipt,
        "html_rendered": False,
        "hosted_publish_requested": False,
        "mutation_performed": False,
        "validation_commands": [_ask_validation_command("sdk", "explorer", "static", "--preview")],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_static_explorer_preview"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion="Fix capability status JSON or rooted .skillsets manifest JSONL before previewing explorer indexes.",
            )
        )
    return result


def skills_sdk_eval_scenario_quality(repo_root: Path, target: str) -> CallResult:
    """Preview eval scenario quality without promoting or mutating scenario sources."""
    result = CallResult()
    result.metadata["command"] = "sdk eval scenario-quality"
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path
    if not source_path:
        result.status = "error"
        result.data["skills_sdk_eval_scenario_quality"] = {
            "schema_version": "skills-sdk-eval-scenario-quality.v0",
            "status": "blocked",
            "query": query,
            "canonical_source_path": source_path_value,
            "receipt": None,
            "mutation_performed": False,
            "promotion_performed": False,
            "validation_commands": [_ask_validation_command("sdk", "eval", "scenario-quality", query, "--preview")],
            "agent_summary": f"skills-sdk eval scenario-quality is blocked for {query}: canonical source is missing.",
        }
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK scenario quality is missing a canonical SKILL.md source for '{query}'.",
                fix_suggestion=_ask_validation_command("sdk", "eval", "scenario-quality", "<skill>", "--preview"),
            )
        )
        return result

    from ask.skills_sdk.scenario_quality import (  # noqa: PLC0415
        ScenarioQualityError,
        build_scenario_quality_receipt,
    )

    try:
        receipt = build_scenario_quality_receipt(repo_root, source_path=source_path, query=query)
    except ScenarioQualityError as exc:
        receipt = exc.receipt
    payload = {
        "schema_version": "skills-sdk-eval-scenario-quality.v0",
        "status": receipt["status"],
        "query": query,
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk eval scenario-quality",
        "receipt": receipt,
        "scenario_count": receipt["scenario_count"],
        "promotion_ready_count": receipt["promotion_ready_count"],
        "blocked_count": receipt["blocked_count"],
        "mutation_performed": False,
        "promotion_performed": False,
        "validation_commands": [_ask_validation_command("sdk", "eval", "scenario-quality", query, "--preview")],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_scenario_quality"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion="Add or repair references/evals.yaml with ids, prompts, acceptance checks, eval modes, and deterministic safety checks.",
            )
        )
    return result


def skills_sdk_eval_scorer_quality(repo_root: Path, target: str) -> CallResult:
    """Preview scorer calibration quality without promoting or mutating eval sources."""
    result = CallResult()
    result.metadata["command"] = "sdk eval scorer-quality"
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path
    if not source_path:
        result.status = "error"
        result.data["skills_sdk_eval_scorer_quality"] = {
            "schema_version": "skills-sdk-eval-scorer-quality.v0",
            "status": "blocked",
            "query": query,
            "canonical_source_path": source_path_value,
            "receipt": None,
            "ready": False,
            "mutation_performed": False,
            "promotion_performed": False,
            "validation_commands": [_ask_validation_command("sdk", "eval", "scorer-quality", query, "--preview")],
            "agent_summary": f"skills-sdk eval scorer-quality is blocked for {query}: canonical source is missing.",
        }
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK scorer quality is missing a canonical SKILL.md source for '{query}'.",
                fix_suggestion=_ask_validation_command("sdk", "eval", "scorer-quality", "<skill>", "--preview"),
            )
        )
        return result

    from ask.skills_sdk.scorer_quality import build_scorer_quality_receipt  # noqa: PLC0415

    receipt = build_scorer_quality_receipt(repo_root, source_path=source_path, query=query)
    payload = {
        "schema_version": "skills-sdk-eval-scorer-quality.v0",
        "status": receipt["status"],
        "query": query,
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk eval scorer-quality",
        "receipt": receipt,
        "ready": receipt["ready"],
        "blocked_count": len(receipt["blockers"]),
        "mutation_performed": False,
        "promotion_performed": False,
        "validation_commands": [_ask_validation_command("sdk", "eval", "scorer-quality", query, "--preview")],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_scorer_quality"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
    return result


def skills_sdk_eval_scorer_calibration(repo_root: Path, target: str) -> CallResult:
    """Preview held-out scorer calibration evidence without mutating eval sources."""
    result = CallResult()
    result.metadata["command"] = "sdk eval scorer-calibration"
    query = target.strip()
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path
    if not source_path:
        result.status = "error"
        result.data["skills_sdk_eval_scorer_calibration"] = {
            "schema_version": "skills-sdk-eval-scorer-calibration.v0",
            "status": "blocked",
            "query": query,
            "canonical_source_path": source_path_value,
            "receipt": None,
            "ready": False,
            "mutation_performed": False,
            "promotion_performed": False,
            "validation_commands": [_ask_validation_command("sdk", "eval", "scorer-calibration", query, "--preview")],
            "agent_summary": f"skills-sdk eval scorer-calibration is blocked for {query}: canonical source is missing.",
        }
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK scorer calibration is missing a canonical SKILL.md source for '{query}'.",
                fix_suggestion=_ask_validation_command("sdk", "eval", "scorer-calibration", "<skill>", "--preview"),
            )
        )
        return result

    from ask.skills_sdk.scorer_calibration import build_scorer_calibration_receipt  # noqa: PLC0415

    receipt = build_scorer_calibration_receipt(repo_root, source_path=source_path, query=query)
    payload = {
        "schema_version": "skills-sdk-eval-scorer-calibration.v0",
        "status": receipt["status"],
        "query": query,
        "canonical_source_path": source_path_value,
        "facade_command": "skills-sdk eval scorer-calibration",
        "receipt": receipt,
        "ready": receipt["ready"],
        "blocked_count": len(receipt["blockers"]),
        "mutation_performed": False,
        "promotion_performed": False,
        "validation_commands": [_ask_validation_command("sdk", "eval", "scorer-calibration", query, "--preview")],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_scorer_calibration"] = payload
    return result


def skills_sdk_eval_tessl_score(
    repo_root: Path,
    *,
    view_json: str,
    skill: str,
    run_id: str | None = None,
) -> CallResult:
    """Preview a Tessl score receipt from an explicit eval view JSON artifact."""
    result = CallResult()
    result.metadata["command"] = "sdk eval tessl-score"
    view_path = Path(view_json)
    if not view_path.is_absolute():
        view_path = repo_root / view_path

    from ask.skills_sdk.tessl_score_receipt import build_tessl_score_receipt  # noqa: PLC0415

    receipt = build_tessl_score_receipt(repo_root, view_json=view_path, skill=skill, run_id=run_id)
    result.data["skills_sdk_eval_tessl_score"] = {
        "schema_version": "skills-sdk-eval-tessl-score.v0",
        "status": receipt["status"],
        "ready": receipt["ready"],
        "skill": skill,
        "run_id": receipt["run_id"],
        "receipt": receipt,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command("sdk", "eval", "tessl-score", "--view-json", view_json, "--skill", skill, "--preview")
        ],
        "agent_summary": receipt["agent_summary"],
    }
    return result


def skills_sdk_observability_promote(
    repo_root: Path,
    *,
    feedback_receipt: str,
    package_receipt: str,
    eval_run_receipt: str,
) -> CallResult:
    """Preview whether observability feedback candidates can advance after package and eval proof."""
    result = CallResult()
    result.metadata["command"] = "sdk observability promote"
    from ask.skills_sdk.observability_promotion import build_observability_promotion_receipt  # noqa: PLC0415

    promotion_receipt = build_observability_promotion_receipt(
        repo_root,
        feedback_receipt_path=feedback_receipt,
        package_receipt_path=package_receipt,
        eval_run_receipt_path=eval_run_receipt,
    )
    payload = {
        "schema_version": "skills-sdk-observability-promotion.v0",
        "status": promotion_receipt["status"],
        "facade_command": "skills-sdk observability promote",
        "package_id": promotion_receipt["package_id"],
        "package_digest": promotion_receipt["package_digest"],
        "receipt": promotion_receipt,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "observability",
                "promote",
                "--feedback-receipt",
                feedback_receipt,
                "--package-receipt",
                package_receipt,
                "--eval-run-receipt",
                eval_run_receipt,
                "--preview",
            )
        ],
        "agent_summary": promotion_receipt["agent_summary"],
    }
    result.data["skills_sdk_observability_promote"] = payload
    if promotion_receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=payload["agent_summary"],
                fix_suggestion=(
                    "Provide matching observability feedback, package digest, and passing eval-run receipts "
                    "for the same package id and digest."
                ),
            )
        )
    return result


def skills_sdk_eval_profiles_preview(repo_root: Path) -> CallResult:
    """Emit the non-mutating Codex execution and judge profile contract."""
    del repo_root
    result = CallResult()
    result.metadata["command"] = "sdk eval profiles --preview"
    receipt = _build_eval_profile_preview_receipt()
    payload = {
        "schema_version": "skills-sdk-eval-profile-preview.v0",
        "status": receipt["status"],
        "facade_command": "skills-sdk eval profiles",
        "receipt": receipt,
        "mutation_performed": False,
        "validation_commands": [_ask_validation_command("sdk", "eval", "profiles", "--preview")],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_profiles"] = payload
    return result


def skills_sdk_eval_ab_rubric_preview(repo_root: Path) -> CallResult:
    """Emit the non-mutating canonical A/B scoring rubric contract."""
    del repo_root
    result = CallResult()
    result.metadata["command"] = "sdk eval ab-rubric --preview"
    receipt = _build_ab_rubric_preview_receipt()
    payload = {
        "schema_version": "skills-sdk-ab-rubric.v0",
        "status": receipt["status"],
        "facade_command": "skills-sdk eval ab-rubric",
        "receipt": receipt,
        "mutation_performed": False,
        "validation_commands": [_ask_validation_command("sdk", "eval", "ab-rubric", "--preview")],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_ab_rubric"] = payload
    return result


def skills_sdk_eval_ab_preview(
    repo_root: Path,
    *,
    skill_a: str,
    skill_b: str,
    fixture: str,
    execution_profile: str = "codex-read-only",
    judge_profile: str = "oss-local",
) -> CallResult:
    """Emit a non-mutating Codex-backed A/B eval experiment contract."""
    result = CallResult()
    result.metadata["command"] = "sdk eval ab-preview --preview"
    skill_a_identity = _skills_sdk_eval_package_identity(repo_root, skill_a)
    skill_b_identity = _skills_sdk_eval_package_identity(repo_root, skill_b)
    receipt = _build_ab_preview_receipt(
        repo_root,
        skill_a=skill_a,
        skill_b=skill_b,
        fixture=fixture,
        skill_a_identity=skill_a_identity,
        skill_b_identity=skill_b_identity,
        execution_profile_id=execution_profile,
        judge_profile_id=judge_profile,
    )
    payload = {
        "schema_version": "skills-sdk-ab-preview.v0",
        "status": receipt["status"],
        "facade_command": "skills-sdk eval ab-preview",
        "receipt": receipt,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "eval",
                "ab-preview",
                "--skill-a",
                skill_a,
                "--skill-b",
                skill_b,
                "--fixture",
                fixture,
                "--execution-profile",
                execution_profile,
                "--judge-profile",
                judge_profile,
                "--preview",
            )
        ],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_ab_preview"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=receipt["agent_summary"],
                fix_suggestion=(
                    "Use canonical repo-local skill sources and a repo-local fixture before running "
                    "ask sdk eval ab-preview."
                ),
            )
        )
    return result


def skills_sdk_eval_ab_plan(
    repo_root: Path,
    *,
    skill_a: str,
    skill_b: str,
    fixture: str,
    execution_profile: str = "codex-read-only",
    judge_profile: str = "oss-local",
    evidence_root: str = ".harness/artifacts/sdk-ab-evals",
) -> CallResult:
    """Emit a non-mutating Codex-backed A/B eval execution plan."""
    result = CallResult()
    result.metadata["command"] = "sdk eval ab-plan --preview"
    skill_a_identity = _skills_sdk_eval_package_identity(repo_root, skill_a)
    skill_b_identity = _skills_sdk_eval_package_identity(repo_root, skill_b)
    receipt = _build_ab_plan_receipt(
        repo_root,
        skill_a=skill_a,
        skill_b=skill_b,
        fixture=fixture,
        skill_a_identity=skill_a_identity,
        skill_b_identity=skill_b_identity,
        execution_profile_id=execution_profile,
        judge_profile_id=judge_profile,
        evidence_root=evidence_root,
    )
    payload = {
        "schema_version": "skills-sdk-ab-plan.v0",
        "status": receipt["status"],
        "facade_command": "skills-sdk eval ab-plan",
        "receipt": receipt,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "eval",
                "ab-plan",
                "--skill-a",
                skill_a,
                "--skill-b",
                skill_b,
                "--fixture",
                fixture,
                "--execution-profile",
                execution_profile,
                "--judge-profile",
                judge_profile,
                "--evidence-root",
                evidence_root,
                "--preview",
            )
        ],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_ab_plan"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=receipt["agent_summary"],
                fix_suggestion=(
                    "Use canonical repo-local skill sources, a repo-local fixture, and a repo-local "
                    "evidence root before running ask sdk eval ab-plan."
                ),
            )
        )
    return result


def skills_sdk_eval_ab_run(
    repo_root: Path,
    *,
    skill_a: str,
    skill_b: str,
    fixture: str,
    execution_profile: str = "codex-read-only",
    judge_profile: str = "oss-local",
    evidence_root: str = ".harness/artifacts/sdk-ab-evals",
    timeout_seconds: int = 1800,
) -> CallResult:
    """Execute a Codex-backed A/B eval and emit bounded evidence receipts."""
    result = CallResult()
    result.metadata["command"] = "sdk eval ab-run --execute"
    skill_a_identity = _skills_sdk_eval_package_identity(repo_root, skill_a)
    skill_b_identity = _skills_sdk_eval_package_identity(repo_root, skill_b)
    receipt = _build_ab_run_receipt(
        repo_root,
        skill_a=skill_a,
        skill_b=skill_b,
        fixture=fixture,
        skill_a_identity=skill_a_identity,
        skill_b_identity=skill_b_identity,
        execution_profile_id=execution_profile,
        judge_profile_id=judge_profile,
        evidence_root=evidence_root,
        timeout_seconds=timeout_seconds,
    )
    payload = {
        "schema_version": "skills-sdk-ab-run.v0",
        "status": receipt["status"],
        "facade_command": "skills-sdk eval ab-run",
        "receipt": receipt,
        "mutation_performed": receipt["mutation_performed"],
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "eval",
                "ab-run",
                "--skill-a",
                skill_a,
                "--skill-b",
                skill_b,
                "--fixture",
                fixture,
                "--execution-profile",
                execution_profile,
                "--judge-profile",
                judge_profile,
                "--evidence-root",
                evidence_root,
                "--timeout-seconds",
                str(timeout_seconds),
                "--execute",
            )
        ],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_ab_run"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=receipt["agent_summary"],
                fix_suggestion=(
                    "Review the per-variant blockers, evidence files, and Codex stderr captures before "
                    "rerunning ask sdk eval ab-run."
                ),
            )
        )
    return result


def skills_sdk_eval_ab_judge_preview(
    repo_root: Path,
    *,
    run_receipt: str,
) -> CallResult:
    """Emit a non-mutating sanitized A/B judge input receipt."""
    result = CallResult()
    result.metadata["command"] = "sdk eval ab-judge-preview --preview"
    receipt = _build_ab_judge_preview_receipt(repo_root, run_receipt=run_receipt)
    payload = {
        "schema_version": "skills-sdk-ab-judge-preview.v0",
        "status": receipt["status"],
        "facade_command": "skills-sdk eval ab-judge-preview",
        "receipt": receipt,
        "mutation_performed": False,
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "eval",
                "ab-judge-preview",
                "--run-receipt",
                run_receipt,
                "--preview",
            )
        ],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_ab_judge_preview"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=receipt["agent_summary"],
                fix_suggestion=(
                    "Provide a repo-local completed ab-run receipt before previewing judge input."
                ),
            )
        )
    return result


def skills_sdk_eval_ab_judge_score(
    repo_root: Path,
    *,
    run_receipt: str,
    evidence_root: str = ".harness/artifacts/sdk-ab-judges",
    judge_profile: str = "oss-local",
    timeout_seconds: int = 300,
) -> CallResult:
    """Invoke Ollama A/B judge scoring and emit advisory decision evidence."""
    result = CallResult()
    result.metadata["command"] = "sdk eval ab-judge-score --execute"
    receipt = _build_ab_judge_score_receipt(
        repo_root,
        run_receipt=run_receipt,
        evidence_root=evidence_root,
        judge_profile_id=judge_profile,
        timeout_seconds=timeout_seconds,
    )
    payload = {
        "schema_version": "skills-sdk-ab-judge-score.v0",
        "status": receipt["status"],
        "facade_command": "skills-sdk eval ab-judge-score",
        "receipt": receipt,
        "mutation_performed": receipt["mutation_performed"],
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "eval",
                "ab-judge-score",
                "--run-receipt",
                run_receipt,
                "--evidence-root",
                evidence_root,
                "--judge-profile",
                judge_profile,
                "--timeout-seconds",
                str(timeout_seconds),
                "--execute",
            )
        ],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_eval_ab_judge_score"] = payload
    if receipt["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=receipt["agent_summary"],
                fix_suggestion=(
                    "Provide a completed ab-run receipt and the selected Ollama judge runtime before "
                    "running ask sdk eval ab-judge-score."
                ),
            )
        )
    return result


def _skills_sdk_internal_case_results(scorecard: dict[str, Any]) -> tuple[list[dict[str, str]], list[str]]:
    cases: list[dict[str, str]] = []
    blockers: list[str] = []
    raw_cases = scorecard.get("cases")
    if not isinstance(raw_cases, list):
        return cases, blockers

    for index, raw_case in enumerate(raw_cases, start=1):
        if not isinstance(raw_case, dict):
            continue
        case_id = str(raw_case.get("id") or raw_case.get("name") or f"case-{index}").strip()
        if not case_id:
            case_id = f"case-{index}"
        passed = raw_case.get("passed") is True
        blocked = raw_case.get("blocked") is True
        status = "pass" if passed else "fail"
        raw_blockers = raw_case.get("blocked_reasons")
        if isinstance(raw_blockers, list):
            blockers.extend(str(reason) for reason in raw_blockers if str(reason).strip())
        raw_blocker_classes = raw_case.get("blocker_classes")
        if isinstance(raw_blocker_classes, list):
            blockers.extend(str(reason) for reason in raw_blocker_classes if str(reason).strip())
        tier1_failures = raw_case.get("tier1_failures")
        if not passed and isinstance(tier1_failures, list):
            blockers.extend(str(reason) for reason in tier1_failures if str(reason).strip())
        actual = "blocked" if blocked else status
        cases.append(
            {
                "case_id": case_id,
                "status": status,
                "oracle": "exact_match",
                "expected": "pass",
                "actual": actual,
            }
        )
    return cases, sorted(set(blockers))


def _skills_sdk_internal_eval_receipt_counts(
    repo_root: Path,
    internal: CallResult,
    *,
    status: str,
    fallback_blockers: list[str],
    eval_commands: _EvalCommandsProtocol,
) -> dict[str, Any]:
    raw_output = str(internal.data.get("raw_output") or "")
    scorecard_path = eval_commands._scorecard_path_from_output(repo_root, raw_output)  # noqa: SLF001
    scorecard = eval_commands._read_scorecard(scorecard_path)  # noqa: SLF001
    quality_gates = _internal_scorecard_quality_gates(scorecard)
    quality_blockers = (
        [f"quality_gate_failed:{item}" for item in quality_gates["failed_assertions"]]
        if quality_gates and quality_gates["failed_assertions"]
        else []
    )
    cases, case_blockers = _skills_sdk_internal_case_results(scorecard)
    if cases:
        failed_count = sum(1 for item in cases if item["status"] == "fail")
        receipt_status = status if status != "pass" else "fail" if failed_count or quality_blockers else "pass"
        blockers = sorted(set(fallback_blockers + case_blockers + quality_blockers)) if receipt_status != "pass" else []
        dataset_path = (
            _skills_sdk_repo_relative(repo_root, scorecard_path)
            if scorecard_path is not None and scorecard_path.is_file()
            else "internal:skill-builder"
        )
        dataset_digest = (
            _skills_sdk_digest_file(scorecard_path)
            if scorecard_path is not None and scorecard_path.is_file()
            else "sha256:" + ("0" * 64)
        )
        return {
            "status": receipt_status,
            "dataset_path": dataset_path,
            "dataset_digest": dataset_digest,
            "case_count": len(cases),
            "passed_count": len(cases) - failed_count,
            "failed_count": failed_count,
            "quality_gates": quality_gates,
            "cases": cases,
            "blockers": blockers,
        }

    internal_case_count = 0 if status == "blocked" else 1
    receipt_status = status if status != "pass" or not quality_blockers else "fail"
    return {
        "status": receipt_status,
        "dataset_path": "internal:skill-builder",
        "dataset_digest": "sha256:" + ("0" * 64),
        "case_count": internal_case_count,
        "passed_count": 1 if receipt_status == "pass" else 0,
        "failed_count": 1 if receipt_status == "fail" else 0,
        "quality_gates": quality_gates,
        "cases": [],
        "blockers": sorted(set(fallback_blockers + quality_blockers)),
    }


def skills_sdk_eval_run(
    repo_root: Path,
    dataset: str | None = None,
    target: str | None = None,
    mode: str = "smoke",
    runner: str = "auto",
    skip_tessl: bool = True,
    cases: list[str] | None = None,
) -> CallResult:
    """Run SDK evals through deterministic JSONL or the internal skill-builder backend."""
    result = CallResult()
    result.metadata["command"] = "sdk eval run"
    resolved_runner = "deterministic-jsonl" if runner == "auto" and dataset else runner
    if resolved_runner == "auto":
        resolved_runner = "internal"
    if resolved_runner == "internal":
        if not target:
            result.status = "error"
            result.data["skills_sdk_eval_run"] = {
                "schema_version": "skills-sdk-eval-run.v0",
                "status": "blocked",
                "dataset": dataset,
                "target": target,
                "runner": "internal_skill_builder_v0",
                "receipt": None,
                "mutation_performed": False,
                "validation_commands": [_ask_validation_command("sdk", "eval", "run", "<skill>", "--runner", "internal")],
                "agent_summary": "skills-sdk eval run is blocked: internal runner requires a skill target.",
            }
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message="Skills SDK internal eval run requires a skill target.",
                    fix_suggestion="Run ask sdk eval run <skill> --runner internal --mode smoke --json --robot.",
                )
            )
            return result
        from ask.commands import evals as _eval_commands  # noqa: PLC0415

        internal = _eval_commands.run_evals(
            repo_root,
            target,
            mode=mode,
            runner="codex",
            dashboard=True,
            skip_tessl=skip_tessl,
            cases=cases,
        )
        raw_status = str(internal.data.get("eval_status") or ("pass" if internal.status == "success" else "fail"))
        blockers = []
        if internal.status != "success":
            blockers = [error.message for error in internal.errors] or [raw_status]
        status = "pass" if internal.status == "success" else "blocked" if raw_status.startswith("blocked") else "fail"
        target_path = str(internal.data.get("resolved_skill_path") or target)
        package_identity = _skills_sdk_eval_package_identity(repo_root, target_path)
        receipt_counts = _skills_sdk_internal_eval_receipt_counts(
            repo_root,
            internal,
            status=status,
            fallback_blockers=blockers,
            eval_commands=_eval_commands,
        )
        receipt = {
            "schema_version": "skills-sdk.eval-run-receipt.v0",
            "schema_uri": "https://jscraik.local/agent-skills/schemas/skills-sdk/eval-run-receipt.v0.schema.json",
            "status": receipt_counts["status"],
            "runner": "internal_skill_builder_v0",
            "dataset_path": receipt_counts["dataset_path"],
            "dataset_digest": receipt_counts["dataset_digest"],
            "skill_ir_schema_version": package_identity["skill_ir_schema_version"] if package_identity else None,
            "package_id": package_identity["package_id"] if package_identity else None,
            "package_digest": package_identity["package_digest"] if package_identity else None,
            "target_path": target_path,
            "mode": mode,
            "case_count": receipt_counts["case_count"],
            "passed_count": receipt_counts["passed_count"],
            "failed_count": receipt_counts["failed_count"],
            "quality_gates": receipt_counts["quality_gates"],
            "cases": receipt_counts["cases"],
            "blockers": receipt_counts["blockers"],
            "mutation_performed": False,
            "acceptance_trace": ["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022"],
        }
        status = receipt["status"]
        payload = {
            "schema_version": "skills-sdk-eval-run.v0",
            "status": status,
            "dataset": dataset,
            "target": target,
            "runner": "internal_skill_builder_v0",
            "mode": mode,
            "receipt": receipt,
            "internal_eval": internal.data,
            "mutation_performed": False,
            "validation_commands": [_ask_validation_command("sdk", "eval", "run", target, "--runner", "internal", "--mode", mode)],
            "agent_summary": f"skills-sdk internal eval run {status} for {target} in {mode} mode.",
        }
        result.data["skills_sdk_eval_run"] = payload
        if status != "pass":
            result.status = "error"
            result.errors.extend(internal.errors)
            if not result.errors:
                result.errors.append(
                    ErrorObject(
                        code="ERR_VALIDATION",
                        message=f"Skills SDK internal eval run did not pass for {target}.",
                        fix_suggestion=_ask_validation_command("sdk", "eval", "run", target, "--runner", "internal", "--mode", mode),
                    )
                )
        return result

    if resolved_runner != "deterministic-jsonl":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Unsupported Skills SDK eval runner: {runner}.",
                fix_suggestion="Use --runner internal or --runner deterministic-jsonl.",
            )
        )
        return result
    if not dataset:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Skills SDK deterministic eval run requires --dataset.",
                fix_suggestion="Run ask sdk eval run --runner deterministic-jsonl --dataset <cases.jsonl> --json --robot.",
            )
        )
        return result
    package_identity: dict[str, str] | None = None
    if target:
        query = target.strip()
        package_identity = _skills_sdk_eval_package_identity(repo_root, query)
        if package_identity is None:
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=f"Skills SDK eval run is missing a canonical SKILL.md source for '{query}'.",
                    fix_suggestion=_ask_validation_command("sdk", "ir", "build", query),
                )
            )
            result.data["skills_sdk_eval_run"] = {
                "schema_version": "skills-sdk-eval-run.v0",
                "status": "blocked",
                "dataset": dataset,
                "target": query,
                "receipt": None,
                "mutation_performed": False,
                "validation_commands": [_ask_validation_command("sdk", "eval", "run", "--dataset", dataset, "--skill", query)],
                "agent_summary": f"skills-sdk eval run is blocked for {query}: canonical source is missing.",
            }
            return result

    receipt = _run_deterministic_eval(
        repo_root,
        dataset=dataset,
        skill_ir_schema_version=package_identity["skill_ir_schema_version"] if package_identity else None,
        package_id=package_identity["package_id"] if package_identity else None,
        package_digest=package_identity["package_digest"] if package_identity else None,
    )
    payload = {
        "schema_version": "skills-sdk-eval-run.v0",
        "status": receipt["status"],
        "dataset": dataset,
        "target": target,
        "runner": receipt["runner"],
        "case_count": receipt["case_count"],
        "passed_count": receipt["passed_count"],
        "failed_count": receipt["failed_count"],
        "receipt": receipt,
        "mutation_performed": False,
        "validation_commands": [_ask_validation_command("sdk", "eval", "run", "--dataset", dataset)],
        "agent_summary": (
            f"skills-sdk eval run {receipt['status']} with "
            f"{receipt['passed_count']}/{receipt['case_count']} deterministic JSONL case(s) passing."
        ),
    }
    if target:
        payload["validation_commands"] = [
            _ask_validation_command("sdk", "eval", "run", "--dataset", dataset, "--skill", target)
        ]
    result.data["skills_sdk_eval_run"] = payload
    if receipt["status"] != "pass":
        result.status = "error"
        message = "Skills SDK deterministic eval run did not pass."
        if receipt["status"] == "blocked" and receipt["blockers"]:
            message = f"Skills SDK deterministic eval run blocked: {receipt['blockers'][0]}"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=message,
                fix_suggestion="Fix the JSONL eval dataset or expected/actual exact-match values and rerun ask sdk eval run.",
            )
        )
    return result


def skills_sdk_project_install(
    repo_root: Path,
    target: str,
    project_root: str | None = None,
    scope: str = "project",
) -> CallResult:
    """Install one local skill into an explicit project root."""
    result = CallResult()
    result.metadata["command"] = "sdk install --apply"
    query = target.strip()
    if scope != "project":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Real Skills SDK installs are bounded to --scope project in PU-009.",
                fix_suggestion="ask sdk install <target> --apply --scope project --project-root /path/to/project --json --robot",
            )
        )
        return result
    target_info, _audit_target = _resolve_doctor_target(repo_root, query)
    source_path_value = target_info.get("source_path") if isinstance(target_info, dict) else None
    source_path = Path(str(source_path_value)) if source_path_value else None
    if source_path and not source_path.is_absolute():
        source_path = repo_root / source_path
    try:
        receipt = _install_project_skill(
            repo_root,
            query=query,
            source_path=source_path,
            target_info=target_info,
            project_root=project_root,
        )
    except _ProjectInstallError as exc:
        result.status = "error"
        result.data["skills_sdk_project_install"] = {
            "schema_version": "skills-sdk-project-install.v1",
            "query": query,
            "status": str(exc.receipt.get("status") or "blocked"),
            "scope": "project",
            "canonical_source_path": str(source_path) if source_path else None,
            "facade_command": "skills-sdk install --apply",
            "receipt": exc.receipt,
            "validation_commands": [
                _ask_validation_command(
                    "sdk",
                    "install",
                    query,
                    "--apply",
                    "--project-root",
                    project_root or "<project-root>",
                ),
            ],
            "agent_summary": exc.message,
        }
        result.errors.append(
            ErrorObject(
                code=exc.code,
                message=exc.message,
                fix_suggestion=exc.fix_suggestion,
            )
        )
        return result

    payload = {
        "schema_version": "skills-sdk-project-install.v1",
        "query": query,
        "status": receipt["status"],
        "scope": "project",
        "canonical_source_path": str(source_path) if source_path else None,
        "facade_command": "skills-sdk install --apply",
        "receipt": receipt,
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "install",
                query,
                "--apply",
                "--project-root",
                project_root or "<project-root>",
            ),
        ],
        "agent_summary": (
            f"skills-sdk installed {len(receipt['files_written'])} file(s) for {query} into {receipt['target_root']}."
        ),
    }
    result.data["skills_sdk_project_install"] = payload
    return result


def skills_sdk_project_rollback(
    repo_root: Path,
    receipt_path: str,
    project_root: str | None = None,
    apply: bool = False,
) -> CallResult:
    """Preview or apply receipt-proven cleanup for one project install receipt."""
    result = CallResult()
    mode = "--apply" if apply else "--preview"
    result.metadata["command"] = f"sdk rollback {mode}"
    try:
        receipt = _rollback_project_install(
            repo_root,
            receipt_path=receipt_path,
            project_root=project_root,
            apply=apply,
        )
    except _ProjectCleanupError as exc:
        result.status = "error"
        result.data["skills_sdk_project_rollback"] = {
            "schema_version": "skills-sdk-project-cleanup.v1",
            "operation": "rollback",
            "status": exc.receipt.get("status", "blocked"),
            "mode": "apply" if apply else "preview",
            "receipt": exc.receipt,
            "validation_commands": [
                _ask_validation_command(
                    "sdk",
                    "rollback",
                    "--receipt",
                    receipt_path,
                    mode,
                    *(("--project-root", project_root) if project_root else ()),
                )
            ],
            "agent_summary": exc.message,
        }
        result.errors.append(
            ErrorObject(
                code=exc.code,
                message=exc.message,
                fix_suggestion=exc.fix_suggestion,
            )
        )
        return result
    payload = {
        "schema_version": "skills-sdk-project-cleanup.v1",
        "operation": "rollback",
        "status": receipt["status"],
        "mode": "apply" if apply else "preview",
        "receipt": receipt,
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "rollback",
                "--receipt",
                receipt_path,
                mode,
                *(("--project-root", project_root) if project_root else ()),
            )
        ],
        "agent_summary": (
            f"skills-sdk rollback {receipt['status']} for {len(receipt.get('files_applied') if 'files_applied' in receipt else receipt.get('files_cleaned_up') if 'files_cleaned_up' in receipt else receipt['files_planned'])} {'applied' if receipt.get('mode') == 'apply' else 'planned'} file(s)."
            if receipt.get('mode') == 'apply'
            else f"skills-sdk rollback {receipt['status']} for {len(receipt['files_planned'])} planned file(s)."
        ),
    }
    result.data["skills_sdk_project_rollback"] = payload
    return result


def skills_sdk_project_uninstall(
    repo_root: Path,
    skill_id: str,
    project_root: str | None = None,
    apply: bool = False,
) -> CallResult:
    """
    Generate a project uninstallation receipt for a lockfile-resolved skill and optionally apply the cleanup.
    
    Parameters:
        repo_root (Path): Repository root path used to resolve and operate on the project.
        skill_id (str): Lockfile-resolved skill identifier to uninstall.
        project_root (str | None): Optional project root path to target; when omitted the repo-level project is used.
        apply (bool): When True, perform the uninstall changes; when False, produce a preview-only receipt.
    
    Returns:
        CallResult: Result with `data["skills_sdk_project_uninstall"]` containing a `skills-sdk-project-cleanup.v1` receipt payload
        with keys: `schema_version`, `operation`, `status`, `mode`, `skill_id`, `receipt`, `validation_commands`, and `agent_summary`.
        On failure (internal project cleanup error) the result has `status="error"` and `errors` contains an `ErrorObject`
        derived from the cleanup exception; the corresponding receipt is included in the data payload.
    """
    result = CallResult()
    mode = "--apply" if apply else "--preview"
    result.metadata["command"] = f"sdk uninstall {mode}"
    try:
        receipt = _uninstall_project_skill(
            repo_root,
            skill_id=skill_id,
            project_root=project_root,
            apply=apply,
        )
    except _ProjectCleanupError as exc:
        result.status = "error"
        result.data["skills_sdk_project_uninstall"] = {
            "schema_version": "skills-sdk-project-cleanup.v1",
            "operation": "uninstall",
            "status": exc.receipt.get("status", "blocked"),
            "mode": "apply" if apply else "preview",
            "skill_id": skill_id,
            "receipt": exc.receipt,
            "validation_commands": [
                _ask_validation_command(
                    "sdk",
                    "uninstall",
                    skill_id,
                    mode,
                    *(("--project-root", project_root) if project_root else ()),
                )
            ],
            "agent_summary": exc.message,
        }
        result.errors.append(
            ErrorObject(
                code=exc.code,
                message=exc.message,
                fix_suggestion=exc.fix_suggestion,
            )
        )
        return result
    payload = {
        "schema_version": "skills-sdk-project-cleanup.v1",
        "operation": "uninstall",
        "status": receipt["status"],
        "mode": "apply" if apply else "preview",
        "skill_id": skill_id,
        "receipt": receipt,
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "uninstall",
                skill_id,
                mode,
                *(("--project-root", project_root) if project_root else ()),
            )
        ],
        "agent_summary": (
            f"skills-sdk uninstall {receipt['status']} for {skill_id} with {len(receipt.get('files_applied') if 'files_applied' in receipt else receipt.get('files_cleaned_up') if 'files_cleaned_up' in receipt else receipt['files_planned'])} {'applied' if receipt.get('mode') == 'apply' else 'planned'} file(s)."
            if receipt.get('mode') == 'apply'
            else f"skills-sdk uninstall {receipt['status']} for {skill_id} with {len(receipt['files_planned'])} planned file(s)."
        ),
    }
    result.data["skills_sdk_project_uninstall"] = payload
    return result


def skills_sdk_project_conformance(
    repo_root: Path,
    project_root: str | None = None,
    mode: str = "status",
) -> CallResult:
    """
    Report Skills SDK project conformance for a given repository and project location.
    
    Parameters:
    	repo_root (Path): Repository root containing skills metadata.
    	project_root (str | None): Project directory to evaluate; when None the project root is inferred.
    	mode (str): Conformance mode, either "status" (summary) or "doctor" (detailed diagnostics).
    
    Returns:
    	result (CallResult): Contains `data["skills_sdk_project_conformance"]` with a `skills-sdk-project-conformance.v1` payload:
    		- `status`: overall conformance status from the generated receipt.
    		- `mode`: the requested mode.
    		- `project_root`: the provided project_root value.
    		- `receipt`: the full conformance receipt produced by the builder.
    		- `validation_commands`: suggested CLI command(s) to re-run the check.
    		- `agent_summary`: short human-readable summary.
    	On invalid `mode`, the result has `status="error"` and an `ERR_VALIDATION` ErrorObject. If the underlying receipt builder fails, the result has `status="error"`, includes the error receipt in the payload, and adds an ErrorObject derived from the builder exception.
    """
    result = CallResult()
    result.metadata["command"] = f"sdk project {mode}"
    if mode not in {"status", "doctor"}:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Skills SDK project conformance mode must be status or doctor.",
                fix_suggestion="ask sdk project status --project-root /path/to/project --json --robot",
            )
        )
        return result
    try:
        receipt = _build_project_conformance_receipt(
            repo_root,
            project_root=project_root,
            mode=mode,
        )
    except _ProjectConformanceError as exc:
        result.status = "error"
        validation_cmd_args = ["sdk", "project", mode]
        if project_root:
            validation_cmd_args.extend(["--project-root", project_root])
        result.data["skills_sdk_project_conformance"] = {
            "schema_version": "skills-sdk-project-conformance.v1",
            "status": exc.receipt.get("status", "blocked"),
            "mode": mode,
            "project_root": project_root,
            "receipt": exc.receipt,
            "validation_commands": [_ask_validation_command(*validation_cmd_args)],
            "agent_summary": exc.message,
        }
        result.errors.append(
            ErrorObject(
                code=exc.code,
                message=exc.message,
                fix_suggestion=exc.fix_suggestion,
            )
        )
        return result
    validation_cmd_args = ["sdk", "project", mode]
    if project_root:
        validation_cmd_args.extend(["--project-root", project_root])
    payload = {
        "schema_version": "skills-sdk-project-conformance.v1",
        "status": receipt["status"],
        "mode": mode,
        "project_root": project_root,
        "receipt": receipt,
        "validation_commands": [_ask_validation_command(*validation_cmd_args)],
        "agent_summary": receipt["agent_summary"],
    }
    result.data["skills_sdk_project_conformance"] = payload
    return result


def skills_sdk_placeholder_lifecycle(
    repo_root: Path,
    surface: str | None = None,
    risk_tier: str = "medium",
) -> CallResult:
    """Emit read-only placeholder lifecycle receipts for unavailable V1.0 surfaces."""
    del repo_root
    result = CallResult()
    result.metadata["command"] = "sdk lifecycle"
    try:
        lifecycle = _build_placeholder_lifecycle_receipts(surface=surface, risk_tier=risk_tier)
    except (ValueError, KeyError, TypeError) as e:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Placeholder lifecycle builder validation failed: {e}",
                fix_suggestion="Check that surface and risk_tier arguments match the canonical SDK contract.",
            )
        )
        return result
    payload = {
        **lifecycle,
        "facade_command": "skills-sdk lifecycle",
        "validation_commands": [
            _ask_validation_command(
                "sdk",
                "lifecycle",
                *(("--surface", surface) if surface else ()),
                "--risk-tier",
                risk_tier,
            )
        ],
    }
    result.data["skills_sdk_placeholder_lifecycle"] = payload
    if lifecycle["status"] == "blocked":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=lifecycle["agent_summary"],
                fix_suggestion="Use --risk-tier medium for optional placeholder reporting, or implement the missing adapter in a later approved slice.",
            )
        )
    return result


def skills_sdk_status(repo_root: Path) -> CallResult:
    """Report the canonical Skills SDK capability truth matrix."""
    result = CallResult()
    result.metadata["command"] = "sdk status"
    try:
        status = _build_capability_status(repo_root)
    except _CapabilityStatusError as e:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skills SDK capability matrix validation failed: {e}",
                fix_suggestion="Fix Infrastructure/config/skills-sdk/capability-matrix.v1.json and rerun ask sdk status.",
            )
        )
        return result
    result.data["skills_sdk_status"] = status
    return result


def skills_prove(repo_root: Path, handle: str) -> CallResult:
    """Compose an agent-facing proof scorecard for one skill handle."""
    result = CallResult()
    result.metadata["command"] = "skills prove"
    query = handle.strip()
    goal_resolution: dict[str, Any] | None = None
    reachability_result = skills_proof(repo_root, query)
    command_proof = reachability_result.data.get("proof", {})
    initial_resolution = command_proof.get("resolution") if isinstance(command_proof, dict) else {}
    resolver_ok = isinstance(initial_resolution, dict) and initial_resolution.get("status") == "ok"
    if reachability_result.status != "success" and not resolver_ok:
        improvement_result = improve_skills(repo_root, goal_text=query)
        goal_resolution = improvement_result.data.get("improvement")
        candidate = (goal_resolution or {}).get("recommended_capability") or {}
        if candidate.get("handle"):
            reachability_result = skills_proof(repo_root, str(candidate["handle"]))
        else:
            result.status = "error"
            result.data["skill_proof"] = {
                "schema_version": "skill-proof-scorecard.v1",
                "query": query,
                "handle": None,
                "proof_status": "blocked_goal_resolution",
                "agent_summary": f"Could not resolve goal '{query}' to one skill handle.",
                "reachability": {"status": "not_checked", "source": "goal_resolution"},
                "structural_quality": {"status": "not_checked", "audit_command": None},
                "analytics": {
                    "status": "unavailable_or_legacy",
                    "evidence_class": "native_skill_invocation_projection",
                    "note": "No skill handle was available for analytics lookup.",
                },
                "outcome_proof": {"status": "not_checked", "workout_candidates": [], "evidence_class": "outcome_proof"},
                "goal_resolution": goal_resolution,
                "next_command": (goal_resolution or {}).get("next_command")
                or _skills_validation_command("improve", query),
            }
            result.data["skill_proof"]["validation_commands"] = [
                result.data["skill_proof"]["next_command"],
            ]
            result.errors.extend(improvement_result.errors)
            if not result.errors:
                result.errors.append(
                    ErrorObject(
                        code="ERR_VALIDATION",
                        message=f"Could not resolve goal '{query}' to one skill handle.",
                        fix_suggestion=result.data["skill_proof"]["next_command"],
                    )
                )
            return result
    command_proof = reachability_result.data.get("proof", {})
    resolution = command_proof.get("resolution") if isinstance(command_proof, dict) else {}
    if not isinstance(resolution, dict):
        resolution = {}
    normalized = str(command_proof.get("handle") or resolution.get("handle") or handle.lstrip("$"))
    reachability_status = command_proof.get("status") if isinstance(command_proof, dict) else "missing"

    audit_target = _skill_audit_target(repo_root, resolution)
    structural_detail: dict[str, Any] = {
        "status": "missing",
        "audit_level": "compat",
        "audit_command": None,
    }
    if audit_target:
        audit_result = audit_skill(repo_root, audit_target, level="compat")
        structural_detail = {
            "status": "pass" if audit_result.status == "success" else "fail",
            "audit_level": "compat",
            "audit_command": _skills_validation_command("audit", audit_target, "--level", "compat"),
            "strict_audit_command": _skills_validation_command("audit", audit_target, "--level", "strict"),
            "diagnostics_exit_code": audit_result.data.get("diagnostics", {}).get("exit_code"),
        }

    analytics = skill_invocation_analytics(repo_root, normalized)
    workouts = _skill_workout_candidates(repo_root, normalized)
    outcome_status = "missing"
    next_command = _skills_validation_command("proof", normalized)
    if reachability_status != "pass":
        proof_status = "blocked_reachability"
    elif structural_detail["status"] != "pass":
        proof_status = "blocked_structural_quality"
        next_command = structural_detail.get("audit_command") or next_command
    elif workouts:
        proof_status = "reachable_without_outcome_proof"
        outcome_status = "available_not_run"
        next_command = _ask_validation_command("workouts", "run", workouts[0])
    else:
        proof_status = "reachable_without_outcome_proof"
        next_command = structural_detail.get("strict_audit_command") or next_command

    scorecard = {
        "schema_version": "skill-proof-scorecard.v1",
        "query": query,
        "handle": normalized,
        "proof_status": proof_status,
        "agent_summary": (
            f"{normalized} is reachable and structurally valid, but outcome proof is not present."
            if proof_status == "reachable_without_outcome_proof"
            else f"{normalized} proof is blocked at {proof_status.replace('blocked_', '').replace('_', ' ')}."
        ),
        "reachability": {
            "status": reachability_status,
            "source": "sdk_skill_proof",
            "command": _skills_validation_command("proof", normalized),
        },
        "structural_quality": structural_detail,
        "analytics": analytics,
        "outcome_proof": {
            "status": outcome_status,
            "workout_candidates": workouts,
            "evidence_class": "outcome_proof",
        },
        "next_command": next_command,
        "validation_commands": [next_command],
    }
    if goal_resolution:
        scorecard["goal_resolution"] = goal_resolution
    result.data["skill_proof"] = scorecard
    result.data["sdk_skill_proof"] = command_proof
    if proof_status.startswith("blocked_"):
        result.status = "error"
        result.errors.extend(reachability_result.errors)
        if not result.errors:
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=f"Skill proof scorecard is blocked for '{normalized}'.",
                    fix_suggestion=next_command,
                )
            )
    return result


def _skill_sections(path: Path) -> dict[str, list[str]]:
    """Return markdown section bodies keyed by heading text."""
    lines = path.read_text(encoding="utf-8").splitlines()
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines:
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            current = match.group(1).strip().lower()
            sections[current] = []
            continue
        if current:
            sections[current].append(line)
    return sections


def _section_items(sections: dict[str, list[str]], names: tuple[str, ...], limit: int = 4) -> list[str]:
    """Extract concise bullets or first paragraphs from named markdown sections."""
    items: list[str] = []
    for name in names:
        for raw in sections.get(name, []):
            line = raw.strip()
            if not line:
                continue
            line = re.sub(r"^[-*]\s+", "", line)
            line = re.sub(r"^\d+\.\s+", "", line)
            items.append(line)
            if len(items) >= limit:
                return items
    return items


def _skill_usage_items(sections: dict[str, list[str]], limit: int = 4) -> tuple[list[str], list[str]]:
    """Split positive and negative guidance from a skill's usage section."""
    when_to_use: list[str] = []
    when_not_to_use: list[str] = []
    for raw in sections.get("when to use", []):
        line = raw.strip()
        if not line:
            continue
        line = re.sub(r"^[-*]\s+", "", line)
        line = re.sub(r"^\d+\.\s+", "", line)
        if line.lower().startswith("avoid "):
            when_not_to_use.append(line)
        else:
            when_to_use.append(line)
        if len(when_to_use) >= limit and len(when_not_to_use) >= limit:
            break
    return when_to_use[:limit], when_not_to_use[:limit]


def _skill_validation_commands(source_path: Path, repo_root: Path) -> list[str]:
    """Return executable validation commands for a resolved skill source."""
    try:
        relative_source = source_path.relative_to(repo_root)
    except ValueError:
        return []
    audit_target = relative_source.parent if relative_source.name == "SKILL.md" else relative_source
    return [_skills_validation_command("audit", str(audit_target), "--level", "strict")]


def explain_skill(repo_root: Path, handle: str) -> CallResult:
    """Explain one SDK-visible skill handle for agent use."""
    result = CallResult()
    result.metadata["command"] = "skills explain"
    resolution = resolve_skill_handle(handle, repo_root_path=repo_root)
    normalized = resolution.get("handle", handle.lstrip("$"))
    if resolution.get("status") != "ok":
        result.status = "error"
        result.data["explanation"] = {
            "schema_version": "skill-explanation.v1",
            "status": "blocked",
            "handle": normalized,
            "agent_summary": f"Could not resolve skill handle '{normalized}'.",
            "next_command": _skills_validation_command("resolve", str(normalized)),
        }
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Could not explain skill handle '{normalized}': {resolution.get('error_code')}",
                fix_suggestion=resolution.get("operator_action"),
            )
        )
        return result

    source_path_value = str(resolution.get("source_path") or "").strip()
    if not source_path_value:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Skill handle '{normalized}' resolved without a canonical source path.",
                fix_suggestion="Run ./bin/ask skills sync --scope workspace --projection flat --json --robot and rerun ./bin/ask skills explain.",
            )
        )
        return result
    raw_source_path = Path(source_path_value)
    source_path = raw_source_path if raw_source_path.is_absolute() else repo_root / raw_source_path
    try:
        resolved_source = source_path.resolve()
        resolved_repo = repo_root.resolve()
        try:
            resolved_source.relative_to(resolved_repo)
        except ValueError:
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_PATH_TRAVERSAL",
                    message=f"Skill handle '{normalized}' resolved outside the repository root.",
                    fix_suggestion="Fix the SDK skill registry source path and rerun ./bin/ask skills explain.",
                )
            )
            return result
    except (ValueError, OSError) as e:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Failed to validate source path: {e}",
                fix_suggestion="Ensure the source path is valid and accessible",
            )
        )
        return result
    if not resolved_source.is_file():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Resolved source for '{normalized}' is missing: {source_path}",
                fix_suggestion="Run ./bin/ask skills sync --scope workspace --projection flat --json --robot and rerun ./bin/ask skills explain.",
            )
        )
        return result
    try:
        sections = _skill_sections(source_path)
    except OSError:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Resolved source for '{normalized}' could not be read: {source_path}",
                fix_suggestion=f"Fix source permissions or rerun `./bin/ask skills explain {shlex.quote(str(normalized))}` after syncing.",
            )
        )
        return result
    description = str(resolution.get("description") or "").strip()
    when_to_use, inline_when_not_to_use = _skill_usage_items(sections, limit=4)
    when_to_use = when_to_use or ([description] if description else [])
    when_not_to_use = inline_when_not_to_use or _section_items(sections, ("avoid",), limit=4)
    required_validation = _section_items(sections, ("validation",), limit=4)
    known_limitations = _section_items(sections, ("failure mode", "anti-patterns", "constraints"), limit=4)
    validation_commands = _skill_validation_commands(source_path, repo_root)
    proof_result = skills_proof(repo_root, str(normalized))
    proof = proof_result.data.get("proof", {})

    skills_explain = {
        "schema_version": "skills-explain.v1",
        "query": handle,
        "canonical_source": resolution.get("source_path"),
        "skill_handle": normalized,
        "handle_source": resolution.get("handle_source") or "sdk_flat_registry",
        "runtime_projection": (resolution.get("provenance") or {}).get("projection_mode"),
        "runtime_visibility": resolution.get("runtime_visibility"),
        "owner": resolution.get("owner"),
        "loaded_references": [],
        "when_to_use": when_to_use,
        "when_not_to_use": when_not_to_use,
        "validation": validation_commands,
        "overlaps": [],
        "ambiguity_notes": [],
    }
    # Determine runtime projection path - check if a file-backed projection exists
    runtime_projection_path = None
    projection_note = None
    canonical_source_path = resolution.get("source_path")

    if canonical_source_path:
        # Check for file-backed runtime projection in .agents/skills
        potential_projection = repo_root / ".agents" / "skills" / normalized / "SKILL.md"
        if potential_projection.is_file():
            try:
                runtime_projection_path = str(potential_projection.relative_to(repo_root))
            except ValueError:
                runtime_projection_path = None
                projection_note = "projection_outside_repo"
        else:
            projection_note = "projection_not_file_backed"

    runtime_projection_mode = (resolution.get("provenance") or {}).get("projection_mode")
    if runtime_projection_path and resolution.get("runtime_visibility") == "flat":
        runtime_projection_mode = "flat"
        if (resolution.get("provenance") or {}).get("projection_mode") not in {None, "flat"}:
            projection_note = "file_backed_flat_projection_overrides_stale_resolver_provenance"
    skills_explain["runtime_projection"] = runtime_projection_mode

    explanation = {
        "schema_version": "skill-explanation.v1",
        "status": "resolved",
        "handle": normalized,
        "agent_summary": f"{normalized} is for {description}" if description else f"{normalized} is resolved.",
        "what_it_is": description,
        "when_to_use": when_to_use,
        "when_not_to_use": when_not_to_use,
        "canonical_source_path": canonical_source_path,
        "runtime_projection_path": runtime_projection_path,
        "skill_handles": [
            {
                "handle": normalized,
                "path": runtime_projection_path,
                "projection_note": projection_note,
                "handle_source": resolution.get("handle_source") or "sdk_flat_registry",
            }
        ],
        "required_validation": required_validation,
        "validation_commands": validation_commands,
        "known_limitations": known_limitations,
        "overlaps": skills_explain["overlaps"],
        "ambiguity_notes": skills_explain["ambiguity_notes"],
        "reachability": {
            "status": proof.get("status") if isinstance(proof, dict) else "not_checked",
            "proof_command": _skills_validation_command("proof", str(normalized)),
        },
        "resolution": resolution,
        "next_command": _skills_validation_command("proof", str(normalized)),
    }
    result.data["skills_explain"] = skills_explain
    result.data["explanation"] = explanation
    return result


def reviewers_resolve(repo_root: Path, handle: str) -> CallResult:
    """Resolve one reviewer/subagent handle from the reviewer namespace."""
    result = CallResult()
    result.metadata["command"] = "reviewers resolve"
    payload = resolve_reviewer_handle(handle)
    normalized = str(payload.get("canonical_handle") or payload.get("handle") or handle).lstrip("@")
    payload["validation_commands"] = [
        _ask_validation_command("reviewers", "resolve", normalized),
    ]
    result.data["resolution"] = payload
    if payload.get("status") != "ok":
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Could not resolve reviewer handle '{payload.get('handle', handle)}': {payload.get('error_code')}",
                fix_suggestion=payload.get("operator_action"),
            )
        )
    return result


def init_skill(repo_root: Path, name: str, category: str, description: str) -> CallResult:
    """Initializes a new skill scaffold using the repo template logic."""
    result = CallResult()
    result.data["validation_commands"] = [
        _skills_validation_command(
            "init",
            name,
            "--category",
            category,
            "--description",
            description,
        )
    ]
    category_token = (category or "").strip()
    if not category_token:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Skill category cannot be empty.",
                fix_suggestion="Use a category such as 'ui' or 'code_quality_review'.",
            )
        )
        return result
    if Path(category_token).is_absolute():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Skill category must be repo-relative.",
                fix_suggestion="Use a category token such as 'ui' (not an absolute path).",
            )
        )
        return result

    if category_token.startswith("Skills/"):
        out_dir = repo_root / category_token
        category_rel = category_token
    else:
        out_dir = repo_root / "Skills" / category_token
        category_rel = f"Skills/{category_token}"
    try:
        out_dir.resolve().relative_to(repo_root.resolve())
    except ValueError:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_PATH_TRAVERSAL",
                message=f"Category '{category}' escapes repository root.",
                fix_suggestion="Use a category path under Skills/.",
            )
        )
        return result

    init_skill_script = _resolve_skill_builder_script(repo_root, "init_skill")
    cmd = _get_python_command(["pyyaml"]) + [
        init_skill_script,
        name,
        "--path",
        str(out_dir),
        "--description", description,
        "--owner", "Agent Skills Kit",
        "--review-cadence", "quarterly",
        "--maturity", "experimental",
        "--lifecycle-state", "incubating"
    ]

    process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)

    if process.returncode == 0:
        result.status = "success"
        result.data["message"] = f"Initialized skill '{name}' in '{category_rel}'"
        result.data["canonical_dest"] = category_rel
        result.metadata["next_steps"] = [f"ask skills audit {category_rel}/{name} --level strict"]
    else:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=process.stderr.strip()))

    return result

def audit_skill(repo_root: Path, skill_path: str, level: str = "compat") -> CallResult:
    """
    Run structural and (optionally) strict security audits for a skill directory.

    Performs path containment validation for `skill_path`, runs structural diagnostics, and when `level` is `"strict"` runs additional validation gates (security gate, family benchmark validation and OpenClaw guard). Populates `result.data` with subprocess outputs under keys `"diagnostics"`, `"security_gate"`, `"family_benchmarks"` and `"openclaw_guard"` as applicable, and appends `ErrorObject`s to `result.errors` when validations fail.

    Parameters:
        repo_root (Path): Repository root against which `skill_path` is resolved.
        skill_path (str): Repository-relative path to the skill directory to audit.
        level (str): Validation level; `"compat"` runs structural diagnostics only, `"strict"` also runs security and benchmark guards.

    Returns:
        CallResult: Result with `status` set to `"success"` when diagnostics pass (and all strict checks pass if requested), or `"error"` with `errors` containing one or more `ErrorObject`s. Possible error codes include `ERR_PATH_TRAVERSAL` and `ERR_VALIDATION`.
    """
    result = CallResult()
    validation_args = [skill_path]
    if level != "compat":
        validation_args.extend(["--level", level])
    result.data["validation_commands"] = [_skills_validation_command("audit", *validation_args)]

    _, path_error = _validate_repo_relative_skill_path(repo_root, skill_path)
    if path_error:
        return path_error

    audit_target, audit_target_path = _normalize_skill_target_path(skill_path)

    python = _get_python_command(["pyyaml", "jsonschema"])

    diag_cmd = python + ["Infrastructure/scripts/lifecycle-and-sync/diagnose_skill.py", skill_path]
    audit_env = _subprocess_env_with_uv_cache()

    diag_proc = subprocess.run(diag_cmd, cwd=str(repo_root), capture_output=True, text=True, env=audit_env)
    result.data["diagnostics"] = {"exit_code": diag_proc.returncode, "stdout": diag_proc.stdout, "stderr": diag_proc.stderr}

    is_skill_factory_system_overlay = audit_target_path in {
        "skills-system/skill-creator",
        "skills-system/skill-installer",
    }

    if level == "strict" and is_skill_factory_system_overlay:
        overlay_cmd = python + ["Infrastructure/scripts/validation-and-linting/check_skill_factory_system_overlays.py"]
        overlay_proc = subprocess.run(overlay_cmd, cwd=str(repo_root), capture_output=True, text=True, env=audit_env)
        result.data["system_overlay"] = {"exit_code": overlay_proc.returncode, "stdout": overlay_proc.stdout, "stderr": overlay_proc.stderr}
        if overlay_proc.returncode != 0:
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Skill Factory system overlay validation failed."))
            return result

        family_cmd = python + ["Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_benchmarks.py", "--skill", audit_target_path]
        family_proc = subprocess.run(family_cmd, cwd=str(repo_root), capture_output=True, text=True, env=audit_env)
        result.data["family_benchmarks"] = {"exit_code": family_proc.returncode, "stdout": family_proc.stdout, "stderr": family_proc.stderr}
        if family_proc.returncode != 0:
            summary = _summarize_family_benchmark_failure(family_proc.stdout, family_proc.stderr)
            message = "Family benchmarks validation failed."
            if summary:
                message = f"{message} First failures: {summary}"
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_VALIDATION", message=message))
            return result

        result.data["security_gate"] = {
            "exit_code": 0,
            "stdout": "skipped: preserved Codex .system SKILL.md body; local strict contract is enforced through attached Skill Factory references and system overlay validators\n",
            "stderr": "",
        }
        result.data["openclaw_guard"] = {
            "exit_code": 0,
            "stdout": "skipped: preserved Codex .system SKILL.md body; run overlay/family validators for local Skill Factory additions\n",
            "stderr": "",
        }
    elif level == "strict":
        # Security gate (skill_gate.py)
        gate_script = _resolve_skill_builder_script(repo_root, "skill_gate")
        gate_cmd = python + [gate_script, audit_target_path, "--require-security-evals", "--pi-high-fail", "--require-fail-fast"]
        gate_proc = subprocess.run(gate_cmd, cwd=str(repo_root), capture_output=True, text=True, env=audit_env)
        result.data["security_gate"] = {"exit_code": gate_proc.returncode, "stdout": gate_proc.stdout, "stderr": gate_proc.stderr}
        if gate_proc.returncode != 0:
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Security gate failed."))
            return result

        # Family benchmarks validation
        family_cmd = python + ["Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_benchmarks.py", "--skill", audit_target_path]
        family_proc = subprocess.run(family_cmd, cwd=str(repo_root), capture_output=True, text=True, env=audit_env)
        result.data["family_benchmarks"] = {"exit_code": family_proc.returncode, "stdout": family_proc.stdout, "stderr": family_proc.stderr}
        if family_proc.returncode != 0:
            summary = _summarize_family_benchmark_failure(family_proc.stdout, family_proc.stderr)
            message = "Family benchmarks validation failed."
            if summary:
                message = f"{message} First failures: {summary}"
            quoted_skill_path = shlex.quote(audit_target_path)

            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_VALIDATION",
                message=message,
                fix_suggestion=(
                    "Inspect data.family_benchmarks for full output, or run: "
                    f"mise exec -- uv run --python 3.12 --with pyyaml --with jsonschema python Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_benchmarks.py --skill {quoted_skill_path} --format text"
                ),
            ))
            return result

        # OpenClaw skill guard
        openclaw_script = _resolve_skill_builder_script(repo_root, "openclaw_skill_guard")
        openclaw_cmd = python + [openclaw_script, audit_target_path, "--mode", "both", "--format", "text"]
        openclaw_proc = subprocess.run(openclaw_cmd, cwd=str(repo_root), capture_output=True, text=True, env=audit_env)
        result.data["openclaw_guard"] = {"exit_code": openclaw_proc.returncode, "stdout": openclaw_proc.stdout, "stderr": openclaw_proc.stderr}
        if openclaw_proc.returncode != 0:
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_VALIDATION", message="OpenClaw guard validation failed."))
            return result

    if diag_proc.returncode == 0:
        result.status = "success"
    else:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message="Structural diagnostics failed. Skill directory not found or invalid.",
            fix_suggestion=f"Ensure '{skill_path}' exists and contains a SKILL.md file."
        ))

    return result


def validate_skill_gate(repo_root: Path, skill_path: str) -> CallResult:
    """Run the canonical skill gate as a first-class validation command."""
    _, path_error = _validate_repo_relative_skill_path(repo_root, skill_path)
    if path_error:
        return path_error

    audit_target, audit_target_path = _normalize_skill_target_path(skill_path)
    python = _get_python_command(["pyyaml", "jsonschema"])
    gate_script = _resolve_skill_builder_script(repo_root, "skill_gate")
    gate_cmd = python + [
        gate_script,
        audit_target_path,
        "--require-security-evals",
        "--pi-high-fail",
        "--require-fail-fast",
    ]
    result = _run_validation_command(
        repo_root,
        gate_cmd,
        "skill_gate",
        "Skill gate validation failed.",
        fix_suggestion=(
            "Inspect data.skill_gate for full output, or rerun the command shown there "
            f"against {shlex.quote(audit_target_path)}."
        ),
    )
    result.data["validation_commands"] = [_skills_validation_command("validate-skill-gate", skill_path)]
    return result


def validate_openai_skill_format(repo_root: Path, skill_path: str, mode: str = "strict") -> CallResult:
    """Run the canonical OpenAI skill format wrapper as a first-class validation command."""
    _, path_error = _validate_repo_relative_skill_path(repo_root, skill_path)
    if path_error:
        return path_error

    _, audit_target_path = _normalize_skill_target_path(skill_path)
    command = [
        "bash",
        "Infrastructure/scripts/validation-and-linting/lint_openai_skill_format.sh",
        "--mode",
        mode,
        audit_target_path,
    ]
    result = _run_validation_command(
        repo_root,
        command,
        "openai_skill_format",
        "OpenAI skill format validation failed.",
        fix_suggestion=(
            "Inspect data.openai_skill_format for full output, or rerun the command shown there "
            f"against {shlex.quote(audit_target_path)}."
        ),
    )
    result.data["validation_commands"] = [
        _skills_validation_command("validate-openai-format", skill_path, "--mode", mode)
    ]
    return result


def external_review_skill(
    repo_root: Path,
    skill_path: str,
    *,
    audit_level: str = "strict",
    skip_plugin_eval: bool = False,
    skip_tessl: bool = False,
    skip_tessl_review: bool = False,
    include_snyk: bool = False,
    timeout_seconds: int = 180,
    report_path: Optional[str] = None,
    dashboard: bool = False,
    dashboard_path: Optional[str] = None,
) -> CallResult:
    """Run the local-only second-review lane for one skill.

    This command intentionally never publishes or registers a skill. Tessl is
    used only as an installed local CLI, never through npx. Tessl describes
    ``skill review`` as a local terminal review for private and work-in-progress
    skills, so it is part of the default second-review lane.
    """
    result = CallResult()
    result.status = "success"

    _, path_error = _validate_repo_relative_skill_path(repo_root, skill_path)
    if path_error:
        return path_error

    audit_target, audit_target_path = _normalize_skill_target_path(skill_path)
    target_abs = (repo_root / audit_target).resolve()
    if not target_abs.is_dir() or not (target_abs / "SKILL.md").is_file():
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message="Skill path must resolve to a directory containing SKILL.md.",
            fix_suggestion=f"Check the path and rerun against a canonical skill directory: {audit_target_path}",
        ))
        return result

    result.data["policy"] = {
        "mode": "local_internal_only",
        "no_publish": True,
        "no_registry_upload": True,
        "uses_npx": False,
        "publish_policy": "never publish, register, upload, or invoke npx from this lane",
        "tessl_review_default": "enabled_local_cli",
        "tessl_review_privacy_basis": "Tessl docs: Review locally from your machine; stays local; results are only visible to you.",
        "primary_gate": "local_eval_ask_audit",
        "external_quality_judge": "tessl_local_review",
        "tessl_review_min_score": TESSL_REVIEW_MIN_SCORE,
        "tessl_review_target_score": TESSL_REVIEW_TARGET_SCORE,
        "tessl_review_threshold_policy": (
            f"Tessl review must return reviewScore >= {TESSL_REVIEW_MIN_SCORE}; "
            f"{TESSL_REVIEW_TARGET_SCORE}+ remains the improvement target."
        ),
        "tessl_staging_root": f"{os.path.join(tempfile.gettempdir(), 'ask-tessl-reviews')}/<skill-path>-<sha12>",
        "tessl_project_marker": "tessl.json",
        "tessl_evidence_retention": "stable tmp wrapper is intentionally left for inspection and copied-input evidence",
        "tessl_lint_role": "stable_plugin_packaging_shape_check",
        "tessl_lint_shape": (
            "Tessl plugin lint expects a .tessl-plugin/plugin.json package. Canonical repo skills are "
            f"SKILL.md-first, so this command builds a stable local plugin wrapper under {tempfile.gettempdir()} before linting."
        ),
        "tessl_review_role": "local_best_practice_content_review",
        "plugin_eval_role": "budget_and_ergonomics_guardrail",
        "plugin_eval_min_acceptable_grade": PLUGIN_EVAL_MIN_ACCEPTABLE_GRADE,
        "plugin_eval_warning_policy": (
            "Plugin Eval warnings are visible follow-up work, but they are not release blockers when "
            "there are zero Plugin Eval failures, the grade is B+ or better, and local/Tessl gates pass."
        ),
        "snyk_role": "opt_in_local_dependency_security_screening",
        "snyk_default": "disabled_until_requested",
        "snyk_release_requirement": "release_required_for_manifest_backed_candidates",
        "snyk_when_to_use": [
            "when a skill or plugin candidate has dependency manifests such as package.json, pyproject.toml, requirements.txt, Gemfile, go.mod, or lockfiles",
            "when claiming release readiness for a manifest-backed skill or plugin package",
            "when dependency files, installer scripts, generated package surfaces, or plugin runtime dependencies changed",
            "when matching the CircleCI/Snyk security screening lane locally before or after CI",
            "when the user explicitly asks for Snyk, dependency vulnerability screening, or external security advisory evidence",
        ],
        "snyk_when_not_to_use": [
            "pure SKILL.md-first instruction-only candidates with no supported dependency manifest, unless the user explicitly asks",
            "routine local iteration where external networked security analysis is not needed",
        ],
        "snyk_privacy_basis": (
            "Snyk CLI security analysis may contact Snyk services. It is never run by default in this "
            "local-first review lane; pass --include-snyk when external Snyk advisory analysis is wanted."
        ),
    }
    result.data["review_mode_details"] = {
        "local_evals": {
            "command": "./bin/ask evals run <path> --mode smoke|release --json --robot",
            "role": "dynamic run-trace behavior checks for skill selection, commands, artifacts, and release gates",
        },
        "plugin_eval": {
            "command": "plugin-eval analyze <path> --format markdown",
            "role": "static budget, ergonomics, and reviewability guardrail; not a substitute for local evals",
        },
        "tessl_lint": {
            "command": "tessl plugin lint <stable-plugin-directory>",
            "role": "stable .tessl-plugin/plugin.json package-shape check, not a direct content finding",
            "canonical_source_shape": "SKILL.md-first",
        },
        "tessl_review": {
            "command": f"tessl skill review --json --threshold {TESSL_REVIEW_MIN_SCORE} <stable-skill-directory>",
            "role": "local best-practice/content review for private or work-in-progress skills",
            "minimum_score": TESSL_REVIEW_MIN_SCORE,
            "target_score": TESSL_REVIEW_TARGET_SCORE,
            "publishes": False,
        },
        "snyk": {
            "command": "snyk test --all-projects --detection-depth=6 --severity-threshold=high --json <skill-path>",
            "role": "opt-in local dependency security screening; release-required for manifest-backed candidates",
            "default": "disabled_until_requested",
            "release_required": "manifest-backed candidates",
            "use_when": [
                "candidate has supported dependency manifests",
                "release-readiness is claimed for a manifest-backed package",
                "dependency/runtime package surfaces changed",
                "local evidence must match CircleCI/Snyk screening",
                "user explicitly requests Snyk or dependency vulnerability evidence",
            ],
        },
    }
    result.data["target"] = audit_target_path
    validation_args = [skill_path]
    if audit_level != "strict":
        validation_args.extend(["--audit-level", audit_level])
    if skip_plugin_eval:
        validation_args.append("--skip-plugin-eval")
    if skip_tessl:
        validation_args.append("--skip-tessl")
    if skip_tessl_review:
        validation_args.append("--skip-tessl-review")
    if include_snyk:
        validation_args.append("--include-snyk")
    if timeout_seconds != 180:
        validation_args.extend(["--timeout-seconds", str(timeout_seconds)])
    if report_path:
        validation_args.extend(["--report-path", report_path])
    if dashboard:
        validation_args.append("--dashboard")
    if dashboard_path:
        validation_args.extend(["--dashboard-path", dashboard_path])
    result.data["validation_commands"] = [_skills_validation_command("external-review", *validation_args)]

    audit_result = audit_skill(repo_root, audit_target_path, level=audit_level)
    result.data["ask_audit"] = {
        "status": audit_result.status,
        "data": audit_result.data,
        "errors": [getattr(error, "__dict__", error) for error in audit_result.errors],
    }
    if audit_result.status != "success":
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message="Internal ask skill audit failed during external-review lane.",
            fix_suggestion="Inspect data.ask_audit for the exact failing gate.",
        ))

    if not skip_plugin_eval:
        plugin_eval_bin = shutil.which("plugin-eval")
        if not plugin_eval_bin:
            result.status = "error"
            result.data["plugin_eval"] = {"status": "blocked_missing_binary", "command": "plugin-eval analyze"}
            result.errors.append(ErrorObject(
                code="ERR_DEPENDENCY",
                message="plugin-eval is not installed or not on PATH.",
                fix_suggestion="Install or expose plugin-eval, then rerun this local-only review lane.",
            ))
        else:
            command = [plugin_eval_bin, "analyze", audit_target_path, "--format", "markdown"]
            try:
                proc = _run_captured_tool(repo_root=repo_root, command=command, timeout_seconds=timeout_seconds)
                payload = _completed_process_payload(proc)
                payload["status"] = "success" if proc.returncode == 0 else "error"
                plugin_summary = _parse_plugin_eval(payload.get("stdout", ""), payload["status"])
                payload["summary"] = plugin_summary
                result.data["plugin_eval"] = payload
                if proc.returncode != 0:
                    result.status = "error"
                    result.errors.append(ErrorObject(
                        code="ERR_VALIDATION",
                        message="plugin-eval analysis failed during external-review lane.",
                        fix_suggestion="Inspect data.plugin_eval for full output.",
                    ))
                elif plugin_summary.get("blocking_fail_count", plugin_summary.get("fail_count", 0)) or not plugin_summary.get("grade_acceptable", False):
                    result.status = "error"
                    result.errors.append(ErrorObject(
                        code="ERR_VALIDATION",
                        message=(
                            "Plugin Eval did not meet the local acceptance floor "
                            f"({PLUGIN_EVAL_MIN_ACCEPTABLE_GRADE} with zero failures)."
                        ),
                        fix_suggestion="Inspect data.plugin_eval.summary for grade, fail count, and follow-up findings.",
                    ))
            except subprocess.TimeoutExpired:
                result.status = "error"
                result.data["plugin_eval"] = {"status": "timeout", "command": command, "timeout_seconds": timeout_seconds}
                result.errors.append(ErrorObject(
                    code="ERR_RUNTIME",
                    message=f"plugin-eval timed out after {timeout_seconds} seconds.",
                    fix_suggestion="Rerun with a higher --timeout-seconds value if the target is intentionally large.",
                ))
    else:
        result.data["plugin_eval"] = {"status": "skipped"}

    if not skip_tessl:
        tessl_bin = shutil.which("tessl")
        if not tessl_bin:
            result.status = "error"
            result.data["tessl_lint"] = {"status": "blocked_missing_binary", "command": "tessl plugin lint"}
            result.errors.append(ErrorObject(
                code="ERR_DEPENDENCY",
                message="Tessl CLI is not installed or not on PATH; Tessl local lint in the Second-Review Lane could not run.",
                fix_suggestion="Install Tessl as a local machine tool and rerun. This command will not invoke npx or publish anything.",
            ))
        else:
            tessl_tmp_path = _stable_tessl_review_root(audit_target_path)
            try:
                staging_root, plugin_info = _write_tessl_plugin_wrapper(repo_root, audit_target_path, tessl_tmp_path)
            except ValueError as exc:
                result.status = "error"
                result.data["tessl_plugin"] = {"status": "blocked_validation", "message": str(exc)}
                result.errors.append(ErrorObject(
                    code="ERR_VALIDATION",
                    message=str(exc),
                    fix_suggestion="Replace symlinked skill review inputs with regular files or directories before Tessl staging.",
                ))
                return result
            tessl_env: dict[str, str] = {}
            result.data["tessl_plugin"] = {
                **plugin_info,
                "mode": "stable_tmp_wrapper",
                "reason": (
                    "Tessl plugin lint validates .tessl-plugin/plugin.json packages. Canonical repo skills remain "
                    "SKILL.md-first, so this command stages a local plugin-shaped wrapper under /tmp."
                ),
                "auth_home": "process_home",
                "support_refs_included": True,
            }

            lint_command = [tessl_bin, "plugin", "lint", str(staging_root)]
            try:
                lint_proc = _run_captured_tool(
                    repo_root=repo_root,
                    command=lint_command,
                    timeout_seconds=timeout_seconds,
                    env_overrides=tessl_env,
                )
                lint_payload = _completed_process_payload(lint_proc)
                lint_payload["status"] = "success" if lint_proc.returncode == 0 else "error"
                result.data["tessl_lint"] = lint_payload
                if lint_proc.returncode != 0:
                    result.status = "error"
                    result.errors.append(ErrorObject(
                        code="ERR_VALIDATION",
                        message="Tessl skill lint failed during local-only external review.",
                        fix_suggestion="Inspect data.tessl_lint for Tessl's validation output.",
                    ))
            except subprocess.TimeoutExpired:
                result.status = "error"
                result.data["tessl_lint"] = {"status": "timeout", "command": lint_command, "timeout_seconds": timeout_seconds}
                result.errors.append(ErrorObject(
                    code="ERR_RUNTIME",
                    message=f"Tessl skill lint timed out after {timeout_seconds} seconds.",
                    fix_suggestion="Check the local Tessl installation and rerun once it responds normally.",
                ))

            if not skip_tessl_review:
                review_command = [
                    tessl_bin,
                    "skill",
                    "review",
                    "--json",
                    "--threshold",
                    str(TESSL_REVIEW_MIN_SCORE),
                    plugin_info["review_path"],
                ]
                try:
                    review_proc = _run_captured_tool(
                        repo_root=repo_root,
                        command=review_command,
                        timeout_seconds=timeout_seconds,
                        env_overrides=tessl_env,
                    )
                    review_payload = _completed_process_payload(review_proc)
                    review_payload["status"] = "success" if review_proc.returncode == 0 else "error"
                    review_summary = _parse_tessl_review_output(review_payload.get("stdout", ""), review_payload["status"])
                    review_payload["summary"] = review_summary
                    review_payload["minimum_score"] = TESSL_REVIEW_MIN_SCORE
                    review_payload["target_score"] = TESSL_REVIEW_TARGET_SCORE
                    result.data["tessl_review"] = review_payload
                    if review_proc.returncode != 0:
                        result.status = "error"
                        result.errors.append(ErrorObject(
                            code="ERR_VALIDATION",
                            message=f"Tessl skill review did not meet the >= {TESSL_REVIEW_MIN_SCORE} threshold.",
                            fix_suggestion="Inspect data.tessl_review for full output and the staged wrapper path.",
                        ))
                except subprocess.TimeoutExpired:
                    result.status = "error"
                    result.data["tessl_review"] = {"status": "timeout", "command": review_command, "timeout_seconds": timeout_seconds}
                    result.errors.append(ErrorObject(
                        code="ERR_RUNTIME",
                        message=f"Tessl skill review timed out after {timeout_seconds} seconds.",
                        fix_suggestion="Check the local Tessl installation and rerun once it responds normally.",
                    ))
            else:
                result.data["tessl_review"] = {
                    "status": "skipped",
                    "reason": "Skipped by --skip-tessl-review.",
                    "minimum_score": TESSL_REVIEW_MIN_SCORE,
                    "target_score": TESSL_REVIEW_TARGET_SCORE,
                }
    else:
        result.data["tessl_lint"] = {"status": "skipped"}
        result.data["tessl_review"] = {
            "status": "skipped",
            "minimum_score": TESSL_REVIEW_MIN_SCORE,
            "target_score": TESSL_REVIEW_TARGET_SCORE,
        }

    if include_snyk:
        snyk_bin = shutil.which("snyk")
        if not snyk_bin:
            result.status = "error"
            result.data["snyk"] = {
                "status": "blocked_missing_binary",
                "command": "snyk test --all-projects --detection-depth=6 --severity-threshold=high --json <skill-path>",
            }
            result.errors.append(ErrorObject(
                code="ERR_DEPENDENCY",
                message="Snyk CLI is not installed or not on PATH.",
                fix_suggestion="Install or expose the Snyk CLI, authenticate it if required, then rerun with --include-snyk.",
            ))
        else:
            snyk_command = [
                snyk_bin,
                "test",
                "--all-projects",
                "--detection-depth=6",
                "--severity-threshold=high",
                "--json",
                audit_target_path,
            ]
            try:
                snyk_proc = _run_captured_tool(
                    repo_root=repo_root,
                    command=snyk_command,
                    timeout_seconds=timeout_seconds,
                )
                snyk_payload = _completed_process_payload(snyk_proc)
                snyk_text = f"{snyk_proc.stdout}\n{snyk_proc.stderr}".lower()
                if snyk_proc.returncode == 0:
                    snyk_payload["status"] = "success"
                elif "could not detect supported target files" in snyk_text or "no supported files" in snyk_text:
                    snyk_payload["status"] = "not_applicable"
                    snyk_payload["reason"] = (
                        "Snyk found no supported dependency manifest under this skill. "
                        "SKILL.md-first skills are still covered by the internal audit, "
                        "security evals, and OpenClaw guard."
                    )
                elif (
                    "use snyk auth" in snyk_text
                    or "not authenticated" in snyk_text
                    or "authentication required" in snyk_text
                    or "snyk_token" in snyk_text
                ):
                    snyk_payload["status"] = "blocked_auth"
                    snyk_payload["reason"] = (
                        "Snyk CLI authentication is unavailable. Run snyk auth locally or provide "
                        "SNYK_TOKEN in CI before rerunning --include-snyk."
                    )
                elif snyk_proc.returncode == 1:
                    snyk_payload["status"] = "advisory"
                else:
                    snyk_payload["status"] = "error"
                result.data["snyk"] = snyk_payload
                if snyk_payload["status"] == "blocked_auth":
                    result.status = "error"
                    result.errors.append(ErrorObject(
                        code="ERR_AUTH",
                        message="Snyk authentication is required for the external security lane.",
                        fix_suggestion="Run snyk auth locally or set SNYK_TOKEN in CI, then rerun with --include-snyk.",
                    ))
                elif snyk_payload["status"] in {"advisory", "error"}:
                    result.status = "error"
                    result.errors.append(ErrorObject(
                        code="ERR_VALIDATION",
                        message="Snyk reported an advisory or failed during the external security lane.",
                        fix_suggestion="Inspect data.snyk for vulnerability details, unsupported-project output, or authentication errors.",
                    ))
            except subprocess.TimeoutExpired:
                result.status = "error"
                result.data["snyk"] = {
                    "status": "timeout",
                    "command": snyk_command,
                    "timeout_seconds": timeout_seconds,
                }
                result.errors.append(ErrorObject(
                    code="ERR_RUNTIME",
                    message=f"Snyk timed out after {timeout_seconds} seconds.",
                    fix_suggestion="Check the local Snyk CLI/auth state and rerun with a higher --timeout-seconds value if needed.",
                ))
    else:
        result.data["snyk"] = {
            "status": "skipped",
            "reason": "Snyk is disabled by default. Use --include-snyk when external Snyk advisory analysis is wanted.",
        }

    report_target: Optional[Path] = None
    if report_path:
        report_target, report_error = _validate_repo_relative_skill_path(repo_root, report_path)
        if report_error:
            return report_error
        assert report_target is not None
        report_target.parent.mkdir(parents=True, exist_ok=True)
        report_payload = {
            "status": result.status,
            "data": result.data,
            "errors": [getattr(error, "__dict__", error) for error in result.errors],
        }
        report_target.write_text(json.dumps(report_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result.data["report_path"] = report_target.relative_to(repo_root.resolve()).as_posix()

    if dashboard:
        if report_target is None:
            default_report = Path("Infrastructure") / "artifacts" / "skill-reviews" / f"{target_abs.name}.json"
            report_target = (repo_root / default_report).resolve()
            report_target.parent.mkdir(parents=True, exist_ok=True)
            report_payload = {
                "status": result.status,
                "data": result.data,
                "errors": [getattr(error, "__dict__", error) for error in result.errors],
            }
            report_target.write_text(json.dumps(report_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            result.data["report_path"] = report_target.relative_to(repo_root.resolve()).as_posix()

        if dashboard_path:
            dashboard_target, dashboard_error = _validate_repo_relative_skill_path(repo_root, dashboard_path)
            if dashboard_error:
                return dashboard_error
            assert dashboard_target is not None
        else:
            dashboard_target = report_target.with_suffix(".html")
        try:
            rendered_dashboard = render_skill_review_dashboard(
                report_path=report_target,
                output_path=dashboard_target,
                repo_root=repo_root,
            )
        except Exception as exc:
            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_RUNTIME",
                message=f"Failed to render local skill review dashboard: {exc}",
                fix_suggestion="Inspect the JSON report and rerun with --dashboard once the report shape is valid.",
            ))
        else:
            dashboard_rel_path = rendered_dashboard.relative_to(repo_root.resolve()).as_posix()
            result.data["dashboard_path"] = dashboard_rel_path
            result.data["dashboard_url"] = dashboard_rel_path

    return result


def validate_skill_boundaries(repo_root: Path, handle: str) -> CallResult:
    """Resolve a handle and expose canonical-versus-projection ownership boundaries."""
    resolved = skills_explain_boundary(repo_root, handle)
    if resolved.status != "success":
        return resolved
    resolved.data["validation_commands"] = [
        _skills_validation_command("validate-boundaries", handle)
    ]
    return resolved


def skills_explain_boundary(repo_root: Path, handle: str) -> CallResult:
    """Return compact SDK source/projection ownership for one skill handle."""
    result = skills_resolve(repo_root, handle=handle)
    if result.status != "success":
        return result

    resolution = result.data.get("resolution", {})
    canonical_path = resolution.get("canonical_skill_path") or resolution.get("source_path")
    projection_risks: list[str] = []
    if canonical_path:
        projection_risks.append("Edit the canonical source path and regenerate or verify projections after changes.")

    boundary = {
        "handle": resolution.get("handle", handle.lstrip("$")),
        "status": "pass",
        "canonical_skill_path": canonical_path,
        "runtime_projection_path": resolution.get("runtime_projection_path"),
        "runtime_visibility": resolution.get("runtime_visibility"),
        "handle_source": resolution.get("handle_source"),
        "projection_mode": resolution.get("projection_mode"),
        "notes": projection_risks,
    }
    result.data = {"boundary_check": boundary}
    return result

def _resolve_canonical_install_dest(repo_root: Path, dest: str) -> tuple[Path, str]:
    """
    Resolve an install destination into an absolute repo path and a canonical repo-relative string.

    Parameters:
        repo_root (Path): Repository root directory against which `dest` is resolved.
        dest (str): User-supplied destination token (e.g. "github" or "backend"); empty values default to "github".

    Returns:
        tuple[Path, str]: A pair where the first element is the absolute resolved destination path inside `repo_root`
        and the second is the normalized repo-relative destination string.

    Raises:
        ValueError: If `dest` is an absolute path, if the resolved destination escapes the repository root,
        or if the repo-relative destination is empty or "." (must include a category directory).
    """
    dest_token = (dest or "Skills/github").strip() or "Skills/github"
    raw_dest = Path(dest_token)
    if raw_dest.is_absolute():
        raise ValueError("Destination must be repo-relative (for example: Skills/github or Skills/backend).")

    resolved_root = repo_root.resolve()
    resolved_dest = (repo_root / raw_dest).resolve()
    try:
        rel_dest = resolved_dest.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("Destination escapes repository root.") from exc

    rel_parts = rel_dest.parts
    if len(rel_parts) == 1:
        rel_dest = Path("Skills") / rel_dest
        resolved_dest = (repo_root / rel_dest).resolve()
        rel_parts = rel_dest.parts
    rel_text = rel_dest.as_posix()
    if len(rel_parts) != 2 or rel_parts[0] != "Skills":
        raise ValueError("Destination must be under Skills/<category>.")
    if resolved_dest.exists() and not resolved_dest.is_dir():
        raise ValueError("Destination must resolve to a directory under repository root.")
    return resolved_dest, rel_text


def _skill_install_intake_decision(repo_root: Path, skill_name: str, target_path: Path) -> dict[str, Any]:
    """
    Analyze existing repository skills for naming/path conflicts and determine installation compatibility.
    
    Scans the canonical catalog for existing skills with similar names or directory names, determines an installation
    outcome based on conflict severity (install_new, keep_separate, needs_human_choice, reject_duplicate),
    and returns a comprehensive intake decision payload with overlapping candidates, pre-install checks,
    compatibility requirements, and post-install gates.
    
    Returns:
        Intake decision dictionary (schema: skill-install-intake.v1) containing outcome determination, matched
        candidates, policy requirements, and operational gates for pre-install validation and post-install promotion.
    """
    normalized_name = skill_name.lower().strip()
    matches: list[dict[str, Any]] = []
    catalog_entries = sorted(
        (
            entry
            for entry in discover_catalog_entries(advanced=True)
            if entry.source_dir.is_relative_to(repo_root)
        ),
        key=lambda entry: entry.source_dir.relative_to(repo_root).as_posix(),
    )
    for entry in catalog_entries:
        skill_dir = entry.source_dir
        skill_md = skill_dir / "SKILL.md"
        try:
            frontmatter = _read_skill_frontmatter_fields(skill_md)
        except OSError:
            frontmatter = {}
        local_name = str(frontmatter.get("name") or entry.name or skill_dir.name)
        local_description = str(frontmatter.get("description") or entry.description or "")
        name_ratio = difflib.SequenceMatcher(None, normalized_name, local_name.lower()).ratio()
        path_ratio = difflib.SequenceMatcher(None, normalized_name, skill_dir.name.lower()).ratio()
        score = max(name_ratio, path_ratio)
        if normalized_name in {local_name.lower(), skill_dir.name.lower()} or score >= 0.72:
            matches.append({
                "name": local_name,
                "path": skill_dir.relative_to(repo_root).as_posix(),
                "description": local_description,
                "similarity": round(score, 3),
            })
    matches.sort(key=lambda item: (-float(item["similarity"]), item["path"]))

    target_exists = target_path.exists()
    if target_exists:
        outcome = "reject_duplicate"
        reason = "target_path_exists"
    elif matches and float(matches[0]["similarity"]) >= 0.86:
        outcome = "needs_human_choice"
        reason = "high_similarity_local_skill"
    elif matches:
        outcome = "keep_separate"
        reason = "nearby_skill_exists_but_not_blocking"
    else:
        outcome = "install_new"
        reason = "no_close_local_match"

    return {
        "schema_version": "skill-install-intake.v1",
        "canonical_term": "External Skill Intake",
        "candidate": skill_name,
        "outcome": outcome,
        "reason": reason,
        "target_exists": target_exists,
        "local_overlap_candidates": matches[:8],
        "allowed_outcomes": [
            "install_new",
            "blend_into_existing",
            "keep_separate",
            "reject_duplicate",
            "needs_human_choice",
        ],
        "pre_install_checks": [
            "inventory existing skills with ./bin/ask skills list --json --robot",
            "search Skills/**, Plugins/**/skills/**, and skills-system/** for overlap",
            "compare intent, trigger wording, scripts/assets, safety boundaries, and closeout contract",
            "return an Intake Decision before writing canonical source",
        ],
        "compatibility_checks": [
            "OpenAI skill format and SKILL.md frontmatter",
            "progressive disclosure shape and required local safety sections",
            "repo path, network, secret, package-manager, and external-tool assumptions",
            "dependency manifest presence for Snyk applicability",
        ],
        "post_install_gates": [
            "./bin/ask skills audit <skill-path> --level strict --json --robot",
            "./bin/ask skills external-review <skill-path> --json --robot",
            "./bin/ask evals run <skill-path> --mode smoke --json --robot once eval cases exist",
            "./bin/ask evals run <skill-path> --mode release --json --robot before promotion or release-readiness claims",
        ],
        "snyk_policy": {
            "required_when": "manifest-backed candidate is promoted or release readiness is claimed",
            "not_applicable_when": "pure SKILL.md-first instruction-only candidate has no supported dependency manifest",
        },
        "promotion_rule": "Do not add a skill handle, route as canonical, blend into an owner skill, or make a Release-Readiness Claim until required gates pass.",
    }


def install_skill(repo_root: Path, url: str, remediate: bool = False, dest: str = "Skills/github", dry_run: bool = False) -> CallResult:
    """
    Install a GitHub-hosted skill into the repository's canonical skill directory.

    Dest is validated and normalised to a repo-relative category (for example "github" or "backend"). In dry-run mode no changes are made and a preview of the planned install is returned. If the installer supports `--validation-level` the command will request `compat` validation; if `--remediate` is requested but unsupported the call returns an error result. After a successful install the workspace projection is synchronised.

    Parameters:
        repo_root (Path): Root path of the repository used to resolve and validate the install destination.
        url (str): URL or repository path of the skill to install (may end with `.git`).
        remediate (bool): Request installer remediation; fails with `ERR_VALIDATION` if the installer does not support `--remediate`.
        dest (str): Repo-relative category directory for installation under Skills/ (must not be absolute or escape the repo).
        dry_run (bool): If true, return a preview without performing any filesystem or network changes.

    Returns:
        CallResult: Result object with `status` set to `"success"` or `"error"`. On success `data` includes at least:
            - `skill_name`: installed skill name,
            - `canonical_dest`: repo-relative destination used,
            - `workspace_sync`: status and logs from the post-install sync.
        On dry-run success `data` includes a preview (`dry_run`, `skill_name`, `target_path`, `url`, `remediate`, `canonical_dest`) and `metadata.next_steps` showing the equivalent install command.
        On error the result contains `errors` with codes such as `ERR_VALIDATION`, `ERR_CONFLICT`, or `ERR_RUNTIME` and a `fix_suggestion`.
    """
    result = CallResult()
    try:
        dest_path, dest_rel = _resolve_canonical_install_dest(repo_root, dest)
    except ValueError as exc:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Invalid install destination '{dest}': {exc}",
                fix_suggestion="Use a category under Skills/ such as 'Skills/github' or shorthand 'github'.",
            )
        )
        return result

    # Parse skill name from URL for preview
    skill_name = url.split("/")[-1].replace(".git", "") if "/" in url else url
    target_path = dest_path / skill_name
    intake_decision = _skill_install_intake_decision(repo_root, skill_name, target_path)

    # Handle dry-run first (before any side-effect checks)
    if dry_run:
        # Preview mode: show what would happen without making changes
        result.status = "success"
        result.data["dry_run"] = True
        result.data["skill_name"] = skill_name
        # Handle absolute paths gracefully - only relativize if within repo
        try:
            display_path = str(target_path.relative_to(repo_root))
        except ValueError:
            display_path = str(target_path)
        result.data["target_path"] = display_path
        result.data["url"] = url
        result.data["remediate"] = remediate
        result.data["canonical_dest"] = dest_rel
        result.data["intake_decision"] = intake_decision
        result.data["readiness_policy"] = {
            "full_evals_required_before_promotion": True,
            "external_skill_install_is_intake_not_copy": True,
            "promotion_rule": intake_decision["promotion_rule"],
        }
        validation_args = [url, "--dest", dest_rel]
        if remediate:
            validation_args.append("--remediate")
        validation_args.append("--dry-run")
        result.data["validation_commands"] = [_skills_validation_command("install", *validation_args)]
        result.metadata["next_steps"] = [
            "Review data.intake_decision.outcome before writing canonical source.",
            f"ask skills install {url} --dest {dest_rel}" + (" --remediate" if remediate else ""),
        ]
        return result

    # Check for existing skill conflict (only for actual installation)
    if intake_decision["outcome"] in {"reject_duplicate", "needs_human_choice"}:
        # Handle absolute paths gracefully - only relativize if within repo
        try:
            display_path = str(target_path.relative_to(repo_root))
        except ValueError:
            display_path = str(target_path)
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_CONFLICT" if intake_decision["outcome"] == "reject_duplicate" else "ERR_REQUIRES_HUMAN_CHOICE",
            message=(
                f"Skill '{skill_name}' already exists at '{display_path}'."
                if intake_decision["outcome"] == "reject_duplicate"
                else f"Skill '{skill_name}' is similar to existing local skills; choose install_new, blend_into_existing, keep_separate, or reject_duplicate before writing."
            ),
            fix_suggestion=(
                "Remove the existing skill or choose a different destination with --dest."
                if intake_decision["outcome"] == "reject_duplicate"
                else "Inspect data.intake_decision.local_overlap_candidates and rerun only after the ownership decision is explicit."
            )
        ))
        result.data["skill_name"] = skill_name
        result.data["canonical_dest"] = dest_rel
        result.data["existing_path"] = display_path
        result.data["intake_decision"] = intake_decision
        return result

    python_cmd = _get_python_command(["pyyaml"])
    installer_script = _resolve_skill_installer_script(repo_root)
    supported_flags = _install_script_supported_flags(repo_root, python_cmd)
    cmd = python_cmd + [
        installer_script,
        "--url", url,
        "--dest", str(dest_path),
    ]
    if "--validation-level" in supported_flags:
        cmd.extend(["--validation-level", "compat"])
        result.data["validation_level"] = "compat"
    else:
        result.data["validation_level"] = "compat_skipped_unsupported"

    if remediate:
        if "--remediate" in supported_flags:
            cmd.append("--remediate")
        else:
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message="Installed skill installer does not support --remediate.",
                    fix_suggestion=(
                        "Re-run without --remediate, or update the installer to a version "
                        "that supports remediation."
                    ),
                )
            )
            return result

    process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
    result.data["raw_output"] = process.stdout
    result.data["raw_error"] = process.stderr
    result.data["canonical_dest"] = dest_rel
    result.data["intake_decision"] = intake_decision

    if process.returncode == 0:
        result.status = "success"
        match = re.search(r"Installed (.*?) to", process.stdout)
        installed_name = match.group(1) if match else skill_name
        result.data["skill_name"] = installed_name

        # Keep repo projections current so canonical install and loader symlinks
        # remain in lockstep.
        sync_result = sync_skills(repo_root, scope="workspace", dry_run=False)
        result.data["workspace_sync"] = {
            "status": sync_result.status,
            "logs": sync_result.data.get("logs", []),
        }
        if sync_result.status != "success":
            sync_error = sync_result.errors[0].message if sync_result.errors else "Unknown sync failure."
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_RUNTIME",
                    message=f"Skill installed to '{dest_rel}', but workspace sync failed: {sync_error}",
                    fix_suggestion="Run `ask skills sync --scope workspace` after resolving the sync error.",
                )
            )
            return result
        installed_path = f"{dest_rel}/{installed_name}"
        result.data["readiness_policy"] = {
            "full_evals_required_before_promotion": True,
            "external_skill_install_is_intake_not_copy": True,
            "promotion_rule": intake_decision["promotion_rule"],
            "post_install_gates": [
                f"ask skills audit {installed_path} --level strict --json --robot",
                f"ask skills external-review {installed_path} --json --robot",
                f"ask evals run {installed_path} --mode smoke --json --robot once eval cases exist",
                f"ask evals run {installed_path} --mode release --json --robot before promotion or release-readiness claims",
            ],
        }
        result.metadata["next_steps"] = result.data["readiness_policy"]["post_install_gates"]
    else:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=process.stderr.strip() or "Installation failed."))

    return result


def _install_script_supported_flags(repo_root: Path, python_cmd: List[str]) -> set[str]:
    """
    Identify which optional flags the installer script advertises in its help text.

    Parameters:
        repo_root (Path): Repository root used as the subprocess working directory.
        python_cmd (List[str]): Tokenised Python command to invoke the script (e.g. ["python3"] or a wrapper tool chain).

    Returns:
        supported (set[str]): Set containing any of `"--validation-level"` and `"--remediate"` that appear in the script's help output.
    """
    installer_script = _resolve_skill_installer_script(repo_root)
    help_cmd = python_cmd + [
        installer_script,
        "--help",
    ]
    try:
        process = subprocess.run(help_cmd, cwd=str(repo_root), capture_output=True, text=True)
    except OSError:
        return set()

    help_text = "\n".join([process.stdout or "", process.stderr or ""])
    supported = set()
    for flag in ("--validation-level", "--remediate"):
        if flag in help_text:
            supported.add(flag)
    return supported


def fold_skills(repo_root: Path, source: str, target: str, sensitivity: float = 0.2) -> CallResult:
    """
    Determine whether the source skill should be folded into the target skill based on description similarity.

    Parameters:
        repo_root (Path): Repository root used to load builder modules and the skill catalog.
        source (str): Name or trailing path segment identifying the source skill to evaluate.
        target (str): Name or trailing path segment identifying the target skill to compare against.
        sensitivity (float): Confidence threshold in the range 0-1 above which overlap is considered high (default 0.2).

    Returns:
        CallResult: Result object containing:
            - On success: `status == "success"`, `data["overlap_score"]` (float), and `data["recommendation"]`
              set to either a "KEEP" message or a "KEEP: No significant overlap found." message.
            - On redundancy detection: `status == "error"`, an `ERR_REDUNDANCY` error with a `fix_suggestion`,
              and `data["overlap_score"]`, `data["rationale"]`, and `data["recommendation"]` describing the overlap.
            - On missing dependencies: `status == "error"` with `ERR_DEPENDENCY`.
            - On missing skills: `status == "error"` with `ERR_VALIDATION`.
            - `data["rationale"]`, when present, contains the router's textual rationale for the match.
    """
    result = CallResult()
    validation_args = [source, target]
    if sensitivity != 0.2:
        validation_args.extend(["--sensitivity", str(sensitivity)])
    result.data["validation_commands"] = [_skills_validation_command("fold", *validation_args)]

    builder_catalog = _load_builder_module(repo_root, "skill_catalog")
    router_mod = _load_builder_module(repo_root, "skill_router")

    if not builder_catalog or not router_mod:
        result.status = "error"
        result.data["dependency_status"] = {
            "skill_catalog": "available" if builder_catalog else "missing",
            "skill_router": "available" if router_mod else "missing",
        }
        result.errors.append(ErrorObject(
            code="ERR_DEPENDENCY",
            message="Skill router or builder catalog not available.",
            fix_suggestion="Restore the Skill Factory script namespace or use skills route for current routing checks.",
        ))
        return result

    try:
        catalog = builder_catalog.load_catalog(repo_root)
    except Exception as exc:  # noqa: BLE001 - convert optional Skill Factory loader failures into ASK errors.
        result.status = "error"
        result.data["dependency_status"] = {
            "skill_catalog": "load_failed",
            "skill_router": "available",
            "error": str(exc),
        }
        result.errors.append(ErrorObject(
            code="ERR_DEPENDENCY",
            message="Skill router or builder catalog not available.",
            fix_suggestion="Inspect data.dependency_status.error or use skills route for current routing checks.",
        ))
        return result
    source_skill = next((s for s in catalog.skills if s.name == source or str(s.skill_path).endswith(source)), None)
    target_skill = next((s for s in catalog.skills if s.name == target or str(s.skill_path).endswith(target)), None)

    if not source_skill or not target_skill:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Source or target skill not found."))
        return result

    # Run router check
    query = source_skill.description
    candidates, _ = router_mod.route(query, [target_skill], top_k=1)

    if candidates:
        match = candidates[0]
        result.data["overlap_score"] = match.confidence
        result.data["rationale"] = match.rationale

        if match.confidence >= sensitivity:
            # High overlap - emit CONFLICT to indicate redundancy issue
            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_REDUNDANCY",
                message=f"High overlap ({int(match.confidence * 100)}%) detected between '{source}' and '{target}'.",
                fix_suggestion=f"Consider folding '{source}' into '{target}' to reduce redundancy."
            ))
            result.data["recommendation"] = f"FOLD: High overlap ({int(match.confidence * 100)}%) detected."
        else:
            result.status = "success"
            result.data["recommendation"] = f"KEEP: Low overlap ({int(match.confidence * 100)}%) detected."
    else:
        result.status = "success"
        result.data["overlap_score"] = 0
        result.data["recommendation"] = "KEEP: No significant overlap found."

    return result


def _scope_rank_for_path(repo_root: Path, skill_path: str) -> int:
    scope = classify_skill_scope(repo_root / skill_path, repo_root=repo_root)
    max_precedence = max(USER_SKILL_SCOPE_PRECEDENCE.values())
    scope_precedence = USER_SKILL_SCOPE_PRECEDENCE.get(scope)
    if scope_precedence is not None:
        return max_precedence - scope_precedence + 1
    if scope == "system":
        return max_precedence + 1
    root = skill_path.split("/", 1)[0].strip()
    if root in REPO_SCAN_ROOTS:
        return max_precedence + REPO_SCAN_ROOTS.index(root) + 2
    return max_precedence + len(REPO_SCAN_ROOTS) + 2


def _canonical_repo_relative_path(path: str) -> str:
    parts = Path(path).parts
    if parts and parts[0] == "plugins":
        return Path("Plugins", *parts[1:]).as_posix()
    return path


def _exact_handle_sort_key(candidate: EligibleCandidate) -> tuple[int, int, str]:
    path = candidate.path.removeprefix("./")
    bridge_rank = 1 if path.startswith(".agents/") else 0
    return bridge_rank, candidate.scope_rank, canonical_sort_key(candidate)


def route_skills(
    repo_root: Path,
    request: str,
    top_k: int = 3,
    considered_limit: int = 20,
) -> CallResult:
    """
    Route a textual request to candidate skills and produce a decision payload.

    Builds a set of eligible skills from the repository, ranks the best matches for the trimmed request using the skill router, evaluates catalog parity, and returns a CallResult containing the routing decision and related metadata.

    Parameters:
        repo_root (Path): Repository root used to discover canonical skill entries.
        request (str): Textual request to route; must be non-empty after trimming.
        top_k (int): Maximum number of top-ranked skills to return; values less than 1 are coerced to 1.
        considered_limit (int): Maximum number of candidate skills to consider when routing; values less than 1 are coerced to 1.

    Returns:
        CallResult: Result object whose `data` includes:
            - `decision`: decision payload produced by the routing logic.
            - `catalog_parity`: parity information comparing catalog and routing considerations.
            - `policy_identity`: policy identity used for the decision.
            - `decision_status`: the decision's status string.
        On error the CallResult will have `status == "error"` and `errors` will include one or more ErrorObject entries describing validation, dependency or runtime issues.
    """
    result = CallResult()
    query = request.strip()
    if not query:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Request cannot be empty for skills route.",
                fix_suggestion="Provide request text, for example: ask skills route \"review this PR\"",
            )
        )
        return result

    default_candidates: list[EligibleCandidate] = []
    default_candidate_ids: set[str] = set()
    for entry in discover_catalog_entries():
        if not entry.source_dir.is_relative_to(repo_root):
            continue
        rel_path = _canonical_repo_relative_path(entry.source_dir.relative_to(repo_root).as_posix())
        candidate = EligibleCandidate(
            name=entry.name,
            path=rel_path,
            description=entry.description,
            scope_rank=_scope_rank_for_path(repo_root, rel_path),
        )
        default_candidates.append(candidate)
        default_candidate_ids.add(candidate_id(candidate))

    advanced_only_candidates: list[EligibleCandidate] = []
    for entry in discover_catalog_entries(advanced=True):
        if not entry.source_dir.is_relative_to(repo_root):
            continue
        rel_path = _canonical_repo_relative_path(entry.source_dir.relative_to(repo_root).as_posix())
        candidate = EligibleCandidate(
            name=entry.name,
            path=rel_path,
            description=entry.description,
            scope_rank=_scope_rank_for_path(repo_root, rel_path),
        )
        if candidate_id(candidate) in default_candidate_ids:
            continue
        advanced_only_candidates.append(candidate)

    ordered_default_candidates = sorted(default_candidates, key=canonical_sort_key)
    all_candidates = list(ordered_default_candidates)
    all_candidate_ids = {candidate_id(candidate) for candidate in all_candidates}
    for candidate in sorted(advanced_only_candidates, key=canonical_sort_key):
        cid = candidate_id(candidate)
        if cid in all_candidate_ids:
            continue
        all_candidates.append(candidate)
        all_candidate_ids.add(cid)

    normalized_handle_query = query.removeprefix("$").strip().lower()
    if normalized_handle_query and " " not in normalized_handle_query:
        for entry in discover_catalog_entries(advanced=True, source="repo"):
            if entry.name.lower() != normalized_handle_query:
                continue
            if not entry.source_dir.is_relative_to(repo_root):
                continue
            rel_path = _canonical_repo_relative_path(entry.source_dir.relative_to(repo_root).as_posix())
            candidate = EligibleCandidate(
                name=entry.name,
                path=rel_path,
                description=entry.description,
                scope_rank=_scope_rank_for_path(repo_root, rel_path),
            )
            cid = candidate_id(candidate)
            if cid in all_candidate_ids:
                continue
            all_candidates.append(candidate)
            all_candidate_ids.add(cid)

    exact_candidates = [
        candidate
        for candidate in all_candidates
        if candidate.name.lower() == normalized_handle_query
    ]
    exact_candidate = min(exact_candidates, key=_exact_handle_sort_key) if exact_candidates else None
    if exact_candidate is not None and normalized_handle_query and " " not in normalized_handle_query:
        ranked_payload = [
            {
                "skill_name": exact_candidate.name,
                "skill_path": exact_candidate.path,
                "confidence": 1.0,
                "rationale": ["exact SDK skill handle match"],
                "risk_tier": "low",
            }
        ]
        catalog_parity = compute_catalog_parity(repo_root, strict=False)
        decision = build_decision_payload(
            request=query,
            policy_identity=get_policy_identity(),
            considered_limit=len(all_candidates),
            top_k=1,
            eligible_candidates=all_candidates,
            ranked_candidates=ranked_payload,
            uncertainty_reasons=[],
            catalog_parity_ok=not bool(catalog_parity.get("drift_detected")),
        )
        result.data["decision"] = decision
        result.data["catalog_parity"] = catalog_parity
        result.data["policy_identity"] = decision["policy_identity"]
        result.data["decision_status"] = decision["decision_status"]
        decision["validation_commands"] = [_skills_validation_command("route", query)]
        if decision["decision_status"] == "resolved":
            result.status = "success"
        else:
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=f"skills route returned {decision['decision_status']}",
                    fix_suggestion=decision.get("operator_action"),
                )
            )
        return result

    bounded_limit = max(1, int(considered_limit))
    considered_candidates = ordered_default_candidates[:bounded_limit]
    considered_candidate_ids = {candidate_id(candidate) for candidate in considered_candidates}
    for candidate in sorted(advanced_only_candidates, key=canonical_sort_key):
        cid = candidate_id(candidate)
        if cid in considered_candidate_ids:
            continue
        considered_candidates.append(candidate)
        considered_candidate_ids.add(cid)

    router_mod = _load_builder_module(repo_root, "skill_router")
    if not router_mod:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_DEPENDENCY",
                message="Skill router module is not available.",
                fix_suggestion=(
                    "Ensure Plugins/skill-factory/scripts/skill-builder/skill_router.py "
                    "exists and rerun."
                ),
            )
        )
        return result
    router_skills = [
        _RouterSkill(name=item.name, description=item.description, skill_path=item.path)
        for item in considered_candidates
    ]

    ranked, uncertainty_reasons = router_mod.route(query, router_skills, top_k=max(1, int(top_k)))
    ranked_payload = [
        {
            "skill_name": candidate.skill_name,
            "skill_path": candidate.skill_path,
            "confidence": float(candidate.confidence),
            "rationale": list(candidate.rationale),
            "risk_tier": candidate.risk_tier,
        }
        for candidate in ranked
    ]

    catalog_parity = compute_catalog_parity(
        repo_root,
        strict=False,
    )

    decision = build_decision_payload(
        request=query,
        policy_identity=get_policy_identity(),
        considered_limit=len(considered_candidates),
        top_k=max(1, int(top_k)),
        eligible_candidates=considered_candidates,
        ranked_candidates=ranked_payload,
        uncertainty_reasons=list(uncertainty_reasons),
        catalog_parity_ok=not bool(catalog_parity.get("drift_detected")),
    )
    decision["validation_commands"] = [_skills_validation_command("route", query)]

    decision_status = decision["decision_status"]
    result.data["decision"] = decision
    result.data["catalog_parity"] = catalog_parity
    result.data["policy_identity"] = decision["policy_identity"]
    result.data["decision_status"] = decision_status

    if decision_status == "resolved":
        result.status = "success"
        return result

    failure_class = decision.get("failure_class")
    code = "ERR_VALIDATION"
    if failure_class == "AMBIGUITY_UNRESOLVED":
        code = "ERR_CONFLICT"
    elif failure_class == "DISCOVERY_POLICY_DRIFT":
        code = "ERR_DEPENDENCY"
    elif failure_class == "CATALOG_PARITY_DRIFT":
        code = "ERR_VALIDATION"

    result.status = "error"
    result.errors.append(
        ErrorObject(
            code=code,
            message=f"skills route returned {decision_status}",
            fix_suggestion=decision.get("operator_action"),
        )
    )
    return result


def goal_skills(
    repo_root: Path,
    intent_text: str,
    top_k: int = 3,
    considered_limit: int = 20,
) -> CallResult:
    """
    Builds a goal-oriented decision from an intent by routing the intent to skills and converting the resulting route decision into a goal decision.

    Parameters:
        repo_root (Path): Repository root used to discover and route against skills.
        intent_text (str): Natural-language intent to resolve into a goal decision.
        top_k (int): Maximum number of top candidate skills to return from routing.
        considered_limit (int): Number of skills to consider during routing.

    Returns:
        CallResult: Contains:
            - `data["goal_decision"]` (dict): The constructed goal decision payload.
            - `data["decision_status"]` (str): Final goal decision status.
            - `data["policy_identity"]` (dict): Policy identity associated with the decision.
            - `data["route_decision_status"]` (optional[str]): Status of the underlying route decision.
            On success (`decision_status == "resolved"`) the result.status is `"success"`. On failure the result.status is `"error"` and result.errors includes an ErrorObject with `code="ERR_VALIDATION"` and a `fix_suggestion` when available. If the routing step did not produce a decision payload the result.error contains an ErrorObject with `code="ERR_RUNTIME"`.
    """
    result = CallResult()
    route_result = route_skills(
        repo_root,
        request=intent_text,
        top_k=max(1, int(top_k)),
        considered_limit=max(1, int(considered_limit)),
    )
    route_decision = route_result.data.get("decision") if isinstance(route_result.data, dict) else None
    if not isinstance(route_decision, dict):
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_RUNTIME",
                message="Route decision payload missing while building goal decision.",
                fix_suggestion="Retry `ask skills goal` after restoring route command health.",
            )
        )
        return result

    goal_decision = build_goal_decision(route_decision)
    goal_decision["validation_commands"] = [_skills_validation_command("goal", intent_text)]
    result.data["goal_decision"] = goal_decision
    result.data["decision_status"] = goal_decision["decision_status"]
    result.data["policy_identity"] = goal_decision["policy_identity"]
    result.data["route_decision_status"] = route_decision.get("decision_status")

    if goal_decision["decision_status"] == "resolved":
        result.status = "success"
        return result

    result.status = "error"
    result.errors.append(
        ErrorObject(
            code="ERR_VALIDATION",
            message=f"skills goal returned {goal_decision['decision_status']}",
            fix_suggestion=goal_decision.get("operator_action"),
        )
    )
    return result


def _candidate_handle(candidate: dict[str, Any]) -> str:
    """Return the best SDK skill handle spelling for a routed candidate."""
    name = str(candidate.get("name") or "").strip().lstrip("$")
    if name:
        return name
    path = str(candidate.get("path") or "").strip().rstrip("/")
    if path:
        return Path(path).name
    candidate_id_value = str(candidate.get("candidate_id") or "").strip()
    if candidate_id_value:
        return candidate_id_value.rsplit(":", 1)[-1].strip().lstrip("$")
    return ""


_IMPROVE_STOPWORDS = frozenset({
    "a",
    "an",
    "and",
    "against",
    "at",
    "better",
    "for",
    "make",
    "of",
    "this",
    "the",
    "to",
})

_IMPROVE_HANDLE_HINTS = (
    (
        frozenset({"validation", "blockers", "fix"}),
        "autofix",
        "fallback validation-blocker intent hint",
    ),
    (
        frozenset({"review", "implementation", "spec"}),
        "he-code-review",
        "fallback implementation-review intent hint",
    ),
    (
        frozenset({"monitor", "long", "running", "phase"}),
        "pr-green-sweep",
        "fallback PR sweep and long-running validation intent hint",
    ),
    (
        frozenset({"linear", "backed", "spec"}),
        "cli-spec",
        "fallback spec intent hint",
    ),
)


def _improve_tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 1 and token not in _IMPROVE_STOPWORDS
    }


def _fallback_improvement_candidate(repo_root: Path, goal_text: str) -> dict[str, Any] | None:
    """Select one SDK skill handle when formal goal routing is too ambiguous."""
    request_tokens = _improve_tokens(goal_text)
    if not request_tokens:
        return None
    try:
        handles = [record.to_resolution() for record in build_sdk_skill_records(repo_root_path=repo_root, visibility="advanced")]
    except (OSError, RuntimeError, ValueError, KeyError, TypeError):
        return None
    handle_rows = {
        str(row.get("handle") or "").strip().lower().lstrip("$"): row
        for row in handles
        if isinstance(row, dict) and row.get("handle")
    }
    for required_tokens, hinted_handle, rationale in _IMPROVE_HANDLE_HINTS:
        normalized_hint = hinted_handle.strip().lower().lstrip("$")
        row = handle_rows.get(normalized_hint)
        if required_tokens.issubset(request_tokens) and row:
            return {
                "candidate_id": f"skill:{row.get('handle')}::{row.get('source_path')}",
                "candidate_type": row.get("kind", "skill"),
                "name": row.get("handle"),
                "path": row.get("source_path"),
                "confidence": 0.85,
                "rationale": [
                    rationale,
                    "matched terms=" + ",".join(sorted(required_tokens)),
                ],
                "scope_rank": 2,
            }
    scored: list[tuple[int, str, dict[str, Any], set[str]]] = []
    for row in handles:
        if not isinstance(row, dict):
            continue
        handle = str(row.get("handle") or "")
        searchable = " ".join(
            str(row.get(key) or "")
            for key in ("handle", "owner", "source_path", "description")
        )
        overlap = request_tokens & _improve_tokens(searchable)
        if overlap:
            scored.append((len(overlap), handle, row, overlap))
    if not scored:
        return None
    score, handle, row, overlap = max(scored, key=lambda item: (item[0], -len(item[1]), item[1]))
    normalized_handle = handle.strip().lower().lstrip("$")
    if score < 2 and normalized_handle not in request_tokens:
        return None
    return {
        "candidate_id": f"skill:{row.get('handle')}::{row.get('source_path')}",
        "candidate_type": row.get("kind", "skill"),
        "name": row.get("handle"),
        "path": row.get("source_path"),
        "confidence": round(min(0.95, 0.45 + (score * 0.1)), 2),
        "rationale": [
            "fallback SDK skill description match",
            "matched terms=" + ",".join(sorted(overlap)),
        ],
        "scope_rank": 2,
    }


def _improvement_route_state(route_decision_status: str | None, *, proof_failed: bool = False) -> tuple[str, str]:
    """Return the stable agent-facing route state for a skills improvement result."""
    if proof_failed:
        return "blocked_reachability", "selected capability failed reachability proof"
    if route_decision_status == "resolved":
        return "resolved", "goal routing selected one reachable capability"
    if route_decision_status == "unresolved_ambiguity":
        return "blocked_ambiguity", "goal routing could not select one capability"
    if route_decision_status in {"blocked_policy_drift", "blocked_catalog_parity", "degraded_no_candidates"}:
        return "blocked_dependency", f"goal routing returned {route_decision_status}"
    return "blocked_dependency", "goal routing did not produce a usable decision"


def _proof_missing_workspace_source(proof: dict[str, Any]) -> bool:
    if not isinstance(proof, dict):
        return False
    gates = proof.get("gates")
    if not isinstance(gates, dict):
        return False
    return gates.get("resolver") is False or gates.get("canonical_source_exists") is False


def improve_skills(
    repo_root: Path,
    goal_text: str,
    top_k: int = 3,
    considered_limit: int = 20,
) -> CallResult:
    """Route a user goal into one capability recommendation with proof status."""
    result = CallResult()
    result.metadata["command"] = "skills improve"
    goal_result = goal_skills(
        repo_root,
        intent_text=goal_text,
        top_k=top_k,
        considered_limit=considered_limit,
    )
    goal_decision = goal_result.data.get("goal_decision", {})
    route_decision_status = goal_result.data.get("route_decision_status")
    recommended = goal_decision.get("recommended_candidate")
    initial_route_state, initial_route_state_reason = _improvement_route_state(route_decision_status)

    improvement: dict[str, Any] = {
        "schema_version": "skill-improvement-recommendation.v1",
        "goal": goal_text,
        "status": "resolved" if goal_result.status == "success" and recommended else "blocked",
        "route_state": initial_route_state,
        "route_state_reason": initial_route_state_reason,
        "agent_summary": "",
        "recommended_capability": None,
        "why": [],
        "reachability": {
            "status": "not_checked",
            "proof_status": None,
            "required_gates_passed": None,
            "user_runtime_ready": None,
        },
        "proof": None,
        "alternatives": goal_decision.get("alternative_candidates", []),
        "next_command": None,
        "validation_commands": [_skills_validation_command("goal", goal_text)],
        "goal_decision_status": goal_decision.get("decision_status"),
        "goal_decision": goal_decision,
    }

    fallback_used = False
    fallback_allowed = route_decision_status == "unresolved_ambiguity"
    if not isinstance(recommended, dict) and fallback_allowed:
        recommended = _fallback_improvement_candidate(repo_root, goal_text)
        fallback_used = recommended is not None

    if not isinstance(recommended, dict):
        prompts = goal_decision.get("disambiguation_prompts") or []
        summary = goal_decision.get("operator_action") or "Goal did not resolve to one capability."
        improvement["agent_summary"] = summary
        improvement["disambiguation_prompts"] = prompts
        improvement["next_command"] = _skills_validation_command("goal", goal_text)
        improvement["validation_commands"] = [improvement["next_command"]]
        result.status = "error"
        result.data["improvement"] = improvement
        result.data["goal_decision"] = goal_decision
        result.errors.extend(goal_result.errors)
        if not result.errors:
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message="skills improve could not resolve one recommended capability.",
                    fix_suggestion=summary,
                )
            )
        return result

    handle = _candidate_handle(recommended)
    proof_result = skills_proof(repo_root, handle=handle) if handle else CallResult(status="error")
    proof = proof_result.data.get("proof", {})
    gates = proof.get("gates", {}) if isinstance(proof, dict) else {}
    required = proof.get("gate_policy", {}).get("required", []) if isinstance(proof, dict) else []
    required_gates_passed = all(bool(gates.get(gate)) for gate in required)
    user_runtime_ready = bool(
        gates.get("user_runtime_ready")
    )
    rationale = recommended.get("rationale") or []
    capability = {
        "handle": handle,
        "name": recommended.get("name"),
        "path": recommended.get("path"),
        "candidate_id": recommended.get("candidate_id"),
        "candidate_type": recommended.get("candidate_type"),
        "confidence": recommended.get("confidence"),
    }

    improvement["recommended_capability"] = capability
    improvement["why"] = rationale
    if fallback_used:
        improvement["status"] = "resolved_with_fallback"
        improvement["route_state"] = "resolved_with_fallback"
        improvement["route_state_reason"] = "fallback SDK description match selected one reachable capability"
    improvement["reachability"] = {
        "status": "pass" if proof_result.status == "success" else "fail",
        "proof_status": proof.get("status") if isinstance(proof, dict) else "fail",
        "required_gates_passed": required_gates_passed,
        "user_runtime_ready": user_runtime_ready,
    }
    improvement["proof"] = proof
    improvement["agent_summary"] = (
        f"Recommended {handle} for this goal."
        if proof_result.status == "success"
        else f"Recommended {handle}, but reachability proof failed."
    )
    improvement["next_command"] = _skills_validation_command("proof", handle)
    improvement["validation_commands"] = [improvement["next_command"]]

    result.data["improvement"] = improvement
    result.data["goal_decision"] = goal_decision
    if proof_result.status == "success":
        return result

    proof_has_gates = isinstance(gates, dict) and bool(gates)
    fallback_after_unreachable_route = (
        not fallback_used
        and route_decision_status == "resolved"
        and proof_has_gates
        and _proof_missing_workspace_source(proof)
    )
    if fallback_after_unreachable_route:
        fallback = _fallback_improvement_candidate(repo_root, goal_text)
        fallback_handle = _candidate_handle(fallback or {})
        if fallback and fallback_handle and fallback_handle != handle:
            fallback_proof_result = skills_proof(repo_root, handle=fallback_handle)
            fallback_proof = fallback_proof_result.data.get("proof", {})
            if fallback_proof_result.status == "success":
                fallback_gates = fallback_proof.get("gates", {}) if isinstance(fallback_proof, dict) else {}
                fallback_required = (
                    fallback_proof.get("gate_policy", {}).get("required", [])
                    if isinstance(fallback_proof, dict)
                    else []
                )
                fallback_required_gates_passed = all(bool(fallback_gates.get(gate)) for gate in fallback_required)
                fallback_user_runtime_ready = bool(fallback_gates.get("user_runtime_ready"))
                improvement["status"] = "resolved_with_fallback"
                improvement["route_state"] = "resolved_with_fallback"
                improvement["route_state_reason"] = (
                    "fallback SDK description match replaced an unreachable routed capability"
                )
                improvement["recommended_capability"] = {
                    "handle": fallback_handle,
                    "name": fallback.get("name"),
                    "path": fallback.get("path"),
                    "candidate_id": fallback.get("candidate_id"),
                    "candidate_type": fallback.get("candidate_type"),
                    "confidence": fallback.get("confidence"),
                }
                improvement["why"] = [
                    *list(fallback.get("rationale") or []),
                    f"initial routed capability unreachable={handle}",
                ]
                improvement["reachability"] = {
                    "status": "pass",
                    "proof_status": fallback_proof.get("status") if isinstance(fallback_proof, dict) else "pass",
                    "required_gates_passed": fallback_required_gates_passed,
                    "user_runtime_ready": fallback_user_runtime_ready,
                }
                improvement["proof"] = fallback_proof
                improvement["agent_summary"] = (
                    f"Recommended {fallback_handle} after routed {handle} failed reachability."
                )
                improvement["next_command"] = _skills_validation_command("proof", fallback_handle)
                improvement["validation_commands"] = [improvement["next_command"]]
                return result

    improvement["status"] = "blocked"
    improvement["route_state"], improvement["route_state_reason"] = _improvement_route_state(
        route_decision_status,
        proof_failed=True,
    )
    result.status = "error"
    result.errors.extend(proof_result.errors)
    if not result.errors:
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"skills improve selected '{handle}', but reachability proof failed.",
                fix_suggestion=improvement["next_command"],
            )
        )
    return result


def _create_symlink(source: Path, target: Path, dry_run: bool = False, *, replace_existing: bool = False) -> str:
    """
    Create or update a filesystem symbolic link at `target` that points to `source`.

    Ensures `target.parent` exists before creating the link. Existing non-symlink paths are preserved by default so user-owned directories like `~/plugins` are not deleted during relink.

    Parameters:
        source (Path): Destination path that the symlink should reference.
        target (Path): Filesystem path where the symlink will be created or updated.
        dry_run (bool): If True, do not perform filesystem mutations; only simulate the action.
        replace_existing (bool): If True, replace an existing non-symlink target before creating the symlink.

    Returns:
        action (str): Human-readable summary, e.g. "Created symlink: <target> -> <source>", "Updated symlink: <target> -> <source>", or "Skipped existing non-symlink path: <target>".
    """
    if target.is_symlink() and target.readlink() == source:
        return f"Symlink already current: {target} -> {source}"
    if target.exists() and not target.is_symlink() and not replace_existing:
        return f"Skipped existing non-symlink path: {target}"
    action = "Created" if not target.exists() else "Updated"
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            target.unlink()
        elif target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        target.symlink_to(source)
    return f"{action} symlink: {target} -> {source}"

def _prune_first_level_symlinks(target_dir: Path, keep_names: set[str], dry_run: bool = False) -> list[str]:
    """
    Remove stale first-level symlinks in target_dir while preserving regular files, directories, hidden names, and any names listed in keep_names.

    Parameters:
        target_dir (Path): Directory whose immediate entries will be inspected.
        keep_names (set[str]): Entry names to skip (preserve) even if they are symlinks.
        dry_run (bool): If true, do not modify the filesystem; only report planned removals.

    Returns:
        list[str]: Log lines describing each removed (or planned-to-remove when dry_run) symlink in the form "Removed stale symlink: <path> -> <target>".
    """
    logs: list[str] = []
    if not target_dir.exists():
        return logs
    for item in sorted(target_dir.iterdir()):
        # Preserve hidden control links (for example ".system") and managed links.
        if not item.is_symlink() or item.name in keep_names or item.name.startswith("."):
            continue
        logs.append(f"Removed stale symlink: {item} -> {os.readlink(item)}")
        if not dry_run:
            item.unlink()
    return logs

def _find_symlink_entries(source: Path) -> list[Path]:
    """
    Find symlinked filesystem entries at or below the given source path.

    If `source` is a symlink, returns a list containing only `source`. If `source`
    does not exist or is not a directory, returns an empty list. Otherwise walks
    the directory tree (without following symlinks) and returns any symlink paths
    found. Top-level traversal skips the `.git`, `node_modules`, and `__pycache__`
    subdirectories.

    Parameters:
        source (Path): Directory or path to inspect for symlink entries.

    Returns:
        list[Path]: A list of Path objects pointing to symlink entries; may be empty.
    """
    symlinks: list[Path] = []
    if source.is_symlink():
        symlinks.append(source)
        return symlinks
    if not source.exists() or not source.is_dir():
        return symlinks

    for root, dirs, files in os.walk(source, topdown=True, followlinks=False):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__")]
        for name in dirs + files:
            candidate = Path(root) / name
            if candidate.is_symlink():
                symlinks.append(candidate)
    return symlinks

def _sync_dir_copy(source: Path, target: Path, dry_run: bool = False) -> str:
    """
    Copy-sync a directory tree into a target directory while disallowing any symlinks in the source.

    Skips top-level entries named ".git", "node_modules", and "__pycache__". If any symlink is present anywhere under the source, raises ValueError. When not a dry run, ensures the target directory exists, replaces existing directories at the destination with fresh copies, and copies files preserving file metadata.

    Parameters:
        source (Path): Source directory to copy from. Must not contain symlinks.
        target (Path): Destination directory to copy into; will be created if missing.
        dry_run (bool): If True, perform no filesystem changes and only simulate the action.

    Returns:
        str: A human-readable message describing the completed sync and the target path.
    """
    symlink_entries = _find_symlink_entries(source)
    if symlink_entries:
        rel = symlink_entries[0]
        rel_text = str(rel.relative_to(source)) if rel != source else "."
        raise ValueError(f"Symlinks are not allowed in sync source: {source} (first: {rel_text})")

    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)
        for item in source.iterdir():
            if item.name in ('.git', 'node_modules', '__pycache__'):
                continue
            dest = target / item.name
            if item.is_symlink():
                raise ValueError(f"Symlink entries are not allowed in sync source: {item}")
            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                # Preserve symlink objects defensively if one appears mid-copy.
                shutil.copytree(item, dest, symlinks=True)
            else:
                shutil.copy2(item, dest, follow_symlinks=False)
    return f"Synced directory: {target} (copy)"


def _refresh_system_lane_link(
    skills_dir: Path,
    system_skills_dir: Path,
    dry_run: bool = False,
) -> list[str]:
    """
    Preserve or create the reserved `.system` symlink in the skills lane when a managed system store exists.

    Parameters:
        skills_dir (Path): Path to the repository skills directory where `.system` should exist.
        system_skills_dir (Path): Path to the managed system skills store; if not a directory, no action is taken.
        dry_run (bool): If true, no filesystem changes are made; actions are returned as planned-log strings.

    Returns:
        list[str]: Log lines describing the action taken (created/updated) or skipped; empty list if no managed system store is present.
    """
    if not system_skills_dir.is_dir():
        return []

    target_link = skills_dir / ".system"
    if target_link.exists() and not target_link.is_symlink():
        return [f"Skipped existing non-symlink system lane: {target_link}"]

    return [_create_symlink(Path("../../skills-system"), target_link, dry_run)]


def _is_generated_root_skill_dir(path: Path) -> bool:
    """Return whether a first-level runtime directory was generated by rooted projection."""
    skill_md = path / "SKILL.md"
    if not path.is_dir() or path.is_symlink() or not skill_md.is_file():
        return False
    try:
        head = skill_md.read_text(encoding="utf-8", errors="ignore")[:600]
    except OSError:
        return False
    return "skill-type: root-skill-set" in head and "projection-mode: rooted" in head


def _prune_generated_root_skill_dirs(
    target_dir: Path,
    keep_names: set[str],
    *,
    dry_run: bool = False,
    preserve_keep_names: bool = True,
) -> list[str]:
    """Remove generated rooted runtime directories that do not belong to the requested projection."""
    logs: list[str] = []
    if not target_dir.exists():
        return logs
    for item in sorted(target_dir.iterdir()):
        if item.name.startswith(".") or (preserve_keep_names and item.name in keep_names):
            continue
        if not _is_generated_root_skill_dir(item):
            continue
        logs.append(f"Removed generated root skill set: {item}")
        if not dry_run:
            shutil.rmtree(item)
    return logs


def _generated_root_skill_dir_names(target_dir: Path) -> list[str]:
    """Return generated rooted projection entries still present in the flat runtime lane."""
    if not target_dir.exists():
        return []
    return sorted(item.name for item in target_dir.iterdir() if _is_generated_root_skill_dir(item))


SYSTEM_BRIDGE_ALIAS_MARKER = ".agent-skills-system-bridge-alias.json"


def _is_generated_system_bridge_alias(item: Path, system_source: Path) -> bool:
    if item.is_symlink():
        raw_target = Path(os.readlink(item))
        if raw_target == Path(".system") / item.name or raw_target.parts[-2:] == (".system", item.name):
            return True
        try:
            return item.resolve(strict=True) == system_source.resolve(strict=True)
        except OSError:
            return False

    marker = (
        item / SYSTEM_BRIDGE_ALIAS_MARKER
        if item.is_dir()
        else item.parent / f".{item.name}-{SYSTEM_BRIDGE_ALIAS_MARKER}"
    )
    if not marker.is_file():
        return False
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if payload.get("kind") != "system_bridge_alias":
        return False
    try:
        target = system_source.parent / str(payload.get("target", ""))
        return target.resolve(strict=True) == system_source.resolve(strict=True)
    except OSError:
        return False


def _prune_first_level_system_bridge_aliases(
    target_dir: Path,
    system_skills_dir: Path,
    *,
    dry_run: bool = False,
) -> list[str]:
    """Remove stale first-level aliases for skills that belong in the hidden system lane."""
    logs: list[str] = []
    if not target_dir.exists() or not system_skills_dir.is_dir():
        return logs

    for bridge_skill in sorted(SYSTEM_BRIDGE_SKILL_NAMES):
        item = target_dir / bridge_skill
        system_source = system_skills_dir / bridge_skill
        if not (item.exists() or item.is_symlink()):
            continue
        if not (system_source / "SKILL.md").exists():
            continue

        if not _is_generated_system_bridge_alias(item, system_source):
            logs.append(f"Skipped first-level system bridge alias without generated provenance: {item}")
            continue

        logs.append(f"Removed first-level system bridge alias: {item}")
        if dry_run:
            continue
        if item.is_symlink() or item.is_file():
            item.unlink()
        else:
            shutil.rmtree(item)
    return logs


def _is_system_bridge_entry(entry: Any, system_skills_dir: Path) -> bool:
    """Return whether a discovered entry is owned by the hidden system lane."""
    if entry.name not in SYSTEM_BRIDGE_SKILL_NAMES:
        return False
    try:
        entry_source = entry.source_dir.resolve(strict=False)
        system_root = system_skills_dir.resolve(strict=False)
        entry_source.relative_to(system_root)
    except (OSError, ValueError):
        return False
    return True


def _public_root_report(report: dict) -> dict:
    return {
        **report,
        "roots": [
            {key: value for key, value in root.items() if key != "content"}
            for root in report.get("roots", [])
        ],
    }


def _public_manifest_report(report: dict) -> dict:
    return {
        **report,
        "manifests": [
            {key: value for key, value in manifest.items() if key != "rows"}
            for manifest in report.get("manifests", [])
        ],
    }


def _append_user_runtime_relinks(
    plan: dict,
    logs: list[str],
    repo_root: Path,
    skills_dir: Path,
    *,
    dry_run: bool,
) -> None:
    home = Path.home()
    targets = [
        (skills_dir, home / ".agents" / "skills", True),
        (skills_dir, home / ".codex" / "skills", True),
        (repo_root, home / ".agents" / "agent-skills", True),
    ]
    for src, dst, replace_existing in targets:
        plan["symlinks"].append({"from": str(dst), "to": str(src)})
        logs.append(_create_symlink(src, dst, dry_run, replace_existing=replace_existing))
    user_plugins = home / ".agents" / "plugins"
    personal_plugins_action = _clear_symlinked_personal_plugin_root(
        repo_root,
        user_plugins,
        dry_run=dry_run,
        plan=plan,
    )
    logs.append(personal_plugins_action)
    if user_plugins.is_symlink() and not personal_plugins_action.startswith(("Would replace", "Replaced")):
        logs.append(f"Skipped home plugin mirror refresh for preserved personal plugin marketplace symlink: {user_plugins}")
    elif personal_plugins_action.startswith(("Would replace", "Replaced")) or user_plugins.exists():
        _refresh_home_plugin_mirrors(plan, logs, repo_root, user_plugins, dry_run=dry_run)
    _refresh_home_plugin_mirrors(plan, logs, repo_root, home / "plugins", dry_run=dry_run)
    for profile_home in _codex_profile_homes(home):
        _refresh_home_plugin_mirrors(
            plan, logs, repo_root, profile_home / "plugins", dry_run=dry_run, prune_command_surface_duplicates=True
        )
        _refresh_home_plugin_mirrors(
            plan, logs, repo_root, profile_home / "Plugins", dry_run=dry_run, prune_command_surface_duplicates=True
        )
        _refresh_home_plugin_mirrors(
            plan, logs, repo_root, profile_home / ".agents" / "plugins", dry_run=dry_run, prune_command_surface_duplicates=True
        )


def _verify_user_runtime_relinks(plan: dict, home: Path, skills_dir: Path, *, dry_run: bool) -> list[ErrorObject]:
    """Verify home runtime skill links point at this checkout's projection after user sync."""
    expected_target = str(skills_dir)
    expected_resolved = skills_dir.resolve(strict=False)
    checks: list[dict[str, Any]] = []
    errors: list[ErrorObject] = []
    if dry_run:
        plan["user_runtime_link_checks"] = {
            "status": "not_run",
            "reason": "dry_run",
            "expected_target": expected_target,
            "checks": checks,
        }
        return errors

    for label, link in (
        ("agents_user_runtime", home / ".agents" / "skills"),
        ("codex_user_runtime", home / ".codex" / "skills"),
    ):
        check: dict[str, Any] = {
            "label": label,
            "path": str(link),
            "expected_target": expected_target,
            "exists": link.exists(),
            "is_symlink": link.is_symlink(),
            "target": None,
            "resolved_target": None,
            "literal_target_matches": False,
            "resolved_target_matches": False,
            "status": "fail",
        }
        if link.is_symlink():
            try:
                target_text = os.readlink(link)
                resolved_target = link.resolve(strict=False)
            except OSError as exc:
                check["error"] = str(exc)
            else:
                check["target"] = target_text
                check["resolved_target"] = str(resolved_target)
                check["literal_target_matches"] = target_text == expected_target
                check["resolved_target_matches"] = resolved_target == expected_resolved
        if check["is_symlink"] and check["literal_target_matches"] and check["resolved_target_matches"]:
            check["status"] = "pass"
        else:
            errors.append(
                ErrorObject(
                    code="ERR_RUNTIME",
                    message=f"User runtime link {link} does not point at the active workspace projection.",
                    fix_suggestion=(
                        "Run ./bin/ask skills sync --scope user --projection flat --json --robot "
                        "from the intended checkout and verify the link target casing matches exactly."
                    ),
                )
            )
        checks.append(check)

    plan["user_runtime_link_checks"] = {
        "status": "pass" if not errors else "fail",
        "expected_target": expected_target,
        "checks": checks,
    }
    return errors


def _clear_symlinked_personal_plugin_root(repo_root: Path, target: Path, *, dry_run: bool, plan: dict) -> str:
    """Remove only repo-backed personal plugin marketplace root symlinks before mirror sync."""
    if not target.exists() and not target.is_symlink():
        return f"Personal plugin marketplace root is absent: {target}"
    if not target.is_symlink():
        return f"Personal plugin marketplace root is already a directory: {target}"
    if not _is_repo_backed_plugin_root_symlink(repo_root, target):
        return f"Preserved personal plugin marketplace symlink: {target}"
    plan["deletes"].append(f"Remove symlinked personal plugin marketplace root: {target}")
    plan["writes"].append(str(target))
    if dry_run:
        return f"Would replace symlinked personal plugin marketplace root with directory: {target}"
    else:
        target.unlink()
        target.mkdir(parents=True, exist_ok=True)
    return f"Replaced symlinked personal plugin marketplace root with directory: {target}"


def _is_repo_backed_plugin_root_symlink(repo_root: Path, target: Path) -> bool:
    try:
        resolved = target.resolve(strict=False)
    except OSError:
        return False
    canonical_plugins = (repo_root / "Plugins").resolve(strict=False)
    if resolved == canonical_plugins:
        return True
    if resolved.name != "Plugins":
        return False
    repo_markers = (".git", "AGENTS.md", "UBIQUITOUS_LANGUAGE.md")
    return any((resolved.parent / marker).exists() for marker in repo_markers)


def _codex_profile_homes(home: Path) -> list[Path]:
    """Return Codex profile homes that can contribute plugin picker entries."""
    candidates = [home / ".codex"]
    try:
        candidates.extend(sorted(home.glob(".codex-*")))
    except OSError:
        pass
    return [path for path in candidates if path.exists() and path.is_dir()]


def _ensure_real_plugin_mirror_root(target: Path, canonical_plugins_dir: Path, dry_run: bool) -> str:
    """Ensure a home plugin mirror root is a real directory, not a symlink."""
    if target.is_symlink():
        if not dry_run:
            target.unlink()
            target.mkdir(parents=True, exist_ok=True)
        return f"Replaced symlinked plugin mirror root with directory: {target}"
    if target.exists() and not target.is_dir():
        return f"Skipped non-directory plugin mirror path: {target}"
    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)
    return f"Ensured plugin mirror directory: {target}"


def _finalize_skill_sync_result(
    result: CallResult,
    plan: dict,
    logs: list[str],
    projection_decision: ProjectionModeDecision,
    *,
    scope: str,
    dry_run: bool,
    status: str,
    plugin_cache_refresh: str = "auto",
) -> CallResult:
    """Populate common sync result data after all mutations have been planned."""
    plan["mutation_counts"] = {
        "writes": len(plan["writes"]),
        "deletes": len(plan["deletes"]),
        "symlinks": len(plan["symlinks"]),
    }
    result.data["plan"] = plan
    result.data["logs"] = logs
    result.data["policy_identity"] = get_policy_identity()
    result.data["projection_mode"] = projection_decision.projection_mode
    result.data["projection"] = build_projection_plan_metadata(
        projection_decision,
        scope=scope,
        dry_run=dry_run,
        warnings=plan["warnings"],
    )
    validation_args: list[str] = []
    if scope != "workspace":
        validation_args.extend(["--scope", scope])
    if dry_run:
        validation_args.append("--dry-run")
    if projection_decision.mode_source in {"cli", "env"}:
        validation_args.extend(["--projection", projection_decision.requested_mode])
    if plugin_cache_refresh != "auto":
        validation_args.extend(["--plugin-cache-refresh", plugin_cache_refresh])
    result.data["validation_commands"] = [_skills_validation_command("sync", *validation_args)]
    result.status = status
    return result


def _refresh_home_plugin_mirrors(
    plan: dict,
    logs: list[str],
    repo_root: Path,
    home_plugins_dir: Path,
    *,
    dry_run: bool,
    prune_command_surface_duplicates: bool = False,
) -> None:
    """
    Replace the user's home plugin mirror copies from the repository's canonical Plugins/ sources.

    When run, ensure the home plugins mirror root is a real directory (not a repository-backed symlink), then for each plugin listed in Plugins/marketplace.json replace the corresponding directory under home_plugins_dir with a copy of the repository source, materialize first-level skill aliases, prune duplicate SDK entries, and write a marker file recording the repository source. In dry-run mode, only record planned actions in logs and the provided plan structure.

    Parameters:
        plan (dict): Operation plan that will be mutated with a mirror plan and per-plugin entries.
        logs (list[str]): Mutable log list to append human-readable action messages.
        repo_root (Path): Repository root containing the Plugins/ directory and marketplace.json.
        home_plugins_dir (Path): Target directory under the user's home where plugin mirrors are maintained.
        dry_run (bool): If True, do not perform filesystem mutations; only record intended actions in logs.
    """
    plugins_dir = repo_root / "Plugins"
    mirror_plan = {
        "from": str(plugins_dir),
        "to": str(home_plugins_dir),
        "mode": "copy-replace",
        "trigger": "refresh after canonical Plugins/ or Plugins/marketplace.json changes",
        "plugins": [],
    }
    plan.setdefault("runtime_plugin_mirrors", []).append(mirror_plan)
    root_log = _ensure_real_plugin_mirror_root(home_plugins_dir, plugins_dir, dry_run)
    logs.append(root_log)
    if root_log.startswith("Skipped"):
        return

    try:
        _marketplace_path, entries = _load_local_marketplace(repo_root)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        logs.append(f"Skipped home plugin mirror refresh: {exc}")
        return

    marker_name = ".codex-repo-plugin-source"
    keep_names = {entry["name"] for entry in entries}
    for entry in entries:
        plugin_name = entry["name"]
        relative = entry["path"]
        source_dir = repo_root / relative.removeprefix("./")
        target_dir = home_plugins_dir / plugin_name
        mirror_plan["plugins"].append({
            "name": plugin_name,
            "source": str(source_dir),
            "target": str(target_dir),
        })
        if not source_dir.is_dir():
            logs.append(f"Skipped missing home plugin mirror source: {source_dir}")
            continue
        if dry_run:
            logs.append(f"Would replace home plugin mirror: {target_dir} <- {source_dir}")
            continue
        try:
            if target_dir.is_symlink() or target_dir.is_file():
                target_dir.unlink()
            elif target_dir.exists():
                shutil.rmtree(target_dir)
        except OSError as exc:
            logs.append(f"Skipped replacing protected home plugin mirror: {target_dir}: {exc}")
            if prune_command_surface_duplicates:
                prune_logs, _prune_deletes = prune_command_surface_duplicate_skill_entries(repo_root, plugin_name, target_dir)
                logs.extend(prune_logs)
            continue
        _copy_directory_contents(source_dir, target_dir)
        _materialize_first_level_skill_aliases(target_dir)
        if prune_command_surface_duplicates:
            prune_logs, _prune_deletes = prune_command_surface_duplicate_skill_entries(repo_root, plugin_name, target_dir)
            logs.extend(prune_logs)
        (target_dir / marker_name).write_text(str(source_dir.resolve()) + "\n", encoding="utf-8")
        logs.append(f"Replaced home plugin mirror: {target_dir} <- {source_dir}")

    # Prune stale home plugin mirrors that are no longer declared in the marketplace.
    reserved = {"marketplace.json", "cache"}
    if home_plugins_dir.is_dir():
        for child in home_plugins_dir.iterdir():
            if child.name in keep_names or child.name in reserved:
                continue
            if not child.is_dir():
                continue
            marker_file = child / marker_name
            if not marker_file.is_file():
                continue
            if dry_run:
                logs.append(f"Would remove stale home plugin mirror: {child}")
                continue
            try:
                if child.is_symlink():
                    child.unlink()
                else:
                    shutil.rmtree(child)
            except OSError as exc:
                logs.append(f"Skipped removing protected stale home plugin mirror: {child}: {exc}")
                continue
            logs.append(f"Removed stale home plugin mirror: {child}")




def sync_skills(
    repo_root: Path,
    scope: str = "workspace",
    dry_run: bool = False,
    projection: Optional[str] = None,
    plugin_cache_refresh: str = "auto",
) -> CallResult:
    """
    Synchronizes derived skill views for either the repository workspace or the user environment.

    For scope="workspace" this prunes stale first-level symlinks under .agents/skills, recreates symlinks for repository-owned skills, preserves a .system bridge when present, and refreshes catalog projections (SKILL.md and README.md). For scope="user" this creates user-facing symlinks from the repo workspace.

    Parameters:
        repo_root (Path): Root path of the repository containing skills directories.
        scope (str): Either "workspace" to sync repository-derived views or "user" to populate user-local locations.
        dry_run (bool): If True, no filesystem mutations are performed; actions are reported only.
        projection (Optional[str]): Explicit runtime projection mode. When omitted,
            SYNC_SKILLS_PROJECTION_MODE is honored before the flat default.
        plugin_cache_refresh (str): Plugin runtime cache refresh mode:
            "auto" refreshes best-effort during workspace sync, "skip" runs
            normal projection sync without cache mutation, and "only" refreshes
            plugin runtime caches without changing skill projections.

    Returns:
        CallResult: Success result contains a `data` object with:
          - plan: dict with lists for "writes", "deletes", and "symlinks" describing intended changes,
          - logs: list of human-readable action logs,
          - policy_identity: identity info from get_policy_identity().
        On error, the result will have status "error" and one or more ErrorObject entries:
          - ERR_INVALID_SCOPE when `scope` is not "workspace" or "user".
          - ERR_VALIDATION when inputs contain disallowed symlinks or other validation failures.
          - Other errors may be returned for copy/sync failures (e.g., when `_sync_dir_copy` detects symlinks).
    """
    result = CallResult()
    try:
        projection_decision = normalize_projection_mode(projection)
    except ProjectionModeError as exc:
        resolved_mode = getattr(exc, "resolved_mode", None)
        fix_suggestions = {
            "ERR_INVALID_PROJECTION_MODE": "Choose the supported SDK projection mode: --projection flat.",
            "ERR_DEFERRED_PROJECTION_MODE": "Use --projection flat until the deferred projection mode is available.",
        }
        result.status = "error"
        result.errors.append(ErrorObject(
            code=exc.code,
            message=exc.message,
            fix_suggestion=fix_suggestions.get(exc.code, "Choose a supported projection mode or rerun with --dry-run."),
        ))
        result.data["projection_mode"] = resolved_mode
        result.data["requested_projection_mode"] = getattr(exc, "requested_mode", projection or "")
        return result

    if plugin_cache_refresh not in {"auto", "skip", "only"}:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Invalid plugin cache refresh mode: '{plugin_cache_refresh}'.",
            fix_suggestion="Use --plugin-cache-refresh auto, skip, or only.",
        ))
        return result

    if scope not in {"workspace", "user"}:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_INVALID_SCOPE",
            message=f"Invalid scope: '{scope}'. Must be 'workspace' or 'user'.",
            fix_suggestion="Use --scope workspace or --scope user"
        ))
        return result

    plan = {
        "writes": [],
        "deletes": [],
        "symlinks": [],
        "system_bridge_skill_names": sorted(SYSTEM_BRIDGE_SKILL_NAMES),
        "preserved_bridge_lane_entries": [],
        "preserved_system_lane_entries": [],
        "validation_status": "not_run",
        "unmapped_entries": [],
        "violations": [],
        "mutation_counts": {
            "writes": 0,
            "deletes": 0,
            "symlinks": 0,
        },
        "warnings": [],
        "plugin_cache_refresh": plugin_cache_permission_declaration(repo_root, mode=plugin_cache_refresh),
    }
    logs = []
    skills_dir = repo_root / ".agents" / "skills"
    system_skills_dir = repo_root / "skills-system"

    if plugin_cache_refresh == "only":
        if scope != "workspace":
            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_INVALID_SCOPE",
                message="Plugin runtime cache refresh is workspace-scoped.",
                fix_suggestion="Use `./bin/ask skills sync --scope workspace --plugin-cache-refresh only`.",
            ))
            return result
        logs.append(
            "Running plugin runtime cache refresh only; normal SDK-flat projection sync skipped. "
            f"If the cache path is blocked, {PLUGIN_CACHE_PERMISSION_RERUN}"
        )
        cache_error = refresh_workspace_plugin_caches(plan, logs, repo_root, dry_run=dry_run)
        if cache_error:
            result.errors.append(cache_error)
            return _finalize_skill_sync_result(
                result,
                plan,
                logs,
                projection_decision,
                scope=scope,
                dry_run=dry_run,
                status="error",
                plugin_cache_refresh=plugin_cache_refresh,
            )
        plan["validation_status"] = "pass"
        return _finalize_skill_sync_result(
            result,
            plan,
            logs,
            projection_decision,
            scope=scope,
            dry_run=dry_run,
            status="success",
            plugin_cache_refresh=plugin_cache_refresh,
        )

    if system_skills_dir.is_dir():
        plan["preserved_system_lane_entries"] = sorted(
            item.name
            for item in system_skills_dir.iterdir()
            if item.is_dir() and (item / "SKILL.md").exists()
        )


    entries = discover_skill_entries(source="repo")
    if scope == "workspace":
        try:
            plan["preserved_bridge_lane_entries"] = sorted(SYSTEM_BRIDGE_SKILL_NAMES)
            keep_names = {entry.name for entry in entries if entry.source_dir.is_relative_to(repo_root)}
            if system_skills_dir.is_dir():
                keep_names.add(".system")
            for log in _prune_first_level_symlinks(skills_dir, keep_names, dry_run):
                plan["deletes"].append(log)
                logs.append(log)
            if not dry_run:
                for log in _prune_first_level_system_bridge_aliases(
                    skills_dir,
                    system_skills_dir,
                    dry_run=False,
                ):
                    plan["deletes"].append(log)
                    logs.append(log)
            for log in _prune_generated_root_skill_dirs(
                skills_dir,
                keep_names,
                dry_run=dry_run,
                preserve_keep_names=False,
            ):
                plan["deletes"].append(log)
                logs.append(log)
            for entry in entries:
                if _is_system_bridge_entry(entry, system_skills_dir):
                    logs.append(f"Skipped hidden system bridge from flat projection: {entry.name}")
                    continue
                skill_name = entry.name
                target_link = skills_dir / skill_name
                if not entry.source_dir.is_relative_to(repo_root):
                    continue
                rel_to_root = entry.source_dir.relative_to(repo_root)
                source_rel = os.path.join("../..", str(rel_to_root))
                plan["symlinks"].append({"from": str(target_link), "to": source_rel})
                logs.append(_create_symlink(Path(source_rel), target_link, dry_run))
            system_lane_logs = _refresh_system_lane_link(skills_dir, system_skills_dir, dry_run)
            if system_lane_logs:
                plan["symlinks"].append({"from": str(skills_dir / ".system"), "to": "../../skills-system"})
                logs.extend(system_lane_logs)
            for log in _prune_first_level_system_bridge_aliases(
                skills_dir,
                system_skills_dir,
                dry_run=dry_run,
            ):
                plan["deletes"].append(log)
                logs.append(log)
            projection_logs = _refresh_catalog_projections(repo_root, dry_run)
            plan["writes"].extend([str(repo_root / "SKILL.md"), str(repo_root / "README.md")])
            logs.extend(projection_logs)
        except OSError as exc:
            plan["validation_status"] = "fail"
            plan["warnings"].append("RUNTIME_PROJECTION_MUTATION_FAILED")
            result.errors.append(
                ErrorObject(
                    code="ERR_RUNTIME",
                    message=f"Skill runtime projection sync failed: {exc}",
                    fix_suggestion=(
                        "Check write permissions on .agents/skills and rerun "
                        "./bin/ask skills sync --scope workspace --json --robot."
                    ),
                )
            )
            return _finalize_skill_sync_result(
                result,
                plan,
                logs,
                projection_decision,
                scope=scope,
                dry_run=dry_run,
                status="error",
                plugin_cache_refresh=plugin_cache_refresh,
            )
        cache_error = None
        if plugin_cache_refresh == "skip":
            plan["plugin_cache_refresh"]["status"] = "skipped"
            logs.append(
                "Skipped plugin runtime cache refresh (--plugin-cache-refresh skip); "
                f"{PLUGIN_CACHE_PERMISSION_RERUN}"
            )
        else:
            cache_error = refresh_workspace_plugin_caches(plan, logs, repo_root, dry_run=dry_run)
        if cache_error:
            result.errors.append(cache_error)
            return _finalize_skill_sync_result(
                result,
                plan,
                logs,
                projection_decision,
                scope=scope,
                dry_run=dry_run,
                status="error",
                plugin_cache_refresh=plugin_cache_refresh,
            )
    elif scope == "user":
        try:
            rooted_entries = _generated_root_skill_dir_names(skills_dir)
            if rooted_entries:
                plan["validation_status"] = "fail"
                plan["warnings"].append("ROOTED_WORKSPACE_RESIDUE")
                plan["rooted_workspace_entries"] = rooted_entries
                result.errors.append(
                    ErrorObject(
                        code="ERR_VALIDATION",
                        message=(
                            "Workspace runtime still contains generated rooted skill-set entries: "
                            + ", ".join(rooted_entries)
                        ),
                        fix_suggestion=(
                            "Run ./bin/ask skills sync --scope workspace --projection flat --json --robot "
                            "before relinking user runtime skills."
                        ),
                    )
                )
                return _finalize_skill_sync_result(
                    result,
                    plan,
                    logs,
                    projection_decision,
                    scope=scope,
                    dry_run=dry_run,
                    status="error",
                    plugin_cache_refresh=plugin_cache_refresh,
                )
            _append_user_runtime_relinks(plan, logs, repo_root, skills_dir, dry_run=dry_run)
            relink_errors = _verify_user_runtime_relinks(plan, Path.home(), skills_dir, dry_run=dry_run)
            if relink_errors:
                plan["validation_status"] = "fail"
                plan["warnings"].append("USER_RUNTIME_LINK_POSTCONDITION_FAILED")
                result.errors.extend(relink_errors)
                return _finalize_skill_sync_result(
                    result,
                    plan,
                    logs,
                    projection_decision,
                    scope=scope,
                    dry_run=dry_run,
                    status="error",
                    plugin_cache_refresh=plugin_cache_refresh,
                )
        except OSError as exc:
            plan["validation_status"] = "fail"
            plan["warnings"].append("USER_RUNTIME_LINK_SYNC_FAILED")
            result.errors.append(
                ErrorObject(
                    code="ERR_RUNTIME",
                    message=f"User runtime link sync failed: {exc}",
                    fix_suggestion=(
                        "Grant write access to ~/.agents and ~/.codex, then rerun "
                        "./bin/ask skills sync --scope user --json --robot."
                    ),
                )
            )
            return _finalize_skill_sync_result(
                result,
                plan,
                logs,
                projection_decision,
                scope=scope,
                dry_run=dry_run,
                status="error",
                plugin_cache_refresh=plugin_cache_refresh,
            )
    plan["validation_status"] = "pass"
    return _finalize_skill_sync_result(
        result,
        plan,
        logs,
        projection_decision,
        scope=scope,
        dry_run=dry_run,
        status="success",
        plugin_cache_refresh=plugin_cache_refresh,
    )
