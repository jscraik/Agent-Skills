"""Regression checks for Harness tooling-policy source parity."""

from __future__ import annotations

import json
from pathlib import Path
import tomllib
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]


class HarnessToolingContractTests(unittest.TestCase):
    def test_required_mise_versions_match_the_pinned_toolchain(self) -> None:
        contract = json.loads((REPO_ROOT / "harness.contract.json").read_text(encoding="utf-8"))
        with (REPO_ROOT / ".mise.toml").open("rb") as handle:
            pinned_tools = tomllib.load(handle)["tools"]
        required_tools = {
            entry["tool"]: entry["version"]
            for entry in contract["toolingPolicy"]["requiredMiseTools"]
        }

        self.assertEqual(required_tools, pinned_tools)

    def test_documentation_uses_the_executable_agentation_name(self) -> None:
        contract = json.loads((REPO_ROOT / "harness.contract.json").read_text(encoding="utf-8"))
        required_terms = contract["toolingPolicy"]["requiredDocumentationTerms"]

        self.assertIn("agentation-mcp", required_terms)
        self.assertNotIn("agentation", required_terms)

    def test_required_codex_actions_exist_in_the_environment(self) -> None:
        contract = json.loads((REPO_ROOT / "harness.contract.json").read_text(encoding="utf-8"))
        with (REPO_ROOT / ".codex/environments/environment.toml").open("rb") as handle:
            environment = tomllib.load(handle)

        required_actions = {
            (entry["name"], entry["icon"])
            for entry in contract["toolingPolicy"]["codexEnvironment"]["requiredActions"]
        }
        environment_actions = {
            (entry["name"], entry["icon"])
            for entry in environment["actions"]
        }

        self.assertLessEqual(required_actions, environment_actions)


if __name__ == "__main__":
    unittest.main()
