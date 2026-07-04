from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ask.skills_sdk.package_security_signature import build_package_security_signature_receipt
from ask.skills_sdk.risk_modes import build_risk_mode_taxonomy_receipt


SECURITY_LANE_SCHEMA_VERSION = "skills-sdk.security-lane-receipt.v0"
SECURITY_LANE_SCHEMA_URI = "https://agent-skills.local/schemas/skills-sdk/security-lane-receipt.v0.schema.json"
SECURITY_LANE_ACCEPTANCE_TRACE = ["PU-033", "FR-008", "SA-004", "SEC-001", "VP-033"]


def _digest_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _ask_command(action: str, query: str) -> str:
    return f"ask sdk security {action} {json.dumps(query)} --preview --json --robot"


def _command_record(
    *,
    action: str,
    query: str,
    receipt: dict[str, Any],
    digest_key: str,
) -> dict[str, Any]:
    return {
        "command": _ask_command(action, query),
        "outcome": receipt["status"],
        "receipt_schema_version": receipt["schema_version"],
        "receipt_digest": receipt[digest_key],
        "execution_performed": False,
        "scanner_execution_performed": False,
        "network_accessed": False,
        "credentials_accessed": False,
        "mutation_performed": False,
    }


def _profile_review(profile: str | None, *, require_review: bool) -> dict[str, Any]:
    if not profile:
        return {
            "profile": None,
            "status": "not_requested",
            "required": require_review,
            "codex_exec_command": None,
            "blocker": None,
        }
    command = (
        "codex exec --profile "
        f"{profile} --sandbox read-only --ephemeral --json --output-last-message <path> "
        "-- '<receipt review prompt>'"
    )
    if require_review:
        return {
            "profile": profile,
            "status": "blocked",
            "required": True,
            "codex_exec_command": command,
            "blocker": (
                "profile review was requested as required, but this deterministic receipt builder "
                "does not execute Codex from inside the ask process."
            ),
        }
    return {
        "profile": profile,
        "status": "not_run",
        "required": False,
        "codex_exec_command": command,
        "blocker": (
            "profile review is recorded as an optional external evidence lane; run the generated "
            "Codex command separately when model review evidence is needed."
        ),
    }


def build_security_lane_receipt(
    repo_root: Path,
    *,
    source_path: Path,
    query: str,
    profile: str | None = None,
    require_review: bool = False,
) -> dict[str, Any]:
    """Build the deterministic Skills SDK security lane without executing skill content."""
    package_receipt = build_package_security_signature_receipt(repo_root, source_path=source_path, query=query)
    risk_receipt = build_risk_mode_taxonomy_receipt(repo_root, source_path=source_path, query=query)
    command_records = [
        _command_record(
            action="package-signature",
            query=query,
            receipt=package_receipt,
            digest_key="package_security_signature_digest",
        ),
        _command_record(
            action="risk-modes",
            query=query,
            receipt=risk_receipt,
            digest_key="taxonomy_digest",
        ),
    ]
    profile_review = _profile_review(profile, require_review=require_review)
    status = "blocked" if profile_review["status"] == "blocked" else "pass"
    lane_material = {
        "package_security_signature_digest": package_receipt["package_security_signature_digest"],
        "risk_mode_taxonomy_digest": risk_receipt["taxonomy_digest"],
        "commands": command_records,
        "profile_review": profile_review,
    }
    return {
        "schema_version": SECURITY_LANE_SCHEMA_VERSION,
        "schema_uri": SECURITY_LANE_SCHEMA_URI,
        "status": status,
        "operation": "security_lane_preview",
        "query": query,
        "package_id": package_receipt["package_id"],
        "package_digest": package_receipt["package_digest"],
        "source_digest": package_receipt["source_digest"],
        "security_lane_digest": _digest_json(lane_material),
        "package_security_signature_digest": package_receipt["package_security_signature_digest"],
        "risk_mode_taxonomy_digest": risk_receipt["taxonomy_digest"],
        "indicator_summary": package_receipt["indicator_summary"],
        "primary_mode": risk_receipt["primary_mode"],
        "detected_modes": risk_receipt["detected_modes"],
        "commands": command_records,
        "profile_review": profile_review,
        "package_security_signature_receipt": package_receipt,
        "risk_mode_taxonomy_receipt": risk_receipt,
        "execution_performed": False,
        "scanner_execution_performed": False,
        "network_accessed": False,
        "credentials_accessed": False,
        "mutation_performed": False,
        "acceptance_trace": SECURITY_LANE_ACCEPTANCE_TRACE,
        "agent_summary": (
            f"security lane inspected {package_receipt['package_id']} with {len(command_records)} deterministic "
            f"security command(s); profile review status is {profile_review['status']}."
        ),
    }
