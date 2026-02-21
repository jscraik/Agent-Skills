#!/usr/bin/env python3
"""Bounded recursive skill self-improvement loop (MVP scaffold).

Implements a deterministic loop:
  generate -> evaluate -> diagnose -> improve -> re-score

Canonical artifacts written per run:
- run.json
- iteration_journal.jsonl
- promotion_decision.json

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


def stable_unit_float(*parts: str) -> float:
    raw = "::".join(parts)
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def token_estimate(text: str) -> int:
    # Lightweight approximation for deterministic budgeting.
    return max(1, math.ceil(len(text) / 4))


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


def run_loop(args: argparse.Namespace) -> int:
    profile = load_profile(Path(args.profile_file).resolve())

    run_seed = args.seed if args.seed is not None else int(stable_unit_float(args.objective, profile.profile_id) * 10_000_000)
    rng = random.Random(run_seed)

    run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{sha256_text(profile.profile_id + args.objective)[:6]}"
    out_dir = Path(args.out_root).resolve() / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    debug_dir = out_dir / "debug"
    if args.emit_debug_artifacts:
        debug_dir.mkdir(parents=True, exist_ok=True)

    started_at = time.time()
    created_at = iso_now()

    max_iterations = args.max_iterations or profile.thresholds.max_iterations
    max_elapsed_ms = args.max_elapsed_ms or profile.thresholds.max_elapsed_ms
    max_tokens = args.max_tokens or profile.thresholds.max_tokens

    events: List[Dict[str, Any]] = [
        {
            "schema_version": "1.0",
            "event_id": sha256_text(run_id + "run_initialized")[:16],
            "ts": created_at,
            "run_id": run_id,
            "skill_name": profile.scope_skill,
            "task_profile": profile.profile_id,
            "event_type": "run_initialized",
            "severity": "info",
            "terminal_status": None,
            "stop_reason": None,
            "actor_id": args.actor_id,
            "evaluator_version": profile.evaluator_version,
            "rubric_version": profile.rubric_version,
            "prompt_hash": sha256_text(args.objective),
        }
    ]

    journals: List[Dict[str, Any]] = []
    candidate = args.objective.strip()
    total_tokens = 0
    consecutive_passes = 0
    no_improvement_count = 0
    last_overall: Optional[float] = None
    baseline_scores: Optional[Dict[str, float]] = None
    best_accepted_scores: Optional[Dict[str, float]] = None
    terminal_status = "failed"
    stop_reason = "budget_exhausted"

    for iteration_id in range(1, max_iterations + 1):
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
            "criterion_deltas": criterion_deltas,
        }
        journals.append(journal)

        candidate = improved_candidate

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

    if terminal_status not in TERMINAL_STATUSES:
        terminal_status = "failed"
    if stop_reason not in STOP_REASONS:
        stop_reason = "policy_failed"

    duration_ms = int((time.time() - started_at) * 1000)

    events.append(
        {
            "schema_version": "1.0",
            "event_id": sha256_text(run_id + terminal_status + stop_reason)[:16],
            "ts": iso_now(),
            "run_id": run_id,
            "skill_name": profile.scope_skill,
            "task_profile": profile.profile_id,
            "event_type": "run_state_changed",
            "severity": "info" if terminal_status == "passed" else "warn",
            "terminal_status": terminal_status,
            "stop_reason": stop_reason,
            "actor_id": args.actor_id,
            "evaluator_version": profile.evaluator_version,
            "rubric_version": profile.rubric_version,
            "prompt_hash": sha256_text(args.objective),
        }
    )

    if terminal_status != "passed":
        events.append(
            {
                "schema_version": "1.0",
                "event_id": sha256_text(run_id + "failure_event")[:16],
                "ts": iso_now(),
                "run_id": run_id,
                "skill_name": profile.scope_skill,
                "task_profile": profile.profile_id,
                "event_type": "failure_event",
                "severity": "fail" if terminal_status == "failed" else "warn",
                "terminal_status": terminal_status,
                "stop_reason": stop_reason,
                "actor_id": args.actor_id,
                "evaluator_version": profile.evaluator_version,
                "rubric_version": profile.rubric_version,
                "prompt_hash": sha256_text(args.objective),
            }
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
            "iterations_completed": len(journals),
            "tokens_used": total_tokens,
            "consecutive_passes": consecutive_passes,
        },
        "versions": {
            "rubric_version": profile.rubric_version,
            "evaluator_version": profile.evaluator_version,
            "persona_set_id": profile.persona_set_id,
        },
        "prompt_hash": sha256_text(args.objective),
        "created_by": args.actor_id,
    }

    promotion_decision = {
        "schema_version": profile.schema_version,
        "run_id": run_id,
        "lesson_id": "",
        "decision": "draft",
        "reviewer_ids": [],
        "expected_version": "",
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
            "iteration_ids": [j["iteration_id"] for j in journals],
        },
    }

    summary_md = (
        "# Recursive Skill Loop Summary\n\n"
        f"- run_id: `{run_id}`\n"
        f"- profile_id: `{profile.profile_id}`\n"
        f"- terminal_status: `{terminal_status}`\n"
        f"- stop_reason: `{stop_reason}`\n"
        f"- iterations_completed: `{len(journals)}`\n"
        f"- tokens_used: `{total_tokens}`\n"
        f"- duration_ms: `{duration_ms}`\n"
    )

    write_json(out_dir / "run.json", run_obj)
    write_jsonl(out_dir / "iteration_journal.jsonl", journals)
    write_json(out_dir / "promotion_decision.json", promotion_decision)

    if args.emit_debug_artifacts:
        write_jsonl(debug_dir / "events.jsonl", events)
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
    p.add_argument("--seed", type=int, help="Optional deterministic seed override")
    p.add_argument("--max-iterations", type=int, help="Override max iterations")
    p.add_argument("--max-elapsed-ms", type=int, help="Override elapsed budget")
    p.add_argument("--max-tokens", type=int, help="Override token budget")
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
