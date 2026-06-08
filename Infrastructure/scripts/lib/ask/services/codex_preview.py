from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - exercised only in minimal runtimes
    yaml = None


CODEX_PREVIEW_SCHEMA_VERSION = "codex-skill-runtime-preview.v1"
CODEX_PREVIEW_MODELED_RULE_VERSION = "codex-core-skills.2026-05-23.source-model.v1"
CODEX_PREVIEW_SOURCE_FILES: tuple[str, ...] = (
    "codex-rs/core-skills/src/loader.rs",
    "codex-rs/core-skills/src/render.rs",
    "codex-rs/core-skills/src/config_rules.rs",
    "codex-rs/core-skills/src/injection.rs",
    "codex-rs/core-skills/src/invocation_utils.rs",
    "codex-rs/config/src/skills_config.rs",
    "codex-rs/core-skills/src/model.rs",
)
CODEX_PREVIEW_DEFAULT_CHAR_BUDGET = 8000
CODEX_PREVIEW_CONTEXT_WINDOW_PERCENT = 2
CODEX_PREVIEW_DESCRIPTION_TRUNCATION_WARNING_THRESHOLD_CHARS = 100
CODEX_PREVIEW_APPROX_BYTES_PER_TOKEN = 4
FIRST_PARTY_SKILL_SCAN_ROOT = "Skills"
FIRST_PARTY_SKILL_EXCLUDED_SEGMENTS = {
    "_archive",
    "agents",
    "assets",
    "examples",
    "fixtures",
    "references",
    "rules",
    "scripts",
    "templates",
}
FIRST_PARTY_SKILL_HIDDEN_NAMES = {
    "browser",
    "circleci",
    "linear",
    "skillgrade-graders",
    "skillgrade-setup",
}


def _ask_validation_command(*args: str) -> str:
    parts = ["./bin/ask"]
    parts.extend(args)
    parts.extend(["--json", "--robot"])
    return " ".join(shlex.quote(part) for part in parts)


def _skills_validation_command(action: str, *args: str) -> str:
    return _ask_validation_command("skills", action, *args)


def _parse_frontmatter_scalar(value: str) -> Any:
    cleaned = value.strip().strip("\"'")
    if cleaned.startswith("[") and cleaned.endswith("]"):
        return [
            item.strip().strip("\"'")
            for item in cleaned[1:-1].split(",")
            if item.strip()
        ]
    if cleaned.lower() in {"true", "false"}:
        return cleaned.lower() == "true"
    return cleaned


def _read_skill_frontmatter_fields(skill_md: Path) -> dict[str, Any]:
    """Extract conservative scalar and one-level metadata fields from SKILL.md frontmatter."""
    fields: dict[str, Any] = {}
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return fields
    current_map: str | None = None
    current_list_key: str | None = None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        stripped = line.strip()
        if not stripped:
            continue
        indent = len(line) - len(line.lstrip(" "))
        if stripped.startswith("- "):
            item = _parse_frontmatter_scalar(stripped[2:])
            if current_map == "metadata" and current_list_key:
                nested = fields.setdefault(current_map, {})
                if isinstance(nested, dict):
                    values = nested.setdefault(current_list_key, [])
                    if isinstance(values, list):
                        values.append(item)
                continue
            if current_map and current_map != "metadata":
                values = fields.setdefault(current_map, [])
                if isinstance(values, list):
                    values.append(item)
                continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if indent > 0 and current_map:
            nested = fields.setdefault(current_map, {})
            if isinstance(nested, dict):
                if value:
                    nested[key] = _parse_frontmatter_scalar(value)
                    current_list_key = None
                else:
                    nested[key] = []
                    current_list_key = key
            continue
        current_map = None
        current_list_key = None
        if not value:
            fields[key] = {}
            current_map = key
            continue
        fields[key] = _parse_frontmatter_scalar(value)
    return fields


def _read_agents_openai_yaml_fields(skill_md: Path | None) -> dict[str, Any]:
    """Extract a conservative agents/openai.yaml contract view."""
    if not skill_md:
        return {}
    agents_openai = skill_md.parent / "agents" / "openai.yaml"
    if not agents_openai.is_file():
        return {}
    try:
        text = agents_openai.read_text(encoding="utf-8")
    except OSError:
        return {}
    if yaml is not None:
        try:
            loaded = yaml.safe_load(text) or {}
        except yaml.YAMLError:
            loaded = {}
        if isinstance(loaded, dict):
            return {str(key): value for key, value in loaded.items()}
    fields: dict[str, Any] = {}
    current_map: str | None = None
    current_nested_key: str | None = None
    current_list_item: dict[str, Any] | None = None
    lines = text.splitlines()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if current_map and stripped.startswith("- "):
            nested = fields.setdefault(current_map, {})
            if not isinstance(nested, dict):
                continue
            item_text = stripped[2:].strip()
            if not current_nested_key:
                continue
            values = nested.setdefault(current_nested_key, [])
            if not isinstance(values, list):
                values = []
                nested[current_nested_key] = values
            if ":" in item_text:
                item_key, item_value = item_text.split(":", 1)
                current_list_item = {
                    item_key.strip(): _parse_frontmatter_scalar(item_value.strip())
                }
                values.append(current_list_item)
            else:
                values.append(_parse_frontmatter_scalar(item_text))
                current_list_item = None
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if indent == 0:
            if value:
                fields[key] = _parse_frontmatter_scalar(value)
                current_map = None
                current_nested_key = None
                current_list_item = None
            else:
                fields[key] = {}
                current_map = key
                current_nested_key = None
                current_list_item = None
            continue
        if current_map:
            nested = fields.setdefault(current_map, {})
            if not isinstance(nested, dict):
                continue
            if current_list_item is not None and indent >= 4 and value:
                current_list_item[key] = _parse_frontmatter_scalar(value)
                continue
            if value:
                nested[key] = _parse_frontmatter_scalar(value)
                current_nested_key = None
                current_list_item = None
            else:
                nested[key] = []
                current_nested_key = key
                current_list_item = None
    return fields


def _repo_relative_path(repo_root: Path, path: Path) -> str | None:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return None


def _codex_runtime_source_identity(repo_root: Path) -> dict[str, Any]:
    """
    Assembles identity metadata describing the local Codex core-skills source used for previews.
    
    Parameters:
        repo_root (Path): The repository root used to locate a sibling `../codex` directory.
    
    Returns:
        dict: A structured identity record containing at least the following keys:
            - `schema_version` (str): Fixed schema identifier.
            - `source_repo` (str): Modeled remote repository identifier.
            - `source_files` (list[str]): Files considered relevant for previews.
            - `modeled_rule_version` (str): Modeled rule version.
            - `status` (str): One of status indicators such as `"identified"`, `"blocked_missing_codex_repo"`, or `"blocked_git_error"`.
            - `revision` (str | None): Git revision SHA when identified, otherwise `None`.
            - `relevant_source_dirty` (bool | None): `True` if relevant files are dirty, `False` if clean, or `None` when unknown.
            - `unavailable_reason` (str | None): Human-readable reason when the source is unavailable or blocked.
            - Optional diagnostic keys when present (e.g., `dirty_files`, `stderr`).
    
    Raises:
        RuntimeError: If the `git` executable cannot be found on PATH.
    """
    git_path = shutil.which("git")
    if git_path is None:
        raise RuntimeError("git not found: blocked")
    codex_root = repo_root.parent / "codex"
    identity: dict[str, Any] = {
        "schema_version": "codex-runtime-source-identity.v1",
        "source_repo": "openai/codex",
        "source_files": list(CODEX_PREVIEW_SOURCE_FILES),
        "modeled_rule_version": CODEX_PREVIEW_MODELED_RULE_VERSION,
        "status": "blocked_missing_codex_repo",
        "revision": None,
        "relevant_source_dirty": None,
        "unavailable_reason": None,
    }
    if not codex_root.is_dir():
        identity["unavailable_reason"] = "Expected sibling Codex repository at ../codex was not found."
        return identity
    try:
        revision = subprocess.run(
            [git_path, "-C", str(codex_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        identity["status"] = "blocked_git_error"
        identity["unavailable_reason"] = f"Could not identify Codex source revision: {exc.__class__.__name__}"
        return identity
    if revision.returncode != 0:
        identity["status"] = "blocked_git_error"
        identity["unavailable_reason"] = "git rev-parse failed for the local Codex repository."
        identity["stderr"] = revision.stderr.strip()
        return identity
    identity["revision"] = revision.stdout.strip()
    try:
        status = subprocess.run(
            [git_path, "-C", str(codex_root), "status", "--short", "--", *CODEX_PREVIEW_SOURCE_FILES],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        dirty_lines = [line for line in status.stdout.splitlines() if line.strip()] if status.returncode == 0 else []
    except (OSError, subprocess.SubprocessError):
        dirty_lines = []
    identity["status"] = "identified"
    identity["relevant_source_dirty"] = bool(dirty_lines)
    if dirty_lines:
        identity["dirty_files"] = dirty_lines
    return identity


def _codex_preview_blocked_check(check_id: str, reason: str, source_files: list[str] | None = None) -> dict[str, Any]:
    """
    Create a blocked-check dict describing why a Codex preview is blocked.
    
    Parameters:
        check_id (str): Unique identifier for the blocked check.
        reason (str): Human-readable explanation for the block.
        source_files (list[str] | None): Optional list of repo-relative source file paths implicated in the block; defaults to an empty list.
    
    Returns:
        dict: A mapping with keys `id` (the check_id), `status` set to `"blocked"`, `reason`, and `source_files` (a list).
    """
    return {
        "id": check_id,
        "status": "blocked",
        "reason": reason,
        "source_files": source_files or [],
    }


def _codex_preview_source_basis(source_identity: dict[str, Any], blocked_checks: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Builds a stable metadata object describing the modeled source basis for a Codex preview.
    
    Constructs a dict containing repository and revision identity, whether relevant source files are dirty, the modeled rule version, the list of source files used for modeling, a modeled-basis marker, and the list of blocked-check ids.
    
    Parameters:
        source_identity (dict): Identity information returned by `_codex_runtime_source_identity`, expected to contain keys like
            `source_repo`, `revision`, `status`, `relevant_source_dirty`, `modeled_rule_version`, and `source_files`.
        blocked_checks (list[dict]): List of blocked-check objects; any `id` values present are included in the resulting `blocked_check_ids` list.
    
    Returns:
        dict: A metadata dictionary with keys:
            - `schema_version`: schema identifier string
            - `basis`: modeling basis identifier (`"source_modeled"`)
            - `source_repo`: repo path or identifier from `source_identity`
            - `source_revision`: revision string from `source_identity`
            - `source_identity_status`: status string from `source_identity`
            - `relevant_source_dirty`: boolean indicating whether relevant source files are dirty
            - `modeled_rule_version`: modeled rule version from `source_identity`
            - `source_files`: list of source file paths included in modeling
            - `live_runtime_parity`: parity claim marker (`"not_claimed"`)
            - `blocked_check_ids`: list of stringified blocked-check ids
    """
    return {
        "schema_version": "codex-preview-source-basis.v1",
        "basis": "source_modeled",
        "source_repo": source_identity.get("source_repo"),
        "source_revision": source_identity.get("revision"),
        "source_identity_status": source_identity.get("status"),
        "relevant_source_dirty": source_identity.get("relevant_source_dirty"),
        "modeled_rule_version": source_identity.get("modeled_rule_version"),
        "source_files": list(source_identity.get("source_files") or CODEX_PREVIEW_SOURCE_FILES),
        "live_runtime_parity": "not_claimed",
        "blocked_check_ids": [str(check.get("id")) for check in blocked_checks if check.get("id")],
    }


def _codex_preview_base(repo_root: Path, command: str) -> dict[str, Any]:
    """
    Builds the base metadata payload used by Codex preview builders.
    
    Parameters:
        repo_root (Path): Repository root used to identify the local codex source and resolve paths.
        command (str): The preview command being modeled (e.g., "skills load-preview").
    
    Returns:
        dict: A metadata dictionary containing keys:
            - `schema_version`: preview schema version identifier.
            - `command`: the provided command string.
            - `status`: `"partial"` if any source-based blocked checks exist, otherwise `"pass"`.
            - `source_identity`: detailed identity of the local codex repo and its availability status.
            - `source_basis`: derived source-basis metadata (modeled basis, revision, dirty flag, modeled rule version, and blocked check ids).
            - `modeled_rules`: stable descriptions of modeling semantics (loader, render, config, invocation).
            - `blocked_checks`: list of any source-related blocked check objects.
    """
    source_identity = _codex_runtime_source_identity(repo_root)
    blocked_checks: list[dict[str, Any]] = []
    if source_identity.get("status") != "identified":
        blocked_checks.append(
            _codex_preview_blocked_check(
                "codex_source_identity",
                str(source_identity.get("unavailable_reason") or "Codex source identity could not be identified."),
                list(CODEX_PREVIEW_SOURCE_FILES),
            )
        )
    return {
        "schema_version": CODEX_PREVIEW_SCHEMA_VERSION,
        "command": command,
        "status": "partial" if blocked_checks else "pass",
        "source_identity": source_identity,
        "source_basis": _codex_preview_source_basis(source_identity, blocked_checks),
        "modeled_rules": {
            "version": CODEX_PREVIEW_MODELED_RULE_VERSION,
            "loader": [
                "root discovery order follows Codex loader.rs: config-layer roots, plugin roots, then repo .agents/skills roots, with canonical-path dedupe retaining the first root",
                "skill discovery scans visible directories for SKILL.md, skips dot-prefixed entries, follows symlinked dirs for repo/user/admin scopes, and records parse/read errors",
            ],
            "render": [
                "default skill metadata budget is 8000 characters without context-window information",
                "context-window budget is 2 percent of context tokens when provided",
                "descriptions are shortened before minimum skill lines are omitted",
            ],
            "config": [
                "only user and session flag skills.config layers are modeled as runtime disable/enable rules",
                "path and name selectors are mutually exclusive; later rules override earlier rules with the same selector",
            ],
            "invocation": [
                "explicit text mentions use $name or linked [$name](skill://path-or-SKILL.md) syntax",
                "plain-name mentions are selected only when enabled and unambiguous",
                "implicit attribution detects runner-launched skill scripts and reader commands that read SKILL.md",
            ],
        },
        "blocked_checks": blocked_checks,
    }


def _preview_status_from_blockers(blocked_checks: list[dict[str, Any]]) -> str:
    """
    Determine the preview status based on whether any blocked checks are present.
    
    Parameters:
        blocked_checks (list[dict[str, Any]]): List of blocked-check records to evaluate.
    
    Returns:
        status (str): "partial" if `blocked_checks` contains one or more entries, "pass" otherwise.
    """
    return "partial" if blocked_checks else "pass"


def _refresh_preview_status_and_source_basis(payload: dict[str, Any]) -> None:
    """
    Update a preview payload in place so its source-basis and overall status reflect the current source identity and blocked checks.
    
    Parameters:
        payload (dict): Preview payload object that will be mutated. The function sets:
            - payload['source_basis'] to a summary derived from payload['source_identity'] and payload['blocked_checks'].
            - payload['status'] to the value computed from payload['blocked_checks'].
    
    Notes:
        This function mutates the given payload and does not return a value.
    """
    payload["source_basis"] = _codex_preview_source_basis(payload["source_identity"], payload["blocked_checks"])
    payload["status"] = _preview_status_from_blockers(payload["blocked_checks"])


def _skill_preview_default_name(skill_md: Path) -> str:
    """
    Determine a default preview name for a skill using its SKILL.md file path.
    
    Parameters:
        skill_md (Path): Path to a SKILL.md file within the skill directory.
    
    Returns:
        str: The name of the skill directory if present, otherwise the string "skill".
    """
    return skill_md.parent.name or "skill"


def _skill_preview_metadata(repo_root: Path, skill_md: Path, scope: str, root_path: Path, plugin_id: str | None = None) -> dict[str, Any]:
    """Return the subset of Codex SkillMetadata needed for preview commands."""
    try:
        frontmatter = _read_skill_frontmatter_fields(skill_md)
        parse_status = "pass"
        parse_error = None
    except Exception as exc:
        frontmatter = {}
        parse_status = "blocked_parse"
        parse_error = f"{exc.__class__.__name__}: {exc}"
    agents_openai = _read_agents_openai_yaml_fields(skill_md)
    metadata = frontmatter.get("metadata") if isinstance(frontmatter.get("metadata"), dict) else {}
    name = str(frontmatter.get("name") or _skill_preview_default_name(skill_md)).strip() or _skill_preview_default_name(skill_md)
    if plugin_id and ":" not in name:
        name = f"{plugin_id}:{name}"
    short_description = (
        frontmatter.get("short_description")
        or frontmatter.get("short-description")
        or metadata.get("short_description")
        or metadata.get("short-description")
    )
    rel_path = _repo_relative_path(repo_root, skill_md)
    root_rel = _repo_relative_path(repo_root, root_path)
    payload = {
        "name": name,
        "description": str(frontmatter.get("description") or "").replace("\n", " ").strip(),
        "short_description": str(short_description).strip() if short_description else None,
        "interface": agents_openai.get("interface") or frontmatter.get("interface"),
        "dependencies": agents_openai.get("dependencies") or frontmatter.get("dependencies"),
        "policy": agents_openai.get("policy") or frontmatter.get("policy"),
        "scope": scope,
        "plugin_id": plugin_id,
        "path": rel_path or skill_md.as_posix(),
        "root": root_rel or root_path.as_posix(),
        "enabled": True,
        "parse_status": parse_status,
    }
    if parse_error:
        payload["parse_error"] = parse_error
    return payload


def _is_hidden_skill_frontmatter(skill_md: Path) -> bool:
    try:
        frontmatter = _read_skill_frontmatter_fields(skill_md)
    except Exception:
        return False
    metadata = frontmatter.get("metadata") if isinstance(frontmatter.get("metadata"), dict) else {}
    hidden_markers = {
        str(frontmatter.get("runtime_visibility") or frontmatter.get("runtime-visibility") or ""),
        str(frontmatter.get("command_visibility") or frontmatter.get("command-visibility") or ""),
        str(frontmatter.get("lifecycle_state") or frontmatter.get("lifecycle-state") or ""),
        str(frontmatter.get("lifecycle") or ""),
        str(metadata.get("runtime_visibility") or metadata.get("runtime-visibility") or ""),
    }
    return bool(hidden_markers & {"hidden", "none", "archived", "deprecated"})


def _first_party_skill_inventory(repo_root: Path) -> list[dict[str, str]]:
    """Return picker-eligible first-party repo skills from canonical Skills/** source."""
    skills_root = repo_root / FIRST_PARTY_SKILL_SCAN_ROOT
    if not skills_root.is_dir():
        return []

    inventory: list[dict[str, str]] = []
    for skill_md in sorted(skills_root.rglob("SKILL.md")):
        try:
            rel_parts = skill_md.relative_to(skills_root).parts
        except ValueError:
            continue
        if any(part in FIRST_PARTY_SKILL_EXCLUDED_SEGMENTS for part in rel_parts):
            continue
        name = skill_md.parent.name
        if name in FIRST_PARTY_SKILL_HIDDEN_NAMES:
            continue
        if _is_hidden_skill_frontmatter(skill_md):
            continue
        try:
            source_path = skill_md.parent.relative_to(repo_root).as_posix()
        except ValueError:
            source_path = skill_md.parent.as_posix()
        inventory.append({"name": name, "source_path": source_path})
    return inventory


def _append_first_party_projection_blocker(
    payload: dict[str, Any],
    repo_root: Path,
    skills: list[dict[str, Any]],
) -> None:
    """
    Mark the preview partial when canonical first-party skills are not loadable.

    This protects the SDK projection contract: every visible first-party skill
    under Skills/** must be reachable through the modeled Codex loader roots
    after workspace and user sync. Plugin-scoped skills are handled separately
    by the runtime plugin root lane.
    """
    expected = _first_party_skill_inventory(repo_root)
    if not expected:
        return
    reachable_source_paths = {
        str(skill.get("path") or "").removesuffix("/SKILL.md")
        for skill in skills
    }
    missing = [
        item
        for item in expected
        if item["source_path"] not in reachable_source_paths
    ]
    payload["first_party_projection"] = {
        "schema_version": "first-party-skill-projection.v1",
        "expected_count": len(expected),
        "reachable_count": len(expected) - len(missing),
        "missing_count": len(missing),
        "missing_skills": missing,
        "status": "pass" if not missing else "blocked",
        "fix_suggestion": "./bin/ask skills sync --scope workspace --json --robot && ./bin/ask skills sync --scope user --json --robot",
    }
    if missing:
        payload["blocked_checks"].append(
            {
                "id": "first_party_runtime_projection",
                "status": "blocked",
                "reason": (
                    "Canonical first-party skills under Skills/** are not all reachable "
                    "through the modeled Codex loader roots; refresh workspace and user "
                    "runtime projections before claiming picker coverage."
                ),
                "source_files": [
                    "Infrastructure/scripts/lib/ask/services/codex_preview.py",
                    "Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh",
                ],
                "missing_count": len(missing),
                "missing_skills": missing,
            }
        )


def _dedupe_preview_roots(roots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for root in roots:
        path = Path(str(root["path"]))
        identity = path.resolve().as_posix() if path.exists() else path.as_posix()
        root["identity_path"] = identity
        if identity in seen:
            root["deduped"] = True
            continue
        seen.add(identity)
        root["deduped"] = False
        deduped.append(root)
    return deduped


def _codex_preview_root_candidates(repo_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return source-backed root candidates and structured unsupported dimensions."""
    home = Path.home()
    codex_home = Path(os.environ.get("CODEX_HOME") or (home / ".codex"))
    roots = [
        {
            "id": "project_codex_skills",
            "path": repo_root / ".codex" / "skills",
            "scope": "Repo",
            "source": "project_config_folder",
            "source_file": "codex-rs/core-skills/src/loader.rs",
        },
        {
            "id": "user_codex_skills",
            "path": codex_home / "skills",
            "scope": "User",
            "source": "deprecated_user_codex_home",
            "source_file": "codex-rs/core-skills/src/loader.rs",
        },
        {
            "id": "user_agents_skills",
            "path": home / ".agents" / "skills",
            "scope": "User",
            "source": "home_agents_skills",
            "source_file": "codex-rs/core-skills/src/loader.rs",
        },
        {
            "id": "system_cache_skills",
            "path": codex_home / "skills" / ".system",
            "scope": "System",
            "source": "codex_system_cache",
            "source_file": "codex-rs/core-skills/src/loader.rs",
        },
        {
            "id": "repo_agents_skills",
            "path": repo_root / ".agents" / "skills",
            "scope": "Repo",
            "source": "repo_agents_skill_roots",
            "source_file": "codex-rs/core-skills/src/loader.rs",
        },
    ]
    deduped = _dedupe_preview_roots(roots)
    for index, root in enumerate(deduped):
        path = Path(str(root["path"]))
        root["order"] = index
        root["exists"] = path.is_dir()
        root["path"] = path.as_posix()
    blocked_checks = [
        _codex_preview_blocked_check(
            "live_config_layer_stack",
            "Repo-side preview does not instantiate Codex ConfigLayerStack, so project/user/system/session layer availability is modeled from conventional local paths only.",
            ["codex-rs/core-skills/src/loader.rs", "codex-rs/config/src/skills_config.rs"],
        ),
        _codex_preview_blocked_check(
            "runtime_plugin_skill_roots",
            "PluginSkillRoot values are supplied by the Codex plugin runtime and are not discoverable from this repo without live runtime state.",
            ["codex-rs/core-skills/src/loader.rs"],
        ),
    ]
    return deduped, blocked_checks


def _scan_preview_skills(repo_root: Path, roots: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Scan preview roots using the Codex loader's broad traversal semantics."""
    skills: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    seen_skill_paths: set[str] = set()
    for root in roots:
        root_path = Path(str(root["path"]))
        if not root_path.is_dir():
            continue
        follow_symlinks = root.get("scope") in {"Repo", "User", "Admin"}
        visited_dirs: set[str] = set()
        queue: list[tuple[Path, int]] = [(root_path, 0)]
        while queue:
            current, depth = queue.pop(0)
            try:
                resolved_current = current.resolve() if current.exists() else current
            except OSError:
                resolved_current = current
            current_key = resolved_current.as_posix()
            if current_key in visited_dirs:
                continue
            visited_dirs.add(current_key)
            if depth > 8:
                continue
            try:
                entries = sorted(current.iterdir(), key=lambda item: item.name)
            except OSError as exc:
                errors.append({"path": current.as_posix(), "message": f"{exc.__class__.__name__}: {exc}"})
                continue
            for entry in entries:
                if entry.name.startswith("."):
                    continue
                try:
                    is_symlink = entry.is_symlink()
                    is_dir = entry.is_dir()
                    is_file = entry.is_file()
                except OSError as exc:
                    errors.append({"path": entry.as_posix(), "message": f"{exc.__class__.__name__}: {exc}"})
                    continue
                if is_symlink and not follow_symlinks:
                    continue
                if is_dir:
                    queue.append((entry.resolve() if is_symlink else entry, depth + 1))
                    continue
                if is_file and entry.name == "SKILL.md":
                    identity = entry.resolve().as_posix() if entry.exists() else entry.as_posix()
                    if identity in seen_skill_paths:
                        continue
                    seen_skill_paths.add(identity)
                    skills.append(
                        _skill_preview_metadata(
                            repo_root,
                            entry,
                            str(root.get("scope") or "Unknown"),
                            root_path,
                            plugin_id=root.get("plugin_id"),
                        )
                    )
    return skills, errors


def build_codex_load_preview(repo_root: Path) -> dict[str, Any]:
    """
    Builds a "skills load-preview" payload describing modeled skill roots and discovered SKILL.md files.
    
    Parameters:
        repo_root (Path): Path to the repository root used to discover and scan modeled skill roots.
    
    Returns:
        dict: A preview payload containing metadata and modeled results. Notable keys include:
            - "roots": List of modeled root candidates (with existence/identity info).
            - "root_summary": Counts and deduplication policy for roots.
            - "skills": List of discovered skill metadata entries.
            - "skill_count": Number of discovered skills.
            - "errors": List of scan errors encountered while traversing roots.
            - "disabled_paths": List of paths considered disabled (empty if none).
            - "blocked_checks": List of blocked-check objects that affected preview status.
            - "validation_commands": List of commands suitable for validation of the modeled load.
            - "agent_summary": Human-readable summary of modeled skills/roots.
            - "source_identity", "source_basis", "status": Source/revision identity and overall preview status derived from blocked checks.
    """
    base = _codex_preview_base(repo_root, "skills load-preview")
    roots, root_blockers = _codex_preview_root_candidates(repo_root)
    skills, errors = _scan_preview_skills(repo_root, roots)
    base["blocked_checks"].extend(root_blockers)
    if errors:
        base["blocked_checks"].append(
            _codex_preview_blocked_check(
                "preview_scan_errors",
                "One or more modeled Codex skill roots could not be scanned completely.",
                ["codex-rs/core-skills/src/loader.rs"],
            )
        )
    base.update(
        {
            "roots": roots,
            "root_summary": {
                "modeled_root_count": len(roots),
                "existing_root_count": sum(1 for root in roots if root.get("exists")),
                "dedupe_policy": "canonical-path-first-root-retained",
            },
            "skills": skills,
            "skill_count": len(skills),
            "errors": errors,
            "disabled_paths": [],
            "validation_commands": [_skills_validation_command("load-preview")],
            "agent_summary": f"Modeled {len(skills)} Codex-loadable skill(s) from {sum(1 for root in roots if root.get('exists'))} existing root(s).",
        }
    )
    _append_first_party_projection_blocker(base, repo_root, skills)
    _refresh_preview_status_and_source_basis(base)
    return base


def _preview_skill_line(skill: dict[str, Any]) -> dict[str, Any]:
    description = str(skill.get("description") or "")
    path = str(skill.get("path") or "")
    name = str(skill.get("name") or "")
    full = f"- {name}: {description} (file: {path})"
    minimum = f"- {name} (file: {path})"
    return {
        "name": name,
        "path": path,
        "full": full,
        "minimum": minimum,
        "description": description,
    }


def _preview_budget(context_window: int | None) -> dict[str, Any]:
    if context_window and context_window > 0:
        return {
            "kind": "tokens",
            "limit": max(1, context_window * CODEX_PREVIEW_CONTEXT_WINDOW_PERCENT // 100),
            "context_window": context_window,
            "context_window_percent": CODEX_PREVIEW_CONTEXT_WINDOW_PERCENT,
        }
    return {
        "kind": "characters",
        "limit": CODEX_PREVIEW_DEFAULT_CHAR_BUDGET,
        "context_window": None,
        "context_window_percent": None,
    }


def _preview_cost(text: str, budget: dict[str, Any]) -> int:
    if budget["kind"] == "tokens":
        return (len(text.encode("utf-8")) + CODEX_PREVIEW_APPROX_BYTES_PER_TOKEN - 1) // CODEX_PREVIEW_APPROX_BYTES_PER_TOKEN
    return len(text)


def _render_preview_lines(skills: list[dict[str, Any]], budget: dict[str, Any]) -> tuple[list[str], dict[str, Any], str | None]:
    """
    Render enabled skills into preview lines honoring the provided budget and report truncation and omission metrics.
    
    Parameters:
        skills (list[dict[str, Any]]): Sequence of skill metadata dicts (each should include at least `name`, `path`, `description`, and optional `enabled`) from which enabled skills will be rendered.
        budget (dict[str, Any]): Budget descriptor produced by `_preview_budget`, containing `kind` and numeric `limit` used to decide how much content can be included.
    
    Returns:
        tuple[list[str], dict[str, Any], str | None]: A 3-tuple containing:
            - rendered_lines (list[str]): The list of rendered skill lines chosen under the budget (each line is a display string).
            - report (dict[str, Any]): Metrics about the rendering with keys:
                - `total_count` (int): number of enabled skills considered.
                - `included_count` (int): number of skills included in `rendered_lines`.
                - `omitted_count` (int): number of enabled skills omitted because of budget limits.
                - `truncated_description_chars` (int): total number of description characters removed due to truncation.
                - `truncated_description_count` (int): number of descriptions that were truncated (or counted toward truncation metrics).
                - `render_strategy` (str): one of `"full"`, `"shortened_descriptions"`, or `"minimum_lines_until_budget"` indicating the applied strategy.
            - warning (str | None): Optional human-readable warning when truncation or omission is significant; `None` when no warning is applicable.
    """
    lines = [_preview_skill_line(skill) for skill in skills if skill.get("enabled", True)]
    limit = int(budget["limit"])
    full_cost = sum(_preview_cost(line["full"], budget) for line in lines)
    if full_cost <= limit:
        report = {
            "total_count": len(lines),
            "included_count": len(lines),
            "omitted_count": 0,
            "truncated_description_chars": 0,
            "truncated_description_count": 0,
            "render_strategy": "full",
        }
        return [line["full"] for line in lines], report, None

    minimum_cost = sum(_preview_cost(line["minimum"], budget) for line in lines)
    if minimum_cost <= limit:
        per_line_allowance = max(0, (limit - minimum_cost) // max(1, len(lines)))
        rendered: list[str] = []
        truncated_chars = 0
        truncated_count = 0
        for line in lines:
            description = line["description"]
            shortened = description
            if _preview_cost(description, budget) > per_line_allowance:
                shortened = description[:per_line_allowance].rstrip()
                truncated_chars += max(0, len(description) - len(shortened))
                truncated_count += 1
            rendered.append(f"- {line['name']}: {shortened} (file: {line['path']})")
        report = {
            "total_count": len(lines),
            "included_count": len(lines),
            "omitted_count": 0,
            "truncated_description_chars": truncated_chars,
            "truncated_description_count": truncated_count,
            "render_strategy": "shortened_descriptions",
        }
        warning = None
        if truncated_count and (truncated_chars // max(1, truncated_count)) > CODEX_PREVIEW_DESCRIPTION_TRUNCATION_WARNING_THRESHOLD_CHARS:
            warning = "Skill descriptions were shortened to fit the skills context budget."
        return rendered, report, warning

    rendered = []
    used = 0
    omitted = 0
    truncated_chars = 0
    truncated_count = 0
    for line in lines:
        cost = _preview_cost(line["minimum"], budget)
        if used + cost <= limit:
            used += cost
            rendered.append(line["minimum"])
        else:
            omitted += 1
        if line["description"]:
            truncated_chars += len(line["description"])
            truncated_count += 1
    report = {
        "total_count": len(lines),
        "included_count": len(rendered),
        "omitted_count": omitted,
        "truncated_description_chars": truncated_chars,
        "truncated_description_count": truncated_count,
        "render_strategy": "minimum_lines_until_budget",
    }
    warning = None
    if omitted:
        warning = f"Exceeded skills context budget. {omitted} additional skill(s) were not included in the model-visible skills list."
    return rendered, report, warning


def _preview_truncation_summary(budget: dict[str, Any], report: dict[str, Any], warning: str | None) -> dict[str, Any]:
    """
    Produce a stable summary object describing truncation and budget usage for a render preview.
    
    Parameters:
        budget (dict): Budget descriptor with keys like `kind`, `limit`, `context_window`, and `context_window_percent`.
        report (dict): Render report containing counts and metrics such as `render_strategy`, `total_count`, `included_count`, `omitted_count`, `truncated_description_count`, and `truncated_description_chars`.
        warning (str | None): Optional warning message produced during rendering or truncation.
    
    Returns:
        dict: A stable truncation summary with the following keys:
            - `schema_version`: Fixed schema identifier.
            - `status`: `"truncated"` if any items were omitted or descriptions truncated, otherwise `"none"`.
            - `strategy`: The rendering strategy used.
            - `budget_kind`, `budget_limit`, `context_window`, `context_window_percent`: Budget fields echoed from `budget`.
            - `total_count`, `included_count`, `omitted_count`: Counts of skills considered, included, and omitted.
            - `truncated_description_count`, `truncated_description_chars`: Truncation metrics for descriptions.
            - `warning_message`: The provided warning or `None`.
    """
    omitted_count = int(report.get("omitted_count") or 0)
    truncated_description_count = int(report.get("truncated_description_count") or 0)
    return {
        "schema_version": "codex-preview-truncation.v1",
        "status": "truncated" if omitted_count or truncated_description_count else "none",
        "strategy": report.get("render_strategy"),
        "budget_kind": budget.get("kind"),
        "budget_limit": budget.get("limit"),
        "context_window": budget.get("context_window"),
        "context_window_percent": budget.get("context_window_percent"),
        "total_count": report.get("total_count"),
        "included_count": report.get("included_count"),
        "omitted_count": omitted_count,
        "truncated_description_count": truncated_description_count,
        "truncated_description_chars": report.get("truncated_description_chars"),
        "warning_message": warning,
    }


def build_codex_render_preview(repo_root: Path, context_window: int | None = None) -> dict[str, Any]:
    """
    Builds a "skills render-preview" payload that includes budgeted rendering of modeled skill lines and truncation metadata.
    
    Parameters:
    	repo_root (Path): Repository root used to locate modeled skills and skill metadata.
    	context_window (int | None): Optional context window percentage used to compute a token-based budget; if `None` a fixed character budget is used.
    
    Returns:
    	payload (dict): A preview payload containing keys such as `command`, `validation_commands`, `budget`, `rendered` (with `skill_lines`, `report`, and optional `warning_message`), `truncation` (summary object), and `agent_summary`.
    """
    payload = build_codex_load_preview(repo_root)
    payload["command"] = "skills render-preview"
    payload["validation_commands"] = [_skills_validation_command("render-preview")]
    budget = _preview_budget(context_window)
    rendered_lines, report, warning = _render_preview_lines(payload["skills"], budget)
    payload["budget"] = budget
    payload["rendered"] = {
        "skill_lines": rendered_lines,
        "report": report,
        "warning_message": warning,
    }
    payload["truncation"] = _preview_truncation_summary(budget, report, warning)
    payload["agent_summary"] = f"Rendered {report['included_count']} of {report['total_count']} modeled skill metadata line(s)."
    return payload


def build_codex_config_explain(repo_root: Path) -> dict[str, Any]:
    """
    Build a preview payload describing how Codex skill configuration rules are interpreted.
    
    Produces a preview payload that models the config-rule semantics for skills without reading or merging the live Codex ConfigLayerStack.
    
    Parameters:
        repo_root (Path): Path to the repository root used to locate Codex sources and skills.
    
    Returns:
        payload (dict): A preview payload containing base preview metadata, a blocked check indicating live config layers are not read, a `config_contract` describing recognized config keys and resolution policies, `validation_commands` for reproducing the check, and an `agent_summary`.
    """
    payload = _codex_preview_base(repo_root, "skills config explain")
    payload["blocked_checks"].append(
        _codex_preview_blocked_check(
            "live_skills_config_layers",
            "This command explains Codex config-rule semantics but does not read or merge the live Codex ConfigLayerStack.",
            ["codex-rs/core-skills/src/config_rules.rs", "codex-rs/config/src/skills_config.rs"],
        )
    )
    _refresh_preview_status_and_source_basis(payload)
    payload.update(
        {
            "config_contract": {
                "recognized_skills_keys": ["bundled", "include_instructions", "config"],
                "rule_entry_keys": ["path", "name", "enabled"],
                "selector_policy": "exactly_one_of_path_or_name",
                "path_policy": "canonicalize path selector when possible",
                "name_policy": "trim name selector; empty names ignored",
                "override_policy": "later rules with the same selector replace earlier rules",
                "disabled_resolution": "path selectors toggle one path; name selectors toggle every loaded skill with the exact name",
                "included_config_layers": ["User", "SessionFlags"],
                "excluded_config_layers": ["Project", "System", "Mdm", "LegacyManagedConfigTomlFromFile", "LegacyManagedConfigTomlFromMdm"],
            },
            "validation_commands": [_skills_validation_command("config", "explain")],
            "agent_summary": "Explained source-backed Codex skills.config rule semantics; live layer values are intentionally blocked.",
        }
    )
    return payload


def _extract_preview_mentions(text: str) -> dict[str, set[str]]:
    names: set[str] = set()
    paths: set[str] = set()
    for match in re.finditer(r"\[\$([A-Za-z0-9_.:-]+)\]\(([^)]+)\)", text):
        name = match.group(1)
        path = match.group(2).strip()
        if name:
            names.add(name)
        normalized_path = _normalize_preview_skill_path_reference(path)
        if normalized_path:
            paths.add(normalized_path)
    for match in re.finditer(r"(?<![A-Za-z0-9_])\$([A-Za-z0-9_.:-]+)", text):
        names.add(match.group(1))
    return {"names": names, "paths": paths}


def _normalize_preview_skill_path_reference(path: str) -> str | None:
    """Normalize skill:// directory and SKILL.md links to the preview skill path."""
    normalized = path.removeprefix("skill://").strip().rstrip("/")
    if not normalized:
        return None
    if normalized.endswith("/SKILL.md") or normalized == "SKILL.md":
        return normalized
    return f"{normalized}/SKILL.md"


def _select_preview_explicit_mentions(skills: list[dict[str, Any]], text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    mentions = _extract_preview_mentions(text)
    selected: list[dict[str, Any]] = []
    notes: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    name_counts: dict[str, int] = {}
    for skill in skills:
        if not skill.get("enabled", True):
            continue
        name = str(skill.get("name") or "")
        name_counts[name] = name_counts.get(name, 0) + 1
    for skill in skills:
        path = str(skill.get("path") or "")
        if path in seen_paths or not skill.get("enabled", True):
            continue
        if path in mentions["paths"]:
            selected.append(skill)
            seen_paths.add(path)
    for name in sorted(mentions["names"]):
        if name_counts.get(name, 0) > 1:
            notes.append({"mention": name, "status": "blocked_ambiguous_name", "matching_count": name_counts[name]})
    for skill in skills:
        path = str(skill.get("path") or "")
        name = str(skill.get("name") or "")
        if path in seen_paths or not skill.get("enabled", True):
            continue
        if name in mentions["names"] and name_counts.get(name, 0) == 1:
            selected.append(skill)
            seen_paths.add(path)
    return selected, notes


def build_codex_inject_preview(repo_root: Path, text: str) -> dict[str, Any]:
    """
    Builds a preview payload that identifies skills explicitly mentioned in the provided text and reports the selection results.
    
    Parameters:
        repo_root (Path): Filesystem path to the repository root used to discover skills.
        text (str): User-provided text containing explicit skill mentions (e.g. $name or [$name](...)).
    
    Returns:
        dict: Preview payload including base load-preview metadata and these additional fields:
            - command: the preview command string ("skills inject-preview").
            - input_text: the original input `text`.
            - mentions: dict with `names` (sorted list of mentioned names) and `paths` (sorted list of normalized skill path mentions).
            - selected_skills: list of skill metadata objects selected from explicit mentions.
            - selection_notes: notes about ambiguous or blocked selections.
            - selected_count: integer count of selected skills.
            - validation_commands: list of validation command strings for reproducing the preview.
            - agent_summary: short human-readable summary of the selection outcome.
    """
    payload = build_codex_load_preview(repo_root)
    payload["command"] = "skills inject-preview"
    payload["blocked_checks"].append(
        _codex_preview_blocked_check(
            "structured_userinput_skill_selection",
            "Preview models text mentions only; Codex structured UserInput::Skill path selections require runtime UI payloads.",
            ["codex-rs/core-skills/src/injection.rs"],
        )
    )
    _refresh_preview_status_and_source_basis(payload)
    selected, notes = _select_preview_explicit_mentions(payload["skills"], text)
    mentions = _extract_preview_mentions(text)
    payload.update(
        {
            "input_text": text,
            "mentions": {
                "names": sorted(mentions["names"]),
                "paths": sorted(mentions["paths"]),
            },
            "selected_skills": selected,
            "selection_notes": notes,
            "selected_count": len(selected),
            "validation_commands": [_skills_validation_command("inject-preview", text)],
            "agent_summary": f"Selected {len(selected)} explicit skill mention(s) from preview text.",
        }
    )
    return payload


def _command_tokens(command: str) -> tuple[list[str], str | None]:
    if not command.strip():
        return [], None
    try:
        return shlex.split(command), None
    except ValueError as exc:
        return [], f"{exc.__class__.__name__}: {exc}"


def _command_basename(command: str) -> str:
    return Path(command).name.removesuffix(".exe").lower()


def _preview_implicit_match(repo_root: Path, skills: list[dict[str, Any]], command: str, workdir: Path) -> dict[str, Any] | None:
    tokens, parse_error = _command_tokens(command)
    if parse_error:
        return None
    if not tokens:
        return None
    runner = _command_basename(tokens[0])
    script_token = None
    if runner in {"python", "python3", "bash", "zsh", "sh", "node", "deno", "ruby", "perl", "pwsh"}:
        for token in tokens[1:]:
            if token == "--" or token.startswith("-"):
                continue
            if token.lower().endswith((".py", ".sh", ".js", ".ts", ".rb", ".pl", ".ps1")):
                script_token = token
            break
    if script_token:
        script_path = (workdir / script_token).resolve() if not Path(script_token).is_absolute() else Path(script_token).resolve()
        for skill in skills:
            skill_md = repo_root / str(skill.get("path") or "")
            scripts_dir = skill_md.parent / "scripts"
            try:
                script_path.relative_to(scripts_dir.resolve())
                return skill
            except (OSError, ValueError):
                continue
    if runner in {"cat", "sed", "head", "tail", "less", "more", "bat", "awk"}:
        for token in tokens[1:]:
            if token.startswith("-"):
                continue
            candidate_path = (workdir / token).resolve() if not Path(token).is_absolute() else Path(token).resolve()
            for skill in skills:
                skill_md = repo_root / str(skill.get("path") or "")
                try:
                    if candidate_path == skill_md.resolve():
                        return skill
                except OSError:
                    continue
    return None


def build_codex_implicit_preview(repo_root: Path, command: str, workdir: str | None = None) -> dict[str, Any]:
    """
    Builds a preview payload that attempts to attribute a shell command to a modeled skill using heuristic rules.
    
    Parameters:
        repo_root (Path): Repository root used to locate modeled skills and to resolve relative paths.
        command (str): Shell command text to analyze for implicit skill attribution.
        workdir (str | None): Optional working directory used to resolve relative file/script paths; if omitted or relative, it is resolved against `repo_root`.
    
    Returns:
        dict: Preview payload dictionary derived from the load-preview containing implicit-invocation fields. The payload includes the original load-preview metadata plus attribution results (`selected_skill`, `selected_count`, `attribution_status`), `command_text`, resolved `workdir`, `validation_commands`, `agent_summary`, and any appended `blocked_checks`; `source_basis` and `status` are refreshed before return.
    """
    payload = build_codex_load_preview(repo_root)
    payload["command"] = "skills implicit-preview"
    payload["blocked_checks"].append(
        _codex_preview_blocked_check(
            "shell_parser_exact_parity",
            "Preview uses Python shlex and does not reproduce every shell parser edge case from the Codex runtime environment.",
            ["codex-rs/core-skills/src/invocation_utils.rs"],
        )
    )
    _refresh_preview_status_and_source_basis(payload)
    workdir_path = Path(workdir) if workdir else repo_root
    if not workdir_path.is_absolute():
        workdir_path = repo_root / workdir_path
    _, command_parse_error = _command_tokens(command)
    if command_parse_error:
        payload["blocked_checks"].append(
            _codex_preview_blocked_check(
                "shell_command_parse_error",
                command_parse_error,
                ["codex-rs/core-skills/src/invocation_utils.rs"],
            )
        )
        _refresh_preview_status_and_source_basis(payload)
    selected = _preview_implicit_match(repo_root, payload["skills"], command, workdir_path)
    payload.update(
        {
            "command_text": command,
            "workdir": workdir_path.as_posix(),
            "selected_skill": selected,
            "selected_count": 1 if selected else 0,
            "attribution_status": "matched" if selected else "none",
            "validation_commands": [_skills_validation_command("implicit-preview", "--command", command)],
            "agent_summary": (
                f"Implicit invocation would attribute command to {selected['name']}."
                if selected
                else "No implicit skill invocation matched the modeled command."
            ),
        }
    )
    return payload
