from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "Infrastructure/scripts/check-codestyle-parity.sh"


class TestCheckCodestyleParity(unittest.TestCase):
    def test_default_repo_root_verifies_the_checked_in_manifest(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT_PATH)],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("verified 22 codestyle file(s)", result.stdout)
