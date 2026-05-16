from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills-system" / "skill-creator" / "scripts" / "quick_validate.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("skill_creator_quick_validate", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_validate_skill_accepts_metadata_without_pyyaml_dependency(tmp_path: Path) -> None:
    skill_dir = tmp_path / "example-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: example-skill
description: Create example outputs when the user asks for example work.
metadata:
  short-description: Example outputs
---

# Example Skill
""",
        encoding="utf-8",
    )

    module = _load_module()
    assert module.validate_skill(skill_dir) == (True, "Skill is valid!")


def test_validate_skill_accepts_allowed_tools_list(tmp_path: Path) -> None:
    skill_dir = tmp_path / "tool-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: tool-skill
description: Use a declared tool when the user asks for tool work.
allowed-tools:
  - Bash
  - Read
---

# Tool Skill
""",
        encoding="utf-8",
    )

    module = _load_module()
    assert module.validate_skill(skill_dir) == (True, "Skill is valid!")


def test_cli_runs_with_plain_python3(tmp_path: Path) -> None:
    skill_dir = tmp_path / "plain-python-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: plain-python-skill
description: Validate with the ambient python3 interpreter.
---

# Plain Python Skill
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(skill_dir)],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Skill is valid!" in result.stdout
    assert "ModuleNotFoundError" not in result.stderr
