from __future__ import annotations

import json
import shlex
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "tests"))

from helpers.schema_validator import _validate_schema_subset  # noqa: E402


ARTIFACT_PATH = REPO_ROOT / ".harness/evidence/handoff/skills-sdk-parser-families/authority-parser-replay-receipt.v1.json"
SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/authority-parser-replay-receipt.v1.schema.json"
SELECTION_PATH = REPO_ROOT / ".harness/evidence/handoff/skills-sdk-parser-families/authority-parser-replay-selection.json"


class TestSkillsSdkAuthorityParserReplayReceipt(unittest.TestCase):
    def test_receipt_is_schema_valid_and_revision_bound(self) -> None:
        artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        _validate_schema_subset(schema, artifact, {SCHEMA_PATH.name: schema})

        selection = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))
        self.assertEqual(artifact["source_selection_schema"], selection["schema_version"])
        self.assertEqual(artifact["source_tree_digest"], selection["source_tree_digest"])
        self.assertEqual(artifact["command_count"], len(artifact["commands"]))
        self.assertEqual(artifact["command_count"], len(selection["selected_preview_commands"]))
        self.assertTrue(_is_ancestor(artifact["base_commit"], _git_head()))
        self.assertFalse(artifact["mutation_performed"])
        self.assertTrue(artifact["command_execution_performed"])
        self.assertFalse(artifact["network_accessed"])
        self.assertFalse(artifact["credentials_accessed"])

    def test_each_row_matches_selected_family_and_has_no_write_proof(self) -> None:
        artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        selection = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))
        selected = {row["family"]: row for row in selection["selected_preview_commands"]}
        self.assertEqual({row["family"] for row in artifact["commands"]}, set(selected))

        for row in artifact["commands"]:
            with self.subTest(family=row["family"]):
                self.assertEqual(row["command"], selected[row["family"]]["command"].replace("ask sdk", "./bin/ask sdk", 1))
                self.assertEqual(row["argv"], shlex.split(row["command"]))
                self.assertEqual(row["exit_code"], 0)
                self.assertEqual(row["top_level_status"], "success")
                self.assertIn(row["receipt_status"], {"pass", "preview"})
                self.assertFalse(row["mutation_performed"])
                self.assertGreater(len(row["mutation_evidence"]), 0)
                self.assertEqual(row["stderr_bytes"], 0)


def _git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _is_ancestor(base_commit: str, head: str) -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", base_commit, head],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
    ).returncode == 0


if __name__ == "__main__":
    unittest.main()
