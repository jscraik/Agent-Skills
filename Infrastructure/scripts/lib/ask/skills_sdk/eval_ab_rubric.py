from __future__ import annotations

import hashlib
import json
from typing import Any


AB_RUBRIC_SCHEMA_VERSION = "skills-sdk.ab-rubric-receipt.v0"
AB_RUBRIC_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/ab-rubric-receipt.v0.schema.json"
)
AB_RUBRIC_ID = "skills-sdk.ab-rubric.v0"
AB_RUBRIC_VERSION = "v0"
AB_RUBRIC_DIMENSIONS = [
    {
        "id": "task_success",
        "title": "Task success",
        "description": "Variant satisfies the fixture objective and produces the requested outcome.",
        "weight": 0.30,
        "required_evidence": ["variant_result", "output_last_message_digest", "validation_results"],
    },
    {
        "id": "instruction_following",
        "title": "Instruction following",
        "description": "Variant follows the skill, fixture, repository, and safety instructions without scope drift.",
        "weight": 0.20,
        "required_evidence": ["variant_result", "runner_stdout_digest", "blockers"],
    },
    {
        "id": "evidence_quality",
        "title": "Evidence quality",
        "description": "Variant leaves reviewable evidence with clear command, output, and receipt references.",
        "weight": 0.20,
        "required_evidence": ["runner_stdout_digest", "runner_stderr_digest", "output_last_message_digest"],
    },
    {
        "id": "repo_safety",
        "title": "Repository safety",
        "description": "Variant respects sandbox, secret, mutation, and allowed-path boundaries.",
        "weight": 0.15,
        "required_evidence": ["sandbox_mode", "blockers", "secret_boundary"],
    },
    {
        "id": "maintainability",
        "title": "Maintainability",
        "description": "Variant produces a result that is understandable, locally aligned, and low-risk to evolve.",
        "weight": 0.15,
        "required_evidence": ["output_last_message_digest", "validation_results", "blockers"],
    },
]
AB_RUBRIC_STAGE_POLICIES = [
    {
        "stage": "local_oss_loop",
        "judge_profile": "oss-local",
        "default_model": "qwen3.5:9b-mlx",
        "confidence_weight": "fast_signal",
        "promotion_gate": "improvement_signal_only",
    },
    {
        "stage": "cloud_oss_loop",
        "judge_profile": "oss-cloud",
        "default_model": "deepseek-v4-flash:0731-cloud",
        "confidence_weight": "second_pass_signal",
        "promotion_gate": "confirm_local_delta",
    },
    {
        "stage": "external_validation",
        "judge_profile": "tessl",
        "default_model": "external",
        "confidence_weight": "independent_confirmation",
        "promotion_gate": "release_confirmation",
    },
]
AB_RUBRIC_WINNER_POLICY = {
    "minimum_normalized_delta": 0.10,
    "minimum_confidence": "medium",
    "tie_result": "inconclusive",
    "allowed_winners": ["skill_a", "skill_b", "inconclusive"],
}
AB_RUBRIC_JUDGE_OUTPUT_CONTRACT = {
    "decision_schema_version": "skills-sdk.ab-judge-decision.v0",
    "requires_dimension_scores": True,
    "requires_evidence_refs": True,
    "requires_reason_per_dimension": True,
    "unvalidated_judges_are_advisory": True,
}


def canonical_ab_rubric() -> dict[str, Any]:
    """Return the stable A/B scoring rubric shared by local, cloud, and external eval stages."""
    return {
        "rubric_id": AB_RUBRIC_ID,
        "rubric_version": AB_RUBRIC_VERSION,
        "stable_across_stages": True,
        "score_scale": {"minimum": 0, "maximum": 5},
        "normalization": "weighted_sum_divided_by_five",
        "dimensions": AB_RUBRIC_DIMENSIONS,
        "winner_policy": AB_RUBRIC_WINNER_POLICY,
        "stage_policies": AB_RUBRIC_STAGE_POLICIES,
        "judge_output_contract": AB_RUBRIC_JUDGE_OUTPUT_CONTRACT,
    }


def digest_rubric(rubric: dict[str, Any]) -> str:
    payload = json.dumps(rubric, sort_keys=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"


def canonical_ab_rubric_digest() -> str:
    return digest_rubric(canonical_ab_rubric())


def build_ab_rubric_preview_receipt() -> dict[str, Any]:
    rubric = canonical_ab_rubric()
    return {
        "schema_version": AB_RUBRIC_SCHEMA_VERSION,
        "schema_uri": AB_RUBRIC_SCHEMA_URI,
        "status": "preview",
        "operation": "ab_rubric",
        "rubric": rubric,
        "rubric_digest": digest_rubric(rubric),
        "calibration_required": True,
        "provider_invoked": False,
        "network_accessed": False,
        "mutation_performed": False,
        "blockers": [],
        "acceptance_trace": ["FR-003", "FR-008", "SA-004", "VP-021", "VP-022", "VP-030"],
        "agent_summary": (
            "Canonical A/B rubric preview is ready; Codex oss-local, Codex oss-cloud, and Tessl stages "
            "must reuse this rubric identity and digest."
        ),
    }
