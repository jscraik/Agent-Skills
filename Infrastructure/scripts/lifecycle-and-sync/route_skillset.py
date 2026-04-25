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
# TOKEN_RE captures alphanumeric tokens with optional hyphens.
# Minimum token length is 1 character to include single-letter terms like "i".
# The second character group is optional to allow single-character tokens.
TOKEN_RE = re.compile(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?")


def tokenize(text: str) -> set[str]:
    tokens: set[str] = set()
    for token in TOKEN_RE.findall(text.lower()):
        cleaned = token.strip("-")
        if not cleaned:
            continue
        tokens.add(cleaned)
        tokens.update(part for part in cleaned.split("-") if part)
    return tokens


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
        selected = {
            "id": selected_row.get("id"),
            "level": selected_row.get("level"),
            "source_path": selected_row.get("source_path"),
            "confidence": selected_confidence,
        }
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
