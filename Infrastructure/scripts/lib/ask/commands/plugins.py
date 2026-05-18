import subprocess
import re
import os
import json
import shutil
from pathlib import Path
from typing import Any, List, Optional

from ask.envelope import CallResult, ErrorObject
from ask.plugin_state import collect_plugin_state
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
    "Plugins/plugin-factory/skills/code_quality_review/plugin-builder/scripts/plugin_builder.py",
)
_LOCAL_PLUGIN_ROOTS = ("Plugins", "plugins", ".agents/plugins")


def _to_absolute_path(path: Path) -> Path:
    """
    Return an absolute Path with '~' expanded while preserving symlinks.
    
    Returns:
        Path: Absolute path with the user home expanded; symbolic links are not resolved.
    """
    return Path(path.expanduser()).absolute()


def _runtime_error_result(message: str, *, fix_suggestion: str) -> CallResult:
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
    result.errors.append(
        ErrorObject(
            code="ERR_RUNTIME",
            message=message,
            fix_suggestion=fix_suggestion,
        )
    )
    return result


def _validation_error_result(message: str, *, fix_suggestion: str) -> CallResult:
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
    result.errors.append(
        ErrorObject(
            code="ERR_VALIDATION",
            message=message,
            fix_suggestion=fix_suggestion,
        )
    )
    return result


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


def _sync_one_runtime_root(
    *,
    runtime_root: Path,
    repo_root: Path,
    marketplace_path: Path,
    marketplace_entries: list[dict[str, Any]],
    dry_run: bool,
) -> dict[str, Any]:
    """
    Replaces local plugin runtime mirrors from the repository's local marketplace entries.

    Replaces only the repository-local plugins listed in `marketplace_entries`
    inside `runtime_root`. Non-local plugin cache entries are preserved. Stale
    local mirrors (directories bearing the `.codex-repo-plugin-source` marker)
    that are no longer declared in `marketplace_entries` are removed. When
    `dry_run` is True no filesystem mutations are performed; a report of
    planned/copied/replaced/pruned names is still returned.

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
    removed_entries: list[str] = []
    pruned_plugins: list[str] = []
    marketplace_target = runtime_root / "marketplace.json"
    marker_name = ".codex-repo-plugin-source"

    resolved_sources: list[tuple[str, Path]] = []
    for entry in marketplace_entries:
        plugin_name = entry["name"]
        relative = entry["path"]
        source_dir = repo_root / relative.removeprefix("./")
        if not source_dir.is_dir():
            raise FileNotFoundError(f"Local plugin source missing for '{plugin_name}': {source_dir}")
        resolved_sources.append((plugin_name, source_dir))

    if not dry_run:
        shutil.copy2(marketplace_path, marketplace_target)

    keep_names = {plugin_name for plugin_name, _ in resolved_sources}
    for plugin_name, source_dir in resolved_sources:
        planned_plugins.append(plugin_name)
        target_dir = runtime_root / plugin_name
        if target_dir.exists() or target_dir.is_symlink():
            removed_entries.append(plugin_name)
        if not dry_run:
            _copy_directory_contents(source_dir, target_dir)
            _materialize_first_level_skill_aliases(target_dir)
            (target_dir / marker_name).write_text(str(source_dir.resolve()) + "\n", encoding="utf-8")
            copied_plugins.append(plugin_name)

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
        "removed_entries": removed_entries,
        "pruned_plugins": pruned_plugins,
        "dry_run": dry_run,
    }


def sync_local_runtime_plugins(repo_root: Path, *, dry_run: bool = False) -> CallResult:
    """
    Replaces repository-local plugin runtime mirrors in each Codex profile from canonical `Plugins/` sources.

    Use this after changing or updating any local plugin source or
    `Plugins/marketplace.json`. Runtime plugin mirrors are copied directories,
    not symlinks, so they must be replaced to make plugin changes visible.
    
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
    try:
        marketplace_path, entries = _load_local_marketplace(repo_root)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        return _runtime_error_result(
            str(exc),
            fix_suggestion="Ensure Plugins/marketplace.json exists and contains valid local plugin entries.",
        )

    if not entries:
        return _validation_error_result(
            "No local plugins were found in Plugins/marketplace.json.",
            fix_suggestion="Add local plugin entries before replacing runtime mirrors.",
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
        )

    runtime_reports: list[dict[str, Any]] = []
    for profile_home in profile_homes:
        for relative_root in _LOCAL_PLUGIN_ROOTS:
            runtime_root = profile_home / relative_root
            runtime_reports.append(
                _sync_one_runtime_root(
                    runtime_root=runtime_root,
                    repo_root=repo_root,
                    marketplace_path=marketplace_path,
                    marketplace_entries=entries,
                    dry_run=dry_run,
                )
            )

    result.status = "success"
    result.data["message"] = "Replaced local-plugin runtime mirrors."
    result.data["profile_homes"] = [str(path) for path in profile_homes]
    result.data["plugin_names"] = [entry["name"] for entry in entries]
    result.data["runtime_reports"] = runtime_reports
    result.data["dry_run"] = dry_run
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
    snapshot = collect_plugin_state(repo_root)
    result.status = "success"
    result.data.update(snapshot)
    return result


def status_plugin_state(repo_root: Path, name: str) -> CallResult:
    """Return read-only lifecycle state for a single plugin."""
    result = CallResult()
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
    try:
        parent_path, canonical_parent = _resolve_canonical_plugin_dest(repo_root, category)
    except ValueError as exc:
        return _validation_error_result(
            f"Invalid plugin category '{category}': {exc}",
            fix_suggestion=f"Use a category under Plugins/, for example: Plugins/{_DEFAULT_PLUGIN_CATEGORY}.",
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
    dry_run: bool = False,
) -> CallResult:
    """
    Install a plugin from a GitHub repository into the repo's plugins area using the resolved plugin-installer script.
    
    Parameters:
        repo_root (Path): Repository root used to resolve scripts and relative destinations.
        url (str): GitHub repository URL or archive location to install from.
        plugin_path (str): Path inside the repository at `url` that contains the plugin (repository-relative).
        name (Optional[str]): Explicit name to install the plugin as; if omitted the installer-derived name is used.
        ref (Optional[str]): Git reference (branch, tag, commit) to check out from the source repository.
        dest (str): Destination directory (relative to `repo_root`) where the plugin will be installed.
        validation_level (str): Validation strictness passed to the installer (e.g. "compat").
        allow_untrusted_source (bool): Allow installing from an untrusted source; passed through to the installer.
        allow_unpinned_ref (bool): Allow installing an unpinned ref; passed through to the installer.
        dry_run (bool): If true, do not run the installer; return a best-effort plan including a suggested next-step command.
    
    Returns:
        CallResult: Result with `status` set to "success" or "error".
          - On dry-run: `data` includes `dry_run`, `url`, `plugin_path`, `plugin_name`, `target_path` and `metadata["next_steps"]`.
          - On successful install: `data` includes `message`, `plugin_name` (if determined), `target_path` (if captured), `raw_output`, and `raw_error`.
          - On failure: `errors` contains an `ERR_RUNTIME` error with installer stderr; if an explicit `--name` conflicts with an existing path, `errors` contains `ERR_CONFLICT`.
    """
    result = CallResult()

    try:
        dest_path, canonical_dest = _resolve_canonical_plugin_dest(repo_root, dest)
    except ValueError as exc:
        return _validation_error_result(
            f"Invalid plugin destination '{dest}': {exc}",
            fix_suggestion="Use a destination under Plugins/<category>, for example Plugins/third-party.",
        )
    requested_name = (name or "").strip() or None
    target_path = dest_path / requested_name if requested_name else None

    if dry_run:
        result.status = "success"
        result.data["dry_run"] = True
        result.data["url"] = url
        result.data["plugin_path"] = plugin_path
        result.data["plugin_name"] = requested_name or "unknown"
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
        return result

    result.status = "error"
    result.errors.append(ErrorObject(code="ERR_RUNTIME", message=process.stderr.strip() or "Plugin installation failed."))
    return result


def harden_plugin(
    repo_root: Path,
    plugin_path: str,
    *,
    require_marketplace: bool = True,
    marketplace_path: str = ".agents/Plugins/marketplace.json",
    run_compat: bool = True,
    run_marketplace_audit: bool = True,
    allow_legacy_marketplace_path: bool = True,
) -> CallResult:
    """
    Run the plugin-builder hardening steps (validate, optional compatibility audit, optional marketplace audit) for a plugin package.
    
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
    builder_script, resolve_error = _resolve_script_path_or_runtime_error(
        repo_root,
        _PLUGIN_BUILDER_SCRIPT_CANDIDATES,
        fix_suggestion=(
            "Ensure plugin-builder sources are available in either "
            "Skills/ or Plugins/plugin-factory/."
        ),
    )
    if resolve_error:
        return resolve_error
    assert builder_script is not None

    plugin_root = Path(plugin_path)
    if not plugin_root.is_absolute():
        plugin_root = _to_absolute_path(repo_root / plugin_root)

    if not plugin_root.is_dir():
        return _validation_error_result(
            f"Plugin path '{plugin_root}' is not a directory.",
            fix_suggestion="Pass a valid plugin directory path (for example: Plugins/<name>).",
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

    plugins_dir = repo_root / "Plugins"
    if not plugins_dir.exists():
        return _validation_error_result(
            "Plugins/ directory does not exist.", 
            fix_suggestion="Ensure you are running the command from the root of a valid skills repository."
        )

    # Try to locate the plugin in any category (e.g., third-party, github)
    found_path = None
    for category in plugins_dir.iterdir():
        if category.is_dir() and (category / name).is_dir():
            found_path = category / name
            break

    if not found_path:
        return _validation_error_result(
            f"Plugin '{name}' not found under Plugins/.",
            fix_suggestion="Use 'ask plugins list' to check installed plugins."
        )

    if dry_run:
        result.status = "success"
        result.metadata["next_steps"] = [f"ask plugins uninstall {name}"]
        result.data["dry_run"] = True
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
