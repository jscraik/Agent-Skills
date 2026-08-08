#!/usr/bin/env python3
"""Route a task to a bounded latent module inside one rooted skill set."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from route_skillset_policy import (
    factory_override,
    factory_scope_excluded,
    harness_engineering_override,
    he_row_for_stage,
    is_he_phase_heartbeat_request,
    is_stage_correctness_question,
    resolve_he_stage_alias,
    selected_payload,
)
from route_skillset_support import DEFAULT_SKILLSETS_DIR, read_manifest, row_by_id, score_row
from selection_policy import policy_identity

MAX_TOP_K = 3
LOW_CONFIDENCE_THRESHOLD = 0.18


def _base_payload(
    skill_set: str,
    top_k: int,
    status: str,
    *,
    selected: dict[str, Any] | None = None,
    candidates: list[dict[str, Any]] | None = None,
    operator_action: str | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "status": status,
        "policy_identity": policy_identity(),
        "skill_set": skill_set,
        "top_k": top_k,
        "selected": selected,
        "candidates": candidates or [],
        "operator_action": operator_action,
    }
    if error is not None:
        payload["error"] = error
    return payload


def _skill_factory_system_bridge_rows(rows: list[dict[str, Any]], *, repo_base: Path) -> list[dict[str, Any]]:
    """Return system skill rows that are intentionally routed by Skill Factory."""
    existing_ids = {str(row.get("id")) for row in rows}
    bridge_specs = {
        "skill-creator": (
            "Create or scaffold Codex skills through the system skill-creator with Skill Factory references.",
            "skills-system/skill-creator/SKILL.md",
            ["skill creator", "create skill", "scaffold skill"],
        ),
        "skill-installer": (
            "Install, list, and validate Codex skills through the system skill-installer with Skill Factory references.",
            "skills-system/skill-installer/SKILL.md",
            ["skill installer", "install skill", "list skills"],
        ),
    }
    bridges: list[dict[str, Any]] = []
    for bridge_id, (description, source_path, triggers) in bridge_specs.items():
        if bridge_id in existing_ids or not (repo_base / source_path).is_file():
            continue
        bridges.append(
            {
                "id": bridge_id,
                "description": description,
                "level": "system-bridge",
                "source_path": source_path,
                "triggers": triggers,
            }
        )
    return bridges


def _augmented_rows(skill_set: str, rows: list[dict[str, Any]], skillsets_dir: Path) -> list[dict[str, Any]]:
    if skill_set != "skill-factory":
        return rows
    return [*rows, *_skill_factory_system_bridge_rows(rows, repo_base=skillsets_dir.parent)]


def _policy_override(
    skill_set: str,
    task: str,
    rows: list[dict[str, Any]],
    skillsets_dir: Path,
) -> dict[str, Any] | None:
    if skill_set == "harness-engineering":
        routing_map_path = skillsets_dir.parent / "Plugins/harness-engineering/references/routing-map.json"
        if not routing_map_path.is_file():
            routing_map_path = None
        return harness_engineering_override(task, rows, routing_map_path=routing_map_path)
    if skill_set in {"plugin-factory", "skill-factory"}:
        return factory_override(skill_set, task, rows)
    return None


def _read_manifest(skill_set: str, skillsets_dir: Path) -> tuple[list[dict[str, Any]], str | None, str | None]:
    try:
        rows, error_status = read_manifest(skill_set, skillsets_dir)
    except ValueError as exc:
        return [], None, str(exc)
    return rows, error_status, None


def _safe_policy_override(
    skill_set: str,
    task: str,
    rows: list[dict[str, Any]],
    skillsets_dir: Path,
) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return _policy_override(skill_set, task, rows, skillsets_dir), None
    except ValueError as exc:
        return None, str(exc)


def _factory_exclusion_payload(skill_set: str, top_k: int) -> dict[str, Any]:
    return _base_payload(
        skill_set,
        top_k,
        "no_match",
        operator_action="Handle as ordinary product work; factory routing is excluded by the task text.",
    )


def _score_rows(rows: list[dict[str, Any]], task: str) -> list[tuple[float, dict[str, Any], list[str]]]:
    scored: list[tuple[float, dict[str, Any], list[str]]] = []
    for row in rows:
        confidence, reasons = score_row(row, task)
        if confidence > 0:
            scored.append((confidence, row, reasons))
    scored.sort(key=lambda item: (-item[0], item[1].get("id", "")))
    return scored


def _selected_row_for_result(
    skill_set: str,
    selected_row: dict[str, Any],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    if skill_set != "harness-engineering":
        return selected_row
    selected_id = str(selected_row.get("id", ""))
    resolved_id = resolve_he_stage_alias(selected_id)
    return row_by_id(rows, resolved_id) or selected_row


def _override_payload(
    skill_set: str,
    top_k: int,
    override: dict[str, Any],
) -> dict[str, Any]:
    selected_row = override["row"]
    confidence = float(override["confidence"])
    candidates = [
        {
            "id": selected_row.get("id"),
            "level": selected_row.get("level"),
            "confidence": round(confidence, 4),
            "reason": override["reason"],
        }
    ]
    return _base_payload(
        skill_set,
        top_k,
        "selected",
        selected=selected_payload(selected_row, confidence),
        candidates=candidates,
    )


def _scored_payload(
    skill_set: str,
    top_k: int,
    scored: list[tuple[float, dict[str, Any], list[str]]],
    augmented_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    candidates = [
        {
            "id": row.get("id"),
            "level": row.get("level"),
            "confidence": confidence,
            "reason": "; ".join(reasons) if reasons else "matched manifest metadata",
        }
        for confidence, row, reasons in scored[:top_k]
    ]
    if not candidates:
        return _base_payload(
            skill_set,
            top_k,
            "no_match",
            operator_action="Ask a clarifying question or choose a documented fallback root skill set.",
        )
    selected_confidence, selected_row, _reasons = scored[0]
    selected_row = _selected_row_for_result(skill_set, selected_row, augmented_rows)
    selected = (
        selected_payload(selected_row, selected_confidence)
        if selected_confidence >= LOW_CONFIDENCE_THRESHOLD
        else None
    )
    status = "selected" if selected else "low_confidence"
    return _base_payload(
        skill_set,
        top_k,
        status,
        selected=selected,
        candidates=candidates,
        operator_action=None if selected else "Clarify before loading a latent module.",
    )


def route(
    skill_set: str,
    task: str,
    *,
    top_k: int = MAX_TOP_K,
    skillsets_dir: Path = DEFAULT_SKILLSETS_DIR,
) -> dict[str, Any]:
    bounded_top_k = max(1, min(int(top_k), MAX_TOP_K))
    rows, error_status, manifest_error = _read_manifest(skill_set, skillsets_dir)
    if manifest_error:
        return _base_payload(
            skill_set,
            bounded_top_k,
            "manifest_invalid",
            error=manifest_error,
            operator_action="Repair the skill-set manifest and rerun routing.",
        )
    if error_status:
        action = "Generate manifests before routing." if error_status == "manifest_missing" else "Choose a valid root skill set."
        return _base_payload(skill_set, bounded_top_k, error_status, operator_action=action)
    if skill_set in {"plugin-factory", "skill-factory"} and factory_scope_excluded(skill_set, task):
        return _factory_exclusion_payload(skill_set, bounded_top_k)

    augmented_rows = _augmented_rows(skill_set, rows, skillsets_dir)
    override, policy_error = _safe_policy_override(skill_set, task, rows, skillsets_dir)
    if policy_error:
        return _base_payload(
            skill_set,
            bounded_top_k,
            "routing_policy_invalid",
            error=policy_error,
            operator_action="Repair the routing policy and rerun routing.",
        )
    if override:
        return _override_payload(skill_set, bounded_top_k, override)
    return _scored_payload(skill_set, bounded_top_k, _score_rows(augmented_rows, task), augmented_rows)


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
