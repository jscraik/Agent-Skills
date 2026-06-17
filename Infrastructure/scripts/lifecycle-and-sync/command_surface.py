#!/usr/bin/env python3
"""Resolve SDK skill names and reviewer roles for ASK commands."""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from sdk_skill_registry import (
    build_sdk_skill_record_candidates,
    build_sdk_skill_records,
    resolve_sdk_skill_handle,
    sdk_duplicate_handle_violations,
)
from selection_policy import policy_identity

SKILL_MENTION_RE = re.compile(r"(?<![\w./-])\$([a-z][a-z0-9-]*(?::[a-z][a-z0-9-]*)?)(?![:\w-])")
REVIEWER_MENTION_RE = re.compile(r"(?<![\w./-])@([A-Za-z0-9][A-Za-z0-9_-]*)")
REVIEWER_MANIFEST = Path(
    os.environ.get("CODEX_AGENTS_MANIFEST", Path.home() / ".codex" / "agents" / "manifest.json")
)


@dataclass(frozen=True)
class ReviewerRole:
    handle: str
    kind: str
    source_path: str | None
    owner: str
    description: str
    provenance: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        return {key: value for key, value in payload.items() if value is not None}


def normalize_handle(raw: str) -> str:
    """Normalize a CLI/user mention to the SDK skill name or reviewer role."""
    return raw.strip().removeprefix("$").removeprefix("@").strip()


def resolve_skill_handle(handle: str, *, repo_root_path: Path | None = None) -> dict[str, Any]:
    """Resolve one SDK skill name to its canonical source metadata."""
    return resolve_sdk_skill_handle(handle, repo_root_path=repo_root_path)


def _load_reviewer_roles(manifest_path: Path = REVIEWER_MANIFEST) -> tuple[list[dict[str, Any]], str | None]:
    if not manifest_path.exists():
        return [], f"Reviewer manifest not found: {manifest_path}"
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], f"Reviewer manifest could not be read: {exc}"
    rows = payload.get("agents") if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        return [], "Reviewer manifest must be a list or an object with an agents list."
    return [row for row in rows if isinstance(row, dict) and row.get("role")], None


def build_reviewer_handles(manifest_path: Path = REVIEWER_MANIFEST) -> tuple[list[ReviewerRole], str | None]:
    """Build reviewer roles from the Codex agents manifest."""
    rows, error = _load_reviewer_roles(manifest_path)
    roles = [
        ReviewerRole(
            handle=str(row["role"]).strip(),
            kind="reviewer",
            source_path=str(row.get("source") or ""),
            owner="codex-agents",
            description=f"Codex subagent role: {row['role']}",
            provenance={
                "manifest_path": manifest_path.as_posix(),
                "output": str(row.get("output") or ""),
                "model": str(row.get("model") or ""),
            },
        )
        for row in rows
    ]
    return sorted(roles, key=lambda item: item.handle), error


def _reviewer_alias_key(handle: str) -> str:
    return normalize_handle(handle).replace("-", "").replace("_", "")


def resolve_reviewer_handle(handle: str, *, manifest_path: Path = REVIEWER_MANIFEST) -> dict[str, Any]:
    normalized = normalize_handle(handle)
    roles, manifest_error = build_reviewer_handles(manifest_path)
    exact = [item for item in roles if item.handle == normalized]
    matches = exact or [item for item in roles if _reviewer_alias_key(item.handle) == _reviewer_alias_key(normalized)]
    if not matches:
        return {
            "status": "error",
            "error_code": "unknown_reviewer",
            "handle": normalized,
            "manifest_error": manifest_error,
            "operator_action": "Check the Codex agents manifest for an available reviewer/subagent role.",
        }
    if len(matches) > 1:
        return {
            "status": "error",
            "error_code": "ambiguous_reviewer",
            "handle": normalized,
            "matches": [item.to_dict() for item in matches],
            "operator_action": "Use the exact reviewer role name from the Codex agents manifest.",
        }
    return {"status": "ok", **matches[0].to_dict(), "canonical_handle": matches[0].handle}


def _mention_rows(pattern: re.Pattern[str], prefix: str, text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for match in pattern.finditer(text):
        raw_handle = match.group(1)
        rows.append(
            {
                "mention": raw_handle,
                "token": f"{prefix}{raw_handle}",
                "handle": normalize_handle(raw_handle),
                "start": match.start(),
                "end": match.end(),
            }
        )
    return rows


def parse_sdk_references(text: str, *, repo_root_path: Path | None = None) -> dict[str, Any]:
    """Parse SDK skill mentions and reviewer role mentions from a prompt."""
    skill_mentions = _mention_rows(SKILL_MENTION_RE, "$", text)
    reviewer_mentions = _mention_rows(REVIEWER_MENTION_RE, "@", text)
    unresolved: list[dict[str, Any]] = []

    for mention in skill_mentions:
        resolution = resolve_skill_handle(str(mention["handle"]), repo_root_path=repo_root_path)
        mention["role"] = "sdk_skill"
        mention["resolution"] = resolution
        if resolution.get("status") != "ok":
            unresolved.append(
                {
                    "namespace": "skills",
                    "token": mention["token"],
                    "handle": mention["handle"],
                    "error_code": resolution.get("error_code"),
                    "operator_action": resolution.get("operator_action"),
                }
            )

    for mention in reviewer_mentions:
        resolution = resolve_reviewer_handle(str(mention["handle"]))
        mention["role"] = "reviewer"
        mention["resolution"] = resolution
        if resolution.get("status") != "ok":
            unresolved.append(
                {
                    "namespace": "reviewers",
                    "token": mention["token"],
                    "handle": mention["handle"],
                    "error_code": resolution.get("error_code"),
                    "operator_action": resolution.get("operator_action"),
                }
            )

    return {
        "schema_version": "sdk-reference-parse.v1",
        "status": "pass" if not unresolved else "fail",
        "skill_mentions": skill_mentions,
        "reviewer_mentions": reviewer_mentions,
        "unresolved": unresolved,
        "mention_counts": {
            "skills": len(skill_mentions),
            "reviewers": len(reviewer_mentions),
            "unresolved": len(unresolved),
        },
    }


def handles_report(*, repo_root_path: Path | None = None, include_handles: bool = True) -> dict[str, Any]:
    candidates = build_sdk_skill_record_candidates(repo_root_path=repo_root_path, visibility="advanced")
    records = build_sdk_skill_records(repo_root_path=repo_root_path, visibility="advanced")
    public_rows = [record.to_resolution() for record in records] if include_handles else []
    violations = sdk_duplicate_handle_violations(candidates)
    return {
        "schema_version": "sdk-skill-handles.v1",
        "status": "pass" if not violations else "fail",
        "policy_identity": policy_identity(),
        "generated_from": "sdk_flat_registry",
        "projection_path": None,
        "handle_count": len(records),
        "violations": violations,
        "handles": public_rows,
        "hidden_handles": [],
        "notes": [
            "Skill handles resolve from the SDK-flat registry and canonical SKILL.md frontmatter.",
            "Projection writes are handled by workspace flat sync; handles report is read-only.",
        ],
    }


def removed_projection_payload(action: str) -> dict[str, Any]:
    return {
        "schema_version": "sdk-removed-projection.v1",
        "status": "error",
        "action": action,
        "error_code": "ERR_REMOVED_PROJECTION",
        "message": "Removed projection generation is not part of the SDK skill path.",
        "fix_suggestion": "Use ./bin/ask skills sync --scope workspace --projection flat --json --robot and ./bin/ask skills handles --check --json --robot.",
        "violations": [{"code": "REMOVED_PROJECTION_GENERATION"}],
    }
