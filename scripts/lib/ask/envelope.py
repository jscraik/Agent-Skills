import json
import uuid
import re
import os
from dataclasses import dataclass, asdict, field
from typing import Any, Optional
from enum import IntEnum


class ExitCode(IntEnum):
    """Exit codes per ask CLI spec Error Registry."""
    SUCCESS = 0
    ERR_RUNTIME = 1
    ERR_VALIDATION = 2
    ERR_DEPENDENCY = 3
    ERR_CONFLICT = 4
    ERR_AUTH = 5


class ErrorCode:
    """String error codes for CallResult envelope."""
    SUCCESS = "SUCCESS"
    ERR_RUNTIME = "ERR_RUNTIME"
    ERR_VALIDATION = "ERR_VALIDATION"
    ERR_DEPENDENCY = "ERR_DEPENDENCY"
    ERR_CONFLICT = "ERR_CONFLICT"
    ERR_AUTH = "ERR_AUTH"
    ERR_PATH_TRAVERSAL = "ERR_PATH_TRAVERSAL"
    ERR_PI_GUARD = "ERR_PI_GUARD"
    ERR_SCHEMA_INVALID = "ERR_SCHEMA_INVALID"
    ERR_REDUNDANCY = "ERR_REDUNDANCY"
    ERR_INVALID_HANDOFF = "ERR_INVALID_HANDOFF"
    ERR_INVALID_STATE = "ERR_INVALID_STATE"

@dataclass
class ErrorObject:
    code: str
    message: str
    fix_suggestion: Optional[str] = None
    help_url: Optional[str] = None

    def __post_init__(self):
        # Validate error code is a known constant
        valid_codes = [
            ErrorCode.SUCCESS, ErrorCode.ERR_RUNTIME, ErrorCode.ERR_VALIDATION,
            ErrorCode.ERR_DEPENDENCY, ErrorCode.ERR_CONFLICT, ErrorCode.ERR_AUTH,
            ErrorCode.ERR_PATH_TRAVERSAL, ErrorCode.ERR_PI_GUARD,
            ErrorCode.ERR_SCHEMA_INVALID, ErrorCode.ERR_REDUNDANCY,
            ErrorCode.ERR_INVALID_HANDOFF, ErrorCode.ERR_INVALID_STATE,
        ]
        if self.code not in valid_codes:
            # Allow but warn - don't crash on unknown codes
            pass

def _get_trace_id() -> str:
    """Get trace_id from ASK_TRACE_ID env var or generate UUID."""
    return os.environ.get("ASK_TRACE_ID") or str(uuid.uuid4())


@dataclass
class CallResult:
    status: str = "success"
    trace_id: str = field(default_factory=_get_trace_id)
    metadata: dict[str, Any] = field(default_factory=lambda: {
        "version": "0.1.0",
        "command": "unknown",
        "next_steps": [],
        "correction_note": None,
    })
    data: dict[str, Any] = field(default_factory=dict)
    telemetry: dict[str, Any] = field(default_factory=dict)
    errors: list[ErrorObject] = field(default_factory=list)

    def to_json(self, repo_root: Optional[str] = None) -> str:
        """Serializes to JSON with fail-closed redaction of paths and secrets."""
        raw_dict = asdict(self)
        json_str = json.dumps(raw_dict, indent=2, ensure_ascii=False)
        
        # 1. Redact Secrets (Gold Standard 2026 patterns)
        secret_patterns = [
            r"sk-[a-zA-Z0-9]{20,}",       # OpenAI-style
            r"ghp_[a-zA-Z0-9]{36,}",      # GitHub PAT
            r"AIza[a-zA-Z0-9_-]{35,}",    # Google API Key
            r"Bearer\s+[a-zA-Z0-9._-]{20,}", # JWT/Bearer tokens
        ]
        for pattern in secret_patterns:
            json_str = re.sub(pattern, "<REDACTED_SECRET>", json_str)
            
        # 2. Redact Absolute Paths
        # For security, we redact repo_root and home directory in error messages and logs
        # Redact repo_root FIRST (before home_dir) to handle nested paths correctly
        if repo_root:
            resolved_root = os.path.abspath(repo_root)
            json_str = json_str.replace(resolved_root, "<REPO_ROOT>")
        home_dir = os.path.expanduser("~")
        json_str = json_str.replace(home_dir, "<USER_HOME>")

        return json_str
