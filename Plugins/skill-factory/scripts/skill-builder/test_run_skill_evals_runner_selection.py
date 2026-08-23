#!/usr/bin/env python3
"""Regression tests for optional runner selection."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_skill_evals_workflow  # noqa: E402


class RunSkillEvalsRunnerSelectionTests(unittest.TestCase):
    def test_openai_run_ignores_unselected_codex_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = SimpleNamespace(
                workspace=tmp,
                codex_home=None,
                codex_bin=None,
                openai_bin=None,
                runners=["openai"],
                dual_run=False,
                smoke=False,
                runner="openai",
                codex_kimi_command="codex",
                codex_zai_command="codex",
                codex_kimi_settings="missing-kimi.json",
                codex_zai_settings="missing-zai.json",
                codex_fallback_profile=None,
            )
            context = {"args": args, "skill_dir": Path(tmp)}

            run_skill_evals_workflow._configure_execution(context)

            self.assertEqual(context["selected_runners"], ["openai"])
            self.assertIsNone(context["codex_kimi_settings"])
            self.assertIsNone(context["codex_zai_settings"])


if __name__ == "__main__":
    unittest.main()
