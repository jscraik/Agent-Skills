from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from ask.skills_sdk.typed_contracts import (
    validate_eval_run_receipt,
    validate_observability_feedback_receipt,
    validate_package_digest_receipt,
)


OBSERVABILITY_PROMOTION_SCHEMA_VERSION = "skills-sdk.observability-promotion-receipt.v0"
OBSERVABILITY_PROMOTION_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/observability-promotion-receipt.v0.schema.json"
)
OBSERVABILITY_PROMOTION_ACCEPTANCE_TRACE = ["PU-026", "FR-003", "FR-008", "SA-003", "VP-026"]
REQUIRED_RECEIPTS = ["package_digest_receipt", "eval_run_receipt"]
_REQUIRED_RECEIPTS_SET = set(REQUIRED_RECEIPTS)


def _digest_file(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def _path_allowed(repo_root: Path, path: Path) -> bool:
    try:
        resolved = path.resolve()
    except OSError:
        return False
    try:
        resolved.relative_to(repo_root.resolve())
        return True
    except (OSError, ValueError):
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
            return True
        except (OSError, ValueError):
            return False


def _resolve_input_path(repo_root: Path, path_value: str, label: str) -> tuple[Path | None, str | None]:
    candidate = Path(path_value)
    path = candidate if candidate.is_absolute() else repo_root / candidate
    if not _path_allowed(repo_root, path):
        return None, f"{label}_path_disallowed"
    if not path.is_file():
        return path, f"{label}_path_missing"
    return path, None


def _unwrap_receipt(payload: object, data_key: str) -> object:
    if not isinstance(payload, dict):
        return payload
    if isinstance(payload.get("receipt"), dict):
        return payload["receipt"]
    data = payload.get("data")
    if isinstance(data, dict):
        command_payload = data.get(data_key)
        if isinstance(command_payload, dict) and isinstance(command_payload.get("receipt"), dict):
            return command_payload["receipt"]
    return payload


def _load_receipt(path: Path, data_key: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, "invalid_json"
    receipt = _unwrap_receipt(payload, data_key)
    if not isinstance(receipt, dict):
        return None, "receipt_not_object"
    return receipt, None


def _receipt_input(repo_root: Path, path_value: str, label: str, data_key: str) -> dict[str, Any]:
    path, path_blocker = _resolve_input_path(repo_root, path_value, label)
    result: dict[str, Any] = {
        "path": None if path is None else _repo_relative(repo_root, path),
        "digest": None,
        "receipt": None,
        "blockers": [],
    }
    if path_blocker:
        result["blockers"].append(path_blocker)
        return result
    if path is None:
        result["blockers"].append(f"{label}_path_missing")
        return result
    receipt, load_blocker = _load_receipt(path, data_key)
    if load_blocker:
        result["blockers"].append(f"{label}_{load_blocker}")
    else:
        result["digest"] = _digest_file(path)
        result["receipt"] = receipt
    return result


def _check(check_id: str, status: str, message: str, evidence: list[str]) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": status,
        "severity": "blocker",
        "message": message,
        "evidence": evidence,
    }


def _candidate_rows(feedback_receipt: dict[str, Any] | None) -> list[dict[str, Any]]:
    if feedback_receipt is None:
        return []
    rows = feedback_receipt.get("scenario_candidates", []) + feedback_receipt.get("skill_gap_candidates", [])
    return [row for row in rows if isinstance(row, dict)]


def _identity_blockers(
    feedback_receipt: dict[str, Any] | None,
    package_receipt: dict[str, Any] | None,
    eval_receipt: dict[str, Any] | None,
) -> list[str]:
    blockers: list[str] = []
    if feedback_receipt is None or package_receipt is None or eval_receipt is None:
        return blockers
    package_id = feedback_receipt.get("package_id")
    package_digest = feedback_receipt.get("package_digest")
    if package_receipt.get("package_id") != package_id:
        blockers.append("package_receipt_package_id_mismatch")
    if package_receipt.get("package_digest") != package_digest:
        blockers.append("package_receipt_package_digest_mismatch")
    if eval_receipt.get("package_id") != package_id:
        blockers.append("eval_receipt_package_id_mismatch")
    if eval_receipt.get("package_digest") != package_digest:
        blockers.append("eval_receipt_package_digest_mismatch")
    return blockers


def _contract_blockers(
    feedback_receipt: dict[str, Any] | None,
    package_receipt: dict[str, Any] | None,
    eval_receipt: dict[str, Any] | None,
) -> list[str]:
    blockers: list[str] = []
    if feedback_receipt is None:
        blockers.append("feedback_receipt_missing")
    elif feedback_receipt.get("schema_version") != "skills-sdk.observability-feedback-receipt.v0":
        blockers.append("feedback_receipt_schema_mismatch")
    elif feedback_receipt.get("status") != "preview":
        blockers.append("feedback_receipt_not_preview")

    if package_receipt is None:
        blockers.append("package_receipt_missing")
    elif package_receipt.get("schema_version") != "skills-sdk.package-digest-receipt.v0":
        blockers.append("package_receipt_schema_mismatch")
    elif package_receipt.get("status") != "built":
        blockers.append("package_receipt_not_built")

    if eval_receipt is None:
        blockers.append("eval_receipt_missing")
    elif eval_receipt.get("schema_version") != "skills-sdk.eval-run-receipt.v0":
        blockers.append("eval_receipt_schema_mismatch")
    elif eval_receipt.get("status") != "pass":
        blockers.append("eval_receipt_not_pass")
    blockers.extend(
        _contract_validation_blockers(
            feedback_receipt=feedback_receipt,
            package_receipt=package_receipt,
            eval_receipt=eval_receipt,
        )
    )
    return blockers


def _contract_validation_blockers(
    *,
    feedback_receipt: dict[str, Any] | None,
    package_receipt: dict[str, Any] | None,
    eval_receipt: dict[str, Any] | None,
) -> list[str]:
    blockers: list[str] = []
    for label, receipt, validator in (
        ("feedback_receipt", feedback_receipt, validate_observability_feedback_receipt),
        ("package_receipt", package_receipt, validate_package_digest_receipt),
        ("eval_receipt", eval_receipt, validate_eval_run_receipt),
    ):
        if receipt is None:
            continue
        try:
            validator(receipt)
        except ValueError:
            blockers.append(f"{label}_contract_invalid")
    return blockers


def _candidate_blockers(candidate: dict[str, Any], package_id: str | None) -> list[str]:
    blockers: list[str] = []
    if candidate.get("promotion_status") != "blocked_pending_package_eval":
        blockers.append("candidate_not_waiting_for_package_eval")
    if candidate.get("skill_id") != package_id:
        blockers.append("candidate_skill_id_mismatch")
    required = candidate.get("required_receipts")
    if (
        not isinstance(required, list)
        or len(required) != len(REQUIRED_RECEIPTS)
        or len(set(required)) != len(required)
        or set(required) != _REQUIRED_RECEIPTS_SET
    ):
        blockers.append("candidate_required_receipts_mismatch")
    return blockers


def _candidate_decisions(
    feedback_receipt: dict[str, Any] | None,
    global_blockers: list[str],
) -> list[dict[str, Any]]:
    package_id = feedback_receipt.get("package_id") if feedback_receipt else None
    decisions: list[dict[str, Any]] = []
    for candidate in _candidate_rows(feedback_receipt):
        blockers = [
            *global_blockers,
            *_candidate_blockers(candidate, package_id if isinstance(package_id, str) else None),
        ]
        promotion_ready = not blockers
        decisions.append(
            {
                "id": str(candidate.get("id", "")),
                "candidate_type": candidate.get("candidate_type"),
                "source_event_digest": candidate.get("source_event_digest"),
                "skill_id": candidate.get("skill_id"),
                "decision": "promotion_ready" if promotion_ready else "blocked",
                "promotion_status": "promotion_ready" if promotion_ready else "blocked_pending_package_eval",
                "required_receipts": REQUIRED_RECEIPTS,
                "evidence_refs": ["feedback_receipt", "package_digest_receipt", "eval_run_receipt"],
                "blockers": blockers,
            }
        )
    return decisions


def _receipt_inputs(
    repo_root: Path,
    *,
    feedback_receipt_path: str,
    package_receipt_path: str,
    eval_run_receipt_path: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        _receipt_input(
            repo_root,
            feedback_receipt_path,
            "feedback_receipt",
            "skills_sdk_observability_feedback",
        ),
        _receipt_input(
            repo_root,
            package_receipt_path,
            "package_receipt",
            "skills_sdk_package_build",
        ),
        _receipt_input(
            repo_root,
            eval_run_receipt_path,
            "eval_run_receipt",
            "skills_sdk_eval_run",
        ),
    )


def _all_blockers(
    feedback_input: dict[str, Any],
    package_input: dict[str, Any],
    eval_input: dict[str, Any],
) -> list[str]:
    feedback_receipt = feedback_input["receipt"]
    package_receipt = package_input["receipt"]
    eval_receipt = eval_input["receipt"]
    return [
        *feedback_input["blockers"],
        *package_input["blockers"],
        *eval_input["blockers"],
        *_contract_blockers(feedback_receipt, package_receipt, eval_receipt),
        *_identity_blockers(feedback_receipt, package_receipt, eval_receipt),
    ]


def _receipt_paths_present(blockers: list[str]) -> bool:
    return not [
        blocker
        for blocker in blockers
        if blocker.endswith("_missing") or blocker.endswith("_disallowed")
    ]


def _receipt_contract_state_blockers(blockers: list[str]) -> list[str]:
    state_suffixes = (
        "_contract_invalid",
        "_schema_mismatch",
        "_not_preview",
        "_not_built",
        "_not_pass",
    )
    return [blocker for blocker in blockers if blocker.endswith(state_suffixes)]


def _promotion_checks(
    blockers: list[str],
    feedback_input: dict[str, Any],
    package_input: dict[str, Any],
    eval_input: dict[str, Any],
) -> list[dict[str, Any]]:
    feedback_receipt = feedback_input["receipt"]
    eval_receipt = eval_input["receipt"]
    contract_blockers = _receipt_contract_state_blockers(blockers)
    return [
        _check(
            "receipts_present",
            "pass" if _receipt_paths_present(blockers) else "blocker",
            "Feedback, package, and eval receipts must be present under repo or temporary paths.",
            [str(feedback_input["path"]), str(package_input["path"]), str(eval_input["path"])],
        ),
        _check(
            "receipts_bind_same_package",
            "pass" if "mismatch" not in " ".join(blockers) else "blocker",
            "Feedback, package, and eval receipts must bind to the same package id and digest.",
            [str(feedback_receipt.get("package_id"))] if isinstance(feedback_receipt, dict) else [],
        ),
        _check(
            "receipt_contracts_valid",
            "pass" if not contract_blockers else "blocker",
            "Promotion preview requires schema-valid feedback, package, and eval receipts in the expected states.",
            contract_blockers,
        ),
        _check(
            "eval_receipt_passes",
            "pass" if isinstance(eval_receipt, dict) and eval_receipt.get("status") == "pass" else "blocker",
            "Promotion preview requires a passing eval-run receipt.",
            [str(eval_receipt.get("status"))] if isinstance(eval_receipt, dict) else [],
        ),
    ]


def _decision_blockers(decisions: list[dict[str, Any]]) -> list[str]:
    return [
        blocker
        for decision in decisions
        for blocker in decision.get("blockers", [])
        if isinstance(blocker, str)
    ]


def _top_level_blockers(
    checks: list[dict[str, Any]],
    blockers: list[str],
    decisions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    blocking_checks = [check for check in checks if check["status"] == "blocker"]
    surfaced = {
        evidence
        for check in blocking_checks
        for evidence in check.get("evidence", [])
        if isinstance(evidence, str)
    }
    unsurfaced = list(
        dict.fromkeys(
            blocker
            for blocker in [*blockers, *_decision_blockers(decisions)]
            if blocker not in surfaced
        )
    )
    if unsurfaced:
        blocking_checks.append(
            _check(
                "promotion_blockers",
                "blocker",
                "Promotion preview blockers must be preserved as receipt evidence.",
                unsurfaced,
            )
        )
    return blocking_checks


def _status(decisions: list[dict[str, Any]]) -> str:
    if decisions and all(decision["decision"] == "promotion_ready" for decision in decisions):
        return "preview"
    return "blocked"


def _agent_summary(status: str, ready_count: int, decision_count: int, blocked_count: int, blocker_count: int) -> str:
    if status == "preview":
        return f"observability promotion preview marked {ready_count} of {decision_count} candidate(s) ready."
    return f"observability promotion preview blocked {blocked_count or blocker_count} candidate(s)."


def _receipt_payload(
    *,
    status: str,
    feedback_input: dict[str, Any],
    package_input: dict[str, Any],
    eval_input: dict[str, Any],
    decisions: list[dict[str, Any]],
    checks: list[dict[str, Any]],
    blockers: list[str],
) -> dict[str, Any]:
    feedback_receipt = feedback_input["receipt"]
    ready_count = sum(1 for decision in decisions if decision["decision"] == "promotion_ready")
    blocked_count = len(decisions) - ready_count
    package_id = feedback_receipt.get("package_id") if isinstance(feedback_receipt, dict) else None
    package_digest = feedback_receipt.get("package_digest") if isinstance(feedback_receipt, dict) else None
    return {
        "schema_version": OBSERVABILITY_PROMOTION_SCHEMA_VERSION,
        "schema_uri": OBSERVABILITY_PROMOTION_SCHEMA_URI,
        "status": status,
        "operation": "observability_promotion_preview",
        "package_id": package_id if isinstance(package_id, str) else None,
        "package_digest": package_digest if isinstance(package_digest, str) else None,
        "feedback_receipt_path": feedback_input["path"],
        "feedback_receipt_digest": feedback_input["digest"],
        "package_receipt_path": package_input["path"],
        "package_receipt_digest": package_input["digest"],
        "eval_run_receipt_path": eval_input["path"],
        "eval_run_receipt_digest": eval_input["digest"],
        "candidate_count": len(decisions),
        "promotion_ready_count": ready_count,
        "blocked_count": blocked_count,
        "candidate_decisions": decisions,
        "promotion_checks": checks,
        "blockers": _top_level_blockers(checks, blockers, decisions),
        "mutation_performed": False,
        "acceptance_trace": OBSERVABILITY_PROMOTION_ACCEPTANCE_TRACE,
        "agent_summary": _agent_summary(status, ready_count, len(decisions), blocked_count, len(blockers)),
    }


def build_observability_promotion_receipt(
    repo_root: Path,
    *,
    feedback_receipt_path: str,
    package_receipt_path: str,
    eval_run_receipt_path: str,
) -> dict[str, Any]:
    feedback_input, package_input, eval_input = _receipt_inputs(
        repo_root,
        feedback_receipt_path=feedback_receipt_path,
        package_receipt_path=package_receipt_path,
        eval_run_receipt_path=eval_run_receipt_path,
    )
    feedback_receipt = feedback_input["receipt"]
    blockers = _all_blockers(feedback_input, package_input, eval_input)
    decisions = _candidate_decisions(feedback_receipt, blockers)
    if feedback_receipt is not None and not decisions:
        blockers.append("feedback_receipt_has_no_candidates")
        decisions = _candidate_decisions(feedback_receipt, blockers)

    status = _status(decisions)
    checks = _promotion_checks(blockers, feedback_input, package_input, eval_input)
    return _receipt_payload(
        status=status,
        feedback_input=feedback_input,
        package_input=package_input,
        eval_input=eval_input,
        decisions=decisions,
        checks=checks,
        blockers=blockers,
    )
