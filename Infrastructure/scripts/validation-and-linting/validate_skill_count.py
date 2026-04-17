#!/usr/bin/env python3
"""Validate that SKILL.md total_skills matches actual skill count.

Exits non-zero on mismatch so maintainers cannot forget to update total_skills.
Wired into pre-commit and CI for enforcement.
"""
import re
import sys
from pathlib import Path


def main() -> int:
    """Validate SKILL.md total_skills declaration."""
    repo_root = Path(__file__).resolve().parents[3]
    skill_md = repo_root / "SKILL.md"

    if not skill_md.exists():
        print(f"ERROR: SKILL.md not found at {skill_md}")
        return 1

    content = skill_md.read_text()

    # Find total_skills declaration
    total_skills_match = re.search(
        r'^- `total_skills`: (\d+)$',
        content,
        re.MULTILINE
    )

    if not total_skills_match:
        print("ERROR: Could not find 'total_skills' declaration in SKILL.md")
        print("Expected format: - `total_skills`: 123")
        return 1

    declared_count = int(total_skills_match.group(1))
    line_num = content[:total_skills_match.start()].count('\n') + 1

    # Count actual skill entries (lines starting with "- `skill-name`")
    skill_pattern = re.compile(r'^- `([^`]+)`', re.MULTILINE)
    actual_count = len(skill_pattern.findall(content))

    if actual_count != declared_count:
        print(f"❌ SKILL.md total_skills mismatch!")
        print(f"  Line {line_num}: declared {declared_count}, actual {actual_count}")
        print(f"\n  To fix, update SKILL.md line {line_num}:")
        print(f"    - `total_skills`: {actual_count}")
        return 1

    print(f"✅ total_skills matches: {actual_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
