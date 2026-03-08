#!/usr/bin/env python3
"""Build a single HTML skill state map from existing recursive-skill artifacts.

This renderer keeps readiness, controls, operational health, run/compliance,
and learning/change signals separated into four linked views:
  1) Global program strip
  2) Skill state map
  3) Run/compliance lane
  4) Learning/change lane
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

FALSY_CONTROL_VALUES = {"off", "false", "0", "no", "inactive"}
ROLLOUT_MODES = {"off", "observe_only", "active"}
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
CLASS_TOKEN_PATTERN = re.compile(r"[^a-z0-9_-]+")
GRAPH_ADAPTER_ALLOWED_REL = Path("artifacts/skill-graphs/graph-adapter")
GRAPH_ADAPTER_FILE_PREFIXES = (
    "skill--",
    "profile--",
    "wave--",
    "run--",
    "decision--",
    "candidate--",
    "blocker--",
)
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


@dataclass
class ArtifactMeta:
    label: str
    path: Path
    exists: bool
    generated_at: Optional[str]
    file_mtime: Optional[str]


@dataclass
class SkillProfile:
    scope_skill: str
    profile_id: str
    scope_profile: str
    delegation_mode: str
    thresholds: Dict[str, Any]
    criteria: List[Dict[str, Any]]
    wave: str
    wave_ready: bool
    profile_path: str
    profile_present: bool


@dataclass
class RunEntry:
    run_id: str
    profile_id: Optional[str] = None
    scope_skill: Optional[str] = None
    terminal_status: Optional[str] = None
    stop_reason: Optional[str] = None
    iterations_completed: Optional[int] = None
    quality_uplift: Optional[float] = None
    critical_non_regression_passed: Optional[bool] = None
    capture_record_present: Optional[bool] = None
    confidence_bucket: Optional[str] = None
    injected_lesson_count: Optional[int] = None
    parity_status: Optional[str] = None
    promotion_state: Optional[str] = None
    finished_at: Optional[str] = None
    queue_reason: Optional[str] = None
    source_shadow: bool = False
    source_manifest: bool = False
    source_run_dir: bool = False
    skill_key: Optional[str] = None


@dataclass
class CandidateRow:
    candidate_id: str
    skill_raw: str
    skill_key: Optional[str]
    composite_score: float
    window_count: int
    decision_reason: str
    created_at: Optional[str]


@dataclass
class SkillNodeState:
    skill: SkillProfile
    recent_halo: str
    recent_run: Optional[RunEntry]
    promotion_badge: str
    parity_corner: str
    candidate_pressure: float
    centrality_score: float
    node_size_px: int
    recent_run_count: int
    total_run_count: int
    queue_count: int
    top_queue_reason: str
    blockers: List[str]
    blocker_severity: str


@dataclass(frozen=True)
class InventoryPolicy:
    include_prefixes: Tuple[str, ...]
    exclude_prefixes: Tuple[str, ...]
    system_prefixes: Tuple[str, ...]
    system_slice_mode: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--out-html",
        default="artifacts/skill-graphs/telemetry/skill-state-map.html",
        help="Output HTML path",
    )
    parser.add_argument(
        "--controls-dir",
        default="artifacts/skill-graphs/controls",
        help="Control files directory",
    )
    parser.add_argument(
        "--wave-readiness",
        default="artifacts/skill-graphs/onboarding/wave-readiness.json",
    )
    parser.add_argument(
        "--profile-index",
        default="artifacts/skill-graphs/onboarding/profile-index.json",
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
    parser.add_argument(
        "--shadow-dashboard",
        default="artifacts/skill-graphs/pilot/shadow-dashboard.json",
    )
    parser.add_argument(
        "--daily-health-md",
        default="docs/skill-graphs/telemetry/daily-skill-health.md",
    )
    parser.add_argument(
        "--promotion-queue-md",
        default="artifacts/skill-graphs/telemetry/promotion-queue.md",
    )
    parser.add_argument(
        "--promotion-validation",
        default="artifacts/skill-graphs/pilot/promotion-validation-report.json",
    )
    parser.add_argument(
        "--parity-manifest",
        default="artifacts/skill-graphs/pilot/artifact-parity-manifest.json",
    )
    parser.add_argument(
        "--candidates-jsonl",
        default="artifacts/skill-graphs/telemetry/candidates.jsonl",
    )
    parser.add_argument(
        "--runs-root",
        default="artifacts/skill-graphs/runs",
    )
    parser.add_argument(
        "--feedback-log",
        default="ops/metrics/skill-feedback/decision-feedback.jsonl",
    )
    parser.add_argument(
        "--graph-adapter-dir",
        default="artifacts/skill-graphs/graph-adapter/notes",
    )
    parser.add_argument(
        "--with-graph-adapter",
        action="store_true",
        help="Generate optional wiki-link adapter projection for Ars Contexta overlays",
    )
    return parser.parse_args()


def _utc_iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _path(repo_root: Path, raw: str) -> Path:
    p = Path(raw).expanduser()
    if p.is_absolute():
        return p.resolve()
    return (repo_root / p).resolve()


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return obj if isinstance(obj, dict) else None


def load_required_json(path: Path, label: str) -> Dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing required {label} artifact: {path}")
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in required {label} artifact: {path}") from exc
    if not isinstance(obj, dict):
        raise RuntimeError(f"Required {label} artifact must be a JSON object: {path}")
    return obj


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            row = json.loads(raw)
        except Exception:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def try_parse_ts(value: Any) -> Optional[datetime]:
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    text = text.replace(" ", "T")
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def fmt_ts(value: Any) -> str:
    parsed = try_parse_ts(value)
    if parsed is None:
        return "n/a"
    return parsed.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fmt_num(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def artifact_meta(label: str, path: Path, payload: Optional[Dict[str, Any]]) -> ArtifactMeta:
    exists = path.exists()
    generated_at: Optional[str] = None
    if isinstance(payload, dict):
        raw_generated = payload.get("generated_at")
        if isinstance(raw_generated, str) and raw_generated.strip():
            generated_at = fmt_ts(raw_generated)
    mtime = None
    if exists:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).replace(
            microsecond=0
        ).isoformat().replace("+00:00", "Z")
    return ArtifactMeta(label=label, path=path, exists=exists, generated_at=generated_at, file_mtime=mtime)


def read_rollout_mode(path: Path, default: str = "observe_only") -> Tuple[str, str, bool]:
    if not path.exists():
        return default, "<missing>", False
    raw = path.read_text(encoding="utf-8").strip()
    mode = raw.lower()
    if mode not in ROLLOUT_MODES:
        mode = default
    return mode, (raw or "<blank>"), True


def read_fail_closed_switch(path: Path) -> Tuple[bool, str, bool]:
    if not path.exists():
        return False, "<missing>", False
    raw = path.read_text(encoding="utf-8").strip()
    active = raw.lower() not in FALSY_CONTROL_VALUES
    return active, (raw or "<blank>"), True


def parse_daily_health(path: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        if line.startswith("- Decision:"):
            m = re.search(r"`([^`]+)`", line)
            if m:
                out["decision"] = m.group(1)
        elif line.startswith("- Window:"):
            m = re.search(r"`([^`]+)`", line)
            if m:
                out["window"] = m.group(1)
        elif line.startswith("- Generated at:"):
            m = re.search(r"`([^`]+)`", line)
            if m:
                out["generated_at"] = m.group(1)
    return out


def parse_promotion_queue(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    rows: List[Dict[str, str]] = []
    pattern = re.compile(
        r"^- `(?P<run_id>[^`]+)` \| profile `(?P<profile>[^`]+)`(?:.*\| reason `(?P<reason>[^`]+)`)?"
    )
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("- `"):
            continue
        m = pattern.match(line)
        if not m:
            continue
        rows.append(
            {
                "run_id": m.group("run_id"),
                "profile": m.group("profile"),
                "reason": m.group("reason") or "unknown",
                "raw": line,
            }
        )
    return rows


def parse_feedback(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {
            "exists": False,
            "events": 0,
            "decision_counts": {},
            "outcome_counts": {},
            "latest_recorded_at": None,
        }

    rows = load_jsonl(path)
    decision_counts: Counter[str] = Counter()
    outcome_counts: Counter[str] = Counter()
    latest_ts: Optional[datetime] = None
    for row in rows:
        decision_counts[str(row.get("decision", "unknown"))] += 1
        outcome_counts[str(row.get("outcome", "unknown"))] += 1
        candidate_ts = try_parse_ts(row.get("recorded_at"))
        if candidate_ts is not None and (latest_ts is None or candidate_ts > latest_ts):
            latest_ts = candidate_ts

    return {
        "exists": True,
        "events": len(rows),
        "decision_counts": dict(sorted(decision_counts.items())),
        "outcome_counts": dict(sorted(outcome_counts.items())),
        "latest_recorded_at": latest_ts.replace(microsecond=0).isoformat().replace("+00:00", "Z")
        if latest_ts
        else None,
    }


def classify_source_state(path: Path, signal_count: int) -> str:
    if not path.exists():
        return "missing"
    if signal_count > 0:
        return "present"
    return "empty"


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


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


def load_inventory_policy(
    repo_root: Path,
    profile_index: Dict[str, Any],
    raw_path: str,
    system_slice_mode: Optional[str],
) -> InventoryPolicy:
    include_prefixes: Tuple[str, ...] = tuple()
    exclude_prefixes: Tuple[str, ...] = tuple()
    system_prefixes: Tuple[str, ...] = tuple()
    configured_mode = "separate"

    embedded = profile_index.get("inventory_policy")
    if isinstance(embedded, dict):
        include_prefixes = _normalize_prefixes(
            embedded.get("include_prefixes", DEFAULT_INCLUDE_PREFIXES)
        )
        exclude_prefixes = _normalize_prefixes(
            embedded.get("exclude_prefixes", DEFAULT_EXCLUDE_PREFIXES)
        )
        system_prefixes = _normalize_prefixes(
            embedded.get("system_prefixes", DEFAULT_SYSTEM_PREFIXES)
        )
        configured_mode = str(embedded.get("system_slice_mode", "separate")).strip().lower()
    else:
        path = _path(repo_root, raw_path)
        if path.exists():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Invalid inventory policy JSON: {path}") from exc
            if not isinstance(payload, dict):
                raise RuntimeError(f"Inventory policy must be a JSON object: {path}")
            include_prefixes = _normalize_prefixes(
                payload.get("include_prefixes", DEFAULT_INCLUDE_PREFIXES)
            )
            exclude_prefixes = _normalize_prefixes(
                payload.get("exclude_prefixes", DEFAULT_EXCLUDE_PREFIXES)
            )
            system_prefixes = _normalize_prefixes(
                payload.get("system_prefixes", DEFAULT_SYSTEM_PREFIXES)
            )
            configured_mode = str(payload.get("system_slice_mode", "separate")).strip().lower()
        else:
            include_prefixes = _normalize_prefixes(DEFAULT_INCLUDE_PREFIXES)
            exclude_prefixes = _normalize_prefixes(DEFAULT_EXCLUDE_PREFIXES)
            system_prefixes = _normalize_prefixes(DEFAULT_SYSTEM_PREFIXES)

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


def normalize_class_token(value: Any, fallback: str = "unknown") -> str:
    token = CLASS_TOKEN_PATTERN.sub("_", str(value).strip().lower()).strip("_")
    if not token:
        return fallback
    if not re.fullmatch(r"[a-z0-9_-]+", token):
        return fallback
    return token


def canonical_profile_inventory(
    profile_index: Dict[str, Any],
    inventory_policy: InventoryPolicy,
) -> Tuple[List[str], Dict[str, Dict[str, Any]]]:
    rows = profile_index.get("skills") if isinstance(profile_index.get("skills"), list) else []
    if not rows:
        raise RuntimeError("profile-index.json is missing a non-empty skills[] inventory.")

    by_scope: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        scope_skill = str(row.get("scope_skill", "")).strip()
        if not scope_skill:
            continue
        if inventory_policy.include_prefixes and not _matches_prefix(
            scope_skill, inventory_policy.include_prefixes
        ):
            continue
        if _matches_prefix(scope_skill, inventory_policy.exclude_prefixes):
            continue
        if _matches_prefix(scope_skill, inventory_policy.system_prefixes) and (
            inventory_policy.system_slice_mode == "exclude"
        ):
            continue
        by_scope[scope_skill] = row

    if not by_scope:
        raise RuntimeError("profile-index.json does not contain canonical scope_skill entries.")

    strict_count_check = True
    embedded_policy = profile_index.get("inventory_policy")
    if isinstance(embedded_policy, dict):
        embedded_include = _normalize_prefixes(
            embedded_policy.get("include_prefixes", inventory_policy.include_prefixes)
        )
        embedded_exclude = _normalize_prefixes(
            embedded_policy.get("exclude_prefixes", inventory_policy.exclude_prefixes)
        )
        embedded_system = _normalize_prefixes(
            embedded_policy.get("system_prefixes", inventory_policy.system_prefixes)
        )
        embedded_mode = str(
            embedded_policy.get("system_slice_mode", inventory_policy.system_slice_mode)
        ).strip().lower()
        strict_count_check = (
            embedded_include == inventory_policy.include_prefixes
            and embedded_exclude == inventory_policy.exclude_prefixes
            and embedded_system == inventory_policy.system_prefixes
            and embedded_mode == inventory_policy.system_slice_mode
        )

    if strict_count_check:
        expected_count = _safe_int(profile_index.get("expected_count"))
        if expected_count is not None and expected_count > 0 and len(by_scope) != expected_count:
            raise RuntimeError(
                f"Canonical inventory mismatch: expected_count={expected_count}, discovered={len(by_scope)}"
            )

        active_count = _safe_int(profile_index.get("active_skill_count"))
        if active_count is None:
            summary = (
                profile_index.get("summary") if isinstance(profile_index.get("summary"), dict) else {}
            )
            active_count = _safe_int(summary.get("active_skill_count")) if summary else None
        if active_count is not None and active_count > 0 and len(by_scope) != active_count:
            raise RuntimeError(
                f"Canonical inventory mismatch: active_skill_count={active_count}, discovered={len(by_scope)}"
            )

    return sorted(by_scope.keys()), by_scope


def load_profiles(
    repo_root: Path,
    profile_index: Dict[str, Any],
    wave_readiness: Dict[str, Any],
    inventory_policy: InventoryPolicy,
) -> List[SkillProfile]:
    active_skill_dirs, profile_index_by_scope = canonical_profile_inventory(profile_index, inventory_policy)
    wave_map = wave_readiness.get("waves") if isinstance(wave_readiness.get("waves"), dict) else {}

    profiles: List[SkillProfile] = []
    for scope_skill in active_skill_dirs:
        item = profile_index_by_scope.get(scope_skill, {})
        profile_rel = str(item.get("profile_path", f"{scope_skill}/references/task-profile.json")).strip()
        profile_path = _path(repo_root, profile_rel)
        if not _is_relative_to(profile_path, repo_root):
            raise RuntimeError(
                f"profile-index.json references profile_path outside repo root: {profile_rel}"
            )
        profile_obj = load_json(profile_path)

        fallback_mode = "manual" if scope_skill in MANUAL_SKILL_PATHS else "co-pilot"
        fallback_wave = "wave-1-manual" if fallback_mode == "manual" else "wave-2-co-pilot"

        profile_present = bool(profile_obj)
        profile_id = (
            str(profile_obj.get("profile_id", "")).strip()
            if profile_obj
            else ""
        ) or scope_skill.replace("/", "-")
        row_scope_profile = str(item.get("scope_profile", "")).strip()
        is_system = _matches_prefix(scope_skill, inventory_policy.system_prefixes)
        if is_system and inventory_policy.system_slice_mode == "separate":
            fallback_scope_profile = "system"
        else:
            fallback_scope_profile = scope_skill.split("/", 1)[0]
        scope_profile = (
            row_scope_profile
            or (str(profile_obj.get("scope_profile", "")).strip() if profile_obj else "")
            or fallback_scope_profile
        )
        delegation = profile_obj.get("delegation") if isinstance(profile_obj, dict) and isinstance(profile_obj.get("delegation"), dict) else {}
        delegation_mode = str(
            delegation.get("mode", item.get("delegation_mode", fallback_mode))
        ).strip().lower()
        wave = str(item.get("wave", fallback_wave))
        wave_ready = bool((wave_map.get(wave) or {}).get("ready", False)) if wave in wave_map else False

        thresholds = (
            profile_obj.get("thresholds")
            if isinstance(profile_obj, dict) and isinstance(profile_obj.get("thresholds"), dict)
            else {}
        )
        criteria = (
            profile_obj.get("criteria")
            if isinstance(profile_obj, dict) and isinstance(profile_obj.get("criteria"), list)
            else []
        )

        profiles.append(
            SkillProfile(
                scope_skill=scope_skill,
                profile_id=profile_id,
                scope_profile=scope_profile,
                delegation_mode=delegation_mode,
                thresholds=thresholds,
                criteria=[c for c in criteria if isinstance(c, dict)],
                wave=wave,
                wave_ready=wave_ready,
                profile_path=profile_rel,
                profile_present=profile_present,
            )
        )

    profiles.sort(key=lambda p: p.scope_skill)
    return profiles


def load_runs_from_dir(runs_root: Path) -> Dict[str, RunEntry]:
    out: Dict[str, RunEntry] = {}
    if not runs_root.exists():
        return out

    for run_dir in sorted(runs_root.glob("run_*")):
        if not run_dir.is_dir():
            continue
        run_obj = load_json(run_dir / "run.json")
        if not run_obj:
            continue

        run_id = str(run_obj.get("run_id", run_dir.name)).strip() or run_dir.name
        counters = run_obj.get("counters") if isinstance(run_obj.get("counters"), dict) else {}

        entry = out.get(run_id, RunEntry(run_id=run_id))
        entry.source_run_dir = True
        entry.profile_id = entry.profile_id or _clean_optional_str(run_obj.get("profile_id"))
        entry.scope_skill = entry.scope_skill or _clean_optional_str(run_obj.get("scope_skill"))
        entry.terminal_status = entry.terminal_status or _clean_optional_str(run_obj.get("terminal_status"))
        entry.stop_reason = entry.stop_reason or _clean_optional_str(run_obj.get("stop_reason"))
        if entry.iterations_completed is None:
            iterations = counters.get("iterations_completed")
            entry.iterations_completed = _safe_int(iterations)
        if entry.capture_record_present is None:
            entry.capture_record_present = (run_dir / "capture_record.json").exists()

        finished = (
            _clean_optional_str(run_obj.get("finished_at"))
            or _clean_optional_str(run_obj.get("started_at"))
        )
        if finished:
            entry.finished_at = finished

        out[run_id] = entry

    return out


def _clean_optional_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _safe_int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except Exception:
        return None


def _safe_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except Exception:
        return None


def merge_shadow_runs(runs: Dict[str, RunEntry], shadow: Dict[str, Any]) -> Set[str]:
    recent = shadow.get("recent_runs") if isinstance(shadow.get("recent_runs"), list) else []
    run_ids: Set[str] = set()

    for row in recent:
        if not isinstance(row, dict):
            continue
        run_id = str(row.get("run_id", "")).strip()
        if not run_id:
            continue
        run_ids.add(run_id)
        entry = runs.get(run_id, RunEntry(run_id=run_id))
        entry.source_shadow = True
        entry.profile_id = _coalesce(entry.profile_id, _clean_optional_str(row.get("profile_id")))
        entry.terminal_status = _coalesce(entry.terminal_status, _clean_optional_str(row.get("terminal_status")))
        entry.stop_reason = _coalesce(entry.stop_reason, _clean_optional_str(row.get("stop_reason")))
        entry.iterations_completed = _coalesce_num(entry.iterations_completed, _safe_int(row.get("iterations_completed")))
        entry.quality_uplift = _coalesce_num(entry.quality_uplift, _safe_float(row.get("quality_uplift")))
        if entry.critical_non_regression_passed is None:
            critical = row.get("critical_non_regression_passed")
            entry.critical_non_regression_passed = bool(critical) if isinstance(critical, bool) else None
        if entry.capture_record_present is None:
            capture = row.get("capture_record_present")
            entry.capture_record_present = bool(capture) if isinstance(capture, bool) else None
        entry.confidence_bucket = _coalesce(entry.confidence_bucket, _clean_optional_str(row.get("confidence_bucket")))
        entry.injected_lesson_count = _coalesce_num(entry.injected_lesson_count, _safe_int(row.get("injected_lesson_count")))
        entry.finished_at = _coalesce(entry.finished_at, _clean_optional_str(row.get("finished_at")))
        entry.queue_reason = _coalesce(entry.queue_reason, _clean_optional_str(row.get("queue_reason")))
        runs[run_id] = entry

    return run_ids


def merge_parity_manifest(runs: Dict[str, RunEntry], manifest: Dict[str, Any]) -> None:
    rows = manifest.get("runs") if isinstance(manifest.get("runs"), list) else []
    for row in rows:
        if not isinstance(row, dict):
            continue
        run_dir = str(row.get("run_dir", "")).strip()
        run_id = Path(run_dir).name if run_dir else ""
        if not run_id:
            continue

        entry = runs.get(run_id, RunEntry(run_id=run_id))
        entry.source_manifest = True
        entry.parity_status = _coalesce(entry.parity_status, _clean_optional_str(row.get("status")))
        entry.promotion_state = _coalesce(entry.promotion_state, _clean_optional_str(row.get("promotion_state")))
        entry.terminal_status = _coalesce(entry.terminal_status, _clean_optional_str(row.get("terminal_status")))
        entry.stop_reason = _coalesce(entry.stop_reason, _clean_optional_str(row.get("stop_reason")))

        if entry.capture_record_present is None:
            missing_files = row.get("missing_files") if isinstance(row.get("missing_files"), list) else []
            if missing_files:
                entry.capture_record_present = "capture_record.json" not in {
                    str(item) for item in missing_files
                }

        runs[run_id] = entry


def merge_promotion_validation(
    runs: Dict[str, RunEntry],
    promotion_validation: Dict[str, Any],
) -> Tuple[Dict[str, str], Dict[str, int]]:
    decision_by_run: Dict[str, str] = {}
    warning_counter: Counter[str] = Counter()

    results = (
        promotion_validation.get("results")
        if isinstance(promotion_validation.get("results"), list)
        else []
    )
    for row in results:
        if not isinstance(row, dict):
            continue
        run_id = str(row.get("run_id", "")).strip()
        if not run_id:
            continue

        decision = str(row.get("decision", "")).strip().lower() or "unknown"
        decision_by_run[run_id] = decision

        entry = runs.get(run_id, RunEntry(run_id=run_id))
        entry.promotion_state = decision
        runs[run_id] = entry

        warnings = row.get("warnings") if isinstance(row.get("warnings"), list) else []
        for warning in warnings:
            if isinstance(warning, dict):
                code = str(warning.get("code", "unknown")).strip() or "unknown"
                warning_counter[code] += 1

    return decision_by_run, dict(sorted(warning_counter.items()))


def _coalesce(current: Optional[str], incoming: Optional[str]) -> Optional[str]:
    return current if current not in (None, "") else incoming


def _coalesce_num(current: Optional[Any], incoming: Optional[Any]) -> Optional[Any]:
    return current if current is not None else incoming


def build_skill_alias_maps(profiles: Sequence[SkillProfile]) -> Dict[str, Dict[str, str]]:
    by_scope: Dict[str, str] = {}
    by_profile_id: Dict[str, str] = {}
    basename_hits: Dict[str, List[str]] = defaultdict(list)

    for p in profiles:
        by_scope[p.scope_skill] = p.scope_skill
        by_profile_id[p.profile_id] = p.scope_skill
        basename_hits[p.scope_skill.split("/")[-1]].append(p.scope_skill)

    by_basename: Dict[str, str] = {}
    for basename, keys in basename_hits.items():
        unique = sorted(set(keys))
        if len(unique) == 1:
            by_basename[basename] = unique[0]

    return {
        "scope": by_scope,
        "profile": by_profile_id,
        "basename": by_basename,
    }


def resolve_skill_key(
    *,
    run_profile_id: Optional[str],
    run_scope_skill: Optional[str],
    aliases: Dict[str, Dict[str, str]],
) -> Optional[str]:
    by_scope = aliases["scope"]
    by_profile = aliases["profile"]
    by_basename = aliases["basename"]

    candidates = [
        run_scope_skill,
        run_profile_id,
    ]

    for raw in candidates:
        if not raw:
            continue
        if raw in by_scope:
            return by_scope[raw]
        if raw in by_profile:
            return by_profile[raw]

        basename = raw.split("/")[-1]
        if basename in by_basename:
            return by_basename[basename]

    return None


def assign_runs_to_skills(runs: Dict[str, RunEntry], aliases: Dict[str, Dict[str, str]]) -> None:
    for run in runs.values():
        run.skill_key = resolve_skill_key(
            run_profile_id=run.profile_id,
            run_scope_skill=run.scope_skill,
            aliases=aliases,
        )


def parse_candidates(path: Path, aliases: Dict[str, Dict[str, str]]) -> List[CandidateRow]:
    rows = load_jsonl(path)
    out: List[CandidateRow] = []

    for row in rows:
        candidate_id = str(row.get("candidate_id", "")).strip() or "unknown"
        raw_skill = str(row.get("skill_path", "")).strip()
        skill_key = resolve_skill_key(
            run_profile_id=raw_skill,
            run_scope_skill=raw_skill,
            aliases=aliases,
        )
        out.append(
            CandidateRow(
                candidate_id=candidate_id,
                skill_raw=raw_skill,
                skill_key=skill_key,
                composite_score=_safe_float(row.get("composite_score")) or 0.0,
                window_count=_safe_int(row.get("window_count")) or 1,
                decision_reason=str(row.get("decision_reason", "")).strip(),
                created_at=_clean_optional_str(row.get("created_at")),
            )
        )

    return out


def build_wave_blocker_map(wave_readiness: Dict[str, Any]) -> Dict[str, List[str]]:
    waves = wave_readiness.get("waves")
    if not isinstance(waves, dict):
        return {}

    wave_name_map = {
        "wave-0-controls": "wave-0-controls",
        "wave-1-manual": "wave-1-manual",
        "wave-2-co-pilot": "wave-2-co-pilot",
    }
    out: Dict[str, List[str]] = {}
    for wave_key, canonical in wave_name_map.items():
        wave_obj = waves.get(wave_key)
        if not isinstance(wave_obj, dict):
            continue
        blockers = wave_obj.get("blockers")
        if not isinstance(blockers, list):
            continue
        codes: List[str] = []
        for blocker in blockers:
            if not isinstance(blocker, dict):
                continue
            code = str(blocker.get("code", "")).strip()
            if code:
                codes.append(code)
        if codes:
            out[canonical] = sorted(set(codes))
    return out


def compute_skill_graph_degrees(
    profiles: Sequence[SkillProfile],
    runs_by_skill: Dict[str, List[RunEntry]],
    candidates: Sequence[CandidateRow],
    queue_reason_by_skill: Dict[str, Counter[str]],
    wave_blockers_by_wave: Dict[str, List[str]],
) -> Dict[str, int]:
    degrees: Dict[str, Set[str]] = defaultdict(set)

    candidates_by_skill: Dict[str, List[CandidateRow]] = defaultdict(list)
    for candidate in candidates:
        if candidate.skill_key:
            candidates_by_skill[candidate.skill_key].append(candidate)

    for profile in profiles:
        key = profile.scope_skill
        degrees[key].add(f"profile::{profile.profile_id}")
        degrees[key].add(f"wave::{profile.wave}")
        for blocker_code in wave_blockers_by_wave.get(profile.wave, []):
            degrees[key].add(f"wave_blocker::{blocker_code}")
        for run in runs_by_skill.get(key, []):
            degrees[key].add(f"run::{run.run_id}")
        for candidate in candidates_by_skill.get(key, []):
            degrees[key].add(f"candidate::{candidate.candidate_id}")
        for queue_reason in queue_reason_by_skill.get(key, Counter()).keys():
            degrees[key].add(f"queue_reason::{queue_reason}")

    return {k: len(v) for k, v in degrees.items()}


def build_skill_states(
    profiles: Sequence[SkillProfile],
    runs: Dict[str, RunEntry],
    aliases: Dict[str, Dict[str, str]],
    shadow_run_ids: Set[str],
    decision_by_run: Dict[str, str],
    queue_rows: Sequence[Dict[str, str]],
    candidates: Sequence[CandidateRow],
    wave_blockers_by_wave: Dict[str, List[str]],
) -> List[SkillNodeState]:
    runs_by_skill: Dict[str, List[RunEntry]] = defaultdict(list)
    recent_runs_by_skill: Dict[str, List[RunEntry]] = defaultdict(list)
    for run in runs.values():
        if not run.skill_key:
            continue
        runs_by_skill[run.skill_key].append(run)
        if run.run_id in shadow_run_ids:
            recent_runs_by_skill[run.skill_key].append(run)

    queue_by_skill: Dict[str, int] = defaultdict(int)
    queue_reason_by_skill: Dict[str, Counter[str]] = defaultdict(Counter)
    for row in queue_rows:
        row_skill = row.get("skill_key") or row.get("profile")
        skill_key = resolve_skill_key(
            run_profile_id=row_skill,
            run_scope_skill=row_skill,
            aliases=aliases,
        )
        if skill_key:
            queue_by_skill[skill_key] += 1
            reason = str(row.get("reason", "unknown")).strip() or "unknown"
            queue_reason_by_skill[skill_key][reason] += 1

    pressure_by_skill: Dict[str, float] = defaultdict(float)
    for candidate in candidates:
        if candidate.skill_key:
            pressure_by_skill[candidate.skill_key] += max(candidate.composite_score, 0.0) * max(candidate.window_count, 1)

    graph_degrees = compute_skill_graph_degrees(
        profiles,
        runs_by_skill,
        candidates,
        queue_reason_by_skill,
        wave_blockers_by_wave,
    )
    max_degree = max(graph_degrees.values(), default=0)
    max_pressure = max(pressure_by_skill.values(), default=0.0)

    states: List[SkillNodeState] = []
    for profile in sorted(profiles, key=lambda p: p.scope_skill):
        recent_runs = sorted(
            recent_runs_by_skill.get(profile.scope_skill, []),
            key=lambda r: (try_parse_ts(r.finished_at) or datetime(1970, 1, 1, tzinfo=timezone.utc)),
            reverse=True,
        )
        all_runs = sorted(
            runs_by_skill.get(profile.scope_skill, []),
            key=lambda r: (try_parse_ts(r.finished_at) or datetime(1970, 1, 1, tzinfo=timezone.utc)),
            reverse=True,
        )

        latest_recent = recent_runs[0] if recent_runs else None
        latest_any = all_runs[0] if all_runs else None

        if latest_recent is None:
            halo = "no_recent_run_data"
        else:
            halo = latest_recent.terminal_status or "unknown"

        parity = (latest_any.parity_status if latest_any else None) or "empty"

        decisions_for_skill = [
            decision_by_run.get(run.run_id, run.promotion_state or "")
            for run in all_runs
            if decision_by_run.get(run.run_id, run.promotion_state)
        ]
        if any(dec == "approved" for dec in decisions_for_skill):
            badge = "approved"
        elif any(dec == "draft" for dec in decisions_for_skill):
            badge = "draft"
        elif pressure_by_skill.get(profile.scope_skill, 0.0) > 0 or queue_by_skill.get(profile.scope_skill, 0) > 0:
            badge = "candidate"
        elif any(dec in {"rejected", "failed"} for dec in decisions_for_skill):
            badge = "rejected"
        else:
            badge = "none"

        pressure = pressure_by_skill.get(profile.scope_skill, 0.0)
        pressure_norm = (pressure / max_pressure) if max_pressure > 0 else 0.0
        degree_norm = (graph_degrees.get(profile.scope_skill, 0) / max_degree) if max_degree > 0 else 0.0
        composite = max(pressure_norm, degree_norm)
        size_px = 16 + int(round(20 * composite))
        queue_counter = queue_reason_by_skill.get(profile.scope_skill, Counter())
        top_queue_reason = queue_counter.most_common(1)[0][0] if queue_counter else "none"
        blockers: List[str] = []
        blockers.extend(wave_blockers_by_wave.get(profile.wave, []))
        if top_queue_reason and top_queue_reason not in {"none", "unknown"}:
            blockers.append(f"QUEUE_{top_queue_reason}")
        if parity in {"missing_mandatory", "legacy_partial", "empty"}:
            blockers.append(f"PARITY_{parity}")
        seen_blockers: Set[str] = set()
        unique_blockers = []
        for blocker in blockers:
            if blocker in seen_blockers:
                continue
            seen_blockers.add(blocker)
            unique_blockers.append(blocker)

        blocker_severity = "none"
        if unique_blockers:
            blocker_severity = "moderate"
        if any(code in {"EVENT_ENVELOPE_ERRORS", "PARITY_missing_mandatory"} for code in unique_blockers):
            blocker_severity = "critical"
        elif any(code.startswith("QUEUE_") or code == "PARITY_legacy_partial" for code in unique_blockers):
            blocker_severity = "high"

        states.append(
            SkillNodeState(
                skill=profile,
                recent_halo=halo,
                recent_run=latest_recent,
                promotion_badge=badge,
                parity_corner=parity,
                candidate_pressure=pressure,
                centrality_score=degree_norm,
                node_size_px=size_px,
                recent_run_count=len(recent_runs),
                total_run_count=len(all_runs),
                queue_count=queue_by_skill.get(profile.scope_skill, 0),
                top_queue_reason=top_queue_reason,
                blockers=unique_blockers,
                blocker_severity=blocker_severity,
            )
        )

    return states


def build_run_lane(runs: Dict[str, RunEntry]) -> List[RunEntry]:
    def sort_key(run: RunEntry) -> Tuple[datetime, str]:
        ts = try_parse_ts(run.finished_at) or datetime(1970, 1, 1, tzinfo=timezone.utc)
        return (ts, run.run_id)

    return sorted(runs.values(), key=sort_key, reverse=True)


def group_nodes_by_cluster(states: Sequence[SkillNodeState]) -> Dict[str, List[SkillNodeState]]:
    grouped: Dict[str, List[SkillNodeState]] = defaultdict(list)
    for state in states:
        grouped[state.skill.scope_profile].append(state)
    for key in grouped:
        grouped[key].sort(key=lambda s: s.skill.scope_skill)
    return dict(sorted(grouped.items(), key=lambda kv: kv[0]))


def escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_chip(label: str, klass: str) -> str:
    tokens = [normalize_class_token(token) for token in str(klass).split() if token.strip()]
    class_attr = " ".join(["chip", *tokens])
    return f'<span class="{escape(class_attr)}">{escape(label)}</span>'


def render_global_strip(
    *,
    controls: Dict[str, Any],
    readiness: Dict[str, Any],
    health: Dict[str, Any],
    promotion: Dict[str, Any],
    artifact_metas: Sequence[ArtifactMeta],
) -> str:
    waves = readiness.get("waves") if isinstance(readiness.get("waves"), dict) else {}

    wave_items = []
    for wave_key in ["wave-0-controls", "wave-1-manual", "wave-2-co-pilot"]:
        wave_obj = waves.get(wave_key, {}) if isinstance(waves, dict) else {}
        ready = bool(wave_obj.get("ready", False))
        wave_items.append(f"<li>{escape(wave_key)}: <strong>{'ready' if ready else 'blocked'}</strong></li>")

    artifact_rows = []
    for meta in artifact_metas:
        status = "present" if meta.exists else "missing"
        artifact_rows.append(
            "<tr>"
            f"<td>{escape(meta.label)}</td>"
            f"<td>{escape(status)}</td>"
            f"<td>{escape(meta.generated_at or 'n/a')}</td>"
            f"<td>{escape(meta.file_mtime or 'n/a')}</td>"
            "</tr>"
        )

    internal_flag = health.get("dashboard_json_generated_flag")

    return """
<section class="panel global-strip">
  <h2>1) Global program strip</h2>
  <div class="card-grid four">
    <article class="card">
      <h3>Controls</h3>
      <ul>
        <li>rollout-mode: <strong>{rollout_mode}</strong> (raw: <code>{rollout_raw}</code>)</li>
        <li>kill-switch: <strong>{kill_state}</strong> (raw: <code>{kill_raw}</code>)</li>
        <li>rollback-required: <strong>{rollback_state}</strong> (raw: <code>{rollback_raw}</code>)</li>
      </ul>
      <p class="muted">Kill/rollback use runtime fail-closed semantics from <code>run_skill_genome_loop.py</code>: only explicit falsy values are inactive.</p>
    </article>
    <article class="card">
      <h3>Readiness</h3>
      <ul>
        {wave_items}
      </ul>
      <p class="muted">Summary: active={active_skills}, manual={manual_skills}, co-pilot={copilot_skills}, valid profiles={valid_profiles}, invalid profiles={invalid_profiles}.</p>
      <p class="muted">Canonical inventory rows: active={active_scan}, task-profile coverage={profile_coverage}.</p>
    </article>
    <article class="card">
      <h3>Operational health</h3>
      <ul>
        <li>shadow decision: <strong>{shadow_decision}</strong></li>
        <li>daily-health decision: <strong>{daily_decision}</strong></li>
        <li>window: <code>{window}</code></li>
        <li>pilot scoped: <strong>yes</strong> (4 UI pilot skills)</li>
      </ul>
      <p class="muted">Readiness and health are independent dimensions; this panel never collapses into a single status pill.</p>
      <p class="muted">Known caveat: <code>shadow-dashboard.json</code> exists but internal <code>artifact_outputs.dashboard_json.generated</code> is <code>{internal_flag}</code>. This view trusts file existence + generated_at.</p>
    </article>
    <article class="card">
      <h3>Promotion maturity</h3>
      <ul>
        <li>status: <strong>{promotion_status}</strong></li>
        <li>approved: <strong>{approved}</strong></li>
        <li>draft: <strong>{draft}</strong></li>
        <li>failed: <strong>{failed}</strong></li>
      </ul>
      <p class="muted">Warning patterns are preserved in Learning/change lane (legacy events/confidence/counterfactual gaps).</p>
    </article>
  </div>
  <details>
    <summary>Artifact timestamps by source</summary>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Artifact</th><th>File</th><th>generated_at</th><th>file mtime (UTC)</th></tr></thead>
        <tbody>
          {artifact_rows}
        </tbody>
      </table>
    </div>
  </details>
</section>
""".format(
        rollout_mode=escape(controls["rollout_mode"]),
        rollout_raw=escape(controls["rollout_raw"]),
        kill_state="active" if controls["kill_active"] else "inactive",
        kill_raw=escape(controls["kill_raw"]),
        rollback_state="active" if controls["rollback_active"] else "inactive",
        rollback_raw=escape(controls["rollback_raw"]),
        wave_items="\n        ".join(wave_items),
        active_skills=escape(readiness.get("active_skill_count", "n/a")),
        manual_skills=escape(readiness.get("manual_skill_count", "n/a")),
        copilot_skills=escape(readiness.get("co_pilot_skill_count", "n/a")),
        valid_profiles=escape(readiness.get("profile_valid_count", "n/a")),
        invalid_profiles=escape(readiness.get("profile_invalid_count", "n/a")),
        active_scan=escape(readiness.get("active_scan_count", "n/a")),
        profile_coverage=escape(readiness.get("profile_coverage", "n/a")),
        shadow_decision=escape(health.get("shadow_decision", "n/a")),
        daily_decision=escape(health.get("daily_decision", "n/a")),
        window=escape(health.get("window", "n/a")),
        promotion_status=escape(promotion.get("status", "n/a")),
        approved=escape(promotion.get("approved", "n/a")),
        draft=escape(promotion.get("draft", "n/a")),
        failed=escape(promotion.get("failed", "n/a")),
        internal_flag=escape(internal_flag if internal_flag is not None else "n/a"),
        artifact_rows="\n          ".join(artifact_rows),
    )


def render_skill_map(
    states: Sequence[SkillNodeState],
    grouped: Dict[str, List[SkillNodeState]],
) -> str:
    cluster_sections: List[str] = []
    graph_nodes: List[str] = []
    graph_positions: Dict[str, Tuple[float, float]] = {}

    mode_values = sorted({normalize_class_token(s.skill.delegation_mode) for s in states})
    wave_values = sorted({normalize_class_token(s.skill.wave) for s in states})
    halo_values = sorted({normalize_class_token(s.recent_halo) for s in states})
    parity_values = sorted({normalize_class_token(s.parity_corner) for s in states})
    badge_values = sorted({normalize_class_token(s.promotion_badge) for s in states})
    queue_reason_values = sorted({normalize_class_token(s.top_queue_reason) for s in states})
    blocker_values = sorted(
        {
            normalize_class_token(blocker)
            for state in states
            for blocker in (state.blockers or [])
        }
    )
    blocker_severity_values = sorted({normalize_class_token(s.blocker_severity) for s in states})

    def _graph_position(scope_skill: str, wave: str) -> Tuple[float, float]:
        digest = hashlib.sha1(scope_skill.encode("utf-8")).hexdigest()
        frac = int(digest[:8], 16) / 0xFFFFFFFF
        wave_ring = {
            "wave-0-controls": 0.20,
            "wave-1-manual": 0.34,
            "wave-2-co-pilot": 0.48,
        }
        ring = wave_ring.get(normalize_class_token(wave), 0.40)
        angle = frac * (2.0 * math.pi)
        x = 50.0 + (math.cos(angle) * ring * 60.0)
        y = 50.0 + (math.sin(angle) * ring * 42.0)
        return (round(x, 2), round(y, 2))

    def _node_markup(state: SkillNodeState, *, layout_mode: str, graph_xy: Optional[Tuple[float, float]] = None) -> str:
        halo = state.recent_halo
        parity = state.parity_corner
        badge = state.promotion_badge
        mode = normalize_class_token(state.skill.delegation_mode)
        wave = normalize_class_token(state.skill.wave)
        halo_token = normalize_class_token(halo)
        parity_token = normalize_class_token(parity)
        badge_token = normalize_class_token(badge)
        queue_reason = normalize_class_token(state.top_queue_reason)
        wave_ready_token = "wave_ready" if state.skill.wave_ready else "wave_blocked"
        profile_status = "present" if state.skill.profile_present else "missing"
        latest_run = state.recent_run.run_id if state.recent_run else "n/a"
        criteria_ids = [
            str(c.get("id", "")).strip()
            for c in state.skill.criteria
            if str(c.get("id", "")).strip()
        ]
        blocker_codes = state.blockers or []
        blocker_primary = blocker_codes[0] if blocker_codes else "none"
        blocker_token = normalize_class_token(blocker_primary)
        blocker_tokens: List[str] = []
        for blocker_code in blocker_codes:
            token = normalize_class_token(blocker_code)
            if not token or token == "none" or token in blocker_tokens:
                continue
            blocker_tokens.append(token)
        blocker_tokens_value = ",".join(blocker_tokens) if blocker_tokens else "none"
        blocker_severity = normalize_class_token(state.blocker_severity or "none")
        detail_payload = {
            "scope_skill": state.skill.scope_skill,
            "profile_id": state.skill.profile_id,
            "scope_profile": state.skill.scope_profile,
            "delegation_mode": state.skill.delegation_mode,
            "wave": state.skill.wave,
            "wave_ready": state.skill.wave_ready,
            "recent_status": state.recent_halo,
            "recent_run": latest_run,
            "parity": state.parity_corner,
            "promotion": state.promotion_badge,
            "queue_count": state.queue_count,
            "queue_reason": state.top_queue_reason,
            "pilot_window_runs": state.recent_run_count,
            "total_runs": state.total_run_count,
            "profile_status": profile_status,
            "thresholds": state.skill.thresholds,
            "criteria_ids": criteria_ids,
            "candidate_pressure": round(state.candidate_pressure, 3),
            "centrality_score": round(state.centrality_score, 3),
            "blockers": blocker_codes,
            "blocker_severity": state.blocker_severity,
        }
        short_label = state.skill.scope_skill.split("/")[-1]
        node_title = (
            f"{state.skill.scope_skill} | mode={state.skill.delegation_mode} | wave={state.skill.wave} "
            f"| recent={state.recent_halo} | parity={state.parity_corner} | promotion={state.promotion_badge} "
            f"| blockers={','.join(blocker_codes) if blocker_codes else 'none'}"
        )
        style_bits = [f"--node-size:{state.node_size_px}px"]
        if layout_mode == "graph" and graph_xy:
            style_bits.append(f"--gx:{graph_xy[0]}%")
            style_bits.append(f"--gy:{graph_xy[1]}%")
        style_attr = "; ".join(style_bits)
        blocker_display = str(len(blocker_codes)) if blocker_codes else "0"
        primary_blocker_label = blocker_primary.replace("_", " ")

        return (
            f'<article class="skill-node mode-{mode} halo-{halo_token} parity-{parity_token} '
            f'badge-{badge_token} blocker-{blocker_severity} blocker-code-{blocker_token} {wave_ready_token}" '
            f'style="{style_attr}" '
            f'data-skill-key="{escape(state.skill.scope_skill)}" '
            f'data-layout="{escape(layout_mode)}" '
            f'data-mode="{escape(mode)}" '
            f'data-wave="{escape(wave)}" '
            f'data-wave-ready="{escape(wave_ready_token)}" '
            f'data-halo="{escape(halo_token)}" '
            f'data-parity="{escape(parity_token)}" '
            f'data-badge="{escape(badge_token)}" '
            f'data-queue-reason="{escape(queue_reason)}" '
            f'data-blocker="{escape(blocker_token)}" '
            f'data-blockers="{escape(blocker_tokens_value)}" '
            f'data-blocker-severity="{escape(blocker_severity)}" '
            f'data-has-recent="{escape("yes" if state.recent_run else "no")}" '
            f'data-detail="{escape(json.dumps(detail_payload, separators=(",", ":")))}" '
            f'title="{escape(node_title)}" tabindex="0">'
            '<div class="node-glyph">'
            f'<span class="node-halo halo-{halo_token}" aria-hidden="true"></span>'
            f'<span class="node-core mode-{mode}" aria-hidden="true"></span>'
            f'<span class="node-corner parity-{parity_token}" aria-hidden="true"></span>'
            f'<span class="node-badge badge-{badge_token}">{escape(badge[:1].upper() if badge != "none" else "-")}</span>'
            f'<span class="node-blocker blocker-{blocker_severity}" title="{escape(primary_blocker_label)}">{escape(blocker_display)}</span>'
            "</div>"
            '<div class="node-labels">'
            f"<h4>{escape(short_label)}</h4>"
            f'<p class="node-sub">{escape(state.skill.profile_id)}</p>'
            "</div>"
            '<div class="node-metrics">'
            f"<span>pilot {state.recent_run_count}</span>"
            f"<span>total {state.total_run_count}</span>"
            f"<span>queue {state.queue_count}</span>"
            "</div>"
            '<div class="node-tags">'
            f'{render_chip(state.skill.delegation_mode, f"mode-{mode}")}'
            f'{render_chip(state.skill.wave, "wave-ready" if state.skill.wave_ready else "wave-blocked")}'
            f'{render_chip(f"parity:{parity}", f"parity-{parity_token}")}'
            f'{render_chip(f"blocker:{blocker_primary}", f"blocker-{blocker_severity} blocker-code-{blocker_token}")}'
            "</div>"
            "</article>"
        )

    for cluster, cluster_states in grouped.items():
        nodes: List[str] = []
        for state in cluster_states:
            graph_xy = _graph_position(state.skill.scope_skill, state.skill.wave)
            graph_positions[state.skill.scope_skill] = graph_xy
            nodes.append(_node_markup(state, layout_mode="cluster"))
            graph_nodes.append(
                _node_markup(
                    state,
                    layout_mode="graph",
                    graph_xy=graph_xy,
                )
            )

        cluster_sections.append(
            f"""
<details class="cluster" open data-cluster="{escape(cluster)}">
  <summary><h3>{escape(cluster)} <span class="muted">({len(cluster_states)} skills)</span></h3></summary>
  <div class="cluster-grid">
    {'\n    '.join(nodes)}
  </div>
</details>
""".strip()
        )

    def _edge_key(edge_type: str, source: str, target: str) -> Tuple[str, str, str]:
        ordered = tuple(sorted([source, target]))
        return (edge_type, ordered[0], ordered[1])

    edge_map: Dict[Tuple[str, str, str], Dict[str, Any]] = {}

    def _add_edge(edge_type: str, source: str, target: str, reason: str) -> None:
        if source == target:
            return
        if source not in graph_positions or target not in graph_positions:
            return
        key = _edge_key(edge_type, source, target)
        if key in edge_map:
            edge_map[key]["weight"] = int(edge_map[key].get("weight", 1)) + 1
            return
        edge_map[key] = {
            "type": edge_type,
            "source": source,
            "target": target,
            "reason": reason,
            "weight": 1,
        }

    by_profile: Dict[str, List[SkillNodeState]] = defaultdict(list)
    by_wave: Dict[str, List[SkillNodeState]] = defaultdict(list)
    by_blocker: Dict[str, List[SkillNodeState]] = defaultdict(list)
    by_queue: Dict[str, List[SkillNodeState]] = defaultdict(list)
    for state in states:
        by_profile[state.skill.scope_profile].append(state)
        by_wave[state.skill.wave].append(state)
        for blocker in state.blockers:
            by_blocker[blocker].append(state)
        if state.top_queue_reason not in {"none", "unknown", ""}:
            by_queue[state.top_queue_reason].append(state)

    for profile, profile_states in by_profile.items():
        sorted_states = sorted(profile_states, key=lambda s: s.skill.scope_skill)
        for idx in range(len(sorted_states) - 1):
            _add_edge(
                "profile_chain",
                sorted_states[idx].skill.scope_skill,
                sorted_states[idx + 1].skill.scope_skill,
                reason=f"profile:{profile}",
            )

    for wave, wave_states in by_wave.items():
        sorted_states = sorted(
            wave_states,
            key=lambda s: (-s.centrality_score, s.skill.scope_skill),
        )
        for idx in range(min(len(sorted_states) - 1, 30)):
            _add_edge(
                "wave_chain",
                sorted_states[idx].skill.scope_skill,
                sorted_states[idx + 1].skill.scope_skill,
                reason=f"wave:{wave}",
            )

    for blocker, blocker_states in by_blocker.items():
        if len(blocker_states) < 2:
            continue
        anchor = sorted(blocker_states, key=lambda s: (-s.queue_count, s.skill.scope_skill))[0]
        for state in sorted(blocker_states, key=lambda s: s.skill.scope_skill):
            if state.skill.scope_skill == anchor.skill.scope_skill:
                continue
            _add_edge(
                "blocker_star",
                anchor.skill.scope_skill,
                state.skill.scope_skill,
                reason=f"blocker:{blocker}",
            )

    for reason, reason_states in by_queue.items():
        if len(reason_states) < 2:
            continue
        sorted_states = sorted(reason_states, key=lambda s: s.skill.scope_skill)
        for idx in range(min(len(sorted_states) - 1, 18)):
            _add_edge(
                "queue_chain",
                sorted_states[idx].skill.scope_skill,
                sorted_states[idx + 1].skill.scope_skill,
                reason=f"queue:{reason}",
            )

    graph_edges_svg: List[str] = []
    for edge in sorted(
        edge_map.values(),
        key=lambda e: (e["type"], e["source"], e["target"]),
    ):
        x1, y1 = graph_positions[edge["source"]]
        x2, y2 = graph_positions[edge["target"]]
        edge_type_token = normalize_class_token(edge["type"])
        graph_edges_svg.append(
            (
                f'<line class="graph-edge type-{edge_type_token}" '
                f'x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'data-source-skill="{escape(edge["source"])}" '
                f'data-target-skill="{escape(edge["target"])}" '
                f'data-edge-type="{escape(edge_type_token)}" '
                f'data-edge-reason="{escape(edge["reason"])}" '
                f'data-layout="graph">'
                f"<title>{escape(edge['reason'])}</title>"
                "</line>"
            )
        )

    def _render_options(values: Sequence[str], label_map: Optional[Dict[str, str]] = None) -> str:
        opts = ['<option value="all">all</option>']
        for raw in values:
            label = label_map.get(raw, raw.replace("_", " ")) if label_map else raw.replace("_", " ")
            opts.append(f'<option value="{escape(raw)}">{escape(label)}</option>')
        return "\n".join(opts)

    return f"""
<section class="panel skill-map">
  <h2>2) Skill state map</h2>
  <p class="muted">Small layered glyphs keep readiness, run health, parity/compliance, and promotion visually separate while preserving one node per canonical <code>scope_skill</code>.</p>
  <div class="skill-map-toolbar card">
    <div class="control-row">
      <label>mode<select id="filter-mode">{_render_options(mode_values)}</select></label>
      <label>wave<select id="filter-wave">{_render_options(wave_values)}</select></label>
      <label>recent halo<select id="filter-halo">{_render_options(halo_values)}</select></label>
      <label>parity<select id="filter-parity">{_render_options(parity_values)}</select></label>
      <label>promotion<select id="filter-badge">{_render_options(badge_values)}</select></label>
      <label>queue reason<select id="filter-queue">{_render_options(queue_reason_values)}</select></label>
      <label>blocker code<select id="filter-blocker">{_render_options(blocker_values)}</select></label>
      <label>blocker severity<select id="filter-blocker-severity">{_render_options(blocker_severity_values)}</select></label>
      <label class="checkbox"><input id="filter-recent-only" type="checkbox" /> pilot coverage only</label>
    </div>
    <div class="control-row">
      <div class="view-toggle" role="group" aria-label="view mode">
        <button type="button" class="view-btn active" data-view="operational">operational</button>
        <button type="button" class="view-btn" data-view="readiness">readiness</button>
        <button type="button" class="view-btn" data-view="learning">learning</button>
        <button type="button" class="view-btn" data-view="graph">graph overlay</button>
      </div>
      <div class="layout-toggle" role="group" aria-label="layout mode">
        <button type="button" class="layout-btn active" data-layout="cluster">cluster layout</button>
        <button type="button" class="layout-btn" data-layout="graph">graph layout</button>
      </div>
      <fieldset class="edge-toggle" aria-label="edge type filters">
        <legend>edges</legend>
        <label><input type="checkbox" data-edge-type="profile_chain" checked />profile</label>
        <label><input type="checkbox" data-edge-type="wave_chain" checked />wave</label>
        <label><input type="checkbox" data-edge-type="blocker_star" checked />blocker</label>
        <label><input type="checkbox" data-edge-type="queue_chain" checked />queue</label>
      </fieldset>
      <button type="button" id="cluster-expand">expand clusters</button>
      <button type="button" id="cluster-collapse">collapse clusters</button>
      <button type="button" id="reset-controls">reset view</button>
      <span id="visible-node-count" class="muted"></span>
      <span id="visible-edge-count" class="muted"></span>
    </div>
  </div>
  <details open>
    <summary>Encoding legend</summary>
    <ul>
      <li>Core fill = <code>delegation.mode</code>; cluster = <code>scope_profile</code>.</li>
      <li>Outer ring = latest pilot-window <code>terminal_status</code> (or <code>no_recent_run_data</code>).</li>
      <li>Top-right corner = parity status (<code>compliant</code>, <code>missing_mandatory</code>, <code>legacy_partial</code>, <code>empty</code>).</li>
      <li>Badge letter = promotion state (<code>A</code> approved, <code>D</code> draft, <code>C</code> candidate, <code>R</code> rejected, <code>-</code> none).</li>
      <li>Bottom-left blocker bubble = blocker count with severity color; primary blocker appears as chip + filter.</li>
      <li>Node size = derived max(candidate pressure, relation centrality); explicitly derived, not canonical skill mastery.</li>
      <li>Source-state labels in Learning lane distinguish <code>missing</code> vs <code>empty</code> vs <code>present</code>.</li>
    </ul>
  </details>
  <div id="node-detail" class="card node-detail">
    <h3>Skill detail</h3>
    <p class="muted">Select a skill node to inspect thresholds, criteria, queue bottlenecks, and run coverage.</p>
  </div>
  <section id="graph-layout-board" class="graph-board card" hidden>
    <h3>Graph constellation</h3>
    <p class="muted">Deterministic radial placement by wave ring + skill hash for relationship-first scanning. Use filters to isolate blocked clusters.</p>
    <div class="graph-stage">
      <svg class="graph-edges" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
        {'\n        '.join(graph_edges_svg)}
      </svg>
      {'\n      '.join(graph_nodes)}
    </div>
  </section>
  {'\n  '.join(cluster_sections)}
</section>
"""


def render_run_lane(rows: Sequence[RunEntry]) -> str:
    body_rows: List[str] = []
    for run in rows:
        terminal_token = normalize_class_token(run.terminal_status or "unknown")
        parity_token = normalize_class_token(run.parity_status or "empty")
        promotion_token = normalize_class_token(run.promotion_state or "none")
        run_class = f"terminal-{terminal_token} parity-{parity_token} promotion-{promotion_token}"
        skill_cell = run.skill_key or run.scope_skill or run.profile_id or "n/a"
        body_rows.append(
            "<tr class=\"{klass}\" data-skill-key=\"{skill_key}\">"
            f"<td><code>{escape(run.run_id)}</code></td>"
            f"<td>{escape(run.profile_id or 'n/a')}</td>"
            f"<td>{escape(skill_cell)}</td>"
            f"<td>{escape(run.terminal_status or 'n/a')}</td>"
            f"<td>{escape(run.stop_reason or 'n/a')}</td>"
            f"<td>{escape(fmt_num(run.iterations_completed))}</td>"
            f"<td>{escape(fmt_num(run.quality_uplift))}</td>"
            f"<td>{escape(str(run.critical_non_regression_passed).lower() if run.critical_non_regression_passed is not None else 'n/a')}</td>"
            f"<td>{escape(str(run.capture_record_present).lower() if run.capture_record_present is not None else 'n/a')}</td>"
            f"<td>{escape(run.confidence_bucket or 'n/a')}</td>"
            f"<td>{escape(fmt_num(run.injected_lesson_count))}</td>"
            f"<td>{escape(run.promotion_state or 'n/a')}</td>"
            f"<td>{escape(run.parity_status or 'n/a')}</td>"
            f"<td>{escape(run.queue_reason or 'n/a')}</td>"
            f"<td>{escape(fmt_ts(run.finished_at))}</td>"
            "</tr>".format(klass=escape(run_class), skill_key=escape(run.skill_key or "unknown"))
        )

    return f"""
<section class="panel run-lane">
  <h2>3) Run / compliance lane</h2>
  <p class="muted">Time-ordered operational rows from merged <code>RunEntry</code> plus parity/promotion joins. Historical raw enum values are preserved as-is for legacy provenance.</p>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>run_id</th>
          <th>profile_id</th>
          <th>scope_skill</th>
          <th>terminal_status</th>
          <th>stop_reason</th>
          <th>iterations_completed</th>
          <th>quality_uplift</th>
          <th>critical_non_regression_passed</th>
          <th>capture_record_present</th>
          <th>confidence_bucket</th>
          <th>injected_lesson_count</th>
          <th>promotion_state</th>
          <th>parity</th>
          <th>queue_reason</th>
          <th>finished_at</th>
        </tr>
      </thead>
      <tbody>
        {'\n        '.join(body_rows)}
      </tbody>
    </table>
  </div>
</section>
"""


def render_learning_lane(
    *,
    candidates: Sequence[CandidateRow],
    queue_rows: Sequence[Dict[str, str]],
    promotion_validation: Dict[str, Any],
    warning_counts: Dict[str, int],
    feedback: Dict[str, Any],
    graph_adapter_dir_display: str,
    graph_adapter_stats: Dict[str, int],
    source_states: Dict[str, str],
) -> str:
    candidate_rows = sorted(
        candidates,
        key=lambda c: (-(c.composite_score * max(c.window_count, 1)), c.candidate_id),
    )[:20]

    candidate_table_rows: List[str] = []
    for row in candidate_rows:
        skill_key = row.skill_key or "unknown"
        candidate_table_rows.append(
            "<tr data-skill-key=\"{skill_key}\">"
            f"<td><code>{escape(row.candidate_id)}</code></td>"
            f"<td>{escape(row.skill_key or row.skill_raw or 'n/a')}</td>"
            f"<td>{row.composite_score:.3f}</td>"
            f"<td>{row.window_count}</td>"
            f"<td>{escape(row.decision_reason or 'n/a')}</td>"
            "</tr>".format(skill_key=escape(skill_key))
        )

    if not candidate_table_rows:
        candidate_table_rows.append(
            "<tr><td colspan=\"5\" class=\"muted\">No candidates.jsonl rows found (pressure currently zero).</td></tr>"
        )

    queue_items = "\n".join(
        (
            f'<li data-skill-key="{escape(row.get("skill_key") or "unknown")}">'
            f'<code>{escape(row["run_id"])}</code> | profile <code>{escape(row["profile"])}</code> '
            f'| reason <code>{escape(row.get("reason", "unknown"))}</code></li>'
        )
        for row in queue_rows[:20]
    )
    if not queue_items:
        queue_items = "<li class=\"muted\">No promotion queue rows found.</li>"

    warning_items = "\n".join(
        f"<li><code>{escape(code)}</code>: {count}</li>" for code, count in warning_counts.items()
    )
    if not warning_items:
        warning_items = "<li class=\"muted\">No warnings parsed.</li>"

    feedback_decisions = ", ".join(
        f"{k}={v}" for k, v in sorted((feedback.get("decision_counts") or {}).items())
    ) or "n/a"
    feedback_outcomes = ", ".join(
        f"{k}={v}" for k, v in sorted((feedback.get("outcome_counts") or {}).items())
    ) or "n/a"
    adapter_note_files = int(graph_adapter_stats.get("note_files", 0))
    adapter_typed_nodes = int(graph_adapter_stats.get("typed_nodes", 0))
    adapter_typed_edges = int(graph_adapter_stats.get("typed_edges", 0))

    source_items = "\n".join(
        f"<li>{escape(label)}: <strong class=\"source-{escape(state)}\">{escape(state)}</strong></li>"
        for label, state in sorted(source_states.items())
    )

    return f"""
<section class="panel learning-lane">
  <h2>4) Learning / change lane</h2>
  <p class="muted">Learning loop: run outcomes -> queue bottlenecks -> candidate proposals -> promotion validation -> optional feedback.</p>
  <div class="card-grid two">
    <article class="card">
      <h3>Genome-loop candidates</h3>
      <div class="table-wrap">
        <table>
          <thead><tr><th>candidate_id</th><th>skill</th><th>composite_score</th><th>window_count</th><th>decision_reason</th></tr></thead>
          <tbody>
            {'\n            '.join(candidate_table_rows)}
          </tbody>
        </table>
      </div>
    </article>

    <article class="card">
      <h3>Promotion queue</h3>
      <ul>
        {queue_items}
      </ul>
    </article>

    <article class="card">
      <h3>Promotion validation</h3>
      <ul>
        <li>status: <strong>{escape(promotion_validation.get('status', 'n/a'))}</strong></li>
        <li>validated: <strong>{escape(promotion_validation.get('validated', 'n/a'))}</strong></li>
        <li>draft: <strong>{escape(promotion_validation.get('draft', 'n/a'))}</strong></li>
        <li>failed: <strong>{escape(promotion_validation.get('failed', 'n/a'))}</strong></li>
      </ul>
      <p class="muted">Observed warning codes in validated runs:</p>
      <ul>
        {warning_items}
      </ul>
    </article>

    <article class="card">
      <h3>Outcome feedback + graph adapter</h3>
      <ul>
        <li>feedback log present: <strong>{'yes' if feedback.get('exists') else 'no'}</strong></li>
        <li>feedback events: <strong>{escape(feedback.get('events', 0))}</strong></li>
        <li>latest feedback: <code>{escape(feedback.get('latest_recorded_at') or 'n/a')}</code></li>
        <li>decision counts: <code>{escape(feedback_decisions)}</code></li>
        <li>outcome counts: <code>{escape(feedback_outcomes)}</code></li>
        <li>graph adapter notes: <strong>{adapter_note_files}</strong> files at <code>{escape(graph_adapter_dir_display)}</code></li>
        <li>typed graph export: <strong>{adapter_typed_nodes}</strong> nodes / <strong>{adapter_typed_edges}</strong> edges (<code>typed-graph.json</code>)</li>
      </ul>
      <p class="muted">Adapter preserves existing identifiers and emits wiki-link notes for Ars Contexta graph tooling without introducing a new business schema.</p>
    </article>

    <article class="card">
      <h3>Source-state visibility</h3>
      <ul>
        {source_items}
      </ul>
      <p class="muted">Legend: <strong class="source-present">present</strong> = file exists with non-zero signal, <strong class="source-empty">empty</strong> = file exists but no rows/signals, <strong class="source-missing">missing</strong> = source path not found.</p>
    </article>
  </div>
</section>
"""


def render_html(
    *,
    global_strip_html: str,
    skill_map_html: str,
    run_lane_html: str,
    learning_lane_html: str,
    generated_at: str,
) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Recursive Skill Graph State Map</title>
  <style>
    :root {{
      --bg: #081423;
      --panel: #102337;
      --panel-2: #122b42;
      --border: #295070;
      --text: #e7f2ff;
      --muted: #9dc0de;
      --ok: #2ecf8f;
      --warn: #f7bf49;
      --bad: #ff7d76;
      --info: #63a8ff;
      --neutral: #8aa1bf;
      --track: #0b1f31;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Avenir Next", "Segoe UI", "Helvetica Neue", sans-serif;
      background: radial-gradient(circle at 18% 6%, #13385a 0%, var(--bg) 40%, #06121f 100%);
      color: var(--text);
    }}
    .wrap {{ max-width: 1900px; margin: 0 auto; padding: 24px; }}
    h1 {{ margin: 0 0 8px; font-size: 1.65rem; }}
    h2 {{ margin: 0 0 12px; font-size: 1.18rem; letter-spacing: 0.01em; }}
    h3 {{ margin: 0 0 8px; font-size: 1rem; }}
    summary h3 {{ display: inline; }}
    .muted {{ color: var(--muted); }}
    .panel {{ background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 16px; margin-top: 16px; }}
    .card-grid {{ display: grid; gap: 12px; }}
    .card-grid.four {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
    .card-grid.two {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    .card {{
      background: linear-gradient(165deg, rgba(255, 255, 255, 0.03), rgba(0, 0, 0, 0.08)) var(--panel-2);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
    }}
    .table-wrap {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.84rem; }}
    th, td {{ border-bottom: 1px solid var(--border); text-align: left; padding: 8px; vertical-align: top; }}
    th {{ color: #beddff; font-weight: 600; }}
    code {{ background: rgba(255,255,255,0.09); padding: 1px 4px; border-radius: 4px; }}
    .layout {{ display: grid; grid-template-columns: minmax(900px, 1.95fr) minmax(420px, 1fr); gap: 16px; margin-top: 16px; align-items: start; }}
    .skill-map-toolbar {{ display: grid; gap: 10px; margin-bottom: 12px; }}
    .control-row {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
    .control-row label {{ display: inline-flex; align-items: center; gap: 6px; font-size: 0.78rem; color: var(--muted); }}
    .control-row select, .control-row button {{
      background: var(--track);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 4px 8px;
      font-size: 0.77rem;
    }}
    .control-row button {{ cursor: pointer; }}
    .checkbox input {{ margin-right: 4px; }}
    .view-toggle {{ display: inline-flex; gap: 4px; }}
    .view-btn.active {{ border-color: var(--info); box-shadow: 0 0 0 1px rgba(99,168,255,0.35) inset; }}
    .layout-toggle {{ display: inline-flex; gap: 4px; }}
    .layout-btn.active {{ border-color: var(--warn); box-shadow: 0 0 0 1px rgba(247,191,73,0.35) inset; }}
    .edge-toggle {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 4px 8px;
      margin: 0;
      min-height: 30px;
    }}
    .edge-toggle legend {{
      font-size: 0.72rem;
      color: var(--muted);
      padding: 0 4px;
      margin-right: 2px;
    }}
    .edge-toggle label {{
      display: inline-flex;
      align-items: center;
      gap: 3px;
      font-size: 0.72rem;
      color: #c6def7;
      white-space: nowrap;
    }}
    .edge-toggle input {{ margin: 0; }}
    .cluster {{ margin-top: 12px; border-top: 1px solid var(--border); padding-top: 10px; }}
    .cluster summary {{ cursor: pointer; list-style: none; }}
    .cluster summary::-webkit-details-marker {{ display: none; }}
    .cluster-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(165px, 1fr));
      gap: 8px;
      margin-top: 8px;
    }}
    .skill-node {{
      border: 1px solid var(--border);
      background: #0e2437;
      border-radius: 10px;
      padding: 8px;
      min-height: 126px;
      display: grid;
      gap: 6px;
      cursor: pointer;
      transition: transform 120ms ease, border-color 120ms ease, box-shadow 120ms ease;
    }}
    .skill-node:hover, .skill-node:focus {{
      transform: translateY(-1px);
      border-color: #6ba9e7;
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.24);
      outline: none;
    }}
    .skill-node.is-selected {{ border-color: #6ea8fe; box-shadow: 0 0 0 1px rgba(110,168,254,0.48) inset; }}
    .skill-node.is-muted {{ opacity: 0.25; }}
    .node-glyph {{ position: relative; width: 34px; height: 34px; }}
    .node-halo {{
      position: absolute;
      inset: 0;
      border: 2px solid var(--neutral);
      border-radius: 999px;
      opacity: 0.95;
    }}
    .node-core {{
      position: absolute;
      left: 50%;
      top: 50%;
      width: var(--node-size, 20px);
      height: var(--node-size, 20px);
      max-width: 22px;
      max-height: 22px;
      transform: translate(-50%, -50%);
      border-radius: 999px;
      border: 1px solid var(--border);
      background: rgba(138,161,191,0.28);
    }}
    .node-corner {{
      position: absolute;
      right: -1px;
      top: -1px;
      width: 10px;
      height: 10px;
      border-radius: 0 9px 0 9px;
      border: 1px solid var(--border);
      background: rgba(138,161,191,0.3);
    }}
    .node-badge {{
      position: absolute;
      right: -5px;
      bottom: -5px;
      width: 16px;
      height: 16px;
      border-radius: 999px;
      border: 1px solid var(--border);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 0.6rem;
      font-weight: 700;
      background: #0e2437;
    }}
    .node-blocker {{
      position: absolute;
      left: -6px;
      bottom: -6px;
      width: 16px;
      height: 16px;
      border-radius: 999px;
      border: 1px solid var(--border);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 0.57rem;
      font-weight: 700;
      background: #0f1f31;
      color: #d9e6f7;
    }}
    .node-labels h4 {{ margin: 0; font-size: 0.79rem; line-height: 1.2; }}
    .node-sub {{ margin: 0; color: var(--muted); font-size: 0.66rem; line-height: 1.15; }}
    .node-metrics {{ display: flex; gap: 6px; flex-wrap: wrap; font-size: 0.62rem; color: #bed7ff; }}
    .node-metrics span {{ border: 1px solid var(--border); border-radius: 999px; padding: 1px 5px; background: rgba(255,255,255,0.04); }}
    .node-tags {{ display: flex; flex-wrap: wrap; gap: 4px; }}
    .chip {{ display: inline-block; border: 1px solid var(--border); border-radius: 999px; padding: 1px 6px; font-size: 0.64rem; line-height: 1.3; }}
    .mode-manual {{ background: rgba(247,191,73,0.18); border-color: #d69f2b; }}
    .mode-co-pilot {{ background: rgba(99,168,255,0.18); border-color: #4f90df; }}
    .mode-autopilot {{ background: rgba(46,207,143,0.18); border-color: #2baf79; }}
    .wave-ready {{ border-color: var(--ok); color: #b6ffe0; }}
    .wave-blocked {{ border-color: var(--bad); color: #ffd9d6; }}
    .halo-passed {{ border-color: var(--ok); }}
    .halo-failed, .halo-aborted, .halo-escalated {{ border-color: var(--bad); }}
    .halo-no_recent_run_data {{ border-color: var(--neutral); }}
    .badge-approved, .badge-approved.node-badge {{ border-color: var(--ok); color: #d2ffea; }}
    .badge-draft, .badge-draft.node-badge {{ border-color: var(--info); color: #d6e9ff; }}
    .badge-candidate, .badge-candidate.node-badge {{ border-color: var(--warn); color: #ffefcc; }}
    .badge-rejected, .badge-rejected.node-badge {{ border-color: var(--bad); color: #ffe2df; }}
    .badge-none, .badge-none.node-badge {{ border-color: var(--neutral); color: #d9e0ef; }}
    .blocker-critical, .blocker-critical.node-blocker {{ border-color: var(--bad); color: #ffe2df; }}
    .blocker-high, .blocker-high.node-blocker {{ border-color: var(--warn); color: #fff0cc; }}
    .blocker-moderate, .blocker-moderate.node-blocker {{ border-color: var(--info); color: #dfeeff; }}
    .blocker-none, .blocker-none.node-blocker {{ border-color: var(--neutral); color: #d9e0ef; }}
    .parity-compliant {{ border-color: var(--ok); background: rgba(46,207,143,0.25); }}
    .parity-missing_mandatory {{ border-color: var(--bad); background: rgba(255,125,118,0.3); }}
    .parity-legacy_partial {{ border-color: var(--warn); background: rgba(247,191,73,0.3); }}
    .parity-empty {{ border-color: var(--neutral); background: rgba(138,161,191,0.25); }}
    .graph-board {{ margin-top: 14px; }}
    .graph-stage {{
      position: relative;
      min-height: 720px;
      border: 1px dashed var(--border);
      border-radius: 12px;
      background:
        radial-gradient(circle at center, rgba(138,161,191,0.12) 0 1px, transparent 1px),
        radial-gradient(circle at center, rgba(99,168,255,0.07) 0%, rgba(16,35,55,0.85) 64%);
      background-size: 14px 14px, cover;
      overflow: hidden;
    }}
    .graph-edges {{
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      z-index: 1;
      pointer-events: none;
    }}
    .graph-edge {{
      stroke: rgba(157, 192, 222, 0.25);
      stroke-width: 0.25;
      vector-effect: non-scaling-stroke;
      transition: opacity 120ms ease, stroke 120ms ease, stroke-width 120ms ease;
    }}
    .graph-edge.type-profile_chain {{ stroke: rgba(99,168,255,0.35); }}
    .graph-edge.type-wave_chain {{ stroke: rgba(46,207,143,0.30); }}
    .graph-edge.type-blocker_star {{ stroke: rgba(255,125,118,0.36); }}
    .graph-edge.type-queue_chain {{ stroke: rgba(247,191,73,0.33); }}
    .graph-edge.is-muted {{ opacity: 0.08; }}
    .graph-edge.is-selected {{
      opacity: 0.95;
      stroke: #ffe7a8;
      stroke-width: 0.48;
    }}
    .graph-stage .skill-node[data-layout="graph"] {{
      position: absolute;
      left: var(--gx);
      top: var(--gy);
      transform: translate(-50%, -50%);
      width: min(220px, 24vw);
      min-height: 120px;
      z-index: 2;
    }}
    .graph-stage .skill-node[data-layout="graph"]:hover,
    .graph-stage .skill-node[data-layout="graph"]:focus {{
      transform: translate(-50%, -50%) translateY(-1px);
    }}
    body[data-layout="cluster"] #graph-layout-board {{ display: none; }}
    body[data-layout="graph"] .cluster {{ display: none; }}
    body[data-layout="graph"] #cluster-expand,
    body[data-layout="graph"] #cluster-collapse {{ opacity: 0.45; pointer-events: none; }}
    .node-detail pre {{
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 0.76rem;
      line-height: 1.35;
      color: #cce2ff;
    }}
    .run-lane tr.terminal-passed {{ background: rgba(46,207,143,0.06); }}
    .run-lane tr.terminal-failed, .run-lane tr.terminal-escalated, .run-lane tr.terminal-aborted {{ background: rgba(255,125,118,0.08); }}
    .run-lane tr.parity-missing_mandatory {{ box-shadow: inset 4px 0 0 var(--bad); }}
    .run-lane tr.parity-legacy_partial {{ box-shadow: inset 4px 0 0 var(--warn); }}
    .run-lane tr.parity-compliant {{ box-shadow: inset 4px 0 0 var(--ok); }}
    .run-lane tr.is-selected, .learning-lane tr.is-selected, .learning-lane li.is-selected {{
      background: rgba(99,168,255,0.16) !important;
      outline: 1px solid rgba(99,168,255,0.5);
    }}
    .source-present {{ color: #abf5d5; }}
    .source-empty {{ color: #ffe8b1; }}
    .source-missing {{ color: #ffd2cd; }}
    ul {{ margin: 8px 0; padding-left: 20px; }}
    body[data-view="readiness"] .node-halo,
    body[data-view="readiness"] .node-corner,
    body[data-view="readiness"] .node-badge {{
      opacity: 0.35;
    }}
    body[data-view="learning"] .node-core,
    body[data-view="learning"] .node-corner {{
      opacity: 0.45;
    }}
    body[data-view="graph"] .node-core {{
      box-shadow: 0 0 0 1px rgba(247,191,73,0.6), 0 0 12px rgba(247,191,73,0.2);
    }}
    @media (max-width: 1500px) {{
      .layout {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 1200px) {{
      .card-grid.four {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .card-grid.two {{ grid-template-columns: 1fr; }}
      .cluster-grid {{ grid-template-columns: repeat(auto-fill, minmax(155px, 1fr)); }}
    }}
  </style>
</head>
<body data-view="operational" data-layout="cluster">
  <div class="wrap">
    <h1>Recursive Skill Graph State Map</h1>
    <p class="muted">Generated at {escape(generated_at)} UTC. This view intentionally separates onboarding readiness, runtime controls, pilot operational health, and learning/promotion maturity.</p>
    {global_strip_html}
    <div class="layout">
      {skill_map_html}
      {learning_lane_html}
    </div>
    {run_lane_html}
  </div>
  <script>
    (function () {{
      const nodes = Array.from(document.querySelectorAll(".skill-node"));
      const graphEdges = Array.from(document.querySelectorAll(".graph-edge"));
      const runRows = Array.from(document.querySelectorAll(".run-lane tbody tr"));
      const candidateRows = Array.from(document.querySelectorAll(".learning-lane tbody tr[data-skill-key]"));
      const queueItems = Array.from(document.querySelectorAll(".learning-lane li[data-skill-key]"));
      const detail = document.getElementById("node-detail");
      const visibleNodeCount = document.getElementById("visible-node-count");
      const visibleEdgeCount = document.getElementById("visible-edge-count");
      const filters = {{
        mode: document.getElementById("filter-mode"),
        wave: document.getElementById("filter-wave"),
        halo: document.getElementById("filter-halo"),
        parity: document.getElementById("filter-parity"),
        badge: document.getElementById("filter-badge"),
        queue: document.getElementById("filter-queue"),
        blocker: document.getElementById("filter-blocker"),
        blockerSeverity: document.getElementById("filter-blocker-severity"),
        recentOnly: document.getElementById("filter-recent-only"),
      }};
      const edgeTypeControls = Array.from(document.querySelectorAll(".edge-toggle input[data-edge-type]"));
      const viewButtons = Array.from(document.querySelectorAll(".view-btn"));
      const layoutButtons = Array.from(document.querySelectorAll(".layout-btn"));
      const clusterBlocks = Array.from(document.querySelectorAll(".cluster"));
      const graphLayoutBoard = document.getElementById("graph-layout-board");
      const expandBtn = document.getElementById("cluster-expand");
      const collapseBtn = document.getElementById("cluster-collapse");
      const resetControlsBtn = document.getElementById("reset-controls");
      let selectedSkill = "";
      const UI_STATE_STORAGE_KEY = "skill-state-map-ui-v1";
      const esc = (value) =>
        String(value ?? "")
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;")
          .replace(/"/g, "&quot;")
          .replace(/'/g, "&#39;");

      function setActiveButton(buttons, value, attrName) {{
        buttons.forEach((btn) => {{
          const match = (btn.dataset[attrName] || "") === value;
          btn.classList.toggle("active", match);
        }});
      }}

      function collectUiState() {{
        return {{
          view: document.body.dataset.view || "operational",
          layout: document.body.dataset.layout || "cluster",
          filters: {{
            mode: filters.mode?.value || "all",
            wave: filters.wave?.value || "all",
            halo: filters.halo?.value || "all",
            parity: filters.parity?.value || "all",
            badge: filters.badge?.value || "all",
            queue: filters.queue?.value || "all",
            blocker: filters.blocker?.value || "all",
            blockerSeverity: filters.blockerSeverity?.value || "all",
            recentOnly: !!filters.recentOnly?.checked,
          }},
          edges: edgeTypeControls
            .filter((checkbox) => checkbox.checked)
            .map((checkbox) => checkbox.dataset.edgeType || "")
            .filter(Boolean)
            .sort(),
        }};
      }}

      function readLocalUiState() {{
        try {{
          const raw = window.localStorage.getItem(UI_STATE_STORAGE_KEY);
          if (!raw) return null;
          const parsed = JSON.parse(raw);
          return parsed && typeof parsed === "object" ? parsed : null;
        }} catch (err) {{
          return null;
        }}
      }}

      function writeLocalUiState(state) {{
        try {{
          window.localStorage.setItem(UI_STATE_STORAGE_KEY, JSON.stringify(state));
        }} catch (err) {{
          // best-effort persistence
        }}
      }}

      function readUrlUiState() {{
        try {{
          const params = new URLSearchParams(window.location.search || "");
          const edges = (params.get("edges") || "")
            .split(",")
            .map((token) => token.trim())
            .filter(Boolean);
          return {{
            view: params.get("view") || undefined,
            layout: params.get("layout") || undefined,
            filters: {{
              mode: params.get("mode") || undefined,
              wave: params.get("wave") || undefined,
              halo: params.get("halo") || undefined,
              parity: params.get("parity") || undefined,
              badge: params.get("badge") || undefined,
              queue: params.get("queue") || undefined,
              blocker: params.get("blocker") || undefined,
              blockerSeverity: params.get("blockerSeverity") || undefined,
              recentOnly: params.get("recentOnly") === null ? undefined : params.get("recentOnly") === "1",
            }},
            edges: edges.length ? edges : undefined,
          }};
        }} catch (err) {{
          return null;
        }}
      }}

      function applyUiState(state) {{
        if (!state || typeof state !== "object") return;
        const view = state.view || document.body.dataset.view || "operational";
        const layout = state.layout || document.body.dataset.layout || "cluster";
        document.body.dataset.view = view;
        document.body.dataset.layout = layout;
        setActiveButton(viewButtons, view, "view");
        setActiveButton(layoutButtons, layout, "layout");

        const patchSelect = (control, value) => {{
          if (!control || value == null) return;
          const wanted = String(value);
          const hasOption = Array.from(control.options || []).some((opt) => opt.value === wanted);
          control.value = hasOption ? wanted : "all";
        }};
        const f = state.filters || {{}};
        patchSelect(filters.mode, f.mode);
        patchSelect(filters.wave, f.wave);
        patchSelect(filters.halo, f.halo);
        patchSelect(filters.parity, f.parity);
        patchSelect(filters.badge, f.badge);
        patchSelect(filters.queue, f.queue);
        patchSelect(filters.blocker, f.blocker);
        patchSelect(filters.blockerSeverity, f.blockerSeverity);
        if (filters.recentOnly && typeof f.recentOnly === "boolean") {{
          filters.recentOnly.checked = f.recentOnly;
        }}

        if (Array.isArray(state.edges) && state.edges.length) {{
          const enabled = new Set(state.edges.map((token) => String(token)));
          edgeTypeControls.forEach((checkbox) => {{
            checkbox.checked = enabled.has(checkbox.dataset.edgeType || "");
          }});
        }}
      }}

      function writeUrlUiState(state) {{
        try {{
          const url = new URL(window.location.href);
          const params = url.searchParams;
          const s = state || collectUiState();
          params.set("view", s.view || "operational");
          params.set("layout", s.layout || "cluster");
          params.set("mode", s.filters?.mode || "all");
          params.set("wave", s.filters?.wave || "all");
          params.set("halo", s.filters?.halo || "all");
          params.set("parity", s.filters?.parity || "all");
          params.set("badge", s.filters?.badge || "all");
          params.set("queue", s.filters?.queue || "all");
          params.set("blocker", s.filters?.blocker || "all");
          params.set("blockerSeverity", s.filters?.blockerSeverity || "all");
          params.set("recentOnly", s.filters?.recentOnly ? "1" : "0");
          const allEdgeTypes = edgeTypeControls.map((checkbox) => checkbox.dataset.edgeType).filter(Boolean).sort();
          const enabledEdges = Array.isArray(s.edges) ? s.edges.slice().sort() : [];
          if (
            allEdgeTypes.length &&
            enabledEdges.length === allEdgeTypes.length &&
            enabledEdges.every((edge, idx) => edge === allEdgeTypes[idx])
          ) {{
            params.delete("edges");
          }} else {{
            params.set("edges", enabledEdges.join(","));
          }}
          window.history.replaceState(null, "", `${{url.pathname}}?${{params.toString()}}${{url.hash}}`);
        }} catch (err) {{
          // best-effort persistence
        }}
      }}

      function persistUiState() {{
        const state = collectUiState();
        writeLocalUiState(state);
        writeUrlUiState(state);
      }}

      function cloneUiState(state) {{
        try {{
          return JSON.parse(JSON.stringify(state));
        }} catch (err) {{
          return collectUiState();
        }}
      }}

      function showDetail(node) {{
        if (!detail) return;
        const raw = node?.dataset?.detail;
        if (!raw) {{
          detail.innerHTML = "<h3>Skill detail</h3><p class='muted'>Select a skill node to inspect thresholds, criteria, queue bottlenecks, and run coverage.</p>";
          return;
        }}
        let payload;
        try {{
          payload = JSON.parse(raw);
        }} catch (err) {{
          detail.innerHTML = "<h3>Skill detail</h3><p class='muted'>Unable to parse node detail payload.</p>";
          return;
        }}
        const criteriaText = (payload.criteria_ids && payload.criteria_ids.length) ? payload.criteria_ids.join(", ") : "n/a";
        const blockersText = (payload.blockers && payload.blockers.length) ? payload.blockers.join(", ") : "none";
        const thresholdsText = payload.thresholds ? JSON.stringify(payload.thresholds) : "{{}}";
        detail.innerHTML = [
          "<h3>" + esc(payload.scope_skill) + "</h3>",
          "<p class='muted'>" + esc(payload.profile_id) + " | cluster " + esc(payload.scope_profile) + "</p>",
          "<pre>" +
            "mode: " + esc(payload.delegation_mode) + "\\n" +
            "wave: " + esc(payload.wave) + " (" + esc(payload.wave_ready ? "ready" : "blocked") + ")\\n" +
            "recent: " + esc(payload.recent_status) + " / run " + esc(payload.recent_run) + "\\n" +
            "parity: " + esc(payload.parity) + "\\n" +
            "promotion: " + esc(payload.promotion) + "\\n" +
            "queue: " + esc(payload.queue_count) + " (top reason: " + esc(payload.queue_reason) + ")\\n" +
            "blockers: " + esc(blockersText) + " (severity: " + esc(payload.blocker_severity || "none") + ")\\n" +
            "coverage: pilot=" + esc(payload.pilot_window_runs) + " total=" + esc(payload.total_runs) + "\\n" +
            "profile: " + esc(payload.profile_status) + "\\n" +
            "candidate_pressure: " + esc(payload.candidate_pressure) + "\\n" +
            "centrality_score: " + esc(payload.centrality_score) + "\\n" +
            "criteria: " + esc(criteriaText) + "\\n" +
            "thresholds: " + esc(thresholdsText) +
          "</pre>"
        ].join("");
      }}

      function applySelection() {{
        nodes.forEach((node) => {{
          const active = selectedSkill && node.dataset.skillKey === selectedSkill;
          node.classList.toggle("is-selected", !!active);
          node.classList.toggle("is-muted", !!selectedSkill && !active);
        }});
        graphEdges.forEach((edge) => {{
          if (!selectedSkill) {{
            edge.classList.remove("is-selected");
            edge.classList.remove("is-muted");
            return;
          }}
          const connected =
            edge.dataset.sourceSkill === selectedSkill ||
            edge.dataset.targetSkill === selectedSkill;
          edge.classList.toggle("is-selected", connected);
          edge.classList.toggle("is-muted", !connected);
        }});
        runRows.forEach((row) => {{
          row.classList.toggle("is-selected", !!selectedSkill && row.dataset.skillKey === selectedSkill);
        }});
        candidateRows.forEach((row) => {{
          row.classList.toggle("is-selected", !!selectedSkill && row.dataset.skillKey === selectedSkill);
        }});
        queueItems.forEach((item) => {{
          item.classList.toggle("is-selected", !!selectedSkill && item.dataset.skillKey === selectedSkill);
        }});
      }}

      function matchesFilter(node, key, value) {{
        if (!value || value === "all") return true;
        if (key === "blockers") {{
          const blockerTokens = (node.dataset.blockers || "")
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean);
          return blockerTokens.includes(value);
        }}
        return node.dataset[key] === value;
      }}

      function inActiveLayout(node) {{
        const layout = document.body.dataset.layout || "cluster";
        return (node.dataset.layout || "cluster") === layout;
      }}

      function isSkillVisible(skillKey) {{
        return nodes.some((node) =>
          node.dataset.skillKey === skillKey &&
          inActiveLayout(node) &&
          !node.hidden
        );
      }}

      function isEdgeTypeEnabled(edgeType) {{
        if (!edgeType) return true;
        if (!edgeTypeControls.length) return true;
        const control = edgeTypeControls.find((item) => item.dataset.edgeType === edgeType);
        return control ? !!control.checked : true;
      }}

      function applyFilters() {{
        let visible = 0;
        nodes.forEach((node) => {{
          const show =
            matchesFilter(node, "mode", filters.mode?.value) &&
            matchesFilter(node, "wave", filters.wave?.value) &&
            matchesFilter(node, "halo", filters.halo?.value) &&
            matchesFilter(node, "parity", filters.parity?.value) &&
            matchesFilter(node, "badge", filters.badge?.value) &&
            matchesFilter(node, "queueReason", filters.queue?.value) &&
            matchesFilter(node, "blockers", filters.blocker?.value) &&
            matchesFilter(node, "blockerSeverity", filters.blockerSeverity?.value) &&
            (!filters.recentOnly?.checked || node.dataset.hasRecent === "yes");
          const activeLayout = inActiveLayout(node);
          node.hidden = !show || !activeLayout;
          if (show && activeLayout) visible += 1;
        }});
        if ((document.body.dataset.layout || "cluster") === "cluster") {{
          clusterBlocks.forEach((cluster) => {{
            const clusterNodes = Array.from(cluster.querySelectorAll('.skill-node[data-layout="cluster"]'));
            const anyVisible = clusterNodes.some((node) => !node.hidden);
            cluster.hidden = !anyVisible;
          }});
          if (graphLayoutBoard) graphLayoutBoard.hidden = true;
        }} else {{
          clusterBlocks.forEach((cluster) => {{
            cluster.hidden = true;
          }});
          if (graphLayoutBoard) graphLayoutBoard.hidden = false;
        }}
        graphEdges.forEach((edge) => {{
          const isGraphLayout = (document.body.dataset.layout || "cluster") === "graph";
          const show =
            isGraphLayout &&
            isEdgeTypeEnabled(edge.dataset.edgeType || "") &&
            isSkillVisible(edge.dataset.sourceSkill || "") &&
            isSkillVisible(edge.dataset.targetSkill || "");
          edge.hidden = !show;
        }});
        if (visibleNodeCount) {{
          visibleNodeCount.textContent = visible + " visible nodes";
        }}
        if (visibleEdgeCount) {{
          const visibleEdges = graphEdges.filter((edge) => !edge.hidden).length;
          visibleEdgeCount.textContent = visibleEdges + " visible edges";
        }}
      }}

      nodes.forEach((node) => {{
        node.addEventListener("click", () => {{
          selectedSkill = node.dataset.skillKey || "";
          showDetail(node);
          applySelection();
        }});
        node.addEventListener("keydown", (event) => {{
          if (event.key === "Enter" || event.key === " ") {{
            event.preventDefault();
            node.click();
          }}
        }});
      }});

      Object.values(filters).forEach((el) => {{
        if (!el) return;
        el.addEventListener("change", () => {{
          applyFilters();
          applySelection();
          persistUiState();
        }});
      }});
      edgeTypeControls.forEach((checkbox) => {{
        checkbox.addEventListener("change", () => {{
          applyFilters();
          applySelection();
          persistUiState();
        }});
      }});

      viewButtons.forEach((btn) => {{
        btn.addEventListener("click", () => {{
          viewButtons.forEach((item) => item.classList.remove("active"));
          btn.classList.add("active");
          document.body.dataset.view = btn.dataset.view || "operational";
          persistUiState();
        }});
      }});

      layoutButtons.forEach((btn) => {{
        btn.addEventListener("click", () => {{
          layoutButtons.forEach((item) => item.classList.remove("active"));
          btn.classList.add("active");
          document.body.dataset.layout = btn.dataset.layout || "cluster";
          applyFilters();
          applySelection();
          persistUiState();
        }});
      }});

      if (expandBtn) {{
        expandBtn.addEventListener("click", () => {{
          clusterBlocks.forEach((cluster) => {{ cluster.open = true; }});
        }});
      }}
      if (collapseBtn) {{
        collapseBtn.addEventListener("click", () => {{
          clusterBlocks.forEach((cluster) => {{ cluster.open = false; }});
        }});
      }}

      const DEFAULT_UI_STATE = collectUiState();
      const localState = readLocalUiState();
      const urlState = readUrlUiState();
      const bootstrapState = cloneUiState(DEFAULT_UI_STATE);
      if (localState && typeof localState === "object") {{
        bootstrapState.view = localState.view || bootstrapState.view;
        bootstrapState.layout = localState.layout || bootstrapState.layout;
        bootstrapState.filters = Object.assign({{}}, bootstrapState.filters, localState.filters || {{}});
        if (Array.isArray(localState.edges)) bootstrapState.edges = localState.edges;
      }}
      if (urlState && typeof urlState === "object") {{
        if (urlState.view) bootstrapState.view = urlState.view;
        if (urlState.layout) bootstrapState.layout = urlState.layout;
        bootstrapState.filters = Object.assign({{}}, bootstrapState.filters, urlState.filters || {{}});
        if (Array.isArray(urlState.edges)) bootstrapState.edges = urlState.edges;
      }}
      applyUiState(bootstrapState);

      if (resetControlsBtn) {{
        resetControlsBtn.addEventListener("click", () => {{
          selectedSkill = "";
          applyUiState(cloneUiState(DEFAULT_UI_STATE));
          showDetail(null);
          applyFilters();
          applySelection();
          persistUiState();
        }});
      }}

      applyFilters();
      applySelection();
      persistUiState();
    }})();
  </script>
</body>
</html>
"""


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "item"


def sanitize_note_value(value: Any) -> str:
    text = str(value if value is not None else "n/a").replace("\r", " ").replace("\n", " ").strip()
    text = text.replace("`", "'").replace("[[", "[ [").replace("]]", "] ]")
    return text or "n/a"


def build_graph_adapter(
    *,
    repo_root: Path,
    out_dir: Path,
    states: Sequence[SkillNodeState],
    runs: Sequence[RunEntry],
    candidates: Sequence[CandidateRow],
) -> Dict[str, int]:
    allowed_root = (repo_root / GRAPH_ADAPTER_ALLOWED_REL).resolve()
    if not _is_relative_to(out_dir, allowed_root):
        raise RuntimeError(
            f"Refusing to write graph adapter outside repo-managed directory: {out_dir} (allowed root: {allowed_root})"
        )

    out_dir.mkdir(parents=True, exist_ok=True)

    for prefix in GRAPH_ADAPTER_FILE_PREFIXES:
        for existing in out_dir.glob(f"{prefix}*.md"):
            existing.unlink()

    files_written = 0

    skill_title: Dict[str, str] = {}
    profile_title: Dict[str, str] = {}
    wave_title: Dict[str, str] = {}
    blocker_title: Dict[str, str] = {}

    typed_nodes: Dict[str, Dict[str, Any]] = {}
    typed_edges: Dict[Tuple[str, str, str], Dict[str, Any]] = {}

    def add_typed_node(
        node_id: str,
        *,
        node_type: str,
        label: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        current = typed_nodes.get(node_id, {})
        merged_metadata: Dict[str, Any] = {}
        for source in [current.get("metadata"), metadata]:
            if isinstance(source, dict):
                merged_metadata.update(source)
        typed_nodes[node_id] = {
            "id": node_id,
            "type": node_type,
            "label": label,
            "metadata": merged_metadata,
        }

    def add_typed_edge(
        *,
        edge_type: str,
        source: str,
        target: str,
        weight: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        key = (edge_type, source, target)
        if key not in typed_edges:
            typed_edges[key] = {
                "type": edge_type,
                "source": source,
                "target": target,
                "weight": max(weight, 1),
                "metadata": metadata or {},
            }
            return
        typed_edges[key]["weight"] = int(typed_edges[key].get("weight", 1)) + max(weight, 1)
        if isinstance(metadata, dict):
            merged = typed_edges[key].get("metadata")
            if isinstance(merged, dict):
                merged.update(metadata)
            else:
                typed_edges[key]["metadata"] = dict(metadata)

    runs_by_skill: Dict[str, List[RunEntry]] = defaultdict(list)
    for run in runs:
        if run.skill_key:
            runs_by_skill[run.skill_key].append(run)

    candidates_by_skill: Dict[str, List[CandidateRow]] = defaultdict(list)
    for candidate in candidates:
        if candidate.skill_key:
            candidates_by_skill[candidate.skill_key].append(candidate)

    for state in states:
        skill_key = state.skill.scope_skill
        skill_title[skill_key] = f"skill--{slugify(skill_key)}"
        profile_title[skill_key] = f"profile--{slugify(state.skill.profile_id)}"
        wave_title[state.skill.wave] = f"wave--{slugify(state.skill.wave)}"
        for blocker in state.blockers:
            blocker_title[blocker] = f"blocker--{slugify(blocker)}"

        add_typed_node(
            skill_title[skill_key],
            node_type="skill",
            label=skill_key,
            metadata={
                "delegation_mode": state.skill.delegation_mode,
                "wave": state.skill.wave,
                "parity": state.parity_corner,
                "promotion_badge": state.promotion_badge,
                "blocker_severity": state.blocker_severity,
            },
        )
        add_typed_node(
            profile_title[skill_key],
            node_type="profile",
            label=state.skill.profile_id,
            metadata={"scope_profile": state.skill.scope_profile},
        )
        add_typed_node(
            wave_title[state.skill.wave],
            node_type="wave",
            label=state.skill.wave,
            metadata={},
        )
        add_typed_edge(
            edge_type="skill_profile",
            source=skill_title[skill_key],
            target=profile_title[skill_key],
            metadata={"scope_skill": skill_key},
        )
        add_typed_edge(
            edge_type="skill_wave",
            source=skill_title[skill_key],
            target=wave_title[state.skill.wave],
            metadata={"scope_skill": skill_key},
        )

        for blocker in state.blockers:
            blocker_id = blocker_title[blocker]
            add_typed_node(
                blocker_id,
                node_type="blocker",
                label=blocker,
                metadata={"severity_hint": state.blocker_severity},
            )
            add_typed_edge(
                edge_type="skill_blocker",
                source=skill_title[skill_key],
                target=blocker_id,
                weight=max(state.queue_count, 1),
                metadata={"scope_skill": skill_key},
            )

    for state in states:
        skill_key = state.skill.scope_skill
        content = [
            f"# {skill_title[skill_key]}",
            "",
            f"- scope_skill: `{sanitize_note_value(skill_key)}`",
            f"- profile_id: `{sanitize_note_value(state.skill.profile_id)}`",
            f"- scope_profile: `{sanitize_note_value(state.skill.scope_profile)}`",
            f"- delegation_mode: `{sanitize_note_value(state.skill.delegation_mode)}`",
            f"- wave: `{sanitize_note_value(state.skill.wave)}`",
            f"- halo: `{sanitize_note_value(state.recent_halo)}`",
            f"- promotion_badge: `{sanitize_note_value(state.promotion_badge)}`",
            f"- parity: `{sanitize_note_value(state.parity_corner)}`",
            f"- blockers: `{sanitize_note_value(','.join(state.blockers) if state.blockers else 'none')}`",
            f"- blocker_severity: `{sanitize_note_value(state.blocker_severity)}`",
            "",
            f"Links: [[{profile_title[skill_key]}]] [[{wave_title[state.skill.wave]}]]",
        ]
        for run in runs_by_skill.get(skill_key, []):
            content.append(f"[[run--{slugify(run.run_id)}]]")
        for candidate in candidates_by_skill.get(skill_key, []):
            content.append(f"[[candidate--{slugify(candidate.candidate_id)}]]")

        (out_dir / f"{skill_title[skill_key]}.md").write_text("\n".join(content) + "\n", encoding="utf-8")
        files_written += 1

        profile_content = [
            f"# {profile_title[skill_key]}",
            "",
            f"- profile_id: `{sanitize_note_value(state.skill.profile_id)}`",
            f"- scope_skill: `{sanitize_note_value(skill_key)}`",
            f"- scope_profile: `{sanitize_note_value(state.skill.scope_profile)}`",
            "",
            f"Links: [[{skill_title[skill_key]}]] [[{wave_title[state.skill.wave]}]]",
        ]
        (out_dir / f"{profile_title[skill_key]}.md").write_text(
            "\n".join(profile_content) + "\n", encoding="utf-8"
        )
        files_written += 1

    for blocker, title in sorted(blocker_title.items(), key=lambda kv: kv[0]):
        links = [
            f"[[{skill_title[state.skill.scope_skill]}]]"
            for state in states
            if blocker in state.blockers
        ]
        content = [
            f"# {title}",
            "",
            f"- blocker_code: `{sanitize_note_value(blocker)}`",
            "",
            *links,
        ]
        (out_dir / f"{title}.md").write_text("\n".join(content) + "\n", encoding="utf-8")
        files_written += 1

    for wave, title in wave_title.items():
        links = [f"[[{skill_title[state.skill.scope_skill]}]]" for state in states if state.skill.wave == wave]
        content = [
            f"# {title}",
            "",
            f"- wave: `{sanitize_note_value(wave)}`",
            "",
            *links,
        ]
        (out_dir / f"{title}.md").write_text("\n".join(content) + "\n", encoding="utf-8")
        files_written += 1

    decision_titles: Set[str] = set()
    for run in runs:
        run_title = f"run--{slugify(run.run_id)}"
        add_typed_node(
            run_title,
            node_type="run",
            label=run.run_id,
            metadata={
                "terminal_status": run.terminal_status or "n/a",
                "parity": run.parity_status or "n/a",
                "promotion_state": run.promotion_state or "none",
            },
        )
        links = []
        if run.skill_key and run.skill_key in skill_title:
            links.append(f"[[{skill_title[run.skill_key]}]]")
            add_typed_edge(
                edge_type="skill_run",
                source=skill_title[run.skill_key],
                target=run_title,
                metadata={"run_id": run.run_id},
            )
        if run.promotion_state:
            decision_title = f"decision--{slugify(run.run_id)}-{slugify(run.promotion_state)}"
            decision_titles.add(decision_title)
            links.append(f"[[{decision_title}]]")
            add_typed_node(
                decision_title,
                node_type="decision",
                label=run.promotion_state,
                metadata={"run_id": run.run_id},
            )
            add_typed_edge(
                edge_type="run_decision",
                source=run_title,
                target=decision_title,
                metadata={"run_id": run.run_id},
            )

        run_content = [
            f"# {run_title}",
            "",
            f"- run_id: `{sanitize_note_value(run.run_id)}`",
            f"- profile_id: `{sanitize_note_value(run.profile_id or 'n/a')}`",
            f"- terminal_status: `{sanitize_note_value(run.terminal_status or 'n/a')}`",
            f"- stop_reason: `{sanitize_note_value(run.stop_reason or 'n/a')}`",
            f"- parity: `{sanitize_note_value(run.parity_status or 'n/a')}`",
            "",
            f"Links: {' '.join(links) if links else '(none)'}",
        ]
        (out_dir / f"{run_title}.md").write_text("\n".join(run_content) + "\n", encoding="utf-8")
        files_written += 1

    for title in sorted(decision_titles):
        content = [
            f"# {title}",
            "",
            "- entity: promotion-decision",
            "",
        ]
        (out_dir / f"{title}.md").write_text("\n".join(content) + "\n", encoding="utf-8")
        files_written += 1

    for candidate in candidates:
        candidate_title = f"candidate--{slugify(candidate.candidate_id)}"
        add_typed_node(
            candidate_title,
            node_type="candidate",
            label=candidate.candidate_id,
            metadata={
                "skill_raw": candidate.skill_raw,
                "composite_score": round(candidate.composite_score, 3),
                "window_count": candidate.window_count,
            },
        )
        links = []
        if candidate.skill_key and candidate.skill_key in skill_title:
            links.append(f"[[{skill_title[candidate.skill_key]}]]")
            add_typed_edge(
                edge_type="skill_candidate",
                source=skill_title[candidate.skill_key],
                target=candidate_title,
                metadata={"decision_reason": candidate.decision_reason or "n/a"},
            )
        content = [
            f"# {candidate_title}",
            "",
            f"- candidate_id: `{sanitize_note_value(candidate.candidate_id)}`",
            f"- skill_raw: `{sanitize_note_value(candidate.skill_raw or 'n/a')}`",
            f"- composite_score: `{sanitize_note_value(f'{candidate.composite_score:.3f}')}`",
            f"- window_count: `{sanitize_note_value(candidate.window_count)}`",
            f"- decision_reason: `{sanitize_note_value(candidate.decision_reason or 'n/a')}`",
            "",
            f"Links: {' '.join(links) if links else '(none)'}",
        ]
        (out_dir / f"{candidate_title}.md").write_text("\n".join(content) + "\n", encoding="utf-8")
        files_written += 1

    typed_graph = {
        "schema_version": "1.0",
        "generated_at": _utc_iso_now(),
        "counts": {
            "nodes": len(typed_nodes),
            "edges": len(typed_edges),
            "note_files": files_written,
        },
        "nodes": sorted(typed_nodes.values(), key=lambda item: (item.get("type", ""), item.get("id", ""))),
        "edges": sorted(
            typed_edges.values(),
            key=lambda item: (item.get("type", ""), item.get("source", ""), item.get("target", "")),
        ),
    }
    (out_dir / "typed-graph.json").write_text(json.dumps(typed_graph, indent=2) + "\n", encoding="utf-8")

    return {
        "note_files": files_written,
        "typed_nodes": len(typed_nodes),
        "typed_edges": len(typed_edges),
    }


def main() -> int:
    args = parse_args()
    repo_root = _path(Path.cwd(), args.repo_root)

    controls_dir = _path(repo_root, args.controls_dir)
    wave_readiness_path = _path(repo_root, args.wave_readiness)
    profile_index_path = _path(repo_root, args.profile_index)
    shadow_dashboard_path = _path(repo_root, args.shadow_dashboard)
    daily_health_path = _path(repo_root, args.daily_health_md)
    canonical_daily_health_path = _path(repo_root, "docs/skill-graphs/telemetry/daily-skill-health.md")
    legacy_daily_health_path = _path(repo_root, "artifacts/skill-graphs/telemetry/daily-skill-health.md")
    if daily_health_path != canonical_daily_health_path:
        raise RuntimeError(
            "Path divergence: --daily-health-md must resolve to docs/skill-graphs/telemetry/daily-skill-health.md"
        )
    if not daily_health_path.exists():
        if legacy_daily_health_path.exists():
            raise RuntimeError(
                f"Path divergence: canonical daily health is missing ({daily_health_path}) while legacy path exists ({legacy_daily_health_path})."
            )
        raise RuntimeError(f"Missing canonical daily health artifact: {daily_health_path}")
    if legacy_daily_health_path.exists():
        canonical_text = daily_health_path.read_text(encoding="utf-8")
        legacy_text = legacy_daily_health_path.read_text(encoding="utf-8")
        if canonical_text != legacy_text:
            raise RuntimeError(
                f"Path divergence: docs and artifacts daily health files differ ({daily_health_path} vs {legacy_daily_health_path})."
            )
    promotion_queue_path = _path(repo_root, args.promotion_queue_md)
    promotion_validation_path = _path(repo_root, args.promotion_validation)
    parity_manifest_path = _path(repo_root, args.parity_manifest)
    candidates_path = _path(repo_root, args.candidates_jsonl)
    runs_root = _path(repo_root, args.runs_root)
    feedback_log_path = _path(repo_root, args.feedback_log)
    graph_adapter_dir = _path(repo_root, args.graph_adapter_dir)
    typed_graph_path = graph_adapter_dir / "typed-graph.json"
    out_html = _path(repo_root, args.out_html)

    wave_readiness = load_required_json(wave_readiness_path, "wave-readiness")
    profile_index = load_required_json(profile_index_path, "profile-index")
    shadow_dashboard = load_required_json(shadow_dashboard_path, "shadow-dashboard")
    promotion_validation = load_required_json(promotion_validation_path, "promotion-validation")
    parity_manifest = load_required_json(parity_manifest_path, "parity-manifest")
    inventory_policy = load_inventory_policy(
        repo_root=repo_root,
        profile_index=profile_index,
        raw_path=args.inventory_policy,
        system_slice_mode=args.system_slice_mode,
    )

    profiles = load_profiles(repo_root, profile_index, wave_readiness, inventory_policy)
    aliases = build_skill_alias_maps(profiles)

    runs = load_runs_from_dir(runs_root)
    shadow_run_ids = merge_shadow_runs(runs, shadow_dashboard)
    merge_parity_manifest(runs, parity_manifest)
    decision_by_run, warning_counts = merge_promotion_validation(runs, promotion_validation)
    assign_runs_to_skills(runs, aliases)

    candidates = parse_candidates(candidates_path, aliases)
    queue_rows = parse_promotion_queue(promotion_queue_path)
    for row in queue_rows:
        skill_key = resolve_skill_key(
            run_profile_id=row.get("profile"),
            run_scope_skill=row.get("profile"),
            aliases=aliases,
        )
        row["skill_key"] = skill_key or ""
    feedback = parse_feedback(feedback_log_path)

    readiness_summary = (
        wave_readiness.get("summary") if isinstance(wave_readiness.get("summary"), dict) else {}
    )

    daily_health = parse_daily_health(daily_health_path)
    health = {
        "shadow_decision": ((shadow_dashboard.get("decision") or {}).get("state") if isinstance(shadow_dashboard.get("decision"), dict) else "n/a")
        or "n/a",
        "daily_decision": daily_health.get("decision", "n/a"),
        "window": shadow_dashboard.get("current_window") or daily_health.get("window") or "n/a",
        "dashboard_json_generated_flag": (
            (((shadow_dashboard.get("artifact_outputs") or {}).get("dashboard_json") or {}).get("generated"))
            if isinstance(shadow_dashboard.get("artifact_outputs"), dict)
            else None
        ),
    }

    promotion_summary = {
        "status": promotion_validation.get("status", "n/a"),
        "approved": promotion_validation.get("validated", "n/a"),
        "draft": promotion_validation.get("draft", "n/a"),
        "failed": promotion_validation.get("failed", "n/a"),
    }

    controls: Dict[str, Any] = {}
    controls["rollout_mode"], controls["rollout_raw"], _ = read_rollout_mode(controls_dir / "rollout-mode.txt")
    controls["kill_active"], controls["kill_raw"], _ = read_fail_closed_switch(controls_dir / "kill-switch.txt")
    controls["rollback_active"], controls["rollback_raw"], _ = read_fail_closed_switch(controls_dir / "rollback-required.txt")

    readiness = {
        "active_skill_count": readiness_summary.get("active_skill_count", len(profiles)),
        "manual_skill_count": readiness_summary.get("manual_skill_count", "n/a"),
        "co_pilot_skill_count": readiness_summary.get("co_pilot_skill_count", "n/a"),
        "profile_valid_count": readiness_summary.get("profile_valid_count", len(profiles)),
        "profile_invalid_count": readiness_summary.get("profile_invalid_count", "n/a"),
        "waves": wave_readiness.get("waves") if isinstance(wave_readiness.get("waves"), dict) else {},
        "active_scan_count": len(profiles),
        "profile_coverage": f"{sum(1 for p in profiles if p.profile_present)}/{len(profiles)}",
    }

    states = build_skill_states(
        profiles=profiles,
        runs=runs,
        aliases=aliases,
        shadow_run_ids=shadow_run_ids,
        decision_by_run=decision_by_run,
        queue_rows=queue_rows,
        candidates=candidates,
        wave_blockers_by_wave=build_wave_blocker_map(wave_readiness),
    )
    grouped = group_nodes_by_cluster(states)
    run_lane_rows = build_run_lane(runs)

    artifact_metas = [
        artifact_meta("wave-readiness", wave_readiness_path, wave_readiness),
        artifact_meta("profile-index", profile_index_path, profile_index),
        artifact_meta("shadow-dashboard", shadow_dashboard_path, shadow_dashboard),
        artifact_meta("daily-skill-health", daily_health_path, None),
        artifact_meta("promotion-queue", promotion_queue_path, None),
        artifact_meta("promotion-validation", promotion_validation_path, promotion_validation),
        artifact_meta("parity-manifest", parity_manifest_path, parity_manifest),
        artifact_meta("candidates", candidates_path, None),
    ]

    graph_adapter_stats = {"note_files": 0, "typed_nodes": 0, "typed_edges": 0}
    if args.with_graph_adapter:
        graph_adapter_stats = build_graph_adapter(
            repo_root=repo_root,
            out_dir=graph_adapter_dir,
            states=states,
            runs=run_lane_rows,
            candidates=candidates,
        )
    graph_adapter_note_files = len(list(graph_adapter_dir.glob("*.md"))) if graph_adapter_dir.exists() else 0
    typed_graph_payload = load_json(typed_graph_path) if typed_graph_path.exists() else None
    typed_graph_edges = (
        len(typed_graph_payload.get("edges")) if isinstance(typed_graph_payload, dict) and isinstance(typed_graph_payload.get("edges"), list) else 0
    )
    source_states = {
        "candidates.jsonl": classify_source_state(candidates_path, len(candidates)),
        "promotion-queue.md": classify_source_state(promotion_queue_path, len(queue_rows)),
        "promotion-validation-report.json": classify_source_state(
            promotion_validation_path,
            len(
                promotion_validation.get("results")
                if isinstance(promotion_validation.get("results"), list)
                else []
            ),
        ),
        "feedback log": classify_source_state(feedback_log_path, int(feedback.get("events", 0))),
        "graph-adapter notes": classify_source_state(graph_adapter_dir, graph_adapter_note_files),
        "typed-graph.json": classify_source_state(typed_graph_path, typed_graph_edges),
    }

    global_strip_html = render_global_strip(
        controls=controls,
        readiness=readiness,
        health=health,
        promotion=promotion_summary,
        artifact_metas=artifact_metas,
    )
    skill_map_html = render_skill_map(states, grouped)
    run_lane_html = render_run_lane(run_lane_rows)
    graph_adapter_dir_display = (
        graph_adapter_dir.relative_to(repo_root).as_posix()
        if _is_relative_to(graph_adapter_dir, repo_root)
        else "artifacts/skill-graphs/graph-adapter/notes"
    )

    learning_lane_html = render_learning_lane(
        candidates=candidates,
        queue_rows=queue_rows,
        promotion_validation=promotion_validation,
        warning_counts=warning_counts,
        feedback=feedback,
        graph_adapter_dir_display=graph_adapter_dir_display,
        graph_adapter_stats=graph_adapter_stats,
        source_states=source_states,
    )

    rendered = render_html(
        global_strip_html=global_strip_html,
        skill_map_html=skill_map_html,
        run_lane_html=run_lane_html,
        learning_lane_html=learning_lane_html,
        generated_at=_utc_iso_now(),
    )

    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(rendered, encoding="utf-8")

    summary = {
        "out_html": out_html.relative_to(repo_root).as_posix() if _is_relative_to(out_html, repo_root) else "<redacted-absolute-path>",
        "skills": len(states),
        "clusters": len(grouped),
        "runs": len(run_lane_rows),
        "shadow_runs": len(shadow_run_ids),
        "candidate_rows": len(candidates),
        "graph_adapter_files": graph_adapter_stats.get("note_files", 0),
        "typed_graph_nodes": graph_adapter_stats.get("typed_nodes", 0),
        "typed_graph_edges": graph_adapter_stats.get("typed_edges", 0),
        "health_decision": health.get("shadow_decision"),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
    adapter_note_files = int(graph_adapter_stats.get("note_files", 0))
    adapter_typed_nodes = int(graph_adapter_stats.get("typed_nodes", 0))
    adapter_typed_edges = int(graph_adapter_stats.get("typed_edges", 0))
