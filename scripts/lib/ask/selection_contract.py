"""Helpers for building deterministic selection decision payloads."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


SCHEMA_VERSION = "selection-decision.v1"
FAILURE_CLASS_BY_STATUS = {
    "unresolved_ambiguity": "AMBIGUITY_UNRESOLVED",
    "blocked_policy_drift": "DISCOVERY_POLICY_DRIFT",
    "degraded_no_candidates": "NO_ELIGIBLE_CANDIDATES",
}


@dataclass(frozen=True)
class EligibleCandidate:
    name: str
    path: str
    description: str
    scope_rank: int


def canonical_sort_key(candidate: EligibleCandidate) -> str:
    return f"{candidate.name.lower()}::{candidate.path.lower()}"


def candidate_id(candidate: EligibleCandidate) -> str:
    return f"skill:{candidate.name.lower()}::{candidate.path.lower()}"


def default_operator_action(decision_status: str) -> str | None:
    if decision_status == "unresolved_ambiguity":
        return "Narrow the request or mention an exact skill path to resolve ambiguity."
    if decision_status == "blocked_policy_drift":
        return "Run sync/discovery parity checks and restore canonical policy identity."
    if decision_status == "degraded_no_candidates":
        return "Run `ask skills sync` and verify discovery policy/catalog eligibility."
    return None


def map_failure_class(decision_status: str) -> str | None:
    return FAILURE_CLASS_BY_STATUS.get(decision_status)


def build_decision_payload(
    *,
    request: str,
    policy_identity: str,
    considered_limit: int,
    top_k: int,
    eligible_candidates: list[EligibleCandidate],
    ranked_candidates: list[dict],
    uncertainty_reasons: list[str],
    policy_parity_ok: bool = True,
    request_id: str | None = None,
) -> dict:
    ordered = sorted(eligible_candidates, key=canonical_sort_key)
    considered_limit = max(1, considered_limit)
    considered = ordered[:considered_limit]
    truncated_count = max(0, len(ordered) - len(considered))

    selected_by_id = {
        f"skill:{item['skill_name'].lower()}::{item['skill_path'].lower()}": item
        for item in ranked_candidates[: max(1, top_k)]
    }

    considered_payload = []
    excluded_payload = []
    selected_payload = []

    for candidate in considered:
        cid = candidate_id(candidate)
        base = {
            "candidate_id": cid,
            "candidate_type": "skill",
            "name": candidate.name,
            "path": candidate.path,
            "scope_rank": candidate.scope_rank,
            "canonical_sort_key": canonical_sort_key(candidate),
        }
        selected_match = selected_by_id.get(cid)
        if selected_match:
            selected_item = {
                **base,
                "candidate_state": "selected",
                "confidence": selected_match.get("confidence", 0.0),
                "rationale": selected_match.get("rationale", []),
                "rank": len(selected_payload) + 1,
            }
            selected_payload.append(selected_item)
            considered_payload.append(selected_item)
            continue

        excluded_item = {
            **base,
            "candidate_state": "excluded",
            "exclusion_reason": "not_ranked_in_top_k",
        }
        excluded_payload.append(excluded_item)
        considered_payload.append(excluded_item)

    decision_status = "resolved"
    ambiguity_set: list[dict] = []

    if not policy_parity_ok:
        decision_status = "blocked_policy_drift"
        selected_payload = []
        excluded_payload = considered_payload.copy()
    elif not ranked_candidates or float(ranked_candidates[0].get("confidence", 0.0)) <= 0:
        decision_status = "degraded_no_candidates"
        selected_payload = []
        excluded_payload = considered_payload.copy()
    else:
        top_candidates_close = len(ranked_candidates) >= 2 and abs(
            float(ranked_candidates[0].get("confidence", 0.0))
            - float(ranked_candidates[1].get("confidence", 0.0))
        ) < 0.08
        if "top_candidates_close_score" in uncertainty_reasons or top_candidates_close:
            decision_status = "unresolved_ambiguity"
            selected_payload = []
            ambiguity_set = [
                {
                    "name": c.get("skill_name"),
                    "path": c.get("skill_path"),
                    "confidence": c.get("confidence", 0.0),
                    "rationale": c.get("rationale", []),
                }
                for c in ranked_candidates[:2]
            ]

    failure_class = map_failure_class(decision_status)
    operator_action = default_operator_action(decision_status)

    return {
        "schema_version": SCHEMA_VERSION,
        "request_id": request_id or str(uuid4()),
        "policy_identity": policy_identity,
        "decision_status": decision_status,
        "failure_class": failure_class,
        "operator_action": operator_action,
        "request": request,
        "considered_limit": considered_limit,
        "considered_total": len(ordered),
        "considered_truncated": truncated_count > 0,
        "truncated_count": truncated_count,
        "ordering": "canonical_sort_key_asc_then_router_score_desc",
        "selected_candidates": selected_payload,
        "considered_candidates": considered_payload,
        "excluded_candidates": excluded_payload,
        "uncertainty_reasons": uncertainty_reasons,
        "ambiguity_set": ambiguity_set,
    }
