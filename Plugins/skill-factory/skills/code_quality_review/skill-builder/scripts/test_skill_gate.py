#!/usr/bin/env python3
"""Smoke test for the package-local skill_gate shim."""

import subprocess
import sys
from pathlib import Path


def test_skill_gate_help() -> None:
    script = Path(__file__).with_name("skill_gate.py")
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "skill_gate.py" in result.stdout


if __name__ == "__main__":
    test_skill_gate_help()
