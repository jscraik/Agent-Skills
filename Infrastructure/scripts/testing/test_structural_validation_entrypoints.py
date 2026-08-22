from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER = REPO_ROOT / "Infrastructure" / "scripts" / "check-code-size.mjs"
HOOK = REPO_ROOT / "Infrastructure" / "scripts" / "hook-pre-commit.sh"


class StructuralValidationEntrypointTests(unittest.TestCase):
    def test_checker_routes_to_repository_structural_validators(self) -> None:
        source = CHECKER.read_text(encoding="utf-8")

        self.assertIn("verify_ask_cli_modularity.py", source)
        self.assertIn("verify_program_design.py", source)
        self.assertIn("run-infrastructure-python.sh", source)
        self.assertNotIn("quality:size", source)
        self.assertNotIn("pnpm", source)
        self.assertNotIn("allowlist", source.lower())
        self.assertNotIn("waiver", source.lower())

    def test_hook_uses_codestyle_and_structural_validation_only(self) -> None:
        source = HOOK.read_text(encoding="utf-8")

        self.assertIn("bash scripts/validate-codestyle.sh --fast", source)
        self.assertIn("node scripts/check-code-size.mjs", source)
        self.assertNotIn("quality:size", source)
        self.assertNotIn("npm run", source)
        self.assertNotIn("pnpm", source)

    def test_entrypoints_have_valid_syntax(self) -> None:
        for command in (("node", "--check", str(CHECKER)), ("bash", "-n", str(HOOK))):
            with self.subTest(command=command):
                completed = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
                self.assertEqual(completed.returncode, 0, completed.stderr)


if __name__ == "__main__":
    unittest.main()
