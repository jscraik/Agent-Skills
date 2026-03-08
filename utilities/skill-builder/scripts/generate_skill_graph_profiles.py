#!/usr/bin/env python3
"""Generate per-skill task profiles + onboarding artifacts for skill-graph rollout."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RUBRIC_VERSION = "2026-02-26"
DEFAULT_PROFILE_REL_PATH = "references/task-profile.json"

EXCLUDED_PREFIXES = (
    "skills/.system/",
    "utilities/recon-workbench/assets/template/.codex/skills/",
)
MANUAL_SKILL_PATHS = {
    "github/gh-fix-ci",
    "github/gh-workflow",
    "github/local-action-verification",
    "product/ops/release",
    "utilities/1password",
    "utilities/agent-browser",
    "utilities/bootstrap",
    "utilities/codex-agent-builder",
    "utilities/fix-mise",
    "utilities/run-tests-and-write-artifacts",
    "utilities/skill-installer",
    "utilities/using-git-worktrees",
    "utilities/verification-before-completion",
}


@dataclass(frozen=True)
class SkillEntry:
    skill_md: Path
    skill_dir: Path
    relative_skill_dir: str
    profile_path: Path
    wave: str
    delegation_mode: str


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def is_active_skill(skill_md: Path, repo_root: Path) -> bool:
    rel = skill_md.relative_to(repo_root).as_posix()
    if rel == "SKILL.md":
        return False
    if any(rel.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
        return False
    return True


def discover_active_skills(repo_root: Path) -> List[SkillEntry]:
    entries: List[SkillEntry] = []
    for skill_md in sorted(repo_root.rglob("SKILL.md")):
        if not is_active_skill(skill_md, repo_root):
            continue
        skill_dir = skill_md.parent
        rel_dir = skill_dir.relative_to(repo_root).as_posix()
        mode = "manual" if rel_dir in MANUAL_SKILL_PATHS else "co-pilot"
        wave = "wave-1-manual" if mode == "manual" else "wave-2-co-pilot"
        entries.append(
            SkillEntry(
                skill_md=skill_md,
                skill_dir=skill_dir,
                relative_skill_dir=rel_dir,
                profile_path=skill_dir / "references" / "task-profile.json",
                wave=wave,
                delegation_mode=mode,
            )
        )
    return entries


def build_default_profile(entry: SkillEntry, rubric_version: str) -> Dict[str, Any]:
    scope_profile = entry.relative_skill_dir.split("/", 1)[0]
    if entry.delegation_mode == "manual":
        human_baseline_minutes = 60.0
        ai_process_minutes = 20.0
        probability_of_success = 0.68
        rationale = (
            "Manual mode required: high-impact side effects need explicit human sign-off "
            "before applying candidate lessons."
        )
    else:
        human_baseline_minutes = 45.0
        ai_process_minutes = 15.0
        probability_of_success = 0.75
        rationale = (
            "Co-pilot mode default: advisory guidance with controlled rollout and "
            "human oversight for promotions."
        )

    return {
        "schema_version": "1.0",
        "profile_id": entry.relative_skill_dir.replace("/", "-"),
        "scope_skill": entry.relative_skill_dir,
        "scope_profile": scope_profile,
        "rubric_version": rubric_version,
        "evaluator_version": "v1",
        "persona_set_id": "default-v1",
        "thresholds": {
            "stability_consecutive_passes": 1,
            "critical_non_regression": True,
            "max_iterations": 4,
            "max_elapsed_ms": 120000,
            "max_tokens": 12000,
            "no_improvement_escalation_limit": 2,
        },
        "criteria": [
            {
                "id": "clarity",
                "label": "Instructional clarity",
                "threshold": 0.72,
                "weight": 0.34,
                "critical": True,
            },
            {
                "id": "specificity",
                "label": "Concrete implementation detail",
                "threshold": 0.68,
                "weight": 0.33,
                "critical": True,
            },
            {
                "id": "safety",
                "label": "Safety/compliance compliance",
                "threshold": 0.85,
                "weight": 0.33,
                "critical": True,
            },
        ],
        "delegation": {
            "mode": entry.delegation_mode,
            "human_baseline_minutes": human_baseline_minutes,
            "ai_process_minutes": ai_process_minutes,
            "probability_of_success": probability_of_success,
            "rationale": rationale,
        },
    }


def merge_existing(existing: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(defaults)
    for key in (
        "schema_version",
        "rubric_version",
        "evaluator_version",
        "persona_set_id",
    ):
        value = existing.get(key)
        if isinstance(value, str) and value.strip():
            merged[key] = value.strip()

    existing_thresholds = existing.get("thresholds")
    if isinstance(existing_thresholds, dict):
        merged_thresholds = dict(defaults["thresholds"])
        merged_thresholds.update(existing_thresholds)
        merged["thresholds"] = merged_thresholds

    if isinstance(existing.get("criteria"), list) and existing["criteria"]:
        merged["criteria"] = existing["criteria"]

    existing_delegation = existing.get("delegation")
    if isinstance(existing_delegation, dict):
        merged_delegation = dict(defaults["delegation"])
        merged_delegation.update(existing_delegation)
        mode = str(merged_delegation.get("mode", "")).strip().lower()
        if mode == "collaboration":
            mode = "co-pilot"
        merged_delegation["mode"] = mode or defaults["delegation"]["mode"]
        merged["delegation"] = merged_delegation

    return merged


def load_existing_profile(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def rewrite_knowledge_graph_profile_frontmatter(skill_md: Path, *, mode: str) -> bool:
    """Handle legacy knowledge_graph_profile frontmatter binding.

    Modes:
      - legacy: ensure `knowledge_graph_profile: references/task-profile.json` exists
      - remove: remove `knowledge_graph_profile:` if present
      - keep: no change
    """
    if mode == "keep":
        return False

    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return False

    end = text.find("\n---\n", 4)
    if end == -1:
        return False

    frontmatter = text[4:end]
    body = text[end + 5 :]
    lines = frontmatter.splitlines()

    target = f"knowledge_graph_profile: {DEFAULT_PROFILE_REL_PATH}"
    changed = False

    if mode == "legacy":
        found = False
        for idx, line in enumerate(lines):
            if line.strip().startswith("knowledge_graph_profile:"):
                found = True
                if line.strip() != target:
                    lines[idx] = target
                    changed = True
                break

        if not found:
            lines.append(target)
            changed = True
    elif mode == "remove":
        retained = [line for line in lines if not line.strip().startswith("knowledge_graph_profile:")]
        if len(retained) != len(lines):
            lines = retained
            changed = True
    else:
        raise ValueError(f"Unsupported mode: {mode}")

    if not changed:
        return False

    updated = "---\n" + "\n".join(lines).rstrip() + "\n---\n" + body
    skill_md.write_text(updated, encoding="utf-8")
    return True


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_baseline(
    *,
    baseline_path: Path,
    generated_at: str,
    entries: Iterable[SkillEntry],
    expected_count: Optional[int],
) -> None:
    skills = []
    for entry in entries:
        skills.append(
            {
                "skill_md": entry.skill_md.relative_to(ROOT).as_posix(),
                "skill_dir": entry.relative_skill_dir,
                "profile_file": entry.profile_path.relative_to(ROOT).as_posix(),
                "delegation_mode": entry.delegation_mode,
                "wave": entry.wave,
            }
        )

    payload: Dict[str, Any] = {
        "schema_version": "1.0",
        "generated_at": generated_at,
        "repo_root": ".",
        "expected_active_skill_count": expected_count,
        "active_skill_count": len(skills),
        "excluded_prefixes": list(EXCLUDED_PREFIXES),
        "excluded_root_skill": "SKILL.md",
        "skills": skills,
    }
    write_json(baseline_path, payload)


def write_checklist(path: Path, generated_at: str, entries: Iterable[SkillEntry]) -> None:
    rows = sorted(entries, key=lambda item: item.relative_skill_dir)
    wave_counts: Dict[str, int] = {}
    for row in rows:
        wave_counts[row.wave] = wave_counts.get(row.wave, 0) + 1

    lines = [
        "# Skill-by-Skill Onboarding Checklist (All-Skills Graph Migration)",
        "",
        f"- Generated at: `{generated_at}`",
        f"- Active skills: `{len(rows)}`",
        "- Status default: `pending`",
        "",
        "## Wave summary",
        "",
    ]
    for wave in sorted(wave_counts):
        lines.append(f"- {wave}: `{wave_counts[wave]}`")

    lines.extend(
        [
            "",
            "## Checklist",
            "",
            "| # | skill_path | profile_path | delegation_mode | wave | readiness_status | owner | due_date |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )

    for idx, row in enumerate(rows, start=1):
        skill_path = row.skill_md.relative_to(ROOT).as_posix()
        profile_path = row.profile_path.relative_to(ROOT).as_posix()
        lines.append(
            f"| {idx} | `{skill_path}` | `{profile_path}` | `{row.delegation_mode}` | `{row.wave}` | `pending` | `unassigned` | `tbd` |"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    today = datetime.now(timezone.utc).date().isoformat()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(ROOT), help="Repository root")
    parser.add_argument(
        "--rubric-version",
        default=DEFAULT_RUBRIC_VERSION,
        help="Rubric version set in generated task profiles",
    )
    parser.add_argument(
        "--expected-count",
        type=int,
        default=116,
        help="Expected number of active skills. Set 0 to disable assertion.",
    )
    parser.add_argument(
        "--baseline-out",
        default=f"artifacts/skill-graphs/onboarding/baseline-{today}.json",
        help="Path for baseline inventory JSON (repo-relative)",
    )
    parser.add_argument(
        "--checklist-out",
        default=f"artifacts/skill-graphs/onboarding/skill-onboarding-checklist-{today}.md",
        help="Path for onboarding checklist markdown (repo-relative)",
    )
    parser.add_argument(
        "--frontmatter-profile-binding",
        choices=["keep", "legacy", "remove"],
        default="keep",
        help=(
            "Legacy knowledge_graph_profile handling in SKILL.md frontmatter. "
            "`keep` (default): no frontmatter edits; "
            "`legacy`: add/update knowledge_graph_profile binding; "
            "`remove`: strip legacy binding for official frontmatter-only posture."
        ),
    )
    parser.add_argument(
        "--skip-frontmatter-binding",
        action="store_true",
        help="Deprecated alias. Equivalent to --frontmatter-profile-binding keep.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    entries = discover_active_skills(repo_root)
    if args.expected_count and len(entries) != args.expected_count:
        raise SystemExit(
            f"ERROR: active skill count mismatch. expected={args.expected_count} actual={len(entries)}"
        )

    generated_at = now_iso()
    profile_new = 0
    profile_updated = 0
    frontmatter_updated = 0

    for entry in entries:
        defaults = build_default_profile(entry, args.rubric_version)
        existing = load_existing_profile(entry.profile_path)
        payload = merge_existing(existing, defaults) if existing else defaults
        write_json(entry.profile_path, payload)
        if existing is None:
            profile_new += 1
        else:
            profile_updated += 1

        binding_mode = "keep" if args.skip_frontmatter_binding else args.frontmatter_profile_binding
        if rewrite_knowledge_graph_profile_frontmatter(entry.skill_md, mode=binding_mode):
            frontmatter_updated += 1

    baseline_path = (repo_root / args.baseline_out).resolve()
    write_baseline(
        baseline_path=baseline_path,
        generated_at=generated_at,
        entries=entries,
        expected_count=args.expected_count if args.expected_count > 0 else None,
    )

    checklist_path = (repo_root / args.checklist_out).resolve()
    write_checklist(checklist_path, generated_at, entries)

    print(
        json.dumps(
            {
                "active_skill_count": len(entries),
                "profiles_created": profile_new,
                "profiles_updated": profile_updated,
                "frontmatter_updated": frontmatter_updated,
                "baseline_out": str(baseline_path.relative_to(repo_root)),
                "checklist_out": str(checklist_path.relative_to(repo_root)),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
