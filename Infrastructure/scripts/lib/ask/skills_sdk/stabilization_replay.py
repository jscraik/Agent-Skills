from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from ask.skills_sdk.command_evidence_plan import build_command_evidence_plan_receipt


SCHEMA_VERSION = "skills-sdk.private-stabilization-replay.v1"
MAX_HELP_OUTPUT_BYTES = 4096
MAX_HELP_OUTPUT_LINES = 64
ALLOWLIST = {
    ("./bin/ask", "sdk", "package", "build", "Infrastructure/tests/fixtures/skills_sdk/valid_skill", "--json", "--robot"),
    ("./bin/ask", "sdk", "security", "package-signature", "Infrastructure/tests/fixtures/skills_sdk/valid_skill", "--preview", "--json", "--robot"),
    ("./bin/ask", "sdk", "security", "risk-modes", "Infrastructure/tests/fixtures/skills_sdk/valid_skill", "--preview", "--json", "--robot"),
    ("./bin/ask", "sdk", "intake", "inspect", "Infrastructure/tests/fixtures/skills_sdk/valid_skill", "--preview", "--json", "--robot"),
    ("./bin/ask", "sdk", "intake", "review", "Infrastructure/tests/fixtures/skills_sdk/valid_skill", "--preview", "--json", "--robot"),
    ("./bin/ask", "sdk", "lenses", "validate", "--json", "--robot"),
    ("./bin/ask", "sdk", "eval", "profiles", "--preview", "--json", "--robot"),
    ("./bin/ask", "sdk", "eval", "ab-rubric", "--preview", "--json", "--robot"),
    ("./bin/ask", "sdk", "eval", "ab-preview", "--skill-a", "Infrastructure/tests/fixtures/skills_sdk/valid_skill", "--skill-b", "Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill", "--fixture", "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/deterministic-eval-pass.json", "--preview", "--json", "--robot"),
    ("./bin/ask", "sdk", "eval", "scenario-quality", "Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill", "--preview", "--json", "--robot"),
    ("./bin/ask", "sdk", "security", "adapters", "--preview", "--json", "--robot"),
    ("./bin/ask", "sdk", "plugin", "--help"),
}


def build_private_stabilization_replay(repo_root: Path) -> dict[str, Any]:
    """Replay exact allowlisted local read-only evidence and deny everything else."""
    plan = build_command_evidence_plan_receipt(repo_root)
    executions: dict[tuple[str, ...], dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    for row in plan["commands"]:
        argv = tuple(str(item) for item in row["argv"])
        if argv not in executions:
            executions[argv] = _execute_argv(repo_root, argv)
        execution = executions[argv]
        rows.append(_occurrence_row(row, argv, execution))
    terminal = {"executed_pass", "executed_fail", "blocked_external", "blocked_unsafe"}
    unclassified = [row for row in rows if row["status"] not in terminal]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass" if not unclassified else "blocked",
        "scope": "capability-matrix-private-stabilization",
        "public_receipt_changed": False,
        "command_ref_count": len(rows),
        "terminal_count": len(rows) - len(unclassified),
        "unclassified_count": len(unclassified),
        "execution_policy": "exact_argv_allowlist_deny_by_default",
        "network_policy_intent": "local_only_no_network_requested",
        "mutation_policy_intent": "read_only_preview_or_validation_commands_only",
        "unique_execution_count": len(executions),
        "rows": rows,
    }


def _occurrence_row(row: dict[str, Any], argv: tuple[str, ...], execution: dict[str, Any]) -> dict[str, Any]:
    return {
        "capability_id": row["capability_id"],
        "command": row["command"],
        "argv": list(argv),
        **execution,
    }


def _execute_argv(repo_root: Path, argv: tuple[str, ...]) -> dict[str, Any]:
    execution_id = f"sha256:{hashlib.sha256(json.dumps(argv).encode('utf-8')).hexdigest()}"
    if argv not in ALLOWLIST:
        return _blocked_execution(execution_id)
    try:
        completed = _run_allowlisted(repo_root, argv)
    except subprocess.TimeoutExpired:
        return _failed_execution(execution_id, "Allowlisted command timed out after 30 seconds.", ["timeout_seconds:30"])
    except OSError as exc:
        return _failed_execution(
            execution_id,
            f"Allowlisted command could not execute: {type(exc).__name__}.",
            [f"os_error:{exc.errno}"],
        )
    return _classify_completed(execution_id, argv, completed)


def _blocked_execution(execution_id: str) -> dict[str, Any]:
    return {
        "execution_id": execution_id,
        "status": "blocked_unsafe",
        "exit_code": None,
        "reason": "Command is not on the exact private stabilization read-only allowlist.",
        "evidence": ["deny_by_default"],
    }


def _failed_execution(execution_id: str, reason: str, evidence: list[str]) -> dict[str, Any]:
    return {"execution_id": execution_id, "status": "executed_fail", "exit_code": None, "reason": reason, "evidence": evidence}


def _run_allowlisted(repo_root: Path, argv: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(argv),
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
    )


def _classify_completed(execution_id: str, argv: tuple[str, ...], completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    receipt_status, receipt_evidence = _observe_robot_receipt(completed.stdout)
    if completed.returncode != 0:
        status = "executed_fail"
        reason = "Exact allowlisted local read-only command returned a non-zero exit code."
    elif argv[-1:] == ("--help",):
        help_status, help_evidence = _observe_help_receipt(completed.stdout)
        if help_status == "success":
            status = "executed_pass"
            reason = "Exact allowlisted help command returned bounded non-empty argparse text."
            receipt_evidence = help_evidence
        else:
            status = "executed_fail"
            reason = "Allowlisted help command returned zero but not bounded argparse help text."
            receipt_evidence = help_evidence
    elif receipt_status == "success":
        status = "executed_pass"
        reason = "Exact allowlisted local read-only command returned a valid success receipt."
    else:
        status = "executed_fail"
        reason = "Allowlisted command returned zero but not a valid success robot receipt."
    return {
        "execution_id": execution_id,
        "status": status,
        "exit_code": completed.returncode,
        "reason": reason,
        "evidence": receipt_evidence,
    }


def _observe_help_receipt(stdout: str) -> tuple[str | None, list[str]]:
    """Record bounded argparse help evidence without persisting help text."""
    output_bytes = len(stdout.encode("utf-8"))
    lines = [line for line in stdout.splitlines() if line.strip()]
    if output_bytes > MAX_HELP_OUTPUT_BYTES or len(lines) > MAX_HELP_OUTPUT_LINES:
        return None, ["help_receipt:oversize"]
    if not lines or not lines[0].startswith("usage:"):
        return None, ["help_receipt:invalid_text"]
    return "success", ["help_receipt:valid_text", f"help_nonempty_line_count:{len(lines)}"]


def _observe_robot_receipt(stdout: str) -> tuple[str | None, list[str]]:
    """Record only bounded envelope evidence; never persist command output."""
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return None, ["robot_receipt:invalid_json"]
    if not isinstance(payload, dict):
        return None, ["robot_receipt:non_object"]
    status = payload.get("status")
    if status not in {"success", "error"}:
        return None, ["robot_receipt:missing_status"]
    if not isinstance(payload.get("metadata"), dict) or not isinstance(payload.get("data"), dict):
        return None, ["robot_receipt:missing_envelope_fields"]
    metadata_keys = ",".join(sorted(str(key) for key in payload["metadata"]))
    data_keys = ",".join(sorted(str(key) for key in payload["data"]))
    return str(status), [
        "robot_receipt:valid_envelope",
        f"robot_status:{status}",
        f"metadata_keys:{metadata_keys}",
        f"data_keys:{data_keys}",
    ]


def _safe_output_path(repo_root: Path, output: Path) -> Path:
    """Allow evidence output only inside repo_root and never through symlinks."""
    resolved_root = repo_root.resolve()
    candidate = output.expanduser()
    if not candidate.is_absolute():
        candidate = resolved_root / candidate
    candidate = Path(os.path.normpath(str(candidate)))
    try:
        candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("output path must remain inside repo root") from exc

    current = candidate
    while True:
        if current.is_symlink():
            raise ValueError("output path and its parent directories must not be symlinks")
        if current == resolved_root:
            break
        if current == current.parent:
            raise ValueError("output path could not be anchored to repo root")
        current = current.parent
    resolved_candidate = candidate.resolve(strict=False)
    try:
        resolved_candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("output path must remain inside repo root") from exc
    return candidate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    try:
        output_path = _safe_output_path(repo_root, args.output)
    except ValueError as exc:
        parser.error(str(exc))
    payload = build_private_stabilization_replay(repo_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if payload["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
