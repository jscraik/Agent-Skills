#!/usr/bin/env python3
"""Backfill historical recursive run artifacts to current parity requirements.

This script repairs older run directories that predate the mandatory recursive
artifact envelope by reconstructing a minimal but truthful set of files from the
existing run metadata.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_dumps(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def write_json(path: Path, payload: Any, dry_run: bool) -> None:
    if dry_run:
        return
    path.write_text(json_dumps(payload), encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]], dry_run: bool) -> None:
    if dry_run:
        return
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True))
            handle.write("\n")


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return obj if isinstance(obj, dict) else None


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except Exception:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def iso_when(run_obj: Dict[str, Any]) -> str:
    for key in ("finished_at", "started_at", "updated_at"):
        value = str(run_obj.get(key, "")).strip()
        if value:
            return value
    return "2026-01-01T00:00:00Z"


def profile_id(run_obj: Dict[str, Any]) -> str:
    return str(run_obj.get("profile_id") or run_obj.get("scope_skill") or "unknown").strip()


def actor_id(run_obj: Dict[str, Any]) -> str:
    return str(run_obj.get("created_by") or "historical-backfill").strip()


def runtime_controls(run_obj: Dict[str, Any]) -> Dict[str, Any]:
    controls = run_obj.get("runtime_controls")
    if isinstance(controls, dict):
        return controls
    return {}


def terminal_status(run_obj: Dict[str, Any]) -> str:
    return str(run_obj.get("terminal_status") or "failed").strip()


def stop_reason(run_obj: Dict[str, Any]) -> str:
    return str(run_obj.get("stop_reason") or "policy_failed").strip()


def ensure_iteration_journal(run_dir: Path, run_obj: Dict[str, Any], dry_run: bool) -> bool:
    path = run_dir / "iteration_journal.jsonl"
    if path.exists():
        return False

    ts = iso_when(run_obj)
    row = {
        "schema_version": "1.0",
        "run_id": str(run_obj.get("run_id", run_dir.name)),
        "run_version": 1,
        "iteration_id": 1,
        "created_at": ts,
        "created_by": actor_id(run_obj),
        "profile_id": profile_id(run_obj),
        "scope_skill": str(run_obj.get("scope_skill", "")).strip(),
        "scope_profile": str(run_obj.get("scope_profile", "")).strip(),
        "prompt_hash": str(run_obj.get("prompt_hash", "")).strip(),
        "evaluator_version": str(run_obj.get("versions", {}).get("evaluator_version", "unknown")).strip(),
        "rubric_version": str(run_obj.get("versions", {}).get("rubric_version", "unknown")).strip(),
        "persona_set_id": str(run_obj.get("versions", {}).get("persona_set_id", "")).strip(),
        "evaluation_report": {
            "overall_score": 1.0 if terminal_status(run_obj) == "passed" else 0.0,
            "scores": {},
            "findings": [],
            "judge_mode": "historical_backfill",
            "eligible_for_gate_check": True,
            "adversarial_checkpoint_triggered": False,
        },
        "reevaluation_report": {
            "overall_score": 1.0 if terminal_status(run_obj) == "passed" else 0.0,
            "scores": {},
            "findings": [],
            "judge_mode": "historical_backfill",
            "eligible_for_gate_check": True,
            "adversarial_checkpoint_triggered": False,
            "gate_decision": "pass" if terminal_status(run_obj) == "passed" else "continue",
            "non_regression_passed": terminal_status(run_obj) == "passed",
            "regression_criteria": [],
        },
        "state": "accepted" if terminal_status(run_obj) == "passed" else "rejected",
        "generated": {"content_ref": "", "token_estimate": int(run_obj.get("counters", {}).get("tokens_used", 0))},
        "criterion_deltas": {},
        "diagnosis": {"deficits": {}, "reason": "Historical backfill from run metadata.", "weakest_criteria": []},
        "improvement_action": {"action_type": "historical_backfill", "summary": "Reconstructed minimal iteration record."},
        "applied_lessons": [],
    }
    write_jsonl(path, [row], dry_run)
    return True


def build_events(run_obj: Dict[str, Any], run_dir: Path) -> List[Dict[str, Any]]:
    run_id = str(run_obj.get("run_id", run_dir.name))
    skill_name = str(run_obj.get("scope_skill", "unknown"))
    task_profile = profile_id(run_obj)
    started_at = str(run_obj.get("started_at") or iso_when(run_obj))
    finished_at = str(run_obj.get("finished_at") or started_at)
    prompt_hash = str(run_obj.get("prompt_hash", ""))
    evaluator_version = str(run_obj.get("versions", {}).get("evaluator_version", "unknown"))
    rubric_version = str(run_obj.get("versions", {}).get("rubric_version", "unknown"))
    actor = actor_id(run_obj)
    status = terminal_status(run_obj)
    reason = stop_reason(run_obj)

    events: List[Dict[str, Any]] = [
        {
            "schema_version": "1.0",
            "event_id": sha256_text(f"{run_id}:run_initialized:{started_at}")[:16],
            "ts": started_at,
            "run_id": run_id,
            "skill_name": skill_name,
            "task_profile": task_profile,
            "event_type": "run_initialized",
            "severity": "info",
            "terminal_status": None,
            "stop_reason": None,
            "actor_id": actor,
            "evaluator_version": evaluator_version,
            "rubric_version": rubric_version,
            "prompt_hash": prompt_hash,
            "auto_capture_enabled": True,
            "auto_apply_enabled": False,
            "rollout_mode": "observe_only",
            "retrieved_lesson_ids": [],
            "injected_lesson_ids": [],
        },
        {
            "schema_version": "1.0",
            "event_id": sha256_text(f"{run_id}:run_state_changed:{status}:{reason}:{finished_at}")[:16],
            "ts": finished_at,
            "run_id": run_id,
            "skill_name": skill_name,
            "task_profile": task_profile,
            "event_type": "run_state_changed",
            "severity": "warn" if status != "passed" else "info",
            "terminal_status": status,
            "stop_reason": reason,
            "actor_id": actor,
            "evaluator_version": evaluator_version,
            "rubric_version": rubric_version,
            "prompt_hash": prompt_hash,
        },
    ]

    if status != "passed":
        events.append(
            {
                "schema_version": "1.0",
                "event_id": sha256_text(f"{run_id}:failure_event:{finished_at}")[:16],
                "ts": finished_at,
                "run_id": run_id,
                "skill_name": skill_name,
                "task_profile": task_profile,
                "event_type": "failure_event",
                "severity": "fail",
                "terminal_status": status,
                "stop_reason": reason,
                "actor_id": actor,
                "evaluator_version": evaluator_version,
                "rubric_version": rubric_version,
                "prompt_hash": prompt_hash,
            }
        )

    blocker_code = None
    if status == "escalated" and reason == "evaluator_conflict":
        blocker_code = "evaluator_conflict"
    elif status == "failed" and reason == "dependency_missing":
        blocker_code = "run_rollback_required"
    elif status == "failed" and reason == "policy_failed":
        blocker_code = "run_rollforward_blocked"

    if blocker_code:
        events.append(
            {
                "schema_version": "1.0",
                "event_id": sha256_text(f"{run_id}:run_blocked:{blocker_code}:{finished_at}")[:16],
                "ts": finished_at,
                "run_id": run_id,
                "skill_name": skill_name,
                "task_profile": task_profile,
                "event_type": "run_blocked",
                "severity": "fail",
                "terminal_status": status,
                "stop_reason": reason,
                "blocker_code": blocker_code,
                "actor_id": actor,
                "evaluator_version": evaluator_version,
                "rubric_version": rubric_version,
                "prompt_hash": prompt_hash,
            }
        )

    return events


def ensure_events(run_dir: Path, run_obj: Dict[str, Any], dry_run: bool) -> bool:
    path = run_dir / "events.jsonl"
    if path.exists():
        return False
    write_jsonl(path, build_events(run_obj, run_dir), dry_run)
    return True


def build_minimal_promotion_decision(run_obj: Dict[str, Any], run_dir: Path, template: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    created_at = iso_when(run_obj)
    base: Dict[str, Any] = dict(template) if isinstance(template, dict) else {}
    provenance = base.get("provenance") if isinstance(base.get("provenance"), dict) else {}
    if not provenance:
        journals = load_jsonl(run_dir / "iteration_journal.jsonl")
        provenance = {
            "evaluator_version": str(run_obj.get("versions", {}).get("evaluator_version", "unknown")),
            "rubric_version": str(run_obj.get("versions", {}).get("rubric_version", "unknown")),
            "prompt_hash": str(run_obj.get("prompt_hash", "")),
            "iteration_ids": [row.get("iteration_id") for row in journals if row.get("iteration_id") is not None],
        }

    decision = {
        "schema_version": str(base.get("schema_version", "1.0")),
        "run_id": str(run_obj.get("run_id", run_dir.name)),
        "decision": str(base.get("decision", "draft")),
        "expected_version": str(base.get("expected_version", "")),
        "lesson_id": str(base.get("lesson_id", "")),
        "reviewer_ids": base.get("reviewer_ids", []),
        "gate_decision": base.get(
            "gate_decision",
            {
                "notes": "Historical backfill from existing run metadata.",
                "provenance_complete": True,
                "runtime_gates_passed": terminal_status(run_obj) == "passed",
                "security_checklist_passed": False,
            },
        ),
        "provenance": provenance,
        "updated_at": created_at,
    }
    if "review_note" in base:
        decision["review_note"] = base["review_note"]
    if "lesson_content_sha256" in base:
        decision["lesson_content_sha256"] = base["lesson_content_sha256"]
    if "lesson_source_path" in base:
        decision["lesson_source_path"] = base["lesson_source_path"]
    return decision


def ensure_promotion_decision(run_dir: Path, run_obj: Dict[str, Any], dry_run: bool) -> bool:
    path = run_dir / "promotion_decision.json"
    if path.exists():
        return False
    template = load_json(run_dir / "promotion_decision.template.json")
    write_json(path, build_minimal_promotion_decision(run_obj, run_dir, template), dry_run)
    return True


def evidence_score(sources: Dict[str, Dict[str, Any]]) -> float:
    values = [
        bool(sources.get("checks", {}).get("present")),
        bool(sources.get("events", {}).get("present")),
        bool(sources.get("logs", {}).get("present")),
        bool(sources.get("session_signals", {}).get("present")),
        bool(sources.get("traces", {}).get("present")),
    ]
    return round(sum(1 for item in values if item) / len(values), 3)


def build_evidence_packet(run_dir: Path, run_obj: Dict[str, Any], promotion_decision: Dict[str, Any]) -> Dict[str, Any]:
    events_path = run_dir / "events.jsonl"
    journal_path = run_dir / "iteration_journal.jsonl"
    run_id = str(run_obj.get("run_id", run_dir.name))
    created_at = iso_when(run_obj)
    checks = {
        "present": True,
        "provenance_complete": bool(promotion_decision.get("gate_decision", {}).get("provenance_complete", True)),
        "runtime_gates_passed": bool(promotion_decision.get("gate_decision", {}).get("runtime_gates_passed", False)),
        "security_checklist_passed": bool(promotion_decision.get("gate_decision", {}).get("security_checklist_passed", False)),
        "run_blocker_present": (run_dir / "run_blocker.json").exists(),
    }
    sources = {
        "checks": checks,
        "events": {
            "present": events_path.exists(),
            "path": "events.jsonl",
            "sha256": sha256_file(events_path) if events_path.exists() else "",
            "size_bytes": events_path.stat().st_size if events_path.exists() else 0,
        },
        "logs": {"present": False, "paths": []},
        "session_signals": {
            "present": True,
            "terminal_status": terminal_status(run_obj),
            "stop_reason": stop_reason(run_obj),
            "iterations_completed": int(run_obj.get("counters", {}).get("iterations_completed", len(load_jsonl(journal_path)))),
            "tokens_used": int(run_obj.get("counters", {}).get("tokens_used", 0)),
            "duration_ms": int(run_obj.get("duration_ms", 0)),
        },
        "traces": {
            "present": journal_path.exists(),
            "path": "iteration_journal.jsonl",
            "sha256": sha256_file(journal_path) if journal_path.exists() else "",
            "size_bytes": journal_path.stat().st_size if journal_path.exists() else 0,
        },
    }
    seed = f"{run_id}:{created_at}:evidence"
    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "created_at": created_at,
        "evidence_packet_id": sha256_text(seed)[:16],
        "sources": sources,
        "completeness": {
            "checks": bool(sources["checks"]["present"]),
            "events": bool(sources["events"]["present"]),
            "logs": False,
            "session_signals": True,
            "traces": bool(sources["traces"]["present"]),
            "score": evidence_score(sources),
        },
    }


def build_capture_record(
    run_dir: Path,
    run_obj: Dict[str, Any],
    evidence_packet: Dict[str, Any],
    promotion_decision: Dict[str, Any],
) -> Dict[str, Any]:
    created_at = iso_when(run_obj)
    run_id = str(run_obj.get("run_id", run_dir.name))
    controls = runtime_controls(run_obj)
    confidence = {
        "schema_version": "1.0",
        "score": 0.0,
        "bucket": "unknown",
        "calibration_bucket": "C0_historical_backfill",
        "quality_uplift": 0.0,
        "inputs": {
            "terminal_status": terminal_status(run_obj),
            "stop_reason": stop_reason(run_obj),
            "evidence_completeness": evidence_packet["completeness"]["score"],
            "feedback_status": "missing",
            "feedback_signal": 0.5,
            "runtime_gate_signal": 1.0 if promotion_decision.get("gate_decision", {}).get("runtime_gates_passed") else 0.0,
            "quality_uplift_signal": 0.0,
            "non_regression_signal": 0.0,
            "iterations_observed": int(run_obj.get("counters", {}).get("iterations_completed", 0)),
        },
    }
    return {
        "schema_version": "1.0",
        "capture_id": sha256_text(f"{run_id}:{created_at}:capture")[:16],
        "run_id": run_id,
        "profile_id": profile_id(run_obj),
        "scope_skill": str(run_obj.get("scope_skill", "")).strip(),
        "scope_profile": str(run_obj.get("scope_profile", "")).strip(),
        "created_at": created_at,
        "invocation_envelope": {
            "invocation_id": sha256_text(f"{run_id}:{created_at}:invocation")[:16],
            "invoked_at": str(run_obj.get("started_at") or created_at),
            "actor_id": actor_id(run_obj),
            "run_owner": actor_id(run_obj),
            "objective_hash": str(run_obj.get("prompt_hash", "")),
            "idempotency_key": sha256_text(f"{run_id}:idempotency")[:20],
            "kill_switch_file": "",
            "rollback_required_file": "",
            "rollout_mode": str(controls.get("rollout_mode", "observe_only") or "observe_only"),
            "auto_capture_enabled": True,
            "auto_apply_enabled": bool(controls.get("auto_apply_enabled", False)),
        },
        "output_summary": {
            "finished_at": str(run_obj.get("finished_at") or created_at),
            "terminal_status": terminal_status(run_obj),
            "stop_reason": stop_reason(run_obj),
            "iterations_completed": int(run_obj.get("counters", {}).get("iterations_completed", 0)),
            "tokens_used": int(run_obj.get("counters", {}).get("tokens_used", 0)),
            "duration_ms": int(run_obj.get("duration_ms", 0)),
        },
        "feedback": {"status": "missing", "source": "none", "note": "", "captured_at": created_at},
        "evidence": {
            "evidence_packet_id": evidence_packet["evidence_packet_id"],
            "evidence_packet_path": "evidence_packet.json",
            "completeness": evidence_packet["completeness"],
        },
        "confidence": confidence,
        "lesson_observations": {"count": 0, "top_observation_id": ""},
        "candidate_lessons": {"count": 0, "top_candidate_id": ""},
        "injected_lessons": {"count": 0, "items": []},
    }


def ensure_capture_artifacts(run_dir: Path, run_obj: Dict[str, Any], dry_run: bool) -> List[str]:
    changed: List[str] = []
    promotion_path = run_dir / "promotion_decision.json"
    promotion_decision = load_json(promotion_path) or build_minimal_promotion_decision(run_obj, run_dir, None)

    evidence_packet = build_evidence_packet(run_dir, run_obj, promotion_decision)
    confidence = {
        "schema_version": "1.0",
        "score": 0.0,
        "bucket": "unknown",
        "calibration_bucket": "C0_historical_backfill",
        "quality_uplift": 0.0,
        "evidence_completeness": evidence_packet["completeness"]["score"],
    }
    if "confidence" not in promotion_decision:
        promotion_decision["confidence"] = confidence
    if "evidence_packet" not in promotion_decision:
        promotion_decision["evidence_packet"] = {
            "evidence_packet_id": evidence_packet["evidence_packet_id"],
            "completeness_score": evidence_packet["completeness"]["score"],
        }
    if "lesson_candidates" not in promotion_decision:
        promotion_decision["lesson_candidates"] = []

    evidence_path = run_dir / "evidence_packet.json"
    if not evidence_path.exists():
        write_json(evidence_path, evidence_packet, dry_run)
        changed.append("evidence_packet.json")

    candidates_path = run_dir / "lesson_candidates.json"
    if not candidates_path.exists():
        write_json(
            candidates_path,
            {"schema_version": "1.0", "run_id": str(run_obj.get("run_id", run_dir.name)), "items": []},
            dry_run,
        )
        changed.append("lesson_candidates.json")

    capture_path = run_dir / "capture_record.json"
    if not capture_path.exists():
        write_json(capture_path, build_capture_record(run_dir, run_obj, evidence_packet, promotion_decision), dry_run)
        changed.append("capture_record.json")

    # Persist enriched promotion metadata when we synthesized confidence/evidence.
    write_json(promotion_path, promotion_decision, dry_run)
    if "promotion_decision.json" not in changed:
        changed.append("promotion_decision.json")

    return changed


def ensure_blocker_artifacts(run_dir: Path, run_obj: Dict[str, Any], dry_run: bool) -> List[str]:
    changed: List[str] = []
    status = terminal_status(run_obj)
    reason = stop_reason(run_obj)
    blocker_code = None
    needs_rollback = False
    if status == "escalated" and reason == "evaluator_conflict":
        blocker_code = "evaluator_conflict"
    elif status == "failed" and reason == "dependency_missing":
        blocker_code = "run_rollback_required"
        needs_rollback = True
    elif status == "failed" and reason == "policy_failed":
        blocker_code = "run_rollforward_blocked"
        needs_rollback = True

    if not blocker_code:
        return changed

    blocker_path = run_dir / "run_blocker.json"
    if not blocker_path.exists():
        write_json(
            blocker_path,
            {
                "schema_version": "1.0",
                "run_id": str(run_obj.get("run_id", run_dir.name)),
                "code": blocker_code,
                "message": f"historical backfill reconstructed blocker: {blocker_code}",
                "remediation_owner": actor_id(run_obj),
                "created_at": iso_when(run_obj),
            },
            dry_run,
        )
        changed.append("run_blocker.json")

    if needs_rollback:
        rollback_path = run_dir / "rollback_recommendation.json"
        if not rollback_path.exists():
            write_json(
                rollback_path,
                {
                    "schema_version": "1.0",
                    "run_id": str(run_obj.get("run_id", run_dir.name)),
                    "reason": blocker_code,
                    "created_at": iso_when(run_obj),
                    "recommendation": "Review historical run manually before promotion or replay.",
                },
                dry_run,
            )
            changed.append("rollback_recommendation.json")
    return changed


def target_run_dirs(runs_root: Path, waiver_file: Path, explicit: List[str]) -> List[Path]:
    if explicit:
        return [Path(item).expanduser().resolve() for item in explicit]

    payload = load_json(waiver_file) or {}
    rows = payload.get("waived_runs")
    targets: List[Path] = []
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            raw = str(row.get("run_dir", "")).strip()
            if not raw:
                continue
            path = Path(raw)
            if not path.is_absolute():
                path = (Path.cwd() / raw).resolve()
            targets.append(path)
    if targets:
        return targets
    return sorted(p for p in runs_root.glob("run_*") if p.is_dir())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-root", default="artifacts/skill-graphs/runs")
    parser.add_argument("--waiver-file", default="artifacts/skill-graphs/pilot/artifact-parity-waivers.json")
    parser.add_argument("--run-dir", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    runs_root = Path(args.runs_root).expanduser().resolve()
    waiver_file = Path(args.waiver_file).expanduser().resolve()
    targets = target_run_dirs(runs_root, waiver_file, list(args.run_dir))

    repaired = 0
    for run_dir in targets:
        run_obj = load_json(run_dir / "run.json")
        if not run_obj:
            if args.verbose:
                print(f"skip {run_dir}: missing or unreadable run.json")
            continue

        changes: List[str] = []
        if ensure_iteration_journal(run_dir, run_obj, args.dry_run):
            changes.append("iteration_journal.jsonl")
        if ensure_events(run_dir, run_obj, args.dry_run):
            changes.append("events.jsonl")
        if ensure_promotion_decision(run_dir, run_obj, args.dry_run):
            changes.append("promotion_decision.json")
        changes.extend(
            item for item in ensure_capture_artifacts(run_dir, run_obj, args.dry_run) if item not in changes
        )
        changes.extend(
            item for item in ensure_blocker_artifacts(run_dir, run_obj, args.dry_run) if item not in changes
        )

        if changes:
            repaired += 1
            print(f"{run_dir.name}: repaired {', '.join(changes)}")
        elif args.verbose:
            print(f"{run_dir.name}: already complete")

    print(f"repaired_runs={repaired}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
