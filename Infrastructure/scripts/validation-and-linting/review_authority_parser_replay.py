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
import os
import re
import shlex
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
EXPECTED_RECEIPT_SCHEMAS = {
    "eval": "skills-sdk.ab-preview-receipt.v0",
    "trust": "skills-sdk.trust-decision-receipt.v0",
    "plugin": "skills-sdk-plugin-review.v0",
    "improve": "skills-sdk.project-improvement-receipt.v0",
    "install": "skills-sdk.install-preview.v1",
    "rollback": "skills-sdk.project-cleanup-receipt.v1",
    "uninstall": "skills-sdk.project-cleanup-receipt.v1",
    "knowledge": "skills-sdk-knowledge-ingest.v1",
}
EXPECTED_RECEIPT_STATUSES = {
    "eval": "preview",
    "trust": "preview",
    "plugin": "preview",
    "improve": "pass",
    "install": "preview",
    "rollback": "preview",
    "uninstall": "preview",
    "knowledge": "preview",
}
MUTATION_KEYS = {
    "mutation_performed",
    "source_mutation_performed",
    "trust_store_mutated",
    "network_accessed",
    "credentials_accessed",
    "codex_exec_invoked",
}
REQUIRED_NO_WRITE_KEYS = {
    "eval": frozenset({"mutation_performed", "network_accessed", "codex_exec_invoked"}),
    "trust": frozenset({"mutation_performed", "trust_store_mutated"}),
    "plugin": frozenset({"mutation_performed"}),
    "improve": frozenset({"mutation_performed", "source_mutation_performed"}),
    "install": frozenset({"mutation_performed"}),
    "rollback": frozenset({"mutation_performed"}),
    "uninstall": frozenset({"mutation_performed"}),
    "knowledge": frozenset(),
}
PLACEHOLDER_ROOTS = ("/tmp/sample-project", "/path/to/")


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


def _capture_receipt(body: dict[str, Any], family: str) -> dict[str, Any] | None:
    expected_schema = EXPECTED_RECEIPT_SCHEMAS[family]
    expected_status = EXPECTED_RECEIPT_STATUSES[family]
    preview = body.get("preview")
    if isinstance(preview, dict):
        status = body.get("status") if family == "install" else preview.get("status")
        return (
            preview
            if preview.get("schema_version") == expected_schema and status == expected_status
            else None
        )
    candidates = [body.get("receipt"), body]
    return next(
        (
            candidate
            for candidate in candidates
            if isinstance(candidate, dict)
            and candidate.get("schema_version") == expected_schema
            and candidate.get("status") == expected_status
        ),
        None,
    )


def _capture_no_write_findings(receipt: dict[str, Any], family: str, output_path: Path) -> list[dict[str, Any]]:
    missing = sorted(key for key in REQUIRED_NO_WRITE_KEYS[family] if key not in receipt)
    non_false = sorted(key for key in MUTATION_KEYS if key in receipt and receipt[key] is not False)
    findings: list[dict[str, Any]] = []
    if missing:
        findings.append({"severity": "blocker", "family": family, "message": f"nested receipt omits explicit no-write fields: {', '.join(missing)}", "evidence": [str(output_path)]})
    if non_false:
        findings.append({"severity": "blocker", "family": family, "message": f"nested receipt no-write fields are not false: {', '.join(non_false)}", "evidence": [str(output_path)]})
    return findings


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
    receipt = _capture_receipt(body, family)
    if receipt is None:
        findings.append({"severity": "blocker", "family": family, "message": "nested receipt schema_version/status is missing or invalid", "evidence": [str(output_path)]})
    else:
        findings.extend(_capture_no_write_findings(receipt, family, output_path))
    findings.extend(
        {"severity": "blocker", "family": family, "message": f"mutation or external-access flag is true: {flag}", "evidence": [str(output_path)]}
        for flag in _walk_mutation_flags(body, f"$.data.{key}")
    )
    return findings


def _worker_findings(capture_dir: Path, artifact_path: Path, selection_path: Path) -> list[dict[str, Any]]:
    findings = [finding for family in FAMILIES for finding in _capture_findings(capture_dir, family)]
    findings.extend(_worker_command_binding_findings(capture_dir, artifact_path, selection_path))
    return findings


def _row_findings(row: Any, artifact_path: Path) -> list[dict[str, Any]]:
    if not isinstance(row, dict):
        return [{"severity": "blocker", "message": "candidate contains a non-object command row", "evidence": [str(artifact_path)]}]
    findings: list[dict[str, Any]] = []
    family = row.get("family")
    if row.get("mutation_performed") is not False:
        findings.append({"severity": "blocker", "family": family, "message": "candidate row is not explicitly no-write", "evidence": [str(artifact_path)]})
    command = str(row.get("command", ""))
    try:
        argv = shlex.split(command)
    except ValueError as exc:
        findings.append({"severity": "blocker", "family": family, "message": f"candidate command cannot be parsed: {exc}", "evidence": [command]})
        argv = []
    if any(_is_placeholder_argument(argument) for argument in argv):
        findings.append({"severity": "blocker", "family": family, "message": "candidate command contains a template or placeholder argument", "evidence": [command]})
    fixture = str(row.get("source_fixture", ""))
    if not _is_repo_relative_path(fixture):
        findings.append({"severity": "blocker", "family": family, "message": "candidate fixture path is not a safe repository-relative path", "evidence": [fixture]})
    return findings


def _is_placeholder_argument(argument: str) -> bool:
    return bool(re.search(r"<[^>]+>", argument)) or any(argument.startswith(root) for root in PLACEHOLDER_ROOTS)


def _is_repo_relative_path(value: str, *, require_file: bool = False) -> bool:
    if not value or Path(value).is_absolute():
        return False
    try:
        resolved = (ROOT / value).resolve()
        resolved.relative_to(ROOT.resolve())
    except (OSError, ValueError):
        return False
    return resolved.is_file() if require_file else resolved.exists()


def _command_argv(command: Any) -> list[str] | None:
    if isinstance(command, list):
        if not command or not all(isinstance(argument, str) for argument in command):
            return None
        argv = list(command)
    else:
        try:
            argv = shlex.split(str(command))
        except ValueError:
            return None
    if argv and argv[0] == "ask":
        argv[0] = "./bin/ask"
    return argv


def _normalized_command(command: Any) -> list[str] | None:
    argv = _command_argv(command)
    if argv and argv[0] == "./bin/ask":
        return argv[1:]
    return argv


def _has_shell_quoting(command: Any) -> bool:
    return isinstance(command, str) and ("'" in command or '"' in command)


def _rows_by_family(payload: dict[str, Any], key: str) -> dict[str, dict[str, Any]]:
    return {
        row.get("family"): row
        for row in payload.get(key, [])
        if isinstance(row, dict) and isinstance(row.get("family"), str)
    }


def _worker_capture_command(capture_dir: Path, family: str) -> tuple[Path, str | list[str] | None, list[dict[str, Any]]]:
    output_path = capture_dir / f"{family}.json"
    if not output_path.is_file():
        return output_path, None, []
    try:
        payload = _load_json(output_path)
    except (ValueError, json.JSONDecodeError, OSError) as exc:
        finding = {"severity": "blocker", "family": family, "message": f"worker command capture could not be loaded: {exc}", "evidence": [str(output_path)]}
        return output_path, None, [finding]
    metadata = payload.get("metadata")
    actual_argv = metadata.get("command_argv") if isinstance(metadata, dict) else None
    if isinstance(actual_argv, list) and actual_argv and all(isinstance(argument, str) for argument in actual_argv):
        return output_path, actual_argv, []
    actual_command = metadata.get("command") if isinstance(metadata, dict) else None
    return output_path, actual_command if isinstance(actual_command, str) and actual_command.strip() else None, []


def _compare_worker_command(
    family: str,
    actual_command: str | list[str],
    label: str,
    rows: dict[str, dict[str, Any]],
    source_path: Path,
    output_path: Path,
) -> list[dict[str, Any]]:
    expected_row = rows.get(family)
    expected_command = expected_row.get("command") if isinstance(expected_row, dict) else None
    if not isinstance(expected_command, str) or not expected_command.strip():
        return [{"severity": "blocker", "family": family, "message": f"{label} command is missing for worker binding", "evidence": [str(source_path)]}]
    actual_normalized = _normalized_command(actual_command)
    expected_normalized = _normalized_command(expected_command)
    legacy_normalized = (
        _normalized_command(actual_command.replace("'", "").replace('"', ""))
        == _normalized_command(expected_command.replace("'", "").replace('"', ""))
        if isinstance(actual_command, str)
        and not _has_shell_quoting(actual_command)
        and not _has_shell_quoting(expected_command)
        else False
    )
    if actual_normalized == expected_normalized or legacy_normalized:
        return []
    return [{"severity": "blocker", "family": family, "message": f"worker capture command does not match the {label} command", "evidence": [actual_command, expected_command, str(output_path)]}]


def _worker_family_command_findings(
    capture_dir: Path,
    family: str,
    candidate_rows: dict[str, dict[str, Any]],
    selected_rows: dict[str, dict[str, Any]],
    artifact_path: Path,
    selection_path: Path,
) -> list[dict[str, Any]]:
    output_path, actual_command, findings = _worker_capture_command(capture_dir, family)
    if findings or not output_path.is_file():
        return findings
    if actual_command is None:
        return [{"severity": "blocker", "family": family, "message": "worker capture does not declare the executed command", "evidence": [str(output_path)]}]
    for label, rows, source_path in (("candidate", candidate_rows, artifact_path), ("selected", selected_rows, selection_path)):
        findings.extend(_compare_worker_command(family, actual_command, label, rows, source_path, output_path))
    return findings


def _worker_command_binding_findings(
    capture_dir: Path,
    artifact_path: Path,
    selection_path: Path,
) -> list[dict[str, Any]]:
    try:
        artifact = _load_json(artifact_path)
        selection = _load_json(selection_path)
    except (ValueError, json.JSONDecodeError, OSError) as exc:
        return [{"severity": "blocker", "message": f"worker command binding inputs could not be loaded: {exc}", "evidence": [str(artifact_path), str(selection_path)]}]
    candidate_rows = _rows_by_family(artifact, "commands")
    selected_rows = _rows_by_family(selection, "selected_preview_commands")
    return [
        finding
        for family in FAMILIES
        for finding in _worker_family_command_findings(
            capture_dir, family, candidate_rows, selected_rows, artifact_path, selection_path
        )
    ]


def _row_binding_findings(rows: list[Any], selected: Any, artifact_path: Path, selection_path: Path) -> list[dict[str, Any]]:
    if not isinstance(selected, list):
        return []
    findings: list[dict[str, Any]] = []
    selected_by_family = {
        expected.get("family"): expected
        for expected in selected
        if isinstance(expected, dict) and isinstance(expected.get("family"), str)
    }
    for index, row in enumerate(rows):
        expected = selected_by_family.get(row.get("family")) if isinstance(row, dict) else None
        if not isinstance(row, dict) or not isinstance(expected, dict):
            findings.append({"severity": "blocker", "message": f"candidate row {index} cannot be bound to a selected preview row", "evidence": [str(artifact_path), str(selection_path)]})
            continue
        if row.get("family") != expected.get("family") or _command_argv(row.get("command")) != _command_argv(expected.get("command")):
            findings.append({"severity": "blocker", "message": f"candidate row {index} command does not exactly match the selected preview row", "evidence": [str(row.get("command")), str(expected.get("command"))]})
    return findings


def _artifact_shape_findings(artifact: dict[str, Any], selection: dict[str, Any], artifact_path: Path, selection_path: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if artifact.get("schema_version") != "skills-sdk.authority-parser-replay-receipt.v1":
        findings.append({"severity": "blocker", "message": "candidate schema_version is incorrect", "evidence": [str(artifact_path)]})
    rows = artifact.get("commands")
    if artifact.get("status") == "blocked":
        return findings + _blocked_shape_findings(artifact, rows, artifact_path)
    return findings + _pass_shape_findings(artifact, selection, rows, artifact_path, selection_path)


def _blocked_shape_findings(artifact: dict[str, Any], rows: Any, artifact_path: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not isinstance(rows, list) or rows:
        findings.append({"severity": "blocker", "message": "blocked candidate must contain an empty commands array", "evidence": [str(artifact_path)]})
    if artifact.get("command_count") != 0:
        findings.append({"severity": "blocker", "message": "blocked candidate must declare command_count 0 when no commands were executed", "evidence": [str(artifact.get("command_count"))]})
    return findings


def _pass_shape_findings(artifact: dict[str, Any], selection: dict[str, Any], rows: Any, artifact_path: Path, selection_path: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
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
        if artifact.get("command_count") != len(rows):
            findings.append({"severity": "blocker", "message": "candidate command_count does not equal the commands array length", "evidence": [str(artifact.get("command_count")), str(len(rows))]})
        findings.extend(_row_binding_findings(rows, selected, artifact_path, selection_path))
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
    if not isinstance(source_files, list) or not source_files or not all(isinstance(path, str) and path for path in source_files):
        findings.append({"severity": "blocker", "message": "selection must declare a non-empty source_files string list before replay approval", "evidence": [str(selection_path)]})
    else:
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
        if not _is_repo_relative_path(path, require_file=True):
            raise OSError(f"declared source file is not a safe existing repository-relative file: {path}")
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
    environment = os.environ.copy()
    environment["SKILLS_SDK_AUTHORITY_REPLAY_ARTIFACT"] = str(artifact_path)
    environment["SKILLS_SDK_AUTHORITY_REPLAY_SELECTION"] = str(selection_path)
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=90, check=False, env=environment)
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
        findings = _worker_findings(args.capture_dir, artifact_path, selection_path)
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
