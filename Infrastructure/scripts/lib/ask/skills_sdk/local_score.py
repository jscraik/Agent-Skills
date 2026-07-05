from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ask.skills_sdk.contracts import read_skill_frontmatter_fields


LOCAL_SCORE_SCHEMA_VERSION = "skills-sdk.local-score.v1"
LOCAL_SCORE_SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/local-score.v1.schema.json"
LOCAL_SCORE_DEFAULT_TTL_SECONDS = 300
LOCAL_SCORE_ACCEPTANCE_TRACE = ["PU-030", "FR-008", "SEC-001", "VP-030"]
LOCAL_SCORE_GATES = (
    "creation",
    "oss-security",
    "oss-local",
    "oss-cloud",
    "tessl-dry-run",
    "release",
)
SEVERITY_PENALTIES = {
    "critical": 25,
    "high": 20,
    "medium": 10,
    "low": 5,
}
SAFE_SKILL_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def repo_relative(repo_root: Path, path: Path) -> str:
    resolved = path.resolve(strict=False)
    try:
        return resolved.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def safe_skill_name_segment(skill_name: str) -> str:
    segment = SAFE_SKILL_NAME_RE.sub("-", skill_name.strip()).strip(".-_")
    return segment or "unnamed-skill"


def _extract_data(envelope: Any, key: str) -> dict[str, Any] | None:
    data = getattr(envelope, "data", None)
    if not isinstance(data, dict):
        return None
    value = data.get(key)
    return value if isinstance(value, dict) else None


def _quality_lane(envelope: Any, command: str) -> dict[str, Any]:
    payload = _extract_data(envelope, "skill_package_verification")
    if not payload:
        return _missing_lane("quality", command, "receipt_missing")

    status = str(payload.get("status") or "missing")
    blockers = payload.get("blockers")
    blocker_count = len(blockers) if isinstance(blockers, list) else 0
    score = 100 if status in {"pass", "success"} and blocker_count == 0 else 0
    return {
        "score": score,
        "status": "pass" if score == 100 else "blocked",
        "evidence_usable": True,
        "label": "Package verification",
        "command": command,
        "receipt_path": None,
        "absence_reason": None,
        "summary": str(payload.get("agent_summary") or "Package verification evidence was emitted."),
        "details": {
            "source_status": status,
            "blocker_count": blocker_count,
        },
    }


def _impact_lane(envelope: Any, command: str) -> dict[str, Any]:
    payload = _extract_data(envelope, "skills_sdk_eval_scenario_quality")
    if not payload:
        return _missing_lane("impact", command, "receipt_missing")
    receipt = payload.get("receipt")
    if not isinstance(receipt, dict):
        return _missing_lane("impact", command, "receipt_malformed")

    total = int(receipt.get("scenario_count") or 0)
    ready = int(receipt.get("promotion_ready_count") or 0)
    blocked = int(receipt.get("blocked_count") or 0)
    score = round((ready / total) * 100) if total else 0
    return {
        "score": score,
        "status": "pass" if total > 0 and blocked == 0 else "blocked",
        "evidence_usable": True,
        "label": "Scenario quality",
        "command": command,
        "receipt_path": None,
        "absence_reason": None,
        "summary": str(receipt.get("agent_summary") or "Scenario quality evidence was emitted."),
        "details": {
            "ready_count": ready,
            "total_count": total,
            "blocked_count": blocked,
        },
    }


def _security_lane(envelope: Any, command: str) -> dict[str, Any]:
    payload = _extract_data(envelope, "skills_sdk_risk_mode_taxonomy")
    if not payload:
        return _missing_lane("security", command, "receipt_missing")
    receipt = payload.get("receipt")
    if not isinstance(receipt, dict):
        return _missing_lane("security", command, "receipt_malformed")

    detected_results = [
        result
        for result in receipt.get("mode_results", [])
        if isinstance(result, dict) and result.get("status") == "detected"
    ]
    penalty = sum(SEVERITY_PENALTIES.get(str(result.get("severity")), 0) for result in detected_results)
    score = max(0, 100 - penalty)
    risk_count = len(detected_results)
    status = "pass" if risk_count == 0 else "flagged"
    severity_counts: dict[str, int] = {}
    for result in detected_results:
        severity = str(result.get("severity") or "unknown")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    severity_summary = ", ".join(
        f"{count} {severity}" for severity, count in sorted(severity_counts.items())
    ) or "no detected risk modes"
    return {
        "score": score,
        "status": status,
        "evidence_usable": True,
        "label": "Risk modes",
        "command": command,
        "receipt_path": None,
        "absence_reason": None,
        "summary": str(receipt.get("agent_summary") or "Risk-mode taxonomy evidence was emitted."),
        "details": {
            "risk_count": risk_count,
            "severity_summary": severity_summary,
            "primary_mode": receipt.get("primary_mode"),
            "detected_modes": receipt.get("detected_modes", []),
        },
    }


def _missing_lane(label: str, command: str, absence_reason: str) -> dict[str, Any]:
    return {
        "score": None,
        "status": "missing",
        "evidence_usable": False,
        "label": label,
        "command": command,
        "receipt_path": None,
        "absence_reason": absence_reason,
        "summary": f"{label} evidence is missing.",
        "details": {},
    }


def _score_status(lanes: dict[str, dict[str, Any]]) -> tuple[str, bool, list[str], list[str]]:
    missing = [
        name
        for name, lane in lanes.items()
        if not lane.get("evidence_usable")
    ]
    blocked = [
        name
        for name, lane in lanes.items()
        if lane.get("evidence_usable") and lane.get("status") in {"blocked", "fail", "flagged"}
    ]
    if len(missing) == len(lanes):
        return "blocked", False, missing, blocked
    if missing or blocked:
        return "partial", False, missing, blocked
    return "complete", True, missing, blocked


def _next_action(gate: str, missing: list[str], blocked: list[str], skill_path: str) -> dict[str, str]:
    if missing:
        lane = missing[0]
        return {
            "label": f"Collect {lane} evidence",
            "command": _lane_command(lane, skill_path),
            "reason": f"The {lane} lane has no usable local receipt evidence.",
        }
    if blocked:
        lane = blocked[0]
        return {
            "label": f"Repair {lane} lane",
            "command": _lane_command(lane, skill_path),
            "reason": f"The {lane} lane emitted usable evidence but is not passing.",
        }
    next_gate = _next_gate(gate)
    return {
        "label": "Advance next gate" if next_gate else "Review release evidence",
        "command": f"./bin/ask sdk score local {skill_path} --gate {next_gate} --json --robot" if next_gate else "./bin/ask sdk status --json --robot",
        "reason": "All local score lanes are complete for the current gate." if next_gate else "No later local score gate is defined.",
    }


def _next_gate(gate: str) -> str | None:
    try:
        index = LOCAL_SCORE_GATES.index(gate)
    except ValueError:
        return None
    return LOCAL_SCORE_GATES[index + 1] if index + 1 < len(LOCAL_SCORE_GATES) else None


def _lane_command(lane: str, skill_path: str) -> str:
    if lane == "quality":
        return f"./bin/ask skills package verify {skill_path} --json --robot"
    if lane == "impact":
        return f"./bin/ask sdk eval scenario-quality {skill_path} --preview --json --robot"
    if lane == "security":
        return f"./bin/ask sdk security risk-modes {skill_path} --preview --json --robot"
    return f"./bin/ask sdk score local {skill_path} --json --robot"


def build_local_score_receipt_from_lane_payloads(
    repo_root: Path,
    *,
    source_path: Path,
    query: str,
    gate: str,
    quality_result: Any,
    impact_result: Any,
    security_result: Any,
    generated_at: str | None = None,
    ttl_seconds: int = LOCAL_SCORE_DEFAULT_TTL_SECONDS,
) -> dict[str, Any]:
    source = source_path if source_path.name == "SKILL.md" else source_path / "SKILL.md"
    frontmatter = read_skill_frontmatter_fields(source)
    skill_path = repo_relative(repo_root, source_path)
    skill_name = str(frontmatter.get("name") or source_path.parent.name)
    lanes = {
        "quality": _quality_lane(quality_result, _lane_command("quality", query)),
        "impact": _impact_lane(impact_result, _lane_command("impact", query)),
        "security": _security_lane(security_result, _lane_command("security", query)),
    }
    usable_scores = [
        int(lane["score"])
        for lane in lanes.values()
        if lane.get("evidence_usable") and isinstance(lane.get("score"), int)
    ]
    score_value = round(sum(usable_scores) / len(usable_scores)) if usable_scores else 0
    status, complete, missing, blocked = _score_status(lanes)
    basis = " ".join(
        f"{key[0].upper()}{lane['score'] if lane['score'] is not None else 'NA'}"
        for key, lane in lanes.items()
    )
    now = generated_at or utc_now_iso()
    return {
        "schema_version": LOCAL_SCORE_SCHEMA_VERSION,
        "schema_uri": LOCAL_SCORE_SCHEMA_URI,
        "skill_path": skill_path,
        "skill_name": skill_name,
        "gate": gate,
        "generated_at": now,
        "source_identity": {
            "query": query,
            "source_path": skill_path,
            "source_digest": _first_digest(quality_result, "source_digest"),
            "package_digest": _first_digest(quality_result, "package_digest"),
            "rubric_version": "skills-sdk.local-score.v1",
        },
        "score": {
            "value": score_value,
            "status": status,
            "basis": basis,
            "complete": complete,
        },
        "lanes": lanes,
        "provenance": {
            "source": "local",
            "repo_root": repo_root.as_posix(),
            "sdk_version": "skills-sdk.local-score.v1",
            "ttl_seconds": ttl_seconds,
            "freshness": "fresh",
        },
        "completeness": {
            "complete": complete,
            "missing_lanes": missing,
            "blocked_lanes": blocked,
        },
        "next_action": _next_action(gate, missing, blocked, query),
        "acceptance_trace": LOCAL_SCORE_ACCEPTANCE_TRACE,
    }


def _first_digest(envelope: Any, field: str) -> str | None:
    payload = _extract_data(envelope, "skill_package_verification")
    if not isinstance(payload, dict):
        return None
    value = payload.get(field)
    if isinstance(value, str):
        return value
    receipt = payload.get("receipt")
    if isinstance(receipt, dict) and isinstance(receipt.get(field), str):
        return receipt[field]
    return None


def write_local_score_receipts(repo_root: Path, receipt: dict[str, Any]) -> dict[str, str]:
    skill_name = safe_skill_name_segment(str(receipt["skill_name"]))
    gate = str(receipt["gate"])
    generated_at = str(receipt["generated_at"]).replace(":", "").replace("-", "")
    root = repo_root / ".harness" / "evidence" / "skills-sdk" / "local-score" / skill_name
    history = root / "history"
    history.mkdir(parents=True, exist_ok=True)
    current_path = root / "current.json"
    history_path = history / f"{generated_at}-{gate}.json"
    payload = json.dumps(receipt, indent=2, sort_keys=False) + "\n"
    current_path.write_text(payload, encoding="utf-8")
    history_path.write_text(payload, encoding="utf-8")
    return {
        "current": repo_relative(repo_root, current_path),
        "history": repo_relative(repo_root, history_path),
    }
