import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.commands.skills_impl import skills_profiles  # noqa: E402


class TestAskSkillsProfiles(unittest.TestCase):
    def test_profiles_lists_skill_operation_modes(self) -> None:
        result = skills_profiles(REPO_ROOT)

        self.assertEqual(result.status, "success")
        payload = result.data["skill_profiles"]
        self.assertEqual(payload["schema_version"], "skill-operation-profiles.v1")
        self.assertEqual(payload["status"], "pass")
        self.assertIsNone(payload["selected_profile"])
        self.assertEqual(payload["profile_model"], "profile-v2-inspired")
        self.assertEqual(payload["workspace_roots"]["repo_root"], str(REPO_ROOT))
        self.assertIn("Skills", payload["workspace_roots"]["canonical_skill_roots"])
        self.assertIn(".agents/skills", payload["workspace_roots"]["runtime_projection_roots"])
        self.assertIn("authoring", payload["profiles"])
        self.assertIn("eval", payload["profiles"])
        self.assertIn("live-mutation", payload["profiles"])

    def test_profiles_can_return_one_profile(self) -> None:
        result = skills_profiles(REPO_ROOT, profile="eval")

        self.assertEqual(result.status, "success")
        payload = result.data["skill_profiles"]
        self.assertEqual(payload["selected_profile"], "eval")
        self.assertEqual(list(payload["profiles"]), ["eval"])
        self.assertIn("timeout_no_output", payload["profiles"]["eval"]["stop_conditions"])
        self.assertEqual(
            payload["profiles"]["eval"]["effective_roots"],
            ["Skills/**", "Infrastructure/workouts/**", "Infrastructure/artifacts/**"],
        )
        payload["profiles"]["eval"]["effective_roots"].append("tmp/**")
        self.assertNotIn("tmp/**", payload["profiles"]["eval"]["allowed_roots"])

    def test_profiles_blocks_unknown_profile(self) -> None:
        result = skills_profiles(REPO_ROOT, profile="unknown-mode")

        self.assertEqual(result.status, "error")
        payload = result.data["skill_profiles"]
        self.assertEqual(payload["status"], "blocked")
        self.assertIsNone(payload["selected_profile"])
        self.assertIn("authoring", payload["available_profiles"])
        self.assertTrue(result.errors)


if __name__ == "__main__":
    unittest.main()
