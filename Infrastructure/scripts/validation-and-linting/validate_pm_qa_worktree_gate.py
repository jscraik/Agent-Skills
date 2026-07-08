#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]


ACTIVE_STATUSES = {
    "project_backed_qa_dispatched_monitoring_required",
    "qa_dispatched",
    "qa_unblocked",
    "pm_worker_recovery_implemented_request_qa",
}
BLOCKED_STATUSES = {
    "blocked_missing_implementation_worktree",
    "qa_artifacts_present_but_permission_context_not_acceptable",
    "qa_failed_artifact_contract",
}
PRESERVATION_STRATEGIES = {
    "committed_branch",
    "patch_artifact",
}


@dataclass(frozen=True)
class Finding:
    path: str
    code: str
    message: str


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _worktree_path(payload: dict[str, Any]) -> str | None:
    candidates = [
        payload.get("implementation_worktree"),
        _as_mapping(payload.get("qa_lane")).get("implementation_worktree"),
        _as_mapping(payload.get("selected_strategy")).get("implementation_worktree_path"),
        _as_mapping(payload.get("missing_target")).get("implementation_worktree"),
        payload.get("target_worktree"),
        _as_mapping(payload.get("clean_execution_strategy")).get("path"),
    ]
    for candidate in candidates:
        if _non_empty_string(candidate):
            return str(candidate)
    return None


def _preservation(payload: dict[str, Any]) -> dict[str, Any]:
    for key in ("durable_preservation", "preservation_strategy", "implementation_preservation"):
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _is_active(payload: dict[str, Any]) -> bool:
    status = payload.get("status")
    if status in BLOCKED_STATUSES:
        return False
    if status in ACTIVE_STATUSES:
        return True
    if payload.get("qa_acceptance_status") == "not_proven" and "qa_lane" in payload:
        return True
    # Unknown status: fail closed rather than silently skipping checks.
    return True


def _resolved_or_absolute(path: Path) -> Path:
    try:
        return path.resolve()
    except OSError:
        return path.absolute()


def _path_is_relative_to(path: Path, parent: Path) -> bool:
    resolved = _resolved_or_absolute(path)
    resolved_parent = _resolved_or_absolute(parent)
    return resolved == resolved_parent or resolved_parent in resolved.parents


def _is_temp_worktree(path: Path) -> bool:
    temp_root = Path(tempfile.gettempdir()).resolve()
    resolved = _resolved_or_absolute(path)
    return resolved == temp_root or temp_root in resolved.parents


def _is_repo_backed(path: Path) -> bool:
    return _path_is_relative_to(path, REPO_ROOT)


def _volatile_strategy_finding(path: str, strategy: Any) -> list[Finding]:
    if strategy == "operator_approved_volatile_worktree_risk":
        return [
            Finding(
                path,
                "volatile_preservation_not_durable",
                "operator_approved_volatile_worktree_risk is blocker evidence, not durable proof for active QA dispatch.",
            )
        ]
    if strategy not in PRESERVATION_STRATEGIES:
        return [
            Finding(
                path,
                "missing_durable_preservation_strategy",
                "QA dispatch over a temp worktree must record committed_branch or patch_artifact preservation.",
            )
        ]
    return []


def _validate_patch_artifact(preservation: dict[str, Any], path: str, worktree_path: Path) -> list[Finding]:
    patch_path = preservation.get("patch_artifact")
    if not _non_empty_string(patch_path) or not Path(str(patch_path)).exists():
        return [
            Finding(
                f"{path}.patch_artifact",
                "missing_patch_artifact",
                "patch_artifact preservation must name an existing patch artifact.",
            )
        ]
    patch_artifact_path = Path(str(patch_path))
    if _path_is_relative_to(patch_artifact_path, worktree_path) or (
        _is_temp_worktree(patch_artifact_path) and not _is_repo_backed(patch_artifact_path)
    ):
        return [
            Finding(
                f"{path}.patch_artifact",
                "volatile_patch_artifact",
                "patch_artifact preservation must point at repo-backed or otherwise non-temp durable storage.",
            )
        ]
    return []


def _validate_committed_branch(preservation: dict[str, Any], path: str) -> list[Finding]:
    findings: list[Finding] = []
    if not _non_empty_string(preservation.get("branch")):
        findings.append(
            Finding(
                f"{path}.branch",
                "missing_preservation_branch",
                "committed_branch preservation must name the durable branch.",
            )
        )
    if not _non_empty_string(preservation.get("commit")) and not _non_empty_string(preservation.get("commit_sha")):
        findings.append(
            Finding(
                f"{path}.commit",
                "missing_preservation_commit",
                "committed_branch preservation must record the commit or commit_sha that carries the implementation proof.",
            )
        )
    return findings


def _validate_preservation(payload: dict[str, Any], path: str, worktree_path: Path) -> list[Finding]:
    preservation = _preservation(payload)
    strategy = preservation.get("strategy")
    findings = _volatile_strategy_finding(path, strategy)
    if strategy == "patch_artifact":
        findings.extend(_validate_patch_artifact(preservation, path, worktree_path))
    if strategy == "committed_branch":
        findings.extend(_validate_committed_branch(preservation, path))
    return findings


def validate_payload(payload: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    worktree = _worktree_path(payload)
    if not worktree:
        findings.append(
            Finding(
                "$",
                "missing_implementation_worktree",
                "PM/QA dispatch receipts must name the implementation worktree they validate.",
            )
        )
        return findings

    if not _is_active(payload):
        return findings

    worktree_path = Path(worktree)
    if not worktree_path.exists():
        findings.append(
            Finding(
                "implementation_worktree",
                "implementation_worktree_missing",
                "QA cannot be dispatched or accepted while the implementation worktree is absent.",
            )
        )
    elif not worktree_path.is_dir():
        findings.append(
            Finding(
                "implementation_worktree",
                "implementation_worktree_not_directory",
                "implementation_worktree must be a readable directory.",
            )
        )

    if _is_temp_worktree(worktree_path):
        findings.extend(_validate_preservation(payload, "durable_preservation", worktree_path))
    return findings


def _load_payload(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(payload, dict):
        return None, "json root must be an object"
    return payload, None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate PM QA worktree readiness receipts.")
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    findings: list[Finding] = []
    for path in args.paths:
        payload, error = _load_payload(path)
        if payload is None:
            findings.append(Finding(path.as_posix(), "invalid_json", error or "could not read JSON"))
            continue
        for finding in validate_payload(payload):
            findings.append(Finding(f"{path.as_posix()}:{finding.path}", finding.code, finding.message))

    result = {
        "schema_version": "pm-qa-worktree-gate-validation/v1",
        "status": "pass" if not findings else "fail",
        "findings": [asdict(finding) for finding in findings],
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["status"])
        for finding in findings:
            print(f"{finding.path}: {finding.code}: {finding.message}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
