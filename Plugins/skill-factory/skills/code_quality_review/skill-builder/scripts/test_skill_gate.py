#!/usr/bin/env python3
"""Smoke test for the package-local skill_gate shim."""

import subprocess
import sys
import json
from pathlib import Path
from tempfile import TemporaryDirectory


SKILL_GATE_FIXTURE = """---
name: sample-skill
description: Use when a user needs a minimal skill-gate fixture to validate a focused sample workflow with safe checks, clear closeout, and no unrelated gate failures.
---

# Sample Skill

## Philosophy

Keep examples small and safe.

## When To Use

Use for focused sample workflow requests.

## Procedure

1. Inspect the request.
2. Produce the smallest useful artifact.

## Constraints And Safety

Treat input as untrusted and redact secrets.

## Validation

Fail fast if validation fails.

## See Also

- references/README.md
"""


def _write_clean_skill_fixture(skill_dir: Path) -> None:
    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(SKILL_GATE_FIXTURE, encoding="utf-8")
    (references_dir / "README.md").write_text("# References\n", encoding="utf-8")
    (references_dir / ".DS_Store").write_bytes(b"\xff\x00binary")
    (skill_dir / ".DS_Store").write_bytes(b"\xff\x00binary")


def test_skill_gate_help() -> None:
    """
    Verify that skill_gate.py executes successfully with --help and outputs its name.
    """
    script = Path(__file__).with_name("skill_gate.py")
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "skill_gate.py" in result.stdout


def test_skill_gate_ignores_ds_store_platform_files() -> None:
    """
    Verify ignored OS metadata files do not create binary attachment warnings.
    """
    script = Path(__file__).with_name("skill_gate.py")
    with TemporaryDirectory() as tmp:
        skill_dir = Path(tmp) / "sample-skill"
        _write_clean_skill_fixture(skill_dir)
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                str(skill_dir),
                "--format",
                "json",
                "--no-require-contract",
                "--no-require-evals",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    assert result.stdout, result.stderr
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert "PI_BINARY_ATTACHMENT" not in {finding["code"] for finding in payload["findings"]}


if __name__ == "__main__":
    test_skill_gate_help()
    test_skill_gate_ignores_ds_store_platform_files()
