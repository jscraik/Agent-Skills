import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"
sys.path.insert(0, str(SCRIPT_DIR))

import route_skillset  # noqa: E402


class TestRouteSkillset(unittest.TestCase):
    def test_sdk_tessl_skill_hardening_prefers_skill_builder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skillsets_dir = Path(tmp)
            manifest_dir = skillsets_dir / "skill-factory"
            manifest_dir.mkdir(parents=True)
            rows = [
                {
                    "id": "skill-builder",
                    "description": "Improve skill SDK and Tessl eval readiness.",
                    "level": "compound",
                    "source_path": "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md",
                    "triggers": [],
                },
                {
                    "id": "skill-factory-router",
                    "description": "Route generic skill factory work.",
                    "level": "compound",
                    "source_path": "Plugins/skill-factory/skills/skill-factory-router/SKILL.md",
                    "triggers": [],
                },
            ]
            (manifest_dir / "manifest.jsonl").write_text(
                "\n".join(json.dumps(row) for row in rows) + "\n",
                encoding="utf-8",
            )

            result = route_skillset.route(
                "skill-factory",
                "harden the skill eval pipeline",
                skillsets_dir=skillsets_dir,
            )

        self.assertEqual(result["status"], "selected")
        self.assertEqual(result["selected"]["id"], "skill-builder")
        self.assertIn("explicit precedence", result["candidates"][0]["reason"])


if __name__ == "__main__":
    unittest.main()
