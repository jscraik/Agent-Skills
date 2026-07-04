#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _read_events(path: Path) -> tuple[list[dict[str, Any]], str]:
    raw = path.read_text(encoding="utf-8")
    events: list[dict[str, Any]] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped.startswith("{"):
            continue
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            events.append(value)
    return events, raw


def classify(path: Path) -> dict[str, Any]:
    events, raw = _read_events(path)
    text = raw.lower()
    agent_messages = [
        item.get("item", {}).get("text", "")
        for item in events
        if item.get("type") == "item.completed" and item.get("item", {}).get("type") == "agent_message"
    ]
    observed_text = "\n".join(agent_messages).lower()
    command_seen = "ask sdk security run-lane" in raw
    lane_success_seen = any(
        event.get("status") == "success"
        and isinstance(event.get("data"), dict)
        and isinstance(event["data"].get("skills_sdk_security_lane"), dict)
        and event["data"]["skills_sdk_security_lane"].get("status") == "pass"
        for event in events
    )
    incompatible_payload = "incompatible payload" in text or "failed to parse function arguments" in text
    startup_failed = "failed to initialize in-process app-server client" in text
    sandbox_failed = "sandbox_apply: operation not permitted" in text
    invented_failure = sandbox_failed and "sandbox_apply: operation not permitted" not in raw

    if startup_failed:
        status = "blocked"
        blocker = "codex_app_server_startup"
        diagnostic = "codex exec could not initialize its in-process app-server client."
    elif lane_success_seen:
        status = "pass"
        blocker = None
        diagnostic = "codex exec evidence includes a successful SDK security lane receipt."
    elif incompatible_payload:
        status = "blocked"
        blocker = "model_tool_call_payload"
        diagnostic = "the local model attempted tool use with a payload Codex could not parse."
    elif command_seen and "pass" in observed_text:
        status = "weak"
        blocker = "agent_message_without_receipt"
        diagnostic = "agent text mentions pass, but the JSONL does not include the security lane receipt."
    else:
        status = "blocked"
        blocker = "missing_security_lane_evidence"
        diagnostic = "codex exec did not produce observable SDK security lane receipt evidence."

    return {
        "schema_version": "skills-sdk.codex-exec-security-lane-classification.v0",
        "status": status,
        "blocker": blocker,
        "diagnostic": diagnostic,
        "evidence_path": path.as_posix(),
        "event_count": len(events),
        "command_seen": command_seen,
        "lane_success_seen": lane_success_seen,
        "startup_failed": startup_failed,
        "incompatible_payload": incompatible_payload,
        "sandbox_failed": sandbox_failed,
        "invented_failure": invented_failure,
        "agent_message_count": len(agent_messages),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify codex exec evidence for the SDK security lane.")
    parser.add_argument("jsonl", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = classify(args.jsonl)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"{result['status']}: {result['diagnostic']}")
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
