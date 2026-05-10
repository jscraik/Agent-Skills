"""Small helpers for agent-facing golden-path command payloads."""

from __future__ import annotations

from typing import Any


SEVERITY_ORDER = {
    "blocker": 0,
    "warning": 1,
    "info": 2,
}
SORT_PRIORITY_KEY = "_sort_priority"


def _priority_value(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 1000


def sort_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort findings deterministically by severity and stable identifier."""
    return sorted(
        findings,
        key=lambda finding: (
            SEVERITY_ORDER.get(str(finding.get("severity")), 99),
            _priority_value(finding.get(SORT_PRIORITY_KEY, finding.get("priority"))),
            str(finding.get("id", "")),
        ),
    )


def _strip_internal_sort_keys(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            key: value for key, value in finding.items()
            if key != SORT_PRIORITY_KEY
        }
        for finding in findings
    ]


def build_golden_path_payload(
    *,
    signals: dict[str, dict[str, Any]],
    normal_next_command: str | None,
    signal_priorities: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Build the stable agent-facing payload shared by golden-path commands."""
    blocker_items = []
    diagnostic_items = []
    for signal_id, signal in signals.items():
        item = {
            "id": signal_id,
            "severity": signal.get("severity", "info"),
            "summary": signal.get("summary", ""),
        }
        priority = (signal_priorities or {}).get(signal_id, signal.get("priority"))
        if priority is not None:
            item[SORT_PRIORITY_KEY] = priority
        if signal.get("next_command"):
            item["next_command"] = signal["next_command"]

        state = signal.get("state")
        if item["severity"] == "blocker" or state in {"block", "error"}:
            item["severity"] = "blocker"
            blocker_items.append(item)
        elif item["severity"] in {"warning", "info"} and state != "pass":
            diagnostic_items.append(item)

    blockers = _strip_internal_sort_keys(sort_findings(blocker_items))
    diagnostic_debt = _strip_internal_sort_keys(sort_findings(diagnostic_items))
    blocking = bool(blockers)

    next_command = None
    next_command_kind = "normal_inspection"
    next_command_blocks_task = False
    selected_next_command: dict[str, Any] | None = None
    command_peers: list[dict[str, Any]] = []
    if blockers:
        selected = blockers[0]
        next_command = selected.get("next_command")
        next_command_kind = "blocking_repair" if next_command else "no_safe_command"
        next_command_blocks_task = True
        selected_next_command = {
            "id": selected["id"],
            "kind": next_command_kind,
            "command": next_command,
            "blocks_task": next_command_blocks_task,
        }
        command_peers = blockers
    else:
        actionable_warnings = [
            item for item in diagnostic_debt
            if item.get("severity") == "warning" and item.get("next_command")
        ]
        if actionable_warnings:
            selected = actionable_warnings[0]
            next_command = selected["next_command"]
            next_command_kind = "diagnostic_advisory"
            selected_next_command = {
                "id": selected["id"],
                "kind": next_command_kind,
                "command": next_command,
                "blocks_task": next_command_blocks_task,
            }
            command_peers = actionable_warnings
        else:
            next_command = normal_next_command
            if next_command:
                next_command_kind = "normal_inspection"
            else:
                next_command_kind = "no_safe_command"
                next_command_blocks_task = True
            selected_next_command = {
                "id": "normal_inspection",
                "kind": next_command_kind,
                "command": next_command,
                "blocks_task": next_command_blocks_task,
            }

    selected_id = selected_next_command["id"] if selected_next_command else None
    secondary_next_commands = [
        {
            "id": item["id"],
            "severity": item.get("severity", "info"),
            "summary": item.get("summary", ""),
            "next_command": item["next_command"],
        }
        for item in command_peers
        if item.get("id") != selected_id and item.get("next_command")
    ]

    if blocking:
        agent_summary = f"Blocked: {blockers[0]['summary']}"
    elif diagnostic_debt:
        agent_summary = f"Usable with diagnostic debt: {diagnostic_debt[0]['summary']}"
    else:
        agent_summary = "Usable: repo doctor found no blocking issues."

    return {
        "agent_summary": agent_summary,
        "blocking": blocking,
        "blockers": blockers,
        "next_command": next_command,
        "next_command_kind": next_command_kind,
        "next_command_blocks_task": next_command_blocks_task,
        "selected_next_command": selected_next_command,
        "secondary_next_commands": secondary_next_commands,
        "signals": signals,
        "diagnostic_debt": diagnostic_debt,
    }


def render_golden_path_summary(
    payload: dict[str, Any],
    *,
    title: str | None = None,
    status_icon: str | None = None,
    indent: str = "  ",
) -> list[str]:
    """Render the compact human summary shared by golden-path commands."""
    summary = payload.get("agent_summary")
    if title:
        label = f"{status_icon} {title}" if status_icon else title
        lines = [f"{label}: {summary}"]
    else:
        lines = [f"{indent}Summary: {summary}"]
    lines.extend(
        [
            f"{indent}Blocking: {payload.get('blocking')}",
            f"{indent}Next: {payload.get('next_command')}",
        ]
    )
    return lines
