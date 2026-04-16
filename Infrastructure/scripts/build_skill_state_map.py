#!/usr/bin/env python3
"""Build a single HTML skill state map from existing recursive-skill artifacts.

This renderer keeps readiness, controls, operational health, run/compliance, and
learning/change signals separated into four linked views:
1) Global program strip
2) Skill state map
3) Run/compliance lane
4) Learning/change lane
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


CANONICAL_DAILY_HEALTH = "Docs/skill-graphs/telemetry/daily-skill-health.md"
LEGACY_DAILY_HEALTH = "Infrastructure/artifacts/skill-graphs/telemetry/daily-skill-health.md"
DEFAULT_INVENTORY_POLICY = "Docs/skill-graphs/governance/inventory-policy.json"
DEFAULT_GRAPH_ADAPTER_DIR = "Infrastructure/artifacts/skill-graphs/graph-adapter"
DEFAULT_SYSTEM_PREFIXES = ("Skills/.system/", ".agents/skills/.system/")
CORE_PROFILES = {"auth", "backend", "frontend", "github", "utilities"}
CLASS_TOKEN_PATTERN = re.compile(r"[^a-z0-9_-]+")
FALSY_CONTROL_VALUES = {"0", "off", "false", "inactive", "disabled", "no", "none"}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_class_token(value: Any, default: str = "unknown") -> str:
    raw = str(value or "").strip().lower()
    cleaned = CLASS_TOKEN_PATTERN.sub("_", raw).strip("_-")
    return cleaned or default


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def parse_dt(value: str) -> Optional[datetime]:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def parse_control_state(raw_text: str) -> bool:
    text = raw_text.strip().lower()
    if not text:
        return False
    return text not in FALSY_CONTROL_VALUES


def esc(value: Any) -> str:
    text = str(value if value is not None else "")
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def parse_daily_health(daily_health_path: Path) -> Dict[str, Any]:
    text = daily_health_path.read_text(encoding="utf-8")
    metrics = {
        "generated_at": "unknown",
        "decision": "unknown",
        "window": "unknown",
        "event_envelope_errors": "unknown",
    }
    for line in text.splitlines():
        if line.startswith("- Generated at:"):
            metrics["generated_at"] = line.split("`")[1] if "`" in line else line.split(":", 1)[1].strip()
        if line.startswith("- Decision:"):
            metrics["decision"] = line.split("`")[1] if "`" in line else line.split(":", 1)[1].strip()
        if line.startswith("- Window:"):
            metrics["window"] = line.split("`")[1] if "`" in line else line.split(":", 1)[1].strip()
        if line.startswith("- Event envelope errors:"):
            metrics["event_envelope_errors"] = (
                line.split("`")[1] if "`" in line else line.split(":", 1)[1].strip()
            )
    return metrics


@dataclass
class SkillNode:
    scope_skill: str
    scope_profile: str
    profile_id: str
    delegation_mode: str
    wave: str
    wave_ready: bool
    inventory_slice: str = "operational"
    display_slice: str = "extended"
    profile_status: str = "valid"
    thresholds: Dict[str, Any] = field(default_factory=dict)
    criteria_ids: List[str] = field(default_factory=list)
    recent_status: str = "no_recent_run_data"
    recent_stop_reason: str = "n/a"
    recent_run: str = "n/a"
    parity: str = "empty"
    promotion: str = "none"
    candidate_pressure: float = 0.0
    queue_reason: str = "none"
    queue_count: int = 0
    pilot_window_runs: int = 0
    total_runs: int = 0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", default=".")
    p.add_argument("--out-html", default="Infrastructure/artifacts/skill-graphs/telemetry/skill-state-map.html", help="Output HTML path")
    p.add_argument("--controls-dir", default="Infrastructure/artifacts/skill-graphs/controls", help="Control files directory")
    p.add_argument("--wave-readiness", default="Infrastructure/artifacts/skill-graphs/onboarding/wave-readiness.json")
    p.add_argument("--profile-index", default="Infrastructure/artifacts/skill-graphs/onboarding/profile-index.json")
    p.add_argument(
        "--inventory-policy",
        default=DEFAULT_INVENTORY_POLICY,
        help="Inventory allowlist/exclude policy JSON (repo-relative)",
    )
    p.add_argument(
        "--system-slice-mode",
        choices=["exclude", "separate"],
        default=None,
        help="Override inventory policy system handling: separate or exclude",
    )
    p.add_argument("--shadow-dashboard", default="Infrastructure/artifacts/skill-graphs/pilot/shadow-dashboard.json")
    p.add_argument("--daily-health-md", default=CANONICAL_DAILY_HEALTH)
    p.add_argument("--promotion-queue-md", default="Infrastructure/artifacts/skill-graphs/telemetry/promotion-queue.md")
    p.add_argument("--promotion-validation", default="Infrastructure/artifacts/skill-graphs/pilot/promotion-validation-report.json")
    p.add_argument("--parity-manifest", default="Infrastructure/artifacts/skill-graphs/pilot/artifact-parity-manifest.json")
    p.add_argument("--candidates-jsonl", default="Infrastructure/artifacts/skill-graphs/telemetry/candidates.jsonl")
    p.add_argument("--runs-root", default="Infrastructure/artifacts/skill-graphs/runs")
    p.add_argument("--feedback-log", default="Infrastructure/artifacts/skill-graphs/telemetry/feedback.log")
    p.add_argument("--graph-adapter-dir", default=DEFAULT_GRAPH_ADAPTER_DIR)
    p.add_argument("--with-graph-adapter", action="store_true")
    return p.parse_args()


def enforce_daily_health_contract(repo_root: Path, daily_health_path: Path) -> None:
    canonical = (repo_root / CANONICAL_DAILY_HEALTH).resolve()
    if daily_health_path != canonical:
        raise RuntimeError(
            "Path divergence: --daily-health-md must resolve to "
            f"{CANONICAL_DAILY_HEALTH} (got {daily_health_path})"
        )
    if not canonical.exists():
        raise RuntimeError(f"Path divergence: canonical daily health is missing ({canonical})")
    legacy = (repo_root / LEGACY_DAILY_HEALTH).resolve()
    if legacy.exists():
        docs_text = canonical.read_text(encoding="utf-8")
        legacy_text = legacy.read_text(encoding="utf-8")
        if docs_text != legacy_text:
            raise RuntimeError(
                f"Path divergence: docs and artifacts daily health files differ ({canonical} vs {legacy})."
            )


def load_inventory_policy(repo_root: Path, path: Path, override_mode: Optional[str]) -> Dict[str, Any]:
    payload = read_json(path, {})
    if not isinstance(payload, dict):
        raise RuntimeError(f"Invalid inventory policy JSON: {path}")
    mode = str(payload.get("system_slice_mode", "exclude")).strip().lower()
    if override_mode:
        mode = override_mode
    if mode not in {"exclude", "separate"}:
        raise RuntimeError("inventory policy system_slice_mode must be one of ['exclude', 'separate']")
    allowlist = sorted({str(item).strip().strip("/") for item in payload.get("allowlist_scope_skills", []) if str(item).strip()})
    system_prefixes = [
        (str(item).strip().replace("\\", "/").rstrip("/") + "/")
        for item in payload.get("system_prefixes", list(DEFAULT_SYSTEM_PREFIXES))
        if str(item).strip()
    ]
    payload["allowlist_scope_skills"] = allowlist
    payload["system_prefixes"] = sorted(set(system_prefixes))
    payload["system_slice_mode"] = mode
    payload["source_path"] = str(path.relative_to(repo_root))
    return payload


def iter_system_skills(repo_root: Path, policy: Dict[str, Any]) -> List[str]:
    if policy.get("system_slice_mode") != "separate":
        return []
    system_prefixes: Sequence[str] = policy.get("system_prefixes", [])
    out: List[str] = []
    for skill_md in sorted(repo_root.rglob("SKILL.md")):
        rel = skill_md.relative_to(repo_root).as_posix()
        rel_dir = skill_md.parent.relative_to(repo_root).as_posix()
        if any(rel.startswith(prefix) for prefix in system_prefixes):
            out.append(rel_dir)
    return sorted(set(out))


def discover_nodes(
    repo_root: Path,
    profile_index: Dict[str, Any],
    wave_readiness: Dict[str, Any],
    inventory_policy: Dict[str, Any],
) -> List[SkillNode]:
    rows = profile_index.get("skills") if isinstance(profile_index, dict) else []
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("profile-index.json is missing a non-empty skills[] inventory.")

    wave_ready: Dict[str, bool] = {}
    waves = wave_readiness.get("waves") if isinstance(wave_readiness, dict) else {}
    if isinstance(waves, dict):
        for wave, payload in waves.items():
            if isinstance(payload, dict):
                wave_ready[wave] = bool(payload.get("ready"))

    nodes: List[SkillNode] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        scope_skill = str(row.get("scope_skill", "")).strip()
        if not scope_skill:
            continue
        profile_path_rel = str(row.get("profile_path", "")).strip()
        if not profile_path_rel:
            continue
        profile_path = (repo_root / profile_path_rel).resolve()
        try:
            profile_path.relative_to(repo_root)
        except ValueError:
            continue
        profile_obj = read_json(profile_path, {})
        if not isinstance(profile_obj, dict):
            profile_obj = {}
        delegation = profile_obj.get("delegation") if isinstance(profile_obj.get("delegation"), dict) else {}
        criteria = profile_obj.get("criteria") if isinstance(profile_obj.get("criteria"), list) else []
        scope_profile = str(row.get("scope_skill", "")).split("/", 1)[0]
        display_slice = "core" if scope_profile in CORE_PROFILES else "extended"
        nodes.append(
            SkillNode(
                scope_skill=scope_skill,
                scope_profile=scope_profile,
                profile_id=str(profile_obj.get("profile_id", "")).strip() or scope_skill.replace("/", "-"),
                delegation_mode=str(delegation.get("mode", row.get("delegation_mode", "co-pilot"))).strip() or "co-pilot",
                wave=str(row.get("wave", "wave-2-co-pilot")).strip() or "wave-2-co-pilot",
                wave_ready=wave_ready.get(str(row.get("wave", "")), False),
                display_slice=display_slice,
                profile_status=str(
                    row.get("task_profile_status", row.get("status", "unknown"))
                ).strip()
                or "unknown",
                thresholds=profile_obj.get("thresholds") if isinstance(profile_obj.get("thresholds"), dict) else {},
                criteria_ids=[str(item.get("id", "")).strip() for item in criteria if isinstance(item, dict) and str(item.get("id", "")).strip()],
            )
        )

    for scope_skill in iter_system_skills(repo_root, inventory_policy):
        if any(node.scope_skill == scope_skill for node in nodes):
            continue
        nodes.append(
            SkillNode(
                scope_skill=scope_skill,
                scope_profile="system",
                profile_id=f"system-{scope_skill.replace('/', '-')}",
                delegation_mode="manual",
                wave="wave-system",
                wave_ready=True,
                inventory_slice="system",
                display_slice="system",
                profile_status="system",
            )
        )

    return sorted(nodes, key=lambda item: (item.inventory_slice, item.scope_profile, item.scope_skill))


def build_node_alias_index(nodes: Sequence[SkillNode]) -> Dict[str, SkillNode]:
    """Build a strict alias map for run/profile joins while rejecting ambiguous aliases."""
    collisions: Dict[str, int] = {}
    alias_map: Dict[str, SkillNode] = {}

    def add(alias: str, node: SkillNode) -> None:
        key = str(alias or "").strip().lower()
        if not key:
            return
        existing = alias_map.get(key)
        if existing and existing is not node:
            collisions[key] = collisions.get(key, 1) + 1
            alias_map.pop(key, None)
            return
        if key in collisions:
            return
        alias_map[key] = node

    for node in nodes:
        scope = node.scope_skill.strip("/")
        profile = node.profile_id.strip("/")
        scope_slug = scope.replace("/", "-")
        basename = scope.rsplit("/", 1)[-1]
        add(scope, node)
        add(scope_slug, node)
        add(basename, node)
        add(profile, node)
        add(profile.replace("/", "-"), node)
        if "-" in profile:
            # Legacy runs may emit compact profile ids like "ui-ux-creative-coding".
            maybe_short = profile.split("-", 2)
            if len(maybe_short) == 3:
                add(maybe_short[2], node)
    return alias_map


def apply_shadow_runs(
    nodes: List[SkillNode],
    shadow_dashboard: Dict[str, Any],
    parity_manifest: Dict[str, Any],
    runs_root: Path,
    queue_reason_by_run_id: Dict[str, str],
) -> List[Dict[str, Any]]:
    alias_map = build_node_alias_index(nodes)
    run_rows: List[Dict[str, Any]] = []
    row_by_run_id: Dict[str, Dict[str, Any]] = {}
    shadow_run_ids: set[str] = set()

    def resolve_node(profile_id: str, scope_skill: str) -> Optional[SkillNode]:
        for value in (profile_id, scope_skill):
            key = str(value or "").strip().lower()
            if key and key in alias_map:
                return alias_map[key]
        return None

    def ensure_row(run_id: str) -> Dict[str, Any]:
        row = row_by_run_id.get(run_id)
        if row is None:
            row = {"run_id": run_id}
            row_by_run_id[run_id] = row
        return row

    def apply_values(target: Dict[str, Any], source: Dict[str, Any], *, overwrite: bool) -> None:
        for key, value in source.items():
            if key == "run_id" or value is None:
                continue
            text = value.strip() if isinstance(value, str) else value
            if isinstance(text, str) and not text:
                continue
            if overwrite or key not in target or target.get(key) in {"", None, "unknown"}:
                target[key] = text

    parity_runs = parity_manifest.get("runs") if isinstance(parity_manifest, dict) else []
    parity_by_run_id: Dict[str, str] = {}
    promotion_by_run_id: Dict[str, str] = {}
    if isinstance(parity_runs, list):
        for item in parity_runs:
            if not isinstance(item, dict):
                continue
            run_dir = str(item.get("run_dir", "")).strip()
            run_id = Path(run_dir).name if run_dir else ""
            if run_id:
                parity_by_run_id[run_id] = str(item.get("status", "empty")).strip() or "empty"
                promotion_state = str(item.get("promotion_state", "")).strip().lower()
                if promotion_state:
                    promotion_by_run_id[run_id] = promotion_state

    if runs_root.exists():
        for run_json in sorted(runs_root.glob("*/run.json")):
            run_obj = read_json(run_json, {})
            if not isinstance(run_obj, dict):
                continue
            run_id = str(run_obj.get("run_id", "")).strip() or run_json.parent.name
            row = ensure_row(run_id)
            apply_values(
                row,
                {
                    "run_id": run_id,
                    "profile_id": run_obj.get("profile_id"),
                    "scope_skill": run_obj.get("scope_skill"),
                    "terminal_status": run_obj.get("terminal_status"),
                    "stop_reason": run_obj.get("stop_reason"),
                    "iterations_completed": run_obj.get("iterations_completed"),
                    "quality_uplift": run_obj.get("quality_uplift"),
                    "critical_non_regression_passed": run_obj.get("critical_non_regression_passed"),
                    "capture_record_present": run_obj.get("capture_record_present"),
                    "confidence_bucket": run_obj.get("confidence_bucket"),
                    "injected_lesson_count": run_obj.get("injected_lesson_count"),
                    "finished_at": run_obj.get("finished_at"),
                },
                overwrite=False,
            )

    recent_runs = shadow_dashboard.get("recent_runs") if isinstance(shadow_dashboard, dict) else []
    if not isinstance(recent_runs, list):
        recent_runs = []
    for row in recent_runs:
        if not isinstance(row, dict):
            continue
        profile_id = str(row.get("profile_id", "")).strip()
        run_id = str(row.get("run_id", "")).strip() or "unknown"
        shadow_run_ids.add(run_id)
        run_entry = ensure_row(run_id)
        apply_values(
            run_entry,
            {
                "run_id": run_id,
                "profile_id": profile_id,
                "scope_skill": row.get("scope_skill"),
                "terminal_status": row.get("terminal_status"),
                "stop_reason": row.get("stop_reason"),
                "iterations_completed": row.get("iterations_completed"),
                "quality_uplift": row.get("quality_uplift"),
                "critical_non_regression_passed": row.get("critical_non_regression_passed"),
                "capture_record_present": row.get("capture_record_present"),
                "confidence_bucket": row.get("confidence_bucket"),
                "injected_lesson_count": row.get("injected_lesson_count"),
                "queue_reason": row.get("queue_reason"),
                "finished_at": row.get("finished_at"),
            },
            overwrite=True,
        )

    for run_id, row in row_by_run_id.items():
        profile_id = str(row.get("profile_id", "")).strip()
        scope_skill = str(row.get("scope_skill", "")).strip()
        node = resolve_node(profile_id, scope_skill)
        parity_status = parity_by_run_id.get(run_id, "empty")
        promotion_state = str(row.get("promotion_state", "")).strip().lower() or promotion_by_run_id.get(run_id, "")
        queue_reason = str(row.get("queue_reason", "")).strip() or queue_reason_by_run_id.get(run_id, "none")
        status = str(row.get("terminal_status", "unknown")).strip() or "unknown"
        stop_reason = str(row.get("stop_reason", "unknown")).strip() or "unknown"
        finished = str(row.get("finished_at", "")).strip()
        resolved_scope_skill = node.scope_skill if node else (scope_skill or profile_id or "unmapped")

        run_rows.append(
            {
                "run_id": run_id,
                "profile_id": profile_id or (node.profile_id if node else "unknown"),
                "scope_skill": resolved_scope_skill,
                "terminal_status": status,
                "stop_reason": stop_reason,
                "iterations_completed": row.get("iterations_completed"),
                "quality_uplift": row.get("quality_uplift"),
                "critical_non_regression_passed": row.get("critical_non_regression_passed"),
                "capture_record_present": row.get("capture_record_present"),
                "confidence_bucket": row.get("confidence_bucket"),
                "injected_lesson_count": row.get("injected_lesson_count"),
                "parity": parity_status,
                "promotion_state": promotion_state or "none",
                "queue_reason": queue_reason,
                "finished_at": finished,
            }
        )

        if not node:
            continue
        node.total_runs += 1
        if run_id in shadow_run_ids:
            node.pilot_window_runs += 1
            run_dt = parse_dt(finished) or datetime.min.replace(tzinfo=timezone.utc)
            node_dt = parse_dt(node.recent_run if node.recent_run not in {"n/a", ""} else "")
            if node.recent_run == "n/a" or not node_dt or run_dt >= node_dt:
                node.recent_status = status
                node.recent_stop_reason = stop_reason
                node.recent_run = run_id
                node.parity = parity_status
                node.queue_reason = queue_reason
            if queue_reason != "none":
                node.queue_count += 1

    # Non-pilot rows should stay neutral/no coverage unless run rows map to the node.
    for node in nodes:
        if node.pilot_window_runs == 0:
            node.recent_status = "no_recent_run_data"
            if node.parity == "empty":
                node.parity = "empty"

    # Promotion badges.
    return sorted(run_rows, key=lambda item: str(item.get("finished_at", "")), reverse=True)


def apply_promotion_badges(nodes: List[SkillNode], promotion_validation: Dict[str, Any], run_rows: List[Dict[str, Any]]) -> None:
    alias_map = build_node_alias_index(nodes)
    run_by_id = {str(row.get("run_id", "")).strip(): row for row in run_rows if str(row.get("run_id", "")).strip()}
    results = promotion_validation.get("results") if isinstance(promotion_validation, dict) else []
    if isinstance(results, list):
        for row in results:
            if not isinstance(row, dict):
                continue
            run_id = str(row.get("run_id", "")).strip()
            decision = str(row.get("decision", "")).strip().lower()
            if not decision:
                continue
            if run_id and run_id in run_by_id:
                run_by_id[run_id]["promotion_state"] = decision
                node = alias_map.get(str(run_by_id[run_id].get("scope_skill", "")).strip().lower())
                if node:
                    node.promotion = decision

    validated = promotion_validation.get("validated_runs") if isinstance(promotion_validation, dict) else []
    if isinstance(validated, list):
        for row in validated:
            if not isinstance(row, dict):
                continue
            profile_id = str(row.get("profile_id", "")).strip().lower()
            decision = str(row.get("decision", "")).strip().lower()
            if not profile_id or not decision:
                continue
            node = alias_map.get(profile_id)
            if node:
                node.promotion = decision

    for row in run_rows:
        promotion_state = str(row.get("promotion_state", "")).strip().lower()
        if not promotion_state or promotion_state == "none":
            continue
        node = alias_map.get(str(row.get("scope_skill", "")).strip().lower())
        if node and node.promotion in {"none", "candidate"}:
            node.promotion = promotion_state


def apply_candidates(nodes: List[SkillNode], candidates_rows: Iterable[Dict[str, Any]]) -> None:
    by_skill = {node.scope_skill: node for node in nodes}
    by_profile = {node.profile_id: node for node in nodes}
    for row in candidates_rows:
        if not isinstance(row, dict):
            continue
        scope_skill = str(row.get("scope_skill", "")).strip()
        profile_id = str(row.get("profile_id", "")).strip()
        node = by_skill.get(scope_skill) or by_profile.get(profile_id)
        if not node:
            continue
        node.promotion = "candidate" if node.promotion == "none" else node.promotion
        score = row.get("composite_score")
        try:
            node.candidate_pressure = max(node.candidate_pressure, float(score))
        except Exception:  # noqa: BLE001 — score may be None or non-numeric
            pass


def parse_queue_reasons(path: Path) -> Tuple[Dict[str, int], Dict[str, str]]:
    if not path.exists():
        return {}, {}
    counts: Dict[str, int] = {}
    by_run: Dict[str, str] = {}
    reason_re = re.compile(r"reason `([^`]+)`")
    run_re = re.compile(r"^- `(run_[^`]+)`")
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("- `run_"):
            continue
        run_match = run_re.search(line)
        run_id = run_match.group(1).strip() if run_match else ""
        m = reason_re.search(line)
        reason = (m.group(1) if m else "unknown").strip()
        counts[reason] = counts.get(reason, 0) + 1
        if run_id:
            by_run[run_id] = reason
    return counts, by_run


def summarize_promotion_counts(promotion_validation: Dict[str, Any], run_rows: List[Dict[str, Any]]) -> Dict[str, int]:
    if not isinstance(promotion_validation, dict):
        promotion_validation = {}
    decision_counts = promotion_validation.get("decision_counts")
    if isinstance(decision_counts, dict):
        return {
            "approved": int(decision_counts.get("approved", 0) or 0),
            "draft": int(decision_counts.get("draft", 0) or 0),
            "failed": int(decision_counts.get("failed", 0) or 0),
        }

    direct_keys = ("approved", "draft", "failed")
    if all(key in promotion_validation for key in direct_keys):
        return {
            "approved": int(promotion_validation.get("approved", 0) or 0),
            "draft": int(promotion_validation.get("draft", 0) or 0),
            "failed": int(promotion_validation.get("failed", 0) or 0),
        }

    summary = {"approved": 0, "draft": 0, "failed": 0}
    for row in run_rows:
        state = str(row.get("promotion_state", "")).strip().lower()
        if state in summary:
            summary[state] += 1
        elif state in {"rejected", "error"}:
            summary["failed"] += 1
    return summary


def render_html(
    *,
    generated_at: str,
    controls: Dict[str, Any],
    readiness_summary: Dict[str, Any],
    wave_status: Dict[str, Any],
    shadow_dashboard: Dict[str, Any],
    daily_health: Dict[str, Any],
    promotion_validation: Dict[str, Any],
    nodes: List[SkillNode],
    run_rows: List[Dict[str, Any]],
    queue_reason_counts: Dict[str, int],
    candidates_rows: List[Dict[str, Any]],
    artifact_rows: List[Tuple[str, str, str, str]],
) -> str:
    cluster_cards: Dict[str, List[str]] = {}
    cluster_slice: Dict[str, str] = {}
    cluster_counts: Dict[str, int] = {}
    for node in nodes:
        mode_cls = normalize_class_token(f"mode-{node.delegation_mode}")
        halo_cls = normalize_class_token(f"halo-{node.recent_status}")
        parity_cls = normalize_class_token(f"parity-{node.parity}")
        badge_cls = normalize_class_token(f"badge-{node.promotion}")
        slice_cls = normalize_class_token(f"slice-{node.display_slice}")
        wave_cls = "wave-ready" if node.wave_ready else "wave-blocked"
        size_px = 18 + int(min(10, round(node.candidate_pressure * 10)))
        cluster = node.scope_profile or "unknown"
        cluster_counts[cluster] = cluster_counts.get(cluster, 0) + 1
        cluster_slice[cluster] = node.display_slice
        cluster_cards.setdefault(cluster, []).append(
            f"""
<article class="skill-node {mode_cls} {halo_cls} {parity_cls} {badge_cls} {slice_cls}" style="--node-size:{size_px}px">
  <div class="glyph">
    <span class="halo"></span>
    <span class="core"></span>
    <span class="corner"></span>
    <span class="badge">{esc((node.promotion or "none")[:1].upper())}</span>
  </div>
  <h4>{esc(node.scope_skill)}</h4>
  <p class="muted">{esc(node.profile_id)} | {esc(node.scope_profile)}</p>
  <p class="chips"><span class="chip {wave_cls}">{esc(node.wave)}</span> <span class="chip">{esc(node.delegation_mode)}</span> <span class="chip">{esc(node.parity)}</span></p>
  <p class="muted small">recent: {esc(node.recent_status)} ({esc(node.recent_run)})</p>
</article>
"""
        )
    cluster_sections: List[str] = []
    for cluster in sorted(cluster_cards):
        section_slice_cls = normalize_class_token(f"slice-{cluster_slice.get(cluster, 'extended')}")
        cluster_sections.append(
            f"""
<article class="card cluster-card {section_slice_cls}">
  <h3>{esc(cluster)}</h3>
  <p class="muted small">skills={cluster_counts.get(cluster, 0)}</p>
  <div class="skill-grid">{''.join(cluster_cards[cluster])}</div>
</article>
"""
        )

    run_rows_html: List[str] = []
    for row in run_rows:
        run_rows_html.append(
            "<tr>"
            f"<td><code>{esc(row.get('run_id'))}</code></td>"
            f"<td>{esc(row.get('profile_id'))}</td>"
            f"<td>{esc(row.get('scope_skill'))}</td>"
            f"<td>{esc(row.get('terminal_status'))}</td>"
            f"<td>{esc(row.get('stop_reason'))}</td>"
            f"<td>{esc(row.get('iterations_completed'))}</td>"
            f"<td>{esc(row.get('quality_uplift'))}</td>"
            f"<td>{esc(row.get('critical_non_regression_passed'))}</td>"
            f"<td>{esc(row.get('capture_record_present'))}</td>"
            f"<td>{esc(row.get('confidence_bucket'))}</td>"
            f"<td>{esc(row.get('injected_lesson_count'))}</td>"
            f"<td>{esc(row.get('parity'))}</td>"
            f"<td>{esc(row.get('promotion_state', 'none'))}</td>"
            f"<td>{esc(row.get('queue_reason'))}</td>"
            f"<td>{esc(row.get('finished_at'))}</td>"
            "</tr>"
        )
    if not run_rows_html:
        run_rows_html.append("<tr><td colspan='15' class='muted'>No run rows found.</td></tr>")

    cand_rows_html: List[str] = []
    for row in candidates_rows[:40]:
        cand_rows_html.append(
            "<tr>"
            f"<td>{esc(row.get('candidate_id', 'n/a'))}</td>"
            f"<td>{esc(row.get('scope_skill', row.get('profile_id', 'n/a')))}</td>"
            f"<td>{esc(row.get('composite_score', 'n/a'))}</td>"
            f"<td>{esc(row.get('window_count', 'n/a'))}</td>"
            f"<td>{esc(row.get('decision_reason', 'n/a'))}</td>"
            "</tr>"
        )
    if not cand_rows_html:
        cand_rows_html.append("<tr><td colspan='5' class='muted'>No candidates.jsonl rows found.</td></tr>")

    queue_items = "".join(
        f"<li><code>{esc(reason)}</code>: <strong>{count}</strong></li>"
        for reason, count in sorted(queue_reason_counts.items(), key=lambda item: (-item[1], item[0]))
    ) or "<li class='muted'>No queue reasons found.</li>"

    artifact_rows_html = "".join(
        f"<tr><td>{esc(name)}</td><td><code>{esc(path)}</code></td><td>{esc(generated_at)}</td><td>{esc(mtime)}</td></tr>"
        for name, path, generated_at, mtime in artifact_rows
    )

    shadow_decision = (
        str(shadow_dashboard.get("decision", {}).get("state", "unknown"))
        if isinstance(shadow_dashboard.get("decision"), dict)
        else "unknown"
    )
    promotion_counts = summarize_promotion_counts(promotion_validation, run_rows)
    approved = promotion_counts.get("approved", 0)
    draft = promotion_counts.get("draft", 0)
    failed = promotion_counts.get("failed", 0)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Recursive Skill Graph State Map</title>
  <style>
    :root {{
      --bg:#071522; --panel:#10273c; --border:#2b5272; --text:#e9f3ff; --muted:#a9c4dd;
      --ok:#31c48d; --warn:#f6c24d; --bad:#ff8277; --info:#69abff; --neutral:#8da6c4;
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:"Avenir Next","Segoe UI",sans-serif; background:linear-gradient(180deg,#0a1f33,#071522); color:var(--text); }}
    .wrap {{ max-width:1800px; margin:0 auto; padding:20px; }}
    .panel {{ background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:14px; margin-top:14px; }}
    .grid4 {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; }}
    .grid2 {{ display:grid; grid-template-columns:2fr 1fr; gap:14px; }}
    .toolbar {{ display:flex; gap:8px; margin-bottom:10px; flex-wrap:wrap; }}
    .toggle-btn {{ border:1px solid var(--border); background:#17314a; color:var(--text); border-radius:999px; padding:5px 10px; cursor:pointer; font-size:0.78rem; }}
    .toggle-btn.active {{ border-color:var(--ok); }}
    .card {{ background:rgba(255,255,255,0.03); border:1px solid var(--border); border-radius:10px; padding:10px; }}
    .muted {{ color:var(--muted); }}
    .small {{ font-size:0.75rem; }}
    .clusters {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(310px,1fr)); gap:10px; }}
    .clusters.mode-core .slice-extended,.clusters.mode-core .slice-system {{ display:none; }}
    .clusters.mode-full .slice-system {{ display:none; }}
    .skill-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(210px,1fr)); gap:8px; }}
    .skill-node {{ border:1px solid var(--border); border-radius:10px; padding:8px; background:#0c2032; }}
    .skill-node h4 {{ margin:2px 0 4px; font-size:0.84rem; word-break:break-word; }}
    .glyph {{ position:relative; width:34px; height:34px; margin-bottom:6px; }}
    .halo,.core,.corner,.badge {{ position:absolute; display:inline-flex; align-items:center; justify-content:center; border:1px solid var(--border); }}
    .halo {{ inset:0; border-radius:999px; }}
    .core {{ width:var(--node-size,20px); height:var(--node-size,20px); max-width:24px; max-height:24px; left:50%; top:50%; transform:translate(-50%,-50%); border-radius:999px; background:rgba(141,166,196,0.28); }}
    .corner {{ right:-1px; top:-1px; width:11px; height:11px; border-radius:0 9px 0 9px; }}
    .badge {{ right:-6px; bottom:-6px; width:16px; height:16px; border-radius:999px; font-size:0.58rem; font-weight:700; }}
    .chips {{ display:flex; flex-wrap:wrap; gap:4px; margin:4px 0; }}
    .chip {{ border:1px solid var(--border); border-radius:999px; padding:1px 6px; font-size:0.63rem; }}
    .wave-ready {{ border-color:var(--ok); }}
    .wave-blocked {{ border-color:var(--bad); }}
    .mode-manual .core {{ background:rgba(246,194,77,0.25); }}
    .mode-co-pilot .core {{ background:rgba(105,171,255,0.25); }}
    .mode-autopilot .core {{ background:rgba(49,196,141,0.25); }}
    .halo-passed .halo {{ border-color:var(--ok); }}
    .halo-failed .halo,.halo-escalated .halo,.halo-aborted .halo {{ border-color:var(--bad); }}
    .halo-no_recent_run_data .halo {{ border-color:var(--neutral); }}
    .parity-compliant .corner {{ background:rgba(49,196,141,0.35); }}
    .parity-missing_mandatory .corner {{ background:rgba(255,130,119,0.35); }}
    .parity-legacy_partial .corner {{ background:rgba(246,194,77,0.35); }}
    .parity-empty .corner {{ background:rgba(141,166,196,0.35); }}
    .badge-approved .badge {{ border-color:var(--ok); }}
    .badge-draft .badge {{ border-color:var(--info); }}
    .badge-candidate .badge {{ border-color:var(--warn); }}
    .badge-rejected .badge {{ border-color:var(--bad); }}
    table {{ width:100%; border-collapse:collapse; font-size:0.8rem; }}
    th,td {{ border-bottom:1px solid var(--border); text-align:left; padding:7px; vertical-align:top; }}
    code {{ background:rgba(255,255,255,0.08); border-radius:4px; padding:1px 4px; }}
    @media (max-width:1200px) {{ .grid4 {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} .grid2 {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Recursive Skill Graph State Map</h1>
    <p class="muted">Generated at {esc(generated_at)}. This view intentionally separates readiness, controls, run/compliance, and learning/change lanes.</p>

    <section class="panel">
      <h2>1) Global program strip</h2>
      <div class="grid4">
        <article class="card">
          <h3>Controls</h3>
          <ul>
            <li>rollout-mode: <strong>{esc(controls.get("rollout_mode", "unknown"))}</strong> (raw: <code>{esc(controls.get("rollout_raw", ""))}</code>)</li>
            <li>kill-switch: <strong>{esc(controls.get("kill_switch", "unknown"))}</strong> (raw: <code>{esc(controls.get("kill_raw", ""))}</code>)</li>
            <li>rollback-required: <strong>{esc(controls.get("rollback_required", "unknown"))}</strong> (raw: <code>{esc(controls.get("rollback_raw", ""))}</code>)</li>
          </ul>
        </article>
        <article class="card">
          <h3>Readiness</h3>
          <ul>
            <li>wave-0-controls: <strong>{esc("ready" if wave_status.get("wave-0-controls", False) else "blocked")}</strong></li>
            <li>wave-1-manual: <strong>{esc("ready" if wave_status.get("wave-1-manual", False) else "blocked")}</strong></li>
            <li>wave-2-co-pilot: <strong>{esc("ready" if wave_status.get("wave-2-co-pilot", False) else "blocked")}</strong></li>
          </ul>
          <p class="muted">active={esc(readiness_summary.get("active_skill_count"))}, manual={esc(readiness_summary.get("manual_skill_count"))}, co-pilot={esc(readiness_summary.get("co_pilot_skill_count"))}, valid={esc(readiness_summary.get("profile_valid_count"))}, invalid={esc(readiness_summary.get("profile_invalid_count"))}</p>
        </article>
        <article class="card">
          <h3>Operational health</h3>
          <ul>
            <li>shadow decision: <strong>{esc(shadow_decision)}</strong></li>
            <li>daily-health decision: <strong>{esc(daily_health.get("decision", "unknown"))}</strong></li>
            <li>window: <code>{esc(daily_health.get("window", "unknown"))}</code></li>
          </ul>
        </article>
        <article class="card">
          <h3>Promotion</h3>
          <ul>
            <li>status: <strong>{esc(promotion_validation.get("status", "unknown"))}</strong></li>
            <li>approved: <strong>{esc(approved)}</strong></li>
            <li>draft: <strong>{esc(draft)}</strong></li>
            <li>failed: <strong>{esc(failed)}</strong></li>
          </ul>
        </article>
      </div>
      <details>
        <summary>Artifact timestamps</summary>
        <table>
          <thead><tr><th>artifact</th><th>path</th><th>generated_at</th><th>mtime (UTC)</th></tr></thead>
          <tbody>{artifact_rows_html}</tbody>
        </table>
      </details>
    </section>

    <section class="panel">
      <h2>2) Skill state map</h2>
      <div class="toolbar">
        <button id="view-core" class="toggle-btn active" type="button">Core View (70)</button>
        <button id="view-full" class="toggle-btn" type="button">Full View (114)</button>
      </div>
      <div id="skill-clusters" class="clusters mode-core">
        {''.join(cluster_sections)}
      </div>
    </section>

    <section class="panel">
      <h2>3) Run / compliance lane</h2>
      <table>
        <thead>
          <tr>
            <th>run_id</th><th>profile_id</th><th>scope_skill</th><th>terminal_status</th><th>stop_reason</th>
            <th>iterations</th><th>quality_uplift</th><th>non_regression</th><th>capture</th><th>confidence</th>
            <th>injected</th><th>parity</th><th>promotion</th><th>queue_reason</th><th>finished_at</th>
          </tr>
        </thead>
        <tbody>{''.join(run_rows_html)}</tbody>
      </table>
    </section>

    <section class="panel">
      <h2>4) Learning / change lane</h2>
      <div class="grid2">
        <article class="card">
          <h3>Candidate pressure</h3>
          <table>
            <thead><tr><th>candidate_id</th><th>skill</th><th>composite_score</th><th>window_count</th><th>decision_reason</th></tr></thead>
            <tbody>{''.join(cand_rows_html)}</tbody>
          </table>
        </article>
        <article class="card">
          <h3>Queue bottlenecks</h3>
          <ul>{queue_items}</ul>
          <p class="muted small">source-state semantics: missing vs empty vs present are preserved by source existence checks.</p>
        </article>
      </div>
    </section>
  </div>
  <script>
    (() => {{
      const clusters = document.getElementById("skill-clusters");
      const coreBtn = document.getElementById("view-core");
      const fullBtn = document.getElementById("view-full");
      if (!clusters || !coreBtn || !fullBtn) return;
      function setMode(mode) {{
        clusters.classList.remove("mode-core", "mode-full");
        clusters.classList.add(mode === "full" ? "mode-full" : "mode-core");
        coreBtn.classList.toggle("active", mode !== "full");
        fullBtn.classList.toggle("active", mode === "full");
      }}
      coreBtn.addEventListener("click", () => setMode("core"));
      fullBtn.addEventListener("click", () => setMode("full"));
      setMode("core");
    }})();
  </script>
</body>
</html>
"""


def graph_adapter_guarded_dir(repo_root: Path, graph_adapter_dir: Path) -> Path:
    allowed = (repo_root / DEFAULT_GRAPH_ADAPTER_DIR).resolve()
    target = graph_adapter_dir.resolve()
    if target != allowed and allowed not in target.parents:
        raise RuntimeError(f"graph-adapter path must be under {allowed}; got {target}")
    return target


def clear_graph_adapter_notes(notes_dir: Path) -> None:
    notes_dir.mkdir(parents=True, exist_ok=True)
    prefixes = ("skill--", "profile--", "wave--", "run--", "decision--", "candidate--")
    for prefix in prefixes:
        for note in notes_dir.glob(f"{prefix}*.md"):
            note.unlink(missing_ok=True)


def maybe_write_graph_adapter(
    *,
    repo_root: Path,
    graph_adapter_dir: Path,
    nodes: List[SkillNode],
    run_rows: List[Dict[str, Any]],
    candidates_rows: List[Dict[str, Any]],
) -> Tuple[int, int]:
    safe_dir = graph_adapter_guarded_dir(repo_root, graph_adapter_dir)
    notes_dir = safe_dir / "notes"
    clear_graph_adapter_notes(notes_dir)
    edges: List[Dict[str, str]] = []
    count = 0

    for node in nodes:
        fname = f"skill--{normalize_class_token(node.scope_skill)}.md"
        links = [f"[[profile--{normalize_class_token(node.profile_id)}]]", f"[[wave--{normalize_class_token(node.wave)}]]"]
        text = "\n".join(
            [
                "---",
                f"title: skill--{node.scope_skill}",
                "---",
                "",
                f"- scope_skill: `{node.scope_skill}`",
                f"- delegation_mode: `{node.delegation_mode}`",
                f"- parity: `{node.parity}`",
                "",
                "## Links",
                *[f"- {link}" for link in links],
                "",
            ]
        )
        (notes_dir / fname).write_text(text, encoding="utf-8")
        count += 1
        for link in links:
            target = link.strip("[]")
            edges.append({"source": f"skill--{node.scope_skill}", "target": target, "type": "declared"})

    for run in run_rows:
        run_id = str(run.get("run_id", "")).strip()
        if not run_id:
            continue
        fname = f"run--{normalize_class_token(run_id)}.md"
        skill = str(run.get("scope_skill", "")).strip()
        links = [f"[[skill--{normalize_class_token(skill)}]]"] if skill else []
        (notes_dir / fname).write_text(
            "\n".join(
                [
                    "---",
                    f"title: run--{run_id}",
                    "---",
                    "",
                    f"- terminal_status: `{run.get('terminal_status', 'unknown')}`",
                    f"- stop_reason: `{run.get('stop_reason', 'unknown')}`",
                    "",
                    "## Links",
                    *[f"- {link}" for link in links],
                    "",
                ]
            ),
            encoding="utf-8",
        )
        count += 1

    for row in candidates_rows:
        cid = str(row.get("candidate_id", "")).strip()
        if not cid:
            continue
        fname = f"candidate--{normalize_class_token(cid)}.md"
        scope_skill = str(row.get("scope_skill", "")).strip()
        link = f"[[skill--{normalize_class_token(scope_skill)}]]" if scope_skill else ""
        (notes_dir / fname).write_text(
            "\n".join(
                [
                    "---",
                    f"title: candidate--{cid}",
                    "---",
                    "",
                    f"- composite_score: `{row.get('composite_score', 'n/a')}`",
                    f"- decision_reason: `{row.get('decision_reason', 'n/a')}`",
                    "",
                    "## Links",
                    f"- {link}" if link else "- n/a",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        count += 1

    typed_graph = {"generated_at": now_iso(), "nodes": count, "edges": edges}
    (safe_dir / "typed-graph.json").write_text(json.dumps(typed_graph, indent=2) + "\n", encoding="utf-8")
    return count, len(edges)


def artifact_generated_at(payload: Any) -> str:
    if isinstance(payload, dict):
        value = payload.get("generated_at")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "unknown"


def mtime_iso(path: Path) -> str:
    if not path.exists():
        return "missing"
    ts = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return ts.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_html = (repo_root / args.out_html).resolve()
    controls_dir = (repo_root / args.controls_dir).resolve()
    wave_readiness_path = (repo_root / args.wave_readiness).resolve()
    profile_index_path = (repo_root / args.profile_index).resolve()
    inventory_policy_path = (repo_root / args.inventory_policy).resolve()
    shadow_dashboard_path = (repo_root / args.shadow_dashboard).resolve()
    daily_health_path = (repo_root / args.daily_health_md).resolve()
    promotion_queue_path = (repo_root / args.promotion_queue_md).resolve()
    promotion_validation_path = (repo_root / args.promotion_validation).resolve()
    parity_manifest_path = (repo_root / args.parity_manifest).resolve()
    candidates_path = (repo_root / args.candidates_jsonl).resolve()
    runs_root = (repo_root / args.runs_root).resolve()
    graph_adapter_dir = (repo_root / args.graph_adapter_dir).resolve()

    enforce_daily_health_contract(repo_root, daily_health_path)
    inventory_policy = load_inventory_policy(repo_root, inventory_policy_path, args.system_slice_mode)
    profile_index = read_json(profile_index_path, {})
    wave_readiness = read_json(wave_readiness_path, {})
    shadow_dashboard = read_json(shadow_dashboard_path, {})
    parity_manifest = read_json(parity_manifest_path, {})
    promotion_validation = read_json(promotion_validation_path, {})
    candidates_rows = read_jsonl(candidates_path)

    controls = {}
    rollout_raw = (controls_dir / "rollout-mode.txt").read_text(encoding="utf-8").strip() if (controls_dir / "rollout-mode.txt").exists() else ""
    kill_raw = (controls_dir / "kill-switch.txt").read_text(encoding="utf-8").strip() if (controls_dir / "kill-switch.txt").exists() else ""
    rollback_raw = (controls_dir / "rollback-required.txt").read_text(encoding="utf-8").strip() if (controls_dir / "rollback-required.txt").exists() else ""
    controls["rollout_raw"] = rollout_raw
    controls["kill_raw"] = kill_raw
    controls["rollback_raw"] = rollback_raw
    controls["rollout_mode"] = rollout_raw or "off"
    controls["kill_switch"] = "active" if parse_control_state(kill_raw) else "inactive"
    controls["rollback_required"] = "active" if parse_control_state(rollback_raw) else "inactive"

    queue_reason_counts, queue_reason_by_run = parse_queue_reasons(promotion_queue_path)
    nodes = discover_nodes(repo_root, profile_index, wave_readiness, inventory_policy)
    run_rows = apply_shadow_runs(nodes, shadow_dashboard, parity_manifest, runs_root, queue_reason_by_run)
    apply_promotion_badges(nodes, promotion_validation, run_rows)
    apply_candidates(nodes, candidates_rows)
    daily_health = parse_daily_health(daily_health_path)

    readiness_summary = wave_readiness.get("summary", {}) if isinstance(wave_readiness, dict) else {}
    wave_status = {}
    waves = wave_readiness.get("waves") if isinstance(wave_readiness, dict) else {}
    if isinstance(waves, dict):
        for key, payload in waves.items():
            if isinstance(payload, dict):
                wave_status[key] = bool(payload.get("ready"))

    artifact_rows = [
        ("profile-index", str(profile_index_path.relative_to(repo_root)), artifact_generated_at(profile_index), mtime_iso(profile_index_path)),
        ("wave-readiness", str(wave_readiness_path.relative_to(repo_root)), artifact_generated_at(wave_readiness), mtime_iso(wave_readiness_path)),
        ("shadow-dashboard", str(shadow_dashboard_path.relative_to(repo_root)), artifact_generated_at(shadow_dashboard), mtime_iso(shadow_dashboard_path)),
        ("daily-health", str(daily_health_path.relative_to(repo_root)), daily_health.get("generated_at", "inline-only"), mtime_iso(daily_health_path)),
        ("promotion-validation", str(promotion_validation_path.relative_to(repo_root)), artifact_generated_at(promotion_validation), mtime_iso(promotion_validation_path)),
        ("parity-manifest", str(parity_manifest_path.relative_to(repo_root)), artifact_generated_at(parity_manifest), mtime_iso(parity_manifest_path)),
        ("inventory-policy", str(inventory_policy_path.relative_to(repo_root)), "n/a", mtime_iso(inventory_policy_path)),
    ]

    html = render_html(
        generated_at=now_iso(),
        controls=controls,
        readiness_summary=readiness_summary if isinstance(readiness_summary, dict) else {},
        wave_status=wave_status,
        shadow_dashboard=shadow_dashboard if isinstance(shadow_dashboard, dict) else {},
        daily_health=daily_health,
        promotion_validation=promotion_validation if isinstance(promotion_validation, dict) else {},
        nodes=nodes,
        run_rows=run_rows,
        queue_reason_counts=queue_reason_counts,
        candidates_rows=candidates_rows,
        artifact_rows=artifact_rows,
    )

    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(html, encoding="utf-8")

    graph_nodes = 0
    graph_edges = 0
    if args.with_graph_adapter:
        graph_nodes, graph_edges = maybe_write_graph_adapter(
            repo_root=repo_root,
            graph_adapter_dir=graph_adapter_dir,
            nodes=nodes,
            run_rows=run_rows,
            candidates_rows=candidates_rows,
        )
    shadow_recent_count = len(shadow_dashboard.get("recent_runs", [])) if isinstance(shadow_dashboard, dict) and isinstance(shadow_dashboard.get("recent_runs"), list) else 0

    print(
        json.dumps(
            {
                "out_html": str(out_html.relative_to(repo_root)),
                "skills": len(nodes),
                "clusters": len(sorted({node.scope_profile for node in nodes})),
                "runs": len(run_rows),
                "shadow_runs": shadow_recent_count,
                "candidate_rows": len(candidates_rows),
                "graph_adapter_files": graph_nodes,
                "typed_graph_nodes": graph_nodes,
                "typed_graph_edges": graph_edges,
                "health_decision": daily_health.get("decision", "unknown"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
