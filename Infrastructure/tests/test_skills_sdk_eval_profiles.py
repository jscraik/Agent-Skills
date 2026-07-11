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


def _judge_by_id() -> dict[str, dict[str, object]]:
    receipt = build_eval_profile_preview_receipt()
    return {profile["id"]: profile for profile in receipt["judge_profiles"]}


def _assert_qwen_local_profile(test: unittest.TestCase, profile: dict[str, object]) -> None:
    test.assertEqual(profile["provider"], "codex")
    test.assertEqual(profile["codex_profile"], "oss-local")
    test.assertEqual(profile["model"], "qwen3.5:9b-mlx")
    test.assertEqual(profile["model_role"], "local_sandbox_eval_default")
    test.assertEqual(profile["model_settings"]["num_ctx"], 8192)
    test.assertEqual(profile["model_settings"]["num_predict"], 1024)
    test.assertEqual(profile["runtime_metadata"]["model_id"], "203e30078279")
    test.assertEqual(profile["runtime_metadata"]["architecture"], "qwen3_5")
    test.assertEqual(profile["runtime_metadata"]["quantization"], "nvfp4")
    test.assertEqual(profile["smoke_guard"]["max_tokens_used"], 7000)
    test.assertTrue(profile["smoke_guard"]["forbid_visible_thinking"])
    test.assertTrue(profile["smoke_guard"]["allow_codex_jsonl_reasoning_events"])
    test.assertTrue(profile["smoke_guard"]["forbid_fallback_metadata"])


def _assert_cloud_profile(test: unittest.TestCase, profile: dict[str, object]) -> None:
    test.assertEqual(profile["provider"], "codex")
    test.assertEqual(profile["model"], "minimax-m2.7:cloud")
    test.assertEqual(profile["host"], "codex-cli-profile")
    test.assertTrue(profile["network_required"])
    test.assertEqual(profile["secret_env_names"], ["OLLAMA_API_KEY"])
    test.assertEqual(profile["auth_boundary"], "codex_cli_auth")


class TestSkillsSdkEvalProfiles(unittest.TestCase):
    def test_preview_receipt_keeps_judge_secrets_out_of_skill_execution(self) -> None:
        receipt = build_eval_profile_preview_receipt()

        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["execution_boundary"], "codex_exec_sandbox")
        self.assertEqual(receipt["external_intake_boundary"], "sdk_quarantine_only")
        self.assertEqual(receipt["secret_boundary"]["skill_execution_env_secret_names"], [])
        self.assertFalse(receipt["secret_boundary"]["skill_execution_receives_judge_secrets"])
        validate_eval_profile_preview_receipt(receipt)

    def test_preview_receipt_declares_codex_backed_oss_profiles(self) -> None:
        judge_by_id = _judge_by_id()
        _assert_qwen_local_profile(self, judge_by_id["oss-local"])

        self.assertEqual(judge_by_id["oss-local"]["model_settings"]["temperature"], 0.1)
        self.assertEqual(judge_by_id["oss-local"]["model_settings"]["top_p"], 0.9)
        self.assertEqual(judge_by_id["oss-local"]["host"], "codex-cli-profile")
        self.assertTrue(judge_by_id["oss-local"]["network_required"])
        self.assertEqual(judge_by_id["oss-local"]["auth_boundary"], "none")
        self.assertEqual(judge_by_id["oss-local-large-transcript"]["model"], "qwen3.5:9b-mlx")
        self.assertEqual(judge_by_id["oss-local-large-transcript"]["model_role"], "larger_local_transcript_trial")
        self.assertEqual(judge_by_id["oss-local-large-transcript"]["model_settings"]["num_ctx"], 16384)
        self.assertEqual(judge_by_id["oss-local-large-transcript"]["model_settings"]["num_predict"], 1536)
        self.assertEqual(judge_by_id["oss-local-code"]["codex_profile"], "oss-local-code")
        self.assertEqual(judge_by_id["oss-local-code"]["model"], "qwen3-coder:30b")
        self.assertEqual(judge_by_id["oss-local-code"]["model_role"], "code_heavy_specialist")
        self.assertEqual(judge_by_id["oss-local-fallback"]["codex_profile"], "oss-local-fallback")
        self.assertEqual(judge_by_id["oss-local-fallback"]["model"], "qwen3.5:latest")
        self.assertEqual(judge_by_id["oss-local-fallback"]["model_role"], "fast_fallback")
        self.assertEqual(judge_by_id["oss-security"]["codex_profile"], "oss-security")
        self.assertEqual(judge_by_id["oss-security"]["model"], "CyberCrew/notmythos-8b")
        self.assertEqual(judge_by_id["oss-security"]["model_role"], "local_security_specialist")
        self.assertEqual(judge_by_id["oss-security"]["model_settings"]["temperature"], 0.35)
        self.assertEqual(judge_by_id["oss-security"]["model_settings"]["top_k"], 40)
        self.assertEqual(judge_by_id["oss-security"]["auth_boundary"], "none")
        _assert_cloud_profile(self, judge_by_id["oss-cloud"])
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
