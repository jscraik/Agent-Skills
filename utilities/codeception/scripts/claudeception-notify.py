#!/usr/bin/env python3
"""Codex notify hook for Claudeception.

This script is meant to be used with Codex's `notify` config:

    notify = ["python3", "/path/to/claudeception-notify.py"]

Codex passes a single JSON argument describing the event (currently `agent-turn-complete`).
See the Codex docs for the full schema.
""" 

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional


def _load_payload() -> Dict[str, Any]:
    # Primary: Codex passes the payload as a single JSON argument.
    if len(sys.argv) >= 2 and sys.argv[1].strip():
        try:
            return json.loads(sys.argv[1])
        except json.JSONDecodeError:
            # Fall back to stdin.
            pass

    # Compatibility fallback: read JSON from stdin.
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _coalesce_keys(d: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    for k in keys:
        if k in d:
            return d[k]
    return default


def _as_str_list(v: Any) -> List[str]:
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x) for x in v if x is not None]
    return [str(v)]


def _truncate(s: str, n: int) -> str:
    s = " ".join(s.split())
    if len(s) <= n:
        return s
    return s[: max(0, n - 1)] + "…"


def _notify(title: str, message: str, group: Optional[str] = None) -> None:
    """Best-effort desktop notification (Linux) with a stdout fallback."""

    if shutil.which("terminal-notifier"):
        cmd = [
            "terminal-notifier",
            "-title",
            title,
            "-message",
            message,
        ]
        if group:
            cmd += ["-group", group]
        try:
            subprocess.check_output(cmd)
            return
        except Exception:
            pass

    # Linux (libnotify)
    if shutil.which("notify-send"):
        cmd = ["notify-send", title, message]
        try:
            subprocess.check_output(cmd)
            return
        except Exception:
            pass

    # Fallback: print to stderr so it doesn't pollute command output.
    print(f"[claudeception] {title}: {message}", file=sys.stderr)


def main() -> int:
    payload = _load_payload()
    if payload.get("type") != "agent-turn-complete":
        return 0

    thread_id = _coalesce_keys(payload, "thread-id", "thread_id", default="")
    last = str(_coalesce_keys(payload, "last-assistant-message", "last_assistant_message", default="")).strip()
    inputs = _as_str_list(_coalesce_keys(payload, "input-messages", "input_messages", default=[]))

    title = "Codex turn complete"
    if last:
        title = f"Codex: {_truncate(last, 48)}"

    # Keep the toast short: show the user prompt context + a reminder.
    prompt_snip = _truncate(" ".join(inputs), 140) if inputs else ""
    reminder = "If this required discovery, run $claudeception to extract a skill."
    message = reminder if not prompt_snip else f"{reminder}\n\nPrompt: {prompt_snip}"

    group = f"codex-{thread_id}" if thread_id else None
    _notify(title, message, group=group)
    print(f"[codeception] notify hook ran: {title}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
