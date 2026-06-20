from __future__ import annotations

import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Any


OBSERVABILITY_FEEDBACK_SCHEMA_VERSION = "skills-sdk.observability-feedback-receipt.v0"
OBSERVABILITY_FEEDBACK_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/observability-feedback-receipt.v0.schema.json"
)
OBSERVABILITY_ACCEPTANCE_TRACE = ["PU-026", "FR-003", "FR-008", "SA-003", "VP-026"]
RAW_EVENT_KEYS = frozenset({"prompt", "raw_prompt", "output", "raw_output", "transcript", "messages"})
SHA256_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


class ObservabilityFeedbackError(ValueError):
    def __init__(self, receipt: dict[str, Any]) -> None:
        super().__init__(receipt["agent_summary"])
        self.receipt = receipt


def _sha256_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _path_allowed(repo_root: Path, path: Path) -> bool:
    resolved = path.resolve(strict=False)
    roots = (repo_root.resolve(), Path(tempfile.gettempdir()).resolve(), Path("/private/tmp").resolve(), Path("/tmp").resolve())
    return any(resolved == root or root in resolved.parents for root in roots)


def _check(check_id: str, status: str, message: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {"id": check_id, "status": status, "severity": "blocker", "message": message, "evidence": evidence or []}


def _load_events(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    events: list[dict[str, Any]] = []
    errors: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line:{line_number}:json:{exc.msg}")
            continue
        if isinstance(value, dict):
            events.append(value)
        else:
            errors.append(f"line:{line_number}:not_object")
    return events, errors


def _event_redaction_errors(events: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for index, event in enumerate(events):
        raw_keys = sorted(set(event) & RAW_EVENT_KEYS)
        if raw_keys:
            errors.append(f"event:{index}:raw_keys:{','.join(raw_keys)}")
        if event.get("redacted") is not True:
            errors.append(f"event:{index}:redacted_not_true")
        prompt_digest = event.get("prompt_digest")
        if not isinstance(prompt_digest, str):
            errors.append(f"event:{index}:prompt_digest_missing")
        elif SHA256_DIGEST_RE.fullmatch(prompt_digest) is None:
            errors.append(f"event:{index}:prompt_digest_malformed")
    return errors


def _event_package_errors(events: list[dict[str, Any]], package_id: str) -> list[str]:
    errors: list[str] = []
    for index, event in enumerate(events):
        skill_id = event.get("skill_id")
        if skill_id != package_id:
            errors.append(f"event:{index}:skill_id:{skill_id!s}:expected:{package_id}")
    return errors


def _scenario_candidate(event: dict[str, Any], index: int) -> dict[str, Any]:
    event_digest = _sha256_json(event)
    return {
        "id": f"eval-scenario-{event_digest.removeprefix('sha256:')[:12]}",
        "candidate_type": "eval_scenario",
        "source_event_digest": event_digest,
        "skill_id": str(event.get("skill_id") or "unknown"),
        "prompt_digest": str(event.get("prompt_digest")),
        "failure_summary": str(event.get("failure_summary") or event.get("summary") or f"event {index} needs review"),
        "promotion_status": "blocked_pending_package_eval",
        "required_receipts": ["package_digest_receipt", "eval_run_receipt"],
    }


def _skill_gap_candidate(event: dict[str, Any], index: int) -> dict[str, Any]:
    event_digest = _sha256_json({"gap": event})
    return {
        "id": f"skill-gap-{event_digest.removeprefix('sha256:')[:12]}",
        "candidate_type": "skill_gap",
        "source_event_digest": _sha256_json(event),
        "skill_id": str(event.get("skill_id") or "unknown"),
        "gap_summary": str(event.get("gap_summary") or event.get("failure_summary") or f"event {index} suggests a gap"),
        "promotion_status": "blocked_pending_package_eval",
        "required_receipts": ["package_digest_receipt", "eval_run_receipt"],
    }


def _candidate_events(events: list[dict[str, Any]]) -> list[tuple[int, dict[str, Any]]]:
    return [(index, event) for index, event in enumerate(events) if str(event.get("outcome") or "").lower() != "pass"]


def _receipt(
    repo_root: Path,
    package_receipt: dict[str, Any],
    events_path: Path,
    events: list[dict[str, Any]],
    checks: list[dict[str, Any]],
) -> dict[str, Any]:
    blockers = [check for check in checks if check["status"] == "blocker"]
    candidate_events = _candidate_events(events) if not blockers else []
    scenario_candidates = [_scenario_candidate(event, index) for index, event in candidate_events]
    gap_candidates = [_skill_gap_candidate(event, index) for index, event in candidate_events]
    return {
        "schema_version": OBSERVABILITY_FEEDBACK_SCHEMA_VERSION,
        "schema_uri": OBSERVABILITY_FEEDBACK_SCHEMA_URI,
        "status": "blocked" if blockers else "preview",
        "operation": "observability_feedback_preview",
        "package_id": package_receipt["package_id"],
        "package_digest": package_receipt["package_digest"],
        "events_path": _repo_relative(repo_root, events_path),
        "event_count": len(events),
        "accepted_event_count": 0 if blockers else len(events),
        "scenario_candidates": scenario_candidates,
        "skill_gap_candidates": gap_candidates,
        "promotion_blockers": ["package_digest_receipt", "eval_run_receipt"] if scenario_candidates or gap_candidates else [],
        "feedback_checks": checks,
        "blockers": blockers,
        "mutation_performed": False,
        "acceptance_trace": OBSERVABILITY_ACCEPTANCE_TRACE,
        "agent_summary": f"observability feedback preview produced {len(scenario_candidates)} scenario candidate(s) and {len(gap_candidates)} skill gap candidate(s).",
    }


def build_observability_feedback_receipt(
    repo_root: Path,
    *,
    package_receipt: dict[str, Any],
    events_path: str,
) -> dict[str, Any]:
    events = Path(events_path)
    if not events.is_absolute():
        events = repo_root / events
    path_allowed = _path_allowed(repo_root, events)
    checks = [_check("events_path_allowed", "pass" if path_allowed else "blocker", "Events input must stay inside the repository or a temporary test path.", [_repo_relative(repo_root, events)])]
    if not path_allowed:
        receipt = _receipt(repo_root, package_receipt, events, [], checks)
        raise ObservabilityFeedbackError(receipt)
    if events.is_file():
        loaded_events, load_errors = _load_events(events)
    else:
        loaded_events, load_errors = [], [f"missing:{_repo_relative(repo_root, events)}"]
    checks.append(_check("events_jsonl_parse", "blocker" if load_errors else "pass", "Events input must be JSONL object records.", load_errors))
    redaction_errors = _event_redaction_errors(loaded_events)
    checks.append(_check("events_redacted", "blocker" if redaction_errors else "pass", "Events must be redacted and carry digest references instead of raw prompts or outputs.", redaction_errors))
    package_errors = _event_package_errors(loaded_events, str(package_receipt["package_id"]))
    checks.append(_check("events_package_bound", "blocker" if package_errors else "pass", "Events must match the selected package id before feedback candidates can be promoted.", package_errors))
    receipt = _receipt(repo_root, package_receipt, events, loaded_events, checks)
    if receipt["status"] == "blocked":
        raise ObservabilityFeedbackError(receipt)
    return receipt
