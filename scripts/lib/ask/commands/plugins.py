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
    "skills-system/plugin-creator/scripts/create_basic_plugin.py",
    "plugins/plugin-factory/skills/plugin-creator/scripts/create_basic_plugin.py",
)
_PLUGIN_INSTALLER_SCRIPT_CANDIDATES = (
    "skills-system/plugin-installer/scripts/install-plugin-from-github.py",
    "plugins/plugin-factory/skills/plugin-installer/scripts/install-plugin-from-github.py",
)
_PLUGIN_BUILDER_SCRIPT_CANDIDATES = (
    "utilities/plugin-builder/scripts/plugin_builder.py",
    "plugins/plugin-factory/skills/plugin-builder/scripts/plugin_builder.py",
)


def _to_absolute_path(path: Path) -> Path:
    """Return an absolute path without resolving symlinks."""
    return Path(path.expanduser()).absolute()


def _runtime_error_result(message: str, *, fix_suggestion: str) -> CallResult:
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
    try:
        return _resolve_script_path(repo_root, candidates), None
    except FileNotFoundError as exc:
        return None, _runtime_error_result(str(exc), fix_suggestion=fix_suggestion)


def _normalize_plugin_name(raw_name: str) -> str:
    normalized = raw_name.strip().lower()
    normalized = _PLUGIN_NAME_SANITIZE_RE.sub("-", normalized).strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized


def _extract_plugin_root_from_output(stdout: str, repo_root: Path, raw_name: str) -> Path:
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
    """List read-only plugin lifecycle state for the current repo."""
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
    """Initialize a new plugin scaffold."""
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
            "skills-system/ or plugins/plugin-factory/."
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
    dest: str = "plugins/third-party",
    validation_level: str = "compat",
    allow_untrusted_source: bool = False,
    allow_unpinned_ref: bool = False,
    dry_run: bool = False,
) -> CallResult:
    """Install a plugin from GitHub via the plugin-installer script."""
    result = CallResult()
    installer_script, resolve_error = _resolve_script_path_or_runtime_error(
        repo_root,
        _PLUGIN_INSTALLER_SCRIPT_CANDIDATES,
        fix_suggestion=(
            "Ensure plugin-installer sources are available in either "
            "skills-system/ or plugins/plugin-factory/."
        ),
    )
    if resolve_error:
        return resolve_error
    assert installer_script is not None

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
    marketplace_path: str = ".agents/plugins/marketplace.json",
    run_compat: bool = True,
    run_marketplace_audit: bool = True,
    allow_legacy_marketplace_path: bool = True,
) -> CallResult:
    """Run plugin-builder hardening checks for a plugin package."""
    builder_script, resolve_error = _resolve_script_path_or_runtime_error(
        repo_root,
        _PLUGIN_BUILDER_SCRIPT_CANDIDATES,
        fix_suggestion=(
            "Ensure plugin-builder sources are available in either "
            "utilities/ or plugins/plugin-factory/."
        ),
    )
    if resolve_error:
        return resolve_error
    assert builder_script is not None

    plugin_root = Path(plugin_path)
    if not plugin_root.is_absolute():
        plugin_root = _to_absolute_path(repo_root / plugin_root)

    if not plugin_root.exists():
        return _validation_error_result(
            f"Plugin path '{plugin_root}' does not exist.",
            fix_suggestion="Pass a valid plugin directory path (for example: plugins/<name>).",
        )

    marketplace = Path(marketplace_path)
    if not marketplace.is_absolute():
        marketplace = _to_absolute_path(repo_root / marketplace)

    command_runs: list[dict[str, str]] = []

    def _run(command: list[str], step: str) -> bool:
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
