from __future__ import annotations

import re
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_EVAL_CASES = (
    (
        REPO_ROOT / "Skills" / "agent-ops" / "simplify" / "references" / "evals.yaml",
        "smoke-discovery",
        "current repository",
    ),
    (
        REPO_ROOT / "Skills" / "agent-ops" / "improve-agent-native" / "references" / "evals.yaml",
        "edge-universal-target-repo",
        "target repository",
    ),
)
MACHINE_PATH = re.compile(
    r"(?:(?<![A-Za-z0-9_/-])/(?!/)[^/\s]+(?:/[^/\s]*)*"
    r"|(?i:[A-Z]:[\\/][^\\/\s]+(?:[\\/][^\\/\s]*)*)"
    r"|\\\\[^\\/\s]+[\\/][^\\/\s]+)"
)


def test_machine_path_pattern_covers_common_absolute_forms() -> None:
    machine_paths = (
        "/Users/jamie/project",
        "/home/jamie/project",
        "/private/tmp/fixture",
        "/tmp/fixture",
        "/workspace/fixture",
        "/root/project",
        "/opt/checkouts/repo",
        "/mnt/work/repo",
        "/repo",
        r"C:\Users\jamie\project",
        r"c:\users\jamie\project",
        r"D:\dev\repo",
        r"C:\repo",
        r"\\build-host\workspace\fixture",
    )

    assert all(MACHINE_PATH.search(path) for path in machine_paths)
    assert not MACHINE_PATH.search("See https://example.com/docs/path")


def test_first_migration_eval_prompts_are_machine_portable() -> None:
    for path, case_id, expected_target in MIGRATION_EVAL_CASES:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        cases = payload.get("cases", [])
        case = next((candidate for candidate in cases if candidate.get("id") == case_id), None)
        assert case is not None
        prompt = case.get("prompt", "")
        assert not MACHINE_PATH.search(prompt), path.relative_to(REPO_ROOT)
        assert expected_target in prompt
