from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Any


def load_json_object(path: Path) -> dict[str, Any]:
    """Load a JSON object with path context instead of silently degrading."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RuntimeError(f"failed to read JSON file {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"failed to parse JSON file {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected JSON object in {path}, got {type(payload).__name__}")
    return payload


def stable_json_hash(payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None
