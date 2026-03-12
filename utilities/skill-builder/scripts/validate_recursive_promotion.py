#!/usr/bin/env python3
"""Validate recursive-loop human promotion decisions against run evidence."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import sys
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

ALLOWED_DECISIONS = {"draft", "candidate", "approved", "rejected"}
ALLOWED_STOP_REASONS = {
    "pass",
    "budget_exhausted",
    "escalated",
    "aborted",
    "policy_failed",
    "evaluator_conflict",
    "dependency_missing",
}
ALLOWED_TERMINAL_STATUSES = {"passed", "failed", "escalated", "aborted"}

DEFAULT_POLICY_FILE = "docs/skill-graphs/governance/recursive-loop-approvers.yaml"
DEFAULT_POLICY_SIG_FILE = "docs/skill-graphs/governance/recursive-loop-approvers.sig"

RUN_REQUIRED_FILES = {"run.json", "iteration_journal.jsonl", "events.jsonl", "promotion_decision.json"}
CONTROL_CAPTURE_FILES = {
    "capture_record.json",
    "evidence_packet.json",
    "lesson_candidates.json",
}
CONTROL_BLOCKER_REQUIRED_FILES = {
    "run_rollforward_blocked": {"run_blocker.json", "rollback_recommendation.json"},
    "run_rollback_required": {"run_blocker.json", "rollback_recommendation.json"},
    "kill_switch_activated": {"run_blocker.json", "rollback_recommendation.json"},
    "evaluator_conflict": {"run_blocker.json"},
}
LEGACY_OPTIONAL_FILES = {
    "promotion_decision.template.json",
}
LEGACY_LAYOUT_FILES = {
    "run.json",
    "iteration_journal.jsonl",
    "promotion_decision.json",
    "promotion_decision.template.json",
}
LEGACY_RELAXED_FILE_SETS = {
    frozenset({"run.json", "iteration_journal.jsonl", "promotion_decision.json"}),
    frozenset({"run.json", "iteration_journal.jsonl", "promotion_decision.json", "promotion_decision.template.json"}),
}
STOP_REASON_TO_BLOCKER: Dict[str, str] = {
    "policy_failed": "run_rollforward_blocked",
    "dependency_missing": "run_rollback_required",
    "evaluator_conflict": "evaluator_conflict",
    "aborted": "kill_switch_activated",
}
TERMINAL_STOP_TO_BLOCKER: Dict[str, Dict[str, str]] = {
    "failed": {
        "policy_failed": "run_rollforward_blocked",
        "dependency_missing": "run_rollback_required",
    },
    "escalated": {
        "evaluator_conflict": "evaluator_conflict",
    },
    "aborted": {
        "aborted": "kill_switch_activated",
    },
}

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{30,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)aws_access_key_id\s*[:=]\s*[A-Z0-9]{16,}"),
    re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{8,}"),
]
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate recursive promotion decision artifact")
    p.add_argument("--run-dir", required=True, help="Path to run artifact directory")
    p.add_argument(
        "--decision-file",
        help="Promotion decision file path (default: <run-dir>/promotion_decision.json)",
    )
    p.add_argument("--lesson-file", help="Optional lesson content file to scan for secrets/PII")
    p.add_argument(
        "--skip-lesson-content-scan",
        action="store_true",
        help="Allow approved decisions without lesson content scan",
    )
    p.add_argument(
        "--policy-file",
        default=DEFAULT_POLICY_FILE,
        help="Reviewer policy file (JSON content in .yaml path is supported)",
    )
    p.add_argument(
        "--policy-sig-file",
        default=DEFAULT_POLICY_SIG_FILE,
        help="Policy signature file containing sha256(policy file)",
    )
    # C-01: HMAC-SHA256 decision integrity
    p.add_argument(
        "--decision-sig-file",
        help="Path to HMAC-SHA256 signature file for promotion_decision.json (written by human_promote_recursive_run.sh)",
    )
    p.add_argument(
        "--require-sig",
        action="store_true",
        default=bool(os.environ.get("PROMOTION_SIG_REQUIRED", "").strip() in {"1", "true", "TRUE", "yes"}),
        help="Hard-fail if no decision signature file is present (set via PROMOTION_SIG_REQUIRED=1 in CI)",
    )
    p.add_argument("--write-report", help="Optional JSON output path for validation report")
    return p.parse_args()


def add_error(errors: List[Dict[str, str]], code: str, message: str) -> None:
    errors.append({"code": code, "message": message})


def add_warning(warnings: List[Dict[str, str]], code: str, message: str) -> None:
    warnings.append({"code": code, "message": message})


def required_fields(
    obj: Dict[str, Any],
    fields: List[str],
    prefix: str,
    code: str,
    errors: List[Dict[str, str]],
) -> None:
    for field in fields:
        if field not in obj:
            add_error(errors, code, f"{prefix} missing field: {field}")


def schema_version_at_least(version: str, minimum: str) -> bool:
    def parse(raw: str) -> List[int]:
        parts: List[int] = []
        for token in str(raw or "").split("."):
            token = token.strip()
            if not token:
                continue
            try:
                parts.append(int(token))
            except Exception:
                parts.append(0)
        return parts or [0]

    left = parse(version)
    right = parse(minimum)
    max_len = max(len(left), len(right))
    left.extend([0] * (max_len - len(left)))
    right.extend([0] * (max_len - len(right)))
    return left >= right


def load_json(path: Path) -> Dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"JSON root must be object: {path}")
    return obj


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL line {i} in {path}: {exc}") from exc
        if not isinstance(obj, dict):
            raise ValueError(f"invalid JSONL object at line {i} in {path}")
        rows.append(obj)
    return rows


def locate_repo_root(start_dir: Path) -> Path:
    """Resolve the repository root from ``start_dir``, falling back to known roots.

    Tests and callers may construct run directories in temp paths, so this helper
    walks upward to find ``.git`` and falls back to the validator location or cwd.
    """
    cur = start_dir
    while cur != cur.parent:
        if (cur / ".git").exists():
            return cur
        cur = cur.parent
    if (cur / ".git").exists():
        return cur

    script_root = Path(__file__).resolve()
    fallback_roots = [Path.cwd().resolve(), script_root.parents[3] if len(script_root.parents) >= 4 else script_root]
    for candidate in fallback_roots:
        if (candidate / ".git").exists():
            return candidate

    return Path.cwd().resolve()


def sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_decision_hmac(
    decision_path: Path,
    sig_path: Path,
    errors: List[Dict[str, str]],
    warnings: List[Dict[str, str]],
    require_key: bool = False,
) -> bool:
    """Verify the HMAC-SHA256 signature of a promotion decision file.

    The key is read from the PROMOTION_SIGNING_KEY environment variable.  Uses
    ``hmac.compare_digest`` for constant-time comparison to prevent timing
    attacks.

    When ``require_key`` is True (i.e. --require-sig was set), a missing or
    empty PROMOTION_SIGNING_KEY is treated as a hard verification failure rather
    than a silent skip.  This prevents a misconfigured runner from accepting any
    sig file without actually verifying the MAC.

    Returns True if verification passed.
    Returns False and appends an error if verification fails.
    """
    key_raw = os.environ.get("PROMOTION_SIGNING_KEY", "").strip()
    if not key_raw:
        if require_key:
            add_error(
                errors,
                "E_DECISION_SIG_KEY_MISSING",
                "PROMOTION_SIGNING_KEY is not set — cannot verify signature (--require-sig enforces key presence)",
            )
            return False
        # Key not set and not required — skip silently (backwards-compatible).
        return True

    try:
        sig_line = sig_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        add_error(errors, "E_DECISION_SIG_READ_FAILED", f"cannot read sig file: {exc}")
        return False

    if not sig_line.startswith("hmac-sha256:"):
        add_error(errors, "E_DECISION_SIG_FORMAT", f"unexpected sig format (expected 'hmac-sha256:<hex>'): {sig_path}")
        return False

    recorded_mac = sig_line[len("hmac-sha256:"):].strip()
    try:
        obj = json.loads(decision_path.read_text(encoding="utf-8"))
        canonical = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    except Exception as exc:
        add_error(errors, "E_DECISION_SIG_CANONICAL_FAILED", f"cannot canonicalise decision for sig check: {exc}")
        return False

    key = key_raw.encode("utf-8")
    expected_mac = hmac.new(key, canonical, sha256).hexdigest()
    if not hmac.compare_digest(recorded_mac, expected_mac):
        add_error(
            errors,
            "E_DECISION_SIG_MISMATCH",
            "HMAC-SHA256 signature mismatch — promotion_decision.json may have been tampered with",
        )
        return False

    return True


def scan_lesson_content(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    secret_hit_count: int = 0
    pii_hits: List[str] = []

    for idx, line in enumerate(text.splitlines(), start=1):
        for pattern in SECRET_PATTERNS:
            if pattern.search(line):
                # Increment a counter instead of recording potentially sensitive context.
                secret_hit_count += 1
                break

        for match in EMAIL_PATTERN.findall(line):
            lower = match.lower()
            if lower.endswith("@example.com") or lower.endswith("@test.com"):
                continue
            pii_hits.append(f"line {idx}: email-like identifier '{match}'")

    return {"secret_hit_count": secret_hit_count, "pii_hits": pii_hits}


def load_policy(policy_file: Path, sig_file: Path) -> Dict[str, Any]:
    policy_raw = policy_file.read_text(encoding="utf-8")
    recorded_sig = sig_file.read_text(encoding="utf-8").strip().split()[0]
    actual_sig = hashlib.sha256(policy_raw.encode("utf-8")).hexdigest()
    if recorded_sig != actual_sig:
        raise ValueError("reviewer policy signature mismatch")
    policy = json.loads(policy_raw)
    if not isinstance(policy, dict):
        raise ValueError("reviewer policy must be object")
    return policy


def resolve_lesson_file(
    *,
    args: argparse.Namespace,
    decision: Dict[str, Any],
    repo_root: Path,
    run_dir: Path,
    errors: List[Dict[str, str]],
) -> Optional[Path]:
    if args.lesson_file:
        lesson_file = Path(args.lesson_file).expanduser().resolve()
        if not lesson_file.exists():
            add_error(errors, "E_LESSON_FILE_NOT_FOUND", f"lesson file not found: {lesson_file}")
            return None
        return lesson_file

    source_path = decision.get("lesson_source_path")
    if isinstance(source_path, str) and source_path.strip():
        raw = source_path.strip()
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = (repo_root / candidate).resolve()
        if candidate.exists():
            return candidate
        candidate_run = (run_dir / raw).resolve()
        if candidate_run.exists():
            return candidate_run
        add_error(
            errors,
            "E_LESSON_SOURCE_MISSING",
            f"lesson_source_path does not resolve to a file: {source_path}",
        )
        return None

    if args.skip_lesson_content_scan:
        return None

    add_error(
        errors,
        "E_LESSON_SCAN_REQUIRED",
        "approved decision requires lesson content scan (provide --lesson-file or lesson_source_path)",
    )
    return None


def normalize_blocker_code(terminal_status: Optional[str], stop_reason: Optional[str]) -> Optional[str]:
    status = str(terminal_status or "").strip().lower()
    reason = str(stop_reason or "").strip().lower()
    if reason in STOP_REASON_TO_BLOCKER:
        candidate = STOP_REASON_TO_BLOCKER[reason]
        if status in TERMINAL_STOP_TO_BLOCKER:
            mapped = TERMINAL_STOP_TO_BLOCKER[status].get(reason)
            if mapped:
                return mapped
        if candidate == "kill_switch_activated" and status != "aborted":
            return None
        return candidate
    if status in TERMINAL_STOP_TO_BLOCKER and reason:
        return TERMINAL_STOP_TO_BLOCKER[status].get(reason)
    return None


def is_legacy_relaxed_layout(run: Dict[str, Any], decision: Dict[str, Any], artifact_files: Set[str]) -> bool:
    run_version = str(run.get("schema_version", "")).strip() or "0"
    decision_version = str(decision.get("schema_version", "")).strip() or "0"
    if schema_version_at_least(run_version, "1.1") or schema_version_at_least(decision_version, "1.1"):
        return False

    runtime_controls = run.get("runtime_controls")
    if isinstance(runtime_controls, dict) and runtime_controls:
        return False

    normalized_files = {name for name in artifact_files if name in LEGACY_LAYOUT_FILES and name not in LEGACY_OPTIONAL_FILES}
    return frozenset(normalized_files) in {
        frozenset(files - LEGACY_OPTIONAL_FILES)
        for files in LEGACY_RELAXED_FILE_SETS
    }


def validate_event_rows(
    events: List[Dict[str, Any]],
    run_id: str,
    errors: List[Dict[str, str]],
    warnings: List[Dict[str, str]],
) -> Set[str]:
    blocker_codes: Set[str] = set()
    has_state_change = False
    has_approved = False

    required = {
        "schema_version",
        "event_id",
        "ts",
        "run_id",
        "event_type",
        "severity",
        "terminal_status",
        "stop_reason",
    }

    allowed_event_types = {
        "run_initialized",
        "run_state_changed",
        "run_blocked",
        "promotion_approved",
        "run_completed",
        "failure_event",
        "run_aborted",
    }

    for idx, row in enumerate(events, start=1):
        missing = [key for key in required if key not in row]
        if missing:
            add_error(
                errors,
                "E_EVENT_REQUIRED_FIELD_MISSING",
                f"event row {idx} missing fields: {', '.join(sorted(missing))}",
            )
            continue

        event_type = str(row.get("event_type", "")).strip()
        row_run_id = str(row.get("run_id", ""))
        if row_run_id and row_run_id != run_id:
            add_warning(
                warnings,
                "W_EVENT_RUN_ID_MISMATCH",
                f"event row {idx} run_id does not match run_id ({row_run_id} != {run_id})",
            )

        if event_type not in allowed_event_types:
            add_warning(warnings, "W_EVENT_UNKNOWN_TYPE", f"event row {idx} has unknown event_type={event_type}")
        if event_type == "run_state_changed":
            has_state_change = True
        if event_type == "promotion_approved":
            has_approved = True
        if event_type == "run_blocked":
            code = str(row.get("blocker_code", "")).strip()
            if not code:
                add_error(
                    errors,
                    "E_EVENT_BLOCKER_CODE_MISSING",
                    f"event row {idx} run_blocked missing blocker_code",
                )
            else:
                blocker_codes.add(code)

    if not has_state_change:
        add_warning(
            warnings,
            "W_EVENT_STATE_CHANGED_MISSING",
            "events.jsonl does not include a run_state_changed event",
        )

    # Keep behavior stable with older callers that check for explicit approval event.
    # Approved decisions will enforce this separately in schema checks.
    _ = has_approved
    return blocker_codes


def validate(args: argparse.Namespace) -> Dict[str, Any]:
    errors: List[Dict[str, str]] = []
    warnings: List[Dict[str, str]] = []

    run_dir = Path(args.run_dir).expanduser().resolve()
    repo_root = locate_repo_root(run_dir)

    run_json_path = run_dir / "run.json"
    journal_path = run_dir / "iteration_journal.jsonl"
    events_path = run_dir / "events.jsonl"
    decision_path = (
        Path(args.decision_file).expanduser().resolve()
        if args.decision_file
        else run_dir / "promotion_decision.json"
    )
    artifact_files = {p.name for p in run_dir.glob("*") if p.is_file()}

    # C-01: Verify HMAC-SHA256 signature before any schema or policy checks.
    sig_file_arg = getattr(args, "decision_sig_file", None)
    require_sig = getattr(args, "require_sig", False)
    if sig_file_arg:
        sig_path = Path(sig_file_arg).expanduser().resolve()
        if sig_path.exists() and decision_path.exists():
            verify_decision_hmac(decision_path, sig_path, errors, warnings, require_key=require_sig)
        elif not sig_path.exists():
            add_error(errors, "E_DECISION_SIG_MISSING", f"--decision-sig-file specified but not found: {sig_path}")
    elif require_sig:
        add_error(
            errors,
            "E_DECISION_SIG_MISSING",
            "PROMOTION_SIG_REQUIRED=1 but no --decision-sig-file was provided",
        )
    # No sig file, no require_sig → backwards-compatible: validation proceeds without sig check.

    if str(decision_path) == str(run_json_path):
        add_warning(
            warnings,
            "W_DECISION_PATH_MISCONFIG",
            "decision file resolves to run.json; expected promotion_decision.json",
        )

    decision_file_out = (
        str(decision_path.relative_to(repo_root))
        if decision_path.is_relative_to(repo_root)
        else str(decision_path)
    )

    for required_file in (run_json_path, journal_path, decision_path):
        if not required_file.exists():
            add_error(errors, "E_REQUIRED_ARTIFACT_MISSING", f"missing required file: {required_file.name}")

    run: Dict[str, Any] = {}
    if run_json_path.exists():
        try:
            run = load_json(run_json_path)
        except Exception as exc:
            add_error(errors, "E_RUN_JSON_INVALID", f"invalid run.json: {exc}")

    journal_rows: List[Dict[str, Any]] = []
    if journal_path.exists():
        try:
            journal_rows = load_jsonl(journal_path)
        except Exception as exc:
            add_error(errors, "E_JOURNAL_JSONL_INVALID", f"invalid iteration_journal.jsonl: {exc}")

    decision: Dict[str, Any] = {}
    if decision_path.exists():
        try:
            decision = load_json(decision_path)
        except Exception as exc:
            add_error(errors, "E_DECISION_JSON_INVALID", f"invalid decision file: {exc}")

    if not run or not decision:
        report = {
            "validator": "recursive_promotion",
            "run_id": str(run.get("run_id", "")) if run else None,
            "decision_file": decision_file_out,
            "status": "fail",
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": errors,
            "warnings": warnings,
            "decision": str(decision.get("decision", "")) if decision else "",
        }
        if args.write_report:
            report_path = Path(args.write_report).expanduser().resolve()
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return report

    decision_state = str(decision.get("decision", "")).strip().lower()
    legacy_relaxed_layout = is_legacy_relaxed_layout(run, decision, artifact_files)
    if not events_path.exists():
        if legacy_relaxed_layout and decision_state != "approved":
            add_warning(
                warnings,
                "W_LEGACY_EVENTS_FILE_MISSING",
                "events.jsonl missing for legacy promotion layout; tolerated for historical run",
            )
        else:
            add_error(errors, "E_REQUIRED_ARTIFACT_MISSING", "missing required file: events.jsonl")

    control_obj = run.get("runtime_controls", {}) if isinstance(run.get("runtime_controls"), dict) else {}
    auto_capture_enabled = bool(control_obj.get("auto_capture_enabled", True))

    terminal_status = str(run.get("terminal_status", "")).strip().lower() or None
    stop_reason = str(run.get("stop_reason", "")).strip().lower() or None

    if terminal_status and terminal_status not in ALLOWED_TERMINAL_STATUSES:
        add_error(errors, "E_INVALID_TERMINAL_STATUS", f"unknown terminal_status: {terminal_status}")
        terminal_status = None
    if stop_reason and stop_reason not in ALLOWED_STOP_REASONS:
        add_error(errors, "E_INVALID_STOP_REASON", f"unknown stop_reason: {stop_reason}")
        stop_reason = None

    blocker_code_run = None
    run_blocker = run.get("run_blocker")
    if isinstance(run_blocker, dict):
        blocker_code_run = str(run_blocker.get("code", "")).strip() or None

    expected_blocker = normalize_blocker_code(terminal_status, stop_reason)

    require_events_for_validation = decision_state == "approved" or bool(expected_blocker)

    required_artifacts = {"run.json", "iteration_journal.jsonl", "promotion_decision.json"}
    if not legacy_relaxed_layout or require_events_for_validation:
        required_artifacts.add("events.jsonl")
    if auto_capture_enabled and not legacy_relaxed_layout:
        required_artifacts.update(CONTROL_CAPTURE_FILES)

    if blocker_code_run:
        blocker_key = blocker_code_run
        required_artifacts.update(CONTROL_BLOCKER_REQUIRED_FILES.get(blocker_key, set()))
    elif expected_blocker:
        required_artifacts.update(CONTROL_BLOCKER_REQUIRED_FILES.get(expected_blocker, set()))

    # Re-check after reading runtime controls and blocker state.
    for file_name in sorted(required_artifacts):
        if file_name == "promotion_decision.json":
            target = decision_path
        elif file_name == "run.json":
            target = run_json_path
        elif file_name == "iteration_journal.jsonl":
            target = journal_path
        elif file_name == "events.jsonl":
            target = events_path
        else:
            target = run_dir / file_name
        if not target.exists():
            add_error(errors, "E_REQUIRED_ARTIFACT_MISSING", f"missing required file: {file_name}")

    run_id = str(run.get("run_id", "")).strip()
    if not run_id:
        add_error(errors, "E_RUN_ID_MISSING", "run.json missing run_id")

    required_fields(
        run,
        ["run_id", "schema_version", "terminal_status", "stop_reason", "prompt_hash", "versions", "counters"],
        "run",
        "E_RUN_MISSING_FIELD",
        errors,
    )

    required_fields(
        decision,
        ["schema_version", "run_id", "lesson_id", "decision", "reviewer_ids", "expected_version", "provenance"],
        "promotion_decision",
        "E_DECISION_MISSING_FIELD",
        errors,
    )

    if decision_state not in ALLOWED_DECISIONS:
        add_error(errors, "E_INVALID_DECISION_STATE", f"invalid decision state: {decision_state}")

    decision_run_id = str(decision.get("run_id", "")).strip()
    if run_id and decision_run_id and run_id != decision_run_id:
        add_error(
            errors,
            "E_RUN_ID_MISMATCH",
            f"run_id mismatch: run.json={run_id} decision={decision_run_id}",
        )

    if decision_state in {"approved", "candidate"}:
        if not str(decision.get("lesson_id", "")).strip():
            add_error(errors, "E_LESSON_ID_MISSING", "lesson_id is required for candidate/approved decisions")

        reviewers = decision.get("reviewer_ids")
        if not isinstance(reviewers, list) or not any(str(r).strip() for r in reviewers):
            add_error(errors, "E_REVIEWER_IDS_MISSING", "reviewer_ids must include at least one reviewer")

        if not str(decision.get("expected_version", "")).strip():
            add_error(errors, "E_EXPECTED_VERSION_MISSING", "expected_version is required")

        policy_file = Path(args.policy_file).expanduser().resolve()
        sig_file = Path(args.policy_sig_file).expanduser().resolve()
        allow_policy_override = os.environ.get("RECURSIVE_PROMOTION_ALLOW_POLICY_OVERRIDE", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        canonical_policy = (repo_root / DEFAULT_POLICY_FILE).resolve()
        canonical_policy_sig = (repo_root / DEFAULT_POLICY_SIG_FILE).resolve()

        if not allow_policy_override:
            if policy_file != canonical_policy:
                add_error(
                    errors,
                    "E_POLICY_FILE_NON_CANONICAL",
                    f"non-canonical policy-file not allowed: {policy_file}",
                )
            if sig_file != canonical_policy_sig:
                add_error(
                    errors,
                    "E_POLICY_SIG_NON_CANONICAL",
                    f"non-canonical policy-sig-file not allowed: {sig_file}",
                )

        if not policy_file.exists():
            add_error(errors, "E_POLICY_FILE_MISSING", f"reviewer policy file missing: {policy_file}")
        if not sig_file.exists():
            add_error(errors, "E_POLICY_SIG_MISSING", f"reviewer policy signature missing: {sig_file}")
        if policy_file.exists() and sig_file.exists():
            try:
                policy = load_policy(policy_file, sig_file)
                allowed_map = {
                    str(r.get("id", "")).strip(): str(r.get("role", "")).strip().lower()
                    for r in policy.get("reviewers", [])
                    if isinstance(r, dict) and str(r.get("id", "")).strip()
                }
                min_roles = {
                    str(role).strip().lower()
                    for role in policy.get("min_roles_for_approve", ["approver"])
                    if str(role).strip()
                } or {"approver"}
                for reviewer in reviewers or []:
                    rv = str(reviewer).strip()
                    if rv not in allowed_map:
                        add_error(errors, "E_REVIEWER_NOT_ALLOWLISTED", f"reviewer not allowlisted: {rv}")
                        continue
                    if allowed_map[rv] not in min_roles:
                        add_error(
                            errors,
                            "E_REVIEWER_ROLE_INSUFFICIENT",
                            f"reviewer role not permitted: {rv}:{allowed_map[rv]}",
                        )
            except Exception as exc:
                add_error(errors, "E_POLICY_VALIDATION_FAILED", f"reviewer policy validation failed: {exc}")

    confidence_obj = decision.get("confidence")
    if confidence_obj is None:
        add_warning(warnings, "W_CONFIDENCE_MISSING", "confidence object missing (Phase-4 queue enrichment expected)")
    elif not isinstance(confidence_obj, dict):
        add_error(errors, "E_CONFIDENCE_INVALID", "confidence must be an object")
    else:
        score = confidence_obj.get("score")
        if score is None:
            add_warning(warnings, "W_CONFIDENCE_SCORE_MISSING", "confidence.score missing (Phase-4 queue enrichment expected)")
        else:
            try:
                score_f = float(score)
                if score_f < 0.0 or score_f > 1.0:
                    add_error(errors, "E_CONFIDENCE_SCORE_OUT_OF_RANGE", "confidence.score must be between 0 and 1")
            except Exception:
                add_error(errors, "E_CONFIDENCE_SCORE_INVALID", "confidence.score must be numeric")

        bucket = str(confidence_obj.get("bucket", "")).strip().lower()
        if bucket and bucket not in {"high", "medium", "low"}:
            add_error(errors, "E_CONFIDENCE_BUCKET_INVALID", "confidence.bucket must be one of high|medium|low")

    evidence_obj = decision.get("evidence_packet")
    if isinstance(evidence_obj, dict):
        completeness = evidence_obj.get("completeness_score")
        if completeness is not None:
            try:
                completeness_f = float(completeness)
                if completeness_f < 0.0 or completeness_f > 1.0:
                    add_error(
                        errors,
                        "E_EVIDENCE_COMPLTENESS_SCORE_OUT_OF_RANGE",
                        "evidence_packet.completeness_score must be between 0 and 1",
                    )
            except Exception:
                add_error(errors, "E_EVIDENCE_COMPLTENESS_SCORE_INVALID", "evidence_packet.completeness_score must be numeric")

    gate = decision.get("gate_decision")
    if not isinstance(gate, dict):
        add_error(errors, "E_GATE_MISSING", "gate_decision must be an object")
        gate = {}

    provenance = decision.get("provenance")
    if not isinstance(provenance, dict):
        add_error(errors, "E_PROVENANCE_INVALID", "provenance must be an object")
        provenance = {}

    if decision_state == "approved":
        if args.skip_lesson_content_scan:
            add_error(errors, "E_SKIP_SCAN_NOT_ALLOWED", "approved decision cannot use --skip-lesson-content-scan")

        if terminal_status != "passed":
            add_error(errors, "E_APPROVED_NOT_PASSED", "approved decision requires run terminal_status=passed")
        if stop_reason != "pass":
            add_error(errors, "E_APPROVED_NOT_PASSED", "approved decision requires run stop_reason=pass")

        if gate.get("runtime_gates_passed") is not True:
            add_error(errors, "E_APPROVED_RUNTIME_GATE", "gate_decision.runtime_gates_passed must be true for approved decision")
        if gate.get("provenance_complete") is not True:
            add_error(errors, "E_APPROVED_PROVENANCE", "gate_decision.provenance_complete must be true for approved decision")
        if gate.get("security_checklist_passed") is not True:
            add_error(errors, "E_APPROVED_SECURITY", "gate_decision.security_checklist_passed must be true for approved decision")

    # Control-state-specific expectations.
    if expected_blocker:
        blocker_json = run_dir / "run_blocker.json"
        if not blocker_json.exists():
            add_error(
                errors,
                "E_BLOCKER_ARTIFACT_MISSING",
                f"blocked terminal_state requires run_blocker.json for {expected_blocker}",
            )
        else:
            try:
                blocker_obj = load_json(blocker_json)
                blocker_code_artifact = str(blocker_obj.get("code", "")).strip() or None
                if blocker_code_run and blocker_code_artifact and blocker_code_artifact != blocker_code_run:
                    add_error(
                        errors,
                        "E_BLOCKER_CODE_MISMATCH",
                        "run_blocker.json code does not match run.run_blocker.code",
                    )
                if blocker_code_artifact != expected_blocker:
                    add_error(
                        errors,
                        "E_BLOCKER_CODE_MISMATCH",
                        f"expected blocker code {expected_blocker} for terminal state {terminal_status}/{stop_reason}",
                    )
            except Exception as exc:
                add_error(errors, "E_BLOCKER_JSON_INVALID", f"invalid run_blocker.json: {exc}")

        if expected_blocker in {"run_rollforward_blocked", "run_rollback_required", "kill_switch_activated"}:
            if not (run_dir / "rollback_recommendation.json").exists():
                add_error(
                    errors,
                    "E_ROLLBACK_RECOMMENDATION_MISSING",
                    f"blocked terminal_state requires rollback_recommendation.json for {expected_blocker}",
                )

    # Journal checks.
    if terminal_status == "passed" and stop_reason == "pass" and decision_state in {"approved", "candidate"}:
        if not journal_rows:
            add_warning(
                warnings,
                "W_JOURNAL_EMPTY",
                "run journal has no rows for terminal passing run",
            )

    journal_ids: Set[int] = set()
    for row in journal_rows:
        if not isinstance(row, dict):
            continue
        iteration_id = row.get("iteration_id")
        if isinstance(iteration_id, int):
            journal_ids.add(iteration_id)
        else:
            add_error(
                errors,
                "E_JOURNAL_ITERATION_ID_INVALID",
                "iteration_journal iteration_id must be an integer",
            )

    if decision_state in {"approved", "candidate"}:
        required_fields(
            provenance,
            ["prompt_hash", "rubric_version", "evaluator_version", "iteration_ids"],
            "provenance",
            "E_PROVENANCE_MISSING_FIELD",
            errors,
        )

        prov_ids_raw = provenance.get("iteration_ids")
        if isinstance(prov_ids_raw, list) and prov_ids_raw:
            if any(not isinstance(x, int) for x in prov_ids_raw):
                add_error(errors, "E_PROVENANCE_ITERATION_IDS_TYPE", "provenance.iteration_ids must contain only integers")
            prov_ids = {int(x) for x in prov_ids_raw if isinstance(x, int)}
        else:
            prov_ids = set()
            if not isinstance(prov_ids_raw, list):
                add_error(errors, "E_PROVENANCE_ITERATION_IDS_TYPE", "provenance.iteration_ids must be an array of integers")

        if prov_ids and not prov_ids.issubset(journal_ids):
            add_error(
                errors,
                "E_PROVENANCE_ITERATION_IDS_MISMATCH",
                "provenance.iteration_ids must reference existing iteration ids",
            )

        if provenance.get("prompt_hash") != run.get("prompt_hash"):
            add_error(errors, "E_PROMPT_HASH_MISMATCH", "provenance.prompt_hash mismatch with run.prompt_hash")

        versions = run.get("versions", {}) if isinstance(run.get("versions"), dict) else {}
        if provenance.get("rubric_version") != versions.get("rubric_version"):
            add_error(errors, "E_VERSION_MISMATCH", "provenance.rubric_version mismatch with run.versions.rubric_version")
        if provenance.get("evaluator_version") != versions.get("evaluator_version"):
            add_error(errors, "E_VERSION_MISMATCH", "provenance.evaluator_version mismatch with run.versions.evaluator_version")

        if journal_rows:
            last_row = journal_rows[-1]
            if isinstance(last_row, dict):
                last_gate = (
                    last_row.get("reevaluation_report", {}).get("gate_decision")
                    if isinstance(last_row.get("reevaluation_report"), dict)
                    else None
                )
                if decision_state == "approved" and last_gate != "pass":
                    add_error(
                        errors,
                        "E_APPROVED_GATING_FAIL",
                        "latest iteration reevaluation_report.gate_decision must be pass for approved decisions",
                    )
            for row in journal_rows:
                if not isinstance(row, dict):
                    continue
                ree = row.get("reevaluation_report")
                if isinstance(ree, dict) and ree.get("non_regression_passed") is not True:
                    add_error(
                        errors,
                        "E_APPROVED_NON_REGRESSION_FAIL",
                        "approved decision requires non_regression_passed=true for all iterations",
                    )
                    break

    # Counterfactual checks.
    requires_counterfactual = schema_version_at_least(str(decision.get("schema_version", "1.0")), "1.1")
    counterfactual = decision.get("counterfactual_uplift")
    if not isinstance(counterfactual, dict):
        if requires_counterfactual:
            add_error(errors, "E_COUNTERFACTUAL_MISSING", "counterfactual_uplift object is required for schema_version >= 1.1")
        else:
            add_warning(warnings, "W_COUNTERFACTUAL_MISSING", "counterfactual_uplift missing (legacy schema)")
    else:
        required_fields(
            counterfactual,
            [
                "analysis_method_version",
                "sample_size",
                "match_quality_metrics",
                "promotion_decision",
                "auto_apply_decision",
                "uplift_confidence_band",
            ],
            "counterfactual_uplift",
            "E_COUNTERFACTUAL_MISSING_FIELD",
            errors,
        )
        try:
            sample_size = int(counterfactual.get("sample_size"))
            if sample_size < 0:
                add_error(errors, "E_COUNTERFACTUAL_SAMPLE_SIZE", "counterfactual_uplift.sample_size must be >= 0")
        except Exception:
            add_error(errors, "E_COUNTERFACTUAL_SAMPLE_SIZE", "counterfactual_uplift.sample_size must be an integer")

        for key in ("treatment_outcome", "control_outcome", "uplift_delta"):
            value = counterfactual.get(key)
            if value is None:
                continue
            try:
                value_f = float(value)
                if value_f < -1.0 or value_f > 1.0:
                    add_error(
                        errors,
                        "E_COUNTERFACTUAL_BOUND",
                        f"counterfactual_uplift.{key} must be between -1 and 1",
                    )
            except Exception:
                add_error(errors, "E_COUNTERFACTUAL_NUMERIC", f"counterfactual_uplift.{key} must be numeric when present")

        ci_obj = counterfactual.get("uplift_confidence_band")
        if isinstance(ci_obj, dict):
            lower = ci_obj.get("lower")
            upper = ci_obj.get("upper")
            if lower is not None and upper is not None:
                try:
                    lower_f = float(lower)
                    upper_f = float(upper)
                    if lower_f > upper_f:
                        add_error(errors, "E_COUNTERFACTUAL_CI", "counterfactual_uplift.uplift_confidence_band lower cannot exceed upper")
                except Exception:
                    add_error(errors, "E_COUNTERFACTUAL_CI", "counterfactual_uplift.uplift_confidence_band bounds must be numeric")

        match_obj = counterfactual.get("match_quality_metrics")
        if isinstance(match_obj, dict):
            untreated = match_obj.get("treated_unmatched_rate")
            if untreated is not None:
                try:
                    untreated_f = float(untreated)
                    if untreated_f < 0.0 or untreated_f > 1.0:
                        add_error(
                            errors,
                            "E_COUNTERFACTUAL_MATCH",
                            "counterfactual_uplift.match_quality_metrics.treated_unmatched_rate must be between 0 and 1",
                        )
                except Exception:
                    add_error(
                        errors,
                        "E_COUNTERFACTUAL_MATCH",
                        "counterfactual_uplift.match_quality_metrics.treated_unmatched_rate must be numeric",
                    )

        for key in ("promotion_decision", "auto_apply_decision"):
            if key in counterfactual:
                state = str(counterfactual.get(key, "")).strip().lower()
                if state not in {
                    "pass",
                    "hold",
                    "regressed",
                    "insufficient_data",
                    "insufficient_match_quality",
                }:
                    add_error(
                        errors,
                        "E_COUNTERFACTUAL_DECISION_VALUE",
                        f"counterfactual_uplift.{key} has invalid value: {state}",
                    )

        if decision_state == "approved":
            if str(counterfactual.get("promotion_decision", "")).strip().lower() != "pass":
                add_error(
                    errors,
                    "E_APPROVED_COUNTERFACTUAL_NOT_PASS",
                    "approved decision requires counterfactual_uplift.promotion_decision=pass",
                )
            try:
                sample_size = int(counterfactual.get("sample_size", 0))
            except Exception:
                sample_size = 0
            thresholds = (
                counterfactual.get("promotion_thresholds", {})
                if isinstance(counterfactual.get("promotion_thresholds"), dict)
                else {}
            )
            min_pairs_required = int(thresholds.get("min_pairs_total", 0) or 0)
            if min_pairs_required and sample_size < min_pairs_required:
                add_error(
                    errors,
                    "E_APPROVED_COUNTERFACTUAL_SAMPLE_SIZE",
                    "approved decision requires sample_size >= promotion threshold",
                )
            ci_obj = (
                counterfactual.get("uplift_confidence_band", {})
                if isinstance(counterfactual.get("uplift_confidence_band"), dict)
                else {}
            )
            ci_lower_required = float(thresholds.get("ci_lower_min", 0.0) or 0.0)
            ci_lower_raw = ci_obj.get("lower")
            if ci_lower_raw is None:
                add_error(
                    errors,
                    "E_APPROVED_COUNTERFACTUAL_CI_MISSING",
                    "approved decision requires counterfactual_uplift.uplift_confidence_band.lower",
                )
            else:
                try:
                    if float(ci_lower_raw) < ci_lower_required:
                        add_error(errors, "E_APPROVED_COUNTERFACTUAL_CI", "approved decision requires uplift CI lower bound above threshold")
                except Exception:
                    add_error(
                        errors,
                        "E_APPROVED_COUNTERFACTUAL_CI_INVALID",
                        "counterfactual_uplift.uplift_confidence_band.lower must be numeric",
                    )
            match_obj = (
                counterfactual.get("match_quality_metrics", {})
                if isinstance(counterfactual.get("match_quality_metrics"), dict)
                else {}
            )
            if isinstance(match_obj, dict) and match_obj.get("valid") is not True:
                add_error(
                    errors,
                    "E_APPROVED_COUNTERFACTUAL_MATCH",
                    "approved decision requires valid counterfactual match_quality_metrics",
                )

    # Events are mandatory when promotions are being validated.
    event_blocker_codes: Set[str] = set()
    if events_path.exists():
        try:
            events = load_jsonl(events_path)
            event_blocker_codes = validate_event_rows(events, run_id, errors, warnings)
            if decision_state == "approved" and not any(
                isinstance(row, dict) and row.get("event_type") == "promotion_approved" and str(row.get("run_id", "")).strip() == run_id
                for row in events
            ):
                add_error(errors, "E_APPROVED_PROMOTION_EVENT", "run/events.jsonl missing promotion_approved event")

            if expected_blocker:
                if not any(
                    isinstance(row, dict)
                    and row.get("event_type") == "run_blocker"
                    and str(row.get("run_id", "")).strip() == run_id
                    and str(row.get("blocker_code", "")).strip() == expected_blocker
                    for row in events
                ):
                    add_error(
                        errors,
                        "E_BLOCKER_EVENT_MISMATCH",
                        f"run_blocked event with blocker_code={expected_blocker} required for terminal state {terminal_status}/{stop_reason}",
                    )
        except Exception as exc:
            add_error(errors, "E_EVENTS_JSONL_INVALID", f"invalid events.jsonl: {exc}")
    elif not errors and (not legacy_relaxed_layout or require_events_for_validation):
        add_error(errors, "E_EVENTS_FILE_MISSING", "events.jsonl missing")

    if blocker_code_run and expected_blocker and blocker_code_run != expected_blocker:
        add_error(
            errors,
            "E_BLOCKER_STATE_MISMATCH",
            f"run_blocker code {blocker_code_run} does not match terminal state {terminal_status}/{stop_reason}",
        )

    # Ensure event blocker consistency with file blocker (best-effort)
    if blocker_code_run and blocker_code_run not in event_blocker_codes:
        add_warning(
            warnings,
            "W_BLOCKER_EVENT_MISSING",
            f"run_blocker code {blocker_code_run} not observed in events.jsonl",
        )

    # Candidate decisions often skip lesson scan requirements.
    if decision_state in {"candidate", "approved"}:
        lesson_file = resolve_lesson_file(
            args=args,
            decision=decision,
            repo_root=repo_root,
            run_dir=run_dir,
            errors=errors,
        )
        if lesson_file and lesson_file.exists():
            scan = scan_lesson_content(lesson_file)
            secret_hit_count = int(scan.get("secret_hit_count", 0))
            if secret_hit_count > 0:
                add_error(
                    errors,
                    "E_LESSON_SECRET",
                    "lesson security check failed: secret-like tokens detected in lesson content",
                )
            for message in scan["pii_hits"]:
                add_warning(warnings, "W_LESSON_PII", f"lesson privacy warning: {message}")

            recorded_sha = decision.get("lesson_content_sha256")
            actual_sha = sha256_file(lesson_file)
            if decision_state == "approved":
                if recorded_sha:
                    if str(recorded_sha) != actual_sha:
                        add_error(errors, "E_LESSON_HASH_MISMATCH", "lesson_content_sha256 mismatch with lesson source file")
                else:
                    add_error(errors, "E_LESSON_HASH_MISSING", "lesson_content_sha256 is required for approved decisions")

    return {
        "validator": "recursive_promotion",
        "run_id": run_id or decision_run_id,
        "decision_file": decision_file_out,
        "status": "ok" if not errors else "fail",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "decision": decision_state,
    }


def main() -> int:
    args = parse_args()
    try:
        report = validate(args)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "validator": "recursive_promotion",
                    "status": "error",
                    "error": str(exc),
                }
            )
        )
        return 1

    # Write report to stdout as single-line JSON for JSONL compatibility
    # (consumers parse stdout with splitlines() + json.loads(line))
    print(json.dumps(report, separators=(",", ":")))

    # Also write to disk when explicitly requested (with pretty formatting)
    if args.write_report:
        report_path = Path(args.write_report).expanduser().resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    return 0 if report["status"] == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
