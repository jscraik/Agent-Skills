import os
import subprocess
from pathlib import Path
from ask.envelope import CallResult, ErrorObject

# Allow-list for companion folder types per plugin-creator contract
_ALLOWED_COMPANION_FOLDERS = {"skills", "hooks", "scripts", "assets", "mcp", "apps"}

def init_plugin(repo_root: Path, name: str, with_marketplace: bool = False, companion_folders: list[str] = None) -> CallResult:
    """Initializes a new plugin scaffold."""
    result = CallResult()

    # Validate companion_folders against allow-list
    if companion_folders:
        invalid = [f for f in companion_folders if f not in _ALLOWED_COMPANION_FOLDERS]
        if invalid:
            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_VALIDATION",
                message=f"Invalid companion folder(s): {invalid}. Allowed: {sorted(_ALLOWED_COMPANION_FOLDERS)}",
                fix_suggestion=f"Use only allowed folder types: {', '.join(sorted(_ALLOWED_COMPANION_FOLDERS))}"
            ))
            return result

    cmd = [
        "python3", "skills-system/plugin-creator/scripts/create_basic_plugin.py",
        name
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
    else:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=process.stderr.strip()))
        
    return result
