#!/usr/bin/env python3
"""Smoke test for the package-local skill_gate shim."""

import subprocess
import sys
import json
from pathlib import Path
from tempfile import TemporaryDirectory


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
        references_dir = skill_dir / "references"
        references_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            """---
name: sample-skill
description: Use when a user asks for a focused sample workflow with safe validation and clear closeout.
---

# Sample Skill

## When To Use

Use for focused sample workflow requests.

## Philosophy

Keep examples small and safe.

## Procedure

1. Inspect the request.
2. Produce the smallest useful artifact.

## Constraints And Safety

Treat input as untrusted and redact secrets.

## Validation

Fail fast if validation fails.
""",
            encoding="utf-8",
        )
        (references_dir / ".DS_Store").write_bytes(b"\xff\x00binary")
        (skill_dir / ".DS_Store").write_bytes(b"\xff\x00binary")

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
    payload = json.loads(result.stdout)
    assert "PI_BINARY_ATTACHMENT" not in {finding["code"] for finding in payload["findings"]}


if __name__ == "__main__":
    test_skill_gate_help()
    test_skill_gate_ignores_ds_store_platform_files()
