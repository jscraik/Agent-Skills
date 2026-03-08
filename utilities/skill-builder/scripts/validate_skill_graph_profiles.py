#!/usr/bin/env python3
"""Validate all-skill graph onboarding contracts and emit status artifacts."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[3]
COCKPIT_MODES = {"autopilot", "co-pilot", "manual"}
DEFAULT_PROFILE_REL_PATH = "references/task-profile.json"
DEFAULT_INVENTORY_POLICY = "docs/skill-graphs/governance/inventory-policy.json"
INVENTORY_SLICE_MODES = {"separate", "exclude"}
DEFAULT_INCLUDE_PREFIXES = (
    ".agents/skills/.system/",
    "auth/",
    "backend/",
    "frontend/",
    "github/",
    "interview/",
    "personas/",
    "product/",
    "utilities/",
)
DEFAULT_EXCLUDE_PREFIXES = (
    "skills/.system/",
    "utilities/recon-workbench/assets/template/.codex/skills/",
)
DEFAULT_SYSTEM_PREFIXES = (".agents/skills/.system/",)
MANUAL_SKILL_PATHS = {
    "github/gh-fix-ci",
    "github/gh-workflow",
    "github/local-action-verification",
    "product/ops/release",
    "utilities/1password",
    "utilities/agent-browser",
    "utilities/bootstrap",
    "utilities/codex-agent-creator",
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
    expected_mode: str
    wave: str
    scope_profile: str
    inventory_class: str


@dataclass(frozen=True)
class InventoryPolicy:
    include_prefixes: Tuple[str, ...]
    exclude_prefixes: Tuple[str, ...]
    system_prefixes: Tuple[str, ...]
    system_slice_mode: str


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_prefixes(values: Sequence[Any]) -> Tuple[str, ...]:
    out: List[str] = []
    for value in values:
        text = str(value).strip().replace("\\", "/")
        if not text:
            continue
        if not text.endswith("/"):
            text = text + "/"
        out.append(text)
    return tuple(dict.fromkeys(out))


def _matches_prefix(value: str, prefixes: Sequence[str]) -> bool:
    for prefix in prefixes:
        needle = prefix.rstrip("/")
        if value == needle or value.startswith(prefix):
            return True
    return False


def load_inventory_policy(repo_root: Path, raw_path: str, system_slice_mode: Optional[str]) -> InventoryPolicy:
    path = (repo_root / raw_path).resolve()
    if not path.exists():
        raise RuntimeError(f"Missing inventory policy file: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid inventory policy JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"Inventory policy must be a JSON object: {path}")

    include_prefixes = _normalize_prefixes(payload.get("include_prefixes", DEFAULT_INCLUDE_PREFIXES))
    exclude_prefixes = _normalize_prefixes(payload.get("exclude_prefixes", DEFAULT_EXCLUDE_PREFIXES))
    system_prefixes = _normalize_prefixes(payload.get("system_prefixes", DEFAULT_SYSTEM_PREFIXES))
    configured_mode = str(payload.get("system_slice_mode", "separate")).strip().lower()
    mode = (system_slice_mode or configured_mode).strip().lower()
    if mode not in INVENTORY_SLICE_MODES:
        raise RuntimeError(
            f"inventory policy system_slice_mode must be one of {sorted(INVENTORY_SLICE_MODES)}: {mode!r}"
        )

    return InventoryPolicy(
        include_prefixes=include_prefixes,
        exclude_prefixes=exclude_prefixes,
        system_prefixes=system_prefixes,
        system_slice_mode=mode,
    )


def is_active_skill(skill_md: Path, repo_root: Path, policy: InventoryPolicy) -> bool:
    rel = skill_md.relative_to(repo_root).as_posix()
    if rel == "SKILL.md":
        return False
    if policy.include_prefixes and not _matches_prefix(rel, policy.include_prefixes):
        return False
    if _matches_prefix(rel, policy.exclude_prefixes):
        return False
    return True


def discover_active_skills(repo_root: Path, policy: InventoryPolicy) -> List[SkillEntry]:
    entries: List[SkillEntry] = []
    for skill_md in sorted(repo_root.rglob("SKILL.md")):
        if not is_active_skill(skill_md, repo_root, policy):
            continue
        skill_dir = skill_md.parent
        rel_dir = skill_dir.relative_to(repo_root).as_posix()
        is_system = _matches_prefix(rel_dir, policy.system_prefixes)
        if is_system and policy.system_slice_mode == "exclude":
            continue
        mode = "manual" if rel_dir in MANUAL_SKILL_PATHS else "co-pilot"
        wave = "wave-1-manual" if mode == "manual" else "wave-2-co-pilot"
        scope_profile = "system" if is_system and policy.system_slice_mode == "separate" else rel_dir.split("/", 1)[0]
        inventory_class = "system" if is_system else "standard"
        entries.append(
            SkillEntry(
                skill_md=skill_md,
                skill_dir=skill_dir,
                relative_skill_dir=rel_dir,
                profile_path=skill_dir / "references" / "task-profile.json",
                expected_mode=mode,
                wave=wave,
                scope_profile=scope_profile,
                inventory_class=inventory_class,
            )
        )
    return entries


def add_error(errors: List[str], message: str) -> None:
    errors.append(message)


def parse_frontmatter_binding(skill_md: Path) -> Optional[str]:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    frontmatter = text[4:end]
    for line in frontmatter.splitlines():
        stripped = line.strip()
        if stripped.startswith("knowledge_graph_profile:"):
            return stripped.split(":", 1)[1].strip()
    return None


def validate_profile(entry: SkillEntry, payload: Dict[str, Any], errors: List[str]) -> None:
    required_top = {
        "schema_version": str,
        "profile_id": str,
        "scope_skill": str,
        "scope_profile": str,
        "rubric_version": str,
        "evaluator_version": str,
        "persona_set_id": str,
    }
    for field, expected_type in required_top.items():
        value = payload.get(field)
        if not isinstance(value, expected_type) or not str(value).strip():
            add_error(errors, f"missing/invalid `{field}`")

    expected_profile_id = entry.relative_skill_dir.replace("/", "-")
    if str(payload.get("profile_id", "")).strip() != expected_profile_id:
        add_error(errors, f"profile_id must equal `{expected_profile_id}`")

    if str(payload.get("scope_skill", "")).strip() != entry.relative_skill_dir:
        add_error(errors, f"scope_skill must equal `{entry.relative_skill_dir}`")

    expected_scope_profile = entry.scope_profile
    if str(payload.get("scope_profile", "")).strip() != expected_scope_profile:
        add_error(errors, f"scope_profile must equal `{expected_scope_profile}`")

    thresholds = payload.get("thresholds")
    if not isinstance(thresholds, dict):
        add_error(errors, "missing/invalid `thresholds` object")
    else:
        for key in (
            "stability_consecutive_passes",
            "critical_non_regression",
            "max_iterations",
            "max_elapsed_ms",
            "max_tokens",
            "no_improvement_escalation_limit",
        ):
            if key not in thresholds:
                add_error(errors, f"thresholds missing `{key}`")
        if "no_improvement_escalation_limit" in thresholds:
            try:
                if int(thresholds["no_improvement_escalation_limit"]) < 1:
                    add_error(errors, "thresholds.no_improvement_escalation_limit must be >= 1")
            except Exception:
                add_error(errors, "thresholds.no_improvement_escalation_limit must be numeric")

    criteria = payload.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        add_error(errors, "missing/invalid `criteria` list")
    else:
        total_weight = 0.0
        for idx, criterion in enumerate(criteria, start=1):
            if not isinstance(criterion, dict):
                add_error(errors, f"criteria[{idx}] must be object")
                continue
            for key in ("id", "label", "threshold", "weight", "critical"):
                if key not in criterion:
                    add_error(errors, f"criteria[{idx}] missing `{key}`")
            try:
                weight = float(criterion.get("weight", 0))
                if weight < 0:
                    add_error(errors, f"criteria[{idx}].weight must be >= 0")
                total_weight += max(weight, 0.0)
            except Exception:
                add_error(errors, f"criteria[{idx}].weight must be numeric")
        if total_weight <= 0:
            add_error(errors, "criteria total weight must be > 0")

    delegation = payload.get("delegation")
    if not isinstance(delegation, dict):
        add_error(errors, "missing required `delegation` object")
    else:
        mode = str(delegation.get("mode", "")).strip().lower()
        if mode == "collaboration":
            add_error(errors, "delegation.mode must be canonical (`co-pilot`), not `collaboration`")
        if mode not in COCKPIT_MODES:
            add_error(errors, "delegation.mode must be autopilot|co-pilot|manual")
        if mode != entry.expected_mode:
            add_error(errors, f"delegation.mode expected `{entry.expected_mode}`")
        for key in ("human_baseline_minutes", "ai_process_minutes", "probability_of_success"):
            if key not in delegation:
                add_error(errors, f"delegation missing `{key}`")
                continue
            try:
                value = float(delegation[key])
            except Exception:
                add_error(errors, f"delegation.{key} must be numeric")
                continue
            if key != "probability_of_success" and value < 0:
                add_error(errors, f"delegation.{key} must be >= 0")
            if key == "probability_of_success" and not (0.0 <= value <= 1.0):
                add_error(errors, "delegation.probability_of_success must be in range 0..1")
        rationale = str(delegation.get("rationale", "")).strip()
        if not rationale:
            add_error(errors, "delegation.rationale must be non-empty")


def parse_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def parse_telemetry_event_errors(health_path: Path) -> Optional[int]:
    if not health_path.exists():
        return None
    text = health_path.read_text(encoding="utf-8")
    match = re.search(r"Event envelope errors:\s*`?(\d+)`?", text)
    if match:
        return int(match.group(1))
    return None


def load_approver_count(path: Path) -> Optional[int]:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    reviewers = payload.get("reviewers")
    if not isinstance(reviewers, list):
        return None
    approvers = 0
    for reviewer in reviewers:
        if isinstance(reviewer, dict) and str(reviewer.get("role", "")).strip().lower() == "approver":
            approvers += 1
    return approvers


def blockers_with_sla(items: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in items:
        out.append(
            {
                **item,
                "owner": item.get("owner", "unassigned"),
                "due_date": item.get("due_date"),
                "escalation_date": item.get("escalation_date"),
            }
        )
    return out


def parse_args() -> argparse.Namespace:
    today = datetime.now(timezone.utc).date().isoformat()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(ROOT), help="Repository root")
    parser.add_argument(
        "--expected-count",
        type=int,
        default=0,
        help="Expected active skill count (0 disables strict count assertion)",
    )
    parser.add_argument(
        "--profile-index-out",
        default="artifacts/skill-graphs/onboarding/profile-index.json",
        help="Output path for per-skill profile validation index",
    )
    parser.add_argument(
        "--wave-readiness-out",
        default="artifacts/skill-graphs/onboarding/wave-readiness.json",
        help="Output path for wave readiness artifact",
    )
    parser.add_argument(
        "--decision-date",
        default=today,
        help="Decision date for wave readiness artifact",
    )
    parser.add_argument(
        "--inventory-policy",
        default=DEFAULT_INVENTORY_POLICY,
        help="Inventory allowlist/exclude policy JSON (repo-relative)",
    )
    parser.add_argument(
        "--system-slice-mode",
        choices=sorted(INVENTORY_SLICE_MODES),
        default=None,
        help="Override inventory policy system handling: separate or exclude",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    policy = load_inventory_policy(repo_root, args.inventory_policy, args.system_slice_mode)
    entries = discover_active_skills(repo_root, policy)
    generated_at = iso_now()

    if args.expected_count > 0 and len(entries) != args.expected_count:
        print(
            json.dumps(
                {
                    "error": "active skill count mismatch",
                    "expected": args.expected_count,
                    "actual": len(entries),
                },
                indent=2,
            )
        )
        return 2

    profile_rows: List[Dict[str, Any]] = []
    invalid_count = 0
    missing_profile_count = 0
    missing_legacy_binding_count = 0
    invalid_legacy_binding_count = 0
    wave_counts: Dict[str, int] = {"wave-1-manual": 0, "wave-2-co-pilot": 0}

    manual_total = 0
    manual_valid = 0
    copilot_total = 0
    copilot_valid = 0

    for entry in entries:
        wave_counts[entry.wave] = wave_counts.get(entry.wave, 0) + 1
        if entry.expected_mode == "manual":
            manual_total += 1
        else:
            copilot_total += 1

        errors: List[str] = []
        profile_exists = entry.profile_path.exists()
        if not profile_exists:
            missing_profile_count += 1
            add_error(errors, f"missing profile file `{entry.profile_path.relative_to(repo_root).as_posix()}`")
            payload = None
        else:
            payload = parse_json(entry.profile_path)
            if payload is None:
                add_error(errors, "profile file is not valid JSON object")
            else:
                validate_profile(entry, payload, errors)

        binding = parse_frontmatter_binding(entry.skill_md)
        binding_mode = "implicit-default"
        resolved_binding = DEFAULT_PROFILE_REL_PATH
        if binding:
            binding_mode = "legacy-frontmatter"
            resolved_binding = binding
            if binding != DEFAULT_PROFILE_REL_PATH:
                invalid_legacy_binding_count += 1
                add_error(
                    errors,
                    f"legacy knowledge_graph_profile must equal `{DEFAULT_PROFILE_REL_PATH}` when present",
                )
        else:
            missing_legacy_binding_count += 1

        if errors:
            invalid_count += 1
        else:
            if entry.expected_mode == "manual":
                manual_valid += 1
            else:
                copilot_valid += 1

        profile_rows.append(
            {
                "skill_path": entry.skill_md.relative_to(repo_root).as_posix(),
                "scope_skill": entry.relative_skill_dir,
                "wave": entry.wave,
                "profile_path": entry.profile_path.relative_to(repo_root).as_posix(),
                "profile_binding": resolved_binding,
                "profile_binding_mode": binding_mode,
                "delegation_mode": entry.expected_mode,
                "scope_profile": entry.scope_profile,
                "inventory_class": entry.inventory_class,
                "status": "valid" if not errors else "invalid",
                "errors": errors,
            }
        )

    profile_rows.sort(key=lambda row: row["scope_skill"])

    profile_index = {
        "schema_version": "1.0",
        "generated_at": generated_at,
        "decision_date": args.decision_date,
        "active_skill_count": len(entries),
        "expected_count": args.expected_count if args.expected_count > 0 else len(entries),
        "inventory_policy": {
            "include_prefixes": list(policy.include_prefixes),
            "exclude_prefixes": list(policy.exclude_prefixes),
            "system_prefixes": list(policy.system_prefixes),
            "system_slice_mode": policy.system_slice_mode,
        },
        "summary": {
            "valid_count": len(entries) - invalid_count,
            "invalid_count": invalid_count,
            "missing_profile_count": missing_profile_count,
            # Backward-compat: legacy binding is now optional (official posture).
            # Keep this as 0 so existing gates that treat it as an error signal do not trip.
            "missing_binding_count": 0,
            "missing_legacy_binding_count": missing_legacy_binding_count,
            "invalid_binding_count": invalid_legacy_binding_count,
            "wave_counts": wave_counts,
        },
        "skills": profile_rows,
    }

    profile_index_path = (repo_root / args.profile_index_out).resolve()
    profile_index_path.parent.mkdir(parents=True, exist_ok=True)
    profile_index_path.write_text(json.dumps(profile_index, indent=2) + "\n", encoding="utf-8")

    controls_dir = repo_root / "artifacts/skill-graphs/controls"
    required_controls = (
        controls_dir / "kill-switch.txt",
        controls_dir / "rollback-required.txt",
        controls_dir / "rollout-mode.txt",
    )
    wave0_blockers: List[Dict[str, Any]] = []
    for control_path in required_controls:
        if not control_path.exists():
            wave0_blockers.append(
                {
                    "code": "MISSING_CONTROL_FILE",
                    "detail": control_path.relative_to(repo_root).as_posix(),
                }
            )

    telemetry_errors = parse_telemetry_event_errors(
        repo_root / "docs/skill-graphs/telemetry/daily-skill-health.md"
    )
    if telemetry_errors is None:
        wave0_blockers.append(
            {
                "code": "TELEMETRY_HEALTH_MISSING",
                "detail": "Could not parse Event envelope errors metric from daily-skill-health.md",
            }
        )
    elif telemetry_errors > 0:
        wave0_blockers.append(
            {
                "code": "EVENT_ENVELOPE_ERRORS",
                "detail": f"Event envelope errors in decision window: {telemetry_errors}",
            }
        )

    approver_count = load_approver_count(
        repo_root / "docs/skill-graphs/governance/recursive-loop-approvers.yaml"
    )
    if approver_count is None:
        wave0_blockers.append(
            {
                "code": "APPROVER_POLICY_INVALID",
                "detail": "Could not parse approver policy reviewers[]",
            }
        )
    elif approver_count < 2:
        wave0_blockers.append(
            {
                "code": "APPROVER_CAPACITY",
                "detail": f"Approver count must be >=2 (actual={approver_count})",
            }
        )

    wave0_ready = not wave0_blockers
    wave1_blockers: List[Dict[str, Any]] = []
    if manual_valid < manual_total:
        wave1_blockers.append(
            {
                "code": "MANUAL_SKILL_VALIDATION",
                "detail": f"Manual skills valid {manual_valid}/{manual_total}",
            }
        )
    if not wave0_ready:
        wave1_blockers.append(
            {
                "code": "WAVE0_NOT_READY",
                "detail": "Wave 1 blocked until Wave 0 controls verification passes",
            }
        )
    wave1_ready = not wave1_blockers

    wave2_blockers: List[Dict[str, Any]] = []
    if copilot_valid < copilot_total:
        wave2_blockers.append(
            {
                "code": "COPILOT_SKILL_VALIDATION",
                "detail": f"Co-pilot skills valid {copilot_valid}/{copilot_total}",
            }
        )
    if not wave1_ready:
        wave2_blockers.append(
            {
                "code": "WAVE1_NOT_READY",
                "detail": "Wave 2 blocked until Wave 1 manual onboarding passes",
            }
        )
    if telemetry_errors is not None and telemetry_errors > 0:
        wave2_blockers.append(
            {
                "code": "EVENT_ENVELOPE_ERRORS",
                "detail": f"Wave 2 requires zero event envelope errors (actual={telemetry_errors})",
            }
        )
    wave2_ready = not wave2_blockers

    wave_readiness = {
        "schema_version": "1.0",
        "generated_at": generated_at,
        "decision_date": args.decision_date,
        "summary": {
            "active_skill_count": len(entries),
            "manual_skill_count": manual_total,
            "co_pilot_skill_count": copilot_total,
            "profile_valid_count": len(entries) - invalid_count,
            "profile_invalid_count": invalid_count,
            "event_envelope_errors": telemetry_errors,
            "approver_count": approver_count,
        },
        "waves": {
            "wave-0-controls": {
                "ready": wave0_ready,
                "checks": {
                    "required_controls_present": len(wave0_blockers) == 0
                    or all(blocker["code"] != "MISSING_CONTROL_FILE" for blocker in wave0_blockers),
                    "event_envelope_errors_zero": telemetry_errors == 0 if telemetry_errors is not None else False,
                    "approver_count_gte_2": bool(approver_count is not None and approver_count >= 2),
                },
                "blockers": blockers_with_sla(wave0_blockers),
            },
            "wave-1-manual": {
                "ready": wave1_ready,
                "checks": {
                    "manual_profiles_valid": manual_valid == manual_total,
                    "wave_0_ready": wave0_ready,
                },
                "coverage": {
                    "total": manual_total,
                    "valid": manual_valid,
                },
                "blockers": blockers_with_sla(wave1_blockers),
            },
            "wave-2-co-pilot": {
                "ready": wave2_ready,
                "checks": {
                    "co_pilot_profiles_valid": copilot_valid == copilot_total,
                    "wave_1_ready": wave1_ready,
                    "event_envelope_errors_zero": telemetry_errors == 0 if telemetry_errors is not None else False,
                },
                "coverage": {
                    "total": copilot_total,
                    "valid": copilot_valid,
                },
                "blockers": blockers_with_sla(wave2_blockers),
            },
        },
    }

    readiness_path = (repo_root / args.wave_readiness_out).resolve()
    readiness_path.parent.mkdir(parents=True, exist_ok=True)
    readiness_path.write_text(json.dumps(wave_readiness, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "active_skill_count": len(entries),
                "invalid_profiles": invalid_count,
                "missing_profiles": missing_profile_count,
                "missing_bindings": 0,
                "missing_legacy_bindings": missing_legacy_binding_count,
                "invalid_bindings": invalid_legacy_binding_count,
                "wave_0_ready": wave0_ready,
                "wave_1_ready": wave1_ready,
                "wave_2_ready": wave2_ready,
                "profile_index_out": str(profile_index_path.relative_to(repo_root)),
                "wave_readiness_out": str(readiness_path.relative_to(repo_root)),
                "system_slice_mode": policy.system_slice_mode,
            },
            indent=2,
        )
    )
    return 1 if invalid_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
