import os
import subprocess
from pathlib import Path
from typing import Dict, Any
from ask.envelope import CallResult, ErrorObject
from ask.context import find_repo_root

def repo_status(repo_root: Path, verbose: bool = False) -> CallResult:
    """Returns overall health, sync status, and lint issues."""
    result = CallResult()
    result.data["repo_root"] = str(repo_root)
    result.data["is_git"] = (repo_root / ".git").exists()
    
    # Check if .agents/skills is synced
    skills_dir = repo_root / ".agents" / "skills"
    is_synced = skills_dir.is_dir() and any(skills_dir.iterdir())
    result.data["skills_synced"] = is_synced
    
    result.status = "success"
    return result

def repo_validate(repo_root: Path, ephemeral: bool = False) -> CallResult:
    """Wraps scripts/validate_all.sh with structured JSON error reporting."""
    result = CallResult()
    
    cmd = ["bash", "scripts/validate_all.sh"]
    if ephemeral:
        cmd.append("--ephemeral")
    else:
        cmd.append("--persistent")
        
    process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
    
    # Parse output for summary
    stdout = process.stdout
    required_failures = 0
    warn_only_issues = 0
    
    for line in stdout.splitlines():
        if "- required_failures:" in line:
            required_failures = int(line.split(":")[-1].strip())
        elif "- warn_only_issues:" in line:
            warn_only_issues = int(line.split(":")[-1].strip())
            
    result.data["required_failures"] = required_failures
    result.data["warn_only_issues"] = warn_only_issues
    result.data["raw_output"] = stdout
    
    if process.returncode == 0:
        result.status = "success"
    else:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Validation failed with {required_failures} required failures.",
            fix_suggestion="Review the validation logs in artifacts/validation/latest/"
        ))
        
    return result
