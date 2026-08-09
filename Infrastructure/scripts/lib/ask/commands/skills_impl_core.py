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
import tomllib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Literal, Optional, Protocol

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
from ask.skills_sdk.skill_intake import build_skill_intake_receipt as _build_skill_intake_receipt  # noqa: E402
from ask.skills_sdk.skill_intake_review import build_skill_intake_review_receipt as _build_skill_intake_review_receipt  # noqa: E402
from ask.skills_sdk.ir import build_skill_ir as _build_skill_ir  # noqa: E402
from ask.skills_sdk.docs_projection import verify_capability_docs_projection as _verify_capability_docs_projection  # noqa: E402
from ask.skills_sdk.package_build import build_package_digest_receipt as _build_package_digest_receipt  # noqa: E402
from ask.skills_sdk.package_hardening import build_package_hardening_receipt as _build_package_hardening_receipt  # noqa: E402
from ask.skills_sdk.eval_runner import internal_scorecard_quality_gates as _internal_scorecard_quality_gates  # noqa: E402
from ask.skills_sdk.eval_runner import run_deterministic_eval as _run_deterministic_eval  # noqa: E402
from ask.skills_sdk.eval_shard_aggregate import _current_rubric_digest as _skills_sdk_current_rubric_digest  # noqa: E402
from ask.skills_sdk.release_scenario_sets import (  # noqa: E402
    RELEASE_SCENARIO_MAXIMUM,
    RELEASE_SCENARIO_MINIMUM,
)
from ask.skills_sdk.eval_profiles import build_eval_profile_preview_receipt as _build_eval_profile_preview_receipt  # noqa: E402
from ask.skills_sdk.sandbox_profile import (  # noqa: E402
    SandboxProfileError as _SandboxProfileError,
    build_sandbox_profile_receipt as _build_sandbox_profile_receipt,
)
from ask.skills_sdk.project_manifest import (  # noqa: E402
    ManifestEvaluation as _ManifestEvaluation,
    evaluate_repo_manifest as _evaluate_repo_manifest,
    evaluate_manifest_file as _evaluate_manifest_file,
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
from ask.skills_sdk.capability_evidence import (  # noqa: E402
    build_capability_evidence_receipt as _build_capability_evidence_receipt,
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


TESSL_REVIEW_MIN_SCORE = 95
TESSL_REVIEW_TARGET_SCORE = 95
PLUGIN_EVAL_MIN_ACCEPTABLE_GRADE = "B+"
PLUGIN_EVAL_EXCLUDED_PACKAGE_SURFACES = (
    "README.md",
    "references/evals.yaml",
    "references/evals",
    "references/scorer-calibration",
)


class _EvalCommandsProtocol(Protocol):
    def _scorecard_path_from_output(self, repo_root: Path, raw_output: str) -> Path | None: ...
    def _read_scorecard(self, path: Path | None) -> dict[str, Any]: ...


def _reject_symlinked_stage_inputs(root: Path) -> None:
    if root.is_symlink():
        raise ValueError(f"plugin-eval staging rejects symlinked support path: {root}")
    for candidate in root.rglob("*"):
        if candidate.is_symlink():
            raise ValueError(f"plugin-eval staging rejects symlinked support path: {candidate}")

def _stage_plugin_eval_agent_context(repo_root: Path, target_abs: Path, audit_target: str) -> tuple[Path, dict[str, Any]]:
    """Stage the agent-loaded skill context used by Plugin Eval budget checks."""
    _reject_symlinked_stage_inputs(target_abs)
    digest = hashlib.sha256(str(target_abs).encode("utf-8")).hexdigest()[:12]
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "__", str(audit_target).strip("/")) or "skill"
    staging_root = Path(tempfile.gettempdir()) / "ask-plugin-eval-reviews" / f"{safe_name}-{digest}"
    current = staging_root / "current"
    if current.exists():
        archive_root = staging_root / "archive"
        archive_root.mkdir(parents=True, exist_ok=True)
        current.replace(archive_root / f"current-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}")

    excluded = set(PLUGIN_EVAL_EXCLUDED_PACKAGE_SURFACES)

    def ignore(src: str, names: list[str]) -> set[str]:
        src_path = Path(src)
        try:
            rel = src_path.relative_to(target_abs).as_posix()
        except ValueError:
            rel = "."
        ignored: set[str] = {name for name in names if name in {".DS_Store", "Thumbs.db", "desktop.ini"}}
        for name in names:
            candidate = name if rel == "." else f"{rel}/{name}"
            if candidate in excluded:
                ignored.add(name)
        return ignored

    shutil.copytree(target_abs, current, ignore=ignore)
    rel_current = _repo_relative_path(repo_root, current) if current.is_relative_to(repo_root) else current.as_posix()
    return current, {
        "mode": "agent_context_staging",
        "staging_root": current.as_posix(),
        "display_path": rel_current,
        "excluded_package_surfaces": sorted(excluded),
        "reason": (
            "Plugin Eval budget checks should score agent-loaded skill context, not SDK workbench "
            "surfaces such as README, canonical eval indexes, generated scenario notes, or scorer calibration."
        ),
    }


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
    "skills_sdk_intake_inspect",
    "skills_sdk_intake_review",
    "skills_sdk_start",
    "skills_sdk_docs_verify",
    "skills_sdk_ir_build",
    "skills_sdk_package_build",
    "skills_sdk_package_harden",
    "skills_sdk_package_signing_intent",
    "skills_sdk_trust_decide",
    "skills_sdk_observability_feedback",
    "skills_sdk_observability_promote",
    "skills_sdk_observability_phoenix_status",
    "skills_sdk_observability_phoenix_smoke",
    "skills_sdk_observability_phoenix_mirror",
    "skills_sdk_emitter_preview",
    "skills_sdk_ci_policy_preview",
    "skills_sdk_security_adapters_preview",
    "skills_sdk_security_package_signature_preview",
    "skills_sdk_security_risk_modes_preview",
    "skills_sdk_security_run_lane_preview",
    "skills_sdk_static_explorer_preview",
    "skills_sdk_eval_scenario_quality",
    "skills_sdk_eval_shard_aggregate",
    "skills_sdk_eval_scorer_quality",
    "skills_sdk_eval_scorer_calibration",
    "skills_sdk_eval_tessl_score",
    "skills_sdk_eval_tessl_local_proof",
    "skills_sdk_eval_regression_plan",
    "skills_sdk_eval_handoff_readiness",
    "skills_sdk_eval_profiles_preview",
    "skills_sdk_eval_ab_rubric_preview",
    "skills_sdk_eval_ab_preview",
    "skills_sdk_eval_ab_plan",
    "skills_sdk_eval_ab_run",
    "skills_sdk_eval_ab_judge_preview",
    "skills_sdk_eval_ab_judge_score",
    "skills_sdk_eval_run",
    "skills_sdk_placeholder_lifecycle",
    "skills_sdk_project_improve",
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


def _is_path_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def _resolve_project_relative_config_path(
    project_root: Path,
    value: str,
    *,
    allow_project_root: bool = False,
) -> Path | None:
    raw_value = value.strip()
    if not raw_value:
        return None
    raw_path = Path(raw_value)
    if raw_path.is_absolute() or ".." in raw_path.parts:
        return None
    if raw_path.parts in {(), (".",)}:
        if not allow_project_root:
            return None
        return project_root.resolve()
    try:
        resolved = (project_root / raw_path).resolve(strict=False)
    except OSError:
        return None
    return resolved if _is_path_relative_to(resolved, project_root) else None


def _find_project_manifest_root(path: Path) -> tuple[Path, Path] | None:
    """Return the nearest ancestor containing skills-sdk.json for a source path."""
    current = path if path.is_dir() else path.parent
    for candidate in (current, *current.parents):
        manifest = candidate / "skills-sdk.json"
        if manifest.is_file():
            return candidate, manifest
    return None


def _declared_project_skill_source(project_root: Path, manifest_path: Path, source: Path) -> str | None:
    """Return the declared source root for a project-local skill source."""
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    declared_sources: list[tuple[Any, Any]] = []
    skill_sources = manifest.get("skill_sources")
    if isinstance(skill_sources, list):
        declared_sources.extend(
            (item.get("root"), item.get("kind"))
            for item in skill_sources
            if isinstance(item, dict)
        )
    skill_roots = manifest.get("skill_roots")
    if isinstance(skill_roots, list):
        declared_sources.extend(
            (item.get("path"), item.get("classification"))
            for item in skill_roots
            if isinstance(item, dict)
        )
    for root_value, classification in declared_sources:
        if classification != "canonical_project_source":
            continue
        if not isinstance(root_value, str) or not root_value.strip():
            continue
        declared_root = _resolve_project_relative_config_path(project_root, root_value)
        if declared_root is None:
            continue
        if _is_path_relative_to(source, declared_root):
            return Path(root_value).as_posix()
    return None


def _project_local_skill_target(repo_root: Path, query: str) -> tuple[dict[str, Any] | None, str | None]:
    """Resolve a manifest-declared project-local SKILL.md outside the foundry."""
    raw_path = Path(query).expanduser()
    if not raw_path.is_absolute():
        return None, None
    try:
        resolved_path = raw_path.resolve(strict=False)
    except OSError:
        return None, None
    if _is_path_relative_to(resolved_path, repo_root):
        return None, None
    source = resolved_path if resolved_path.name == "SKILL.md" else resolved_path / "SKILL.md"
    if not source.is_file():
        return None, None
    manifest_info = _find_project_manifest_root(source)
    if not manifest_info:
        return None, None
    project_root, manifest_path = manifest_info
    declared_root = _declared_project_skill_source(project_root, manifest_path, source)
    if not declared_root:
        return None, None
    try:
        target_path = resolved_path.relative_to(project_root).as_posix()
    except ValueError:
        target_path = resolved_path.as_posix()
    try:
        source_relative = source.relative_to(project_root).as_posix()
    except ValueError:
        source_relative = source.as_posix()
    source_path = source.as_posix()
    return {
        "target_kind": "project_local_source_path",
        "handle": None,
        "source_path": source_path,
        "target_path": target_path,
        "requested_path": raw_path.as_posix(),
        "source_exists": True,
        "resolution": None,
        "project_root": project_root.as_posix(),
        "project_manifest": manifest_path.as_posix(),
        "project_source_root": declared_root,
        "project_relative_source_path": source_relative,
    }, source.parent.as_posix()


def _resolve_existing_skill_path(path: Path) -> Path | None:
    """Return a skill directory for an existing explicit filesystem target."""
    if path.is_file() and path.name == "SKILL.md":
        path = path.parent
    if path.is_dir() and (path / "SKILL.md").is_file():
        return path.resolve()
    return None


def _resolve_audit_skill_path(repo_root: Path, skill_path: str) -> tuple[Path | None, bool, CallResult | None]:
    """Resolve repo-local or explicit external skill audit targets.

    Repo-relative inputs keep the existing traversal guard. Existing filesystem
    skill directories outside the foundry are allowed as read-only project-local
    audit targets so installed Skill Factory lanes can operate from owner repos.
    """
    raw_target = Path(skill_path).expanduser()
    candidate = raw_target if raw_target.is_absolute() else repo_root / raw_target
    explicit_skill_dir = _resolve_existing_skill_path(candidate)
    if explicit_skill_dir is not None:
        try:
            explicit_skill_dir.relative_to(repo_root.resolve())
            return explicit_skill_dir, False, None
        except ValueError:
            return explicit_skill_dir, True, None

    resolved_path, path_error = _validate_repo_relative_skill_path(repo_root, skill_path)
    return resolved_path, False, path_error


def _external_skill_root_children(repo_root: Path, skill_path: str) -> list[Path]:
    """Return immediate child skill dirs for an explicit external skill root."""
    raw_target = Path(skill_path).expanduser()
    candidate = raw_target if raw_target.is_absolute() else repo_root / raw_target
    try:
        root = candidate.resolve()
        root.relative_to(repo_root.resolve())
        return []
    except ValueError:
        pass
    except OSError:
        return []
    if not root.is_dir() or (root / "SKILL.md").is_file():
        return []
    return sorted(path.resolve() for path in root.iterdir() if (path / "SKILL.md").is_file())


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

__all__ = [name for name in globals() if not name.startswith("__")]
