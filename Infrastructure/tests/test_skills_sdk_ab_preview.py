from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.eval_ab_preview import build_ab_preview_receipt  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_ab_preview_receipt  # noqa: E402


SKILL_A = "Infrastructure/tests/fixtures/skills_sdk/valid_skill"
SKILL_B = "Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill"
FIXTURE = "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/deterministic-eval-pass.json"
IDENTITY_A = {
    "skill_ir_schema_version": "skills-sdk.skill-ir.v0",
    "package_id": "skills-sdk-valid-fixture",
    "package_digest": f"sha256:{'1' * 64}",
}
IDENTITY_B = {
    "skill_ir_schema_version": "skills-sdk.skill-ir.v0",
    "package_id": "skills-sdk-scenario-quality-fixture",
    "package_digest": f"sha256:{'2' * 64}",
}


class TestSkillsSdkAbPreview(unittest.TestCase):
    def test_builder_records_cloud_judge_secret_as_judge_only(self) -> None:
        receipt = build_ab_preview_receipt(
            REPO_ROOT,
            skill_a=SKILL_A,
            skill_b=SKILL_B,
            fixture=FIXTURE,
            skill_a_identity=IDENTITY_A,
            skill_b_identity=IDENTITY_B,
            judge_profile_id="oss-cloud",
        )

        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["judge_profile"]["id"], "oss-cloud")
        self.assertEqual(receipt["judge_profile"]["model"], "deepseek-v4-flash:0731-cloud")
        self.assertEqual(receipt["secret_boundary"]["judge_env_secret_names"], ["OLLAMA_API_KEY"])
        self.assertEqual(receipt["secret_boundary"]["skill_execution_env_secret_names"], [])
        self.assertFalse(receipt["secret_boundary"]["skill_execution_receives_judge_secrets"])
        self.assertFalse(receipt["codex_exec_invoked"])
        self.assertFalse(receipt["provider_invoked"])
        validate_ab_preview_receipt(receipt)

    def test_cli_preview_returns_non_executing_ab_receipt(self) -> None:
        proc = subprocess.run(
            [
                str(REPO_ROOT / "bin/ask"),
                "sdk",
                "eval",
                "ab-preview",
                "--skill-a",
                SKILL_A,
                "--skill-b",
                SKILL_B,
                "--fixture",
                FIXTURE,
                "--preview",
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        receipt = payload["data"]["skills_sdk_eval_ab_preview"]["receipt"]
        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["skill_a"]["package_id"], "skills-sdk-valid-fixture")
        self.assertEqual(receipt["skill_b"]["package_id"], "skills-sdk-scenario-quality-fixture")
        self.assertEqual(receipt["execution_profile"]["id"], "codex-read-only")
        self.assertEqual(receipt["judge_profile"]["model"], "qwen3.5:9b-mlx")
        self.assertEqual(receipt["secret_boundary"]["skill_execution_env_secret_names"], [])
        self.assertFalse(receipt["codex_exec_invoked"])
        self.assertFalse(receipt["provider_invoked"])
        self.assertFalse(receipt["mutation_performed"])
        validate_ab_preview_receipt(receipt)

    def test_builder_returns_schema_valid_blocked_receipt_for_missing_fixture(self) -> None:
        receipt = build_ab_preview_receipt(
            REPO_ROOT,
            skill_a=SKILL_A,
            skill_b=SKILL_B,
            fixture="Infrastructure/tests/fixtures/skills_sdk/missing-ab-fixture.json",
            skill_a_identity=IDENTITY_A,
            skill_b_identity=IDENTITY_B,
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("fixture_missing", receipt["blockers"])
        self.assertIsNone(receipt["fixture"])
        validate_ab_preview_receipt(receipt)

    def test_builder_records_codex_fast_as_authenticated_network_judge(self) -> None:
        receipt = build_ab_preview_receipt(
            REPO_ROOT,
            skill_a=SKILL_A,
            skill_b=SKILL_B,
            fixture=FIXTURE,
            skill_a_identity=IDENTITY_A,
            skill_b_identity=IDENTITY_B,
            judge_profile_id="codex-fast",
        )

        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["judge_profile"]["model"], "gpt-5.3-codex-spark")
        self.assertTrue(receipt["judge_profile"]["network_required"])
        self.assertEqual(receipt["judge_profile"]["auth_boundary"], "codex_cli_auth")
        self.assertEqual(receipt["secret_boundary"]["skill_execution_env_secret_names"], [])
        self.assertFalse(receipt["secret_boundary"]["skill_execution_receives_judge_secrets"])
        validate_ab_preview_receipt(receipt)

    def test_typed_contract_rejects_preview_with_blockers(self) -> None:
        receipt = build_ab_preview_receipt(
            REPO_ROOT,
            skill_a=SKILL_A,
            skill_b=SKILL_B,
            fixture=FIXTURE,
            skill_a_identity=IDENTITY_A,
            skill_b_identity=IDENTITY_B,
        )
        receipt["blockers"] = ["unexpected_blocker"]

        with self.assertRaises(ValueError):
            validate_ab_preview_receipt(receipt)


if __name__ == "__main__":
    unittest.main()
