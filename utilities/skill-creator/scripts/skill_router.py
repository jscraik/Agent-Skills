#!/usr/bin/env python3
"""Deterministic intent-first skill router (top-k + confidence + rationale)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
from uuid import uuid4

from skill_catalog import SkillMeta, load_catalog
from skill_router_schema import Candidate, build_router_result, validate_router_result

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_\-]{1,}")


def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(text.lower())


def risk_tier(skill: SkillMeta) -> str:
    marker = f"{skill.name} {skill.skill_path}".lower()
    if any(k in marker for k in ["security", "threat", "recon", "ownership"]):
        return "high"
    if any(k in marker for k in ["deploy", "release", "workflow", "github"]):
        return "medium"
    return "low"


def score_skill(query: str, query_tokens: List[str], skill: SkillMeta) -> Tuple[float, List[str], bool]:
    skill_name_norm = skill.name.lower().replace(":", "-").replace("_", "-")
    skill_tokens = set(tokenize(f"{skill.name} {skill.description} {skill.skill_path}"))
    query_set = set(query_tokens)

    rationale: List[str] = []
    explicit = skill_name_norm in query.lower() or f"${skill_name_norm}" in query.lower()
    overlap = len(query_set & skill_tokens)
    overlap_ratio = overlap / max(1, len(query_set))

    path_bonus = 0.2 if any(part in query_set for part in tokenize(skill.skill_path)) else 0.0
    negation_penalty = 0.0
    if re.search(rf"\b(?:not|don't|dont|avoid)\s+{re.escape(skill_name_norm)}\b", query.lower()):
        negation_penalty = 0.8

    score = 0.0
    if explicit:
        score += 1.5
        rationale.append("explicit skill mention")

    if overlap > 0:
        score += overlap_ratio
        rationale.append(f"keyword overlap={overlap}")

    if path_bonus > 0:
        score += path_bonus
        rationale.append("path context match")

    if negation_penalty > 0:
        score -= negation_penalty
        rationale.append("negation penalty")

    score = max(0.0, score)
    return score, rationale, explicit


def confidence_from_score(score: float) -> float:
    return min(1.0, round(score / 2.2, 4))


def route(query: str, skills: List[SkillMeta], top_k: int = 3) -> Tuple[List[Candidate], List[str]]:
    query_tokens = tokenize(query)
    ranked: List[Tuple[float, bool, SkillMeta, List[str]]] = []
    uncertainty_reasons: List[str] = []

    for skill in skills:
        score, rationale, explicit = score_skill(query, query_tokens, skill)
        confidence = confidence_from_score(score)
        ranked.append((confidence, explicit, skill, rationale))

    ranked.sort(
        key=lambda item: (
            -item[0],
            -int(item[1]),
            item[2].name.lower(),
            item[2].skill_path.lower(),
        )
    )

    candidates: List[Candidate] = []
    for confidence, _explicit, skill, rationale in ranked[:top_k]:
        candidates.append(
            Candidate(
                skill_name=skill.name,
                skill_path=skill.skill_path,
                confidence=confidence,
                rationale=rationale or ["low signal match"],
                risk_tier=risk_tier(skill),
            )
        )

    if len(ranked) >= 2 and abs(ranked[0][0] - ranked[1][0]) < 0.08:
        uncertainty_reasons.append("top_candidates_close_score")

    lowered = query.lower()
    if " and " in lowered or " or " in lowered:
        uncertainty_reasons.append("possible_multi_intent")

    return candidates, uncertainty_reasons


def render_human(result: Dict[str, object]) -> str:
    lines = [
        f"schema={result['schema_version']} catalog={result['catalog_version']}",
        f"actor={result['actor_type']} policy_mode={result['policy_mode']} decision={result['policy_decision']}",
        f"requires_clarification={result['requires_clarification']}",
        "",
        "Top candidates:",
    ]

    for idx, candidate in enumerate(result.get("top_candidates", []), start=1):
        lines.append(
            f"{idx}. {candidate['skill_name']} ({candidate['skill_path']}) "
            f"confidence={candidate['confidence']} band={candidate['confidence_band']} risk={candidate['risk_tier']}"
        )
        lines.append(f"   rationale: {', '.join(candidate['rationale'])}")

    return "\n".join(lines)


def build_route_event(
    *,
    result: Dict[str, object],
    selected_rank: int | None = None,
    correction_latency_ms: int | None = None,
) -> Dict[str, object]:
    candidates = result.get("top_candidates", [])
    top1 = candidates[0] if candidates else {}
    top1_confidence = float(top1.get("confidence", 0.0)) if isinstance(top1, dict) else 0.0

    event = {
        "event_id": str(uuid4()),
        "event_ts": datetime.now(timezone.utc).isoformat(),
        "event_type": "skill_router.route_decision",
        "schema_version": result.get("schema_version"),
        "catalog_version": result.get("catalog_version"),
        "actor_type": result.get("actor_type"),
        "policy_mode": result.get("policy_mode"),
        "policy_decision": result.get("policy_decision"),
        "requires_clarification": result.get("requires_clarification"),
        "uncertainty_reasons": result.get("uncertainty_reasons", []),
        "prompt_hash": result.get("prompt_hash"),
        "top1_skill": top1.get("skill_name") if isinstance(top1, dict) else None,
        "top1_confidence": top1_confidence,
        "selected_rank": selected_rank,
        "top1_chosen": selected_rank == 1 if selected_rank is not None else None,
        "override_regret_flag": bool(selected_rank and selected_rank > 1 and top1_confidence >= 0.85),
        "correction_latency_ms": correction_latency_ms,
    }
    return event


def append_event(path: Path, event: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministic skill router")
    parser.add_argument("--query", required=True, help="User request text")
    parser.add_argument("--actor-type", default="human", choices=["human", "agent"])
    parser.add_argument(
        "--policy-mode",
        default="observe_only",
        choices=["observe_only", "co_pilot", "autopilot"],
    )
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument(
        "--allow-catalog-issues",
        action="store_true",
        help="Allow routing to continue when metadata quality checks fail",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--catalog-version", default="skills-current")
    parser.add_argument("--events-out", type=Path, help="Optional JSONL path for routing telemetry events")
    parser.add_argument("--selected-rank", type=int, help="Optional selected candidate rank for feedback")
    parser.add_argument("--correction-latency-ms", type=int, help="Optional latency between suggestion and correction")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        catalog = load_catalog(args.repo_root, strict=not args.allow_catalog_issues)
    except ValueError as exc:
        print("Catalog validation failed:", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 4

    if not catalog.skills:
        print("No skills discovered.", file=sys.stderr)
        return 2

    candidates, uncertainty_reasons = route(args.query, catalog.skills, top_k=max(1, args.top_k))
    result = build_router_result(
        query=args.query,
        actor_type=args.actor_type,
        policy_mode=args.policy_mode,
        catalog_version=catalog.catalog_version if args.catalog_version == "skills-current" else args.catalog_version,
        candidates=candidates,
        uncertainty_reasons=uncertainty_reasons,
    )

    issues = validate_router_result(result, fail_on_sensitive_fields=True)
    if issues:
        print("Router result validation failed:", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 3

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_human(result))

    if args.events_out:
        event = build_route_event(
            result=result,
            selected_rank=args.selected_rank,
            correction_latency_ms=args.correction_latency_ms,
        )
        append_event(args.events_out, event)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
