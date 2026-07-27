import shlex
from typing import Any


def _string_sequence(value: object) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return [item for item in value if isinstance(item, str) and item]


def print_readiness_overview(payload: dict[str, Any]) -> None:
    """Print compact contract readiness details when a command exposes them."""
    overview = payload.get("readiness_overview")
    if not isinstance(overview, dict):
        return
    status = overview.get("contract_status")
    gap_count = overview.get("contract_gap_count")
    if status is None or gap_count is None:
        return
    print(f"Readiness: {status} ({gap_count} gaps)")
    ready_sections = _string_sequence(overview.get("ready_contract_sections"))
    blocked_sections = _string_sequence(overview.get("blocked_contract_sections"))
    if ready_sections:
        print(f"Ready sections: {', '.join(ready_sections)}")
    if blocked_sections:
        print(f"Blocked sections: {', '.join(blocked_sections)}")


def print_first_validation_command(payload: dict[str, Any]) -> None:
    """Print the primary validation command for diagnostic human output."""
    commands = payload.get("validation_commands")
    if not commands:
        operation_context = payload.get("operation_context") or {}
        commands = operation_context.get("validation_commands") if isinstance(operation_context, dict) else None
    command_values = _string_sequence(commands)
    if command_values:
        print(f"Validation: {command_values[0]}")


def replay_command(*parts: object) -> str:
    return " ".join(shlex.quote(str(part)) for part in parts if part is not None)


def compact_package_verify_payload(data: dict[str, Any]) -> None:
    """Keep stable package verification decision-sized by default."""
    verification = data.get("skill_package_verification")
    if not isinstance(verification, dict):
        return
    data["skill_package_verification"] = {
        key: verification.get(key)
        for key in (
            "schema_version",
            "query",
            "status",
            "target_identity",
            "archive_identity",
            "provenance_identity",
            "blockers",
            "mutation_status",
            "rollback_hint",
            "agent_summary",
            "validation_commands",
            "next_command",
        )
    }
    data["skill_package_verification"]["claims_boundary"] = (
        "This verifies the requested package without install, extraction, or "
        "runtime-root mutation; it does not prove runtime reachability, task "
        "outcome, publication, or release readiness."
    )


def compact_skill_prove_payload(data: dict[str, Any]) -> None:
    """Keep stable proof output separate from its lower-level runtime report."""
    proof = data.get("skill_proof")
    if not isinstance(proof, dict):
        return

    def selected(section: str, keys: tuple[str, ...]) -> dict[str, object]:
        payload = proof.get(section)
        if not isinstance(payload, dict):
            return {"status": "missing"}
        return {key: payload.get(key) for key in keys if key in payload}

    data["skill_proof"] = {
        "schema_version": proof.get("schema_version"),
        "query": proof.get("query"),
        "handle": proof.get("handle"),
        "proof_status": proof.get("proof_status"),
        "agent_summary": proof.get("agent_summary"),
        "structural_quality": selected(
            "structural_quality", ("status", "audit_level", "audit_command")
        ),
        "runtime_reachability": selected("reachability", ("status", "command")),
        "outcome_proof": selected("outcome_proof", ("status", "evidence_class")),
        "next_command": proof.get("next_command"),
        "validation_commands": proof.get("validation_commands"),
        "claims_boundary": (
            "Structural validation, runtime reachability, and task outcome are "
            "separate facts. This result does not prove installation, activation, "
            "publication, review acceptance, or release readiness."
        ),
    }
    if "goal_resolution" in proof:
        data["skill_proof"]["goal_resolution"] = proof["goal_resolution"]
    data.pop("sdk_skill_proof", None)
