from __future__ import annotations

import subprocess
import re
import os
import json
import shutil
import shlex
import time
from pathlib import Path
from typing import Any, List, Optional

from ask.envelope import CallResult, ErrorObject
from ask.plugin_state import collect_plugin_state
from ask.services.plugin_cache import refresh_workspace_plugin_caches
from ask.services.plugin_sources import (
    copy_directory_contents as _copy_directory_contents,
    load_local_marketplace as _load_local_marketplace,
    materialize_first_level_skill_aliases as _materialize_first_level_skill_aliases,
)

# Allow-list for companion folder types per plugin-creator contract
_ALLOWED_COMPANION_FOLDERS = {"skills", "hooks", "scripts", "assets", "mcp", "apps", "references", "workflows"}
_INSTALL_SUMMARY_RE = re.compile(r"Installed\s+([a-z0-9][a-z0-9-]{0,63})\s+to\s+(.+)")
_SCAFFOLD_SUMMARY_RE = re.compile(r"Created plugin scaffold:\s+(.+)")
_CREATOR_FLAG_FOLDERS = {"skills", "hooks", "scripts", "assets", "mcp", "apps"}
_MANUAL_COMPANION_FOLDERS = {"references", "workflows"}
_PLUGIN_NAME_SANITIZE_RE = re.compile(r"[^a-z0-9]+")
_DEFAULT_PLUGIN_CATEGORY = "third-party"

_PLUGIN_CREATOR_SCRIPT_CANDIDATES = (
    "Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/scripts/create_basic_plugin.pyw",
)
_PLUGIN_INSTALLER_SCRIPT_CANDIDATES = (
    "Plugins/plugin-factory/skills/infrastructure_ops/plugin-installer/scripts/install-plugin-from-github.py",
)
_PLUGIN_BUILDER_SCRIPT_CANDIDATES = (
    "Plugins/plugin-factory/scripts/plugin-builder/plugin_builder.py",
)
_LOCAL_PLUGIN_ROOTS = ("plugins", "Plugins", ".agents/plugins")
_PERSONAL_PLUGIN_MARKETPLACE_ROOT = Path(".agents/plugins")
_PROJECT_PERSONAL_PLUGIN_MARKETPLACE_ROOT = Path(".agents/personal-plugins")
_REPO_PLUGIN_RUNTIME_CACHE_ROOT = Path(".agents/plugins-runtime/cache/agent-skills-local")
_NON_LOADABLE_PLUGIN_SKILL_PARTS = {"fixtures", "budget-archive", "preserved-context"}


def _to_absolute_path(path: Path) -> Path:
    """
    Produce an absolute Path with user-home expansion while preserving symbolic links.
    
    Expands '~' to the current user's home directory and returns an absolute Path without resolving or following any symbolic links.
    
    Returns:
        Path: Absolute path with '~' expanded and symlinks preserved.
    """
    return Path(path.expanduser()).absolute()


def _runtime_error_result(
    message: str,
    *,
    fix_suggestion: str,
    validation_command: str | None = None,
) -> CallResult:
    """
    Create a CallResult representing a runtime error with a single `ERR_RUNTIME` error object.

    Parameters:
        message (str): Human-readable description of the runtime error.
        fix_suggestion (str): Suggested action the operator can take to fix the error.

    Returns:
        CallResult: A result with `status` set to `"error"` and `errors` containing one `ErrorObject` with `code` `"ERR_RUNTIME"`, the provided `message`, and `fix_suggestion`.
    """
    result = CallResult()
    result.status = "error"
    if validation_command:
        result.data["validation_commands"] = [validation_command]
    result.errors.append(
        ErrorObject(
            code="ERR_RUNTIME",
            message=message,
            fix_suggestion=fix_suggestion,
        )
    )
    return result


def _validation_error_result(
    message: str,
    *,
    fix_suggestion: str,
    validation_command: str | None = None,
) -> CallResult:
    """
    Create a CallResult representing a validation error.

    Parameters:
        message (str): Human-readable validation message describing the problem.
        fix_suggestion (str): Recommended corrective action or command the user can run.

    Returns:
        CallResult: A result with `status` set to "error" and a single `ErrorObject` with code `ERR_VALIDATION`, containing the provided message and fix suggestion.
    """
    result = CallResult()
    result.status = "error"
    if validation_command:
        result.data["validation_commands"] = [validation_command]
    result.errors.append(
        ErrorObject(
            code="ERR_VALIDATION",
            message=message,
            fix_suggestion=fix_suggestion,
        )
    )
    return result


def _plugin_init_validation_command(
    name: str,
    *,
    category: str = _DEFAULT_PLUGIN_CATEGORY,
    with_marketplace: bool = False,
    companion_folders: Optional[List[str]] = None,
    action: str = "init",
) -> str:
    parts = ["./bin/ask", "plugins", action, name]
    if category != _DEFAULT_PLUGIN_CATEGORY:
        parts.extend(["--category", category])
    if with_marketplace:
        parts.append("--with-marketplace")
    for folder in companion_folders or []:
        if folder in {"scripts", "assets", "references", "workflows"}:
            parts.append(f"--with-{folder}")
    parts.extend(["--json", "--robot"])
    return " ".join(shlex.quote(part) for part in parts)


def _plugin_install_validation_command(
    url: str,
    plugin_path: str,
    *,
    name: str | None = None,
    ref: str | None = None,
    dest: str = "Plugins/third-party",
    validation_level: str = "compat",
    allow_untrusted_source: bool = False,
    allow_unpinned_ref: bool = False,
    dry_run: bool = False,
    sync_profile: bool = False,
    require_desktop_loadable: bool = False,
    action: str = "install",
) -> str:
    """
    Builds a shell-quoted validation command string for plugin install-related `ask plugins` actions.
    
    Parameters:
        url (str): Source URL or identifier passed to the action.
        plugin_path (str): Target filesystem path supplied to `--path`.
        name (str | None): Optional `--name` to override installed plugin name.
        ref (str | None): Optional `--ref` (git ref, tag, or digest).
        dest (str): Optional `--dest` repository-relative destination (defaults to `Plugins/third-party`).
        validation_level (str): Validation level passed to `--validation-level` (defaults to `compat`).
        allow_untrusted_source (bool): If true, includes `--allow-untrusted-source`.
        allow_unpinned_ref (bool): If true, includes `--allow-unpinned-ref`.
        dry_run (bool): If true, includes `--dry-run`.
        sync_profile (bool): If true, includes `--sync-profile`.
        require_desktop_loadable (bool): If true, includes `--require-desktop-loadable`.
        action (str): Subcommand action name (e.g., `install`, `update`).
    
    Returns:
        str: A shell-quoted command string ready to execute (always includes `--json --robot`).
    """
    parts = ["./bin/ask", "plugins", action, url, "--path", plugin_path]
    if name:
        parts.extend(["--name", name])
    if ref:
        parts.extend(["--ref", ref])
    if dest != "Plugins/third-party":
        parts.extend(["--dest", dest])
    if validation_level != "compat":
        parts.extend(["--validation-level", validation_level])
    if allow_untrusted_source:
        parts.append("--allow-untrusted-source")
    if allow_unpinned_ref:
        parts.append("--allow-unpinned-ref")
    if sync_profile:
        parts.append("--sync-profile")
    if require_desktop_loadable:
        parts.append("--require-desktop-loadable")
    if dry_run:
        parts.append("--dry-run")
    parts.extend(["--json", "--robot"])
    return " ".join(shlex.quote(part) for part in parts)


def _plugins_prune_stale_config_validation_command(
    *,
    dry_run: bool = False,
    stability_seconds: float = 10.0,
    stability_interval_seconds: float = 0.5,
    verify_stable_when_clean: bool = False,
) -> str:
    """
    Builds the validation command for `ask plugins prune-stale-config` with given verification and dry-run options.
    
    Parameters:
        dry_run (bool): If True, include `--dry-run` to only simulate changes.
        stability_seconds (float): Maximum seconds to wait for stale plugin state to clear; adds `--stability-seconds <value>` when different from the default.
        stability_interval_seconds (float): Poll interval in seconds used when waiting for stability; adds `--stability-interval-seconds <value>` when different from the default.
        verify_stable_when_clean (bool): If True, add `--verify-stable-when-clean` to perform an additional stability verification when no stale IDs are initially found.
    
    Returns:
        str: A shell-quoted command string to run the validation (`./bin/ask plugins prune-stale-config ...`) including `--json --robot`.
    """
    parts = ["./bin/ask", "plugins", "prune-stale-config"]
    if dry_run:
        parts.append("--dry-run")
    if stability_seconds != 10.0:
        parts.extend(["--stability-seconds", str(stability_seconds)])
    if stability_interval_seconds != 0.5:
        parts.extend(["--stability-interval-seconds", str(stability_interval_seconds)])
    if verify_stable_when_clean:
        parts.append("--verify-stable-when-clean")
    parts.extend(["--json", "--robot"])
    return " ".join(shlex.quote(part) for part in parts)


def _remove_stale_plugin_config_blocks(content: str, stale_plugin_ids: set[str]) -> tuple[str, list[str]]:
    """
    Remove TOML plugin configuration entries for the given stale plugin IDs.
    
    This parses the provided TOML text and removes plugin definitions that match any ID in `stale_plugin_ids`. It recognizes two shapes:
    - Table headers like `[plugins."<plugin_id>"]` and removes that header plus all following lines up to the next section header.
    - Dotted keys like `plugins."<plugin_id>".enabled = ...` and removes that single line.
    Trailing empty lines produced by removals are trimmed where appropriate.
    
    Parameters:
        content (str): The TOML file content to process.
        stale_plugin_ids (set[str]): Plugin IDs to remove from the content.
    
    Returns:
        tuple[str, list[str]]: A pair where the first element is the updated TOML content and the second is a sorted list of unique plugin IDs that were removed.
    """
    lines = content.splitlines(keepends=True)
    kept: list[str] = []
    removed: list[str] = []
    index = 0
    table_re = re.compile(r'^\s*\[plugins\."(?P<plugin_id>[^"]+)"\]\s*(?:#.*)?$')
    dotted_re = re.compile(r'^\s*plugins\."(?P<plugin_id>[^"]+)"\.enabled\s*=')

    while index < len(lines):
        line = lines[index]
        table_match = table_re.match(line.rstrip("\r\n"))
        if table_match and table_match.group("plugin_id") in stale_plugin_ids:
            plugin_id = table_match.group("plugin_id")
            removed.append(plugin_id)
            index += 1
            while index < len(lines) and not lines[index].lstrip().startswith("["):
                index += 1
            while kept and kept[-1].strip() == "" and (not lines[index:] or lines[index].strip() == ""):
                kept.pop()
            continue

        dotted_match = dotted_re.match(line)
        if dotted_match and dotted_match.group("plugin_id") in stale_plugin_ids:
            removed.append(dotted_match.group("plugin_id"))
            index += 1
            continue

        kept.append(line)
        index += 1

    return "".join(kept), sorted(set(removed))


def _marketplace_source_path_for_runtime_root(runtime_root: Path, plugin_name: str) -> str:
    """
    Compute the marketplace-style relative path to a plugin for a given runtime root.
    
    Parameters:
        runtime_root (Path): The runtime root directory. If this is the `plugins` directory under a `.agents` parent, the returned path will use the `".agents/plugins"` segment.
        plugin_name (str): The plugin directory name.
    
    Returns:
        path (str): A relative path of the form `"./<runtime_root_segment>/<plugin_name>"`.
    """
    relative_runtime_root = runtime_root.name
    if runtime_root.name == "plugins" and runtime_root.parent.name == ".agents":
        relative_runtime_root = ".agents/plugins"
    return f"./{relative_runtime_root}/{plugin_name}"


def _runtime_marketplace_payload(entries: list[dict[str, Any]], *, runtime_root: Path) -> dict[str, Any]:
    """
    Builds a runtime-local marketplace payload that maps plugin entries to local sources.
    
    Parameters:
        entries (list[dict[str, Any]]): List of plugin metadata dictionaries. Each entry must include a `name` key; any existing `path` or `source` keys are ignored.
        runtime_root (Path): The runtime root used to compute the marketplace-relative `path` for each plugin's local `source`.
    
    Returns:
        dict[str, Any]: A payload with `"name": "agent-skills-local"` and a `"plugins"` list where each plugin object contains the original entry fields (excluding `path` and `source`) and a `source` mapping of the form `{"source": "local", "path": <computed_path>}`.
    """
    return {
        "name": "agent-skills-local",
        "plugins": [
            {
                **{
                    key: value
                    for key, value in entry.items()
                    if key not in {"path", "source"}
                },
                "source": {
                    "source": "local",
                    "path": _marketplace_source_path_for_runtime_root(runtime_root, str(entry["name"])),
                },
            }
            for entry in entries
        ],
    }


def _personal_marketplace_payload(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Build a personal marketplace payload mapping entries to local plugin sources.
    
    Parameters:
        entries (list[dict[str, Any]]): Iterable of plugin metadata dicts; each entry must include a 'name' key.
    
    Returns:
        dict[str, Any]: Marketplace payload with keys:
            - "name": fixed string "agent-skills-local".
            - "plugins": list of plugin records where each record contains all original entry keys except `path` and `source`, and a normalized `source` object:
                {"source": "local", "path": "./.codex/plugins/<name>"} where `<name>` is taken from the entry's 'name'.
    """
    return {
        "name": "agent-skills-local",
        "plugins": [
            {
                **{
                    key: value
                    for key, value in entry.items()
                    if key not in {"path", "source"}
                },
                "source": {
                    "source": "local",
                    "path": f"./.codex/plugins/{entry['name']}",
                },
            }
            for entry in entries
        ],
    }


def _looks_like_materialized_plugin_payload(path: Path) -> bool:
    """Return true when a marketplace child is a local plugin payload, not arbitrary user data."""
    return (
        path.is_dir()
        and not path.is_symlink()
        and (
            (path / ".codex-plugin" / "plugin.json").is_file()
            or (path / "plugin.json").is_file()
            or (path / "marketplace.json").is_file()
        )
    )


def _sync_personal_marketplace(
    *,
    home: Path,
    repo_root: Path,
    marketplace_entries: list[dict[str, Any]],
    dry_run: bool,
) -> dict[str, Any]:
    """
    Synchronize the user's personal plugin marketplace directory and ensure marketplace entries are represented (by writing marketplace.json and creating symlinks to local plugin locations).
    
    When dry_run is True the function only computes the plan and does not modify the filesystem. When not dry_run the function:
    - Writes a personal `marketplace.json` describing the provided entries under the user's personal marketplace root.
    - If the existing personal marketplace root is a symlink that points into the repository's Plugins/ or plugins/ directories, replaces it with a symlink to the project-local personal marketplace root.
    - Ensures a symlink exists for each requested plugin at `<personal marketplace root>/<plugin_name>` that points to `~/.codex/plugins/<plugin_name>` when that target exists; records plugins that were symlinked and those skipped.
    
    Parameters:
        home (Path): The user's home directory (used as base for personal `.codex` locations).
        repo_root (Path): Repository root used to locate the project personal marketplace root.
        marketplace_entries (list[dict[str, Any]]): List of marketplace entry objects; each entry must include a `"name"` key with the plugin name.
        dry_run (bool): If True, no filesystem mutations are performed; the returned report reflects the planned actions.
    
    Returns:
        dict[str, Any]: A report of the synchronization attempt containing:
          - runtime_root: path to the personal marketplace root used.
          - marketplace_target: path to the written `marketplace.json`.
          - planned_plugins: list of plugin names requested.
          - copied_plugins, skipped_plugins, removed_entries, pruned_plugins: lists reserved for other sync variants (empty here).
          - skipped_marketplace_copy: boolean (False here).
          - symlinked_plugins: list of plugin names that were symlinked during this run.
          - planned_symlinked_plugins: list of plugin names that would be symlinked during a dry run.
          - skipped_symlinks: list of plugin names that were not symlinked and the reason is either existing wrong file, missing target, or identical existing symlink.
          - official_personal_marketplace: True when the marketplace root is the canonical personal marketplace.
          - project_marketplace_root: path to the repository-local personal marketplace root.
          - personal_marketplace_symlink_target: resolved target of the marketplace root symlink when present, otherwise None.
          - repointed_marketplace_root: True if an existing symlinked marketplace root was repointed to the project marketplace root.
          - planned_repoint_marketplace_root: True if dry-run detected a marketplace root repoint.
          - dry_run: echoes the input dry_run flag.
    """
    marketplace_root = home / _PERSONAL_PLUGIN_MARKETPLACE_ROOT
    project_marketplace_root = repo_root / _PROJECT_PERSONAL_PLUGIN_MARKETPLACE_ROOT
    marketplace_target = marketplace_root / "marketplace.json"
    symlinked_plugins: list[str] = []
    planned_symlinked_plugins: list[str] = []
    skipped_symlinks: list[str] = []
    replaced_materialized_plugins: list[str] = []
    planned_plugins = [str(entry["name"]) for entry in marketplace_entries]
    repointed_marketplace_root = False
    planned_repoint_marketplace_root = False
    unsafe_repo_roots = [repo_root / "Plugins", repo_root / "plugins"]

    if marketplace_root.is_symlink():
        try:
            resolved_marketplace_root = marketplace_root.resolve(strict=True)
        except OSError:
            resolved_marketplace_root = None
        if resolved_marketplace_root is not None:
            points_at_repo_source = False
            for repo_source_root in unsafe_repo_roots:
                try:
                    points_at_repo_source = repo_source_root.exists() and resolved_marketplace_root.samefile(repo_source_root)
                except OSError:
                    points_at_repo_source = False
                if points_at_repo_source:
                    break
            if points_at_repo_source:
                planned_repoint_marketplace_root = True
                if not dry_run:
                    marketplace_root.unlink()
                    marketplace_root.symlink_to(project_marketplace_root, target_is_directory=True)
                    repointed_marketplace_root = True

    if not dry_run:
        marketplace_root.parent.mkdir(parents=True, exist_ok=True)
        project_marketplace_root.mkdir(parents=True, exist_ok=True)
        marketplace_root.mkdir(parents=True, exist_ok=True)
        marketplace_target.write_text(
            json.dumps(_personal_marketplace_payload(marketplace_entries), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    for entry in marketplace_entries:
        plugin_name = str(entry["name"])
        link_path = marketplace_root / plugin_name
        target_path = home / ".codex" / "plugins" / plugin_name
        root_will_repoint = planned_repoint_marketplace_root
        if target_path.exists() and (root_will_repoint or not link_path.exists() or link_path.is_symlink()):
            if root_will_repoint or not link_path.is_symlink() or link_path.resolve() != target_path.resolve():
                planned_symlinked_plugins.append(plugin_name)
        if dry_run:
            continue
        if link_path.is_symlink():
            if link_path.resolve() == target_path.resolve():
                skipped_symlinks.append(plugin_name)
                continue
            link_path.unlink()
        elif link_path.exists():
            if target_path.exists() and _looks_like_materialized_plugin_payload(link_path):
                shutil.rmtree(link_path)
                replaced_materialized_plugins.append(plugin_name)
            else:
                skipped_symlinks.append(plugin_name)
                continue
        if target_path.exists():
            link_path.symlink_to(target_path)
            symlinked_plugins.append(plugin_name)
        else:
            skipped_symlinks.append(plugin_name)

    return {
        "runtime_root": str(marketplace_root),
        "marketplace_target": str(marketplace_target),
        "planned_plugins": planned_plugins,
        "copied_plugins": [],
        "skipped_plugins": [],
        "removed_entries": [],
        "pruned_plugins": [],
        "skipped_marketplace_copy": False,
        "symlinked_plugins": symlinked_plugins,
        "replaced_materialized_plugins": replaced_materialized_plugins,
        "planned_symlinked_plugins": planned_symlinked_plugins,
        "skipped_symlinks": skipped_symlinks,
        "official_personal_marketplace": True,
        "project_marketplace_root": str(project_marketplace_root),
        "personal_marketplace_symlink_target": (
            str(marketplace_root.resolve()) if marketplace_root.exists() else None
        ),
        "repointed_marketplace_root": repointed_marketplace_root,
        "planned_repoint_marketplace_root": planned_repoint_marketplace_root,
        "dry_run": dry_run,
    }


def prune_stale_plugin_config(
    repo_root: Path,
    *,
    dry_run: bool = False,
    stability_seconds: float = 10.0,
    stability_interval_seconds: float = 0.5,
    verify_stable_when_clean: bool = False,
) -> CallResult:
    """
    Remove stale enabled plugin entries from the active Codex config file.
    
    Parameters:
        repo_root (Path): Repository root used to collect plugin desktop readiness state.
        dry_run (bool): If True, report planned removals without modifying the config.
        stability_seconds (float): Maximum seconds to wait when verifying desktop readiness stability (must be >= 0).
        stability_interval_seconds (float): Poll interval in seconds when waiting for stability (must be > 0).
        verify_stable_when_clean (bool): If True and no stale IDs are initially found, poll until stability_seconds to confirm none appear.
    
    Returns:
        CallResult: Result object containing status and structured data. On success or error the `data` dictionary includes at least:
            - `validation_commands`: list with the validation command string.
            - `config_path`: path to the active Codex config examined.
            - `stale_enabled_plugin_ids`: list of stale plugin IDs detected.
            - `removed_plugin_ids`: list of plugin IDs removed from the config (empty if none or on failure).
            - `changed`: `True` if the config would be/were modified, `False` otherwise.
            - `desktop_readiness_state`: the desktop readiness snapshot collected after any stability checks.
            - `stability_checks`: list of per-attempt readiness snapshots observed while waiting for stability.
        On validation or IO errors the `errors` list contains ErrorObject entries describing the problem and suggested fixes.
    """
    result = CallResult()
    result.data["validation_commands"] = [
        _plugins_prune_stale_config_validation_command(
            dry_run=dry_run,
            stability_seconds=stability_seconds,
            stability_interval_seconds=stability_interval_seconds,
            verify_stable_when_clean=verify_stable_when_clean,
        )
    ]
    result.data["dry_run"] = dry_run
    result.data["stability_seconds"] = stability_seconds
    result.data["stability_interval_seconds"] = stability_interval_seconds
    result.data["verify_stable_when_clean"] = verify_stable_when_clean

    if stability_seconds < 0:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="stability_seconds must be greater than or equal to 0.",
                fix_suggestion="Pass --stability-seconds 0 or a positive number.",
            )
        )
        return result
    if stability_interval_seconds <= 0:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="stability_interval_seconds must be greater than 0.",
                fix_suggestion="Pass a positive --stability-interval-seconds value.",
            )
        )
        return result

    readiness = collect_plugin_state(repo_root)["desktop_readiness_state"]
    stale_plugin_ids = sorted(readiness.get("stale_enabled_plugin_ids", []))
    config_path_value = readiness.get("config_path")
    config_path = Path(config_path_value) if isinstance(config_path_value, str) else Path.home() / ".codex" / "config.toml"

    result.data["config_path"] = str(config_path)
    result.data["stale_enabled_plugin_ids"] = stale_plugin_ids
    if not stale_plugin_ids:
        result.data["message"] = "No stale enabled plugin IDs found in active Codex config."
        result.data["changed"] = False
        result.data["removed_plugin_ids"] = []
        if verify_stable_when_clean and not dry_run:
            post_readiness, stability_checks = _watch_stale_plugin_stability(
                repo_root,
                stability_seconds=stability_seconds,
                stability_interval_seconds=stability_interval_seconds,
            )
            result.data["desktop_readiness_state"] = post_readiness
            result.data["stability_checks"] = stability_checks
            if post_readiness.get("stale_enabled_plugin_ids"):
                result.status = "error"
                result.errors.append(
                    ErrorObject(
                        code="ERR_VALIDATION",
                        message="Stale enabled plugin IDs appeared while verifying clean active Codex config.",
                        fix_suggestion=(
                            "An external Codex Desktop/config writer is reintroducing stale plugin IDs. "
                            "Restart Codex Desktop, then rerun ./bin/ask plugins prune-stale-config "
                            "--verify-stable-when-clean --json --robot."
                        ),
                    )
                )
        return result

    try:
        content = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_IO",
                message=f"Failed to read active Codex config: {exc}",
                fix_suggestion=f"Check permissions for {config_path}.",
            )
        )
        return result

    updated, removed_plugin_ids = _remove_stale_plugin_config_blocks(content, set(stale_plugin_ids))
    result.data["removed_plugin_ids"] = removed_plugin_ids
    result.data["changed"] = bool(removed_plugin_ids)
    if sorted(removed_plugin_ids) != stale_plugin_ids:
        missing = sorted(set(stale_plugin_ids) - set(removed_plugin_ids))
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Active Codex config has stale enabled plugin IDs that could not be removed safely.",
                fix_suggestion=f"Remove these stale plugin IDs manually from {config_path}: {', '.join(missing)}",
            )
        )
        return result

    if dry_run:
        result.data["message"] = "Dry run - would remove stale enabled plugin IDs from active Codex config."
        return result

    try:
        config_path.write_text(updated, encoding="utf-8")
    except OSError as exc:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_IO",
                message=f"Failed to write active Codex config: {exc}",
                fix_suggestion=f"Check write permissions for {config_path}.",
            )
        )
        return result

    post_readiness, stability_checks = _watch_stale_plugin_stability(
        repo_root,
        stability_seconds=stability_seconds,
        stability_interval_seconds=stability_interval_seconds,
    )
    result.data["desktop_readiness_state"] = post_readiness
    result.data["stability_checks"] = stability_checks
    result.data["message"] = "Removed stale enabled plugin IDs from active Codex config."
    if post_readiness.get("stale_enabled_plugin_ids"):
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message="Stale enabled plugin IDs reappeared after pruning active Codex config.",
                fix_suggestion=(
                    "An external Codex Desktop/config writer is reintroducing stale plugin IDs. "
                    "Restart Codex Desktop, then rerun ./bin/ask plugins prune-stale-config --json --robot."
                ),
            )
        )
    return result


def _watch_stale_plugin_stability(
    repo_root: Path,
    *,
    stability_seconds: float,
    stability_interval_seconds: float,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """
    Polls the repository's desktop readiness state until the set of stale enabled plugin IDs clears or the stability timeout elapses.
    
    Parameters:
    	repo_root (Path): Repository root used by collect_plugin_state to obtain desktop readiness.
    	stability_seconds (float): Maximum time in seconds to wait for stability.
    	stability_interval_seconds (float): Seconds between consecutive polls (the function will not sleep past the deadline).
    
    Returns:
    	post_readiness (dict): Final `desktop_readiness_state` snapshot returned by collect_plugin_state.
    	stability_checks (list[dict[str, Any]]): Ordered list of poll attempts; each entry contains `attempt` (int) and `stale_enabled_plugin_ids` (list[str]).
    """
    stability_checks: list[dict[str, Any]] = []
    post_readiness = collect_plugin_state(repo_root)["desktop_readiness_state"]
    stability_checks.append(
        {
            "attempt": 0,
            "stale_enabled_plugin_ids": post_readiness.get("stale_enabled_plugin_ids", []),
        }
    )
    deadline = time.monotonic() + stability_seconds
    attempt = 1
    while time.monotonic() < deadline:
        if post_readiness.get("stale_enabled_plugin_ids"):
            break
        time.sleep(min(stability_interval_seconds, max(deadline - time.monotonic(), 0)))
        post_readiness = collect_plugin_state(repo_root)["desktop_readiness_state"]
        stability_checks.append(
            {
                "attempt": attempt,
                "stale_enabled_plugin_ids": post_readiness.get("stale_enabled_plugin_ids", []),
            }
        )
        attempt += 1
    return post_readiness, stability_checks


def _plugin_harden_validation_command(
    plugin_path: str,
    *,
    require_marketplace: bool = True,
    marketplace_path: str = "Plugins/marketplace.json",
    run_compat: bool = True,
    run_marketplace_audit: bool = True,
    allow_legacy_marketplace_path: bool = True,
) -> str:
    """
    Builds a shell-quoted `ask plugins harden` command for the given plugin path with selected audit and marketplace options.
    
    Parameters:
        plugin_path (str): Path or identifier passed to `ask plugins harden`.
        require_marketplace (bool): If True, enforce that a marketplace is required; when False adds `--no-require-marketplace`.
        marketplace_path (str): Path to the marketplace JSON to pass via `--marketplace-path` when different from the default.
        run_compat (bool): If False, skip compatibility auditing by adding `--skip-compat`.
        run_marketplace_audit (bool): If False, skip the marketplace audit by adding `--skip-marketplace-audit`.
        allow_legacy_marketplace_path (bool): If False, require strict marketplace path handling by adding `--strict-marketplace-path`.
    
    Returns:
        str: A shell-quoted command string ready to be executed (e.g. via subprocess) to run the harden action with `--json --robot` appended.
    """
    parts = ["./bin/ask", "plugins", "harden", plugin_path]
    if marketplace_path != "Plugins/marketplace.json":
        parts.extend(["--marketplace-path", marketplace_path])
    if not run_compat:
        parts.append("--skip-compat")
    if not run_marketplace_audit:
        parts.append("--skip-marketplace-audit")
    if not require_marketplace:
        parts.append("--no-require-marketplace")
    if not allow_legacy_marketplace_path:
        parts.append("--strict-marketplace-path")
    parts.extend(["--json", "--robot"])
    return " ".join(shlex.quote(part) for part in parts)


def _plugin_validation_command(action: str, *args: str, **flags: bool) -> str:
    parts = ["./bin/ask", "plugins", action, *args]
    for flag, enabled in flags.items():
        if enabled:
            parts.append(f"--{flag.replace('_', '-')}")
    parts.extend(["--json", "--robot"])
    return " ".join(shlex.quote(part) for part in parts)


def _resolve_script_path(repo_root: Path, candidates: tuple[str, ...]) -> Path:
    """
    Selects the first existing helper script from a list of relative candidate paths under a repository root.

    Parameters:
        repo_root (Path): Root directory to resolve candidate relative paths against.
        candidates (tuple[str, ...]): Ordered relative paths to check under `repo_root`.

    Returns:
        Path: The path to the first candidate that exists as a file.

    Raises:
        FileNotFoundError: If none of the candidates exist; the error message lists the checked paths.
    """
    for rel in candidates:
        candidate = repo_root / rel
        if candidate.is_file():
            return candidate
    searched = ", ".join(candidates)
    raise FileNotFoundError(f"No matching helper script found under repo root. Checked: {searched}")


def _resolve_script_path_or_runtime_error(
    repo_root: Path,
    candidates: tuple[str, ...],
    *,
    fix_suggestion: str,
) -> tuple[Optional[Path], Optional[CallResult]]:
    """
    Resolve the first existing script path from a list of candidate relative paths under `repo_root`, or produce a runtime error result if none are found.

    Parameters:
        repo_root (Path): Repository root against which candidate paths are resolved.
        candidates (tuple[str, ...]): Relative file paths (candidates) to check under `repo_root`, in order of preference.
        fix_suggestion (str): Human-facing suggestion to fix the problem when no candidate is found.

    Returns:
        tuple[Optional[Path], Optional[CallResult]]: A pair where the first element is the resolved Path when found and the second is None; or the first element is None and the second is a `CallResult` describing the runtime error and containing `fix_suggestion`.
    """
    try:
        return _resolve_script_path(repo_root, candidates), None
    except FileNotFoundError as exc:
        return None, _runtime_error_result(str(exc), fix_suggestion=fix_suggestion)


def _normalize_plugin_name(raw_name: str) -> str:
    """
    Normalize a raw plugin name into a filesystem- and URL-safe kebab-case identifier.

    Parameters:
        raw_name (str): The original plugin name.

    Returns:
        str: The name lowercased with each sequence of non-alphanumeric characters replaced by a single hyphen, leading and trailing hyphens removed, and consecutive hyphens collapsed.
    """
    normalized = raw_name.strip().lower()
    normalized = _PLUGIN_NAME_SANITIZE_RE.sub("-", normalized).strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized


def _prune_non_loadable_plugin_skill_manifests(plugin_root: Path) -> list[str]:
    """Remove archive/fixture SKILL.md files from materialized runtime payloads."""
    removed: list[str] = []
    if not plugin_root.is_dir():
        return removed
    skills_root = plugin_root / "skills"
    for skill_md in sorted(plugin_root.rglob("SKILL.md")):
        relative = skill_md.relative_to(plugin_root)
        relative_parts = set(relative.parts[:-1])
        if not (relative_parts & _NON_LOADABLE_PLUGIN_SKILL_PARTS):
            if (
                skills_root.is_dir()
                and skill_md.parent.parent != skills_root
                and (skills_root / skill_md.parent.name / "SKILL.md").is_file()
            ):
                pass
            else:
                continue
        skill_md.unlink()
        removed.append(relative.as_posix())
    return removed


def _sync_one_runtime_root(
    *,
    runtime_root: Path,
    canonical_runtime_root: Path | None = None,
    repo_root: Path,
    marketplace_path: Path,
    marketplace_entries: list[dict[str, Any]],
    dry_run: bool,
) -> dict[str, Any]:
    """
    Replaces local plugin runtime mirrors from the repository's local marketplace entries.

    The canonical runtime root receives one materialized plugin payload. Other
    runtime roots receive symlink aliases to the canonical payload so compatibility
    paths cannot drift into independent plugin copies. Non-local plugin cache
    entries are preserved. Stale local mirrors (directories bearing the
    `.codex-repo-plugin-source` marker) that are no longer declared in
    `marketplace_entries` are removed. When `dry_run` is True no filesystem
    mutations are performed; a report of planned/copied/replaced/pruned names is
    still returned.

    Parameters:
        runtime_root (Path): Absolute path to the runtime profile directory to synchronize.
        repo_root (Path): Repository root used to resolve marketplace entry paths.
        marketplace_path (Path): Path to the source `marketplace.json` in the repository.
        marketplace_entries (list[dict[str, Any]]): List of marketplace entries; each entry must contain `"name"` and `"path"` (repo-relative).
        dry_run (bool): If True, perform a non-mutating dry run (no copies, removals, or manifest write).

    Returns:
        dict[str, Any]: Report containing:
            - "runtime_root": str path of the runtime root.
            - "marketplace_target": str path where the manifest would be/was written.
            - "planned_plugins": list of plugin names processed from the marketplace.
            - "copied_plugins": list of plugin names copied (empty if dry_run).
            - "removed_entries": local plugin target names that were replaced or would be replaced.
            - "pruned_plugins": list of stale local plugin names removed (empty if dry_run).
            - "dry_run": the `dry_run` input flag.

    Raises:
        FileNotFoundError: If a marketplace entry's source directory does not exist under `repo_root`.
    """
    runtime_root.mkdir(parents=True, exist_ok=True)

    planned_plugins: list[str] = []
    copied_plugins: list[str] = []
    symlinked_plugins: list[str] = []
    skipped_plugins: list[str] = []
    removed_entries: list[str] = []
    pruned_plugins: list[str] = []
    pruned_non_loadable_skill_manifests: list[dict[str, Any]] = []
    marketplace_target = runtime_root / "marketplace.json"
    skipped_marketplace_copy = False
    marker_name = ".codex-repo-plugin-source"
    canonical_root = canonical_runtime_root or runtime_root
    materializes_payload = runtime_root == canonical_root

    resolved_sources: list[tuple[str, Path]] = []
    for entry in marketplace_entries:
        plugin_name = entry["name"]
        relative = entry["path"]
        source_dir = repo_root / relative.removeprefix("./")
        if not source_dir.is_dir():
            raise FileNotFoundError(f"Local plugin source missing for '{plugin_name}': {source_dir}")
        resolved_sources.append((plugin_name, source_dir))

    if not dry_run:
        if marketplace_target.exists() and marketplace_path.samefile(marketplace_target):
            skipped_marketplace_copy = True
        else:
            marketplace_target.write_text(
                json.dumps(
                    _runtime_marketplace_payload(marketplace_entries, runtime_root=runtime_root),
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )

    keep_names = {plugin_name for plugin_name, _ in resolved_sources}
    for plugin_name, source_dir in resolved_sources:
        planned_plugins.append(plugin_name)
        target_dir = runtime_root / plugin_name
        canonical_target_dir = canonical_root / plugin_name
        if target_dir.exists() or target_dir.is_symlink():
            removed_entries.append(plugin_name)
        if not dry_run:
            if materializes_payload:
                if target_dir.exists() and source_dir.samefile(target_dir):
                    skipped_plugins.append(plugin_name)
                    continue
                if target_dir.is_symlink():
                    target_dir.unlink()
                _copy_directory_contents(source_dir, target_dir)
                _materialize_first_level_skill_aliases(target_dir)
                removed_manifests = _prune_non_loadable_plugin_skill_manifests(target_dir)
                if removed_manifests:
                    pruned_non_loadable_skill_manifests.append(
                        {"plugin": plugin_name, "skill_manifests": removed_manifests}
                    )
                (target_dir / marker_name).write_text(str(source_dir.resolve()) + "\n", encoding="utf-8")
                copied_plugins.append(plugin_name)
                continue

            if not canonical_target_dir.exists():
                raise FileNotFoundError(
                    f"Canonical local plugin payload missing for '{plugin_name}': {canonical_target_dir}"
                )
            if target_dir.is_symlink():
                if target_dir.resolve() == canonical_target_dir.resolve():
                    skipped_plugins.append(plugin_name)
                    continue
                target_dir.unlink()
            elif target_dir.exists():
                if target_dir.is_dir():
                    shutil.rmtree(target_dir)
                else:
                    target_dir.unlink()
            target_dir.symlink_to(canonical_target_dir, target_is_directory=True)
            symlinked_plugins.append(plugin_name)

    # Prune stale local plugin mirrors no longer declared in the marketplace.
    reserved = {"marketplace.json", "cache"}
    if runtime_root.is_dir():
        for child in runtime_root.iterdir():
            if child.name in keep_names or child.name in reserved:
                continue
            if not child.is_dir():
                continue
            marker_file = child / marker_name
            if not marker_file.is_file():
                continue
            pruned_plugins.append(child.name)
            if not dry_run:
                if child.is_symlink():
                    child.unlink()
                else:
                    shutil.rmtree(child)

    return {
        "runtime_root": str(runtime_root),
        "marketplace_target": str(marketplace_target),
        "planned_plugins": planned_plugins,
        "copied_plugins": copied_plugins,
        "symlinked_plugins": symlinked_plugins,
        "skipped_plugins": skipped_plugins,
        "removed_entries": removed_entries,
        "pruned_plugins": pruned_plugins,
        "pruned_non_loadable_skill_manifests": pruned_non_loadable_skill_manifests,
        "skipped_marketplace_copy": skipped_marketplace_copy,
        "materializes_payload": materializes_payload,
        "dry_run": dry_run,
    }


def sync_local_runtime_plugins(repo_root: Path, *, dry_run: bool = False) -> CallResult:
    """
    Replaces repository-local plugin runtime mirrors in each Codex profile from canonical `Plugins/` sources.

    Use this after changing or updating any local plugin source or
    `Plugins/marketplace.json`. The profile-local `plugins/` root is the only
    materialized payload root; compatibility roots are symlink aliases to that
    payload so loader-visible paths cannot become competing plugin copies.

    Parameters:
        repo_root (Path): Path to the repository root containing the Plugins/ tree and Plugins/marketplace.json.
        dry_run (bool): If True, performs a simulation without making filesystem changes.

    Returns:
        CallResult: On success, contains status "success" and data with:
            - message (str): Short success message.
            - profile_homes (list[str]): Paths of Codex profile homes that were processed.
            - plugin_names (list[str]): Names of local plugins considered for sync.
            - runtime_reports (list[dict]): Per-runtime-root synchronization reports produced by the sync logic.
            - dry_run (bool): Echoes the input dry_run flag.
        On error, returns a CallResult with status "error" and an ErrorObject describing the problem (e.g., missing/invalid marketplace manifest or no Codex profile homes found).
    """
    result = CallResult()
    validation_command = _plugin_validation_command("sync-local-runtime", dry_run=dry_run)
    result.data["validation_commands"] = [validation_command]
    try:
        marketplace_path, entries = _load_local_marketplace(repo_root)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        return _runtime_error_result(
            str(exc),
            fix_suggestion="Ensure Plugins/marketplace.json exists and contains valid local plugin entries.",
            validation_command=validation_command,
        )

    if not entries:
        return _validation_error_result(
            "No local plugins were found in Plugins/marketplace.json.",
            fix_suggestion="Add local plugin entries before replacing runtime mirrors.",
            validation_command=validation_command,
        )

    home = Path.home()
    profile_homes = []
    default_home = home / ".codex"
    if default_home.is_dir() or default_home.exists():
        profile_homes.append(default_home)
    profile_homes.extend(sorted(path for path in home.glob(".codex-*") if path.is_dir()))

    if not profile_homes:
        return _validation_error_result(
            "No Codex home directories were found under the current user home.",
            fix_suggestion="Create ~/.codex first, then rerun the sync command.",
            validation_command=validation_command,
        )

    runtime_reports: list[dict[str, Any]] = []
    try:
        for profile_home in profile_homes:
            canonical_runtime_root = profile_home / "plugins"
            for relative_root in _LOCAL_PLUGIN_ROOTS:
                runtime_root = profile_home / relative_root
                if relative_root != "plugins" and canonical_runtime_root.exists() and runtime_root.exists():
                    try:
                        same_runtime_root = runtime_root.samefile(canonical_runtime_root)
                    except OSError:
                        same_runtime_root = False
                    if same_runtime_root:
                        runtime_reports.append(
                            {
                                "runtime_root": str(runtime_root),
                                "marketplace_target": str(runtime_root / "marketplace.json"),
                                "planned_plugins": [str(entry["name"]) for entry in entries],
                                "copied_plugins": [],
                                "symlinked_plugins": [],
                                "skipped_plugins": [str(entry["name"]) for entry in entries],
                                "removed_entries": [],
                                "pruned_plugins": [],
                                "skipped_marketplace_copy": True,
                                "materializes_payload": False,
                                "skipped_samefile_runtime_root": True,
                                "dry_run": dry_run,
                            }
                        )
                        continue
                runtime_reports.append(
                    _sync_one_runtime_root(
                        runtime_root=runtime_root,
                        canonical_runtime_root=canonical_runtime_root,
                        repo_root=repo_root,
                        marketplace_path=marketplace_path,
                        marketplace_entries=entries,
                        dry_run=dry_run,
                    )
                )
        runtime_reports.append(
            _sync_one_runtime_root(
                runtime_root=repo_root / _REPO_PLUGIN_RUNTIME_CACHE_ROOT,
                repo_root=repo_root,
                marketplace_path=marketplace_path,
                marketplace_entries=entries,
                dry_run=dry_run,
            )
        )
        runtime_reports.append(
            _sync_personal_marketplace(
                home=home,
                repo_root=repo_root,
                marketplace_entries=entries,
                dry_run=dry_run,
            )
        )
    except OSError as exc:
        error_result = _runtime_error_result(
            f"Failed to sync local-plugin runtime mirrors: {exc}",
            fix_suggestion=(
                "Grant write access to the Codex plugin runtime mirror directories "
                "or rerun with --dry-run to inspect the planned writes."
            ),
            validation_command=validation_command,
        )
        error_result.data["profile_homes"] = [str(path) for path in profile_homes]
        error_result.data["plugin_names"] = [entry["name"] for entry in entries]
        error_result.data["runtime_reports"] = runtime_reports
        error_result.data["dry_run"] = dry_run
        return error_result

    result.status = "success"
    result.data["message"] = "Replaced local-plugin runtime mirrors."
    result.data["profile_homes"] = [str(path) for path in profile_homes]
    result.data["plugin_names"] = [entry["name"] for entry in entries]
    result.data["runtime_reports"] = runtime_reports
    result.data["dry_run"] = dry_run
    result.data["desktop_readiness_state"] = collect_plugin_state(repo_root)["desktop_readiness_state"]
    return result


def _extract_plugin_root_from_output(
    stdout: str,
    repo_root: Path,
    raw_name: str,
    *,
    fallback_parent: str = f"Plugins/{_DEFAULT_PLUGIN_CATEGORY}",
) -> Path:
    """
    Derives the absolute plugin root path from scaffold creator output or computes a fallback under the repository.

    Parameters:
        stdout (str): Captured stdout from the plugin creator script; may contain a scaffold summary with the created path.
        repo_root (Path): Repository root used to resolve relative created paths and to construct fallback locations.
        raw_name (str): Original plugin name provided to the creator; used (after normalization) as the final path segment when falling back.
        fallback_parent (str): Repository-relative parent under which to place the fallback plugin folder (default: "Plugins/third-party").

    Returns:
        Path: Absolute path to the plugin root extracted from output, or the computed fallback path under `repo_root`.
    """
    for line in stdout.splitlines():
        match = _SCAFFOLD_SUMMARY_RE.search(line.strip())
        if match:
            plugin_root = Path(match.group(1)).expanduser()
            if not plugin_root.is_absolute():
                plugin_root = repo_root / plugin_root
            return _to_absolute_path(plugin_root)
    normalized = _normalize_plugin_name(raw_name)
    fallback = normalized if normalized else raw_name.strip()
    return _to_absolute_path(repo_root / fallback_parent / fallback)


def _resolve_canonical_plugin_dest(repo_root: Path, dest: str) -> tuple[Path, str]:
    dest_token = (dest or f"Plugins/{_DEFAULT_PLUGIN_CATEGORY}").strip() or f"Plugins/{_DEFAULT_PLUGIN_CATEGORY}"
    raw_dest = Path(dest_token)
    if raw_dest.is_absolute():
        raise ValueError("Destination must be repo-relative (for example: Plugins/third-party).")

    resolved_root = repo_root.resolve()
    resolved_dest = (repo_root / raw_dest).resolve()
    try:
        rel_dest = resolved_dest.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("Destination escapes repository root.") from exc

    rel_parts = rel_dest.parts
    if len(rel_parts) == 1:
        rel_dest = Path("Plugins") / rel_dest
        resolved_dest = (repo_root / rel_dest).resolve()
        rel_parts = rel_dest.parts

    if len(rel_parts) != 2 or rel_parts[0] != "Plugins":
        raise ValueError("Destination must be under Plugins/<category>.")
    if resolved_dest.exists() and not resolved_dest.is_dir():
        raise ValueError("Destination must resolve to a directory under repository root.")
    return resolved_dest, rel_dest.as_posix()


def list_plugins_state(repo_root: Path) -> CallResult:
    """
    Retrieve a snapshot of the repository's plugin lifecycle state.

    Returns:
        CallResult: status set to "success" and `data` populated with the plugin state snapshot obtained from the repository.
    """
    result = CallResult()
    result.data["validation_commands"] = [_plugin_validation_command("list")]
    snapshot = collect_plugin_state(repo_root)
    result.status = "success"
    result.data.update(snapshot)
    return result


def status_plugin_state(repo_root: Path, name: str) -> CallResult:
    """Return read-only lifecycle state for a single plugin."""
    result = CallResult()
    result.data["validation_commands"] = [_plugin_validation_command("status", name)]
    snapshot = collect_plugin_state(repo_root, plugin_name=name)
    plugins = snapshot["installed_state"]["plugins"]
    if not plugins:
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_VALIDATION",
                message=f"Plugin '{name}' was not found in installed state.",
                fix_suggestion="Run `ask plugins list` to inspect available plugin names.",
            )
        )
        return result
    result.status = "success"
    result.data.update(snapshot)
    return result


def doctor_plugins_state(repo_root: Path) -> CallResult:
    """
    Run plugin health diagnostics and return a CallResult containing the diagnostic snapshot.

    Populates result.data with the collected snapshot from the plugin state doctor. If the snapshot's health_state.status is "healthy" the result.status is set to "success". If not healthy, result.status is set to "error", result.data["operator_action"] is set to instruct inspection of data.health_state.blockers, and an ErrorObject with code "ERR_VALIDATION" and a fix suggestion is appended to result.errors.

    Returns:
        CallResult: The call result containing the diagnostic snapshot and status.
    """
    result = CallResult()
    result.data["validation_commands"] = [_plugin_validation_command("doctor")]
    snapshot = collect_plugin_state(repo_root, run_doctor=True)
    result.data.update(snapshot)
    if snapshot["health_state"]["status"] == "healthy":
        result.status = "success"
        return result

    result.data["operator_action"] = "Inspect data.health_state.blockers and resolve failing checks before retrying."
    result.status = "error"
    result.errors.append(
        ErrorObject(
            code="ERR_VALIDATION",
            message="Plugin doctor detected lifecycle blockers.",
            fix_suggestion="Inspect data.health_state.blockers and resolve the listed checks.",
        )
    )
    return result


def init_plugin(
    repo_root: Path,
    name: str,
    category: str = _DEFAULT_PLUGIN_CATEGORY,
    with_marketplace: bool = False,
    companion_folders: Optional[List[str]] = None,
    action: str = "init",
) -> CallResult:
    """
    Create a new plugin scaffold in the repository.

    Initialises a plugin scaffold by invoking the repository's creator script and, when requested, creates additional companion folders that are not handled by the creator.

    Parameters:
        repo_root (Path): Path to the repository root where the creator script is resolved and executed.
        name (str): Name to give the new plugin (used by the creator script and for fallback paths).
        category (str): Canonical plugin category under Plugins/ where the plugin will be created.
        with_marketplace (bool): If true, instruct the creator script to include marketplace-related scaffolding.
        companion_folders (Optional[List[str]]): Optional list of companion folder types to include. Values must be in the allowed companion-folder set; some types are passed to the creator as `--with-<folder>` flags while others are created manually under the generated plugin root.

    Returns:
        CallResult: Result object with `status` set to `"success"` or `"error"`. On success, `data` contains:
            - `message`: short success message
            - `raw_output`: stdout from the creator script
            - `plugin_root`: absolute path to the created plugin directory
            - `created_manual_folders`: list of paths for any companion folders created manually
        On error, `errors` contains one or more ErrorObject entries and `data` may include `raw_output` and `raw_error`.
    """
    result = CallResult()
    result.data["validation_commands"] = [
        _plugin_init_validation_command(
            name,
            category=category,
            with_marketplace=with_marketplace,
            companion_folders=companion_folders,
            action=action,
        )
    ]
    try:
        parent_path, canonical_parent = _resolve_canonical_plugin_dest(repo_root, category)
    except ValueError as exc:
        return _validation_error_result(
            f"Invalid plugin category '{category}': {exc}",
            fix_suggestion=f"Use a category under Plugins/, for example: Plugins/{_DEFAULT_PLUGIN_CATEGORY}.",
            validation_command=_plugin_init_validation_command(
                name,
                category=category,
                with_marketplace=with_marketplace,
                companion_folders=companion_folders,
                action=action,
            ),
        )

    if companion_folders:
        invalid = [f for f in companion_folders if f not in _ALLOWED_COMPANION_FOLDERS]
        if invalid:
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message=f"Invalid companion folder(s): {invalid}. Allowed: {sorted(_ALLOWED_COMPANION_FOLDERS)}",
                    fix_suggestion=f"Use only allowed folder types: {', '.join(sorted(_ALLOWED_COMPANION_FOLDERS))}",
                )
            )
            return result

    creator_script, resolve_error = _resolve_script_path_or_runtime_error(
        repo_root,
        _PLUGIN_CREATOR_SCRIPT_CANDIDATES,
        fix_suggestion=(
            "Ensure plugin-creator sources are available in either "
            "Skills/ or Plugins/plugin-factory/."
        ),
    )
    if resolve_error:
        resolve_error.data["validation_commands"] = result.data["validation_commands"]
        return resolve_error
    assert creator_script is not None

    cmd = ["python3", str(creator_script), name, "--path", str(parent_path)]

    if with_marketplace:
        cmd.append("--with-marketplace")

    manual_folders: list[str] = []
    if companion_folders:
        for folder in companion_folders:
            if folder in _CREATOR_FLAG_FOLDERS:
                cmd.append(f"--with-{folder}")
            elif folder in _MANUAL_COMPANION_FOLDERS:
                manual_folders.append(folder)

    process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, check=False)

    if process.returncode == 0:
        plugin_root = _extract_plugin_root_from_output(
            process.stdout,
            repo_root,
            name,
            fallback_parent=canonical_parent,
        )
        plugin_root_missing = not plugin_root.is_dir()
        if plugin_root_missing:
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_RUNTIME",
                    message=f"Plugin creator did not materialize a scaffold at '{plugin_root}'.",
                    fix_suggestion="Inspect creator output and retry with a valid plugin name/path.",
                )
            )
            result.data["raw_output"] = process.stdout
            result.data["raw_error"] = process.stderr
            return result
        created_manual_folders: list[str] = []
        for folder in manual_folders:
            target = plugin_root / folder
            target.mkdir(parents=True, exist_ok=True)
            created_manual_folders.append(str(target))
        result.status = "success"
        result.data["message"] = f"Initialized plugin '{name}'"
        result.data["raw_output"] = process.stdout
        result.data["plugin_root"] = str(plugin_root)
        result.data["canonical_dest"] = canonical_parent
        result.data["created_manual_folders"] = created_manual_folders
        return result

    result.status = "error"
    result.errors.append(ErrorObject(code="ERR_RUNTIME", message=process.stderr.strip() or "Plugin init failed."))
    result.data["raw_output"] = process.stdout
    result.data["raw_error"] = process.stderr
    return result


def install_plugin(
    repo_root: Path,
    url: str,
    plugin_path: str,
    *,
    name: Optional[str] = None,
    ref: Optional[str] = None,
    dest: str = "Plugins/third-party",
    validation_level: str = "compat",
    allow_untrusted_source: bool = False,
    allow_unpinned_ref: bool = False,
    sync_profile: bool = False,
    require_desktop_loadable: bool = False,
    dry_run: bool = False,
    action: str = "install",
) -> CallResult:
    """
    Install a plugin from a remote repository into this repository's Plugins area.
    
    Parameters:
        repo_root (Path): Repository root used to resolve installer scripts and repo-relative destinations.
        url (str): Remote repository or archive URL to install from.
        plugin_path (str): Path inside the remote repository that contains the plugin (repository-relative).
        name (Optional[str]): Explicit install name; if omitted the installer-derived name will be used.
        ref (Optional[str]): Git reference (branch, tag, commit) to check out from the source.
        dest (str): Destination directory relative to `repo_root` (must be under `Plugins/<category>`).
        validation_level (str): Validation strictness passed to the installer (e.g. "compat").
        allow_untrusted_source (bool): Permit installation from an untrusted source.
        allow_unpinned_ref (bool): Permit installing from an unpinned ref.
        sync_profile (bool): If true, sync local runtime plugin profiles after a successful install.
        require_desktop_loadable (bool): If true, treat a plugin that is not desktop-loadable after install as an error.
        dry_run (bool): If true, do not run the installer and instead return a best-effort plan and next-step command.
        action (str): Installer action verb used when building the validation command (default "install").
    
    Returns:
        CallResult: Result with `status` set to "success" or "error".
          - On dry-run: `data` contains `dry_run`, `url`, `plugin_path`, `plugin_name`, `target_path` (best-effort), `canonical_dest`, `validation_commands`, `sync_profile`, `require_desktop_loadable`, and `metadata["next_steps"]`.
          - On success: `data` contains `message`, `plugin_name` (when determined), `target_path` (when reported by installer), `raw_output`, `raw_error`, `canonical_dest`, plugin cache refresh info, optional `profile_sync`, and `desktop_readiness_state` / `desktop_loadable`.
          - On failure: `errors` includes an `ERR_RUNTIME` error with installer stderr; if an explicit `--name` conflicts with an existing path, `errors` includes `ERR_CONFLICT`.
    """
    result = CallResult()
    validation_command = _plugin_install_validation_command(
        url,
        plugin_path,
        name=name,
        ref=ref,
        dest=dest,
        validation_level=validation_level,
        allow_untrusted_source=allow_untrusted_source,
        allow_unpinned_ref=allow_unpinned_ref,
        sync_profile=sync_profile,
        require_desktop_loadable=require_desktop_loadable,
        dry_run=dry_run,
        action=action,
    )
    result.data["validation_commands"] = [validation_command]

    try:
        dest_path, canonical_dest = _resolve_canonical_plugin_dest(repo_root, dest)
    except ValueError as exc:
        return _validation_error_result(
            f"Invalid plugin destination '{dest}': {exc}",
            fix_suggestion="Use a destination under Plugins/<category>, for example Plugins/third-party.",
            validation_command=validation_command,
        )
    requested_name = (name or "").strip() or None
    target_path = dest_path / requested_name if requested_name else None

    if dry_run:
        result.status = "success"
        result.data["dry_run"] = True
        result.data["url"] = url
        result.data["plugin_path"] = plugin_path
        result.data["plugin_name"] = requested_name or "unknown"
        result.data["validation_commands"] = [validation_command]
        if target_path is not None:
            try:
                result.data["target_path"] = str(target_path.relative_to(repo_root))
            except ValueError:
                result.data["target_path"] = str(target_path)
        else:
            result.data["target_path"] = "unknown"
        next_step = f"ask plugins install {url} --path {plugin_path} --dest {canonical_dest}"
        if ref:
            next_step += f" --ref {ref}"
        result.metadata["next_steps"] = [next_step]
        result.data["canonical_dest"] = canonical_dest
        result.data["sync_profile"] = sync_profile
        result.data["require_desktop_loadable"] = require_desktop_loadable
        return result

    # Resolve installer helper only when actually running the installer
    installer_script, resolve_error = _resolve_script_path_or_runtime_error(
        repo_root,
        _PLUGIN_INSTALLER_SCRIPT_CANDIDATES,
        fix_suggestion=(
            "Ensure plugin-installer sources are available in either "
            "Skills/ or Plugins/plugin-factory/."
        ),
    )
    if resolve_error:
        resolve_error.data["validation_commands"] = [validation_command]
        return resolve_error
    assert installer_script is not None

    # If --name is explicit we can preflight destination conflict. Otherwise
    # installer-derived manifest name is authoritative and conflict checks must
    # run after that name is resolved by the installer.
    if target_path is not None and target_path.exists():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_CONFLICT",
                message=f"Plugin '{requested_name}' already exists at '{target_path}'.",
                fix_suggestion="Choose a different --name/--dest or remove the existing plugin first.",
            )
        )
        return result

    cmd = [
        "python3",
        str(installer_script),
        "--url",
        url,
        "--path",
        plugin_path,
        "--dest",
        str(dest_path),
        "--validation-level",
        validation_level,
    ]

    if requested_name:
        cmd.extend(["--name", requested_name])
    if ref:
        cmd.extend(["--ref", ref])
    if allow_untrusted_source:
        cmd.append("--allow-untrusted-source")
    if allow_unpinned_ref:
        cmd.append("--allow-unpinned-ref")

    process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, check=False)
    result.data["raw_output"] = process.stdout
    result.data["raw_error"] = process.stderr
    result.data["canonical_dest"] = canonical_dest

    if process.returncode == 0:
        installed_name = requested_name
        installed_path: Optional[str] = None
        for line in process.stdout.splitlines():
            match = _INSTALL_SUMMARY_RE.search(line.strip())
            if match:
                installed_name = match.group(1)
                installed_path = match.group(2).strip()
                break

        result.status = "success"
        if installed_name:
            result.data["message"] = f"Installed plugin '{installed_name}'"
            result.data["plugin_name"] = installed_name
            _sync_plugin_config(installed_name, enable=True)
        else:
            result.data["message"] = "Installed plugin."
        if installed_path:
            result.data["target_path"] = installed_path
        cache_plan: dict[str, Any] = {}
        cache_logs: list[str] = []
        cache_error = refresh_workspace_plugin_caches(cache_plan, cache_logs, repo_root, dry_run=False)
        result.data["plugin_cache_refresh"] = cache_plan.get("plugin_cache_refresh", {})
        result.data["plugin_cache_logs"] = cache_logs
        if cache_error is not None:
            result.data["plugin_cache_error"] = {
                "code": cache_error.code,
                "message": cache_error.message,
                "fix_suggestion": cache_error.fix_suggestion,
            }
        if sync_profile:
            sync_result = sync_local_runtime_plugins(repo_root, dry_run=False)
            result.data["profile_sync"] = {
                "status": sync_result.status,
                "data": sync_result.data,
                "errors": [
                    {
                        "code": error.code,
                        "message": error.message,
                        "fix_suggestion": error.fix_suggestion,
                    }
                    for error in sync_result.errors
                ],
            }
            if sync_result.status != "success" or sync_result.errors:
                result.status = "error"
                # Construct ErrorObject for top-level error collection
                error_message = sync_result.message if hasattr(sync_result, 'message') and sync_result.message else "Profile sync failed"
                if sync_result.errors:
                    error_details = "; ".join([
                        f"{e.message}" for e in sync_result.errors
                    ])
                    error_message = f"{error_message}: {error_details}"
                result.errors.append(ErrorObject(
                    code="ERR_PROFILE_SYNC",
                    message=error_message
                ))
        if installed_name:
            readiness = collect_plugin_state(repo_root, plugin_name=installed_name)["desktop_readiness_state"]
        else:
            readiness = collect_plugin_state(repo_root)["desktop_readiness_state"]
        result.data["desktop_readiness_state"] = readiness
        result.data["desktop_loadable"] = bool(readiness.get("desktop_loadable"))
        if require_desktop_loadable and not result.data["desktop_loadable"]:
            result.status = "error"
            result.errors.append(
                ErrorObject(
                    code="ERR_VALIDATION",
                    message="Plugin installed, but Codex Desktop readiness is blocked.",
                    fix_suggestion="Inspect data.desktop_readiness_state.blockers and run the listed repair commands.",
                )
            )
        return result

    result.status = "error"
    result.errors.append(ErrorObject(code="ERR_RUNTIME", message=process.stderr.strip() or "Plugin installation failed."))
    return result


def harden_plugin(
    repo_root: Path,
    plugin_path: str,
    *,
    require_marketplace: bool = True,
    marketplace_path: str = "Plugins/marketplace.json",
    run_compat: bool = True,
    run_marketplace_audit: bool = True,
    allow_legacy_marketplace_path: bool = True,
) -> CallResult:
    """
    Run the plugin hardening steps (validate, optional compatibility audit, optional marketplace audit) for a plugin package.

    Parameters:
        repo_root (Path): Repository root used as the working directory and base for resolving relative paths.
        plugin_path (str): Path to the plugin package; may be absolute or relative to `repo_root`.
        require_marketplace (bool): If true, pass `--require-marketplace` to the validate step to require a marketplace entry.
        marketplace_path (str): Path to the marketplace JSON file; may be absolute or relative to `repo_root`.
        run_compat (bool): If true, run the `audit-compat` compatibility audit step.
        run_marketplace_audit (bool): If true, run the `audit-marketplace` step against the repository plugins list.
        allow_legacy_marketplace_path (bool): If true, allow legacy marketplace path behaviour by adding the corresponding flag to builder commands.

    Returns:
        CallResult: On success, status is `"success"` and `data` contains:
            - `message`: human-readable confirmation including the plugin name,
            - `plugin_path`: the resolved absolute plugin path,
            - `command_runs`: list of executed commands with their stdout/stderr and return codes.
        On failure, status is `"error"`, `errors` includes an `ERR_RUNTIME` entry describing the failing step, and `data["command_runs"]` contains the recorded command outputs for diagnosis.
    """
    validation_command = _plugin_harden_validation_command(
        plugin_path,
        require_marketplace=require_marketplace,
        marketplace_path=marketplace_path,
        run_compat=run_compat,
        run_marketplace_audit=run_marketplace_audit,
        allow_legacy_marketplace_path=allow_legacy_marketplace_path,
    )
    builder_script, resolve_error = _resolve_script_path_or_runtime_error(
        repo_root,
        _PLUGIN_BUILDER_SCRIPT_CANDIDATES,
        fix_suggestion=(
            "Restore the Plugin Factory hardening implementation under "
            "Plugins/plugin-factory/scripts/plugin-builder/ or route through plugin-factory-router."
        ),
    )
    if resolve_error:
        resolve_error.data["validation_commands"] = [validation_command]
        return resolve_error
    assert builder_script is not None

    plugin_root = Path(plugin_path)
    if not plugin_root.is_absolute():
        plugin_root = _to_absolute_path(repo_root / plugin_root)

    if not plugin_root.is_dir():
        return _validation_error_result(
            f"Plugin path '{plugin_root}' is not a directory.",
            fix_suggestion="Pass a valid plugin directory path (for example: Plugins/<name>).",
            validation_command=validation_command,
        )

    marketplace = Path(marketplace_path)
    if not marketplace.is_absolute():
        marketplace = _to_absolute_path(repo_root / marketplace)

    command_runs: list[dict[str, str]] = []

    def _run(command: list[str], step: str) -> bool:
        """
        Record and run a shell command step, appending its execution details to `command_runs`.

        Parameters:
        	command (list[str]): Command and arguments to execute (executable first element).
        	step (str): Short identifier for the step recorded alongside the command output.

        Returns:
        	bool: `True` if the command exited with code 0, `False` otherwise.
        """
        process = subprocess.run(command, cwd=str(repo_root), capture_output=True, text=True, check=False)
        command_runs.append(
            {
                "step": step,
                "command": " ".join(command),
                "returncode": str(process.returncode),
                "stdout": process.stdout,
                "stderr": process.stderr,
            }
        )
        return process.returncode == 0

    validate_cmd = [
        "python3",
        str(builder_script),
        "validate",
        str(plugin_root),
        "--marketplace-path",
        str(marketplace),
    ]
    if require_marketplace:
        validate_cmd.append("--require-marketplace")
    if allow_legacy_marketplace_path:
        validate_cmd.append("--allow-legacy-marketplace-path")
    def _fail(step_name: str) -> CallResult:
        """
        Create a CallResult representing a runtime failure for the given hardening step.

        The returned result has `status` set to `"error"`, contains a single `ErrorObject` with code `ERR_RUNTIME` and a message identifying the failing step, and includes the `command_runs` list under `data["command_runs"]`.

        Parameters:
            step_name (str): Name of the hardening step that failed.

        Returns:
            CallResult: A failure result populated with an `ERR_RUNTIME` error and the recorded command runs.
        """
        failure = CallResult()
        failure.status = "error"
        failure.data["validation_commands"] = [validation_command]
        failure.errors.append(
            ErrorObject(
                code="ERR_RUNTIME",
                message=f"Plugin hardening failed during {step_name} step.",
                fix_suggestion="Inspect data.command_runs for the failing command output.",
            )
        )
        failure.data["command_runs"] = command_runs
        return failure

    if not _run(validate_cmd, "validate"):
        return _fail("validate")

    if run_compat:
        compat_cmd = [
            "python3",
            str(builder_script),
            "audit-compat",
            str(plugin_root),
            "--marketplace-path",
            str(marketplace),
        ]
        if allow_legacy_marketplace_path:
            compat_cmd.append("--allow-legacy-marketplace-path")
        if not _run(compat_cmd, "audit-compat"):
            return _fail("audit-compat")

    if run_marketplace_audit:
        plugins_parent = plugin_root.parent
        marketplace_cmd = [
            "python3",
            str(builder_script),
            "audit-marketplace",
            "--marketplace-path",
            str(marketplace),
            "--plugins-path",
            str(plugins_parent),
        ]
        if allow_legacy_marketplace_path:
            marketplace_cmd.append("--allow-legacy-marketplace-path")
        if not _run(marketplace_cmd, "audit-marketplace"):
            return _fail("audit-marketplace")

    result = CallResult()
    result.status = "success"
    result.data["validation_commands"] = [validation_command]
    result.data["message"] = f"Hardened plugin '{plugin_root.name}'"
    result.data["plugin_path"] = str(plugin_root)
    result.data["command_runs"] = command_runs
    return result


def _sync_plugin_config(plugin_name: str, enable: bool = True, remove: bool = False) -> bool:
    """Sync a plugin's auto-registration state natively in ~/.codex/config.toml."""
    import re
    config_path = os.path.expanduser("~/.codex/config.toml")
    if not os.path.exists(config_path):
        return False
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()

        regex = r'(\[plugins\."' + re.escape(plugin_name) + r'@[^"]+"\]\n\s*enabled\s*=\s*)(true|false)(\n?)'
        pattern = re.compile(regex)

        if remove:
            remove_regex = r'\[plugins\."' + re.escape(plugin_name) + r'@[^"]+"\]\n\s*enabled\s*=\s*(?:true|false)\n?'
            new_content, count = re.subn(remove_regex, '', content)
            if count > 0:
                with open(config_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                return True
            return False

        if pattern.search(content):
            rep = 'true' if enable else 'false'
            new_content = pattern.sub(rf'\g<1>{rep}\g<3>', content)
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True
        else:
            rep = 'true' if enable else 'false'
            with open(config_path, "a", encoding="utf-8") as f:
                f.write(f'\n[plugins."{plugin_name}@agent-skills-local"]\nenabled = {rep}\n')
            return True
    except OSError as exc:
        import sys
        print(f"Warning: Failed to sync config.toml for plugin '{plugin_name}': {exc}", file=sys.stderr)
    return False


def uninstall_plugin(repo_root: Path, name: str, *, dry_run: bool = False) -> CallResult:
    """Safely uninstalls a plugin by removing its directory and syncing config.toml."""
    import shutil
    import subprocess
    result = CallResult()
    validation_command = _plugin_validation_command("uninstall", name, dry_run=dry_run)
    result.data["validation_commands"] = [validation_command]

    plugins_dir = repo_root / "Plugins"
    if not plugins_dir.exists():
        return _validation_error_result(
            "Plugins/ directory does not exist.",
            fix_suggestion="Ensure you are running the command from the root of a valid skills repository.",
            validation_command=validation_command,
        )

    found_path = None
    direct_path = plugins_dir / name
    if direct_path.is_dir():
        found_path = direct_path

    # Try to locate categorized plugins (e.g. third-party/demo-plugin, github/demo-plugin).
    for category in plugins_dir.iterdir():
        if found_path is None and category.is_dir() and (category / name).is_dir():
            found_path = category / name
            break

    if not found_path:
        return _validation_error_result(
            f"Plugin '{name}' not found under Plugins/.",
            fix_suggestion="Use 'ask plugins list' to check installed plugins.",
            validation_command=validation_command,
        )

    if dry_run:
        result.status = "success"
        result.metadata["next_steps"] = [f"ask plugins uninstall {name}"]
        result.data["dry_run"] = True
        result.data["plugin_name"] = name
        result.data["target_path"] = str(found_path.relative_to(repo_root))
        return result

    # Check if tracked by git to properly remove
    git_check = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(found_path)],
        cwd=repo_root, capture_output=True
    )

    if git_check.returncode == 0:
        cmd = ["git", "rm", "-r", "--quiet", str(found_path)]
        process = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
        if process.returncode != 0:
            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_RUNTIME",
                message=f"Git rm failed: {process.stderr}",
                fix_suggestion="Manually remove directory."
            ))
            return result
    else:
        try:
            shutil.rmtree(found_path)
        except OSError as exc:
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_RUNTIME", message=f"Failed to delete {found_path}: {exc}"))
            return result

    # Config sync after file removal
    sync_ok = _sync_plugin_config(name, remove=True)

    result.status = "success"
    msg = f"Uninstalled plugin '{name}'."
    if sync_ok:
        msg += " Registration removed from config.toml."
    result.data["message"] = msg
    result.data["plugin_name"] = name
    result.data["target_path"] = str(found_path.relative_to(repo_root))

    # Let user know to run validation for global parity (like baseline.json sync)
    result.metadata["next_steps"] = ["ask repo validate"]
    return result
