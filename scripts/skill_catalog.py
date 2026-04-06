#!/usr/bin/env python3
"""Compatibility shim for skill_catalog.py → skill_discovery.py

Deprecated: Use scripts/skill_discovery.py directly.
This shim preserves backward compatibility for existing callers.
"""
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

# Delegate to skill_discovery
skill_discovery_path = Path(__file__).resolve().parent / "skill_discovery.py"
sys.path.insert(0, str(skill_discovery_path.parent))

from skill_discovery import main, parse_args, discover_skill_entries, SkillEntry, REPO_ROOT


@dataclass(frozen=True)
class SkillMeta:
    """Legacy skill metadata class for backward compatibility."""
    name: str
    description: str
    skill_path: str


def load_catalog(repo_root: Optional[Path] = None, strict: bool = True) -> List[SkillMeta]:
    """Load skill catalog for backward compatibility.

    Args:
        repo_root: Repository root path (optional, auto-detected if not provided)
        strict: If True, raise on catalog issues; if False, return best effort

    Returns:
        List of SkillMeta objects
    """
    try:
        entries = discover_skill_entries(source="auto")
        return [
            SkillMeta(
                name=entry.name,
                description=entry.description,
                skill_path=str(entry.source_dir.relative_to(REPO_ROOT))
            )
            for entry in entries
        ]
    except Exception as e:
        if strict:
            raise
        # Return empty catalog in non-strict mode
        return []


# Re-export for backward compatibility
__all__ = ["main", "parse_args", "SkillMeta", "load_catalog", "SkillEntry"]

if __name__ == "__main__":
    raise SystemExit(main())
