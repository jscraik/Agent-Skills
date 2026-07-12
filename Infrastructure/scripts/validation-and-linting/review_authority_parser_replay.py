#!/usr/bin/env python3
"""Run bounded, artifact-first review for authority parser replay evidence.

This is the repo-native fallback when Codex child-agent startup does not produce
the required Worker, QA, or adversarial report. Each role is a separate process
invocation with the same immutable candidate and a distinct disproof contract.
The command is read-only except for its explicitly named report output path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
FAMILIES = ("eval", "trust", "plugin", "improve", "install", "rollback", "uninstall", "knowledge")
EXPECTED_DATA_KEYS = {
    "eval": "skills_sdk_eval_ab_preview",
    "trust": "skills_sdk_trust_decide",
    "plugin": "skills_sdk_plugin_review",
    "improve": "skills_sdk_project_improve",
    "install": "skills_sdk_install_preview",
    "rollback": "skills_sdk_project_rollback",
    "uninstall": "skills_sdk_project_uninstall",
    "knowledge": "knowledge_ingest",
}
MUTATION_KEYS = {
    "mutation_performed",
    "source_mutation_performed",
    "trust_store_mutated",
    "network_accessed",
    "credentials_accessed",
    "codex_exec_invoked",
}


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _walk_mutation_flags(value: Any, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in MUTATION_KEYS and child is True:
                findings.append(f"{child_path}:true")
            findings.extend(_walk_mutation_flags(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_walk_mutation_flags(child, f"{path}[{index}]"))
    return findings


def _capture_receipt(body: dict[str, Any]) -> dict[str, Any] | None:
    candidates = [body.get("receipt"), body.get("preview"), body]
    return next(
        (
            candidate
            for candidate in candidates
            if isinstance(candidate, dict)
            and isinstance(candidate.get("schema_version"), str)
            and candidate.get("status") in {"pass", "preview"}
        ),
        None,
    )


def _capture_findings(capture_dir: Path, family: str) -> list[dict[str, Any]]:
    output_path = capture_dir / f"{family}.json"
    exit_path = capture_dir / f"{family}.exit"
    stderr_path = capture_dir / f"{family}.stderr"
    evidence = [str(output_path), str(exit_path), str(stderr_path)]
    if not output_path.is_file() or not exit_path.is_file() or not stderr_path.is_file():
        return [{"severity": "blocker", "family": family, "message": "replay capture is incomplete", "evidence": evidence}]
    try:
        payload = _load_json(output_path)
        exit_code = int(exit_path.read_text(encoding="utf-8").strip())
    except (ValueError, json.JSONDecodeError, OSError) as exc:
        return [{"severity": "blocker", "family": family, "message": f"replay capture is invalid: {exc}", "evidence": evidence}]
    findings: list[dict[str, Any]] = []
    if exit_code != 0 or payload.get("status") != "success":
        findings.append({"severity": "blocker", "family": family, "message": "replay did not return success with exit code 0", "evidence": evidence})
    if stderr_path.read_bytes():
        findings.append({"severity": "blocker", "family": family, "message": "replay emitted stderr", "evidence": [str(stderr_path)]})
    key = EXPECTED_DATA_KEYS[family]
    data = payload.get("data")
    if not isinstance(data, dict) or not isinstance(data.get(key), dict):
        findings.append({"severity": "blocker", "family": family, "message": f"expected data key {key!r} is missing", "evidence": [str(output_path)]})
        return findings
    body = data[key]
    if _capture_receipt(body) is None:
        findings.append({"severity": "blocker", "family": family, "message": "nested receipt schema_version/status is missing or invalid", "evidence": [str(output_path)]})
    findings.extend(
        {"severity": "blocker", "family": family, "message": f"mutation or external-access flag is true: {flag}", "evidence": [str(output_path)]}
        for flag in _walk_mutation_flags(body, f"$.data.{key}")
    )
    return findings


def _worker_findings(capture_dir: Path) -> list[dict[str, Any]]:
    return [finding for family in FAMILIES for finding in _capture_findings(capture_dir, family)]


def _row_findings(row: Any, artifact_path: Path) -> list[dict[str, Any]]:
    if not isinstance(row, dict):
        return [{"severity": "blocker", "message": "candidate contains a non-object command row", "evidence": [str(artifact_path)]}]
    findings: list[dict[str, Any]] = []
    family = row.get("family")
    if row.get("mutation_performed") is not False:
        findings.append({"severity": "blocker", "family": family, "message": "candidate row is not explicitly no-write", "evidence": [str(artifact_path)]})
    command = str(row.get("command", ""))
    if any(token.startswith("<") and token.endswith(">") for token in command.split()):
        findings.append({"severity": "blocker", "family": family, "message": "candidate command contains a template token", "evidence": [command]})
    fixture = str(row.get("source_fixture", ""))
    if fixture.startswith("/"):
        findings.append({"severity": "blocker", "family": family, "message": "candidate fixture path is not repository-relative", "evidence": [fixture]})
    return findings


def _artifact_shape_findings(artifact: dict[str, Any], selection: dict[str, Any], artifact_path: Path, selection_path: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if artifact.get("schema_version") != "skills-sdk.authority-parser-replay-receipt.v1":
        findings.append({"severity": "blocker", "message": "candidate schema_version is incorrect", "evidence": [str(artifact_path)]})
    rows = artifact.get("commands")
    selected = selection.get("selected_preview_commands")
    if not isinstance(rows, list) or len(rows) != len(FAMILIES):
        findings.append({"severity": "blocker", "message": "candidate does not contain exactly eight command rows", "evidence": [str(artifact_path)]})
    if not isinstance(selected, list) or len(selected) != len(FAMILIES):
        findings.append({"severity": "blocker", "message": "selection does not contain exactly eight preview rows", "evidence": [str(selection_path)]})
    if isinstance(rows, list):
        families = [row.get("family") for row in rows if isinstance(row, dict)]
        commands = [row.get("command") for row in rows if isinstance(row, dict)]
        if set(families) != set(FAMILIES):
            findings.append({"severity": "blocker", "message": "candidate family set does not match the selected authority families", "evidence": [str(artifact_path)]})
        if len(set(commands)) != len(commands):
            findings.append({"severity": "blocker", "message": "candidate contains duplicate commands", "evidence": [str(artifact_path)]})
        for row in rows:
            findings.extend(_row_findings(row, artifact_path))
    return findings


def _artifact_findings(artifact_path: Path, selection_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    try:
        artifact = _load_json(artifact_path)
        selection = _load_json(selection_path)
    except (ValueError, json.JSONDecodeError, OSError) as exc:
        return {}, [{"severity": "blocker", "message": f"artifact load failed: {exc}", "evidence": [str(artifact_path), str(selection_path)]}]
    findings = _artifact_shape_findings(artifact, selection, artifact_path, selection_path)
    head = _git_head()
    base_commit = str(artifact.get("base_commit", ""))
    if not _git_is_ancestor(base_commit, head):
        findings.append({"severity": "blocker", "message": "candidate base_commit is not an ancestor of the current immutable HEAD", "evidence": [base_commit, head]})
    source_files = selection.get("source_files")
    if isinstance(source_files, list) and all(isinstance(path, str) for path in source_files):
        try:
            current_digest = _source_tree_digest(source_files)
        except OSError as exc:
            findings.append({"severity": "blocker", "message": f"declared source digest could not be recomputed: {exc}", "evidence": [str(selection_path)]})
        else:
            if artifact.get("source_tree_digest") != current_digest:
                findings.append({"severity": "blocker", "message": "candidate source_tree_digest does not match the current declared source files", "evidence": [str(artifact.get("source_tree_digest")), current_digest]})
    return artifact, findings


def _git_head() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True, timeout=30)
    return result.stdout.strip()


def _git_is_ancestor(base_commit: str, head: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", base_commit, head],
        cwd=ROOT,
        capture_output=True,
        check=False,
        timeout=30,
    )
    return result.returncode == 0


def _source_tree_digest(source_files: list[str]) -> str:
    digest = hashlib.sha256()
    for path in sorted(source_files):
        digest.update(path.encode())
        digest.update(b"\0")
        digest.update((ROOT / path).read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _qa_findings(artifact_path: Path, selection_path: Path) -> list[dict[str, Any]]:
    _artifact, findings = _artifact_findings(artifact_path, selection_path)
    command = [
        "bash",
        "Infrastructure/scripts/run-infrastructure-python.sh",
        "-m",
        "pytest",
        "-q",
        "tests/test_skills_sdk_authority_parser_replay_receipt.py",
    ]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=90, check=False)
    if result.returncode != 0:
        findings.append({"severity": "blocker", "message": "focused receipt test failed", "evidence": [" ".join(command), result.stdout[-1000:], result.stderr[-1000:]]})
    return findings


def _adversarial_findings(artifact_path: Path, selection_path: Path) -> list[dict[str, Any]]:
    artifact, findings = _artifact_findings(artifact_path, selection_path)
    if artifact.get("status") != "pass":
        findings.append({"severity": "blocker", "message": "candidate claims a non-pass status", "evidence": [str(artifact_path)]})
    required_boundaries = ("Foundry extraction or source admission", "hosted CI")
    declared_boundaries = [str(item) for item in artifact.get("does_not_prove", [])]
    for boundary in required_boundaries:
        if not any(boundary in item for item in declared_boundaries):
            findings.append({"severity": "blocker", "message": f"candidate does not declare boundary {boundary!r}", "evidence": [str(artifact_path)]})
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=("worker", "qa", "adversarial"), required=True)
    parser.add_argument("--capture-dir", type=Path, default=Path("/private/tmp/agent-skills-sdk-phase2-authority-replay-direct"))
    parser.add_argument("--artifact", type=Path, default=Path(".harness/evidence/handoff/skills-sdk-parser-families/authority-parser-replay-receipt.v1.json"))
    parser.add_argument("--selection", type=Path, default=Path(".harness/evidence/handoff/skills-sdk-parser-families/authority-parser-replay-selection.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact_path = args.artifact if args.artifact.is_absolute() else ROOT / args.artifact
    selection_path = args.selection if args.selection.is_absolute() else ROOT / args.selection
    if args.role == "worker":
        findings = _worker_findings(args.capture_dir)
    elif args.role == "qa":
        findings = _qa_findings(artifact_path, selection_path)
    else:
        findings = _adversarial_findings(artifact_path, selection_path)
    report = {
        "schema_version": "skills-sdk.authority-parser-replay-review.v1",
        "role": args.role,
        "status": "pass" if not findings else "blocked_validation",
        "candidate_artifact": str(artifact_path),
        "findings": findings,
        "evidence_boundary": "independent local review of command replay evidence only; no source, runtime, registry, or hosted mutation",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
