#!/usr/bin/env python3
"""Run bounded, artifact-first replay review for the SDK review handoff row.

The handoff parser is read-only, but it requires a same-head plan receipt and
trace sidecar. This runner creates those generated inputs through the plan
command, replays the exact handoff argv, then removes only the generated paths.
It never executes reviewers, contacts a service, or writes a handoff receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
LIB_ROOT = ROOT / "Infrastructure/scripts/lib"
if str(LIB_ROOT) not in sys.path:
    sys.path.insert(0, str(LIB_ROOT))

from ask.skills_sdk.review_plan import _target_digest as canonical_target_digest  # noqa: E402


SOURCE_PATH = ROOT / "Infrastructure/scripts/validation-and-linting/review_handoff_replay.py"
TEST_PATH = ROOT / "Infrastructure/tests/test_review_handoff_replay.py"
PLAN_PATH = ROOT / ".harness/artifacts/sdk-review-plan/simplify.json"
TRACE_DIR = ROOT / ".harness/artifacts/sdk-review-plan/traces"
EXPECTED_PLAN_ARGV = (
    "./bin/ask",
    "sdk",
    "review",
    "plan",
    "--target",
    "Skills/agent-ops/simplify",
    "--intent",
    "validation_review",
    "--receipt-out",
    ".harness/artifacts/sdk-review-plan/simplify.json",
    "--json",
    "--robot",
)
EXPECTED_HANDOFF_ARGV = (
    "./bin/ask",
    "sdk",
    "review",
    "handoff",
    "--plan",
    ".harness/artifacts/sdk-review-plan/simplify.json",
    "--target",
    "Skills/agent-ops/simplify",
    "--intent",
    "validation_review",
    "--json",
    "--robot",
)


def _run(command: tuple[str, ...], *, timeout: int = 120) -> tuple[int, str, str]:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False, timeout=timeout)
    return result.returncode, result.stdout, result.stderr


def _source_digest() -> str:
    digest = hashlib.sha256()
    for path in (SOURCE_PATH, TEST_PATH):
        digest.update(str(path.relative_to(ROOT)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _target_digest() -> str:
    status, digest, findings = canonical_target_digest(ROOT / "Skills/agent-ops/simplify")
    if status != "available" or digest is None:
        raise ValueError(f"canonical target digest unavailable: {status}; findings={findings}")
    return digest


def _tracked_status() -> str:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no", "--", "Skills/agent-ops/simplify"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    return result.stdout


def _load_json(stdout: str, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} did not emit JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} did not emit a JSON object")
    return payload


def _classify_handoff_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if payload.get("status") != "success":
        findings.append({"severity": "blocker", "message": "handoff envelope is not success"})
    data = payload.get("data")
    handoff = data.get("review_handoff") if isinstance(data, dict) else None
    if not isinstance(handoff, dict):
        findings.append({"severity": "blocker", "message": "handoff receipt is missing from data.review_handoff"})
        return findings
    findings.extend(_handoff_receipt_findings(handoff))
    return findings


def _handoff_receipt_findings(handoff: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if handoff.get("schema_version") != "skills-sdk.review-handoff-receipt.v1":
        findings.append({"severity": "blocker", "message": "handoff receipt schema_version is unsupported"})
    if handoff.get("status") != "pass":
        findings.append({"severity": "blocker", "message": "handoff receipt status is not pass"})
    if handoff.get("mutation_performed") is not False:
        findings.append({"severity": "blocker", "message": "handoff receipt mutation_performed must be false"})
    if handoff.get("receipt_written") is not False:
        findings.append({"severity": "blocker", "message": "handoff receipt receipt_written must be false for this replay"})
    if handoff.get("receipt_path") is not None:
        findings.append({"severity": "blocker", "message": "handoff replay must not claim a receipt output path"})
    not_proven = handoff.get("not_proven")
    if not isinstance(not_proven, list) or not {"reviewers_completed", "ci_passed"}.issubset(not_proven):
        findings.append({"severity": "blocker", "message": "handoff receipt not_proven must retain reviewer and CI boundaries"})
    source_plan = handoff.get("source_review_plan")
    if not isinstance(source_plan, dict) or source_plan.get("path") != ".harness/artifacts/sdk-review-plan/simplify.json":
        findings.append({"severity": "blocker", "message": "handoff receipt is not bound to the exact simplify plan fixture path"})
    return findings


def _cleanup(before_plan: bool, before_plan_contents: bytes | None, before_traces: set[Path], trace_after: set[Path]) -> None:
    if before_plan:
        PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)
        PLAN_PATH.write_bytes(before_plan_contents or b"")
    elif PLAN_PATH.exists():
        PLAN_PATH.unlink()
    for trace_path in trace_after - before_traces:
        if trace_path.exists():
            trace_path.unlink()
    if TRACE_DIR.exists() and not any(TRACE_DIR.iterdir()):
        TRACE_DIR.rmdir()
    if PLAN_PATH.parent.exists() and not any(PLAN_PATH.parent.iterdir()):
        PLAN_PATH.parent.rmdir()


def _worker_findings() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    findings: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    before_plan = PLAN_PATH.exists()
    before_plan_contents = PLAN_PATH.read_bytes() if before_plan else None
    before_traces = set(TRACE_DIR.glob("*.trace.json")) if TRACE_DIR.exists() else set()
    before_status = _tracked_status()
    before_target_digest = _target_digest()
    try:
        code, stdout, stderr = _run(EXPECTED_PLAN_ARGV)
        evidence.append({"command": " ".join(EXPECTED_PLAN_ARGV), "status": "pass" if code == 0 else "fail", "stderr_tail": stderr[-1000:]})
        if code != 0:
            findings.append({"severity": "blocker", "message": "same-head review plan setup failed", "evidence": [stdout[-1000:], stderr[-1000:]]})
            return findings, evidence
        code, stdout, stderr = _run(EXPECTED_HANDOFF_ARGV)
        evidence.append({"command": " ".join(EXPECTED_HANDOFF_ARGV), "status": "pass" if code == 0 else "fail", "stderr_tail": stderr[-1000:]})
        if code != 0:
            findings.append({"severity": "blocker", "message": "exact review handoff replay failed", "evidence": [stdout[-1000:], stderr[-1000:]]})
        else:
            try:
                findings.extend(_classify_handoff_payload(_load_json(stdout, "review handoff replay")))
            except ValueError as exc:
                findings.append({"severity": "blocker", "message": str(exc), "evidence": [stdout[-1000:]]})
        if _tracked_status() != before_status:
            findings.append({"severity": "blocker", "message": "handoff replay changed tracked target status", "evidence": ["Skills/agent-ops/simplify"]})
        if _target_digest() != before_target_digest:
            findings.append({"severity": "blocker", "message": "handoff replay changed target content", "evidence": ["Skills/agent-ops/simplify"]})
    finally:
        trace_after = set(TRACE_DIR.glob("*.trace.json")) if TRACE_DIR.exists() else set()
        _cleanup(before_plan, before_plan_contents, before_traces, trace_after)
    return findings, evidence


def _candidate_findings(source_path: Path = SOURCE_PATH, test_path: Path = TEST_PATH) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    source = source_path.read_text(encoding="utf-8") if source_path.is_file() else ""
    test = test_path.read_text(encoding="utf-8") if test_path.is_file() else ""
    if "EXPECTED_HANDOFF_ARGV" not in source or "sdk" not in source or "handoff" not in source:
        findings.append({"severity": "blocker", "message": "source does not declare the exact handoff argv", "evidence": [str(source_path)]})
    if not test_path.is_file() or not all(marker in test for marker in ("mutation", "wrong_status", "adversarial")):
        findings.append({"severity": "blocker", "message": "repository-owned negative replay coverage is missing", "evidence": [str(test_path)]})
    return findings


def _qa_findings() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    findings, evidence = _worker_findings()
    commands = (
        ["bash", "Infrastructure/scripts/run-infrastructure-python.sh", "-m", "pytest", "-q", "tests/test_review_handoff_replay.py"],
        ["uv", "run", "--python", "3.12", "ruff", "check", str(SOURCE_PATH), str(TEST_PATH)],
        ["python3", "Infrastructure/scripts/validation-and-linting/verify_ask_cli_modularity.py", "--changed-files", str(SOURCE_PATH), str(TEST_PATH)],
    )
    for command in commands:
        code, stdout, stderr = _run(tuple(command))
        evidence.append({"command": " ".join(command), "status": "pass" if code == 0 else "fail", "stderr_tail": stderr[-1000:]})
        if code != 0:
            findings.append({"severity": "blocker", "message": f"review command failed: {' '.join(command)}", "evidence": [stdout[-1000:], stderr[-1000:]]})
    return findings, evidence


def _adversarial_findings(source_path: Path = SOURCE_PATH, test_path: Path = TEST_PATH) -> list[dict[str, Any]]:
    findings = _candidate_findings(source_path, test_path)
    source = source_path.read_text(encoding="utf-8") if source_path.is_file() else ""
    unsafe_tokens = (
        "-" + "-execute",
        "socket" + ".create_connection",
        "requests" + ".",
        "urllib" + ".request",
    )
    if any(token in source for token in unsafe_tokens):
        findings.append({"severity": "blocker", "message": "candidate introduces execution or external-access authority", "evidence": [str(source_path)]})
    for payload in (
        {"status": "success", "data": {"review_handoff": {"schema_version": "skills-sdk.review-handoff-receipt.v1", "status": "pass", "mutation_performed": True}}},
        {"status": "success", "data": {"review_handoff": {"schema_version": "wrong.schema", "status": "pass", "mutation_performed": False}}},
    ):
        if not _classify_handoff_payload(payload):
            findings.append({"severity": "blocker", "message": "negative handoff payload was accepted", "evidence": [json.dumps(payload, sort_keys=True)]})
    return findings


def _build_report(role: str, findings: list[dict[str, Any]], evidence: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "skills-sdk.review-handoff-replay-review.v1",
        "role": role,
        "status": "pass" if not findings else "blocked_validation",
        "candidate_source_files": [str(SOURCE_PATH.relative_to(ROOT)), str(TEST_PATH.relative_to(ROOT))],
        "candidate_source_digest": _source_digest() if SOURCE_PATH.is_file() and TEST_PATH.is_file() else None,
        "findings": findings,
        "evidence": evidence,
        "evidence_boundary": "independent local review of the read-only review handoff replay; no reviewer execution, network, source admission, publication, or hosted readiness claim",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=("worker", "qa", "adversarial"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.role == "worker":
        findings, evidence = _candidate_findings(), []
        if not findings:
            runtime_findings, runtime_evidence = _worker_findings()
            findings.extend(runtime_findings)
            evidence.extend(runtime_evidence)
    elif args.role == "qa":
        findings, evidence = _qa_findings()
    else:
        findings, evidence = _adversarial_findings(), []
    report = _build_report(args.role, findings, evidence)
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
