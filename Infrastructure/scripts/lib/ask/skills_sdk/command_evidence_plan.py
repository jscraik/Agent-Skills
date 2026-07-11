from __future__ import annotations

import shlex
from pathlib import Path
from typing import Any

from ask.skills_sdk.capability_evidence import build_capability_evidence_receipt


COMMAND_EVIDENCE_PLAN_SCHEMA_VERSION = "skills-sdk.command-evidence-plan-receipt.v0"
COMMAND_EVIDENCE_PLAN_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/command-evidence-plan-receipt.v0.schema.json"
)
COMMAND_EVIDENCE_PLAN_ACCEPTANCE_TRACE = ["FR-008", "SA-003", "VP-032"]

# This is a deliberately small, explicit adapter inventory. It records the
# currently observed internal services without implying that any service is
# extractable, removable, or a public SDK command.
SERVICE_RATIONALIZATION_ROWS = (
    {
        "path": "Infrastructure/scripts/lib/ask/services/codex_preview.py",
        "disposition": "runtime_model_adapter",
        "caller_modules": (
            "Infrastructure/scripts/lib/ask/commands/skills_impl.py",
            "Infrastructure/scripts/lib/ask/skills_sdk/conformance.py",
        ),
        "caller_consequence": (
            "Retain behind the read-only conformance surface; callers must not treat its Codex-source model "
            "as installed-runtime proof."
        ),
    },
    {
        "path": "Infrastructure/scripts/lib/ask/services/plugin_cache.py",
        "disposition": "generated_projection_adapter",
        "caller_modules": (
            "Infrastructure/scripts/lib/ask/commands/plugins.py",
            "Infrastructure/scripts/lib/ask/commands/skills_impl.py",
        ),
        "caller_consequence": (
            "Retain behind sync commands only; callers require an explicit write-authorized projection refresh "
            "and must not edit the cache as canonical source."
        ),
    },
    {
        "path": "Infrastructure/scripts/lib/ask/services/plugin_sources.py",
        "disposition": "compatibility_adapter",
        "caller_modules": (
            "Infrastructure/scripts/lib/ask/commands/plugins.py",
            "Infrastructure/scripts/lib/ask/commands/skills_impl.py",
            "Infrastructure/scripts/lib/ask/services/plugin_cache.py",
        ),
        "caller_consequence": (
            "Retain as the shared plugin-source boundary; callers must preserve its symlink-safety checks "
            "until a separately proven source migration replaces them."
        ),
    },
)


def build_command_evidence_plan_receipt(repo_root: Path, *, scope: str = "capability-matrix") -> dict[str, Any]:
    capability_receipt = build_capability_evidence_receipt(repo_root, scope=scope)
    command_rows: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    for row in capability_receipt["evidence_rows"]:
        if row["kind"] != "command":
            continue
        try:
            command_rows.append(_command_plan_row(row))
        except (TypeError, ValueError) as exc:
            blockers.append(
                _blocker(
                    "invalid_command_evidence_ref",
                    "Command evidence ref is not shell-parseable.",
                    [str(row.get("capability_id") or "capability:unknown"), str(row.get("ref") or ""), str(exc)],
                )
            )
    if not command_rows:
        blockers.append(_blocker("no_command_evidence_refs", "No command evidence refs were found to plan.", [scope]))
    status = "blocked" if blockers else "planned"
    return {
        "schema_version": COMMAND_EVIDENCE_PLAN_SCHEMA_VERSION,
        "schema_uri": COMMAND_EVIDENCE_PLAN_SCHEMA_URI,
        "status": status,
        "operation": "command_evidence_plan",
        "scope": scope,
        "command_count": len(command_rows),
        "commands": command_rows,
        "service_count": len(SERVICE_RATIONALIZATION_ROWS),
        "services": list(SERVICE_RATIONALIZATION_ROWS),
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
    if not isinstance(command, str) or not command.strip():
        raise TypeError("Command evidence ref must be a non-empty string.")
    argv = shlex.split(command)
    replay_disposition, caller_consequence = _replay_disposition(argv)
    return {
        "capability_id": row["capability_id"],
        "command": command,
        "argv": argv,
        "status": "planned",
        "execution_lane": "local_command",
        "receipt_required": True,
        "execution_policy": "manual_or_ci_replay",
        "replay_disposition": replay_disposition,
        "caller_consequence": caller_consequence,
        "source_evidence_reason": row["reason"],
    }


def _replay_disposition(argv: list[str]) -> tuple[str, str]:
    if any(argument.startswith("<") and argument.endswith(">") for argument in argv):
        return (
            "template_requires_concrete_fixture",
            "Do not replay until a repository-owned fixture replaces every template argument.",
        )
    if "--apply" in argv or "--execute" in argv:
        return (
            "authority_bound_mutation",
            "Do not replay under the inventory lane; a bounded authority and a dedicated mutation receipt are required.",
        )
    if "--preview" in argv:
        return (
            "preview_replay",
            "Replay may exercise only the declared preview path and still requires its own run receipt.",
        )
    return (
        "explicit_run_receipt",
        "Replay remains a retained lifecycle surface and requires a command-specific receipt before behavior is claimed.",
    )


def _blocker(blocker_id: str, message: str, evidence: list[str]) -> dict[str, Any]:
    return {
        "id": blocker_id,
        "status": "blocker",
        "severity": "blocker",
        "message": message,
        "evidence": evidence,
    }
