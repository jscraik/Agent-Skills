#!/usr/bin/env python3
"""Validate all-skill graph onboarding contracts and emit status artifacts."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from skill_graph_inventory import (
    DEFAULT_INVENTORY_POLICY,
    discover_inventory_skills,
    load_inventory_policy,
)

ROOT = Path(__file__).resolve().parents[3]
COCKPIT_MODES = {"autopilot", "co-pilot", "manual"}
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
    inventory_slice: str
    profile_path: Path
    expected_mode: str
    wave: str


@dataclass(frozen=True)
class TelemetryHealth:
    generated_at: Optional[datetime]
    window_start: Optional[str]
    window_end: Optional[str]
    event_envelope_errors_total: Optional[int]
    event_envelope_errors_waived: int
    event_envelope_errors_unresolved: Optional[int]


def iso_now() -> str:
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
        mode = "manual" if rel_dir in MANUAL_SKILL_PATHS else "co-pilot"
        wave = "wave-1-manual" if mode == "manual" else "wave-2-co-pilot"
        entries.append(
            SkillEntry(
                skill_md=skill_md,
                skill_dir=skill_dir,
                relative_skill_dir=rel_dir,
                inventory_slice=row.inventory_slice,
                profile_path=skill_dir / "references" / "task-profile.json",
                expected_mode=mode,
                wave=wave,
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

    expected_scope_profile = entry.relative_skill_dir.split("/", 1)[0]
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


def parse_telemetry_health(health_path: Path) -> Optional[TelemetryHealth]:
    if not health_path.exists():
        return None
    text = health_path.read_text(encoding="utf-8")
    generated_at: Optional[datetime] = None
    generated_match = re.search(r"Generated at:\s*`([^`]+)`", text)
    if generated_match:
        raw = generated_match.group(1).strip()
        try:
            generated_at = datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)
        except Exception:
            generated_at = None

    window_start: Optional[str] = None
    window_end: Optional[str] = None
    window_match = re.search(r"Window:\s*`(\d{4}-\d{2}-\d{2})\.\.(\d{4}-\d{2}-\d{2})`", text)
    if window_match:
        window_start = window_match.group(1)
        window_end = window_match.group(2)

    total_match = re.search(r"Event envelope errors total:\s*`?(\d+)`?", text)
    waived_match = re.search(r"Event envelope errors waived:\s*`?(\d+)`?", text)
    unresolved_match = re.search(r"Event envelope errors unresolved:\s*`?(\d+)`?", text)
    legacy_match = re.search(r"Event envelope errors:\s*`?(\d+)`?", text)

    total = int(total_match.group(1)) if total_match else None
    waived = int(waived_match.group(1)) if waived_match else 0
    unresolved = int(unresolved_match.group(1)) if unresolved_match else None

    if unresolved is None and total is not None:
        unresolved = max(total - waived, 0)
    if unresolved is None and legacy_match:
        unresolved = int(legacy_match.group(1))
        if total is None:
            total = unresolved
        waived = 0

    return TelemetryHealth(
        generated_at=generated_at,
        window_start=window_start,
        window_end=window_end,
        event_envelope_errors_total=total,
        event_envelope_errors_waived=waived,
        event_envelope_errors_unresolved=unresolved,
    )


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
    parser.add_argument("--expected-count", type=int, default=72, help="Expected active skill count")
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
        "--window-days",
        type=int,
        default=7,
        help="Expected decision window size used by daily health artifacts",
    )
    parser.add_argument(
        "--max-health-age-hours",
        type=float,
        default=24.0,
        help="Maximum allowed age for daily health generated_at before readiness blocks",
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
    generated_at = iso_now()

    if args.expected_count and len(entries) != args.expected_count:
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
        "expected_count": args.expected_count,
        "inventory_policy": str(policy.source_path.relative_to(repo_root)),
        "system_slice_mode": policy.system_slice_mode,
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

    telemetry_health = parse_telemetry_health(
        repo_root / "docs/skill-graphs/telemetry/daily-skill-health.md"
    )
    telemetry_errors_unresolved: Optional[int] = None
    telemetry_errors_total: Optional[int] = None
    telemetry_errors_waived = 0
    telemetry_generated_at: Optional[str] = None
    telemetry_window_start: Optional[str] = None
    telemetry_window_end: Optional[str] = None
    telemetry_freshness_ok = False

    if telemetry_health is None or telemetry_health.event_envelope_errors_unresolved is None:
        wave0_blockers.append(
            {
                "code": "TELEMETRY_HEALTH_MISSING",
                "detail": "Could not parse Event envelope errors metric from daily-skill-health.md",
            }
        )
    else:
        telemetry_errors_unresolved = telemetry_health.event_envelope_errors_unresolved
        telemetry_errors_total = telemetry_health.event_envelope_errors_total
        telemetry_errors_waived = telemetry_health.event_envelope_errors_waived
        telemetry_generated_at = (
            telemetry_health.generated_at.replace(microsecond=0).isoformat().replace("+00:00", "Z")
            if telemetry_health.generated_at
            else None
        )
        telemetry_window_start = telemetry_health.window_start
        telemetry_window_end = telemetry_health.window_end

        freshness_checks_ok = True
        if telemetry_health.generated_at is None:
            freshness_checks_ok = False
            wave0_blockers.append(
                {
                    "code": "TELEMETRY_HEALTH_STALE",
                    "detail": "daily-skill-health.md missing parseable Generated at timestamp",
                }
            )
        else:
            max_age_hours = max(args.max_health_age_hours, 0.0)
            age_hours = (datetime.now(timezone.utc) - telemetry_health.generated_at).total_seconds() / 3600.0
            if age_hours > max_age_hours:
                freshness_checks_ok = False
                wave0_blockers.append(
                    {
                        "code": "TELEMETRY_HEALTH_STALE",
                        "detail": f"daily-skill-health.md age {age_hours:.2f}h exceeds {max_age_hours:.2f}h",
                    }
                )

        expected_end = args.decision_date
        try:
            expected_end_date = datetime.fromisoformat(expected_end).date()
            expected_start_date = expected_end_date - timedelta(days=max(args.window_days, 1) - 1)
            expected_start = expected_start_date.isoformat()
        except Exception:
            freshness_checks_ok = False
            expected_start = None
            wave0_blockers.append(
                {
                    "code": "TELEMETRY_WINDOW_MISMATCH",
                    "detail": f"Invalid --decision-date provided: {args.decision_date}",
                }
            )

        if expected_start is not None:
            if telemetry_health.window_start != expected_start or telemetry_health.window_end != expected_end:
                freshness_checks_ok = False
                wave0_blockers.append(
                    {
                        "code": "TELEMETRY_WINDOW_MISMATCH",
                        "detail": (
                            "daily-skill-health.md window mismatch "
                            f"(expected {expected_start}..{expected_end}, "
                            f"actual {telemetry_health.window_start}..{telemetry_health.window_end})"
                        ),
                    }
                )

        telemetry_freshness_ok = freshness_checks_ok

    if telemetry_errors_unresolved is not None and telemetry_errors_unresolved > 0:
        wave0_blockers.append(
            {
                "code": "EVENT_ENVELOPE_ERRORS",
                "detail": f"Unresolved event envelope errors in decision window: {telemetry_errors_unresolved}",
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
    if telemetry_errors_unresolved is not None and telemetry_errors_unresolved > 0:
        wave2_blockers.append(
            {
                "code": "EVENT_ENVELOPE_ERRORS",
                "detail": (
                    "Wave 2 requires zero unresolved event envelope errors "
                    f"(actual={telemetry_errors_unresolved})"
                ),
            }
        )
    wave2_ready = not wave2_blockers

    # Build triage summary for blockers with owners/acceptance criteria
    triage_summary: List[Dict[str, Any]] = []
    for wave_name, wave_blockers in [
        ("wave-0-controls", wave0_blockers),
        ("wave-1-manual", wave1_blockers),
        ("wave-2-co-pilot", wave2_blockers),
    ]:
        for blocker in wave_blockers:
            triage_summary.append({
                "wave": wave_name,
                "code": blocker.get("code", "UNKNOWN"),
                "owner": blocker.get("owner", "unassigned"),
                "due_date": blocker.get("due_date"),
                "escalation_date": blocker.get("escalation_date"),
                "acceptance": "pending" if blocker.get("due_date") else "triage-needed",
            })

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
            "event_envelope_errors": telemetry_errors_unresolved,
            "event_envelope_errors_total": telemetry_errors_total,
            "event_envelope_errors_waived": telemetry_errors_waived,
            "event_envelope_errors_unresolved": telemetry_errors_unresolved,
            "approver_count": approver_count,
            "telemetry_generated_at": telemetry_generated_at,
            "telemetry_window_start": telemetry_window_start,
            "telemetry_window_end": telemetry_window_end,
            "telemetry_freshness_ok": telemetry_freshness_ok,
            "triage_summary": triage_summary,
        },
        "waves": {
            "wave-0-controls": {
                "ready": wave0_ready,
                "checks": {
                    "required_controls_present": len(wave0_blockers) == 0
                    or all(blocker["code"] != "MISSING_CONTROL_FILE" for blocker in wave0_blockers),
                    "event_envelope_errors_zero": (
                        telemetry_errors_unresolved == 0 if telemetry_errors_unresolved is not None else False
                    ),
                    "telemetry_freshness_ok": telemetry_freshness_ok,
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
                    "event_envelope_errors_zero": (
                        telemetry_errors_unresolved == 0 if telemetry_errors_unresolved is not None else False
                    ),
                    "telemetry_freshness_ok": telemetry_freshness_ok,
                },
                "coverage": {
                    "total": copilot_total,
                    "valid": copilot_valid,
                },
                "blockers": blockers_with_sla(wave2_blockers),
            },
        },
    }

    # Governance check: blockers with dates must have owners
    for wave_name, wave_blockers in [
        ("wave-0-controls", wave0_blockers),
        ("wave-1-manual", wave1_blockers),
        ("wave-2-co-pilot", wave2_blockers),
    ]:
        for blocker in wave_blockers:
            has_dates = blocker.get("due_date") or blocker.get("escalation_date")
            owner = blocker.get("owner", "unassigned")
            if has_dates and (not owner or owner == "unassigned"):
                raise SystemExit(
                    f"FAIL governance: {wave_name} blocker {blocker.get('code', 'UNKNOWN')} "
                    f"has dates but no owner assigned"
                )

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
            },
            indent=2,
        )
    )
    return 1 if invalid_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
