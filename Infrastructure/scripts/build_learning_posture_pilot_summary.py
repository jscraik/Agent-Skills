#!/usr/bin/env python3
"""Build pilot conformance summary for learning-preserving posture work.

Artifact paths from scorecards are resolved against repo root so this script is
safe to run from any current working directory.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

PILOT_SKILLS = [
    "Skills/skill-builder",
    "frontend/tools/agentation",
    "Skills/systematic-debugging",
    "interview/interview-me",
]

VALID_POSTURES = {"learn", "guided", "execute"}
VALID_TAGS = {
    "conceptual_inquiry",
    "explain_then_generate",
    "generate_then_explain",
    "full_delegation",
    "ai_led_debugging",
}
TELEMETRY_DIR = Path("Infrastructure/artifacts/skill-graphs/pilot/telemetry")
REPO_ROOT = Path(__file__).resolve().parents[2]


def collect_json(path: Path) -> dict:
    """Load JSON from disk or return {} if missing/corrupt."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def collect_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load JSONL events from disk; ignore malformed lines."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    events: list[dict[str, Any]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            events.append(parsed)
    return events


def resolve_artifact_path(path_like: str, workspace_root: Path) -> Path:
    """Resolve artifact paths deterministically, independent of current cwd."""
    candidate = Path(path_like).expanduser()
    if candidate.is_absolute():
        return candidate
    return (workspace_root / candidate).resolve()


def latest_scorecard(skill_path: str) -> Tuple[dict, Path | None]:
    """Return latest scorecard and its path for a pilot skill."""
    base = Path("Infrastructure/artifacts/skills") / Path(skill_path).name
    if not base.exists():
        return {}, None

    run_dirs = [p for p in sorted(base.iterdir()) if p.is_dir()]
    if not run_dirs:
        return {}, None

    scorecard_path = run_dirs[-1] / "scorecard.json"
    return collect_json(scorecard_path), scorecard_path


def latest_report_state(scorecard: dict) -> str:
    if not scorecard:
        return "not_run"
    if scorecard.get("passed") is True:
        return "pass"
    if scorecard.get("passed") is False:
        return "blocked"
    return "partial"


def infer_case_tags(case: dict) -> set[str]:
    tags: set[str] = set()
    text = " ".join(
        [
            str(case.get("id", "")).lower(),
            str(case.get("name", "")).lower(),
            str(case.get("category", "")).lower(),
        ]
    )

    if any(token in text for token in ("learn", "guided", "posture", "clarify", "interview", "explain")):
        tags.add("conceptual_inquiry")
        tags.add("explain_then_generate")
    if any(token in text for token in ("pressure", "debug", "hypothesis", "diagnose")):
        tags.add("ai_led_debugging")
    if any(token in text for token in ("negative", "out-of-scope", "not_selected")):
        tags.add("full_delegation")
    if any(token in text for token in ("happy", "explicit", "execute", "contract", "watch")):
        tags.add("generate_then_explain")

    return {tag for tag in tags if tag in VALID_TAGS}


def summarize_trace_and_selection(case: dict) -> Dict[str, Any]:
    selected_present = False
    trace_present = False
    trace_error = False
    warnings: List[str] = []

    runners = case.get("runners", {})
    if not isinstance(runners, dict):
        return {
            "selected_present": selected_present,
            "trace_present": trace_present,
            "trace_error": trace_error,
            "warnings": warnings,
        }

    for runner in runners.values():
        if not isinstance(runner, dict):
            continue
        metrics = runner.get("metrics")
        if isinstance(metrics, dict) and metrics.get("selected_skill") is not None:
            selected_present = True

        artifacts = runner.get("artifacts")
        if not isinstance(artifacts, dict):
            continue
        jsonl_path = artifacts.get("jsonl")
        if not isinstance(jsonl_path, str) or not jsonl_path:
            continue
        events = collect_jsonl(resolve_artifact_path(jsonl_path, REPO_ROOT))
        if events:
            trace_present = True
            if any(event.get("type") in {"error", "turn.failed"} for event in events):
                trace_error = True
                warnings.append("Trace events include error/turn.failed.")

    return {
        "selected_present": selected_present,
        "trace_present": trace_present,
        "trace_error": trace_error,
        "warnings": warnings,
    }


def evaluate_telemetry(scorecard: dict) -> Tuple[str, list[str], list[str], dict]:
    if not scorecard:
        return "not_run", ["No eval scorecard found yet for this pilot."], [], {
            "case_count": 0,
            "trace_case_count": 0,
            "selection_case_count": 0,
            "trace_error_case_count": 0,
            "telemetry_coverage_ratio": 0.0,
        }

    cases = scorecard.get("cases", [])
    if not isinstance(cases, list) or not cases:
        return "partial", ["Eval scorecard has no case details."], [], {
            "case_count": 0,
            "trace_case_count": 0,
            "selection_case_count": 0,
            "trace_error_case_count": 0,
            "telemetry_coverage_ratio": 0.0,
        }

    warnings: list[str] = []
    tags: set[str] = set()
    trace_case_count = 0
    selection_case_count = 0
    trace_error_case_count = 0

    for case in cases:
        if not isinstance(case, dict):
            continue
        tags.update(infer_case_tags(case))
        summary = summarize_trace_and_selection(case)
        if summary["trace_present"]:
            trace_case_count += 1
        if summary["selected_present"]:
            selection_case_count += 1
        if summary["trace_error"]:
            trace_error_case_count += 1
        warnings.extend(summary["warnings"])

    case_count = len(cases)
    coverage_ratio = trace_case_count / case_count if case_count else 0.0

    if not tags and case_count > 0:
        tags.add("explain_then_generate")

    if trace_case_count == 0:
        telemetry_state = "blocked"
        warnings.append("No usable trace evidence was captured for any eval case.")
    elif trace_error_case_count == case_count:
        telemetry_state = "blocked"
        warnings.append("All traced cases failed with runtime errors.")
    elif coverage_ratio < 1.0 or selection_case_count < case_count:
        telemetry_state = "partial"
        warnings.append("Telemetry coverage is incomplete across pilot eval cases.")
    else:
        telemetry_state = "pass"

    metrics = {
        "case_count": case_count,
        "trace_case_count": trace_case_count,
        "selection_case_count": selection_case_count,
        "trace_error_case_count": trace_error_case_count,
        "telemetry_coverage_ratio": round(coverage_ratio, 3),
    }
    return telemetry_state, warnings, sorted(tags), metrics


def telemetry_artifact_path(skill_path: str) -> Path:
    return TELEMETRY_DIR / f"{skill_path.replace('/', '__')}.json"


def write_telemetry_artifact(
    skill_path: str,
    telemetry_state: str,
    telemetry_tags: list[str],
    telemetry_warnings: list[str],
    telemetry_metrics: dict,
    scorecard_path: Path | None,
) -> None:
    payload = {
        "skill": skill_path,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "telemetry_state": telemetry_state,
        "interaction_pattern_tags": telemetry_tags,
        "warnings": telemetry_warnings,
        "metrics": telemetry_metrics,
        "scorecard_path": scorecard_path.as_posix() if scorecard_path else None,
    }
    out_path = telemetry_artifact_path(skill_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def evaluate_profile_pairings(
    task_profile: dict,
    declared_posture: str,
) -> tuple[list[str], str]:
    warnings: list[str] = []
    status = "pass"
    delegation = task_profile.get("delegation", {})
    mode = str(delegation.get("mode", "")).strip().lower() if isinstance(delegation, dict) else ""
    learning_posture = task_profile.get("learning_posture", {})
    degraded_ack = []
    if isinstance(learning_posture, dict):
        raw_ack = learning_posture.get("degraded_pairings_acknowledged", [])
        if isinstance(raw_ack, list):
            degraded_ack = [str(item).strip() for item in raw_ack]

    if mode == "autopilot" and declared_posture == "learn":
        warnings.append("Invalid pairing surfaced: autopilot + learn is blocked.")
        status = "blocked"
    if mode == "autopilot" and declared_posture == "guided" and not degraded_ack:
        warnings.append("Degraded pairing surfaced: autopilot + guided requires degraded_pairings_acknowledged.")
        status = "partial" if status != "blocked" else status
    return warnings, status


def evaluate_pilot(skill_path: str) -> dict[str, object]:
    task_profile = collect_json(Path(skill_path) / "references" / "task-profile.json")
    learning_posture = task_profile.get("learning_posture", {})
    default_posture = learning_posture.get("default") if isinstance(learning_posture, dict) else None
    supported_posture = learning_posture.get("supported", []) if isinstance(learning_posture, dict) else []
    declared_posture = str(default_posture) if default_posture else "not_declared"

    scorecard, scorecard_path = latest_scorecard(skill_path)
    eval_state = latest_report_state(scorecard)
    telemetry_state, telemetry_warnings, telemetry_tags, telemetry_metrics = evaluate_telemetry(scorecard)
    pairing_warnings, pairing_state = evaluate_profile_pairings(task_profile, declared_posture)
    warnings: list[str] = []

    if declared_posture == "not_declared":
        warnings.append("Task profile is missing learning_posture.default.")
    if not isinstance(supported_posture, list) or not supported_posture:
        warnings.append("Task profile is missing learning_posture.supported.")
    if declared_posture != "not_declared" and isinstance(supported_posture, list) and declared_posture not in supported_posture:
        warnings.append("Default posture is not present in learning_posture.supported.")
    if declared_posture != "not_declared" and declared_posture not in VALID_POSTURES:
        warnings.append("Declared posture is outside learn|guided|execute contract.")
    if eval_state == "not_run":
        warnings.append("No eval scorecard found yet for this pilot.")

    warnings.extend(telemetry_warnings)
    warnings.extend(pairing_warnings)

    selected_posture = declared_posture if declared_posture in VALID_POSTURES else "not_selected"
    if selected_posture == "not_selected":
        warnings.append("No selected posture was recorded.")

    conformance_state = "pass"
    if eval_state in {"blocked"} or telemetry_state in {"blocked"} or pairing_state == "blocked":
        conformance_state = "blocked"
    elif eval_state in {"partial", "not_run"} or telemetry_state in {"partial", "not_run"} or pairing_state == "partial":
        conformance_state = "partial"

    if not warnings:
        warnings.append("Pilot posture metadata/eval/telemetry implemented and executed.")

    write_telemetry_artifact(
        skill_path=skill_path,
        telemetry_state=telemetry_state,
        telemetry_tags=telemetry_tags,
        telemetry_warnings=warnings,
        telemetry_metrics=telemetry_metrics,
        scorecard_path=scorecard_path,
    )

    return {
        "skill": skill_path,
        "declared_posture": declared_posture,
        "selected_posture": selected_posture,
        "eval_state": eval_state,
        "telemetry_state": telemetry_state,
        "conformance_state": conformance_state,
        "interaction_pattern_tags": telemetry_tags,
        "warnings": sorted(set(warnings)),
    }


def determine_overall(entries: Iterable[dict[str, object]]) -> str:
    states = [entry["conformance_state"] for entry in entries]
    if "blocked" in states:
        return "blocked"
    if "partial" in states:
        return "partial"
    if all(state == "pass" for state in states):
        return "pass"
    return "partial"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build pilot conformance summary")
    parser.add_argument(
        "--out-json",
        required=True,
        type=Path,
        help="Output JSON summary path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_json: Path = args.out_json
    pilot_skills = [evaluate_pilot(skill_path) for skill_path in PILOT_SKILLS]
    payload = {
        "pilot_version": "v0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "overall_state": determine_overall(pilot_skills),
        "pilot_skills": pilot_skills,
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
