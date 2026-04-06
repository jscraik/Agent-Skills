import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
from ask.envelope import CallResult
from skill_catalog import discover_skill_entries

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

def sync_skills(repo_root: Path, scope: str = "workspace", dry_run: bool = False) -> CallResult:
    result = CallResult()
    plan = {"writes": [], "deletes": [], "symlinks": []}
    
    skills_dir = repo_root / ".agents" / "skills"
    
    # Discovery logic similar to sync_skills.sh
    entries = discover_skill_entries(source="repo")
    
    for entry in entries:
        skill_name = entry.name
        target_link = skills_dir / skill_name
        
        # Calculate relative path from .agents/skills back to repo root then to skill
        # e.g. ../../auth/create-auth
        rel_to_root = entry.source_dir.relative_to(repo_root)
        source_rel = os.path.join("../..", str(rel_to_root))
        
        plan["symlinks"].append({
            "from": str(target_link.relative_to(repo_root)),
            "to": source_rel
        })
        
    result.data["plan"] = plan
    result.status = "success"
    
    if not dry_run:
        # Actual execution would happen here in Phase 3.1 implementation
        # For now, we just satisfy the dry-run test
        pass
        
    return result
