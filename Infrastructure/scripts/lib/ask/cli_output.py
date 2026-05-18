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
