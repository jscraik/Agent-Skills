#!/usr/bin/env python3
"""Deterministic intent-first skill router (top-k + confidence + rationale)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from skill_router_schema import Candidate, build_router_result, validate_router_result

SKIP_DIRS = {
    ".git",
    "artifacts",
    "node_modules",
    "docs",
    "templates",
    "references",
    "skills-system",
    ".worktrees",
}

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_\-]{1,}")


@dataclass
class SkillMeta:
    name: str
    description: str
    skill_path: str


def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(text.lower())


def parse_frontmatter(skill_file: Path) -> Tuple[str, str]:
    content = skill_file.read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()
    name = skill_file.parent.name
    description = ""

    if len(lines) > 2 and lines[0].strip() == "---":
        idx = 1
        while idx < len(lines) and lines[idx].strip() != "---":
            line = lines[idx]
            if line.startswith("name:"):
                value = line.split(":", 1)[1].strip()
                if value:
                    name = value.strip("\"'")
            if line.startswith("description:"):
                value = line.split(":", 1)[1].strip()
                description = value.strip("\"'")
            idx += 1

    if not description:
        body = "\n".join(lines[10:40])
        match = re.search(r"\n\s*[-*]?\s*(.+)", body)
        if match:
            description = match.group(1).strip()

    return name, description


def discover_skills(repo_root: Path) -> List[SkillMeta]:
    skills: List[SkillMeta] = []
    for skill_file in sorted(repo_root.rglob("SKILL.md")):
        rel = skill_file.relative_to(repo_root)
        if rel.as_posix() == "SKILL.md":
            continue
        if any(part in SKIP_DIRS for part in rel.parts):
            continue

        name, description = parse_frontmatter(skill_file)
        skills.append(
            SkillMeta(
                name=name,
                description=description,
                skill_path=str(skill_file.parent.relative_to(repo_root)),
            )
        )
    return skills


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


def route(query: str, skills: Iterable[SkillMeta], top_k: int = 3) -> List[Candidate]:
    query_tokens = tokenize(query)
    ranked: List[Tuple[float, bool, SkillMeta, List[str]]] = []

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

    return candidates


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
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--catalog-version", default="skills-current")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    skills = discover_skills(args.repo_root)
    if not skills:
        print("No skills discovered.", file=sys.stderr)
        return 2

    candidates = route(args.query, skills, top_k=max(1, args.top_k))
    result = build_router_result(
        query=args.query,
        actor_type=args.actor_type,
        policy_mode=args.policy_mode,
        catalog_version=args.catalog_version,
        candidates=candidates,
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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
