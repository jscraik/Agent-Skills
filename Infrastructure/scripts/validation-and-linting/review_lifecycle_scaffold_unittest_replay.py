#!/usr/bin/env python3
"""Run bounded, artifact-first review for lifecycle-scaffold unittest replay.

This is the repo-native fallback when a Codex adversarial child does not emit a
review artifact. Each role is a separate process invocation and writes a JSON
report. The runner is read-only except for its explicitly named report path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
SOURCE_PATH = ROOT / "Infrastructure/scripts/lib/ask/skills_sdk/stabilization_replay.py"
TEST_PATH = ROOT / "Infrastructure/tests/test_skills_sdk_lifecycle_scaffold_unittest_replay.py"
EXPECTED_ARGV = (
    "python3",
    "-m",
    "unittest",
    "Infrastructure.scripts.testing.test_skill_creator_lifecycle_scaffold",
    "-v",
)
MAX_OUTPUT_BYTES = 4096
MAX_OUTPUT_LINES = 64


def _observe_transcript(transcript: str) -> tuple[str, list[str]]:
    lines = [line.strip() for line in transcript.splitlines() if line.strip()]
    if len(transcript.encode("utf-8")) > MAX_OUTPUT_BYTES or len(lines) > MAX_OUTPUT_LINES:
        return "fail", ["lifecycle_scaffold_unittest_receipt:oversize"]
    ran_lines = [line for line in lines if line.startswith("Ran ")]
    prefix = "Ran 4 tests in "
    if len(ran_lines) != 1 or not ran_lines[0].startswith(prefix) or not ran_lines[0].endswith("s"):
        return "fail", ["lifecycle_scaffold_unittest_receipt:invalid_marker"]
    duration = ran_lines[0][len(prefix) : -1]
    if not _valid_duration(duration):
        return "fail", ["lifecycle_scaffold_unittest_receipt:invalid_marker"]
    if _has_failure_marker(lines):
        return "fail", ["lifecycle_scaffold_unittest_receipt:invalid_marker"]
    return "pass", ["lifecycle_scaffold_unittest_receipt:valid_marker", "lifecycle_scaffold_unittest_test_count:4"]


def _valid_duration(duration: str) -> bool:
    whole, separator, fraction = duration.partition(".")
    return duration.isascii() and whole.isdigit() and (not separator or fraction.isdigit())


def _has_failure_marker(lines: list[str]) -> bool:
    return lines[-1:] != ["OK"] or any(line.startswith(("FAILED", "ERROR", "FAIL")) for line in lines)


def _source_digest() -> str:
    digest = hashlib.sha256()
    for path in (SOURCE_PATH, TEST_PATH):
        digest.update(str(path.relative_to(ROOT)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _status_snapshot() -> str:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--", str(SOURCE_PATH), str(TEST_PATH)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    return result.stdout


def _run(command: list[str], *, timeout: int = 120) -> tuple[int, str, str]:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False, timeout=timeout)
    return result.returncode, result.stdout, result.stderr


def _candidate_findings(source_path: Path = SOURCE_PATH, test_path: Path = TEST_PATH) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not source_path.is_file() or "LIFECYCLE_SCAFFOLD_UNITTEST_ARGV" not in source_path.read_text(encoding="utf-8"):
        findings.append({"severity": "blocker", "message": "source does not declare the exact lifecycle unittest argv", "evidence": [str(source_path)]})
    if not test_path.is_file():
        findings.append({"severity": "blocker", "message": "repository-owned lifecycle replay test is missing", "evidence": [str(test_path)]})
    elif not all(marker in test_path.read_text(encoding="utf-8") for marker in ("near_miss", "malformed", "oversized")):
        findings.append({"severity": "blocker", "message": "negative replay coverage is missing", "evidence": [str(test_path)]})
    return findings


def _worker_findings() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    findings = _candidate_findings()
    evidence: list[dict[str, Any]] = []
    before = _status_snapshot()
    code, stdout, stderr = _run(list(EXPECTED_ARGV))
    evidence.append({"command": " ".join(EXPECTED_ARGV), "status": "pass" if code == 0 else "fail", "stdout_tail": stdout[-1000:], "stderr_tail": stderr[-1000:]})
    if code != 0:
        findings.append({"severity": "blocker", "message": "direct lifecycle scaffold unittest failed", "evidence": [stdout[-1000:], stderr[-1000:]]})
    if _status_snapshot() != before:
        findings.append({"severity": "blocker", "message": "direct unittest mutated the intended source/test paths", "evidence": [str(SOURCE_PATH), str(TEST_PATH)]})
    return findings, evidence


def _qa_findings() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    findings, evidence = _worker_findings()
    commands = (
        ["bash", "Infrastructure/scripts/run-infrastructure-python.sh", "-m", "pytest", "-q", "tests/test_skills_sdk_lifecycle_scaffold_unittest_replay.py"],
        ["uv", "run", "--python", "3.12", "ruff", "check", str(SOURCE_PATH), str(TEST_PATH)],
        ["python3", "Infrastructure/scripts/validation-and-linting/verify_ask_cli_modularity.py", "--changed-files", str(SOURCE_PATH), str(TEST_PATH)],
    )
    for command in commands:
        code, stdout, stderr = _run(command)
        evidence.append({"command": " ".join(command), "status": "pass" if code == 0 else "fail", "stdout_tail": stdout[-1000:], "stderr_tail": stderr[-1000:]})
        if code != 0:
            findings.append({"severity": "blocker", "message": f"review command failed: {' '.join(command)}", "evidence": [stdout[-1000:], stderr[-1000:]]})
    return findings, evidence


def _adversarial_findings(source_path: Path = SOURCE_PATH, test_path: Path = TEST_PATH) -> list[dict[str, Any]]:
    findings = _candidate_findings(source_path, test_path)
    source = source_path.read_text(encoding="utf-8") if source_path.is_file() else ""
    if "--execute" in source or "network_accessed = True" in source:
        findings.append({"severity": "blocker", "message": "candidate introduces an authority or network mutation path", "evidence": [str(source_path)]})
    for transcript in ("Ran 3 tests in 0.1s\nOK\n", "Ran 4 tests in .1s\nOK\n", "Ran 4 tests in 0.1s\nFAILED\nOK\n", "Ran 4 tests in 0.1s\nOK\ntrailing\n"):
        status, _evidence = _observe_transcript(transcript)
        if status != "fail":
            findings.append({"severity": "blocker", "message": "negative transcript was accepted", "evidence": [repr(transcript)]})
    if "--verbose" not in source and "-v" not in source:
        findings.append({"severity": "blocker", "message": "exact verbose unittest argv is not visible in the candidate", "evidence": [str(source_path)]})
    return findings


def _build_report(role: str, findings: list[dict[str, Any]], evidence: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "skills-sdk.lifecycle-scaffold-unittest-review.v1",
        "role": role,
        "status": "pass" if not findings else "blocked_validation",
        "candidate_source_files": [str(SOURCE_PATH.relative_to(ROOT)), str(TEST_PATH.relative_to(ROOT))],
        "candidate_source_digest": _source_digest() if SOURCE_PATH.is_file() and TEST_PATH.is_file() else None,
        "findings": findings,
        "evidence": evidence,
        "evidence_boundary": "independent local review of lifecycle-scaffold unittest replay only; no source, runtime, registry, hosted, Foundry, or publication mutation",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=("worker", "qa", "adversarial"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.role == "worker":
        findings, evidence = _worker_findings()
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
