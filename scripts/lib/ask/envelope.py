import json
import uuid
from dataclasses import dataclass, asdict, field
from typing import Any, List, Optional, Dict

@dataclass
class ErrorObject:
    code: str
    message: str
    fix_suggestion: Optional[str] = None
    help_url: Optional[str] = None

@dataclass
class CallResult:
    status: str = "success"
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=lambda: {
        "version": "0.1.0",
        "command": "unknown",
        "next_steps": []
    })
    data: Dict[str, Any] = field(default_factory=dict)
    telemetry: Dict[str, Any] = field(default_factory=dict)
    errors: List[ErrorObject] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)
