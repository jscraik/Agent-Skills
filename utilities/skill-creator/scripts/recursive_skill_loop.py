#!/usr/bin/env python3
"""Bounded recursive skill self-improvement loop (MVP scaffold).

Implements a deterministic loop:
  generate -> evaluate -> diagnose -> improve -> re-score

Canonical artifacts written per run:
- run.json
- iteration_journal.jsonl
- promotion_decision.json
- capture_record.json
- evidence_packet.json
- lesson_candidates.json

Optional debug artifacts (disabled by default):
- debug/events.jsonl
- debug/summary.md
- debug/iter-*-generated.txt
- debug/iter-*-improved.txt
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

TERMINAL_STATUSES = {"passed", "failed", "escalated", "aborted"}
STOP_REASONS = {
    "pass",
    "budget_exhausted",
    "escalated",
    "aborted",
    "policy_failed",
    "evaluator_conflict",
    "dependency_missing",
}

FEEDBACK_OUTCOMES = {"worked", "partly", "didnt_work"}
ROLLOUT_MODES = {"off", "observe_only", "active"}
LESSON_STATUS_PRIORITY = {
    "active": 5,
    "promoted": 4,
    "superseded": 3,
    "deprecated": 1,
    "revoked": 0,
}

BLOCKER_CODES = {
    "run_rollforward_blocked",
    "run_rollback_required",
    "kill_switch_activated",
    "evaluator_conflict",
}


@dataclass(frozen=True)
class Criterion:
    id: str
    label: str
    threshold: float
    weight: float
    critical: bool


@dataclass(frozen=True)
class Thresholds:
    stability_consecutive_passes: int
    critical_non_regression: bool
    max_iterations: int
    max_elapsed_ms: int
    max_tokens: int
    no_improvement_escalation_limit: int


@dataclass(frozen=True)
class Profile:
    schema_version: str
    profile_id: str
    scope_skill: str
    scope_profile: str
    rubric_version: str
    evaluator_version: str
    persona_set_id: str
    thresholds: Thresholds
    criteria: List[Criterion]


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_unit_float(*parts: str) -> float:
    raw = "::".join(parts)
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def token_estimate(text: str) -> int:
    # Lightweight approximation for deterministic budgeting.
    return max(1, math.ceil(len(text) / 4))


def normalize_feedback(feedback_outcome: Optional[str], feedback_note: Optional[str]) -> Dict[str, str]:
    outcome_raw = (feedback_outcome or "").strip().lower()
    note = (feedback_note or "").strip()
    if outcome_raw and outcome_raw not in FEEDBACK_OUTCOMES:
        raise ValueError(f"Invalid feedback outcome: {feedback_outcome}")
    outcome = outcome_raw if outcome_raw else "missing"
    if len(note) > 500:
        note = note[:500]
    if outcome == "missing":
        note = ""
    return {
        "status": outcome,
        "note": note,
        "captured_at": iso_now(),
        "source": "cli_one_tap" if outcome_raw else "none",
    }


def build_evidence_packet(
    *,
    run_id: str,
    out_dir: Path,
    events_path: Path,
    iteration_journal_path: Path,
    run_obj: Dict[str, Any],
    promotion_decision: Dict[str, Any],
) -> Dict[str, Any]:
    debug_dir = out_dir / "debug"
    debug_files = sorted(str(p.relative_to(out_dir)) for p in debug_dir.glob("*") if p.is_file()) if debug_dir.exists() else []

    events_present = events_path.exists()
    traces_present = iteration_journal_path.exists()
    logs_present = len(debug_files) > 0

    sources: Dict[str, Any] = {
        "events": {
            "present": events_present,
            "path": str(events_path.relative_to(out_dir)) if events_present else "",
            "sha256": sha256_file(events_path) if events_present else "",
            "size_bytes": events_path.stat().st_size if events_present else 0,
        },
        "logs": {
            "present": logs_present,
            "paths": debug_files,
        },
        "traces": {
            "present": traces_present,
            "path": str(iteration_journal_path.relative_to(out_dir)) if traces_present else "",
            "sha256": sha256_file(iteration_journal_path) if traces_present else "",
            "size_bytes": iteration_journal_path.stat().st_size if traces_present else 0,
        },
        "session_signals": {
            "present": bool(run_obj.get("run_id")),
            "terminal_status": run_obj.get("terminal_status", ""),
            "stop_reason": run_obj.get("stop_reason", ""),
            "iterations_completed": int(run_obj.get("counters", {}).get("iterations_completed", 0)),
            "tokens_used": int(run_obj.get("counters", {}).get("tokens_used", 0)),
            "duration_ms": int(run_obj.get("duration_ms", 0)),
        },
        "checks": {
            "present": bool(promotion_decision.get("gate_decision")),
            "runtime_gates_passed": bool(
                promotion_decision.get("gate_decision", {}).get("runtime_gates_passed", False)
            ),
            "provenance_complete": bool(
                promotion_decision.get("gate_decision", {}).get("provenance_complete", False)
            ),
            "security_checklist_passed": bool(
                promotion_decision.get("gate_decision", {}).get("security_checklist_passed", False)
            ),
            "run_blocker_present": bool(run_obj.get("run_blocker")),
        },
    }

    completeness_flags = {
        "events": bool(sources["events"]["present"]),
        "logs": bool(sources["logs"]["present"]),
        "traces": bool(sources["traces"]["present"]),
        "session_signals": bool(sources["session_signals"]["present"]),
        "checks": bool(sources["checks"]["present"]),
    }
    completeness_score = round(sum(1 for ok in completeness_flags.values() if ok) / len(completeness_flags), 3)

    packet_seed = f"{run_id}:{run_obj.get('finished_at', '')}:{run_obj.get('terminal_status', '')}:evidence"
    return {
        "schema_version": "1.0",
        "evidence_packet_id": sha256_text(packet_seed)[:16],
        "run_id": run_id,
        "created_at": iso_now(),
        "sources": sources,
        "completeness": {
            **completeness_flags,
            "score": completeness_score,
        },
    }


def load_iteration_rows(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def quality_signal_from_uplift(uplift: float) -> float:
    if uplift >= 0.05:
        return 1.0
    if uplift >= 0.02:
        return 0.8
    if uplift >= 0.0:
        return 0.6
    if uplift >= -0.03:
        return 0.4
    return 0.2


def feedback_signal(status: str) -> float:
    table = {
        "worked": 1.0,
        "partly": 0.7,
        "didnt_work": 0.2,
        "missing": 0.5,
    }
    return table.get(status, 0.5)


def compute_confidence_assessment(
    *,
    run_obj: Dict[str, Any],
    promotion_decision: Dict[str, Any],
    evidence_packet: Dict[str, Any],
    feedback: Dict[str, str],
    iteration_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    initial_overall = 0.0
    final_overall = 0.0
    non_regression_all = True
    if iteration_rows:
        first = iteration_rows[0]
        last = iteration_rows[-1]
        initial_overall = float(first.get("evaluation_report", {}).get("overall_score", 0.0))
        final_overall = float(last.get("reevaluation_report", {}).get("overall_score", initial_overall))
        non_regression_all = all(
            bool(row.get("reevaluation_report", {}).get("non_regression_passed", False))
            for row in iteration_rows
        )

    quality_uplift = round(final_overall - initial_overall, 3)
    evidence_completeness = float(evidence_packet.get("completeness", {}).get("score", 0.0))
    runtime_gates_passed = bool(promotion_decision.get("gate_decision", {}).get("runtime_gates_passed", False))

    components = {
        "evidence_completeness": evidence_completeness,
        "runtime_gate_signal": 1.0 if runtime_gates_passed else 0.0,
        "non_regression_signal": 1.0 if non_regression_all else 0.0,
        "quality_uplift_signal": quality_signal_from_uplift(quality_uplift),
        "feedback_signal": feedback_signal(feedback.get("status", "missing")),
    }
    weights = {
        "evidence_completeness": 0.35,
        "runtime_gate_signal": 0.25,
        "non_regression_signal": 0.2,
        "quality_uplift_signal": 0.1,
        "feedback_signal": 0.1,
    }
    score = round(sum(components[k] * weights[k] for k in weights), 3)

    if score >= 0.8:
        bucket = "high"
        calibration_bucket = "C1_high_confidence"
    elif score >= 0.6:
        bucket = "medium"
        calibration_bucket = "C2_medium_confidence"
    else:
        bucket = "low"
        calibration_bucket = "C3_low_confidence"

    return {
        "schema_version": "1.0",
        "score": score,
        "bucket": bucket,
        "calibration_bucket": calibration_bucket,
        "quality_uplift": quality_uplift,
        "inputs": {
            **components,
            "feedback_status": feedback.get("status", "missing"),
            "iterations_observed": len(iteration_rows),
            "terminal_status": str(run_obj.get("terminal_status", "")),
            "stop_reason": str(run_obj.get("stop_reason", "")),
        },
    }


def build_lesson_candidates(
    *,
    run_id: str,
    profile: Profile,
    iteration_rows: List[Dict[str, Any]],
    run_obj: Dict[str, Any],
    feedback: Dict[str, str],
    confidence: Dict[str, Any],
    evidence_packet: Dict[str, Any],
) -> List[Dict[str, Any]]:
    if not iteration_rows:
        return []

    latest = iteration_rows[-1]
    iteration_id = int(latest.get("iteration_id", len(iteration_rows)))
    diagnosis = latest.get("diagnosis", {}) if isinstance(latest.get("diagnosis"), dict) else {}
    action = latest.get("improvement_action", {}) if isinstance(latest.get("improvement_action"), dict) else {}
    deltas = latest.get("criterion_deltas", {}) if isinstance(latest.get("criterion_deltas"), dict) else {}
    positive_deltas = {
        str(k): float(v)
        for k, v in deltas.items()
        if isinstance(v, (int, float)) and float(v) > 0
    }

    weakest = diagnosis.get("weakest_criteria", [])
    if isinstance(weakest, list):
        weakest_text = ", ".join(str(w) for w in weakest if str(w).strip())
    else:
        weakest_text = ""

    candidate_id_seed = f"{run_id}:{profile.profile_id}:{iteration_id}:candidate"
    candidate_id = f"candidate_{sha256_text(candidate_id_seed)[:12]}"
    terminal_status = str(run_obj.get("terminal_status", ""))

    advice_summary = str(diagnosis.get("reason", "")).strip() or "No diagnosis summary available."
    implementation_summary = str(action.get("summary", "")).strip() or "No improvement action summary available."

    candidate = {
        "schema_version": "1.0",
        "candidate_id": candidate_id,
        "run_id": run_id,
        "profile_id": profile.profile_id,
        "scope_skill": profile.scope_skill,
        "scope_profile": profile.scope_profile,
        "iteration_id": iteration_id,
        "created_at": iso_now(),
        "status": "candidate",
        "advice": {
            "summary": advice_summary,
            "weakest_criteria": weakest if isinstance(weakest, list) else [],
        },
        "implementation": {
            "summary": implementation_summary,
            "positive_criterion_deltas": positive_deltas,
        },
        "outcome": {
            "terminal_status": terminal_status,
            "stop_reason": str(run_obj.get("stop_reason", "")),
            "feedback_status": feedback.get("status", "missing"),
            "feedback_note": feedback.get("note", ""),
            "quality_uplift": float(confidence.get("quality_uplift", 0.0)),
        },
        "confidence": {
            "score": float(confidence.get("score", 0.0)),
            "bucket": str(confidence.get("bucket", "low")),
            "calibration_bucket": str(confidence.get("calibration_bucket", "C3_low_confidence")),
            "evidence_completeness": float(evidence_packet.get("completeness", {}).get("score", 0.0)),
        },
        "evidence_refs": {
            "iteration_journal_path": "iteration_journal.jsonl",
            "events_path": "events.jsonl",
            "evidence_packet_path": "evidence_packet.json",
        },
        "title": (
            f"{profile.scope_skill} remediation candidate"
            + (f" ({weakest_text})" if weakest_text else "")
        ),
    }
    return [candidate]


def parse_lesson_effective_from(value: Any) -> float:
    raw = str(value or "").strip()
    if not raw:
        return 0.0
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).timestamp()
    except Exception:
        return 0.0


def load_canonical_lessons(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def retrieve_and_rank_lessons(
    *,
    profile: Profile,
    lessons_file: Path,
    max_lessons: int,
    low_confidence_threshold: float,
) -> Dict[str, Any]:
    all_rows = load_canonical_lessons(lessons_file)
    scoped: List[Dict[str, Any]] = []
    for row in all_rows:
        scope_skill = str(row.get("scope_skill", "")).strip()
        scope_profile = str(row.get("scope_profile", "")).strip()
        if scope_skill != profile.scope_skill or scope_profile != profile.scope_profile:
            continue
        status = str(row.get("status", "")).strip().lower()
        if status in {"revoked"}:
            continue
        scoped.append(row)

    ranked: List[Dict[str, Any]] = []
    for row in scoped:
        lesson_id = str(row.get("lesson_id", "")).strip()
        status = str(row.get("status", "promoted")).strip().lower() or "promoted"
        confidence = float(row.get("confidence", 0.0) or 0.0)
        effective_from_ts = parse_lesson_effective_from(row.get("effective_from"))
        status_priority = LESSON_STATUS_PRIORITY.get(status, 2)
        low_confidence = confidence < low_confidence_threshold
        confidence_adjusted = confidence - (0.15 if low_confidence else 0.0)
        ranking_score = round(status_priority * 10.0 + confidence_adjusted, 4)
        ranked.append(
            {
                "lesson_id": lesson_id,
                "status": status,
                "confidence": round(confidence, 3),
                "status_priority": status_priority,
                "effective_from": str(row.get("effective_from", "")),
                "effective_from_ts": effective_from_ts,
                "low_confidence_flag": low_confidence,
                "warning": (
                    "low_confidence_downranked" if low_confidence else ""
                ),
                "ranking_score": ranking_score,
            }
        )

    ranked.sort(
        key=lambda x: (
            float(x["ranking_score"]),
            float(x["effective_from_ts"]),
            str(x["lesson_id"]),
        ),
        reverse=True,
    )
    selected = ranked[: max(0, max_lessons)]
    injection_text = ""
    if selected:
        lines = ["[Injected canonical lessons]"]
        for item in selected:
            warn = f" ⚠ {item['warning']}" if item["warning"] else ""
            lines.append(
                f"- lesson_id={item['lesson_id']} status={item['status']} confidence={item['confidence']:.3f}{warn}"
            )
        injection_text = "\n".join(lines)

    return {
        "schema_version": "1.0",
        "lessons_file": str(lessons_file),
        "scoped_count": len(scoped),
        "selected_count": len(selected),
        "low_confidence_threshold": low_confidence_threshold,
        "selected": selected,
        "injection_text": injection_text,
    }


def load_profile(path: Path) -> Profile:
    obj = json.loads(path.read_text(encoding="utf-8"))

    for field in (
        "schema_version",
        "profile_id",
        "scope_skill",
        "scope_profile",
        "rubric_version",
        "evaluator_version",
        "persona_set_id",
        "thresholds",
        "criteria",
    ):
        if field not in obj:
            raise ValueError(f"Profile missing required field: {field}")

    t = obj["thresholds"]
    thresholds = Thresholds(
        stability_consecutive_passes=int(t.get("stability_consecutive_passes", 1)),
        critical_non_regression=bool(t.get("critical_non_regression", True)),
        max_iterations=int(t.get("max_iterations", 4)),
        max_elapsed_ms=int(t.get("max_elapsed_ms", 120000)),
        max_tokens=int(t.get("max_tokens", 12000)),
        no_improvement_escalation_limit=int(t.get("no_improvement_escalation_limit", 2)),
    )

    criteria: List[Criterion] = []
    for idx, c in enumerate(obj["criteria"], start=1):
        try:
            criterion = Criterion(
                id=str(c["id"]),
                label=str(c.get("label") or c["id"]),
                threshold=float(c["threshold"]),
                weight=float(c["weight"]),
                critical=bool(c.get("critical", False)),
            )
        except KeyError as exc:
            raise ValueError(f"Criterion #{idx} missing field: {exc}") from exc
        criteria.append(criterion)

    if not criteria:
        raise ValueError("Profile must include at least one criterion")

    total_weight = sum(max(0.0, c.weight) for c in criteria)
    if total_weight <= 0:
        raise ValueError("At least one criterion must have positive weight")

    return Profile(
        schema_version=str(obj["schema_version"]),
        profile_id=str(obj["profile_id"]),
        scope_skill=str(obj["scope_skill"]),
        scope_profile=str(obj["scope_profile"]),
        rubric_version=str(obj["rubric_version"]),
        evaluator_version=str(obj["evaluator_version"]),
        persona_set_id=str(obj["persona_set_id"]),
        thresholds=thresholds,
        criteria=criteria,
    )


def evaluate_candidate(
    *,
    profile: Profile,
    objective: str,
    candidate: str,
    iteration_id: int,
    improved: bool,
    seed: int,
) -> Dict[str, Any]:
    scores: Dict[str, float] = {}
    findings: List[Dict[str, str]] = []

    for c in profile.criteria:
        deterministic = stable_unit_float(profile.profile_id, c.id, str(seed), candidate[:240])
        iteration_gain = 0.07 * (iteration_id - 1)
        improve_gain = 0.05 if improved else 0.0
        base_floor = 0.62 if c.critical else 0.55
        criterion_bias = 0.04 if c.id == "safety" else 0.0
        base = base_floor + criterion_bias + (0.18 * deterministic)
        score = clamp(base + iteration_gain + improve_gain, 0.0, 0.99)
        score = round(score, 3)
        scores[c.id] = score

        deficit = round(c.threshold - score, 3)
        if deficit > 0:
            severity = "fail" if c.critical and deficit >= 0.1 else "warn"
            findings.append(
                {
                    "severity": severity,
                    "criterion_id": c.id,
                    "message": f"{c.id} below threshold by {deficit:.3f}",
                }
            )

    total_weight = sum(c.weight for c in profile.criteria)
    overall = sum(scores[c.id] * c.weight for c in profile.criteria) / total_weight

    checkpoint_adversarial = iteration_id == 1
    if any(f["severity"] == "fail" for f in findings):
        checkpoint_adversarial = True

    return {
        "judge_mode": "standard",
        "adversarial_checkpoint_triggered": checkpoint_adversarial,
        "scores": scores,
        "overall_score": round(overall, 3),
        "findings": findings,
        "eligible_for_gate_check": True,
        "objective_hash": sha256_text(objective),
    }


def diagnose(profile: Profile, report: Dict[str, Any]) -> Dict[str, Any]:
    deficits: List[Tuple[str, float]] = []
    scores = report["scores"]

    for c in profile.criteria:
        deficits.append((c.id, round(c.threshold - scores[c.id], 3)))

    deficits.sort(key=lambda x: x[1], reverse=True)
    weakest = [criterion_id for criterion_id, d in deficits if d > 0][:3]

    if not weakest:
        reason = "No criterion deficit detected; keep response concise and verifiable."
    else:
        reason = "Strengthen concrete examples, file-path specificity, and measurable checks."

    return {
        "weakest_criteria": weakest,
        "reason": reason,
        "deficits": {cid: d for cid, d in deficits},
    }


def improve(candidate: str, diagnosis_obj: Dict[str, Any], iteration_id: int) -> Dict[str, Any]:
    weakest = diagnosis_obj.get("weakest_criteria", [])
    focus = ", ".join(weakest) if weakest else "consistency"
    suffix = (
        f"\n\n[Improvement pass {iteration_id}] "
        f"Focus criteria: {focus}. "
        "Add explicit paths, pass/fail checks, and hard-stop conditions."
    )
    improved = candidate + suffix

    return {
        "action_type": "tighten_constraints",
        "summary": f"Applied focused remediation for: {focus}",
        "candidate": improved,
    }


def check_non_regression(
    *,
    profile: Profile,
    baseline_scores: Dict[str, float],
    candidate_scores: Dict[str, float],
    epsilon: float = 1e-6,
) -> Tuple[bool, List[str]]:
    regressions: List[str] = []
    for c in profile.criteria:
        if not c.critical:
            continue
        if candidate_scores[c.id] + epsilon < baseline_scores[c.id]:
            regressions.append(c.id)
    return (len(regressions) == 0, regressions)


def pass_thresholds(profile: Profile, scores: Dict[str, float]) -> bool:
    for c in profile.criteria:
        if scores[c.id] < c.threshold:
            return False
    return True


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True))
            f.write("\n")


def append_jsonl(path: Path, row: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True))
        f.write("\n")


def emit_event(
    *,
    events: List[Dict[str, Any]],
    run_id: str,
    profile: Profile,
    actor_id: str,
    objective_hash: str,
    event_type: str,
    severity: str,
    terminal_status: Optional[str],
    stop_reason: Optional[str],
    blocker_code: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    seed = f"{run_id}:{event_type}:{terminal_status}:{stop_reason}:{blocker_code}:{len(events)}"
    event: Dict[str, Any] = {
        "schema_version": "1.0",
        "event_id": sha256_text(seed)[:16],
        "ts": iso_now(),
        "run_id": run_id,
        "skill_name": profile.scope_skill,
        "task_profile": profile.profile_id,
        "event_type": event_type,
        "severity": severity,
        "terminal_status": terminal_status,
        "stop_reason": stop_reason,
        "actor_id": actor_id,
        "evaluator_version": profile.evaluator_version,
        "rubric_version": profile.rubric_version,
        "prompt_hash": objective_hash,
    }
    if blocker_code:
        event["blocker_code"] = blocker_code
    if extra:
        event.update(extra)
    events.append(event)


def normalize_blocked_reason(blocker_code: str) -> Tuple[str, str]:
    if blocker_code == "run_rollforward_blocked":
        return ("failed", "policy_failed")
    if blocker_code == "run_rollback_required":
        return ("failed", "dependency_missing")
    if blocker_code == "evaluator_conflict":
        return ("escalated", "evaluator_conflict")
    if blocker_code == "kill_switch_activated":
        return ("aborted", "aborted")
    return ("failed", "policy_failed")


def is_kill_switch_activated(path: Optional[Path]) -> bool:
    if path is None or not path.exists():
        return False
    try:
        raw = path.read_text(encoding="utf-8", errors="ignore").strip().lower()
    except Exception:
        return True
    if raw in {"", "1", "true", "yes", "on", "kill", "stop"}:
        return True
    return raw not in {"0", "false", "off", "no"}


def normalize_rollout_mode(raw_mode: Optional[str]) -> str:
    mode = str(raw_mode or "").strip().lower()
    return mode if mode in ROLLOUT_MODES else "observe_only"


def read_rollout_mode(path: Optional[Path], fallback: str) -> str:
    if path is None or not path.exists():
        return fallback
    try:
        return normalize_rollout_mode(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return fallback


def acquire_run_lock(lock_path: Path, run_id: str, run_owner: str, idempotency_key: str) -> None:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run_id,
        "run_owner": run_owner,
        "idempotency_key": idempotency_key,
        "created_at": iso_now(),
    }
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    fd = os.open(lock_path, flags)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(payload, sort_keys=True))
        f.write("\n")


def release_run_lock(lock_path: Path, run_id: str) -> None:
    if not lock_path.exists():
        return
    try:
        payload = json.loads(lock_path.read_text(encoding="utf-8"))
        if str(payload.get("run_id", "")) != run_id:
            return
    except Exception:
        return
    try:
        lock_path.unlink()
    except FileNotFoundError:
        return


def evaluate_candidate_adversarial(
    *,
    profile: Profile,
    objective: str,
    candidate: str,
    iteration_id: int,
    seed: int,
    checkpoint_reason: str,
) -> Dict[str, Any]:
    base = evaluate_candidate(
        profile=profile,
        objective=objective,
        candidate=candidate,
        iteration_id=iteration_id,
        improved=True,
        seed=seed,
    )
    penalty_scale = 0.08 if checkpoint_reason == "initial" else 0.11
    adjusted_scores: Dict[str, float] = {}
    findings: List[Dict[str, str]] = list(base.get("findings", []))

    for c in profile.criteria:
        deterministic = stable_unit_float(profile.profile_id, c.id, "adversarial", str(seed))
        penalty = round(penalty_scale * (0.6 + deterministic), 3)
        adjusted = clamp(float(base["scores"][c.id]) - penalty, 0.0, 0.99)
        adjusted_scores[c.id] = round(adjusted, 3)
        deficit = round(c.threshold - adjusted_scores[c.id], 3)
        if deficit > 0:
            findings.append(
                {
                    "severity": "fail" if c.critical or deficit >= 0.08 else "warn",
                    "criterion_id": c.id,
                    "message": f"adversarial: {c.id} below threshold by {deficit:.3f}",
                }
            )

    total_weight = sum(c.weight for c in profile.criteria)
    overall = sum(adjusted_scores[c.id] * c.weight for c in profile.criteria) / total_weight
    return {
        "judge_mode": "adversarial",
        "checkpoint_reason": checkpoint_reason,
        "scores": adjusted_scores,
        "overall_score": round(overall, 3),
        "findings": findings,
        "eligible_for_gate_check": True,
        "objective_hash": sha256_text(objective),
    }


def run_loop(args: argparse.Namespace) -> int:
    profile = load_profile(Path(args.profile_file).resolve())

    run_seed = args.seed if args.seed is not None else int(stable_unit_float(args.objective, profile.profile_id) * 10_000_000)
    rng = random.Random(run_seed)

    run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{sha256_text(profile.profile_id + args.objective)[:6]}"
    out_dir = Path(args.out_root).resolve() / run_id
    out_root = Path(args.out_root).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    debug_dir = out_dir / "debug"
    if args.emit_debug_artifacts:
        debug_dir.mkdir(parents=True, exist_ok=True)

    events_path = out_dir / "events.jsonl"
    iteration_journal_path = out_dir / "iteration_journal.jsonl"
    started_at = time.time()
    created_at = iso_now()
    objective_hash = sha256_text(args.objective)
    feedback_payload = normalize_feedback(args.feedback_outcome, args.feedback_note)
    invocation_id = sha256_text(f"{objective_hash}:{args.actor_id}:{created_at}")[:16]

    max_iterations = args.max_iterations or profile.thresholds.max_iterations
    max_elapsed_ms = args.max_elapsed_ms or profile.thresholds.max_elapsed_ms
    max_tokens = args.max_tokens or profile.thresholds.max_tokens

    run_owner = str(args.run_owner).strip()
    idempotency_key = (
        str(args.idempotency_key).strip()
        if args.idempotency_key
        else sha256_text(f"{profile.profile_id}:{args.objective}:{run_owner}")[:20]
    )
    lock_path = (
        Path(args.run_lock).resolve()
        if args.run_lock
        else out_root / ".locks" / f"{profile.profile_id}.lock"
    )
    kill_switch_raw = (
        str(args.kill_switch_file).strip()
        if args.kill_switch_file
        else str(os.environ.get("SKILL_GRAPH_KILL_SWITCH_PATH", "")).strip()
    )
    kill_switch_path = Path(kill_switch_raw).expanduser().resolve() if kill_switch_raw else None
    rollback_required_raw = (
        str(args.rollback_required_file).strip()
        if args.rollback_required_file
        else str(os.environ.get("SKILL_GRAPH_ROLLBACK_REQUIRED_PATH", "")).strip()
    )
    rollback_required_path = Path(rollback_required_raw).expanduser().resolve() if rollback_required_raw else None
    controls_dir_raw = str(
        args.controls_dir
        or os.environ.get("SKILL_GRAPH_CONTROLS_DIR")
        or "artifacts/skill-graphs/controls"
    ).strip()
    controls_dir = Path(controls_dir_raw).expanduser().resolve()
    skill_controls_dir_raw = (
        str(args.skill_controls_dir).strip()
        if args.skill_controls_dir
        else str(os.environ.get("SKILL_GRAPH_SKILL_CONTROLS_DIR", "")).strip()
    )
    skill_controls_dir = (
        Path(skill_controls_dir_raw).expanduser().resolve()
        if skill_controls_dir_raw
        else controls_dir / "skills"
    )
    rollout_mode_file_raw = (
        str(args.rollout_mode_file).strip()
        if args.rollout_mode_file
        else str(os.environ.get("SKILL_GRAPH_ROLLOUT_MODE_PATH", "")).strip()
    )
    rollout_mode_file = (
        Path(rollout_mode_file_raw).expanduser().resolve()
        if rollout_mode_file_raw
        else controls_dir / "rollout-mode.txt"
    )
    rollout_mode = (
        normalize_rollout_mode(args.rollout_mode)
        if args.rollout_mode
        else read_rollout_mode(
            rollout_mode_file,
            normalize_rollout_mode(os.environ.get("SKILL_GRAPH_ROLLOUT_MODE")),
        )
    )

    auto_capture_switch_raw = (
        str(args.auto_capture_switch_file).strip()
        if args.auto_capture_switch_file
        else str(os.environ.get("SKILL_GRAPH_AUTO_CAPTURE_SWITCH_PATH", "")).strip()
    )
    auto_capture_switch_path = (
        Path(auto_capture_switch_raw).expanduser().resolve()
        if auto_capture_switch_raw
        else controls_dir / "auto_capture.disabled"
    )
    auto_apply_switch_raw = (
        str(args.auto_apply_switch_file).strip()
        if args.auto_apply_switch_file
        else str(os.environ.get("SKILL_GRAPH_AUTO_APPLY_SWITCH_PATH", "")).strip()
    )
    auto_apply_switch_path = (
        Path(auto_apply_switch_raw).expanduser().resolve()
        if auto_apply_switch_raw
        else controls_dir / "auto_apply.disabled"
    )
    skill_auto_capture_switch_path = skill_controls_dir / profile.scope_skill / "auto_capture.disabled"
    skill_auto_apply_switch_path = skill_controls_dir / profile.scope_skill / "auto_apply.disabled"

    control_reasons: List[str] = []
    auto_capture_enabled = rollout_mode != "off"
    if rollout_mode == "off":
        control_reasons.append("rollout_mode_off_disables_auto_capture")
    if is_kill_switch_activated(auto_capture_switch_path):
        auto_capture_enabled = False
        control_reasons.append("global_auto_capture_kill_switch")
    if is_kill_switch_activated(skill_auto_capture_switch_path):
        auto_capture_enabled = False
        control_reasons.append("skill_auto_capture_kill_switch")

    auto_apply_enabled = rollout_mode == "active"
    if rollout_mode != "active":
        control_reasons.append(f"rollout_mode_{rollout_mode}_disables_auto_apply")
    if is_kill_switch_activated(auto_apply_switch_path):
        auto_apply_enabled = False
        control_reasons.append("global_auto_apply_kill_switch")
    if is_kill_switch_activated(skill_auto_apply_switch_path):
        auto_apply_enabled = False
        control_reasons.append("skill_auto_apply_kill_switch")

    runtime_controls = {
        "schema_version": "1.0",
        "rollout_mode": rollout_mode,
        "auto_capture_enabled": auto_capture_enabled,
        "auto_apply_enabled": auto_apply_enabled,
        "reasons": sorted(set(control_reasons)),
        "paths": {
            "controls_dir": str(controls_dir),
            "skill_controls_dir": str(skill_controls_dir),
            "rollout_mode_file": str(rollout_mode_file),
            "global_auto_capture_switch_file": str(auto_capture_switch_path),
            "global_auto_apply_switch_file": str(auto_apply_switch_path),
            "skill_auto_capture_switch_file": str(skill_auto_capture_switch_path),
            "skill_auto_apply_switch_file": str(skill_auto_apply_switch_path),
        },
    }

    lessons_file = Path(args.lessons_jsonl).expanduser().resolve()
    injection_context = retrieve_and_rank_lessons(
        profile=profile,
        lessons_file=lessons_file,
        max_lessons=args.max_injected_lessons,
        low_confidence_threshold=args.low_confidence_threshold,
    )
    retrieved_lessons = injection_context["selected"]
    injected_lessons = list(retrieved_lessons if auto_apply_enabled else [])
    if not auto_apply_enabled:
        injection_context["injection_text"] = ""

    events: List[Dict[str, Any]] = []
    emit_event(
        events=events,
        run_id=run_id,
        profile=profile,
        actor_id=args.actor_id,
        objective_hash=objective_hash,
        event_type="run_initialized",
        severity="info",
        terminal_status=None,
        stop_reason=None,
        extra={
            "run_owner": run_owner,
            "idempotency_key": idempotency_key,
            "rollout_mode": rollout_mode,
            "auto_capture_enabled": auto_capture_enabled,
            "auto_apply_enabled": auto_apply_enabled,
            "retrieved_lesson_ids": [item["lesson_id"] for item in retrieved_lessons],
            "injected_lesson_ids": [item["lesson_id"] for item in injected_lessons],
        },
    )
    write_jsonl(iteration_journal_path, [])

    def write_capture_artifacts(run_obj: Dict[str, Any], promotion_decision: Dict[str, Any]) -> None:
        if not auto_capture_enabled:
            return
        iteration_rows = load_iteration_rows(iteration_journal_path)
        evidence_packet = build_evidence_packet(
            run_id=run_id,
            out_dir=out_dir,
            events_path=events_path,
            iteration_journal_path=iteration_journal_path,
            run_obj=run_obj,
            promotion_decision=promotion_decision,
        )
        evidence_packet_path = out_dir / "evidence_packet.json"
        write_json(evidence_packet_path, evidence_packet)
        confidence = compute_confidence_assessment(
            run_obj=run_obj,
            promotion_decision=promotion_decision,
            evidence_packet=evidence_packet,
            feedback=feedback_payload,
            iteration_rows=iteration_rows,
        )
        lesson_candidates = build_lesson_candidates(
            run_id=run_id,
            profile=profile,
            iteration_rows=iteration_rows,
            run_obj=run_obj,
            feedback=feedback_payload,
            confidence=confidence,
            evidence_packet=evidence_packet,
        )

        capture_seed = f"{run_id}:{run_obj.get('finished_at', '')}:{run_obj.get('terminal_status', '')}:capture"
        capture_record = {
            "schema_version": "1.0",
            "capture_id": sha256_text(capture_seed)[:16],
            "run_id": run_id,
            "profile_id": profile.profile_id,
            "scope_skill": profile.scope_skill,
            "scope_profile": profile.scope_profile,
            "created_at": iso_now(),
            "invocation_envelope": {
                "invocation_id": invocation_id,
                "invoked_at": created_at,
                "actor_id": args.actor_id,
                "run_owner": run_owner,
                "objective_hash": objective_hash,
                "idempotency_key": idempotency_key,
                "kill_switch_file": str(kill_switch_path) if kill_switch_path else "",
                "rollback_required_file": str(rollback_required_path) if rollback_required_path else "",
                "rollout_mode": rollout_mode,
                "auto_capture_enabled": auto_capture_enabled,
                "auto_apply_enabled": auto_apply_enabled,
            },
            "output_summary": {
                "finished_at": run_obj.get("finished_at", ""),
                "terminal_status": run_obj.get("terminal_status", ""),
                "stop_reason": run_obj.get("stop_reason", ""),
                "iterations_completed": int(run_obj.get("counters", {}).get("iterations_completed", 0)),
                "tokens_used": int(run_obj.get("counters", {}).get("tokens_used", 0)),
                "duration_ms": int(run_obj.get("duration_ms", 0)),
            },
            "feedback": feedback_payload,
            "evidence": {
                "evidence_packet_id": evidence_packet["evidence_packet_id"],
                "evidence_packet_path": str(evidence_packet_path.relative_to(out_dir)),
                "completeness": evidence_packet["completeness"],
            },
            "confidence": confidence,
            "candidate_lessons": {
                "count": len(lesson_candidates),
                "top_candidate_id": lesson_candidates[0]["candidate_id"] if lesson_candidates else "",
            },
            "injected_lessons": {
                "count": len(injected_lessons),
                "items": injected_lessons,
            },
        }
        write_json(out_dir / "capture_record.json", capture_record)
        write_json(out_dir / "lesson_candidates.json", {"schema_version": "1.0", "run_id": run_id, "items": lesson_candidates})

        promotion_decision["confidence"] = {
            "schema_version": "1.0",
            "score": confidence["score"],
            "bucket": confidence["bucket"],
            "calibration_bucket": confidence["calibration_bucket"],
            "quality_uplift": confidence["quality_uplift"],
            "evidence_completeness": evidence_packet["completeness"]["score"],
        }
        promotion_decision["evidence_packet"] = {
            "evidence_packet_id": evidence_packet["evidence_packet_id"],
            "completeness_score": evidence_packet["completeness"]["score"],
        }
        promotion_decision["lesson_candidates"] = lesson_candidates
        write_json(out_dir / "promotion_decision.json", promotion_decision)

    def write_blocker_artifacts(
        *,
        blocker_code: str,
        message: str,
        terminal_status: str,
        stop_reason: str,
    ) -> None:
        blocker = {
            "schema_version": "1.0",
            "run_id": run_id,
            "code": blocker_code,
            "message": message,
            "remediation_owner": run_owner,
            "created_at": iso_now(),
        }
        write_json(out_dir / "run_blocker.json", blocker)
        if blocker_code in {"kill_switch_activated", "run_rollback_required", "run_rollforward_blocked"}:
            write_json(
                out_dir / "rollback_recommendation.json",
                {
                    "schema_version": "1.0",
                    "run_id": run_id,
                    "reason": blocker_code,
                    "owner": run_owner,
                    "recommended_actions": [
                        "review run_blocker.json",
                        "confirm canonical lesson/index unchanged",
                        "rerun with corrected lock/policy inputs",
                    ],
                    "created_at": iso_now(),
                },
            )

        run_obj = {
            "schema_version": profile.schema_version,
            "run_id": run_id,
            "profile_id": profile.profile_id,
            "scope_skill": profile.scope_skill,
            "scope_profile": profile.scope_profile,
            "terminal_status": terminal_status,
            "stop_reason": stop_reason,
            "started_at": created_at,
            "finished_at": iso_now(),
            "duration_ms": int((time.time() - started_at) * 1000),
            "budget": {
                "max_iterations": max_iterations,
                "max_elapsed_ms": max_elapsed_ms,
                "max_tokens": max_tokens,
            },
            "counters": {
                "iterations_completed": 0,
                "tokens_used": 0,
                "consecutive_passes": 0,
            },
            "versions": {
                "rubric_version": profile.rubric_version,
                "evaluator_version": profile.evaluator_version,
                "persona_set_id": profile.persona_set_id,
            },
            "prompt_hash": objective_hash,
            "created_by": args.actor_id,
            "run_owner": run_owner,
            "idempotency_key": idempotency_key,
            "lock_path": str(lock_path),
            "kill_switch_file": str(kill_switch_path) if kill_switch_path else "",
            "rollback_required_file": str(rollback_required_path) if rollback_required_path else "",
            "runtime_controls": runtime_controls,
            "injection_summary": {
                "lessons_file": str(lessons_file),
                "retrieved_count": len(retrieved_lessons),
                "selected_count": len(injected_lessons),
                "selected_lesson_ids": [item["lesson_id"] for item in injected_lessons],
                "low_confidence_threshold": args.low_confidence_threshold,
                "suppressed_by_controls": (not auto_apply_enabled and len(retrieved_lessons) > 0),
            },
            "injected_lessons": injected_lessons,
            "retrieved_lessons": retrieved_lessons,
            "run_blocker": blocker,
        }
        promotion_decision = {
            "schema_version": profile.schema_version,
            "run_id": run_id,
            "lesson_id": "",
            "decision": "draft",
            "reviewer_ids": [],
            "expected_version": "",
            "lesson_status": "",
            "lesson_effective_to": None,
            "gate_decision": {
                "runtime_gates_passed": False,
                "provenance_complete": False,
                "security_checklist_passed": False,
                "notes": message,
            },
            "provenance": {
                "prompt_hash": objective_hash,
                "rubric_version": profile.rubric_version,
                "evaluator_version": profile.evaluator_version,
                "iteration_ids": [],
            },
            "injected_lesson_ids": [item["lesson_id"] for item in injected_lessons],
            "runtime_controls": runtime_controls,
            "run_blocker": blocker,
        }
        write_json(out_dir / "run.json", run_obj)
        write_jsonl(iteration_journal_path, [])
        write_json(out_dir / "promotion_decision.json", promotion_decision)
        write_jsonl(events_path, events)
        write_capture_artifacts(run_obj, promotion_decision)

    if rollout_mode == "off":
        blocker_code = "run_rollforward_blocked"
        terminal_status, stop_reason = normalize_blocked_reason(blocker_code)
        emit_event(
            events=events,
            run_id=run_id,
            profile=profile,
            actor_id=args.actor_id,
            objective_hash=objective_hash,
            event_type="run_blocked",
            severity="warn",
            terminal_status=terminal_status,
            stop_reason=stop_reason,
            blocker_code=blocker_code,
            extra={"message": f"rollout mode is off via {rollout_mode_file}"},
        )
        emit_event(
            events=events,
            run_id=run_id,
            profile=profile,
            actor_id=args.actor_id,
            objective_hash=objective_hash,
            event_type="run_state_changed",
            severity="warn",
            terminal_status=terminal_status,
            stop_reason=stop_reason,
            blocker_code=blocker_code,
        )
        emit_event(
            events=events,
            run_id=run_id,
            profile=profile,
            actor_id=args.actor_id,
            objective_hash=objective_hash,
            event_type="failure_event",
            severity="fail",
            terminal_status=terminal_status,
            stop_reason=stop_reason,
            blocker_code=blocker_code,
        )
        write_blocker_artifacts(
            blocker_code=blocker_code,
            message=f"rollout mode is off ({rollout_mode}); run blocked before execution",
            terminal_status=terminal_status,
            stop_reason=stop_reason,
        )
        write_jsonl(events_path, events)
        print(f"[recursive-loop] run_id={run_id}")
        print(f"[recursive-loop] status={terminal_status} stop_reason={stop_reason}")
        print(f"[recursive-loop] out_dir={out_dir}")
        return 5

    if is_kill_switch_activated(rollback_required_path):
        blocker_code = "run_rollback_required"
        terminal_status, stop_reason = normalize_blocked_reason(blocker_code)
        emit_event(
            events=events,
            run_id=run_id,
            profile=profile,
            actor_id=args.actor_id,
            objective_hash=objective_hash,
            event_type="run_blocked",
            severity="warn",
            terminal_status=terminal_status,
            stop_reason=stop_reason,
            blocker_code=blocker_code,
            extra={"message": f"rollback required control active: {rollback_required_path}"},
        )
        emit_event(
            events=events,
            run_id=run_id,
            profile=profile,
            actor_id=args.actor_id,
            objective_hash=objective_hash,
            event_type="run_state_changed",
            severity="warn",
            terminal_status=terminal_status,
            stop_reason=stop_reason,
            blocker_code=blocker_code,
        )
        emit_event(
            events=events,
            run_id=run_id,
            profile=profile,
            actor_id=args.actor_id,
            objective_hash=objective_hash,
            event_type="failure_event",
            severity="fail",
            terminal_status=terminal_status,
            stop_reason=stop_reason,
            blocker_code=blocker_code,
        )
        write_blocker_artifacts(
            blocker_code=blocker_code,
            message=f"rollback required control active at {rollback_required_path}",
            terminal_status=terminal_status,
            stop_reason=stop_reason,
        )
        write_jsonl(events_path, events)
        print(f"[recursive-loop] run_id={run_id}")
        print(f"[recursive-loop] status={terminal_status} stop_reason={stop_reason}")
        print(f"[recursive-loop] out_dir={out_dir}")
        return 5

    try:
        acquire_run_lock(lock_path, run_id, run_owner, idempotency_key)
    except FileExistsError:
        blocker_code = "run_rollforward_blocked"
        terminal_status, stop_reason = normalize_blocked_reason(blocker_code)
        emit_event(
            events=events,
            run_id=run_id,
            profile=profile,
            actor_id=args.actor_id,
            objective_hash=objective_hash,
            event_type="run_blocked",
            severity="warn",
            terminal_status=terminal_status,
            stop_reason=stop_reason,
            blocker_code=blocker_code,
            extra={"message": f"lock already exists: {lock_path}"},
        )
        emit_event(
            events=events,
            run_id=run_id,
            profile=profile,
            actor_id=args.actor_id,
            objective_hash=objective_hash,
            event_type="run_state_changed",
            severity="warn",
            terminal_status=terminal_status,
            stop_reason=stop_reason,
            blocker_code=blocker_code,
        )
        emit_event(
            events=events,
            run_id=run_id,
            profile=profile,
            actor_id=args.actor_id,
            objective_hash=objective_hash,
            event_type="failure_event",
            severity="fail",
            terminal_status=terminal_status,
            stop_reason=stop_reason,
            blocker_code=blocker_code,
        )
        write_blocker_artifacts(
            blocker_code=blocker_code,
            message=f"run lock exists at {lock_path}; run blocked",
            terminal_status=terminal_status,
            stop_reason=stop_reason,
        )
        write_jsonl(events_path, events)
        print(f"[recursive-loop] run_id={run_id}")
        print(f"[recursive-loop] status={terminal_status} stop_reason={stop_reason}")
        print(f"[recursive-loop] out_dir={out_dir}")
        return 5

    journal_iteration_ids: List[int] = []
    iterations_completed = 0
    candidate = args.objective.strip()
    if injection_context["injection_text"]:
        candidate = candidate + "\n\n" + injection_context["injection_text"]
    total_tokens = 0
    consecutive_passes = 0
    no_improvement_count = 0
    last_overall: Optional[float] = None
    baseline_scores: Optional[Dict[str, float]] = None
    best_accepted_scores: Optional[Dict[str, float]] = None
    terminal_status = "failed"
    stop_reason = "budget_exhausted"
    blocker_code: Optional[str] = None

    try:
        for iteration_id in range(1, max_iterations + 1):
            if is_kill_switch_activated(rollback_required_path):
                blocker_code = "run_rollback_required"
                terminal_status, stop_reason = normalize_blocked_reason(blocker_code)
                break

            if is_kill_switch_activated(kill_switch_path):
                blocker_code = "kill_switch_activated"
                terminal_status, stop_reason = normalize_blocked_reason(blocker_code)
                break

            now_ms = int((time.time() - started_at) * 1000)
            if now_ms > max_elapsed_ms or total_tokens > max_tokens:
                terminal_status = "failed"
                stop_reason = "budget_exhausted"
                break

            generated_path = debug_dir / f"iter-{iteration_id}-generated.txt"
            if args.emit_debug_artifacts:
                generated_path.write_text(candidate + "\n", encoding="utf-8")

            eval_report = evaluate_candidate(
                profile=profile,
                objective=args.objective,
                candidate=candidate,
                iteration_id=iteration_id,
                improved=False,
                seed=run_seed,
            )

            if baseline_scores is None:
                baseline_scores = dict(eval_report["scores"])

            diagnosis_obj = diagnose(profile, eval_report)
            improvement_action = improve(candidate, diagnosis_obj, iteration_id)
            improved_candidate = improvement_action["candidate"]

            improved_path = debug_dir / f"iter-{iteration_id}-improved.txt"
            if args.emit_debug_artifacts:
                improved_path.write_text(improved_candidate + "\n", encoding="utf-8")

            reevaluation_report = evaluate_candidate(
                profile=profile,
                objective=args.objective,
                candidate=improved_candidate,
                iteration_id=iteration_id,
                improved=True,
                seed=run_seed + iteration_id + rng.randint(0, 3),
            )

            baseline_for_regression = best_accepted_scores or baseline_scores
            non_regression_ok, regressions = check_non_regression(
                profile=profile,
                baseline_scores=baseline_for_regression,
                candidate_scores=reevaluation_report["scores"],
            )
            reevaluation_report["non_regression_passed"] = non_regression_ok
            reevaluation_report["regression_criteria"] = regressions

            criterion_deltas = {
                c.id: round(reevaluation_report["scores"][c.id] - eval_report["scores"][c.id], 3)
                for c in profile.criteria
            }

            iteration_pass = pass_thresholds(profile, reevaluation_report["scores"]) and (
                non_regression_ok if profile.thresholds.critical_non_regression else True
            )

            if iteration_pass:
                consecutive_passes += 1
                best_accepted_scores = dict(reevaluation_report["scores"])
                state = "accepted"
                gate_decision = "pass"
            else:
                consecutive_passes = 0
                state = "rejected"
                gate_decision = "continue"

            reevaluation_report["gate_decision"] = gate_decision

            checkpoint_reason: Optional[str] = None
            if iteration_id == 1:
                checkpoint_reason = "initial"
            elif any(f.get("severity") == "fail" for f in eval_report.get("findings", [])):
                checkpoint_reason = "failure_triggered"
            elif iteration_id == max_iterations:
                checkpoint_reason = "final"

            adversarial_report: Optional[Dict[str, Any]] = None
            if checkpoint_reason:
                adversarial_report = evaluate_candidate_adversarial(
                    profile=profile,
                    objective=args.objective,
                    candidate=improved_candidate,
                    iteration_id=iteration_id,
                    seed=run_seed + iteration_id + 17,
                    checkpoint_reason=checkpoint_reason,
                )
                adversarial_pass = pass_thresholds(profile, adversarial_report["scores"])
                reevaluation_report["adversarial_checkpoint_triggered"] = True
                reevaluation_report["adversarial_checkpoint_reason"] = checkpoint_reason
                reevaluation_report["adversarial_passed"] = adversarial_pass
                if iteration_pass and not adversarial_pass:
                    blocker_code = "evaluator_conflict"
                    terminal_status, stop_reason = normalize_blocked_reason(blocker_code)
                    gate_decision = "hold"
                    state = "escalated"
                    reevaluation_report["gate_decision"] = gate_decision

            generated_tokens = token_estimate(candidate)
            improved_tokens = token_estimate(improved_candidate)
            total_tokens += generated_tokens + improved_tokens

            overall_after = float(reevaluation_report["overall_score"])
            if last_overall is not None and overall_after <= (last_overall + 0.005):
                no_improvement_count += 1
            else:
                no_improvement_count = 0
            last_overall = overall_after

            journal = {
                "schema_version": profile.schema_version,
                "run_id": run_id,
                "iteration_id": iteration_id,
                "run_version": iteration_id,
                "state": state,
                "created_at": iso_now(),
                "created_by": args.actor_id,
                "rubric_version": profile.rubric_version,
                "evaluator_version": profile.evaluator_version,
                "persona_set_id": profile.persona_set_id,
                "prompt_hash": sha256_text(candidate),
                "applied_lessons": [],
                "generated": {
                    "content_ref": (
                        str(generated_path.relative_to(out_dir.parent))
                        if args.emit_debug_artifacts
                        else ""
                    ),
                    "token_estimate": generated_tokens,
                },
                "evaluation_report": eval_report,
                "diagnosis": diagnosis_obj,
                "improvement_action": {
                    "action_type": improvement_action["action_type"],
                    "summary": improvement_action["summary"],
                },
                "reevaluation_report": reevaluation_report,
                "adversarial_report": adversarial_report or {},
                "criterion_deltas": criterion_deltas,
            }
            append_jsonl(iteration_journal_path, journal)
            journal_iteration_ids.append(iteration_id)
            iterations_completed += 1

            candidate = improved_candidate
            if blocker_code:
                break

            if consecutive_passes >= max(1, profile.thresholds.stability_consecutive_passes):
                terminal_status = "passed"
                stop_reason = "pass"
                break

            if no_improvement_count >= max(1, profile.thresholds.no_improvement_escalation_limit):
                terminal_status = "escalated"
                stop_reason = "escalated"
                break

            if total_tokens > max_tokens or int((time.time() - started_at) * 1000) > max_elapsed_ms:
                terminal_status = "failed"
                stop_reason = "budget_exhausted"
                break

            if is_kill_switch_activated(kill_switch_path):
                blocker_code = "kill_switch_activated"
                terminal_status, stop_reason = normalize_blocked_reason(blocker_code)
                break
            if is_kill_switch_activated(rollback_required_path):
                blocker_code = "run_rollback_required"
                terminal_status, stop_reason = normalize_blocked_reason(blocker_code)
                break
    finally:
        release_run_lock(lock_path, run_id)

    if terminal_status not in TERMINAL_STATUSES:
        terminal_status = "failed"
    if stop_reason not in STOP_REASONS:
        stop_reason = "policy_failed"

    duration_ms = int((time.time() - started_at) * 1000)

    if blocker_code in BLOCKER_CODES:
        emit_event(
            events=events,
            run_id=run_id,
            profile=profile,
            actor_id=args.actor_id,
            objective_hash=objective_hash,
            event_type="run_blocked",
            severity="warn",
            terminal_status=terminal_status,
            stop_reason=stop_reason,
            blocker_code=blocker_code,
        )
        write_json(
            out_dir / "run_blocker.json",
            {
                "schema_version": "1.0",
                "run_id": run_id,
                "code": blocker_code,
                "message": f"run halted by blocker: {blocker_code}",
                "remediation_owner": run_owner,
                "created_at": iso_now(),
            },
        )
        if blocker_code in {"kill_switch_activated", "run_rollback_required", "run_rollforward_blocked"}:
            write_json(
                out_dir / "rollback_recommendation.json",
                {
                    "schema_version": "1.0",
                    "run_id": run_id,
                    "reason": blocker_code,
                    "owner": run_owner,
                    "recommended_actions": [
                        "inspect blocker and event logs",
                        "validate lock and canonical lesson state",
                        "retry only after blocker condition cleared",
                    ],
                    "created_at": iso_now(),
                },
            )

    emit_event(
        events=events,
        run_id=run_id,
        profile=profile,
        actor_id=args.actor_id,
        objective_hash=objective_hash,
        event_type="run_state_changed",
        severity="info" if terminal_status == "passed" else "warn",
        terminal_status=terminal_status,
        stop_reason=stop_reason,
        blocker_code=blocker_code,
    )

    if terminal_status != "passed":
        emit_event(
            events=events,
            run_id=run_id,
            profile=profile,
            actor_id=args.actor_id,
            objective_hash=objective_hash,
            event_type="failure_event",
            severity="fail" if terminal_status == "failed" else "warn",
            terminal_status=terminal_status,
            stop_reason=stop_reason,
            blocker_code=blocker_code,
        )

    run_obj = {
        "schema_version": profile.schema_version,
        "run_id": run_id,
        "profile_id": profile.profile_id,
        "scope_skill": profile.scope_skill,
        "scope_profile": profile.scope_profile,
        "terminal_status": terminal_status,
        "stop_reason": stop_reason,
        "started_at": created_at,
        "finished_at": iso_now(),
        "duration_ms": duration_ms,
        "budget": {
            "max_iterations": max_iterations,
            "max_elapsed_ms": max_elapsed_ms,
            "max_tokens": max_tokens,
        },
        "counters": {
            "iterations_completed": iterations_completed,
            "tokens_used": total_tokens,
            "consecutive_passes": consecutive_passes,
        },
        "versions": {
            "rubric_version": profile.rubric_version,
            "evaluator_version": profile.evaluator_version,
            "persona_set_id": profile.persona_set_id,
        },
        "prompt_hash": objective_hash,
        "created_by": args.actor_id,
        "run_owner": run_owner,
        "idempotency_key": idempotency_key,
        "lock_path": str(lock_path),
        "kill_switch_file": str(kill_switch_path) if kill_switch_path else "",
        "rollback_required_file": str(rollback_required_path) if rollback_required_path else "",
        "runtime_controls": runtime_controls,
        "run_blocker": (
            {
                "code": blocker_code,
                "remediation_owner": run_owner,
            }
            if blocker_code
            else None
        ),
        "injection_summary": {
            "lessons_file": str(lessons_file),
            "retrieved_count": len(retrieved_lessons),
            "selected_count": len(injected_lessons),
            "selected_lesson_ids": [item["lesson_id"] for item in injected_lessons],
            "low_confidence_threshold": args.low_confidence_threshold,
            "suppressed_by_controls": (not auto_apply_enabled and len(retrieved_lessons) > 0),
        },
        "injected_lessons": injected_lessons,
        "retrieved_lessons": retrieved_lessons,
    }

    promotion_decision = {
        "schema_version": profile.schema_version,
        "run_id": run_id,
        "lesson_id": "",
        "decision": "draft",
        "reviewer_ids": [],
        "expected_version": "",
        "lesson_status": "",
        "lesson_effective_to": None,
        "gate_decision": {
            "runtime_gates_passed": terminal_status == "passed",
            "provenance_complete": True,
            "security_checklist_passed": False,
            "notes": "Fill before approve/reject.",
        },
        "provenance": {
            "prompt_hash": sha256_text(args.objective),
            "rubric_version": profile.rubric_version,
            "evaluator_version": profile.evaluator_version,
            "iteration_ids": journal_iteration_ids,
        },
        "injected_lesson_ids": [item["lesson_id"] for item in injected_lessons],
        "runtime_controls": runtime_controls,
    }

    summary_md = (
        "# Recursive Skill Loop Summary\n\n"
        f"- run_id: `{run_id}`\n"
        f"- profile_id: `{profile.profile_id}`\n"
        f"- terminal_status: `{terminal_status}`\n"
        f"- stop_reason: `{stop_reason}`\n"
        f"- iterations_completed: `{iterations_completed}`\n"
        f"- tokens_used: `{total_tokens}`\n"
        f"- duration_ms: `{duration_ms}`\n"
    )

    write_json(out_dir / "run.json", run_obj)
    write_json(out_dir / "promotion_decision.json", promotion_decision)
    write_jsonl(events_path, events)
    write_capture_artifacts(run_obj, promotion_decision)

    if args.emit_debug_artifacts:
        (debug_dir / "summary.md").write_text(summary_md, encoding="utf-8")

    print(f"[recursive-loop] run_id={run_id}")
    print(f"[recursive-loop] status={terminal_status} stop_reason={stop_reason}")
    print(f"[recursive-loop] out_dir={out_dir}")

    if terminal_status == "passed":
        return 0
    if terminal_status == "escalated":
        return 3
    if terminal_status == "aborted":
        return 4
    return 2


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run bounded recursive skill loop (MVP scaffold)")
    p.add_argument("--profile-file", required=True, help="Path to profile JSON")
    p.add_argument("--objective", required=True, help="Run objective text")
    p.add_argument("--out-root", default="artifacts/skill-graphs/runs", help="Output root directory")
    p.add_argument("--actor-id", default="recursive-skill-loop", help="Actor id for artifacts/events")
    p.add_argument("--run-owner", default="recursive-loop-system", help="Owning operator/service id")
    p.add_argument("--run-lock", help="Optional explicit lock file path")
    p.add_argument("--idempotency-key", help="Optional idempotency key for run ownership")
    p.add_argument("--kill-switch-file", help="Kill switch file path (or use SKILL_GRAPH_KILL_SWITCH_PATH)")
    p.add_argument(
        "--rollback-required-file",
        help="Rollback-required control file path (or use SKILL_GRAPH_ROLLBACK_REQUIRED_PATH)",
    )
    p.add_argument(
        "--controls-dir",
        help="Control root directory (default: artifacts/skill-graphs/controls)",
    )
    p.add_argument(
        "--skill-controls-dir",
        help="Optional skill control root (default: <controls-dir>/skills)",
    )
    p.add_argument(
        "--rollout-mode",
        choices=sorted(ROLLOUT_MODES),
        help="Runtime rollout mode override (off|observe_only|active)",
    )
    p.add_argument(
        "--rollout-mode-file",
        help="Rollout mode control file (default: <controls-dir>/rollout-mode.txt)",
    )
    p.add_argument(
        "--auto-capture-switch-file",
        help="Global auto-capture kill switch path (default: <controls-dir>/auto_capture.disabled)",
    )
    p.add_argument(
        "--auto-apply-switch-file",
        help="Global auto-apply kill switch path (default: <controls-dir>/auto_apply.disabled)",
    )
    p.add_argument("--seed", type=int, help="Optional deterministic seed override")
    p.add_argument("--max-iterations", type=int, help="Override max iterations")
    p.add_argument("--max-elapsed-ms", type=int, help="Override elapsed budget")
    p.add_argument("--max-tokens", type=int, help="Override token budget")
    p.add_argument(
        "--lessons-jsonl",
        default="artifacts/skill-graphs/lessons/canonical-lessons.jsonl",
        help="Path to canonical lessons JSONL for start-of-run retrieval/injection",
    )
    p.add_argument(
        "--max-injected-lessons",
        type=int,
        default=3,
        help="Maximum number of scoped lessons to inject at run start",
    )
    p.add_argument(
        "--low-confidence-threshold",
        type=float,
        default=0.6,
        help="Confidence threshold below which lessons are down-ranked and flagged",
    )
    p.add_argument(
        "--feedback-outcome",
        choices=sorted(FEEDBACK_OUTCOMES),
        help="Optional immediate one-tap outcome feedback: worked|partly|didnt_work",
    )
    p.add_argument(
        "--feedback-note",
        help="Optional short feedback note paired with --feedback-outcome",
    )
    p.add_argument(
        "--emit-debug-artifacts",
        action="store_true",
        help="Write optional debug artifacts under run/debug/",
    )
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return run_loop(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
