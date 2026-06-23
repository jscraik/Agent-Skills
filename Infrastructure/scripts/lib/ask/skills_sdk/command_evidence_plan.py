from __future__ import annotations

import shlex
from pathlib import Path
from typing import Any

from ask.skills_sdk.capability_evidence import build_capability_evidence_receipt


COMMAND_EVIDENCE_PLAN_SCHEMA_VERSION = "skills-sdk.command-evidence-plan-receipt.v0"
COMMAND_EVIDENCE_PLAN_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/command-evidence-plan-receipt.v0.schema.json"
)
COMMAND_EVIDENCE_PLAN_ACCEPTANCE_TRACE = ["FR-008", "SA-003", "VP-032"]


def build_command_evidence_plan_receipt(repo_root: Path, *, scope: str = "capability-matrix") -> dict[str, Any]:
    capability_receipt = build_capability_evidence_receipt(repo_root, scope=scope)
    command_rows = [
        _command_plan_row(row)
        for row in capability_receipt["evidence_rows"]
        if row["kind"] == "command"
    ]
    blockers = [
        {
            "id": "no_command_evidence_refs",
            "status": "blocker",
            "severity": "blocker",
            "message": "No command evidence refs were found to plan.",
            "evidence": [scope],
        }
    ] if not command_rows else []
    status = "planned" if command_rows else "blocked"
    return {
        "schema_version": COMMAND_EVIDENCE_PLAN_SCHEMA_VERSION,
        "schema_uri": COMMAND_EVIDENCE_PLAN_SCHEMA_URI,
        "status": status,
        "operation": "command_evidence_plan",
        "scope": scope,
        "command_count": len(command_rows),
        "commands": command_rows,
        "blockers": blockers,
        "mutation_performed": False,
        "command_execution_performed": False,
        "acceptance_trace": COMMAND_EVIDENCE_PLAN_ACCEPTANCE_TRACE,
        "agent_summary": (
            f"Command evidence plan classified {len(command_rows)} replayable command ref(s) "
            "without executing them; each command still needs its own run receipt before it can prove behavior."
        ),
    }


def _command_plan_row(row: dict[str, Any]) -> dict[str, Any]:
    command = row["ref"]
    try:
        argv = shlex.split(command)
    except ValueError:
        argv = []
    return {
        "capability_id": row["capability_id"],
        "command": command,
        "argv": argv,
        "status": "planned",
        "execution_lane": "local_command",
        "receipt_required": True,
        "execution_policy": "manual_or_ci_replay",
        "source_evidence_reason": row["reason"],
    }
