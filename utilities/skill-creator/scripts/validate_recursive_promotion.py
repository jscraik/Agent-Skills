#!/usr/bin/env python3
"""Validate recursive-loop human promotion decisions against run evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

ALLOWED_DECISIONS = {"draft", "candidate", "approved", "rejected"}
DEFAULT_POLICY_FILE = "docs/skill-graphs/governance/recursive-loop-approvers.yaml"
DEFAULT_POLICY_SIG_FILE = "docs/skill-graphs/governance/recursive-loop-approvers.sig"
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
    p.add_argument("--write-report", help="Optional JSON output path for validation report")
    return p.parse_args()


def load_json(path: Path) -> Dict[str, Any]:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON ({path}): {exc}") from exc
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


def required_fields(obj: Dict[str, Any], fields: List[str], prefix: str, errors: List[str]) -> None:
    for field in fields:
        if field not in obj:
            errors.append(f"{prefix} missing field: {field}")


def sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_lesson_content(path: Path) -> Dict[str, List[str]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    secret_hits: List[str] = []
    pii_hits: List[str] = []

    for idx, line in enumerate(text.splitlines(), start=1):
        for pattern in SECRET_PATTERNS:
            if pattern.search(line):
                secret_hits.append(f"line {idx}: secret-like token")
                break

        for match in EMAIL_PATTERN.findall(line):
            lower = match.lower()
            if lower.endswith("@example.com") or lower.endswith("@test.com"):
                continue
            pii_hits.append(f"line {idx}: email-like identifier '{match}'")

    return {"secret_hits": secret_hits, "pii_hits": pii_hits}


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
    errors: List[str],
) -> Optional[Path]:
    if args.lesson_file:
        lesson_file = Path(args.lesson_file).expanduser().resolve()
        if not lesson_file.exists():
            errors.append(f"lesson file not found: {lesson_file}")
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
        # fallback relative to run dir
        candidate_run = (run_dir / raw).resolve()
        if candidate_run.exists():
            return candidate_run
        errors.append(f"lesson_source_path does not resolve to a file: {source_path}")
        return None

    if args.skip_lesson_content_scan:
        return None

    errors.append("approved decision requires lesson content scan (provide --lesson-file or lesson_source_path)")
    return None


def validate(args: argparse.Namespace) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    run_dir = Path(args.run_dir).expanduser().resolve()
    repo_root = run_dir
    while repo_root != repo_root.parent and not (repo_root / ".git").exists():
        repo_root = repo_root.parent

    run_json_path = run_dir / "run.json"
    journal_path = run_dir / "iteration_journal.jsonl"
    events_path = run_dir / "events.jsonl"
    decision_path = (
        Path(args.decision_file).expanduser().resolve()
        if args.decision_file
        else run_dir / "promotion_decision.json"
    )

    run = load_json(run_json_path)
    journals = load_jsonl(journal_path)
    decision = load_json(decision_path)
    decision_file_out = (
        str(decision_path.relative_to(repo_root))
        if decision_path.is_relative_to(repo_root)
        else str(decision_path)
    )

    if not journals:
        errors.append("iteration_journal.jsonl has no rows")

    required_fields(
        decision,
        [
            "schema_version",
            "run_id",
            "lesson_id",
            "decision",
            "reviewer_ids",
            "expected_version",
            "gate_decision",
            "provenance",
        ],
        "promotion_decision",
        errors,
    )

    run_id = str(run.get("run_id", ""))
    decision_run_id = str(decision.get("run_id", ""))
    if run_id and decision_run_id and run_id != decision_run_id:
        errors.append(f"run_id mismatch: run.json={run_id} decision={decision_run_id}")

    decision_state = str(decision.get("decision", "")).strip().lower()
    if decision_state not in ALLOWED_DECISIONS:
        errors.append(f"invalid decision state: {decision_state}")

    gate = decision.get("gate_decision")
    if not isinstance(gate, dict):
        errors.append("gate_decision must be an object")
        gate = {}

    provenance = decision.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("provenance must be an object")
        provenance = {}

    if decision_state in {"approved", "candidate"}:
        if not str(decision.get("lesson_id", "")).strip():
            errors.append("lesson_id is required for candidate/approved decisions")
        reviewers = decision.get("reviewer_ids")
        if not isinstance(reviewers, list) or not any(str(r).strip() for r in reviewers):
            errors.append("reviewer_ids must include at least one reviewer for candidate/approved decisions")
        else:
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
                    errors.append(f"non-canonical policy-file not allowed: {policy_file}")
                if sig_file != canonical_policy_sig:
                    errors.append(f"non-canonical policy-sig-file not allowed: {sig_file}")
            if not policy_file.exists():
                errors.append(f"reviewer policy file missing: {policy_file}")
            elif not sig_file.exists():
                errors.append(f"reviewer policy signature missing: {sig_file}")
            else:
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
                    for reviewer in reviewers:
                        rv = str(reviewer).strip()
                        if rv not in allowed_map:
                            errors.append(f"reviewer not allowlisted: {rv}")
                            continue
                        if allowed_map[rv] not in min_roles:
                            errors.append(f"reviewer role not permitted: {rv}:{allowed_map[rv]}")
                except Exception as exc:
                    errors.append(f"reviewer policy validation failed: {exc}")

        confidence_obj = decision.get("confidence")
        if not isinstance(confidence_obj, dict):
            warnings.append("confidence object missing (Phase-4 queue enrichment expected)")
        else:
            score = confidence_obj.get("score")
            if score is None:
                warnings.append("confidence.score missing (Phase-4 queue enrichment expected)")
            else:
                try:
                    score_f = float(score)
                    if score_f < 0.0 or score_f > 1.0:
                        errors.append("confidence.score must be between 0 and 1")
                except Exception:
                    errors.append("confidence.score must be numeric")
            bucket = str(confidence_obj.get("bucket", "")).strip().lower()
            if bucket and bucket not in {"high", "medium", "low"}:
                errors.append("confidence.bucket must be one of high|medium|low")

        evidence_obj = decision.get("evidence_packet")
        if isinstance(evidence_obj, dict):
            completeness = evidence_obj.get("completeness_score")
            if completeness is not None:
                try:
                    completeness_f = float(completeness)
                    if completeness_f < 0.0 or completeness_f > 1.0:
                        errors.append("evidence_packet.completeness_score must be between 0 and 1")
                except Exception:
                    errors.append("evidence_packet.completeness_score must be numeric")

    if decision_state == "approved":
        if args.skip_lesson_content_scan:
            errors.append("approved decision cannot use --skip-lesson-content-scan")

        if run.get("terminal_status") != "passed":
            errors.append("approved decision requires run terminal_status=passed")
        if run.get("stop_reason") != "pass":
            errors.append("approved decision requires run stop_reason=pass")

        if not str(decision.get("expected_version", "")).strip():
            errors.append("expected_version is required for approved decision")

        if gate.get("runtime_gates_passed") is not True:
            errors.append("gate_decision.runtime_gates_passed must be true for approved decision")
        if gate.get("provenance_complete") is not True:
            errors.append("gate_decision.provenance_complete must be true for approved decision")
        if gate.get("security_checklist_passed") is not True:
            errors.append("gate_decision.security_checklist_passed must be true for approved decision")
        if str(decision.get("lesson_status", "")).strip().lower() != "active":
            warnings.append("lesson_status should be 'active' for approved decision (legacy artifacts may omit)")
        if not str(decision.get("canonical_version", "")).strip():
            warnings.append("canonical_version should be present for approved decision (legacy artifacts may omit)")

        required_fields(
            provenance,
            ["prompt_hash", "rubric_version", "evaluator_version", "iteration_ids"],
            "provenance",
            errors,
        )

        journal_ids: Set[int] = set()
        for row in journals:
            jid = row.get("iteration_id")
            if isinstance(jid, int):
                journal_ids.add(jid)
            if str(row.get("run_id", "")) != run_id:
                errors.append("iteration journal run_id mismatch")

        prov_ids_raw = provenance.get("iteration_ids")
        if not isinstance(prov_ids_raw, list) or not prov_ids_raw:
            errors.append("provenance.iteration_ids must be a non-empty list")
            prov_ids: Set[int] = set()
        else:
            non_int_ids = [x for x in prov_ids_raw if not isinstance(x, int)]
            if non_int_ids:
                errors.append("provenance.iteration_ids must contain only integers")
            duplicate_ids = {x for x in prov_ids_raw if isinstance(x, int) and prov_ids_raw.count(x) > 1}
            if duplicate_ids:
                errors.append(
                    "provenance.iteration_ids must not contain duplicates: "
                    + ",".join(str(x) for x in sorted(duplicate_ids))
                )
            prov_ids = {int(x) for x in prov_ids_raw if isinstance(x, int)}

        if prov_ids and not prov_ids.issubset(journal_ids):
            errors.append("provenance.iteration_ids must reference existing iteration ids")

        if provenance.get("prompt_hash") != run.get("prompt_hash"):
            errors.append("provenance.prompt_hash mismatch with run.prompt_hash")

        run_versions = run.get("versions", {}) if isinstance(run.get("versions"), dict) else {}
        if provenance.get("rubric_version") != run_versions.get("rubric_version"):
            errors.append("provenance.rubric_version mismatch with run.versions.rubric_version")
        if provenance.get("evaluator_version") != run_versions.get("evaluator_version"):
            errors.append("provenance.evaluator_version mismatch with run.versions.evaluator_version")

        if journals:
            last = sorted(journals, key=lambda x: int(x.get("iteration_id", 0)))[-1]
            last_gate = (
                last.get("reevaluation_report", {}).get("gate_decision")
                if isinstance(last.get("reevaluation_report"), dict)
                else None
            )
            if last_gate != "pass":
                errors.append("latest iteration reevaluation_report.gate_decision must be pass for approved decisions")

            non_regression_failures = [
                row.get("iteration_id")
                for row in journals
                if isinstance(row.get("reevaluation_report"), dict)
                and row["reevaluation_report"].get("non_regression_passed") is not True
            ]
            if non_regression_failures:
                errors.append(
                    "approved decision requires non_regression_passed=true for all iterations; failed iterations: "
                    + ",".join(str(x) for x in non_regression_failures)
                )

        if events_path.exists():
            events = load_jsonl(events_path)
            promotion_events = [
                e
                for e in events
                if e.get("event_type") == "promotion_approved" and e.get("run_id") == run_id
            ]
            if not promotion_events:
                errors.append("promotion_approved event missing in run/events.jsonl")
        else:
            errors.append("run/events.jsonl missing")

        lesson_file = resolve_lesson_file(
            args=args,
            decision=decision,
            repo_root=repo_root,
            run_dir=run_dir,
            errors=errors,
        )

        if lesson_file and lesson_file.exists():
            scan = scan_lesson_content(lesson_file)
            if scan["secret_hits"]:
                errors.extend([f"lesson security check failed: {m}" for m in scan["secret_hits"]])
            if scan["pii_hits"]:
                warnings.extend([f"lesson privacy warning: {m}" for m in scan["pii_hits"]])

            recorded_sha = decision.get("lesson_content_sha256")
            actual_sha = sha256_file(lesson_file)
            if recorded_sha:
                if str(recorded_sha) != actual_sha:
                    errors.append("lesson_content_sha256 mismatch with lesson source file")
            else:
                errors.append("lesson_content_sha256 is required for approved decisions")

    result = {
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

    if args.write_report:
        report_path = Path(args.write_report).expanduser().resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    return result


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

    print(json.dumps(report))
    return 0 if report["status"] == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
