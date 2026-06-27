from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.commands import sdk_eval  # noqa: E402


class TestSkillsSdkEvalCommandHints(unittest.TestCase):
    def test_tessl_local_proof_next_command_requires_execute(self) -> None:
        next_command = sdk_eval._tessl_local_proof_next()

        self.assertIn("tessl-local-proof", next_command)
        self.assertIn("--execute", next_command)
        self.assertNotIn("--preview", next_command)


if __name__ == "__main__":
    unittest.main()
