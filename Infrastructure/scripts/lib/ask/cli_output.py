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


def _compact_package_blockers(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [
        {
            key: blocker.get(key)
            for key in ("rule_id", "class", "status", "message", "path")
            if blocker.get(key) is not None
        }
        for blocker in value
        if isinstance(blocker, dict)
    ]


def _compact_strict_package_readiness(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    package_contract = value.get("package_contract")
    required_fields = package_contract.get("required_fields") if isinstance(package_contract, dict) else {}
    install_gate = package_contract.get("install_gate") if isinstance(package_contract, dict) else {}
    return {
        "status": value.get("status"),
        "canonical_source_path": value.get("canonical_source_path"),
        "missing_fields": required_fields.get("missing", []),
        "gate_blockers": install_gate.get("blocked_reasons", []),
    }


def _package_verify_claims_boundary(mutation_status: object) -> str:
    if isinstance(mutation_status, dict) and mutation_status.get("mutated"):
        return (
            "Verification detected mutation; follow rollback_hint before treating "
            "this result as safe. It does not prove runtime reachability, task "
            "outcome, publication, or release readiness."
        )
    return (
        "This verifies the requested package without install, extraction, or "
        "runtime-root mutation; it does not prove runtime reachability, task "
        "outcome, publication, or release readiness."
    )


def compact_package_verify_payload(data: dict[str, Any]) -> None:
    """Keep stable package verification decision-sized by default."""
    verification = data.get("skill_package_verification")
    if not isinstance(verification, dict):
        return
    compact = {
        key: verification.get(key)
        for key in (
            "schema_version",
            "query",
            "strict",
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
    compact["blockers"] = _compact_package_blockers(verification.get("blockers"))
    strict_readiness = _compact_strict_package_readiness(verification.get("strict_package_readiness"))
    if strict_readiness:
        compact["strict_package_readiness"] = strict_readiness
    data["skill_package_verification"] = compact
    compact["claims_boundary"] = _package_verify_claims_boundary(compact.get("mutation_status"))


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
    analytics = selected(
        "analytics",
        ("status", "invocation_count", "matching_invocation_count", "parse_error_count"),
    )
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
        "analytics": analytics,
        "outcome_proof": selected(
            "outcome_proof",
            ("status", "evidence_class", "evidence_ref", "evidence_digest", "scenario_set", "case_count"),
        ),
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
