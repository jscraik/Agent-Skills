from __future__ import annotations

import json
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
