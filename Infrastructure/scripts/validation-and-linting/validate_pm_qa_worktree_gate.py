#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


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
    "operator_approved_volatile_worktree_risk",
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
        payload.get("target_worktree"),
        _as_mapping(payload.get("qa_lane")).get("implementation_worktree"),
        _as_mapping(payload.get("missing_target")).get("implementation_worktree"),
        _as_mapping(payload.get("clean_execution_strategy")).get("path"),
        _as_mapping(payload.get("selected_strategy")).get("implementation_worktree_path"),
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
    return payload.get("qa_acceptance_status") == "not_proven" and "qa_lane" in payload


def _validate_preservation(payload: dict[str, Any], path: str) -> list[Finding]:
    findings: list[Finding] = []
    preservation = _preservation(payload)
    strategy = preservation.get("strategy")
    if strategy not in PRESERVATION_STRATEGIES:
        findings.append(
            Finding(
                path,
                "missing_durable_preservation_strategy",
                "QA dispatch over a temp worktree must record committed_branch, patch_artifact, "
                "or operator_approved_volatile_worktree_risk preservation.",
            )
        )
    if strategy == "patch_artifact":
        patch_path = preservation.get("patch_artifact")
        if not _non_empty_string(patch_path) or not Path(str(patch_path)).exists():
            findings.append(
                Finding(
                    f"{path}.patch_artifact",
                    "missing_patch_artifact",
                    "patch_artifact preservation must name an existing patch artifact.",
                )
            )
    if strategy == "committed_branch" and not _non_empty_string(preservation.get("branch")):
        findings.append(
            Finding(
                f"{path}.branch",
                "missing_preservation_branch",
                "committed_branch preservation must name the durable branch.",
            )
        )
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

    if worktree.startswith("/private/tmp/") or worktree.startswith("/tmp/"):
        findings.extend(_validate_preservation(payload, "durable_preservation"))
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
