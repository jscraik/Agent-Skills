import subprocess
import re
from pathlib import Path
from typing import List, Optional

from ask.envelope import CallResult, ErrorObject
from ask.plugin_state import collect_plugin_state

# Allow-list for companion folder types per plugin-creator contract
_ALLOWED_COMPANION_FOLDERS = {"skills", "hooks", "scripts", "assets", "mcp", "apps", "references", "workflows"}
_INSTALL_SUMMARY_RE = re.compile(r"Installed\s+([a-z0-9][a-z0-9-]{0,63})\s+to\s+(.+)")
_SCAFFOLD_SUMMARY_RE = re.compile(r"Created plugin scaffold:\s+(.+)")
_CREATOR_FLAG_FOLDERS = {"skills", "hooks", "scripts", "assets", "mcp", "apps"}
_MANUAL_COMPANION_FOLDERS = {"references", "workflows"}
_PLUGIN_NAME_SANITIZE_RE = re.compile(r"[^a-z0-9]+")

_PLUGIN_CREATOR_SCRIPT_CANDIDATES = (
    "Plugins/plugin-factory/skills/plugin-creator/scripts/create_basic_plugin.py",
    "Skills/plugin-creator/scripts/create_basic_plugin.py",
)
_PLUGIN_INSTALLER_SCRIPT_CANDIDATES = (
    "Plugins/plugin-factory/skills/plugin-installer/scripts/install-plugin-from-github.py",
    "Skills/plugin-installer/scripts/install-plugin-from-github.py",
)
_PLUGIN_BUILDER_SCRIPT_CANDIDATES = (
    "Plugins/plugin-factory/skills/plugin-builder/scripts/plugin_builder.py",
    "Skills/plugin-builder/scripts/plugin_builder.py",
)


def _to_absolute_path(path: Path) -> Path:
    """
    Convert a path to an absolute Path, expanding '~' while preserving symlinks.
    
    Returns:
        Absolute Path with the user-home expanded; symbolic links are not resolved.
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
    Normalise a raw plugin name to a filesystem- and URL-safe kebab-case identifier.
    
    Parameters:
        raw_name (str): Original plugin name provided by the user.
    
    Returns:
        normalized_name (str): The input lowercased, with any sequence of non-alphanumeric characters replaced by a single hyphen, leading/trailing hyphens removed, and repeated hyphens collapsed into one.
    """
    normalized = raw_name.strip().lower()
    normalized = _PLUGIN_NAME_SANITIZE_RE.sub("-", normalized).strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized


def _extract_plugin_root_from_output(stdout: str, repo_root: Path, raw_name: str) -> Path:
    """
    Determine the absolute plugin root path from a scaffold creator's stdout or fall back to a conventional plugins location.
    
    Scans each line of `stdout` for a scaffold summary that includes a created-path. If a created path is found, expands user home, resolves it relative to `repo_root` when necessary, and returns its absolute form. If no path is discovered in the output, returns `repo_root/Plugins/<name>` where `<name>` is the normalized `raw_name` when non-empty, otherwise the trimmed `raw_name`.
    
    Parameters:
        stdout (str): The captured stdout from the plugin creator script.
        repo_root (Path): Repository root used to resolve relative paths.
        raw_name (str): The original plugin name provided to the creator; used for fallback path construction.
    
    Returns:
        Path: Absolute path to the plugin root determined from output or the fallback location.
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
    return _to_absolute_path(repo_root / "plugins" / fallback)


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
    with_marketplace: bool = False,
    companion_folders: Optional[List[str]] = None,
) -> CallResult:
    """
    Create a new plugin scaffold in the repository.
    
    Initialises a plugin scaffold by invoking the repository's creator script and, when requested, creates additional companion folders that are not handled by the creator.
    
    Parameters:
        repo_root (Path): Path to the repository root where the creator script is resolved and executed.
        name (str): Name to give the new plugin (used by the creator script and for fallback paths).
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

    cmd = ["python3", str(creator_script), name]

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
        plugin_root = _extract_plugin_root_from_output(process.stdout, repo_root, name)
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

    dest_path = repo_root / dest
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
        next_step = f"ask plugins install {url} --path {plugin_path} --dest {dest}"
        if ref:
            next_step += f" --ref {ref}"
        result.metadata["next_steps"] = [next_step]
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
        marketplace_cmd = [
            "python3",
            str(builder_script),
            "audit-marketplace",
            "--marketplace-path",
            str(marketplace),
            "--plugins-path",
            str(_to_absolute_path(repo_root / "plugins")),
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
