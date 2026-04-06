import os
import shutil
import subprocess
import tempfile
import re
import sys
import importlib.util
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from ask.envelope import CallResult, ErrorObject
from ask.context import find_repo_root
from skill_discovery import discover_skill_entries

# Explicitly load builder-specific logic using absolute paths to avoid namespace collisions
def _load_builder_module(repo_root: Path, module_name: str):
    module_path = repo_root / "utilities" / "skill-builder" / "scripts" / f"{module_name}.py"
    if not module_path.exists():
        return None

    internal_name = f"ask_builder_{module_name}"
    if internal_name in sys.modules:
        return sys.modules[internal_name]

    spec = importlib.util.spec_from_file_location(internal_name, str(module_path))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules[internal_name] = mod # Register BEFORE exec
        spec.loader.exec_module(mod)
        return mod
    return None

def list_skills(repo_root: Path, category: str = None) -> CallResult:
    result = CallResult()
    entries = discover_skill_entries(source="auto")
    skills_data = []
    for entry in entries:
        if category and category.lower() not in entry.category.lower():
            continue
        skills_data.append({
            "name": entry.name,
            "path": str(entry.source_dir.relative_to(repo_root)),
            "category": entry.category,
            "description": entry.description
        })
    result.data["skills"] = skills_data
    result.status = "success"
    return result

def init_skill(repo_root: Path, name: str, category: str, description: str) -> CallResult:
    """Initializes a new skill scaffold using the repo template logic."""
    result = CallResult()
    
    cmd = [
        "python3", "utilities/skill-builder/scripts/init_skill.py",
        name,
        "--category", category,
        "--description", description,
        "--owner", "Agent Skills Kit",
        "--review-cadence", "quarterly",
        "--maturity", "experimental",
        "--lifecycle-state", "incubating"
    ]
    
    process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
    
    if process.returncode == 0:
        result.status = "success"
        result.data["message"] = f"Initialized skill '{name}' in '{category}'"
        result.metadata["next_steps"] = [f"ask skills audit {category}/{name} --level strict"]
    else:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=process.stderr.strip()))
        
    return result

def audit_skill(repo_root: Path, skill_path: str, level: str = "compat") -> CallResult:
    """Runs structural and security audits on a skill."""
    result = CallResult()

    # Path traversal protection: resolve and verify path is within repo
    try:
        resolved_path = (repo_root / skill_path).resolve()
        resolved_root = repo_root.resolve()
        if not str(resolved_path).startswith(str(resolved_root)):
            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_PATH_TRAVERSAL",
                message=f"Path traversal detected: '{skill_path}' resolves outside repository root.",
                fix_suggestion="Use a relative path within the repository."
            ))
            return result
    except Exception as e:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Invalid path: {e}",
            fix_suggestion="Check the path format and try again."
        ))
        return result

    diag_cmd = ["python3", "scripts/diagnose_skill.py", skill_path]
    diag_proc = subprocess.run(diag_cmd, cwd=str(repo_root), capture_output=True, text=True)
    result.data["diagnostics"] = {"exit_code": diag_proc.returncode, "stdout": diag_proc.stdout, "stderr": diag_proc.stderr}
    
    if level == "strict":
        gate_cmd = ["python3", "utilities/skill-builder/scripts/skill_gate.py", skill_path, "--require-security-evals", "--pi-high-fail", "--require-fail-fast"]
        gate_proc = subprocess.run(gate_cmd, cwd=str(repo_root), capture_output=True, text=True)
        result.data["security_gate"] = {"exit_code": gate_proc.returncode, "stdout": gate_proc.stdout, "stderr": gate_proc.stderr}
        if gate_proc.returncode != 0:
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Security gate failed."))
            return result

    if diag_proc.returncode == 0:
        result.status = "success"
    else:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message="Structural diagnostics failed. Skill directory not found or invalid.",
            fix_suggestion=f"Ensure '{skill_path}' exists and contains a SKILL.md file."
        ))
        
    return result

def install_skill(repo_root: Path, url: str, remediate: bool = False, dest: str = "github", dry_run: bool = False) -> CallResult:
    """Installs a skill from GitHub, wrapping the hardened installer script."""
    result = CallResult()
    dest_path = repo_root / dest

    # Parse skill name from URL for preview
    skill_name = url.split("/")[-1].replace(".git", "") if "/" in url else url
    target_path = dest_path / skill_name

    # Check for existing skill conflict
    if target_path.exists():
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_CONFLICT",
            message=f"Skill '{skill_name}' already exists at '{target_path.relative_to(repo_root)}'.",
            fix_suggestion=f"Remove the existing skill or choose a different destination with --dest."
        ))
        result.data["skill_name"] = skill_name
        result.data["existing_path"] = str(target_path.relative_to(repo_root))
        return result

    if dry_run:
        # Preview mode: show what would happen without making changes
        result.status = "success"
        result.data["dry_run"] = True
        result.data["skill_name"] = skill_name
        result.data["target_path"] = str(target_path.relative_to(repo_root))
        result.data["url"] = url
        result.data["remediate"] = remediate
        result.metadata["next_steps"] = [
            f"ask skills install {url} --dest {dest}" + (" --remediate" if remediate else "")
        ]
        return result

    cmd = [
        "python3", "skills-system/skill-installer/scripts/install-skill-from-github.py",
        "--url", url,
        "--dest", str(dest_path),
        "--allow-untrusted-source",
        "--allow-unpinned-ref",
        "--validation-level", "compat"
    ]

    if remediate:
        cmd.append("--remediate")

    process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
    result.data["raw_output"] = process.stdout
    result.data["raw_error"] = process.stderr

    if process.returncode == 0:
        result.status = "success"
        match = re.search(r"Installed (.*?) to", process.stdout)
        if match:
            result.data["skill_name"] = match.group(1)
            result.metadata["next_steps"] = [f"ask skills audit {dest}/{match.group(1)} --level strict"]
    else:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=process.stderr.strip() or "Installation failed."))

    return result

def fold_skills(repo_root: Path, source: str, target: str, sensitivity: float = 0.2) -> CallResult:
    """Calculates functional similarity and suggests folding source into target."""
    result = CallResult()
    
    builder_catalog = _load_builder_module(repo_root, "skill_catalog")
    router_mod = _load_builder_module(repo_root, "skill_router")
    
    if not builder_catalog or not router_mod:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_DEPENDENCY", message="Skill router or builder catalog not available."))
        return result

    catalog = builder_catalog.load_catalog(repo_root)
    source_skill = next((s for s in catalog.skills if s.name == source or str(s.skill_path).endswith(source)), None)
    target_skill = next((s for s in catalog.skills if s.name == target or str(s.skill_path).endswith(target)), None)

    if not source_skill or not target_skill:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Source or target skill not found."))
        return result

    # Run router check
    query = source_skill.description
    candidates, _ = router_mod.route(query, [target_skill], top_k=1)
    
    if candidates:
        match = candidates[0]
        result.data["overlap_score"] = match.confidence
        result.data["rationale"] = match.rationale

        if match.confidence >= sensitivity:
            # High overlap - emit CONFLICT to indicate redundancy issue
            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_REDUNDANCY",
                message=f"High overlap ({int(match.confidence * 100)}%) detected between '{source}' and '{target}'.",
                fix_suggestion=f"Consider folding '{source}' into '{target}' to reduce redundancy."
            ))
            result.data["recommendation"] = f"FOLD: High overlap ({int(match.confidence * 100)}%) detected."
        else:
            result.status = "success"
            result.data["recommendation"] = f"KEEP: Low overlap ({int(match.confidence * 100)}%) detected."
    else:
        result.status = "success"
        result.data["overlap_score"] = 0
        result.data["recommendation"] = "KEEP: No significant overlap found."

    return result

def _create_symlink(source: Path, target: Path, dry_run: bool = False) -> str:
    """Safely create or update a symlink."""
    action = "Created" if not target.exists() else "Updated"
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink() or target.exists():
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            else:
                target.unlink()
        target.symlink_to(source)
    return f"{action} symlink: {target} -> {source}"

def _sync_dir_copy(source: Path, target: Path, dry_run: bool = False) -> str:
    """Sync directory via copy (rsync-like)."""
    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)
        for item in source.iterdir():
            if item.name in ('.git', 'node_modules', '__pycache__'):
                continue
            dest = target / item.name
            if item.is_dir():
                if dest.exists(): shutil.rmtree(dest)
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)
    return f"Synced directory: {target} (copy)"

def sync_skills(repo_root: Path, scope: str = "workspace", dry_run: bool = False) -> CallResult:
    result = CallResult()
    plan = {"writes": [], "deletes": [], "symlinks": []}
    logs = []
    skills_dir = repo_root / ".agents" / "skills"
    antigravity_skills_dir = repo_root / "skills-antigravity"
    entries = discover_skill_entries(source="repo")
    for entry in entries:
        skill_name = entry.name
        target_link = skills_dir / skill_name
        rel_to_root = entry.source_dir.relative_to(repo_root)
        source_rel = os.path.join("../..", str(rel_to_root))
        plan["symlinks"].append({"from": str(target_link), "to": source_rel})
        logs.append(_create_symlink(Path(source_rel), target_link, dry_run))
    if scope == "user":
        home = Path.home()
        targets = [(skills_dir, repo_root / "skills"), (skills_dir, home / ".claude" / "skills"), (skills_dir, home / ".agents" / "skills"), (skills_dir, home / ".codex" / "skills"), (antigravity_skills_dir, home / ".antigravity" / "skills")]
        for src, dst in targets:
            plan["symlinks"].append({"from": str(dst), "to": str(src)})
            logs.append(_create_symlink(src, dst, dry_run))
        antigravity_dest = home / ".gemini" / "antigravity" / "skills"
        plan["writes"].append(str(antigravity_dest))
        logs.append(_sync_dir_copy(antigravity_skills_dir, antigravity_dest, dry_run))
    result.data["plan"] = plan
    result.data["logs"] = logs
    result.status = "success"
    return result
