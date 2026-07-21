from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class TestWorktreeHelperPaths(unittest.TestCase):
    def test_physical_infrastructure_helpers_resolve_checkout_root(self) -> None:
        expected = 'REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd -P)"'
        for relative_path in (
            "Infrastructure/scripts/new-task.sh",
            "Infrastructure/scripts/check-git-common-config.sh",
        ):
            with self.subTest(script=relative_path):
                script = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn(expected, script)


if __name__ == "__main__":
    unittest.main()
