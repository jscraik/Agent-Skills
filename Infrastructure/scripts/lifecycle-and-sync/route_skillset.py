#!/usr/bin/env python3
"""Route a task to a bounded latent module inside one rooted skill set."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from selection_policy import ROOT_SKILL_SET_NAMES, policy_identity
from skillset_model import rel, repo_root

DEFAULT_SKILLSETS_DIR = repo_root() / ".skillsets"
MAX_TOP_K = 3
LOW_CONFIDENCE_THRESHOLD = 0.18
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "before",
    "but",
    "by",
    "can",
    "for",
    "from",
    "has",
    "have",
    "i",
    "in",
    "into",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "please",
    "should",
    "so",
    "that",
    "the",
    "this",
    "to",
    "with",
    "you",
}
# TOKEN_RE captures alphanumeric tokens with optional hyphens.
# Minimum token length is 1 character to include single-letter terms like "i".
# The second character group is optional to allow single-character tokens.
TOKEN_RE = re.compile(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?")
TOKEN_ALIASES = {
    "verification": "verify",
}


def tokenize(text: str) -> set[str]:
    tokens: set[str] = set()
    for token in TOKEN_RE.findall(text.lower()):
        cleaned = token.strip("-")
        if not cleaned:
            continue
        if cleaned in STOPWORDS:
            continue
        tokens.add(cleaned)
        if cleaned in TOKEN_ALIASES:
            tokens.add(TOKEN_ALIASES[cleaned])
        tokens.update(part for part in cleaned.split("-") if part and part not in STOPWORDS)
        tokens.update(TOKEN_ALIASES[part] for part in cleaned.split("-") if part in TOKEN_ALIASES)
    return tokens


def normalize_phrase(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def read_manifest(skill_set: str, skillsets_dir: Path = DEFAULT_SKILLSETS_DIR) -> tuple[list[dict[str, Any]], str | None]:
    if skill_set not in ROOT_SKILL_SET_NAMES:
        return [], "invalid_skill_set"
    manifest_path = skillsets_dir / skill_set / "manifest.jsonl"
    if not manifest_path.is_file():
        return [], "manifest_missing"
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(manifest_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid manifest JSON at {rel(manifest_path)}:{line_no}: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"Invalid manifest row at {rel(manifest_path)}:{line_no}: expected JSON object")
        for field in ("id", "description", "level", "source_path"):
            if not isinstance(row.get(field), str) or not row.get(field):
                raise ValueError(
                    f"Invalid manifest row at {rel(manifest_path)}:{line_no}: field {field!r} must be a non-empty string"
                )
        triggers = row.get("triggers", [])
        if not isinstance(triggers, list) or any(not isinstance(item, str) for item in triggers):
            raise ValueError(
                f"Invalid manifest row at {rel(manifest_path)}:{line_no}: field 'triggers' must be a list of strings"
            )
        rows.append(row)
    return rows, None


def score_row(row: dict[str, Any], task: str) -> tuple[float, list[str]]:
    task_phrase = normalize_phrase(task)
    phrase_candidates = [
        normalize_phrase(str(row.get("id", "")).replace("-", " ")),
        *[
            normalize_phrase(str(item))
            for item in row.get("triggers", [])
            if isinstance(item, str)
        ],
    ]
    for phrase in phrase_candidates:
        if len(phrase.split()) >= 2 and phrase in task_phrase:
            return 1.0, [f"matched phrase '{phrase}'"]

    task_tokens = tokenize(task)
    haystack_parts = [
        str(row.get("id", "")),
        str(row.get("description", "")),
        " ".join(str(item) for item in row.get("triggers", []) if isinstance(item, str)),
    ]
    row_tokens = tokenize(" ".join(haystack_parts))
    if not task_tokens or not row_tokens:
        return 0.0, []
    overlap = task_tokens & row_tokens
    confidence = len(overlap) / max(len(task_tokens), 1)
    reasons = [f"matched term '{term}'" for term in sorted(overlap)[:3]]
    return round(min(confidence, 1.0), 4), reasons


def signal_matches(task_text: str, task_tokens: set[str], signal: str) -> bool:
    signal_text = signal.lower().strip()
    if not signal_text:
        return False
    if signal_text in task_text:
        return True
    signal_tokens = tokenize(signal_text)
    if not signal_tokens:
        return False
    return signal_tokens <= task_tokens


def row_by_id(rows: list[dict[str, Any]], stage_id: str) -> dict[str, Any] | None:
    for row in rows:
        if row.get("id") == stage_id:
            return row
    return None


def selected_payload(row: dict[str, Any], confidence: float) -> dict[str, Any]:
    return {
        "id": row.get("id"),
        "level": row.get("level"),
        "source_path": row.get("source_path"),
        "confidence": round(confidence, 4),
    }


def is_stage_correctness_question(task_text: str, task_tokens: set[str]) -> bool:
    return (
        re.search(r"\bis\s+he-[a-z0-9-]+\s+(correct|right)\b", task_text) is not None
        or "whether" in task_tokens
        or "right stage" in task_text
        or "correct stage" in task_text
        or "best stage" in task_text
        or "which stage" in task_text
        or "what stage" in task_text
        or "should we use" in task_text
        or "should i use" in task_text
        or "should codex use" in task_text
    )


def harness_engineering_override(task: str, rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Apply the HE deterministic stage policy before generic token scoring."""
    routing_map_path = repo_root() / "Plugins/harness-engineering/references/routing-map.json"
    if not routing_map_path.is_file():
        return None
    try:
        routing_map = json.loads(routing_map_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None

    task_text = task.lower()
    task_tokens = tokenize(task)
    stage_ids = {str(row.get("id")) for row in rows}

    mentioned_stages = [stage for stage in re.findall(r"\bhe-[a-z0-9-]+\b", task_text) if stage in stage_ids]
    distinct_mentioned_stages = sorted(set(mentioned_stages))
    router_row = row_by_id(rows, "he-router")
    if len(distinct_mentioned_stages) > 1 and router_row:
        return {
            "row": router_row,
            "confidence": 0.9,
            "reason": "matched multi-stage HE rule 'named-stage-ambiguity'",
        }
    if distinct_mentioned_stages and is_stage_correctness_question(task_text, task_tokens) and router_row:
        return {
            "row": router_row,
            "confidence": 0.9,
            "reason": "matched multi-stage HE rule 'stage-correctness-question'",
        }
    if distinct_mentioned_stages:
        stage_id = distinct_mentioned_stages[0]
        if stage_id in stage_ids:
            row = row_by_id(rows, stage_id)
            if row:
                return {
                    "row": row,
                    "confidence": 1.0,
                    "reason": f"matched deterministic HE rule 'direct-stage-invocation'",
                }

    for rule in sorted(routing_map.get("deterministic_decision_order", []), key=lambda item: item.get("priority", 999)):
        route = str(rule.get("route", ""))
        signals = [str(signal) for signal in rule.get("signals", []) if isinstance(signal, str)]
        if not signals:
            continue
        if not any(signal_matches(task_text, task_tokens, signal) for signal in signals):
            continue
        if route in stage_ids:
            row = row_by_id(rows, route)
            if row:
                return {
                    "row": row,
                    "confidence": 0.95,
                    "reason": f"matched deterministic HE rule '{rule.get('rule')}'",
                }
        if " or " in route or " -> " in route:
            row = row_by_id(rows, "he-router")
            if row:
                return {
                    "row": row,
                    "confidence": 0.9,
                    "reason": f"matched multi-stage HE rule '{rule.get('rule')}'",
                }
    return None


def route(skill_set: str, task: str, *, top_k: int = MAX_TOP_K, skillsets_dir: Path = DEFAULT_SKILLSETS_DIR) -> dict[str, Any]:
    bounded_top_k = max(1, min(int(top_k), MAX_TOP_K))
    rows, error_status = read_manifest(skill_set, skillsets_dir)
    if error_status:
        return {
            "schema_version": 1,
            "status": error_status,
            "policy_identity": policy_identity(),
            "skill_set": skill_set,
            "top_k": bounded_top_k,
            "selected": None,
            "candidates": [],
            "operator_action": "Generate manifests before routing." if error_status == "manifest_missing" else "Choose a valid root skill set.",
        }
    override = harness_engineering_override(task, rows) if skill_set == "harness-engineering" else None
    if override:
        selected_row = override["row"]
        selected_confidence = float(override["confidence"])
        candidates = [
            {
                "id": selected_row.get("id"),
                "level": selected_row.get("level"),
                "confidence": round(selected_confidence, 4),
                "reason": override["reason"],
            }
        ]
        return {
            "schema_version": 1,
            "status": "selected",
            "policy_identity": policy_identity(),
            "skill_set": skill_set,
            "top_k": bounded_top_k,
            "selected": selected_payload(selected_row, selected_confidence),
            "candidates": candidates,
            "operator_action": None,
        }
    scored = []
    for row in rows:
        confidence, reasons = score_row(row, task)
        if confidence <= 0:
            continue
        scored.append((confidence, row, reasons))
    scored.sort(key=lambda item: (-item[0], item[1].get("id", "")))
    candidates = [
        {
            "id": row.get("id"),
            "level": row.get("level"),
            "confidence": confidence,
            "reason": "; ".join(reasons) if reasons else "matched manifest metadata",
        }
        for confidence, row, reasons in scored[:bounded_top_k]
    ]
    if not candidates:
        return {
            "schema_version": 1,
            "status": "no_match",
            "policy_identity": policy_identity(),
            "skill_set": skill_set,
            "top_k": bounded_top_k,
            "selected": None,
            "candidates": [],
            "operator_action": "Ask a clarifying question or choose a documented fallback root skill set.",
        }
    selected_confidence, selected_row, _reasons = scored[0]
    status = "selected" if selected_confidence >= LOW_CONFIDENCE_THRESHOLD else "low_confidence"
    selected = None
    if status == "selected":
        selected = selected_payload(selected_row, selected_confidence)
    return {
        "schema_version": 1,
        "status": status,
        "policy_identity": policy_identity(),
        "skill_set": skill_set,
        "top_k": bounded_top_k,
        "selected": selected,
        "candidates": candidates,
        "operator_action": None if selected else "Clarify before loading a latent module.",
    }


def read_task(args: argparse.Namespace) -> str:
    sources = [bool(args.task), bool(args.task_stdin), bool(args.task_file)]
    if sum(sources) != 1:
        raise SystemExit("Specify exactly one of --task, --task-stdin, or --task-file.")
    if args.task:
        return args.task
    if args.task_stdin:
        import sys

        return sys.stdin.read().strip()
    task_path = Path(args.task_file)
    if not task_path.is_file():
        raise SystemExit(f"Task file not found: {args.task_file}")
    return task_path.read_text(encoding="utf-8").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-set", required=True)
    parser.add_argument("--task", help="Task text; use --task-stdin or --task-file for sensitive tasks")
    parser.add_argument("--task-stdin", action="store_true")
    parser.add_argument("--task-file")
    parser.add_argument("--top-k", type=int, default=MAX_TOP_K)
    parser.add_argument("--skillsets-dir", type=Path, default=DEFAULT_SKILLSETS_DIR)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = route(args.skill_set, read_task(args), top_k=args.top_k, skillsets_dir=args.skillsets_dir)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"route status: {payload['status']}")
        selected = payload.get("selected")
        if selected:
            print(f"selected: {selected['id']} ({selected['source_path']})")
    return 0 if payload["status"] in {"selected", "low_confidence", "no_match"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
