from __future__ import annotations

import re
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_EVAL_CASES = (
    (
        REPO_ROOT / "Skills" / "agent-ops" / "simplify" / "references" / "evals.yaml",
        "smoke-discovery",
    ),
    (
        REPO_ROOT / "Skills" / "agent-ops" / "improve-agent-native" / "references" / "evals.yaml",
        "edge-universal-target-repo",
    ),
)
MACHINE_PATH = re.compile(
    r"(?:(?<![A-Za-z0-9_-])/(?:Users|home|private/tmp|tmp|workspace)(?:/|$)"
    r"|(?i:[A-Z]:[\\/](?:Users|home|private/tmp|tmp|workspace)(?:[\\/]|$))"
    r"|\\\\[^\\/\s]+[\\/][^\\/\s]+)"
)


def test_machine_path_pattern_covers_common_absolute_forms() -> None:
    machine_paths = (
        "/Users/jamie/project",
        "/home/jamie/project",
        "/private/tmp/fixture",
        "/tmp/fixture",
        "/workspace/fixture",
        r"C:\Users\jamie\project",
        r"c:\users\jamie\project",
        r"\\build-host\workspace\fixture",
    )

    assert all(MACHINE_PATH.search(path) for path in machine_paths)


def test_first_migration_eval_prompts_are_machine_portable() -> None:
    for path, case_id in MIGRATION_EVAL_CASES:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        cases = payload.get("cases", [])
        case = next((candidate for candidate in cases if candidate.get("id") == case_id), None)
        assert case is not None
        prompt = case.get("prompt", "")
        assert not MACHINE_PATH.search(prompt), path.relative_to(REPO_ROOT)
        assert "target repository" in prompt
