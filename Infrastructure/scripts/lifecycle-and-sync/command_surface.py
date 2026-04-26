#!/usr/bin/env python3
"""Resolve command-visible skill and reviewer handles for rooted skill trees."""

from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from generate_skillset_manifests import build_manifest_report
from selection_policy import ROOT_SKILL_SET_NAMES, policy_identity
from skillset_model import repo_root

HANDLE_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
COMMAND_VISIBILITY = {"orchestrator", "direct", "target", "reviewer", "none"}
REVIEWER_MANIFEST = Path(os.environ.get("CODEX_AGENTS_MANIFEST", Path.home() / ".codex" / "agents" / "manifest.json"))
RESERVED_SKILL_HANDLES = {
    "repo",
    "runtime",
    "plugins",
    "evals",
    "graph",
    "mcp",
    "wiki",
    "workouts",
    "skill",
    "skills",
    "reviewer",
    "reviewers",
}


@dataclass(frozen=True)
class CommandHandle:
    handle: str
    kind: str
    command_visibility: str
    runtime_visibility: str | None
    source_path: str | None
    stub_path: str | None
    owner: str
    description: str
    invoke_via: str | None = None
    level: str | None = None
    provenance: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        return {key: value for key, value in payload.items() if value is not None}


def normalize_handle(raw: str) -> str:
    """Normalize CLI/user handle input without accepting alternate spellings."""
    return raw.strip().removeprefix("$").removeprefix("@").strip()


def _normalized_confusable_key(handle: str) -> str:
    return handle.lower().replace("_", "-")


def _command_visibility_for(row: dict[str, Any]) -> str:
    explicit = (
        row.get("command_visibility")
        or row.get("command-visibility")
        or row.get("metadata", {}).get("command_visibility")
        or row.get("metadata", {}).get("command-visibility")
    )
    if explicit:
        value = str(explicit).strip().lower().replace("_", "-")
        return value if value in COMMAND_VISIBILITY else "none"

    module_id = str(row.get("id", ""))
    level = str(row.get("level", ""))
    if module_id.endswith("-router") or level in {"router", "compound"}:
        return "orchestrator"
    if module_id in {"skill-builder", "plugin-builder"}:
        return "orchestrator"
    if str(row.get("runtime_visibility", "latent")) in {"root", "flat"}:
        return "direct"
    return "target"


def _invoke_via_for(row: dict[str, Any], command_visibility: str) -> str | None:
    explicit = (
        row.get("invoke_via")
        or row.get("invoke-via")
        or row.get("metadata", {}).get("invoke_via")
        or row.get("metadata", {}).get("invoke-via")
    )
    if explicit:
        return str(explicit).strip()
    if command_visibility == "target":
        return str(row.get("skill_set", "")).strip() or None
    return None


def _handle_from_manifest_row(row: dict[str, Any]) -> CommandHandle:
    handle = str(row.get("handle") or row.get("id") or "").strip()
    command_visibility = _command_visibility_for(row)
    source_path = str(row.get("source_path") or "").strip() or None
    stub_path = f".agents/skills/{handle}/SKILL.md" if handle and command_visibility != "none" else None
    return CommandHandle(
        handle=handle,
        kind="skill",
        command_visibility=command_visibility,
        runtime_visibility=str(row.get("runtime_visibility") or "latent"),
        source_path=source_path,
        stub_path=stub_path,
        owner=str(row.get("skill_set") or ""),
        description=str(row.get("description") or ""),
        invoke_via=_invoke_via_for(row, command_visibility),
        level=str(row.get("level") or ""),
        provenance=row.get("provenance") if isinstance(row.get("provenance"), dict) else None,
    )


def build_skill_handles(*, repo_root_path: Path | None = None) -> list[CommandHandle]:
    """Build command-visible skill handles from the canonical rooted manifest report."""
    root = repo_root_path or repo_root()
    report = build_manifest_report(root / ".skillsets")
    handles: list[CommandHandle] = []
    for manifest in report.get("manifests", []):
        for row in manifest.get("rows", []):
            handle = _handle_from_manifest_row(row)
            if handle.command_visibility != "none":
                handles.append(handle)
    return sorted(handles, key=lambda item: (item.handle, item.owner, item.source_path or ""))


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


def build_reviewer_handles(manifest_path: Path = REVIEWER_MANIFEST) -> tuple[list[CommandHandle], str | None]:
    """Build reviewer handles from the Codex agents manifest."""
    rows, error = _load_reviewer_roles(manifest_path)
    handles = [
        CommandHandle(
            handle=str(row["role"]).strip(),
            kind="reviewer",
            command_visibility="reviewer",
            runtime_visibility=None,
            source_path=str(row.get("source") or ""),
            stub_path=None,
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
    return sorted(handles, key=lambda item: item.handle), error


def validate_skill_handles(handles: list[CommandHandle], *, repo_root_path: Path | None = None) -> list[dict[str, Any]]:
    """Return validation violations for command-visible skill handles."""
    root = (repo_root_path or repo_root()).resolve()
    violations: list[dict[str, Any]] = []
    by_key: dict[str, list[CommandHandle]] = defaultdict(list)
    for handle in handles:
        by_key[_normalized_confusable_key(handle.handle)].append(handle)
        if not HANDLE_RE.match(handle.handle):
            violations.append({"code": "INVALID_HANDLE_SLUG", "handle": handle.handle})
        if handle.handle in RESERVED_SKILL_HANDLES:
            violations.append({"code": "RESERVED_HANDLE", "handle": handle.handle})
        if handle.command_visibility not in COMMAND_VISIBILITY - {"reviewer"}:
            violations.append({
                "code": "INVALID_SKILL_COMMAND_VISIBILITY",
                "handle": handle.handle,
                "command_visibility": handle.command_visibility,
            })
        if handle.command_visibility == "target" and not handle.invoke_via:
            violations.append({"code": "TARGET_HANDLE_MISSING_INVOKE_VIA", "handle": handle.handle})
        if handle.invoke_via and handle.invoke_via not in ROOT_SKILL_SET_NAMES:
            violations.append({
                "code": "TARGET_HANDLE_INVALID_INVOKE_VIA",
                "handle": handle.handle,
                "invoke_via": handle.invoke_via,
            })
        if not handle.source_path:
            violations.append({"code": "SKILL_HANDLE_MISSING_SOURCE_PATH", "handle": handle.handle})
            continue
        source = root / handle.source_path
        if not source.exists():
            violations.append({
                "code": "SKILL_HANDLE_SOURCE_MISSING",
                "handle": handle.handle,
                "source_path": handle.source_path,
            })
            continue
        try:
            source.resolve().relative_to(root)
        except ValueError:
            violations.append({
                "code": "SKILL_HANDLE_SOURCE_ESCAPES_REPO",
                "handle": handle.handle,
                "source_path": handle.source_path,
            })
        if source.name != "SKILL.md":
            violations.append({
                "code": "SKILL_HANDLE_SOURCE_NOT_SKILL_MD",
                "handle": handle.handle,
                "source_path": handle.source_path,
            })
    for key, rows in sorted(by_key.items()):
        if len(rows) > 1:
            violations.append({
                "code": "DUPLICATE_NORMALIZED_HANDLE",
                "normalized_handle": key,
                "handles": [row.to_dict() for row in rows],
            })
    return violations


def resolve_skill_handle(handle: str, *, repo_root_path: Path | None = None) -> dict[str, Any]:
    normalized = normalize_handle(handle)
    handles = build_skill_handles(repo_root_path=repo_root_path)
    matches = [item for item in handles if item.handle == normalized]
    if not matches:
        return {
            "status": "error",
            "error_code": "unknown_handle",
            "handle": normalized,
            "operator_action": "Run `./bin/ask skills handles --json` to list command-visible skill handles.",
        }
    if len(matches) > 1:
        return {
            "status": "error",
            "error_code": "ambiguous_handle",
            "handle": normalized,
            "matches": [item.to_dict() for item in matches],
            "operator_action": "Rename or remove duplicate command handles before projection.",
        }
    return {"status": "ok", **matches[0].to_dict()}


def _reviewer_alias_key(handle: str) -> str:
    return normalize_handle(handle).replace("-", "")


def resolve_reviewer_handle(handle: str, *, manifest_path: Path = REVIEWER_MANIFEST) -> dict[str, Any]:
    normalized = normalize_handle(handle)
    handles, manifest_error = build_reviewer_handles(manifest_path)
    exact = [item for item in handles if item.handle == normalized]
    matches = exact or [item for item in handles if _reviewer_alias_key(item.handle) == _reviewer_alias_key(normalized)]
    if not matches:
        return {
            "status": "error",
            "error_code": "unknown_reviewer",
            "handle": normalized,
            "manifest_error": manifest_error,
            "operator_action": "Check `~/.codex/agents/manifest.json` for an available reviewer/subagent role.",
        }
    if len(matches) > 1:
        return {
            "status": "error",
            "error_code": "ambiguous_reviewer",
            "handle": normalized,
            "matches": [item.to_dict() for item in matches],
            "operator_action": "Use the exact reviewer role name from `~/.codex/agents/manifest.json`.",
        }
    return {"status": "ok", **matches[0].to_dict(), "canonical_handle": matches[0].handle}


def handles_report(*, repo_root_path: Path | None = None, include_handles: bool = True) -> dict[str, Any]:
    handles = build_skill_handles(repo_root_path=repo_root_path)
    violations = validate_skill_handles(handles, repo_root_path=repo_root_path)
    return {
        "schema_version": "command-surface.v1",
        "status": "pass" if not violations else "fail",
        "policy_identity": policy_identity(),
        "handle_count": len(handles),
        "violations": violations,
        "handles": [handle.to_dict() for handle in handles] if include_handles else [],
        "notes": [
            "Skill handles are resolved from rooted manifest metadata.",
            "Reviewer handles are intentionally kept outside the skill command surface.",
            "This slice does not generate runtime command stubs.",
        ],
    }
