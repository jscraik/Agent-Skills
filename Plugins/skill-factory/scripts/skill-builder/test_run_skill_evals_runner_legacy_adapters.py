#!/usr/bin/env python3
"""Regression coverage for legacy runner keyword adapters."""

from __future__ import annotations

import importlib
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

existing_runner = sys.modules.get("run_skill_evals")
if existing_runner is not None:
    existing_path = Path(str(getattr(existing_runner, "__file__", ""))).resolve()
    if existing_path.parent != SCRIPT_DIR:
        del sys.modules["run_skill_evals"]

run_skill_evals = importlib.import_module("run_skill_evals")


class LegacyRunnerAdapterTests(unittest.TestCase):
    def test_keyword_adapters_preserve_alt_and_openai_transports(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            completed = unittest.mock.Mock(returncode=0, stdout="done", stderr="")
            with unittest.mock.patch("run_skill_evals.sp.run", return_value=completed):
                alt_result = run_skill_evals.run_alt_codex_exec(
                    workspace_root=workspace_root,
                    prompt="Route only.",
                    output_last_message_path=workspace_root / "alt.txt",
                    codex_bin=None,
                    output_format="text",
                    settings_path=None,
                    cli_command=None,
                    timeout_sec=1,
                    timeout_profile="default",
                    extra_codex_args=None,
                )
                openai_result = run_skill_evals.run_openai_exec(
                    workspace_root=workspace_root,
                    prompt="Route only.",
                    output_last_message_path=workspace_root / "openai.txt",
                    openai_bin=None,
                    output_format="text",
                    timeout_sec=1,
                    timeout_profile="default",
                    extra_openai_args=None,
                )

        self.assertEqual(alt_result, (0, "done", ""))
        self.assertEqual(openai_result, (0, "done", ""))


if __name__ == "__main__":
    unittest.main()
