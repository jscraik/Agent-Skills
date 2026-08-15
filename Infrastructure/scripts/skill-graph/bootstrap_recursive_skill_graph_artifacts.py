#!/usr/bin/env python3
"""Bootstrap Skill Graph control and canonical lesson artifact directories."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence


DEFAULT_CONTROL_ROOT = Path(".tmp/agent-skills-artifacts/skill-graphs/controls")
DEFAULT_LESSONS_ROOT = Path(".tmp/agent-skills-artifacts/skill-graphs/lessons")
DEFAULT_CONTROL_SKILLS = [
    "frontend/ui/ui-ux-creative-coding",
    "frontend/ui/react-ui-patterns",
    "frontend/ui/frontend-ui-design",
]

CONTROL_FILES: Dict[str, str] = {
    "kill-switch.txt": "off",
    "rollback-required.txt": "off",
    "rollout-mode.txt": "observe_only",
    "auto_capture.disabled": "0",
    "auto_apply.disabled": "0",
}
SKILL_CONTROL_FILES: Dict[str, str] = {
    "auto_capture.disabled": "0",
    "auto_apply.disabled": "0",
}


@dataclass(frozen=True)
class BootstrapResult:
    created: List[str]
    skipped: List[str]
    repaired: List[str]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize skill-graph control + lesson artifact roots.")
    parser.add_argument(
        "--controls-root",
        default=str(DEFAULT_CONTROL_ROOT),
        help="Path to controls root directory (default: .tmp/agent-skills-artifacts/skill-graphs/controls)",
    )
    parser.add_argument(
        "--lessons-root",
        default=str(DEFAULT_LESSONS_ROOT),
        help="Path to canonical lessons root directory (default: .tmp/agent-skills-artifacts/skill-graphs/lessons)",
    )
    parser.add_argument(
        "--scope-skills",
        action="append",
        default=[],
        help="Scope skill names to create per-skill control files for (repeatable)",
    )
    parser.add_argument(
        "--scope-skills-comma",
        default="",
        help="Comma separated scope skills to create per-skill control files for",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files with default values",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would change, but do not write files",
    )
    parser.add_argument(
        "--manifest",
        default=".harness/evidence/skill-graphs/pilot/artifact-parity-manifest.json",
        help="Optional compatibility manifest path for bootstrap run summary",
    )
    return parser.parse_args()


def _split_scope_skills(values: Sequence[str], comma_values: str) -> List[str]:
    skills: List[str] = []
    for item in values:
        if item:
            skills.append(str(item).strip())
    if comma_values:
        for item in str(comma_values).split(","):
            normalized = item.strip()
            if normalized:
                skills.append(normalized)
    ordered = skills or DEFAULT_CONTROL_SKILLS.copy()
    deduped: List[str] = []
    for item in ordered:
        if item and item not in deduped:
            deduped.append(item)
    return deduped


def _ensure_file(
    path: Path,
    text: str,
    *,
    overwrite: bool,
    dry_run: bool,
) -> bool:
    if path.exists() and not overwrite:
        return False
    if dry_run:
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = text if text == "" else f"{text}\n"
    path.write_text(payload, encoding="utf-8")
    return True


def _write_json(path: Path, value: Dict[str, Any], *, overwrite: bool, dry_run: bool) -> bool:
    if path.exists() and not overwrite:
        return False
    if dry_run:
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return True


def _bootstrap_controls(
    controls_root: Path,
    scope_skills: Sequence[str],
    *,
    overwrite: bool,
    dry_run: bool,
) -> List[str]:
    created: List[str] = []

    controls_root.mkdir(parents=True, exist_ok=True)
    for name, default_value in CONTROL_FILES.items():
        target = controls_root / name
        if _ensure_file(target, default_value, overwrite=overwrite, dry_run=dry_run):
            created.append(str(target))

    for scope_skill in scope_skills:
        normalized = scope_skill.strip()
        if not normalized:
            continue
        for name, default_value in SKILL_CONTROL_FILES.items():
            target = controls_root / "skills" / normalized / name
            if _ensure_file(target, default_value, overwrite=overwrite, dry_run=dry_run):
                created.append(str(target))
    return created


def _bootstrap_lessons(
    lessons_root: Path,
    *,
    overwrite: bool,
    dry_run: bool,
) -> List[str]:
    created: List[str] = []
    lessons_root.mkdir(parents=True, exist_ok=True)

    artifact_path = lessons_root / "canonical-lessons.jsonl"
    if not artifact_path.exists() or overwrite:
        if _ensure_file(artifact_path, "", overwrite=overwrite, dry_run=dry_run):
            created.append(str(artifact_path))

    index_path = lessons_root / "canonical-lesson-index.json"
    index_payload = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "scopes": {},
    }
    if _write_json(index_path, index_payload, overwrite=overwrite, dry_run=dry_run):
        created.append(str(index_path))
    return created


def _build_summary(
    controls_created: Sequence[str],
    lessons_created: Sequence[str],
    manifest_path: Path,
    *,
    dry_run: bool,
) -> Dict[str, Any]:
    return {
        "status": "ok",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "dry_run": bool(dry_run),
        "created_files": sorted(set(controls_created) | set(lessons_created)),
        "changed_count": len(set(controls_created) | set(lessons_created)),
    }


def main() -> int:
    args = _parse_args()
    controls_root = Path(args.controls_root).expanduser().resolve()
    lessons_root = Path(args.lessons_root).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve()
    scope_skills = _split_scope_skills(args.scope_skills, args.scope_skills_comma)

    controls_created = _bootstrap_controls(
        controls_root=controls_root,
        scope_skills=scope_skills,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
    )
    lessons_created = _bootstrap_lessons(
        lessons_root=lessons_root,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
    )

    summary = _build_summary(controls_created, lessons_created, manifest_path, dry_run=args.dry_run)

    manifest_payload = dict(summary)
    if args.dry_run:
        manifest_payload["status"] = "dry-run"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest_payload, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
