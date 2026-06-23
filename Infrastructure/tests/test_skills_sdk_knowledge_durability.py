import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.knowledge_durability import build_knowledge_durability_receipt  # noqa: E402


class TestSkillsSdkKnowledgeDurability(unittest.TestCase):
    def test_blocks_cache_owned_skill_without_durable_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            cache_skill = repo_root / "plugins/cache/demo/1.0.0/skills/example"
            references = cache_skill / "references"
            references.mkdir(parents=True)
            (cache_skill / "SKILL.md").write_text("# Example\n", encoding="utf-8")
            (references / "knowledge-capsule.manifest.yaml").write_text("capsules: []\n", encoding="utf-8")
            (references / "knowledge-capsule-routing.md").write_text("# Routing\n", encoding="utf-8")

            receipt = build_knowledge_durability_receipt(repo_root, skill=str(cache_skill))

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("durable_plugin_source_exists", {item["id"] for item in receipt["blockers"]})

    def test_passes_when_cache_and_durable_source_both_carry_knowledge_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            cache_skill = repo_root / "plugins/cache/demo/1.0.0/skills/example"
            source_skill = repo_root / "plugins/demo/skills/example"
            for skill_dir in (cache_skill, source_skill):
                references = skill_dir / "references"
                references.mkdir(parents=True)
                (skill_dir / "SKILL.md").write_text("# Example\n", encoding="utf-8")
                (references / "knowledge-capsule.manifest.yaml").write_text("capsules: []\n", encoding="utf-8")
                (references / "knowledge-capsule-routing.md").write_text("# Routing\n", encoding="utf-8")

            receipt = build_knowledge_durability_receipt(repo_root, skill=str(cache_skill))

        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["blockers"], [])
        self.assertTrue(receipt["cache_owned"])

    def test_detects_namespaced_plugin_cache_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            cache_skill = repo_root / "plugins/cache/agent-skills-local/demo/1.0.0/skills/example"
            source_skill = repo_root / "plugins/demo/skills/example"
            for skill_dir in (cache_skill, source_skill):
                references = skill_dir / "references"
                references.mkdir(parents=True)
                (skill_dir / "SKILL.md").write_text("# Example\n", encoding="utf-8")
                (references / "knowledge-capsule.manifest.yaml").write_text("capsules: []\n", encoding="utf-8")
                (references / "knowledge-capsule-routing.md").write_text("# Routing\n", encoding="utf-8")

            receipt = build_knowledge_durability_receipt(repo_root, skill=str(cache_skill))

        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["durable_source_path"], "plugins/demo/skills/example")
        self.assertTrue(receipt["cache_owned"])


if __name__ == "__main__":
    unittest.main()
