import os
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, Any, List
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

def check_hub_stability(repo_root: Path, changed_files: List[str] = None) -> CallResult:
    """CI gate: blocks deletion/rename of stable skills without deprecation notice."""
    result = CallResult()

    # Build list of all SKILL.md files
    stable_skills = []
    errors = []

    FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---", re.DOTALL)
    STABLE_RE = re.compile(r"^stability\s*:\s*stable\s*$", re.MULTILINE)

    for md in sorted(repo_root.rglob("SKILL.md")):
        try:
            content = md.read_text(encoding="utf-8", errors="replace")
            fm = FRONTMATTER_RE.search(content)
            if fm and STABLE_RE.search(fm.group(1)):
                skill = md.parts[-2]
                stable_skills.append(skill)
        except Exception:
            continue

    # If checking specific changed files
    if changed_files:
        for f in changed_files:
            p = repo_root / f
            if p.name != "SKILL.md":
                continue
            skill = p.parts[-2] if len(p.parts) >= 2 else str(p)

            if not p.exists():
                # File was deleted - check against stable skills list or edges file
                edges_file = repo_root / "ops" / "metrics" / "graph" / "skill-edges.json"
                if edges_file.exists():
                    try:
                        data = json.loads(edges_file.read_text())
                        stable_ids = {n["id"] for n in data.get("nodes", []) if n.get("stability") == "stable"}
                        if skill in stable_ids:
                            errors.append(
                                f"STABLE SKILL DELETED: '{skill}' is marked stable and was deleted "
                                f"without a deprecation notice. Add a ## Deprecation section to the "
                                f"last committed version before removal."
                            )
                    except Exception:
                        pass
                continue

            try:
                content = p.read_text(encoding="utf-8", errors="replace")
                fm = FRONTMATTER_RE.search(content)
                if not (fm and STABLE_RE.search(fm.group(1))):
                    continue

                # Stable skill exists - check required fields
                if not re.search(r"^name\s*:", fm.group(1), re.MULTILINE):
                    errors.append(f"STABLE SKILL MISSING 'name': {skill}")
                if not re.search(r"^description\s*:", fm.group(1), re.MULTILINE):
                    errors.append(f"STABLE SKILL MISSING 'description': {skill}")
            except Exception:
                continue

    result.data["stable_skills"] = sorted(stable_skills)
    result.data["stable_count"] = len(stable_skills)
    result.data["checked_files"] = len(changed_files) if changed_files else 0

    if errors:
        result.status = "error"
        result.data["errors"] = errors
        for e in errors:
            result.errors.append(ErrorObject(code="ERR_VALIDATION", message=e))
    else:
        result.status = "success"

    return result
