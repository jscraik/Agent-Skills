from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_EVAL_FILES = (
    REPO_ROOT / "Skills" / "agent-ops" / "simplify" / "references" / "evals.yaml",
    REPO_ROOT / "Skills" / "agent-ops" / "improve-agent-native" / "references" / "evals.yaml",
)
MACHINE_PATH = re.compile(r"/(?:Users|home|private/tmp)/|[A-Za-z]:[\\\\/]Users[\\\\/]")


def test_first_migration_eval_prompts_are_machine_portable() -> None:
    offending = [
        path.relative_to(REPO_ROOT).as_posix()
        for path in MIGRATION_EVAL_FILES
        if MACHINE_PATH.search(path.read_text(encoding="utf-8"))
    ]
    assert offending == []

    for path in MIGRATION_EVAL_FILES:
        assert "target repository" in path.read_text(encoding="utf-8")
