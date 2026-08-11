from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.phoenix_trace_plan import build_eval_trace_plan  # noqa: E402


class TestSkillsSdkPhoenixTraceProfiles(unittest.TestCase):
    def test_eval_trace_accepts_fast_smoke_profile_with_argv_proof(self) -> None:
        receipt = {
            "schema_version": "skills-sdk.eval-run-receipt.v0",
            "status": "pass",
            "operation": "eval_run",
            "runner": "codex",
            "mode": "smoke",
            "lane": "codex-fast-smoke",
            "codex_profile": "fast",
            "codex_exec_invoked": True,
            "codex_exec_command_shape": ["codex", "exec", "--profile", "fast", "--json", "-"],
        }

        plan = build_eval_trace_plan(receipt)

        self.assertEqual(plan["blockers"], [])
        self.assertEqual(plan["profile_evidence"][0]["derived_codex_profile"], "fast")

    def test_eval_trace_rejects_fast_profile_for_release_proof(self) -> None:
        receipt = {
            "schema_version": "skills-sdk.eval-run-receipt.v0",
            "status": "pass",
            "operation": "eval_run",
            "runner": "codex",
            "mode": "release",
            "lane": "codex-release",
            "codex_profile": "fast",
            "codex_exec_invoked": True,
            "codex_exec_command_shape": ["codex", "exec", "--profile", "fast", "--json", "-"],
        }

        plan = build_eval_trace_plan(receipt)

        self.assertIn("profile_unsupported:fast", plan["blockers"])
