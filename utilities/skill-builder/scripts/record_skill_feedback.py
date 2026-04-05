#!/usr/bin/env python3
"""Record AskQuestion-style skill feedback as JSONL with subject tagging."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


VALID_DECISIONS = {"accepted", "partial", "rejected", "deferred"}
VALID_OUTCOMES = {"good", "neutral", "bad", "unknown"}
VALID_CONFIDENCE = {"high", "medium", "low"}


def infer_subject(skill_path: str, override: str | None = None) -> str:
    if override:
        return override
    p = skill_path.lower()
    if "/frontend/ui/" in p or "/design/" in p or "figma" in p or "react" in p:
        return "ui"
    if "/github/" in p or "review" in p:
        return "code_review"
    if "/backend/" in p or "workers-mcp" in p or "mcp-builder" in p:
        return "backend"
    if "/product/security/" in p or "/security-" in p:
        return "security"
    if "/auth/" in p:
        return "auth"
    if "/product/docs/" in p or "docs-" in p:
        return "docs"
    if "/utilities/" in p:
        return "utilities"
    if "/product/specs/" in p or "spec" in p:
        return "specs"
    if "/product/ops/" in p:
        return "ops"
    if "/product/strategy/" in p:
        return "strategy"
    return "general"


def derive_skill_name(skill_path: Path) -> str:
    if skill_path.name.lower() == "skill.md":
        return skill_path.parent.name
    return skill_path.stem


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Record skill decision feedback with inferred subject tags."
    )
    parser.add_argument("--skill-path", required=True, help="Path to the SKILL.md file.")
    parser.add_argument("--decision", required=True, choices=sorted(VALID_DECISIONS))
    parser.add_argument("--outcome", required=True, choices=sorted(VALID_OUTCOMES))
    parser.add_argument("--confidence", required=True, choices=sorted(VALID_CONFIDENCE))
    parser.add_argument("--notes", default="", help="Optional context on why this outcome was assigned.")
    parser.add_argument("--recommendation-id", default="", help="Optional recommendation ID (e.g., rec-001).")
    parser.add_argument("--action-key", default="", help="Optional normalized action key.")
    parser.add_argument(
        "--subject",
        default="",
        help="Optional override for inferred subject (ui, code_review, backend, security, etc.).",
    )
    parser.add_argument(
        "--workspace",
        default=".",
        help="Workspace root where feedback log should be stored (default: current directory).",
    )
    parser.add_argument(
        "--log-rel",
        default="ops/metrics/skill-feedback/decision-feedback.jsonl",
        help="Feedback log path relative to workspace.",
    )
    parser.add_argument("--actor", default="user", help="Who provided the feedback (default: user).")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace = Path(args.workspace).expanduser().resolve()
    skill_path = Path(args.skill_path).expanduser().resolve()
    log_rel = Path(args.log_rel)
    if log_rel.is_absolute():
        raise SystemExit("--log-rel must be a relative path within --workspace")

    log_path = (workspace / log_rel).resolve()
    try:
        log_path.relative_to(workspace)
    except ValueError as exc:
        raise SystemExit("Resolved --log-rel escapes --workspace") from exc

    log_path.parent.mkdir(parents=True, exist_ok=True)

    event = {
        "schema_version": 1,
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
        "actor": args.actor,
        "skill_path": str(skill_path),
        "skill_name": derive_skill_name(skill_path),
        "subject": infer_subject(str(skill_path), args.subject or None),
        "decision": args.decision,
        "outcome": args.outcome,
        "confidence": args.confidence,
        "recommendation_id": args.recommendation_id,
        "action_key": args.action_key,
        "notes": args.notes,
    }

    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    print("record-skill-feedback: PASS")
    print(f"log: {log_path}")
    print(f"skill: {event['skill_name']}")
    print(f"subject: {event['subject']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
