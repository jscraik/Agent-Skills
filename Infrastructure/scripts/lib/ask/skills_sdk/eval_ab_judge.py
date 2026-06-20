from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ask.skills_sdk.eval_ab_rubric import canonical_ab_rubric, canonical_ab_rubric_digest


AB_JUDGE_PREVIEW_SCHEMA_VERSION = "skills-sdk.ab-judge-preview-receipt.v0"
AB_JUDGE_PREVIEW_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/ab-judge-preview-receipt.v0.schema.json"
)
DECISION_SCHEMA_VERSION = "skills-sdk.ab-judge-decision.v0"
ALLOWED_WINNERS = ["skill_a", "skill_b", "inconclusive"]


def _digest_text(value: str) -> str:
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def _digest_file(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def _resolve_receipt_path(repo_root: Path, run_receipt: str) -> tuple[Path | None, str | None]:
    candidate = Path(run_receipt)
    path = candidate if candidate.is_absolute() else repo_root / candidate
    try:
        resolved = path.resolve()
        resolved.relative_to(repo_root.resolve())
    except (OSError, ValueError):
        return None, "run_receipt_outside_repo"
    if not resolved.is_file():
        return resolved, "run_receipt_missing"
    return resolved, None


def _load_run_receipt(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, "run_receipt_invalid_json"
    if isinstance(payload, dict) and "receipt" in payload and isinstance(payload["receipt"], dict):
        payload = payload["receipt"]
    if not isinstance(payload, dict):
        return None, "run_receipt_not_object"
    if not _run_receipt_shape_valid(payload):
        return None, "run_receipt_contract_invalid"
    return payload, None


def _digest_like(value: object) -> bool:
    return isinstance(value, str) and len(value) >= 71 and value.startswith("sha256:")


def _object_field(payload: dict[str, Any], key: str) -> dict[str, Any] | None:
    value = payload.get(key)
    return value if isinstance(value, dict) else None


def _variant_labels(rows: object) -> set[str]:
    if not isinstance(rows, list):
        return set()
    return {row.get("variant_label") for row in rows if isinstance(row, dict)}


def _run_receipt_shape_valid(payload: dict[str, Any]) -> bool:
    return (
        _run_receipt_header_valid(payload)
        and _run_receipt_identity_valid(payload)
        and _run_receipt_variants_valid(payload)
    )


def _run_receipt_header_valid(payload: dict[str, Any]) -> bool:
    return (
        payload.get("schema_version") == "skills-sdk.ab-run-receipt.v0"
        and payload.get("operation") == "ab_run"
        and payload.get("status") in {"completed", "blocked"}
    )


def _run_receipt_identity_valid(payload: dict[str, Any]) -> bool:
    object_keys = ("skill_a", "skill_b", "fixture", "execution_profile", "judge_profile")
    experiment_id = payload.get("experiment_id")
    return all(_object_field(payload, key) is not None for key in object_keys) and isinstance(experiment_id, str) and len(experiment_id) == 16


def _run_receipt_variants_valid(payload: dict[str, Any]) -> bool:
    if _variant_labels(payload.get("variant_results")) != {"A", "B"}:
        return False
    if _variant_labels(payload.get("command_plan")) != {"A", "B"}:
        return False
    return all(_variant_result_digests_valid(result) for result in payload["variant_results"])


def _variant_result_digests_valid(result: object) -> bool:
    if not isinstance(result, dict):
        return False
    keys = ("output_last_message_digest", "runner_stdout_digest", "runner_stderr_digest")
    return all(_digest_like(result.get(key)) for key in keys)


def _evidence_row(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "variant_label": result["variant_label"],
        "status": result["status"],
        "exit_code": result["exit_code"],
        "sandbox_mode": result["sandbox_mode"],
        "output_last_message_digest": result["output_last_message_digest"],
        "runner_stdout_digest": result["runner_stdout_digest"],
        "runner_stderr_digest": result["runner_stderr_digest"],
        "blockers": result["blockers"],
    }


def _comparison_payload(run_receipt: dict[str, Any]) -> dict[str, Any]:
    rubric = canonical_ab_rubric()
    return {
        "schema_version": DECISION_SCHEMA_VERSION,
        "experiment_id": run_receipt["experiment_id"],
        "rubric": rubric,
        "rubric_digest": canonical_ab_rubric_digest(),
        "skill_a": {
            "package_id": run_receipt["skill_a"]["package_id"],
            "package_digest": run_receipt["skill_a"]["package_digest"],
        },
        "skill_b": {
            "package_id": run_receipt["skill_b"]["package_id"],
            "package_digest": run_receipt["skill_b"]["package_digest"],
        },
        "fixture": {
            "path": run_receipt["fixture"]["path"],
            "digest": run_receipt["fixture"]["digest"],
        },
        "execution_profile": run_receipt["execution_profile"]["id"],
        "variant_results": [_evidence_row(result) for result in run_receipt["variant_results"]],
        "allowed_winners": ALLOWED_WINNERS,
    }


def _judge_prompt(comparison_payload: dict[str, Any]) -> str:
    return (
        "You are judging a Skills SDK A/B eval from sanitized receipt evidence only.\n"
        "Do not infer from package names, local paths, hidden logs, or unavailable content.\n"
        "Use the embedded rubric exactly; do not change weights or criteria.\n"
        "Return JSON matching skills-sdk.ab-judge-decision.v0 with dimension_scores, "
        "reason_per_dimension, winner, confidence, reason, and evidence_refs.\n"
        "Choose inconclusive when the sanitized evidence is insufficient.\n\n"
        f"Evidence:\n{json.dumps(comparison_payload, sort_keys=True, indent=2)}\n"
    )


def build_ab_judge_preview_receipt(repo_root: Path, *, run_receipt: str) -> dict[str, Any]:
    inputs = _judge_inputs(repo_root, run_receipt)
    blockers = inputs["blockers"]
    loaded_receipt = inputs["loaded_receipt"]
    if loaded_receipt is not None and loaded_receipt["status"] != "completed":
        blockers.append("run_receipt_not_completed")

    comparison_payload, judge_prompt = _judge_input_payload(blockers, loaded_receipt)
    status = "preview" if not blockers else "blocked"
    return _judge_receipt_payload(status, blockers, inputs, loaded_receipt, comparison_payload, judge_prompt)


def _judge_inputs(repo_root: Path, run_receipt: str) -> dict[str, Any]:
    blockers: list[str] = []
    receipt_path, path_blocker = _resolve_receipt_path(repo_root, run_receipt)
    if path_blocker:
        blockers.append(path_blocker)
    receipt_path_label, receipt_digest, loaded_receipt, load_blocker = _load_receipt_inputs(
        repo_root,
        receipt_path,
        path_blocker,
    )
    if load_blocker:
        blockers.append(load_blocker)
    return {
        "blockers": blockers,
        "receipt_path_label": receipt_path_label,
        "receipt_digest": receipt_digest,
        "loaded_receipt": loaded_receipt,
    }


def _load_receipt_inputs(
    repo_root: Path,
    receipt_path: Path | None,
    path_blocker: str | None,
) -> tuple[str | None, str | None, dict[str, Any] | None, str | None]:
    if receipt_path is None or path_blocker:
        return None, None, None, None
    loaded_receipt, _load_blocker = _load_run_receipt(receipt_path)
    return _repo_relative(repo_root, receipt_path), _digest_file(receipt_path), loaded_receipt, _load_blocker


def _judge_input_payload(
    blockers: list[str],
    loaded_receipt: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, str | None]:
    if blockers or loaded_receipt is None:
        return None, None
    comparison_payload = _comparison_payload(loaded_receipt)
    return comparison_payload, _judge_prompt(comparison_payload)


def _judge_receipt_payload(
    status: str,
    blockers: list[str],
    inputs: dict[str, Any],
    loaded_receipt: dict[str, Any] | None,
    comparison_payload: dict[str, Any] | None,
    judge_prompt: str | None,
) -> dict[str, Any]:
    return {
        "schema_version": AB_JUDGE_PREVIEW_SCHEMA_VERSION,
        "schema_uri": AB_JUDGE_PREVIEW_SCHEMA_URI,
        "status": status,
        "operation": "ab_judge_preview",
        "run_receipt_path": inputs["receipt_path_label"],
        "run_receipt_digest": inputs["receipt_digest"],
        "experiment_id": None if loaded_receipt is None else loaded_receipt["experiment_id"],
        "judge_profile": None if loaded_receipt is None else loaded_receipt["judge_profile"],
        "rubric_id": None if comparison_payload is None else comparison_payload["rubric"]["rubric_id"],
        "rubric_digest": None if comparison_payload is None else comparison_payload["rubric_digest"],
        "comparison_payload": comparison_payload,
        "judge_prompt_digest": None if judge_prompt is None else _digest_text(judge_prompt),
        "decision_schema_version": DECISION_SCHEMA_VERSION,
        "allowed_winners": ALLOWED_WINNERS,
        "calibration_required": True,
        "provider_invoked": False,
        "network_accessed": False,
        "mutation_performed": False,
        "blockers": blockers,
        "acceptance_trace": ["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022", "VP-030"],
        "agent_summary": (
            "A/B judge preview is ready; no judge provider has been invoked."
            if status == "preview"
            else f"A/B judge preview is blocked: {', '.join(blockers)}."
        ),
    }
