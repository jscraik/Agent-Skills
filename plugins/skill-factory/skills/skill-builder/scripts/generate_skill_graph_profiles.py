#!/usr/bin/env python3
"""Generate per-skill task profiles + onboarding artifacts for skill-graph rollout."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from skill_graph_inventory import (
    DEFAULT_INVENTORY_POLICY,
    discover_inventory_skills,
    load_inventory_policy,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RUBRIC_VERSION = "2026-02-26"
DEFAULT_PROFILE_REL_PATH = "references/task-profile.json"
MANUAL_SKILL_PATHS = {
    "github/gh-workflow",
    "github/local-action-verification",
    "product/ops/release",
    "utilities/1password",
    "utilities/agent-browser",
    "utilities/bootstrap",
    "utilities/codex-agent-creator",
    "utilities/diagram-context-refresh",
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
    source_skill_dirs: tuple[str, ...]
    scope_skill: str
    inventory_slice: str
    profile_path: Path
    wave: str
    delegation_mode: str


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def discover_active_skills(
    repo_root: Path,
    *,
    inventory_policy_path: str,
    system_slice_mode: Optional[str],
) -> List[SkillEntry]:
    policy = load_inventory_policy(
        repo_root,
        policy_rel_path=inventory_policy_path,
        system_slice_mode_override=system_slice_mode,
    )
    entries: List[SkillEntry] = []
    for row in discover_inventory_skills(repo_root, policy):
        if row.inventory_slice != "operational":
            continue
        skill_md = row.skill_md
        skill_dir = skill_md.parent
        rel_dir = row.relative_skill_dir
        scope_skill = row.scope_skill
        mode = "manual" if scope_skill in MANUAL_SKILL_PATHS else "co-pilot"
        wave = "wave-1-manual" if mode == "manual" else "wave-2-co-pilot"
        entries.append(
            SkillEntry(
                skill_md=skill_md,
                skill_dir=skill_dir,
                relative_skill_dir=rel_dir,
                source_skill_dirs=row.source_skill_dirs or (rel_dir,),
                scope_skill=scope_skill,
                inventory_slice=row.inventory_slice,
                profile_path=skill_dir / "references" / "task-profile.json",
                wave=wave,
                delegation_mode=mode,
            )
        )
    return entries


def build_default_profile(entry: SkillEntry, rubric_version: str) -> Dict[str, Any]:
    scope_profile = entry.scope_skill.split("/", 1)[0]
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
        "profile_id": entry.scope_skill.replace("/", "-"),
        "scope_skill": entry.scope_skill,
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

    # Preserve non-canonical extension fields (for example knowledge_graph blocks)
    # while still emitting canonical profile_id/scope_* keys from defaults.
    for key, value in existing.items():
        if key not in merged:
            merged[key] = value

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
    repo_root: Path,
    baseline_path: Path,
    generated_at: str,
    entries: Iterable[SkillEntry],
    expected_count: Optional[int],
    inventory_policy: str,
    system_slice_mode: str,
) -> None:
    skills = []
    for entry in entries:
        skills.append(
            {
                "skill_md": entry.skill_md.relative_to(repo_root).as_posix(),
                "selected_skill_dir": entry.relative_skill_dir,
                "source_skill_dirs": list(entry.source_skill_dirs),
                "scope_skill": entry.scope_skill,
                "profile_file": entry.profile_path.relative_to(repo_root).as_posix(),
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
        "inventory_policy": inventory_policy,
        "system_slice_mode": system_slice_mode,
        "excluded_root_skill": "SKILL.md",
        "skills": skills,
    }
    write_json(baseline_path, payload)


def load_owner_map(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _sanitize_assignment(value: Any, fallback: str) -> str:
    text = str(value).strip() if value is not None else ""
    return text if text else fallback


def write_checklist(
    repo_root: Path,
    path: Path,
    generated_at: str,
    entries: Iterable[SkillEntry],
    owner_map: Dict[str, Any],
) -> None:
    rows = sorted(entries, key=lambda item: item.scope_skill)
    wave_counts: Dict[str, int] = {}
    for row in rows:
        wave_counts[row.wave] = wave_counts.get(row.wave, 0) + 1

    defaults_raw = owner_map.get("defaults", {}) if isinstance(owner_map.get("defaults"), dict) else {}
    fallback_status = _sanitize_assignment(defaults_raw.get("readiness_status"), "pending")
    fallback_owner = _sanitize_assignment(defaults_raw.get("owner"), "unassigned")
    fallback_due_date = _sanitize_assignment(defaults_raw.get("due_date"), "tbd")

    skills_map = owner_map.get("skills", {}) if isinstance(owner_map.get("skills"), dict) else {}
    fallback_row_count = 0

    lines = [
        "# Skill-by-Skill Onboarding Checklist (All-Skills Graph Migration)",
        "",
        f"- Generated at: `{generated_at}`",
        f"- Active skills: `{len(rows)}`",
        f"- Status default: `{fallback_status}`",
        f"- Owner default: `{fallback_owner}`",
        f"- Due date default: `{fallback_due_date}`",
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
        skill_path = row.skill_md.relative_to(repo_root).as_posix()
        profile_path = row.profile_path.relative_to(repo_root).as_posix()
        assignment = None
        candidate_keys = (skill_path, row.scope_skill, row.relative_skill_dir)
        for key in candidate_keys:
            raw = skills_map.get(key)
            if isinstance(raw, dict):
                assignment = raw
                break

        if assignment is None:
            fallback_row_count += 1
            readiness_status = fallback_status
            owner = fallback_owner
            due_date = fallback_due_date
        else:
            readiness_status = _sanitize_assignment(assignment.get("readiness_status"), fallback_status)
            owner = _sanitize_assignment(assignment.get("owner"), fallback_owner)
            due_date = _sanitize_assignment(assignment.get("due_date"), fallback_due_date)

        lines.append(
            f"| {idx} | `{skill_path}` | `{profile_path}` | `{row.delegation_mode}` | `{row.wave}` | `{readiness_status}` | `{owner}` | `{due_date}` |"
        )

    lines.extend(
        [
            "",
            "## Assignment coverage",
            "",
            f"- Rows using explicit per-skill assignment: `{len(rows) - fallback_row_count}`",
            f"- Rows using fallback defaults: `{fallback_row_count}`",
        ]
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
        "--owner-map",
        default="artifacts/skill-graphs/onboarding/skill-owner-map.json",
        help="Optional JSON map for checklist readiness_status/owner/due_date fields",
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
    parser.add_argument(
        "--inventory-policy",
        default=DEFAULT_INVENTORY_POLICY,
        help="Inventory allowlist/exclude policy JSON (repo-relative)",
    )
    parser.add_argument(
        "--system-slice-mode",
        choices=["exclude", "separate"],
        default=None,
        help="Override inventory policy system handling: separate or exclude",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    entries = discover_active_skills(
        repo_root,
        inventory_policy_path=args.inventory_policy,
        system_slice_mode=args.system_slice_mode,
    )
    policy = load_inventory_policy(
        repo_root,
        policy_rel_path=args.inventory_policy,
        system_slice_mode_override=args.system_slice_mode,
    )
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
        repo_root=repo_root,
        baseline_path=baseline_path,
        generated_at=generated_at,
        entries=entries,
        expected_count=args.expected_count if args.expected_count > 0 else None,
        inventory_policy=str(policy.source_path.relative_to(repo_root)),
        system_slice_mode=policy.system_slice_mode,
    )

    checklist_path = (repo_root / args.checklist_out).resolve()
    owner_map_path = (repo_root / args.owner_map).resolve()
    owner_map = load_owner_map(owner_map_path)
    write_checklist(repo_root, checklist_path, generated_at, entries, owner_map)

    print(
        json.dumps(
            {
                "active_skill_count": len(entries),
                "profiles_created": profile_new,
                "profiles_updated": profile_updated,
                "frontmatter_updated": frontmatter_updated,
                "baseline_out": str(baseline_path.relative_to(repo_root)),
                "checklist_out": str(checklist_path.relative_to(repo_root)),
                "owner_map": str(owner_map_path.relative_to(repo_root)),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
