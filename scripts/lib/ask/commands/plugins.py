import subprocess
from pathlib import Path
from typing import List, Optional

from ask.envelope import CallResult, ErrorObject

# Allow-list for companion folder types per plugin-creator contract
_ALLOWED_COMPANION_FOLDERS = {"skills", "hooks", "scripts", "assets", "mcp", "apps", "references", "workflows"}


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

    process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)

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
    dest: str = "plugins/third-party",
    validation_level: str = "compat",
    allow_untrusted_source: bool = False,
    allow_unpinned_ref: bool = False,
    dry_run: bool = False,
) -> CallResult:
    """Install a plugin from GitHub via the plugin-installer script."""
    result = CallResult()

    dest_path = repo_root / dest
    inferred_name = (name or url.split("/")[-1].replace(".git", "")).strip() or "plugin"
    target_path = dest_path / inferred_name

    if dry_run:
        result.status = "success"
        result.data["dry_run"] = True
        result.data["url"] = url
        result.data["plugin_path"] = plugin_path
        result.data["plugin_name"] = inferred_name
        try:
            result.data["target_path"] = str(target_path.relative_to(repo_root))
        except ValueError:
            result.data["target_path"] = str(target_path)
        result.metadata["next_steps"] = [
            f"ask plugins install {url} --path {plugin_path} --dest {dest}"
        ]
        return result

    if target_path.exists():
        result.status = "error"
        result.errors.append(
            ErrorObject(
                code="ERR_CONFLICT",
                message=f"Plugin '{inferred_name}' already exists at '{target_path}'.",
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

    if name:
        cmd.extend(["--name", name])
    if allow_untrusted_source:
        cmd.append("--allow-untrusted-source")
    if allow_unpinned_ref:
        cmd.append("--allow-unpinned-ref")

    process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
    result.data["raw_output"] = process.stdout
    result.data["raw_error"] = process.stderr

    if process.returncode == 0:
        result.status = "success"
        result.data["message"] = f"Installed plugin '{name or inferred_name}'"
        result.data["plugin_name"] = name or inferred_name
        return result

    result.status = "error"
    result.errors.append(ErrorObject(code="ERR_RUNTIME", message=process.stderr.strip() or "Plugin installation failed."))
    return result
