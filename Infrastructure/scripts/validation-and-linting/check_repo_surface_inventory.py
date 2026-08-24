#!/usr/bin/env python3
"""Classify tracked repository paths by repo surface ownership policy."""

from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

_CLI = importlib.import_module("repo_surface_inventory_cli")
SERVICE_ID = _CLI.SERVICE_ID
error_report = _CLI.error_report
parse_args = _CLI.parse_args


REPO_ROOT = Path(__file__).resolve().parents[3]
SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}
FUTURE_ARTIFACT_DEBT_CLASSIFICATIONS = {"historical_artifact"}

SYSTEM_SKILL_SURFACE_PREFIXES = (
    "skills-system/.codex-system-skills.marker",
    "skills-system/imagegen",
    "skills-system/openai-docs",
    "skills-system/plugin-creator",
    "skills-system/plugin-installer",
    "skills-system/skill-creator",
    "skills-system/skill-installer",
)
HARNESS_HISTORICAL_PREFIXES = (
    ".harness/agent-runs",
    ".harness/artifacts",
    ".harness/ci-migrate-snapshots",
    ".harness/evidence/harness/traces",
    ".harness/review-artifacts",
    ".harness/traces",
)
SOURCE_PREFIXES = (
    "Skills",
    "skills-sdk",
    "Infrastructure/scripts",
    "Infrastructure/bin",
    "Infrastructure/tests",
    "codex/agents/evals",
    "bin",
    "codex/agents/evals",
    "scripts",
    "utilities",
    "brand",
)
REFERENCE_PREFIXES = (
    "AI/context",
    "Infrastructure/references",
    "Wiki",
    "AI/context",
    ".harness/knowledge",
    ".harness/memory",
)
HARNESS_REFERENCE_PREFIXES = (
    ".harness/knowledge",
    ".harness/memory",
    ".harness/features",
    ".harness/strategy",
    ".harness/triage",
    ".harness/review",
    ".harness/ideate",
    ".harness/media",
    ".harness/evals",
    ".harness/evidence",
    ".harness/implementation-notes",
    ".harness/reports",
    ".harness/research",
    ".harness/session-evidence",
    ".harness/specs",
    ".harness/plan",
    ".harness/reviews",
)
POLICY_PREFIXES = (
    "Docs",
    "codestyle",
    "contracts",
    ".github",
    ".agents/workflows",
    ".circleci",
    ".codex",
    ".diagram",
    ".vale",
    "Infrastructure/COMPLIANCE",
    "Infrastructure/EVALUATION",
    "Infrastructure/GOVERNANCE",
    "Infrastructure/SECURITY",
    "Infrastructure/config",
    "Infrastructure/catalog",
    "Infrastructure/policy",
    ".harness/brainstorm",
    ".harness/core",
    ".harness/decisions",
    ".harness/linear",
    ".harness/reframes",
    ".harness/refactors",
    ".harness/quality",
    ".harness/solutions",
)
POLICY_EXACT_PATHS = {
    ".agents/PLANS.md",
    ".harness/README.md",
    ".harness/ci-provider-transition-status.json",
    ".harness/ci-required-checks.json",
    ".harness/restore-manifest.json",
    ".harness/upgrade-manifest.json",
    ".harness/active-artifacts.md",
    ".harness/artifact-provenance.json",
    ".harness/review-log.md",
    "Infrastructure/AGENTS.md",
    ".harness/archive/2026-08-15-artifact-retirement/root-artifacts/AGENTS.md",
    "skills-system/AGENTS.md",
    "coding-policy.json",
    "CODEOWNERS",
    "GOVERNANCE",
    "coding-policy.json",
    "Infrastructure/docs-policy.json",
    "Infrastructure/AGENTS.md",
    "Infrastructure/Makefile",
    "Infrastructure/memory.json",
    "Infrastructure/prek.toml",
    "Infrastructure/pyproject.toml",
    "Infrastructure/uv.lock",
    "LICENSE",
    "artifacts/AGENTS.md",
    "logs/AGENTS.md",
}

HARNESS_REFERENCE_EXACT_PATHS = frozenset({
    ".harness/active-artifacts.md",
    ".harness/artifact-provenance.json",
    ".harness/review-log.md",
})

FIXTURE_PREFIXES = (".workouts", "Infrastructure/templates", "Infrastructure/vendor")
AUTHORED_SOURCE_PREFIXES = (
    "Plugins",
    "Prototypes",
    "Infrastructure/factory",
    "Infrastructure/ops",
    "Infrastructure/reports",
    "Infrastructure/storage",
)
@dataclass(frozen=True)
class SurfaceFinding:
    path: str
    classification: str
    status: str
    code: str
    severity: str
    blocking: bool
    reason: str
    recommendation: str
    allowlist_entry: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
def _normalize_path(path: str | Path) -> str:
    normalized = Path(str(path).strip()).as_posix()
    if normalized.startswith("./"):
        return normalized[2:]
    return normalized
def _path_parts(path: str) -> tuple[str, ...]:
    return tuple(part for part in Path(path).parts if part not in ("", "."))
def _starts_with(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(f"{prefix}/")
def _starts_with_any(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(_starts_with(path, prefix) for prefix in prefixes)
def _is_governed_system_skill_surface(path: str) -> bool:
    return any(_starts_with(path, prefix) for prefix in SYSTEM_SKILL_SURFACE_PREFIXES)
def _matches_plugin_subpath(path: str, subpath: str) -> bool:
    """Return whether a Plugins path has the expected third component."""
    parts = _path_parts(path)
    return len(parts) >= 3 and parts[0] == "Plugins" and parts[2] == subpath
def _is_root_front_door_doc(path: str) -> bool:
    """Return whether path is a top-level front-door doc filename."""
    if "/" in path:
        return False
    names = {
        "AGENTS.md",
        "ARCHITECTURE.md",
        "CHANGELOG.md",
        "CODE_OF_CONDUCT.md",
        "CODESTYLE.md",
        "CONTEXT.md",
        "CONTRIBUTING.md",
        "README.md",
        "SECURITY.md",
        "SKILL.md",
        "SUPPORT.md",
        "UBIQUITOUS_LANGUAGE.md",
        "WORKFLOW.md",
    }
    return path in names
def _is_root_config(path: str) -> bool:
    """Return whether path is a recognized top-level config filename."""
    if "/" in path:
        return False
    names = {
        ".architecture.yml",
        ".coderabbit.yaml",
        ".diagramrc",
        ".gitignore",
        ".gitleaks.toml",
        ".markdownlint.yaml",
        ".memory-metrics.json",
        ".mise.toml",
        ".npmrc",
        ".pylintrc",
        ".qdrant-initialized",
        ".semgrepignore",
        ".vale.ini",
        "biome.json",
        "docs-policy.json",
        "harness.contract.json",
        "justfile",
        "Makefile",
        "memory.json",
        "package-lock.json",
        "prek.toml",
    }
    return path in names
def _make_finding(
    path: str,
    *,
    classification: str,
    status: str,
    code: str,
    severity: str,
    blocking: bool,
    reason: str,
    recommendation: str,
    metadata: dict[str, Any] | None = None,
) -> SurfaceFinding:
    metadata = _normalize_metadata(metadata or {})
    return SurfaceFinding(
        path=path,
        classification=classification,
        status=status,
        code=code,
        severity=severity,
        blocking=blocking,
        reason=reason,
        recommendation=recommendation,
        metadata=metadata,
    )
def _next_step(step_type: str, command: str, rationale: str) -> dict[str, str]:
    return {
        "type": step_type,
        "command": command,
        "rationale": rationale,
    }
def _step_from_token(token: str) -> dict[str, str]:
    return _next_step(
        "manual",
        token,
        f"Complete the {token.replace('_', ' ')} step before changing tracked content.",
    )
def _normalize_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    next_steps = metadata.get("next_steps")
    if isinstance(next_steps, list) and all(isinstance(step, str) for step in next_steps):
        metadata = {
            **metadata,
            "next_steps": [_step_from_token(step) for step in next_steps],
        }
    return metadata
FINDING_SPECS = {
    "lowercase_docs_drift": ("classification_required", "violation", "error", True, "Docs/** is the canonical documentation root; lowercase docs/** is casing drift.", "Move the content to Docs/** or document an explicit compatibility migration.", ("move_to_canonical_docs_root", "update_references")),
    "duplicated_infrastructure_path": ("classification_required", "violation", "error", True, "Duplicated Infrastructure/Infrastructure path shape is suspicious.", "Reference-scan and either delete generated debris or classify the canonical owner.", ("scan_references", "decide_owner_or_cleanup")),
    "tracked_plugin_cache": ("generated_ignored", "violation", "error", True, "Plugin cache content is generated runtime state and should not be newly tracked.", "Remove from git after verifying no fixture or vendored snapshot contract applies.", ("verify_no_fixture_consumer", "remove_from_tracked_surface")),
    "tracked_runtime_state": ("runtime_state", "violation", "error", True, "Skill telemetry is local runtime output.", "Keep telemetry untracked unless converted into a documented fixture.", ("verify_fixture_role", "remove_or_relocate")),
    "tracked_runtime_database": ("runtime_state", "violation", "error", True, "Harness database files are runtime state by default.", "Move under fixtures with a documented consumer or remove from tracked source.", ("prove_fixture_consumer", "document_or_untrack")),
    "tracked_harness_backup": ("runtime_state", "violation", "error", True, "Harness backups are local scratch output.", "Keep backups ignored and untracked.", ("remove_from_tracked_surface",)),
    "tracked_harness_snapshot": ("historical_artifact", "warning", "warning", False, "Harness run, review, trace, and migration artifacts are generated evidence by default.", "Keep only a canonical fixture, reference, or intentional archive; otherwise remove the tracked snapshot.", ("retain_fixture_or_archive_reason", "remove_from_tracked_surface")),
    "generated_skillset_projection": ("generated_tracked", "ok", "info", False, ".skillsets contains rooted skill manifests and command-surface projections generated from canonical skill sources.", "Regenerate through skills sync rather than hand-editing.", ("validate_projection_if_changed",)),
    "system_skill_surface": ("generated_tracked", "ok", "info", False, "skills-system contains the governed system-skill bridge pinned by Infrastructure/GOVERNANCE/skills-system-upstream.lock.json.", "Refresh only through the system-skills upstream lock and projection-integrity workflow; do not hand-fork OpenAI-owned SKILL.md bodies.", ("preserve_system_skills_lock", "validate_projection_if_changed")),
    "ownership_decision_required": ("classification_required", "violation", "error", True, "skills-system path is outside the governed system-skill lock or bridge prefixes.", "Document the reader or update command, add it to the system-skills lock/bridge contract, or remove the stray path.", ("identify_reader_or_update_command", "document_owner")),
    "tracked_generated_work_area": ("historical_artifact", "warning", "warning", False, "Temporary and backlog work areas are not canonical source surfaces by default.", "Reference-scan and retain only documented fixtures, indexes, or source migrations.", ("reference_scan", "decide_fixture_or_cleanup")),
    "tracked_historical_artifact": ("historical_artifact", "warning", "warning", False, "Generated evidence and run artifacts are ignored by default.", "Keep only a canonical fixture, reference, or intentional archive; otherwise remove the tracked artifact.", ("reference_scan", "retain_fixture_or_archive_reason")),
    "generated_evidence_pattern": ("historical_artifact", "warning", "warning", False, "JSONL and log files often represent generated evidence.", "Confirm this file is a fixture or move it to generated output.", ("confirm_fixture_or_generated_output",)),
    "command_surface_handle": ("generated_tracked", "ok", "info", False, "Command-surface handles are tracked compatibility metadata surfaces.", "Regenerate through sync rather than hand-editing.", ("validate_projection_if_changed",)),
    "plugin_fixture_surface": ("fixture", "ok", "info", False, "Path is a plugin-owned fixture or archived budget fixture with an explicit consumer.", "Track only when tests, packaging, or preservation indexes reference it.", ("keep_consumer_documented",)),
    "plugin_reference_surface": ("reference", "ok", "info", False, "Path is plugin-owned reference context loaded through progressive disclosure.", "Keep indexed from the owning plugin front door.", ("preserve_index_link_if_changed",)),
    "source_path": ("source", "ok", "info", False, "Path is authored source or test/tooling source.", "Track and edit through the canonical source path.", ("run_focused_validation_if_changed",)),
    "plugin_metadata_source": ("source", "ok", "info", False, "Plugin package metadata is tracked source/policy.", "Track with plugin package validation.", ("run_plugin_validation_if_changed",)),
    "indexed_reference_surface": ("reference", "ok", "info", False, "Path is supporting context loaded through progressive disclosure.", "Keep indexed and intentionally reachable.", ("preserve_index_link_if_changed",)),
    "harness_archive_surface": ("intentional_archive", "ok", "info", False, ".harness/archive contains intentionally retained historical Harness planning and spec archives.", "Keep archive indexes and retention reasons discoverable before changing archived material.", ("preserve_archive_index_if_changed",)),
    "harness_reference_surface": ("reference", "ok", "info", False, "Path is curated Harness context or a durable HE lifecycle artifact.", "Track when intentionally reachable from Harness policy or execution-slice contracts.", ("preserve_harness_classification_if_changed",)),
    "policy_surface": ("policy", "ok", "info", False, "Path is governance, routing, configuration, or validation policy.", "Track and keep linked from the relevant front door.", ("run_policy_validation_if_changed",)),
    "fixture_or_template_surface": ("fixture", "ok", "info", False, "Path is a stable fixture, template, or vendored support input.", "Track only with a clear consumer and reason.", ("keep_consumer_documented",)),
    "authored_source_surface": ("source", "ok", "info", False, "Path is authored repository source.", "Track and validate through the owning workflow.", ("run_owner_validation_if_changed",)),
    "classification_required": ("classification_required", "violation", "error", True, "No repo surface ownership rule matched this tracked path, and tracked paths may not use unknown or any ownership.", "Classify the path in policy or remove the unowned tracked surface after reference checks.", ("inspect_owner", "update_policy_or_cleanup")),
}


def _finding(normalized: str, code: str) -> SurfaceFinding:
    classification, status, severity, blocking, reason, recommendation, steps = FINDING_SPECS[code]
    return _make_finding(
        normalized,
        classification=classification,
        status=status,
        code=code,
        severity=severity,
        blocking=blocking,
        reason=reason,
        recommendation=recommendation,
        metadata={"next_steps": list(steps)},
    )


def _classify_violation_surface(normalized: str, suffix: str) -> SurfaceFinding | None:
    if _starts_with(normalized, "docs"):
        return _finding(normalized, "lowercase_docs_drift")
    if _starts_with(normalized, "Infrastructure/Infrastructure"):
        return _finding(normalized, "duplicated_infrastructure_path")
    if _starts_with(normalized, "Plugins/cache"):
        return _finding(normalized, "tracked_plugin_cache")
    if _starts_with(normalized, ".skill-telemetry"):
        return _finding(normalized, "tracked_runtime_state")
    if normalized.startswith(".harness/") and suffix == ".db":
        return _finding(normalized, "tracked_runtime_database")
    if _starts_with(normalized, ".harness/backups"):
        return _finding(normalized, "tracked_harness_backup")
    return None


def _is_governed_source_artifact(normalized: str, suffix: str) -> bool:
    if normalized in {
        "artifacts/recommended-skills-sdk-pipeline.html",
        "artifacts/skills-sdk-user-lifecycle-one-page.html",
    }:
        return True
    return (
        suffix == ".jsonl"
        and Path(normalized).name == "examples.jsonl"
        and _starts_with_any(normalized, ("Skills", "codex/agents/evals"))
        and "/references/scorer-calibration/" in normalized
    )


def _classify_governed_generated_surface(normalized: str, suffix: str) -> SurfaceFinding | None:
    if normalized == "skills-system/AGENTS.md":
        return _finding(normalized, "policy_surface")
    if _starts_with_any(normalized, HARNESS_HISTORICAL_PREFIXES):
        return _finding(normalized, "tracked_harness_snapshot")
    if _starts_with(normalized, ".harness/evidence") and suffix in {".jsonl", ".log"}:
        return _finding(normalized, "generated_evidence_pattern")
    if _starts_with(normalized, ".harness/evidence"):
        return _finding(normalized, "harness_reference_surface")
    return None


def _classify_generated_surface(normalized: str, suffix: str) -> SurfaceFinding | None:
    if normalized in POLICY_EXACT_PATHS:
        return _finding(normalized, "policy_surface")
    governed_finding = _classify_governed_generated_surface(normalized, suffix)
    if governed_finding is not None:
        return governed_finding
    if _starts_with(normalized, ".skillsets"):
        return _finding(normalized, "generated_skillset_projection")
    if _starts_with(normalized, "skills-system") and _is_governed_system_skill_surface(normalized):
        return _finding(normalized, "system_skill_surface")
    if _starts_with(normalized, "skills-system"):
        return _finding(normalized, "ownership_decision_required")
    if _starts_with_any(normalized, ("Infrastructure/tmp", "Infrastructure/todos")):
        return _finding(normalized, "tracked_generated_work_area")
    if _is_governed_source_artifact(normalized, suffix):
        return _finding(normalized, "authored_source_surface")
    if _starts_with_any(normalized, ("Infrastructure/artifacts", "artifacts")):
        return _finding(normalized, "tracked_historical_artifact")
    if suffix in {".jsonl", ".log"}:
        return _finding(normalized, "generated_evidence_pattern")
    if _starts_with(normalized, ".agents/skills"):
        return _finding(normalized, "command_surface_handle")
    return None


def _classify_source_surface(normalized: str) -> SurfaceFinding | None:
    if _is_governed_source_artifact(normalized, Path(normalized).suffix.lower()):
        return _finding(normalized, "authored_source_surface")
    if _matches_plugin_subpath(normalized, "fixtures"):
        return _finding(normalized, "plugin_fixture_surface")
    if _matches_plugin_subpath(normalized, "references"):
        return _finding(normalized, "plugin_reference_surface")
    if _starts_with_any(normalized, SOURCE_PREFIXES) or _matches_plugin_subpath(normalized, "skills"):
        return _finding(normalized, "source_path")
    if _matches_plugin_subpath(normalized, ".codex-plugin"):
        return _finding(normalized, "plugin_metadata_source")
    return None


def _classify_reference_surface(normalized: str) -> SurfaceFinding | None:
    if normalized in HARNESS_REFERENCE_EXACT_PATHS:
        return _finding(normalized, "harness_reference_surface")
    if _starts_with_any(normalized, REFERENCE_PREFIXES):
        return _finding(normalized, "indexed_reference_surface")
    if _starts_with(normalized, ".harness/archive"):
        return _finding(normalized, "harness_archive_surface")
    if _starts_with_any(normalized, HARNESS_REFERENCE_PREFIXES):
        return _finding(normalized, "harness_reference_surface")
    return None


def _classify_policy_surface(normalized: str) -> SurfaceFinding | None:
    if _starts_with_any(normalized, POLICY_PREFIXES) or normalized in POLICY_EXACT_PATHS or _is_root_config(normalized):
        return _finding(normalized, "policy_surface")
    if _starts_with_any(normalized, FIXTURE_PREFIXES):
        return _finding(normalized, "fixture_or_template_surface")
    if _starts_with_any(normalized, AUTHORED_SOURCE_PREFIXES) or _is_root_front_door_doc(normalized):
        return _finding(normalized, "authored_source_surface")
    return None


def classify_path(path: str | Path) -> SurfaceFinding:
    """Classify a repository-relative path into a surface finding."""
    normalized = _normalize_path(path)
    suffix = Path(normalized).suffix.lower()
    rules = (
        _classify_violation_surface(normalized, suffix),
        _classify_source_surface(normalized),
        _classify_reference_surface(normalized),
        _classify_policy_surface(normalized),
        _classify_generated_surface(normalized, suffix),
    )
    return next((finding for finding in rules if finding is not None), _finding(normalized, "classification_required"))


def _is_changed_path(finding: SurfaceFinding, changed_files: set[str]) -> bool:
    return finding.path in changed_files


def apply_future_artifact_debt_guard(
    finding: SurfaceFinding,
    changed_files: set[str],
) -> SurfaceFinding:
    if not changed_files or not _is_changed_path(finding, changed_files):
        return finding
    if finding.status != "warning" or finding.classification not in FUTURE_ARTIFACT_DEBT_CLASSIFICATIONS:
        return finding

    return _make_finding(
        finding.path,
        classification=finding.classification,
        status="violation",
        code="new_historical_artifact_debt",
        severity="error",
        blocking=True,
        reason=(
            f"{finding.reason} This changed-file lane would add or modify tracked "
            "historical artifact debt."
        ),
        recommendation=(
            "Move future run output to ignored temp or evidence storage, or convert it "
            "to a canonical fixture, reference, or intentional archive before tracking it."
        ),
        metadata={
            **finding.metadata,
            "original_code": finding.code,
            "changed_files_policy": "future_artifact_debt_blocked",
        },
    )


def classify_paths(
    paths: list[str | Path],
    *,
    changed_files: list[str | Path] | None = None,
) -> list[SurfaceFinding]:
    changed_file_set = {_normalize_path(path) for path in changed_files or []}
    findings = [
        apply_future_artifact_debt_guard(
            classify_path(path),
            changed_file_set,
        )
        for path in paths
    ]
    return sorted(
        findings,
        key=lambda finding: (
            -int(finding.blocking),
            SEVERITY_ORDER[finding.severity],
            finding.path,
            finding.code,
        ),
    )


def git_ls_files(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )
    paths = [line for line in result.stdout.splitlines() if line.strip()]
    return [path for path in paths if (repo_root / path).exists()]


def _git_object_size(repo_root: Path, object_name: str) -> int | None:
    result = subprocess.run(
        ["git", "cat-file", "-s", object_name],
        cwd=repo_root,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return int(result.stdout.strip())


def _git_path_differs(repo_root: Path, *args: str) -> bool:
    result = subprocess.run(
        ["git", "diff", "--quiet", *args],
        cwd=repo_root,
        check=False,
    )
    return result.returncode == 1


def future_artifact_debt_candidates(
    repo_root: Path,
    changed_files: list[str],
) -> list[str]:
    """Return changed paths that add to, rather than reduce, artifact debt."""
    candidates: list[str] = []
    for path in changed_files:
        if not (repo_root / path).exists():
            continue

        if _git_path_differs(repo_root, "--cached", "--", path):
            baseline = f"HEAD:{path}"
            current = f":{path}"
        elif _git_path_differs(repo_root, "--", path):
            baseline = f"HEAD:{path}"
            baseline_size = _git_object_size(repo_root, baseline)
            current_size = (repo_root / path).stat().st_size
            if baseline_size is None or current_size > baseline_size:
                candidates.append(path)
            continue
        else:
            baseline = f"HEAD^:{path}"
            current = f"HEAD:{path}"

        baseline_size = _git_object_size(repo_root, baseline)
        current_size = _git_object_size(repo_root, current)
        if current_size is not None and (
            baseline_size is None or current_size > baseline_size
        ):
            candidates.append(path)
    return candidates


def build_report(
    findings: list[SurfaceFinding],
    *,
    strict: bool,
    changed_files: list[str | Path] | None = None,
) -> dict[str, Any]:
    counts_by_classification: dict[str, int] = {}
    counts_by_status: dict[str, int] = {}
    counts_by_code: dict[str, int] = {}
    blocking_counts_by_classification: dict[str, int] = {}
    blocking_counts_by_code: dict[str, int] = {}
    for finding in findings:
        counts_by_classification[finding.classification] = counts_by_classification.get(finding.classification, 0) + 1
        counts_by_status[finding.status] = counts_by_status.get(finding.status, 0) + 1
        counts_by_code[finding.code] = counts_by_code.get(finding.code, 0) + 1
        if finding.blocking:
            blocking_counts_by_classification[finding.classification] = (
                blocking_counts_by_classification.get(finding.classification, 0) + 1
            )
            blocking_counts_by_code[finding.code] = blocking_counts_by_code.get(finding.code, 0) + 1

    blocking_count = sum(1 for finding in findings if finding.blocking)
    status = "warning" if blocking_count else "success"
    if strict and blocking_count:
        status = "error"
    if status == "success" and any(finding.status == "warning" for finding in findings):
        status = "warning"

    return {
        "schema_version": 1,
        "status": status,
        "summary": {
            "total_paths": len(findings),
            "blocking_findings": blocking_count,
            "counts_by_classification": dict(sorted(counts_by_classification.items())),
            "counts_by_status": dict(sorted(counts_by_status.items())),
            "counts_by_code": dict(sorted(counts_by_code.items())),
            "blocking_counts_by_classification": dict(sorted(blocking_counts_by_classification.items())),
            "blocking_counts_by_code": dict(sorted(blocking_counts_by_code.items())),
        },
        "findings": [asdict(finding) for finding in findings],
        "metadata": {
            "service": SERVICE_ID,
            "inventory_scope": "tracked_existing_files",
            "strict": strict,
            "changed_files_policy": (
                "future_artifact_debt_blocking" if changed_files else "not_applied"
            ),
            "changed_file_count": len(changed_files or []),
            "next_steps": [
                _next_step(
                    "review",
                    "python3 Infrastructure/scripts/validation-and-linting/check_repo_surface_inventory.py --json",
                    "Inspect the full machine-readable inventory before changing tracked surfaces.",
                ),
                _next_step(
                    "policy",
                    "edit Docs/agents/15-repo-surface-ownership.md and the owning classifier rule",
                    "Encode canonical ownership instead of suppressing policy debt.",
                ),
                _next_step(
                    "safety",
                    "rg -n '<candidate-path-or-skill-name>' Skills Plugins Infrastructure Docs .skillsets .agents",
                    "Reference-scan candidates before any cleanup action.",
                ),
            ],
        },
    }


def print_human_report(report: dict[str, Any]) -> None:
    summary = report["summary"]
    print("Repo surface inventory")
    print(f"- status: {report['status']}")
    print(f"- tracked paths: {summary['total_paths']}")
    print(f"- blocking findings: {summary['blocking_findings']}")
    print("- counts by classification:")
    for classification, count in summary["counts_by_classification"].items():
        print(f"  - {classification}: {count}")
    print("- notable findings:")
    notable = [
        finding
        for finding in report["findings"]
        if finding["status"] in {"unknown", "violation"} or finding["severity"] == "error"
    ][:20]
    if not notable:
        print("  - none")
        return
    for finding in notable:
        print(
            "  - {path}: {classification}/{status} ({code})".format(
                path=finding["path"],
                classification=finding["classification"],
                status=finding["status"],
                code=finding["code"],
            )
        )
    if len(notable) < summary["blocking_findings"]:
        print(f"  - ... {summary['blocking_findings'] - len(notable)} more blocking findings")


def _build_report_for_args(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root or REPO_ROOT).resolve()
    changed_files = _load_changed_files(args, repo_root)
    debt_candidates = future_artifact_debt_candidates(repo_root, changed_files)
    paths = sorted(
        set(git_ls_files(repo_root))
        | {path for path in changed_files if (repo_root / path).exists()}
    )
    findings = classify_paths(paths, changed_files=debt_candidates)
    return build_report(findings, strict=args.strict, changed_files=changed_files)

def _load_changed_files(args: argparse.Namespace, repo_root: Path) -> list[str]:
    changed_files = [_normalize_path(path) for path in args.changed_files if str(path).strip()]
    if args.changed_files_from:
        changed_files_path = Path(args.changed_files_from)
        if not changed_files_path.is_absolute():
            changed_files_path = repo_root / changed_files_path
        changed_files.extend(
            _normalize_path(line)
            for line in changed_files_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    return sorted(set(changed_files))


def main() -> int:
    args = parse_args()
    try:
        report = _build_report_for_args(args)
    except Exception as exc:
        if args.json:
            print(json.dumps(error_report(args, exc), sort_keys=True))
        else:
            print(f"repo surface inventory failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, sort_keys=True)) if args.json else print_human_report(report)

    if args.strict and report["summary"]["blocking_findings"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
