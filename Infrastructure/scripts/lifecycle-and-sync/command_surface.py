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
from selection_policy import ROOT_SKILL_SET_NAMES, policy_identity
from skillset_model import repo_root

HANDLE_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SKILL_MENTION_RE = re.compile(r"(?<![\w./-])\$([a-z][a-z0-9-]*)")
REVIEWER_MENTION_RE = re.compile(r"(?<![\w./-])@([A-Za-z0-9][A-Za-z0-9_-]*)")
COMMAND_VISIBILITY = {"orchestrator", "direct", "target", "reviewer", "none"}
COMMAND_SURFACE_PATH = Path(".skillsets") / "command-surface.json"
MAX_COMMAND_HANDLE_DESCRIPTION_WORDS = 14
MAX_COMMAND_HANDLE_BODY_WORDS = 120
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
    "he-ideate": "he-brainstorm",
    "he-refine": "he-improve",
    "he-technical-review": "he-code-review",
    "he-reliability-review": "he-code-review",
}


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
    command_handle_path = f".agents/skills/{handle}/SKILL.md" if handle and command_visibility != "none" else None
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


def _display_name(handle: CommandHandle) -> str:
    raw = handle.handle.replace("-", " ").strip()
    if not raw:
        return "Command Handle"
    return " ".join(part.upper() if part in {"he", "ci", "ui", "api"} else part.capitalize() for part in raw.split())


def _word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9$@./_-]+", text))


def requires_generated_command_handle(handle: CommandHandle) -> bool:
    """Return whether a handle needs a generated runtime command handle beyond rooted projection."""
    if handle.kind != "skill" or not handle.command_handle_path:
        return False
    if handle.handle in ROOT_SKILL_SET_NAMES:
        return False
    return handle.command_visibility in {"orchestrator", "direct", "target"}


def render_skill_command_handle(handle: CommandHandle) -> str:
    """Render a minimal Codex-visible SKILL.md command handle."""
    display_name = _display_name(handle)
    description = (
        f"Explicit command handle for {display_name}. "
        f"Use only when named as ${handle.handle}."
    )
    source_path = handle.source_path or "UNRESOLVED_SOURCE_PATH"
    return "\n".join(
        [
            "---",
            f"name: {handle.handle}",
            f'description: "{description}"',
            "---",
            "",
            f"# {display_name} Handle",
            "",
            f"Generated command handle for a child skill under the `{handle.owner}` router heading.",
            "The real workflow is not here.",
            f"Canonical source path: `{source_path}`.",
            "",
            "When invoked:",
            (
                "1. If this is the Agent Skills Kit repo and `./bin/ask` exists, "
                f"run `./bin/ask skills resolve {handle.handle} --json`."
            ),
            f"2. Otherwise, load `{source_path}` directly.",
            "3. Follow the loaded module contract.",
            (
                "4. If the source path is missing, search only the owner skill tree "
                "for this exact handle name."
            ),
            "",
            "When used as another skill's target, pass the resolved card to the active orchestrator and wait for orchestration.",
            "",
        ]
    )


def render_openai_yaml(handle: CommandHandle) -> str:
    """Render UI-facing metadata for a generated command handle."""
    display_name = _display_name(handle)
    short_description = f"${handle.handle} - {display_name} command handle"
    return "\n".join(
        [
            "interface:",
            f'  display_name: "{display_name}"',
            f'  short_description: "{short_description}"',
            f'  default_prompt: "${handle.handle} "',
            "",
            "policy:",
            "  allow_implicit_invocation: false",
            "",
        ]
    )


def _validate_command_handle_payload(handle: CommandHandle, skill_body: str) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    frontmatter_description = (
        f"Explicit command handle for {_display_name(handle)}. "
        f"Use only when named as ${handle.handle}."
    )
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


def _command_handle_write_rows(handles: list[CommandHandle]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for handle in handles:
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
                    "violations": [],
                    "content": yaml_body,
                },
            ]
        )
    return rows


def _is_generated_command_handle_dir(path: Path) -> bool:
    skill_file = path / "SKILL.md"
    if not skill_file.is_file():
        return False
    try:
        content = skill_file.read_text(encoding="utf-8")
    except OSError:
        return False
    return "Generated command handle for a child skill under the" in content


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
    handles = build_skill_handles(repo_root_path=repo_root_path)
    violations = validate_skill_handles(handles, repo_root_path=repo_root_path)
    command_handle_rows = _command_handle_write_rows(handles)
    command_handle_violations = [
        violation
        for row in command_handle_rows
        for violation in row.get("violations", [])
    ]
    violations.extend(command_handle_violations)
    command_handle_count = len({
        row["handle"] for row in command_handle_rows if row["kind"] == "skill_command_handle"
    })
    return {
        "schema_version": "command-surface.v1",
        "status": "pass" if not violations else "fail",
        "policy_identity": policy_identity(),
        "generated_from": "rooted_manifests",
        "projection_path": COMMAND_SURFACE_PATH.as_posix(),
        "handle_count": len(handles),
        "generated_command_handle_count": command_handle_count,
        "violations": violations,
        "handles": [handle.to_dict() for handle in handles] if include_handles else [],
        "notes": [
            "Skill handles are resolved from rooted manifest metadata.",
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


def write_command_handles(*, repo_root_path: Path | None = None, dry_run: bool = False) -> dict[str, Any]:
    """Write or preview generated runtime command handles for non-root handles."""
    root = repo_root_path or repo_root()
    handles = build_skill_handles(repo_root_path=root)
    rows = _command_handle_write_rows(handles)
    violations = validate_skill_handles(handles, repo_root_path=root)
    violations.extend([
        violation
        for row in rows
        for violation in row.get("violations", [])
    ])
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
        "deletes": deletes,
        "violations": violations,
    }


def check_command_handles(*, repo_root_path: Path | None = None) -> dict[str, Any]:
    """Verify generated runtime command handles exist and match the rooted projection."""
    root = repo_root_path or repo_root()
    rows = _command_handle_write_rows(build_skill_handles(repo_root_path=root))
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
        "violations": violations,
    }
