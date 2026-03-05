#!/usr/bin/env python3
"""Schema helpers for skill router outputs and telemetry safety checks."""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Optional

SCHEMA_VERSION = "1.0"
DEFAULT_CONFIDENCE_BANDS = {
    "high": 0.85,
    "medium": 0.65,
}
ACTOR_THRESHOLDS = {
    "human": {
        "clarify_max": 0.60,
    },
    "agent": {
        "autopilot_min": 0.90,
        "confirm_min": 0.70,
    },
}

# Hard forbidden keys to avoid raw prompt/objective persistence.
FORBIDDEN_KEYS = {
    "prompt",
    "prompt_text",
    "objective",
    "objective_text",
    "raw_input",
    "raw_prompt",
}

# Sensitive patterns aligned with existing fail-closed posture in this repo.
SENSITIVE_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{30,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"/Users/[^/]+|/home/[^/]+"),
]


@dataclass
class Candidate:
    skill_name: str
    skill_path: str
    confidence: float
    rationale: List[str]
    risk_tier: str = "low"


@dataclass
class RouterResult:
    schema_version: str
    catalog_version: str
    actor_type: str
    policy_mode: str
    policy_decision: str
    requires_clarification: bool
    prompt_hash: str
    uncertainty_reasons: List[str]
    top_candidates: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def hash_prompt(text: str) -> str:
    """Hash prompt text so we can correlate routing events without storing raw text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def confidence_band(confidence: float, bands: Optional[Dict[str, float]] = None) -> str:
    thresholds = bands or DEFAULT_CONFIDENCE_BANDS
    if confidence >= thresholds["high"]:
        return "high"
    if confidence >= thresholds["medium"]:
        return "medium"
    return "low"


def decide_policy(
    *,
    actor_type: str,
    policy_mode: str,
    best_confidence: float,
    best_risk_tier: str,
    uncertainty_reasons: Optional[List[str]] = None,
    bands: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Return policy decision with fail-safe defaults."""
    normalized_actor = actor_type.lower().strip()
    normalized_mode = policy_mode.lower().strip()
    normalized_risk = best_risk_tier.lower().strip()
    band = confidence_band(best_confidence, bands=bands)

    # Fail closed on unknown modes.
    if normalized_mode not in {"observe_only", "co_pilot", "autopilot"}:
        normalized_mode = "observe_only"

    # Agent defaults remain safe unless explicitly elevated and low risk.
    if normalized_actor == "agent":
        if uncertainty_reasons:
            return {
                "policy_decision": "confirmation_required",
                "requires_clarification": True,
            }
        if normalized_mode == "observe_only":
            return {
                "policy_decision": "suggest_only",
                "requires_clarification": True,
            }
        if normalized_risk != "low":
            return {
                "policy_decision": "confirmation_required",
                "requires_clarification": True,
            }
        if best_confidence >= ACTOR_THRESHOLDS["agent"]["autopilot_min"] and normalized_mode == "autopilot":
            return {
                "policy_decision": "auto_select_top1",
                "requires_clarification": False,
            }
        if best_confidence >= ACTOR_THRESHOLDS["agent"]["confirm_min"] and normalized_mode == "co_pilot":
            return {
                "policy_decision": "suggest",
                "requires_clarification": False,
            }
        if best_confidence < ACTOR_THRESHOLDS["agent"]["confirm_min"]:
            return {
                "policy_decision": "confirmation_required",
                "requires_clarification": True,
            }
        return {
            "policy_decision": "confirmation_required",
            "requires_clarification": True,
        }

    # Humans default to suggestion + optional confirm.
    if uncertainty_reasons:
        return {
            "policy_decision": "clarify",
            "requires_clarification": True,
        }
    if best_confidence <= ACTOR_THRESHOLDS["human"]["clarify_max"] or band == "low":
        return {
            "policy_decision": "clarify",
            "requires_clarification": True,
        }
    return {
        "policy_decision": "suggest",
        "requires_clarification": False,
    }


def build_router_result(
    *,
    query: str,
    actor_type: str,
    policy_mode: str,
    catalog_version: str,
    candidates: Iterable[Candidate],
    uncertainty_reasons: Optional[List[str]] = None,
    control_resolution: Optional[str] = None,
    schema_version: str = SCHEMA_VERSION,
) -> Dict[str, Any]:
    candidates_list = list(candidates)
    best = candidates_list[0] if candidates_list else None
    best_confidence = best.confidence if best else 0.0
    best_risk_tier = best.risk_tier if best else "low"
    policy = decide_policy(
        actor_type=actor_type,
        policy_mode=policy_mode,
        best_confidence=best_confidence,
        best_risk_tier=best_risk_tier,
        uncertainty_reasons=uncertainty_reasons or [],
    )

    result = RouterResult(
        schema_version=schema_version,
        catalog_version=catalog_version,
        actor_type=actor_type,
        policy_mode=policy_mode,
        policy_decision=policy["policy_decision"],
        requires_clarification=policy["requires_clarification"],
        prompt_hash=hash_prompt(query),
        uncertainty_reasons=uncertainty_reasons or [],
        top_candidates=[
            {
                "skill_name": c.skill_name,
                "skill_path": c.skill_path,
                "confidence": round(float(c.confidence), 4),
                "confidence_band": confidence_band(c.confidence),
                "risk_tier": c.risk_tier,
                "rationale": c.rationale,
            }
            for c in candidates_list
        ],
    ).to_dict()
    if control_resolution is not None:
        result["control_resolution"] = control_resolution

    issues = validate_router_result(result, fail_on_sensitive_fields=True)
    if issues:
        raise ValueError("; ".join(issues))
    return result


def _contains_sensitive_text(value: Any) -> bool:
    if isinstance(value, str):
        return any(pattern.search(value) for pattern in SENSITIVE_PATTERNS)
    if isinstance(value, list):
        return any(_contains_sensitive_text(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_sensitive_text(v) for v in value.values())
    return False


def _contains_forbidden_key(data: Any) -> bool:
    if isinstance(data, dict):
        for key, value in data.items():
            if key in FORBIDDEN_KEYS:
                return True
            if _contains_forbidden_key(value):
                return True
    elif isinstance(data, list):
        return any(_contains_forbidden_key(item) for item in data)
    return False


def validate_router_result(result: Dict[str, Any], *, fail_on_sensitive_fields: bool = False) -> List[str]:
    """Validate output contract and telemetry-safety invariants."""
    issues: List[str] = []

    required = {
        "schema_version",
        "catalog_version",
        "actor_type",
        "policy_mode",
        "policy_decision",
        "requires_clarification",
        "prompt_hash",
        "uncertainty_reasons",
        "top_candidates",
    }

    missing = sorted(required - set(result.keys()))
    if missing:
        issues.append(f"missing required fields: {', '.join(missing)}")

    if _contains_forbidden_key(result):
        issues.append("forbidden raw prompt/objective keys present")

    if result.get("actor_type") not in {"human", "agent"}:
        issues.append("actor_type must be human|agent")

    if result.get("policy_mode") not in {"observe_only", "co_pilot", "autopilot"}:
        issues.append("policy_mode must be observe_only|co_pilot|autopilot")

    policy_decision = result.get("policy_decision")
    if policy_decision not in {
        "suggest",
        "suggest_only",
        "clarify",
        "confirmation_required",
        "auto_select_top1",
    }:
        issues.append("invalid policy_decision")

    if not isinstance(result.get("requires_clarification"), bool):
        issues.append("requires_clarification must be boolean")

    if not isinstance(result.get("uncertainty_reasons"), list):
        issues.append("uncertainty_reasons must be list")

    candidates = result.get("top_candidates")
    if not isinstance(candidates, list):
        issues.append("top_candidates must be list")
    else:
        for idx, candidate in enumerate(candidates):
            if not isinstance(candidate, dict):
                issues.append(f"top_candidates[{idx}] must be object")
                continue
            for key in ("skill_name", "skill_path", "confidence", "confidence_band", "risk_tier", "rationale"):
                if key not in candidate:
                    issues.append(f"top_candidates[{idx}] missing {key}")

    if fail_on_sensitive_fields and _contains_sensitive_text(result):
        issues.append("sensitive value pattern detected in router payload")

    return issues
