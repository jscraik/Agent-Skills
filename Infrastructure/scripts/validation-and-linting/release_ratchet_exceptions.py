"""Shared release-ratchet exception parsing helpers."""

from __future__ import annotations

import json
from pathlib import Path


from datetime import date


def release_ratchet_exception_paths(handoff_dir: Path, check: str) -> set[str]:
    """Return accepted legacy exception paths for one release-ratchet check."""
    path = handoff_dir / "release-ratchet-exceptions.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    if not isinstance(payload, dict):
        return set()
    entries = payload.get("accepted_exceptions")
    if not isinstance(entries, list):
        return set()
    paths: set[str] = set()
    for entry in entries:
        if (
            isinstance(entry, dict)
            and entry.get("check") == check
            and isinstance(entry.get("path"), str)
            and entry["path"].strip()
            and _not_expired(entry)
            and isinstance(entry.get("ticket"), str)
            and entry["ticket"].strip()
        ):
            paths.add(entry["path"].strip())
    return paths


def _not_expired(entry: dict) -> bool:
    expires = entry.get("expires")
    if not isinstance(expires, str) or not expires.strip():
        return entry.get("adr_reference") not in (None, "")
    try:
        return date.fromisoformat(expires.strip()) >= date.today()
    except ValueError:
        return False
