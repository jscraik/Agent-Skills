#!/usr/bin/env python3
"""Run artifact-first QA and adversarial checks for signing-intent replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
TARGET = ROOT / "Infrastructure/tests/fixtures/skills_sdk/valid_skill"
POLICY = ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/signing-policy.json"
SOURCE = ROOT / "Infrastructure/scripts/lib/ask/skills_sdk/stabilization_replay.py"
TESTS = (
    ROOT / "Infrastructure/tests/test_skills_sdk_signing_intent.py",
    ROOT / "Infrastructure/tests/test_skills_sdk_signing_intent_replay.py",
)
ARGV = (
    "./bin/ask",
    "sdk",
    "package",
    "signing-intent",
    "Infrastructure/tests/fixtures/skills_sdk/valid_skill",
    "--policy",
    "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/signing-policy.json",
    "--json",
    "--robot",
)


def _run(argv: list[str], *, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=ROOT, text=True, capture_output=True, check=False, timeout=timeout)


def _digest(paths: tuple[Path, ...]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _positive() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    before = _status()
    completed = _run(list(ARGV))
    after = _status()
    findings: list[dict[str, Any]] = []
    try:
        payload = json.loads(completed.stdout)
        body = payload["data"]["skills_sdk_package_signing_intent"]
        receipt = body["receipt"]
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        return [{"severity": "blocker", "message": f"positive receipt malformed: {exc}"}], {"command": " ".join(ARGV), "exit_code": completed.returncode}
    if completed.returncode != 0 or payload.get("status") != "success" or receipt.get("status") != "ready":
        findings.append({"severity": "blocker", "message": "exact signing-intent command did not return ready", "evidence": [completed.stderr, completed.stdout[-1200:]]})
    for key in ("mutation_performed", "signing_performed", "key_material_accessed", "artifact_emitted"):
        if body.get(key) is not False or receipt.get(key) is not False:
            findings.append({"severity": "blocker", "message": f"no-write flag is not false: {key}", "evidence": [str(key)]})
    if before != after:
        findings.append({"severity": "blocker", "message": "positive command mutated the tracked worktree"})
    return findings, {"command": " ".join(ARGV), "exit_code": completed.returncode, "receipt_status": receipt.get("status"), "package_digest": body.get("package_digest"), "mutation_performed": body.get("mutation_performed")}


def _negative() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="skills-sdk-signing-review-") as tmpdir:
        bad_policy = Path(tmpdir) / "policy.json"
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        policy["allowed_package_digests"] = ["sha256:" + ("0" * 64)]
        bad_policy.write_text(json.dumps(policy), encoding="utf-8")
        argv = [*ARGV]
        argv[argv.index(str(POLICY.relative_to(ROOT)))] = str(bad_policy)
        completed = _run(argv)
    findings: list[dict[str, Any]] = []
    try:
        payload = json.loads(completed.stdout)
        body = payload["data"]["skills_sdk_package_signing_intent"]
        receipt = body["receipt"]
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        return [{"severity": "blocker", "message": f"negative receipt malformed: {exc}"}], {"command": " ".join(argv), "exit_code": completed.returncode}
    if completed.returncode != 2 or payload.get("status") != "error" or receipt.get("status") != "blocked":
        findings.append({"severity": "blocker", "message": "mismatched policy did not fail closed", "evidence": [completed.stdout[-1200:], completed.stderr]})
    if not any(blocker.get("id") == "package_digest_pinned" for blocker in receipt.get("blockers", [])):
        findings.append({"severity": "blocker", "message": "negative receipt omitted package_digest_pinned blocker"})
    for key in ("mutation_performed", "signing_performed", "key_material_accessed", "artifact_emitted"):
        if body.get(key) is not False or receipt.get(key) is not False:
            findings.append({"severity": "blocker", "message": f"negative path set a forbidden flag: {key}"})
    return findings, {"command": " ".join(argv), "exit_code": completed.returncode, "receipt_status": receipt.get("status"), "blocker": "package_digest_pinned"}


def _status() -> str:
    return _run(["git", "status", "--porcelain"], timeout=30).stdout


def _qa() -> list[dict[str, Any]]:
    commands = [
        ["bash", "Infrastructure/scripts/run-infrastructure-python.sh", "-m", "pytest", "-q", "tests/test_skills_sdk_signing_intent.py", "tests/test_skills_sdk_signing_intent_replay.py", "tests/test_skills_sdk_schema_spine.py", "-k", "package or signing or hardening or schema_spine"],
        ["bash", "Infrastructure/scripts/run-infrastructure-python.sh", "-m", "ruff", "check", "scripts/lib/ask/skills_sdk/stabilization_replay.py", "tests/test_skills_sdk_signing_intent.py", "tests/test_skills_sdk_signing_intent_replay.py"],
        ["python3", "Infrastructure/scripts/validation-and-linting/verify_ask_cli_modularity.py", "--changed-files", "Infrastructure/scripts/lib/ask/skills_sdk/stabilization_replay.py", "Infrastructure/tests/test_skills_sdk_signing_intent.py", "Infrastructure/tests/test_skills_sdk_signing_intent_replay.py"],
    ]
    findings: list[dict[str, Any]] = []
    for command in commands:
        result = _run(command)
        if result.returncode != 0:
            findings.append({"severity": "blocker", "message": "QA command failed", "command": " ".join(command), "evidence": [result.stdout[-1200:], result.stderr[-1200:]]})
    return findings


def _adversarial() -> list[dict[str, Any]]:
    source = SOURCE.read_text(encoding="utf-8")
    findings: list[dict[str, Any]] = []
    if "signing-intent" not in source or "signing-policy.json" not in source:
        findings.append({"severity": "blocker", "message": "exact signing-intent policy path is not visible in the allowlist"})
    if "--apply" in source or "subprocess.run" not in source:
        findings.append({"severity": "blocker", "message": "candidate authority boundary is missing or expanded"})
    if not all(path.is_file() for path in TESTS):
        findings.append({"severity": "blocker", "message": "positive/negative repository-owned replay tests are missing"})
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=("worker", "qa", "adversarial"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    findings, evidence = _positive()
    negative_findings, negative = _negative()
    findings.extend(negative_findings)
    if args.role == "qa":
        findings.extend(_qa())
    elif args.role == "adversarial":
        findings.extend(_adversarial())
    report = {
        "schema_version": "skills-sdk.signing-intent-review.v1",
        "role": args.role,
        "status": "pass" if not findings else "blocked_validation",
        "candidate_source_digest": _digest((SOURCE, *TESTS)),
        "evidence": [evidence, negative],
        "findings": findings,
        "claims_boundary": "local signing-intent fixture/replay only; no signing, key access, archive, install, publish, registry, hosted CI, Foundry, or release claim",
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
