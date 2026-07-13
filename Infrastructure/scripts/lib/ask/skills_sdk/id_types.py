"""Schema-backed branded identifiers for agent-facing SDK artifacts.

The public policy lives in ``Infrastructure/config/schemas/skills-sdk``. This
module is a compatibility adapter for emitters, not a second type authority:
it loads the canonical pattern and validates values at command boundaries.
Protocol-native identifiers may remain outside the policy when a transport
requires a different wire representation.
"""

from __future__ import annotations

import hashlib
import json
import re
import secrets
import string
from pathlib import Path
from typing import Callable


def _load_policy() -> dict[str, object]:
    repo_root = Path(__file__).resolve().parents[5]
    policy_path = repo_root / "Infrastructure/config/schemas/skills-sdk/type-policy.v1.json"
    payload = json.loads(policy_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Skills SDK type policy must be a JSON object")
    return payload


_TYPE_POLICY = _load_policy()
_ID_CONTRACT = _TYPE_POLICY.get("id_contract")
if not isinstance(_ID_CONTRACT, dict):
    raise RuntimeError("Skills SDK type policy is missing id_contract")
_ID_SCHEMA_PATH = _ID_CONTRACT.get("schema_path")
if not isinstance(_ID_SCHEMA_PATH, str):
    raise RuntimeError("Skills SDK type policy is missing id_contract.schema_path")
_ID_SCHEMA = json.loads(
    (Path(__file__).resolve().parents[5] / _ID_SCHEMA_PATH).read_text(encoding="utf-8")
)
if not isinstance(_ID_SCHEMA, dict) or not isinstance(_ID_SCHEMA.get("pattern"), str):
    raise RuntimeError("Skills SDK branded ID schema must declare a string pattern")
BRANDED_ID_PATTERN = _ID_SCHEMA["pattern"]
_PREFIX_PATTERN = BRANDED_ID_PATTERN.removeprefix("^").split("_", 1)[0]
_BRANDED_ID_RE = re.compile(BRANDED_ID_PATTERN)
_PREFIX_RE = re.compile(rf"^{_PREFIX_PATTERN}$")
_ALPHABET = string.ascii_lowercase + string.digits


class BrandedIdError(ValueError):
    """Raised when an ID does not satisfy the SDK brand contract."""


def _validate_prefix(prefix: str) -> None:
    if not isinstance(prefix, str) or not _PREFIX_RE.fullmatch(prefix):
        raise ValueError("ID prefix must use lowercase ASCII letters and digits")


def _validate_token(token: str, *, length: int) -> None:
    if len(token) != length:
        raise ValueError(f"ID token must be exactly {length} characters")
    if not re.fullmatch(r"[a-z0-9]+", token):
        raise ValueError("ID token must be lowercase alphanumeric")


def new_branded_id(
    prefix: str,
    *,
    length: int = 12,
    token_provider: Callable[[int], str] | None = None,
) -> str:
    """Create a prefixed, lowercase alphanumeric ID.

    ``token_provider`` is injectable so deterministic tests can prove the
    shape without weakening production randomness.
    """

    _validate_prefix(prefix)
    if length < 12 or length > 32:
        raise ValueError("ID token length must be between 12 and 32 characters")
    provider = token_provider or (lambda size: "".join(secrets.choice(_ALPHABET) for _ in range(size)))
    token = provider(length)
    _validate_token(token, length=length)
    value = f"{prefix}_{token}"
    require_branded_id(value, prefix=prefix)
    return value


def branded_id_from_digest(prefix: str, digest: str, *, length: int = 16) -> str:
    """Derive a stable branded ID from an existing digest without a UUID."""

    _validate_prefix(prefix)
    if length < 12 or length > 32:
        raise ValueError("ID token length must be between 12 and 32 characters")
    token = hashlib.sha256(digest.encode("utf-8")).hexdigest()[:length]
    return new_branded_id(prefix, length=length, token_provider=lambda _size: token)


def require_branded_id(value: str, *, prefix: str | None = None) -> str:
    """Validate and return an ID at a JSON or command boundary."""

    if not isinstance(value, str) or not _BRANDED_ID_RE.fullmatch(value):
        raise BrandedIdError("ID must match <lowercase-brand>_<12-32 lowercase alphanumeric characters>")
    actual_prefix = value.split("_", 1)[0]
    if prefix is not None:
        _validate_prefix(prefix)
        if actual_prefix != prefix:
            raise BrandedIdError(f"ID prefix must be {prefix!r}, got {actual_prefix!r}")
    return value
