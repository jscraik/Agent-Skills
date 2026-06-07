#!/usr/bin/env python3
"""Resolve command-visible skill and reviewer handles for rooted skill trees."""

from __future__ import annotations

import json
import os
import re
import shutil
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from generate_skillset_manifests import build_manifest_report
from selection_policy import ROOT_SKILL_SET_NAMES, SYSTEM_BRIDGE_SKILL_NAMES, policy_identity
from skill_discovery import iter_plugin_skill_dirs, normalize_skill_description, parse_skill_frontmatter
from skillset_model import repo_root

HANDLE_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SKILL_MENTION_RE = re.compile(r"(?<![\w./-])\$([a-z][a-z0-9-]*)")
REVIEWER_MENTION_RE = re.compile(r"(?<![\w./-])@([A-Za-z0-9][A-Za-z0-9_-]*)")
COMMAND_VISIBILITY = {"orchestrator", "direct", "target", "reviewer", "none"}
COMMAND_SURFACE_PATH = Path(".skillsets") / "command-surface.json"
MAX_COMMAND_HANDLE_DESCRIPTION_WORDS = 14
MAX_COMMAND_HANDLE_BODY_WORDS = 120
MAX_OPENAI_SHORT_DESCRIPTION_CHARS = 120
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
FOLDED_SKILL_HANDLE_ALIASES = {
    "he-refactor": "he-reframe",
    "he-phase-heartbeat": "he-phase-work",
    "he-ideate": "he-brainstorm",
    "he-refine": "he-improve",
    "he-technical-review": "he-code-review",
    "he-reliability-review": "he-code-review",
}
HIDDEN_COMPATIBILITY_COMMAND_HANDLES = {
    "he-goal-governor-archive",
    "he-phase-heartbeat",
}
ALIAS_KIND_FOLDED_COMPATIBILITY = "folded_compatibility"
DEPRECATION_STATE_DEPRECATED = "deprecated"


@dataclass(frozen=True)
class CommandHandle:
    handle: str
    kind: str
    command_visibility: str
    runtime_visibility: str | None
    source_path: str | None
    command_handle_path: str | None
    owner: str
    description: str
    invoke_via: str | None = None
    level: str | None = None
    alias_of: str | None = None
    alias_kind: str | None = None
    deprecation_state: str | None = None
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
        if value in COMMAND_VISIBILITY:
            return value
        # Preserve invalid values so validation can surface INVALID_SKILL_COMMAND_VISIBILITY
        # instead of silently coercing to "none" and dropping the handle.
        return value

    module_id = str(row.get("id", ""))
    level = str(row.get("level", ""))
    if str(row.get("runtime_visibility", "latent")) == "hidden":
        return "none"
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
    command_handle_path = (
        f".agents/skills/{handle}/SKILL.md"
        if handle and command_visibility != "none" and handle not in SYSTEM_BRIDGE_SKILL_NAMES
        else None
    )
    return CommandHandle(
        handle=handle,
        kind="skill",
        command_visibility=command_visibility,
        runtime_visibility=str(row.get("runtime_visibility") or "latent"),
        source_path=source_path,
        command_handle_path=command_handle_path,
        owner=str(row.get("skill_set") or ""),
        description=str(row.get("description") or ""),
        invoke_via=_invoke_via_for(row, command_visibility),
        level=str(row.get("level") or ""),
        provenance=row.get("provenance") if isinstance(row.get("provenance"), dict) else None,
    )


def _alias_handle_from_target(alias: str, target: CommandHandle) -> CommandHandle:
    """Build a generated compatibility handle that resolves to a canonical target."""
    return CommandHandle(
        handle=alias,
        kind=target.kind,
        command_visibility=target.command_visibility,
        runtime_visibility=target.runtime_visibility,
        source_path=target.source_path,
        command_handle_path=f".agents/skills/{alias}/SKILL.md",
        owner=target.owner,
        description=target.description,
        invoke_via=target.invoke_via,
        level=target.level,
        alias_of=target.handle,
        alias_kind=ALIAS_KIND_FOLDED_COMPATIBILITY,
        deprecation_state=DEPRECATION_STATE_DEPRECATED,
        provenance=target.provenance,
    )


def _with_folded_alias_handles(handles: list[CommandHandle]) -> list[CommandHandle]:
    """Add generated command handles for folded aliases whose targets exist."""
    by_handle = {handle.handle: handle for handle in handles}
    extended = list(handles)
    for alias, target_handle in sorted(FOLDED_SKILL_HANDLE_ALIASES.items()):
        if alias in HIDDEN_COMPATIBILITY_COMMAND_HANDLES:
            continue
        if alias in by_handle:
            continue
        target = by_handle.get(target_handle)
        if not target:
            continue
        extended.append(_alias_handle_from_target(alias, target))
    return extended


def _display_name(handle: CommandHandle) -> str:
    raw = handle.handle.replace("-", " ").strip()
    if not raw:
        return "Command Handle"
    return " ".join(part.upper() if part in {"he", "ci", "ui", "api"} else part.capitalize() for part in raw.split())


def _openai_short_description(handle: CommandHandle) -> str:
    """Return useful picker text without repeating the display name or handle."""
    description = " ".join((handle.description or "").split())
    if not description:
        return "Load the routed skill workflow."
    if len(description) <= MAX_OPENAI_SHORT_DESCRIPTION_CHARS:
        return description
    return f"{description[: MAX_OPENAI_SHORT_DESCRIPTION_CHARS - 3].rstrip()}..."


def _word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9$@./_-]+", text))


def requires_generated_command_handle(handle: CommandHandle) -> bool:
    """Return whether a handle needs a generated runtime command handle beyond rooted projection."""
    if handle.kind != "skill" or not handle.command_handle_path:
        return False
    if handle.handle in ROOT_SKILL_SET_NAMES:
        return False
    if handle.handle in SYSTEM_BRIDGE_SKILL_NAMES:
        return False
    return handle.command_visibility in {"orchestrator", "direct", "target"}


def render_skill_command_handle(handle: CommandHandle) -> str:
    """Render a minimal Codex-visible SKILL.md command handle."""
    display_name = _display_name(handle)
    description = f"Internal entrypoint. Use only when named as ${handle.handle}."
    source_path = handle.source_path or "UNRESOLVED_SOURCE_PATH"
    absolute_source_path = (
        (repo_root() / source_path).as_posix()
        if handle.source_path and not Path(source_path).is_absolute()
        else source_path
    )
    absolute_resolve_cmd = (repo_root() / "bin" / "ask").as_posix()
    return "\n".join(
        [
            "---",
            f"name: {handle.handle}",
            f'description: "{description}"',
            "---",
            "",
            f"# {display_name} Handle",
            "",
            f"Internal activation entrypoint for a child skill under `{handle.owner}`.",
            f"Source: `{source_path}`.",
            "",
            "Invoke:",
            (
                f"1. Load `{source_path}` if present; otherwise load `{absolute_source_path}`."
            ),
            (
                "2. Keep handle/routing/source mechanics out of user replies."
            ),
            (
                "3. If the source path is missing or unreadable, then run "
                f"`{absolute_resolve_cmd} skills resolve {handle.handle} --json` as a diagnostic fallback."
            ),
            "4. Follow the loaded module contract.",
            "5. Preserve source checklists/preludes verbatim in final answers.",
            "6. If missing, search only the owner skill tree for this exact handle.",
            "7. If blocked or ambiguous, fail closed and report only the blocker or choice needed.",
            "",
            "As another skill's target, pass the resolved contract to the active orchestrator and wait.",
            "",
        ]
    )


def render_openai_yaml(handle: CommandHandle) -> str:
    """Render UI-facing metadata for a generated command handle."""
    display_name = _display_name(handle)
    short_description = _openai_short_description(handle)
    return "\n".join(
        [
            "interface:",
            f"  display_name: {json.dumps(display_name)}",
            f"  short_description: {json.dumps(short_description)}",
            f"  default_prompt: {json.dumps(f'${handle.handle} ')}",
            "",
            "policy:",
            "  allow_implicit_invocation: false",
            "",
        ]
    )


def _validate_command_handle_payload(handle: CommandHandle, skill_body: str) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    frontmatter_description = f"Internal entrypoint. Use only when named as ${handle.handle}."
    if _word_count(frontmatter_description) > MAX_COMMAND_HANDLE_DESCRIPTION_WORDS:
        violations.append({
            "code": "COMMAND_HANDLE_DESCRIPTION_BUDGET_EXCEEDED",
            "handle": handle.handle,
            "words": _word_count(frontmatter_description),
            "max_words": MAX_COMMAND_HANDLE_DESCRIPTION_WORDS,
        })
    body = re.sub(r"(?s)^---.*?---", "", skill_body).strip()
    if _word_count(body) > MAX_COMMAND_HANDLE_BODY_WORDS:
        violations.append({
            "code": "COMMAND_HANDLE_BODY_BUDGET_EXCEEDED",
            "handle": handle.handle,
            "words": _word_count(body),
            "max_words": MAX_COMMAND_HANDLE_BODY_WORDS,
        })
    forbidden = ["## Procedure", "## Full Context", "## Examples", "Progressive Disclosure Entry"]
    matches = [marker for marker in forbidden if marker in body]
    if matches:
        violations.append({
            "code": "COMMAND_HANDLE_CONTAINS_FULL_WORKFLOW_MARKERS",
            "handle": handle.handle,
            "markers": matches,
        })
    return violations


def _validate_openai_metadata_payload(handle: CommandHandle, yaml_body: str) -> list[dict[str, Any]]:
    """Reject picker metadata that only describes projection plumbing."""
    violations: list[dict[str, Any]] = []
    useless_description = '  short_description: "$' + handle.handle + f' - {_display_name(handle)} entrypoint"'
    if useless_description in yaml_body:
        violations.append({
            "code": "COMMAND_HANDLE_USELESS_PICKER_DESCRIPTION",
            "handle": handle.handle,
        })
    return violations


def _command_handle_write_rows(handles: list[CommandHandle]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for handle in _with_folded_alias_handles(handles):
        if not requires_generated_command_handle(handle):
            continue
        skill_body = render_skill_command_handle(handle)
        yaml_body = render_openai_yaml(handle)
        base = Path(handle.command_handle_path or "").parent
        rows.extend(
            [
                {
                    "handle": handle.handle,
                    "kind": "skill_command_handle",
                    "path": (base / "SKILL.md").as_posix(),
                    "bytes": len(skill_body.encode("utf-8")),
                    "violations": _validate_command_handle_payload(handle, skill_body),
                    "content": skill_body,
                },
                {
                    "handle": handle.handle,
                    "kind": "openai_metadata",
                    "path": (base / "agents" / "openai.yaml").as_posix(),
                    "bytes": len(yaml_body.encode("utf-8")),
                    "violations": _validate_openai_metadata_payload(handle, yaml_body),
                    "content": yaml_body,
                },
            ]
        )
    return rows


def generated_command_handle_names(*, repo_root_path: Path | None = None) -> set[str]:
    """Return all first-level generated command handle names, including aliases."""
    rows = _command_handle_write_rows(build_command_surface_handles(repo_root_path=repo_root_path))
    return {
        row["handle"]
        for row in rows
        if row["kind"] == "skill_command_handle"
    }


def _is_generated_command_handle_dir(path: Path) -> bool:
    skill_file = path / "SKILL.md"
    if not skill_file.is_file():
        return False
    try:
        content = skill_file.read_text(encoding="utf-8")
    except OSError:
        return False
    generated_markers = (
        "Generated command handle for a child skill under the",
        "Internal activation entrypoint for a child skill under",
    )
    return any(marker in content for marker in generated_markers)


def _prune_obsolete_command_handle_dirs(
    *,
    root: Path,
    expected_dirs: set[Path],
    dry_run: bool,
) -> list[dict[str, str]]:
    skills_dir = root / ".agents" / "skills"
    if not skills_dir.is_dir():
        return []

    deletes: list[dict[str, str]] = []
    for path in sorted(skills_dir.iterdir(), key=lambda item: item.name):
        if path in expected_dirs:
            continue
        if not path.is_dir() or path.is_symlink():
            continue
        if not _is_generated_command_handle_dir(path):
            continue
        row = {
            "path": path.relative_to(root).as_posix(),
            "reason": "obsolete_generated_command_handle",
        }
        deletes.append(row)
        if not dry_run:
            shutil.rmtree(path)
    return deletes


def _runtime_handle_symlink_target(
    *,
    root: Path,
    handle: CommandHandle,
    path: Path,
) -> Path | None:
    """Return the expected rooted runtime target when a handle is already projected."""
    if not handle.source_path:
        return None
    handle_dir = root / ".agents" / "skills" / handle.handle
    if not handle_dir.is_symlink():
        return None
    try:
        target = handle_dir.resolve()
        source_file = root / handle.source_path
        source_parent = source_file.resolve().parent
        source_parent.relative_to(root.resolve())
        path.resolve().relative_to(source_parent)
    except (OSError, ValueError):
        return None
    if target != source_parent:
        return None
    if not source_file.is_file() or not path.is_file():
        return None
    return target


def _rows_needing_generated_command_handles(
    *,
    root: Path,
    handles: list[CommandHandle],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split generated handle rows from handles already covered by rooted projection."""
    by_handle = {handle.handle: handle for handle in _with_folded_alias_handles(handles)}
    rows: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for row in _command_handle_write_rows(handles):
        handle = by_handle.get(str(row["handle"]))
        path = root / row["path"]
        if handle and _runtime_handle_symlink_target(root=root, handle=handle, path=path):
            skipped.append({
                "handle": row["handle"],
                "kind": row["kind"],
                "path": row["path"],
                "reason": "rooted_runtime_symlink",
            })
            continue
        rows.append(row)
    return rows, skipped


def _write_generated_text(path: Path, content: str) -> None:
    """Write generated content via same-directory replace to tolerate protected files."""
    if path.is_file():
        try:
            if path.read_text(encoding="utf-8") == content:
                return
        except OSError:
            pass
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def build_skill_handles(*, repo_root_path: Path | None = None, include_hidden: bool = False) -> list[CommandHandle]:
    """Build command-visible skill handles from rooted manifests and plugin metadata."""
    root = repo_root_path or repo_root()
    report = build_manifest_report(root / ".skillsets", repo_root_path=root)
    handles: list[CommandHandle] = []
    for manifest in report.get("manifests", []):
        for row in manifest.get("rows", []):
            handle = _handle_from_manifest_row(row)
            if include_hidden or handle.command_visibility != "none":
                handles.append(handle)
    for row in _plugin_command_surface_rows(root):
        handle = _handle_from_manifest_row(row)
        if include_hidden or handle.command_visibility != "none":
            handles.append(handle)
    handles = _drop_shadowed_system_bridge_handles(handles)
    return sorted(handles, key=lambda item: (item.handle, item.owner, item.source_path or ""))


def _plugin_command_surface_rows(root: Path) -> list[dict[str, Any]]:
    """Return plugin-owned command handles without promoting plugins to root skill sets."""
    rows: list[dict[str, Any]] = []
    for skill_dir in iter_plugin_skill_dirs():
        try:
            rel_dir = skill_dir.relative_to(root)
        except ValueError:
            continue
        parts = rel_dir.parts
        if len(parts) < 4 or parts[0] not in {"Plugins", "plugins"} or "skills" not in parts:
            continue
        skills_index = parts.index("skills")
        if skills_index < 1:
            continue
        plugin_name = parts[skills_index - 1]
        if plugin_name in ROOT_SKILL_SET_NAMES:
            continue
        skill_md = skill_dir / "SKILL.md"
        frontmatter = parse_skill_frontmatter(skill_md)
        command_visibility = (
            frontmatter.get("metadata.command_visibility")
            or frontmatter.get("metadata.command-visibility")
            or frontmatter.get("command_visibility")
            or frontmatter.get("command-visibility")
        )
        if not command_visibility:
            continue
        runtime_visibility = (
            frontmatter.get("metadata.runtime_visibility")
            or frontmatter.get("metadata.runtime-visibility")
            or frontmatter.get("runtime_visibility")
            or frontmatter.get("runtime-visibility")
            or "latent"
        )
        rows.append({
            "id": frontmatter.get("name") or skill_dir.name,
            "skill_set": plugin_name,
            "level": frontmatter.get("metadata.level") or frontmatter.get("level") or "",
            "source_path": (rel_dir / "SKILL.md").as_posix(),
            "runtime_visibility": runtime_visibility,
            "command_visibility": command_visibility,
            "description": normalize_skill_description(frontmatter.get("description", "")),
            "provenance": {
                "generator": "plugin-command-surface.v1",
                "projection_mode": "plugin-command-handles",
                "policy_identity": policy_identity(),
            },
        })
    return rows


def _drop_shadowed_system_bridge_handles(handles: list[CommandHandle]) -> list[CommandHandle]:
    """Prefer canonical plugin handles over compatibility system bridge handles."""
    canonical_handles = {
        handle.handle
        for handle in handles
        if handle.handle in SYSTEM_BRIDGE_SKILL_NAMES
        and not (handle.source_path or "").startswith("skills-system/")
    }
    return [
        handle
        for handle in handles
        if not (
            handle.handle in canonical_handles
            and (handle.source_path or "").startswith("skills-system/")
        )
    ]


def build_command_surface_handles(*, repo_root_path: Path | None = None) -> list[CommandHandle]:
    """Build Codex-visible skill command handles, including folded compatibility aliases."""
    handles = build_skill_handles(repo_root_path=repo_root_path)
    surfaced_handles = _with_folded_alias_handles(handles)
    return sorted(surfaced_handles, key=lambda item: (item.handle, item.owner, item.source_path or ""))


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
            command_handle_path=None,
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
        source_candidates = [root / handle.source_path]
        canonical_root = repo_root().resolve()
        if canonical_root != root:
            source_candidates.append(canonical_root / handle.source_path)
        if not any(source.exists() for source in source_candidates):
            violations.append({
                "code": "SKILL_HANDLE_SOURCE_MISSING",
                "handle": handle.handle,
                "source_path": handle.source_path,
            })
            continue
        source = next(candidate for candidate in source_candidates if candidate.exists())
        if source_candidates[0].exists():
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
    requested = normalize_handle(handle)
    normalized = FOLDED_SKILL_HANDLE_ALIASES.get(requested, requested)
    handles = build_skill_handles(repo_root_path=repo_root_path)
    matches = [item for item in handles if item.handle == normalized]
    if not matches:
        return {
            "status": "error",
            "error_code": "unknown_handle",
            "handle": requested,
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
    payload = {"status": "ok", **matches[0].to_dict()}
    if requested != normalized:
        payload["requested_handle"] = requested
        payload["alias_resolution"] = normalized
    return payload


def _reviewer_alias_key(handle: str) -> str:
    return normalize_handle(handle).replace("-", "").replace("_", "")


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


def _mention_rows(pattern: re.Pattern[str], prefix: str, text: str) -> list[dict[str, Any]]:
    """Return ordered command-handle mention rows without echoing full prompt text."""
    rows: list[dict[str, Any]] = []
    for match in pattern.finditer(text):
        raw_handle = match.group(1)
        rows.append({
            "mention": raw_handle,
            "token": f"{prefix}{raw_handle}",
            "handle": normalize_handle(raw_handle),
            "start": match.start(),
            "end": match.end(),
        })
    return rows


def _skill_role(resolution: dict[str, Any], *, active_orchestrator_seen: bool) -> str:
    command_visibility = str(resolution.get("command_visibility") or "")
    if command_visibility == "orchestrator" and not active_orchestrator_seen:
        return "active_orchestrator"
    if command_visibility == "orchestrator":
        return "orchestrator_dependency"
    if command_visibility == "target":
        return "target"
    if command_visibility == "direct":
        return "direct_skill"
    return command_visibility or "skill"


def parse_command_handles(text: str, *, repo_root_path: Path | None = None) -> dict[str, Any]:
    """Parse $ skill handles and @ reviewer handles from a prompt and resolve each one."""
    root = repo_root_path or repo_root()
    skill_mentions = _mention_rows(SKILL_MENTION_RE, "$", text)
    reviewer_mentions = _mention_rows(REVIEWER_MENTION_RE, "@", text)
    unresolved: list[dict[str, Any]] = []
    active_orchestrator_seen = False

    for mention in skill_mentions:
        resolution = resolve_skill_handle(str(mention["handle"]), repo_root_path=root)
        role = _skill_role(resolution, active_orchestrator_seen=active_orchestrator_seen)
        if role == "active_orchestrator":
            active_orchestrator_seen = True
        mention["role"] = role
        mention["resolution"] = resolution
        if resolution.get("status") != "ok":
            unresolved.append({
                "namespace": "skills",
                "token": mention["token"],
                "handle": mention["handle"],
                "error_code": resolution.get("error_code"),
                "operator_action": resolution.get("operator_action"),
            })

    for mention in reviewer_mentions:
        resolution = resolve_reviewer_handle(str(mention["handle"]))
        mention["role"] = "reviewer"
        mention["resolution"] = resolution
        if resolution.get("status") != "ok":
            unresolved.append({
                "namespace": "reviewers",
                "token": mention["token"],
                "handle": mention["handle"],
                "error_code": resolution.get("error_code"),
                "operator_action": resolution.get("operator_action"),
            })

    return {
        "schema_version": "command-handle-parse.v1",
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
    handles = build_skill_handles(repo_root_path=repo_root_path, include_hidden=True)
    hidden_handles = [handle for handle in handles if handle.command_visibility == "none"]
    visible_handles = [handle for handle in handles if handle.command_visibility != "none"]
    surfaced_handles = _with_folded_alias_handles(visible_handles)
    violations = validate_skill_handles(surfaced_handles, repo_root_path=repo_root_path)
    command_handle_rows = _command_handle_write_rows(visible_handles)
    command_handle_violations = [
        violation
        for row in command_handle_rows
        for violation in row.get("violations", [])
    ]
    violations.extend(command_handle_violations)
    command_handle_count = len({
        row["handle"] for row in command_handle_rows if row["kind"] == "skill_command_handle"
    })
    public_rows = [handle.to_dict() for handle in surfaced_handles] if include_handles else []
    hidden_rows = [handle.to_dict() for handle in hidden_handles] if include_handles else []
    return {
        "schema_version": "command-surface.v1",
        "status": "pass" if not violations else "fail",
        "policy_identity": policy_identity(),
        "generated_from": "rooted_manifests",
        "projection_path": COMMAND_SURFACE_PATH.as_posix(),
        "handle_count": len(surfaced_handles),
        "generated_command_handle_count": command_handle_count,
        "violations": violations,
        "handles": public_rows,
        "hidden_handles": hidden_rows,
        "notes": [
            "Skill handles are resolved from rooted manifest metadata and explicit plugin command metadata.",
            "The command-surface manifest is a generated projection, not a source of truth.",
            "Generated command handles are runtime pointers for $ invocation; they are not canonical skill sources.",
            "Generated command handles are written only for handles absent from rooted runtime projection.",
            "Reviewer handles are intentionally kept outside the skill command surface.",
        ],
    }


def command_surface_projection(*, repo_root_path: Path | None = None, include_handles: bool = True) -> dict[str, Any]:
    """Return the generated command-surface projection payload."""
    return handles_report(repo_root_path=repo_root_path, include_handles=include_handles)


def write_command_surface_projection(*, repo_root_path: Path | None = None, dry_run: bool = False) -> dict[str, Any]:
    """Write or preview the generated command-surface manifest."""
    root = repo_root_path or repo_root()
    payload = command_surface_projection(repo_root_path=root, include_handles=True)
    destination = root / COMMAND_SURFACE_PATH
    serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(serialized, encoding="utf-8")
    return {
        "schema_version": "command-surface-write.v1",
        "status": payload["status"],
        "dry_run": dry_run,
        "path": COMMAND_SURFACE_PATH.as_posix(),
        "bytes": len(serialized.encode("utf-8")),
        "handle_count": payload["handle_count"],
        "generated_command_handle_count": payload["generated_command_handle_count"],
        "violations": payload["violations"],
    }


def check_command_surface_projection(*, repo_root_path: Path | None = None) -> dict[str, Any]:
    """Verify the committed command-surface projection matches rooted manifests."""
    root = repo_root_path or repo_root()
    payload = command_surface_projection(repo_root_path=root, include_handles=True)
    destination = root / COMMAND_SURFACE_PATH
    violations = list(payload.get("violations", []))

    actual_payload: dict[str, Any] | None = None
    if not destination.exists():
        violations.append({
            "code": "COMMAND_SURFACE_PROJECTION_MISSING",
            "path": COMMAND_SURFACE_PATH.as_posix(),
        })
    else:
        try:
            actual_payload = json.loads(destination.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            violations.append({
                "code": "COMMAND_SURFACE_PROJECTION_INVALID_JSON",
                "path": COMMAND_SURFACE_PATH.as_posix(),
                "error": str(exc),
            })
        except OSError as exc:
            violations.append({
                "code": "COMMAND_SURFACE_PROJECTION_UNREADABLE",
                "path": COMMAND_SURFACE_PATH.as_posix(),
                "error": str(exc),
            })

    def _without_volatile_source_revision(value: dict[str, Any]) -> dict[str, Any]:
        clone = json.loads(json.dumps(value))

        def _remove_source_revision_recursive(obj: Any) -> None:
            if isinstance(obj, dict):
                # Remove source_revision from provenance dicts
                if "provenance" in obj and isinstance(obj["provenance"], dict):
                    obj["provenance"].pop("source_revision", None)
                # Recurse into all dict values
                for val in obj.values():
                    _remove_source_revision_recursive(val)
            elif isinstance(obj, list):
                # Recurse into all list items
                for item in obj:
                    _remove_source_revision_recursive(item)

        _remove_source_revision_recursive(clone)
        return clone

    if (
        actual_payload is not None
        and _without_volatile_source_revision(actual_payload) != _without_volatile_source_revision(payload)
    ):
        violations.append({
            "code": "COMMAND_SURFACE_PROJECTION_DRIFT",
            "path": COMMAND_SURFACE_PATH.as_posix(),
            "expected_handle_count": payload.get("handle_count"),
            "actual_handle_count": actual_payload.get("handle_count"),
        })

    return {
        "schema_version": "command-surface-check.v1",
        "status": "pass" if not violations else "fail",
        "path": COMMAND_SURFACE_PATH.as_posix(),
        "handle_count": payload.get("handle_count"),
        "generated_command_handle_count": payload.get("generated_command_handle_count"),
        "violations": violations,
    }


def write_command_handles(*, repo_root_path: Path | None = None, dry_run: bool = False) -> dict[str, Any]:
    """Write or preview generated runtime command handles for non-root handles."""
    root = repo_root_path or repo_root()
    handles = build_skill_handles(repo_root_path=root)
    rows, skipped = _rows_needing_generated_command_handles(root=root, handles=handles)
    violations = validate_skill_handles(handles, repo_root_path=root)
    violations.extend([
        violation
        for row in rows
        for violation in row.get("violations", [])
    ])
    for row in rows:
        path = root / row["path"]
        if path.parent.is_symlink():
            violations.append({
                "code": "COMMAND_HANDLE_PARENT_SYMLINK",
                "path": row["path"],
                "parent": path.parent.relative_to(root).as_posix(),
            })
    expected_dirs = {
        root / ".agents" / "skills" / row["handle"]
        for row in rows
        if row["kind"] == "skill_command_handle"
    }
    deletes = _prune_obsolete_command_handle_dirs(
        root=root,
        expected_dirs=expected_dirs,
        dry_run=dry_run or bool(violations),
    )
    if not dry_run and not violations:
        for row in rows:
            path = root / row["path"]
            _write_generated_text(path, row["content"])
    return {
        "schema_version": "command-handle-write.v1",
        "status": "pass" if not violations else "fail",
        "dry_run": dry_run,
        "command_handle_count": len({row["handle"] for row in rows if row["kind"] == "skill_command_handle"}),
        "write_count": len(rows),
        "writes": [{key: value for key, value in row.items() if key != "content"} for row in rows],
        "skipped": skipped,
        "deletes": deletes,
        "violations": violations,
    }


def check_command_handles(*, repo_root_path: Path | None = None) -> dict[str, Any]:
    """Verify generated runtime command handles exist and match the rooted projection."""
    root = repo_root_path or repo_root()
    rows, skipped = _rows_needing_generated_command_handles(
        root=root,
        handles=build_skill_handles(repo_root_path=root),
    )
    violations: list[dict[str, Any]] = []
    expected_dirs = {
        root / ".agents" / "skills" / row["handle"]
        for row in rows
        if row["kind"] == "skill_command_handle"
    }
    for row in _prune_obsolete_command_handle_dirs(root=root, expected_dirs=expected_dirs, dry_run=True):
        violations.append({
            "code": "COMMAND_HANDLE_OBSOLETE",
            **row,
        })
    for row in rows:
        path = root / row["path"]
        if not path.exists():
            violations.append({
                "code": "COMMAND_HANDLE_MISSING",
                "handle": row["handle"],
                "path": row["path"],
            })
            continue
        expected = row["content"]
        try:
            actual = path.read_text(encoding="utf-8")
        except OSError as exc:
            violations.append({
                "code": "COMMAND_HANDLE_UNREADABLE",
                "handle": row["handle"],
                "path": row["path"],
                "error": str(exc),
            })
            continue
        if actual != expected:
            violations.append({
                "code": "COMMAND_HANDLE_DRIFT",
                "handle": row["handle"],
                "path": row["path"],
            })
    return {
        "schema_version": "command-handle-check.v1",
        "status": "pass" if not violations else "fail",
        "command_handle_count": len({row["handle"] for row in rows if row["kind"] == "skill_command_handle"}),
        "checked_count": len(rows),
        "skipped": skipped,
        "violations": violations,
    }
