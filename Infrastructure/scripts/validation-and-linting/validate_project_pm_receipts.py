#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[3]
PM_REPORT_PREFIX = ".harness/reports/project-pm/"


@dataclass(frozen=True)
class Finding:
    file: str
    code: str
    message: str


def _run_git(args: list[str]) -> list[str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def changed_paths() -> list[str]:
    paths = set(_run_git(["diff", "--name-only", "--diff-filter=ACMR", "HEAD"]))
    paths.update(_run_git(["ls-files", "--others", "--exclude-standard"]))
    return sorted(paths)


def normalize_path(path: str) -> str:
    return path.strip().removeprefix("./")


def should_scan_path(path: str) -> bool:
    rel = normalize_path(path)
    return rel.startswith(PM_REPORT_PREFIX) and rel.endswith(".json") and (REPO_ROOT / rel).is_file()


def _non_empty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return value is not None


def _has_command_evidence(payload: dict[str, Any]) -> bool:
    for key in ("commands", "evidence", "validation"):
        value = payload.get(key)
        if isinstance(value, list) and value:
            return True
    post_recovery = payload.get("post_recovery_validation")
    return isinstance(post_recovery, dict) and _non_empty(post_recovery.get("status"))


def _has_unproven_boundary(payload: dict[str, Any]) -> bool:
    for key in ("what_remains_unproven", "what_it_does_not_prove", "remaining_unproven"):
        if _non_empty(payload.get(key)):
            return True
    claims = payload.get("claims_boundary")
    if isinstance(claims, dict) and _non_empty(claims.get("not_proven")):
        return True
    if isinstance(claims, str) and claims.strip():
        return True
    return False


def _has_next_owner_or_outbound(payload: dict[str, Any]) -> bool:
    if _non_empty(payload.get("next_owner")):
        return True
    if _non_empty(payload.get("next_action")):
        return True
    outbound = payload.get("outbound_update")
    if isinstance(outbound, dict) and _non_empty(outbound.get("recipient")):
        return True
    escalation = payload.get("outbound_escalation") or payload.get("outbound_escalation_evidence")
    if isinstance(escalation, dict) and (
        _non_empty(escalation.get("recipient")) or _non_empty(escalation.get("requested_decision"))
    ):
        return True
    push_or_pr = payload.get("push_or_pr_needed")
    return isinstance(push_or_pr, dict) and _non_empty(push_or_pr.get("reason"))


def validate_payload(path: str, payload: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    if not _non_empty(payload.get("schema_version")):
        findings.append(Finding(path, "missing_schema_version", "PM receipt must include schema_version."))
    if not _non_empty(payload.get("status")):
        findings.append(Finding(path, "missing_status", "PM receipt must include status."))
    if not _has_command_evidence(payload):
        findings.append(Finding(path, "missing_command_evidence", "PM receipt must include commands, evidence, validation, or post_recovery_validation."))
    if not _has_unproven_boundary(payload):
        findings.append(Finding(path, "missing_unproven_boundary", "PM receipt must state what remains unproven or provide a claims boundary."))
    if not _has_next_owner_or_outbound(payload):
        findings.append(Finding(path, "missing_next_owner_or_outbound", "PM receipt must name next_owner, next_action, outbound recipient, escalation decision, or push/PR disposition."))
    return findings


def scan_paths(paths: Iterable[str]) -> list[Finding]:
    findings: list[Finding] = []
    for raw_path in paths:
        rel = normalize_path(raw_path)
        if not should_scan_path(rel):
            continue
        try:
            payload = json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            findings.append(Finding(rel, "invalid_json", str(exc)))
            continue
        if not isinstance(payload, dict):
            findings.append(Finding(rel, "invalid_root", "PM receipt JSON root must be an object."))
            continue
        findings.extend(validate_payload(rel, payload))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate changed Project PM receipt closeout shape.")
    parser.add_argument("--changed-files", nargs="*", help="Repo-relative files to scan. Defaults to current changed files.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    paths = [normalize_path(path) for path in args.changed_files] if args.changed_files is not None else changed_paths()
    findings = scan_paths(paths)
    result = {
        "schema_version": "project-pm-receipt-validation/v1",
        "status": "pass" if not findings else "fail",
        "scanned_files": [path for path in paths if should_scan_path(path)],
        "findings": [asdict(finding) for finding in findings],
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["status"])
        for finding in findings:
            print(f"{finding.file}: {finding.code}: {finding.message}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
