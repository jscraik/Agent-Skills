from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from ask.skills_sdk.command_evidence_plan import build_command_evidence_plan_receipt


SCHEMA_VERSION = "skills-sdk.private-stabilization-replay.v1"
ALLOWLIST = {
    ("./bin/ask", "sdk", "security", "risk-modes", "Infrastructure/tests/fixtures/skills_sdk/valid_skill", "--preview", "--json", "--robot"),
    ("./bin/ask", "sdk", "intake", "inspect", "Infrastructure/tests/fixtures/skills_sdk/valid_skill", "--preview", "--json", "--robot"),
    ("./bin/ask", "sdk", "lenses", "validate", "--json", "--robot"),
    ("./bin/ask", "sdk", "eval", "profiles", "--preview", "--json", "--robot"),
    ("./bin/ask", "sdk", "security", "adapters", "--preview", "--json", "--robot"),
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
        return {
            "execution_id": execution_id,
            "status": "blocked_unsafe",
            "exit_code": None,
            "reason": "Command is not on the exact private stabilization read-only allowlist.",
            "evidence": ["deny_by_default"],
        }
    try:
        completed = subprocess.run(list(argv), cwd=repo_root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)
    except subprocess.TimeoutExpired:
        return {"execution_id": execution_id, "status": "executed_fail", "exit_code": None, "reason": "Allowlisted command timed out after 30 seconds.", "evidence": ["timeout_seconds:30"]}
    except OSError as exc:
        return {"execution_id": execution_id, "status": "executed_fail", "exit_code": None, "reason": f"Allowlisted command could not execute: {type(exc).__name__}.", "evidence": [f"os_error:{exc.errno}"]}
    status = "executed_pass" if completed.returncode == 0 else "executed_fail"
    return {
        "execution_id": execution_id,
        "status": status,
        "exit_code": completed.returncode,
        "reason": "Exact allowlisted local read-only command completed.",
        "evidence": [f"stdout_bytes:{len(completed.stdout.encode('utf-8'))}", f"stderr_bytes:{len(completed.stderr.encode('utf-8'))}"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build_private_stabilization_replay(args.repo_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if payload["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
