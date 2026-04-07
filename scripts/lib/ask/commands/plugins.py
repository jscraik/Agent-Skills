import subprocess
import re
from pathlib import Path
from typing import List, Optional

from ask.envelope import CallResult, ErrorObject

# Allow-list for companion folder types per plugin-creator contract
_ALLOWED_COMPANION_FOLDERS = {"skills", "hooks", "scripts", "assets", "mcp", "apps", "references", "workflows"}
_INSTALL_SUMMARY_RE = re.compile(r"Installed\s+([a-z0-9][a-z0-9-]{0,63})\s+to\s+(.+)")


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

    cmd = [
        "python3",
        "skills-system/plugin-creator/scripts/create_basic_plugin.py",
        name,
    ]

    if with_marketplace:
        cmd.append("--with-marketplace")

    if companion_folders:
        for folder in companion_folders:
            cmd.append(f"--with-{folder}")

    process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, check=False)

    if process.returncode == 0:
        result.status = "success"
        result.data["message"] = f"Initialized plugin '{name}'"
        result.data["raw_output"] = process.stdout
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
        "skills-system/plugin-installer/scripts/install-plugin-from-github.py",
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
