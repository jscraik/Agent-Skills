from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.eval_ab_plan import build_ab_plan_receipt  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_ab_plan_receipt  # noqa: E402


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


class TestSkillsSdkAbPlan(unittest.TestCase):
    def test_builder_records_codex_command_plan_without_invocation(self) -> None:
        receipt = build_ab_plan_receipt(
            REPO_ROOT,
            skill_a=SKILL_A,
            skill_b=SKILL_B,
            fixture=FIXTURE,
            skill_a_identity=IDENTITY_A,
            skill_b_identity=IDENTITY_B,
        )

        self.assertEqual(receipt["status"], "planned")
        self.assertEqual(receipt["execution_profile"]["id"], "codex-read-only")
        self.assertEqual(receipt["command_variant_labels"], ["A", "B"])
        self.assertEqual({plan["variant_label"] for plan in receipt["command_plan"]}, {"A", "B"})
        self.assertEqual(receipt["command_plan"][0]["command_argv"][:4], ["codex", "exec", "--sandbox", "read-only"])
        self.assertEqual(receipt["command_plan"][0]["approval_policy"], "on-request")
        self.assertIn("--ask-for-approval", receipt["command_plan"][0]["command_argv"])
        self.assertIn("--json", receipt["command_plan"][0]["command_argv"])
        self.assertEqual(
            receipt["command_plan"][0]["runner_stdout_capture_path"],
            receipt["command_plan"][0]["event_log_path"],
        )
        self.assertEqual(receipt["command_plan"][0]["planned_write_paths"], [receipt["command_plan"][0]["output_last_message_path"]])
        self.assertFalse(receipt["codex_exec_invoked"])
        self.assertFalse(receipt["provider_invoked"])
        self.assertFalse(receipt["network_accessed"])
        self.assertFalse(receipt["mutation_performed"])
        validate_ab_plan_receipt(receipt)

    def test_cli_plan_returns_non_executing_receipt(self) -> None:
        proc = subprocess.run(
            [
                str(REPO_ROOT / "bin/ask"),
                "sdk",
                "eval",
                "ab-plan",
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
        receipt = payload["data"]["skills_sdk_eval_ab_plan"]["receipt"]
        self.assertEqual(receipt["status"], "planned")
        self.assertEqual(receipt["execution_profile"]["id"], "codex-read-only")
        self.assertEqual(receipt["evidence_root"], ".harness/artifacts/sdk-ab-evals")
        self.assertEqual(receipt["command_variant_labels"], ["A", "B"])
        self.assertEqual(len(receipt["command_plan"]), 2)
        self.assertFalse(receipt["codex_exec_invoked"])
        validate_ab_plan_receipt(receipt)

    def test_builder_blocks_external_evidence_root(self) -> None:
        receipt = build_ab_plan_receipt(
            REPO_ROOT,
            skill_a=SKILL_A,
            skill_b=SKILL_B,
            fixture=FIXTURE,
            skill_a_identity=IDENTITY_A,
            skill_b_identity=IDENTITY_B,
            evidence_root="/tmp/sdk-ab-evals",
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("evidence_root_outside_repo", receipt["blockers"])
        self.assertEqual(receipt["command_plan"], [])
        validate_ab_plan_receipt(receipt)


if __name__ == "__main__":
    unittest.main()
