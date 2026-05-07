"""Small helpers for agent-facing golden-path command payloads."""

from __future__ import annotations

from typing import Any


SEVERITY_ORDER = {
    "blocker": 0,
    "warning": 1,
    "info": 2,
}


def sort_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort findings deterministically by severity and stable identifier."""
    return sorted(
        findings,
        key=lambda finding: (
            SEVERITY_ORDER.get(str(finding.get("severity")), 99),
            str(finding.get("id", "")),
        ),
    )


def build_golden_path_payload(
    *,
    signals: dict[str, dict[str, Any]],
    normal_next_command: str | None,
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
        if signal.get("next_command"):
            item["next_command"] = signal["next_command"]

        state = signal.get("state")
        if item["severity"] == "blocker" or state in {"block", "error"}:
            item["severity"] = "blocker"
            blocker_items.append(item)
        elif item["severity"] in {"warning", "info"} and state != "pass":
            diagnostic_items.append(item)

    blockers = sort_findings(blocker_items)
    diagnostic_debt = sort_findings(diagnostic_items)
    blocking = bool(blockers)

    next_command = None
    if blockers:
        next_command = blockers[0].get("next_command")
    else:
        actionable_warnings = [
            item for item in diagnostic_debt
            if item.get("severity") == "warning" and item.get("next_command")
        ]
        if actionable_warnings:
            next_command = actionable_warnings[0]["next_command"]
        else:
            next_command = normal_next_command

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
