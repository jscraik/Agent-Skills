from __future__ import annotations

from typing import Any

def _operation_context_events(
    consumers: dict[str, dict[str, Any]], *event_types: str
) -> dict[str, dict[str, Any]]:
    """Copy immutable event routes into JSON-safe operation-context data."""
    return {
        event_type: {
            field: list(value) if isinstance(value, list) else value
            for field, value in consumers[event_type].items()
        }
        for event_type in event_types
    }
