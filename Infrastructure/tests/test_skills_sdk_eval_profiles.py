from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.eval_profiles import build_eval_profile_preview_receipt  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_eval_profile_preview_receipt  # noqa: E402


class TestSkillsSdkEvalProfiles(unittest.TestCase):
    def test_preview_receipt_keeps_judge_secrets_out_of_skill_execution(self) -> None:
        receipt = build_eval_profile_preview_receipt()

        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["execution_boundary"], "codex_exec_sandbox")
        self.assertEqual(receipt["external_intake_boundary"], "sdk_quarantine_only")
        self.assertEqual(receipt["secret_boundary"]["skill_execution_env_secret_names"], [])
        self.assertFalse(receipt["secret_boundary"]["skill_execution_receives_judge_secrets"])
        validate_eval_profile_preview_receipt(receipt)

    def test_preview_receipt_declares_selected_ollama_models(self) -> None:
        receipt = build_eval_profile_preview_receipt()
        judge_by_id = {profile["id"]: profile for profile in receipt["judge_profiles"]}

        self.assertEqual(judge_by_id["oss-local"]["model"], "qwen3.5:latest")
        self.assertEqual(judge_by_id["oss-local"]["host"], "http://localhost:11434")
        self.assertTrue(judge_by_id["oss-local"]["network_required"])
        self.assertEqual(judge_by_id["oss-local"]["auth_boundary"], "none")
        self.assertEqual(judge_by_id["oss-cloud"]["model"], "deepseek-v4-flash:cloud")
        self.assertEqual(judge_by_id["oss-cloud"]["host"], "https://ollama.com")
        self.assertTrue(judge_by_id["oss-cloud"]["network_required"])
        self.assertEqual(judge_by_id["oss-cloud"]["secret_env_names"], ["OLLAMA_API_KEY"])
        self.assertEqual(judge_by_id["oss-cloud"]["auth_boundary"], "env_secret")
        self.assertEqual(judge_by_id["codex-fast"]["model"], "gpt-5.3-codex-spark")
        self.assertEqual(judge_by_id["codex-fast"]["host"], "codex-cli-authenticated-session")
        self.assertTrue(judge_by_id["codex-fast"]["network_required"])
        self.assertEqual(judge_by_id["codex-fast"]["auth_boundary"], "codex_cli_auth")

    def test_cli_preview_returns_non_mutating_receipt(self) -> None:
        proc = subprocess.run(
            [
                str(REPO_ROOT / "bin/ask"),
                "sdk",
                "eval",
                "profiles",
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
        receipt = payload["data"]["skills_sdk_eval_profiles"]["receipt"]
        self.assertFalse(receipt["mutation_performed"])
        self.assertFalse(receipt["network_accessed"])
        self.assertFalse(receipt["provider_invoked"])
        validate_eval_profile_preview_receipt(receipt)


if __name__ == "__main__":
    unittest.main()
