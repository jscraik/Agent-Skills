import json
import uuid
import re
import os
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
        home_dir = os.path.expanduser("~")
        json_str = json_str.replace(home_dir, "<USER_HOME>")
        
        if repo_root:
            json_str = json_str.replace(repo_root, "<REPO_ROOT>")
            
        return json_str
