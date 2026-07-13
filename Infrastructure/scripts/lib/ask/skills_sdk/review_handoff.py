from __future__ import annotations

import json
from pathlib import Path

from ask.skills_sdk.review_plan import (
    REVIEW_PLAN_SCHEMA_VERSION,
    TRACE_DIR,
    canonical_receipt_digest,
    _head_sha,
    _repo_relative,
    _target_info,
)


REVIEW_HANDOFF_SCHEMA_VERSION = "skills-sdk.review-handoff-receipt.v1"
REVIEW_HANDOFF_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/sdk-review-handoff-receipt.v1.schema.json"
)


def build_review_handoff(
    repo_root: Path,
    *,
    plan_path: str,
    target: str,
    task_intent: str,
    receipt_out: str | None = None,
) -> dict[str, object]:
    source_plan_path = _safe_input_path(repo_root, plan_path)
    source_plan = _load_json_object(source_plan_path)
    _validate_source_plan_shape(source_plan)

    source_context_raw = source_plan.get("source_context")
    if not isinstance(source_context_raw, dict):
        raise ValueError("source review plan source_context must be an object.")
    source_context = source_context_raw

    plan_intent = source_plan.get("task_intent")
    if not isinstance(plan_intent, str) or not plan_intent:
        raise ValueError("source review plan task_intent must be a non-empty string.")
    if plan_intent != task_intent:
        raise ValueError("handoff intent must match the source review plan intent.")

    _validate_source_context(repo_root, source_context=source_context, target=target)
    receipt_instance_id = source_context.get("receipt_instance_id")
    if not isinstance(receipt_instance_id, str) or not receipt_instance_id:
        raise ValueError("source_context receipt_instance_id must be a non-empty string.")

    receipt_sha256 = canonical_receipt_digest(source_plan)
    trace_path = repo_root / TRACE_DIR / f"{receipt_sha256}.trace.json"
    trace = _load_json_object(trace_path)
    _validate_trace(
        repo_root,
        trace=trace,
        source_plan=source_plan,
        source_plan_path=source_plan_path,
        receipt_sha256=receipt_sha256,
    )

    receipt: dict[str, object] = {
        "schema_version": REVIEW_HANDOFF_SCHEMA_VERSION,
        "schema_uri": REVIEW_HANDOFF_SCHEMA_URI,
        "status": "pass",
        "source_review_plan": {
            "path": _repo_relative(repo_root, source_plan_path),
            "schema_version": source_plan["schema_version"],
            "receipt_sha256": receipt_sha256,
            "receipt_instance_id": receipt_instance_id,
        },
        "source_context": source_context,
        "source_trace": {
            "path": _repo_relative(repo_root, trace_path),
            "receipt_sha256": trace["receipt_sha256"],
            "receipt_instance_id": trace["receipt_instance_id"],
            "branch_policy": trace["branch_policy"],
        },
        "target": target,
        "target_kind": source_context["target_kind"],
        "task_intent": task_intent,
        "selected_lenses": _selected_lens_ids(source_plan),
        "reviewer_roles": _reviewer_roles(source_plan),
        "required_artifacts": _required_artifacts(source_plan),
        "evidence_boundaries": [
            "local code/test truth is separate from PR, CI, review-thread, tracker, and merge-readiness truth",
            "review handoff receipt does not prove reviewer execution",
            "review handoff receipt does not prove external service state",
        ],
        "not_proven": [
            "reviewers_completed",
            "ci_passed",
            "pr_mergeable",
            "review_threads_resolved",
            "tracker_updated",
        ],
        "next_commands": _next_commands(source_plan, target=target, task_intent=task_intent),
        "mutation_performed": False,
        "receipt_written": False,
        "receipt_path": None,
    }
    if receipt_out:
        output_path = _safe_output_path(repo_root, receipt_out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        receipt["receipt_written"] = True
        receipt["receipt_path"] = _repo_relative(repo_root, output_path)
        output_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def _load_json_object(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"required JSON file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"required JSON file must contain an object: {path}")
    return payload


def _validate_source_plan_shape(source_plan: dict[str, object]) -> None:
    if source_plan.get("schema_version") != REVIEW_PLAN_SCHEMA_VERSION:
        raise ValueError("source review plan schema_version is unsupported.")
    if source_plan.get("status") != "pass":
        raise ValueError("source review plan must have pass status.")
    if "source_context" not in source_plan:
        raise ValueError("source review plan is missing source_context.")
    target = source_plan.get("target")
    if not isinstance(target, str) or not target:
        raise ValueError("source review plan target must be a non-empty string.")
    if source_plan.get("receipt_written") is not True:
        raise ValueError("source review plan must be written with --receipt-out before handoff.")
    receipt_path = source_plan.get("receipt_path")
    if not isinstance(receipt_path, str) or not receipt_path:
        raise ValueError("source review plan receipt_path must be a non-empty string.")
    selected_lenses = source_plan.get("selected_lenses")
    if not isinstance(selected_lenses, list) or not selected_lenses:
        raise ValueError("source review plan must include selected_lenses.")


def _validate_trace(
    repo_root: Path,
    *,
    trace: dict[str, object],
    source_plan: dict[str, object],
    source_plan_path: Path,
    receipt_sha256: str,
) -> None:
    source_context_raw = source_plan.get("source_context")
    if not isinstance(source_context_raw, dict):
        raise ValueError("source review plan source_context must be an object.")
    receipt_instance_id = source_context_raw.get("receipt_instance_id")
    if not isinstance(receipt_instance_id, str) or not receipt_instance_id:
        raise ValueError("source_context receipt_instance_id must be a non-empty string.")
    expected = {
        "schema_version": "skills-sdk.review-plan-trace.v1",
        "receipt_sha256": receipt_sha256,
        "receipt_instance_id": receipt_instance_id,
        "branch_policy": "same_head_required",
    }
    for key, expected_value in expected.items():
        if trace.get(key) != expected_value:
            raise ValueError(f"review plan trace {key} does not match the source receipt.")
    trace_receipt_path = trace.get("receipt_path")
    if not isinstance(trace_receipt_path, str) or not trace_receipt_path:
        raise ValueError("review plan trace receipt_path is missing.")
    if _safe_input_path(repo_root, trace_receipt_path) != source_plan_path:
        raise ValueError("review plan trace receipt_path does not match the supplied --plan path.")
    for key in (
        "repo_root",
        "head_sha",
        "branch",
        "target_identity",
        "target_resolved_path",
        "target_content_digest",
        "target_digest_status",
    ):
        if trace.get(key) != source_context_raw.get(key):
            raise ValueError(f"review plan trace {key} does not match source_context.")


def _validate_source_context(repo_root: Path, *, source_context: dict[str, object], target: str) -> None:
    required = {
        "repo_root",
        "head_sha",
        "branch",
        "branch_policy",
        "receipt_instance_id",
        "receipt_created_at",
        "target_input",
        "target_kind",
        "target_identity",
        "target_resolved_path",
        "target_content_digest",
        "target_digest_status",
        "provenance_risk_flags",
    }
    missing = sorted(key for key in required if key not in source_context)
    if missing:
        raise ValueError(f"source_context is missing required fields: {', '.join(missing)}.")
    if source_context["repo_root"] != str(repo_root.resolve()):
        raise ValueError("source_context repo_root does not match the current repository.")
    if source_context["branch_policy"] != "same_head_required":
        raise ValueError("source_context branch_policy is unsupported.")
    if source_context["head_sha"] != _head_sha(repo_root):
        raise ValueError("source_context head_sha is stale.")
    if source_context["target_kind"] == "unresolved_handle":
        raise ValueError("review handoff requires a path-backed target; unresolved handles fail closed.")
    if source_context["target_digest_status"] != "available":
        raise ValueError("review handoff requires a supported target digest.")
    if source_context["provenance_risk_flags"]:
        raise ValueError("review handoff requires empty provenance_risk_flags.")

    current_target_info = _target_info(repo_root, target)
    for key in (
        "target_kind",
        "target_identity",
        "target_resolved_path",
        "target_content_digest",
        "target_digest_status",
    ):
        if current_target_info.get(key) != source_context.get(key):
            raise ValueError(f"source_context {key} is stale or mismatched.")


def validate_handoff_current_head(repo_root: Path, source_handoff: dict[str, object]) -> None:
    """Reject execution or verification against a stale same-head handoff."""
    source_context = source_handoff.get("source_context")
    if not isinstance(source_context, dict):
        raise ValueError("source review handoff source_context must be an object.")
    if source_context.get("branch_policy") != "same_head_required":
        raise ValueError("source review handoff branch_policy is unsupported.")
    if source_context.get("head_sha") != _head_sha(repo_root):
        raise ValueError("source_context head_sha is stale.")


def _selected_lens_ids(source_plan: dict[str, object]) -> list[str]:
    selected = source_plan["selected_lenses"]
    if not isinstance(selected, list):
        return []
    lens_ids: list[str] = []
    for lens in selected:
        if isinstance(lens, dict) and isinstance(lens.get("id"), str):
            lens_ids.append(lens["id"])
    if not lens_ids:
        raise ValueError("source review plan selected_lenses do not include lens ids.")
    return lens_ids


def _reviewer_roles(source_plan: dict[str, object]) -> list[str]:
    lens_ids = set(_selected_lens_ids(source_plan))
    roles = ["correctness-reviewer", "testing-reviewer"]
    if any("architecture" in lens_id or "design" in lens_id for lens_id in lens_ids):
        roles.append("architecture-strategist")
    if any("security" in lens_id for lens_id in lens_ids):
        roles.append("security-reviewer")
    if any("agent" in lens_id or "workflow" in lens_id for lens_id in lens_ids):
        roles.append("agent-native-reviewer")
    return sorted(set(roles))


def _required_artifacts(source_plan: dict[str, object]) -> list[str]:
    target = str(source_plan["target"]).replace("/", "-")
    return [
        f"artifacts/reviews/sdk-review-handoff/{target}/review-summary.md",
        f"artifacts/reviews/sdk-review-handoff/{target}/reviewer-findings.json",
        f"artifacts/reviews/sdk-review-handoff/{target}/validation-evidence.json",
    ]


def _next_commands(source_plan: dict[str, object], *, target: str, task_intent: str) -> list[str]:
    commands = [
        f"./bin/ask sdk review handoff --plan {source_plan['receipt_path']} --target {target} --intent {task_intent} --json --robot",
        "Run the bounded reviewer set named in data.review_handoff.reviewer_roles.",
        "Collect every required artifact before claiming review completion.",
    ]
    return commands


def _safe_input_path(repo_root: Path, path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    resolved_repo = repo_root.resolve()
    resolved = candidate.resolve()
    try:
        resolved.relative_to(resolved_repo)
    except ValueError as exc:
        raise ValueError("plan path must resolve inside the repository root.") from exc
    return resolved


def _safe_output_path(repo_root: Path, path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    resolved_repo = repo_root.resolve()
    resolved = candidate.resolve()
    try:
        resolved.relative_to(resolved_repo)
    except ValueError as exc:
        raise ValueError("receipt_out must resolve inside the repository root.") from exc
    return resolved
