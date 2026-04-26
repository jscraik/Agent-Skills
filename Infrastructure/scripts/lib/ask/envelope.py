import json
import logging
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
    ERR_INVALID_SCOPE = "ERR_INVALID_SCOPE"
    ERR_INVALID_PROJECTION_MODE = "ERR_INVALID_PROJECTION_MODE"
    ERR_DEFERRED_PROJECTION_MODE = "ERR_DEFERRED_PROJECTION_MODE"
    ERR_PROJECTION_MUTATION_UNAVAILABLE = "ERR_PROJECTION_MUTATION_UNAVAILABLE"


_VALID_ERROR_CODES = frozenset({
    ErrorCode.SUCCESS, ErrorCode.ERR_RUNTIME, ErrorCode.ERR_VALIDATION,
    ErrorCode.ERR_DEPENDENCY, ErrorCode.ERR_CONFLICT, ErrorCode.ERR_AUTH,
    ErrorCode.ERR_PATH_TRAVERSAL, ErrorCode.ERR_PI_GUARD,
    ErrorCode.ERR_SCHEMA_INVALID, ErrorCode.ERR_REDUNDANCY,
    ErrorCode.ERR_INVALID_HANDOFF, ErrorCode.ERR_INVALID_STATE,
    ErrorCode.ERR_INVALID_SCOPE, ErrorCode.ERR_INVALID_PROJECTION_MODE,
    ErrorCode.ERR_DEFERRED_PROJECTION_MODE,
    ErrorCode.ERR_PROJECTION_MUTATION_UNAVAILABLE,
})


@dataclass
class ErrorObject:
    code: str
    message: str
    fix_suggestion: Optional[str] = None
    help_url: Optional[str] = None

    def __post_init__(self):
        # Validate error code is a known constant
        if self.code not in _VALID_ERROR_CODES:
            logging.getLogger(__name__).warning(
                "Unknown error code '%s' used in ErrorObject. "
                "Consider registering it in ErrorCode.", self.code
            )

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

        # 1. Redact Secrets (Gold Standard 2026 patterns)
        secret_patterns = [
            r"sk-[a-zA-Z0-9]{20,}",       # OpenAI-style
            r"ghp_[a-zA-Z0-9]{36,}",      # GitHub PAT
            r"AIza[a-zA-Z0-9_-]{35,}",    # Google API Key
            r"Bearer\s+[a-zA-Z0-9._-]{20,}", # JWT/Bearer tokens
        ]

        # 2. Redact paths in error messages and free-text fields, but preserve data fields
        home_dir = os.path.expanduser("~")

        def redact_string(s: str) -> str:
            """Redact secrets and paths from a string."""
            for pattern in secret_patterns:
                s = re.sub(pattern, "<REDACTED_SECRET>", s)
            if repo_root:
                s = s.replace(os.path.abspath(repo_root), "<REPO_ROOT>")
            s = s.replace(home_dir, "<USER_HOME>")
            return s

        def redact_errors(errors: list) -> list:
            """Redact paths from error messages only."""
            redacted = []
            for err in errors:
                redacted_err = {
                    "code": err.get("code", ""),
                    "message": redact_string(err.get("message", "")),
                }
                if err.get("fix_suggestion"):
                    redacted_err["fix_suggestion"] = redact_string(err["fix_suggestion"])
                if err.get("help_url"):
                    redacted_err["help_url"] = err["help_url"]
                redacted.append(redacted_err)
            return redacted

        # Redact in errors and metadata strings, but NOT in data fields
        if "errors" in raw_dict:
            raw_dict["errors"] = redact_errors(raw_dict["errors"])

        # Redact secrets globally (they should never appear anywhere)
        json_str = json.dumps(raw_dict, indent=2, ensure_ascii=False)
        for pattern in secret_patterns:
            json_str = re.sub(pattern, "<REDACTED_SECRET>", json_str)

        return json_str
