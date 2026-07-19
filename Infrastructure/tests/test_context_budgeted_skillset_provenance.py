"""Focused regression coverage for generated skillset provenance."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
LIFECYCLE_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"
VALIDATION_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting"
sys.path.insert(0, str(LIFECYCLE_DIR))
sys.path.insert(0, str(VALIDATION_DIR))

import check_context_budget  # noqa: E402
from selection_policy import policy_identity  # noqa: E402


class TestSkillsetProvenance(unittest.TestCase):
    """Verify that generated manifest hashes remain bound to canonical sources."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="skillset-provenance-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_rejects_stale_source_hash(self) -> None:
        repo_root = self.temp_dir / "repo"
        skill_path = repo_root / "Skills" / "agent-ops" / "sample-skill" / "SKILL.md"
        skill_path.parent.mkdir(parents=True)
        skill_path.write_text("# Sample skill\n", encoding="utf-8")
        manifest = self.temp_dir / ".skillsets" / "agent-ops" / "manifest.jsonl"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({
            "skill_set": "agent-ops",
            "source_path": "Skills/agent-ops/sample-skill/SKILL.md",
            "provenance": {
                "generator": "test",
                "projection_mode": "rooted",
                "policy_identity": policy_identity(),
                "source_revision": "test",
                "source_sha256": "0" * 64,
            },
        }) + "\n", encoding="utf-8")

        violations = check_context_budget.validate_written_manifest_provenance(
            skillsets_dir=self.temp_dir / ".skillsets",
            repo_root_path=repo_root,
        )

        self.assertIn("SKILLSET_SOURCE_HASH_STALE", {violation["code"] for violation in violations})
