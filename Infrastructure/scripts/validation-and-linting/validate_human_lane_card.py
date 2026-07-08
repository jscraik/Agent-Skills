#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


OPAQUE_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+){2,}$", re.IGNORECASE)
HUMAN_TEXT_PATTERN = re.compile(r"[A-Za-z][A-Za-z]+(?:[ -][A-Za-z][A-Za-z]+)+")


@dataclass(frozen=True)
class Finding:
    path: str
    code: str
    message: str


def _non_empty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _looks_human_readable(value: str) -> bool:
    stripped = value.strip()
    if not HUMAN_TEXT_PATTERN.search(stripped):
        return False
    return not OPAQUE_ID_PATTERN.fullmatch(stripped)


def _validate_human_text(path: str, value: Any, field_name: str) -> list[Finding]:
    if not _non_empty(value):
        return [Finding(path, "missing_human_text", f"{field_name} must be a non-empty human-readable string.")]
    if not _looks_human_readable(value):
        return [
            Finding(
                path,
                "opaque_primary_display_name",
                f"{field_name} must be a human-readable label, not an opaque lane id.",
            )
        ]
    return []


def _iter_lane_cards(payload: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    if isinstance(payload.get("human_lane_card"), dict):
        yield "human_lane_card", payload["human_lane_card"]
    if payload.get("schema_version") == "human_lane_card/v1":
        yield "$", payload
    for key in ("worker_packets", "workers", "lanes"):
        items = payload.get(key)
        if isinstance(items, list):
            for index, item in enumerate(items):
                if isinstance(item, dict):
                    yield f"{key}.{index}", item
    qa_packet = payload.get("qa_packet")
    if isinstance(qa_packet, dict):
        yield "qa_packet", qa_packet


def validate_payload(payload: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    if "human_task_name" in payload or "human_pr_title" in payload:
        findings.extend(_validate_human_text("human_task_name", payload.get("human_task_name"), "human_task_name"))
        findings.extend(_validate_human_text("human_pr_title", payload.get("human_pr_title"), "human_pr_title"))

    lane_cards = list(_iter_lane_cards(payload))
    for path, lane in lane_cards:
        label = lane.get("human_name") or lane.get("human_task_name")
        findings.extend(_validate_human_text(f"{path}.human_name", label, "human_name"))
        if "human_pr_title" in lane:
            findings.extend(_validate_human_text(f"{path}.human_pr_title", lane.get("human_pr_title"), "human_pr_title"))

    if not lane_cards and "human_task_name" not in payload and "human_pr_title" not in payload:
        findings.append(
            Finding(
                "$",
                "missing_human_lane_card",
                "payload must include human_task_name/human_pr_title or at least one human lane card.",
            )
        )
    return findings


def _load_payload(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(payload, dict):
        return None, "json root must be an object"
    return payload, None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate human-readable lane cards in PM/Worker task artifacts.")
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    findings: list[Finding] = []
    for path in args.paths:
        payload, error = _load_payload(path)
        if payload is None:
            findings.append(Finding(path.as_posix(), "invalid_json", error or "could not read json"))
            continue
        for finding in validate_payload(payload):
            findings.append(Finding(f"{path.as_posix()}:{finding.path}", finding.code, finding.message))

    result = {
        "schema_version": "human-lane-card-validation/v1",
        "status": "pass" if not findings else "fail",
        "findings": [asdict(finding) for finding in findings],
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["status"])
        for finding in findings:
            print(f"{finding.path}: {finding.code}: {finding.message}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
