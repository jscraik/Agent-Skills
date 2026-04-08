#!/usr/bin/env python3
"""Regression tests for repo-wide skill quality artifact generation."""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_repo_skill_quality


class RunRepoSkillQualityTests(unittest.TestCase):
    def test_merge_sarif_reports_combines_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            one = tmp / "one.sarif"
            two = tmp / "two.sarif"
            out = tmp / "merged.sarif"
            one.write_text(json.dumps({"version": "2.1.0", "runs": [{"tool": {"driver": {"name": "one"}}}]}), encoding="utf-8")
            two.write_text(json.dumps({"version": "2.1.0", "runs": [{"tool": {"driver": {"name": "two"}}}]}), encoding="utf-8")

            payload = run_repo_skill_quality.merge_sarif_reports([one, two], out)
            merged = json.loads(out.read_text(encoding="utf-8"))

            self.assertEqual(payload["run_count"], 2)
            self.assertEqual(len(merged["runs"]), 2)
            self.assertTrue(out.exists())

    def test_main_writes_repo_artifacts_and_threads_report_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_dir = root / "utilities" / "codex-agent-creator"
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: codex-agent-builder
description: Test skill
---

# Test
""",
                encoding="utf-8",
            )

            recorded_commands = []

            def fake_run_cmd(cmd: list[str], cwd: Path):
                recorded_commands.append(cmd)
                script_name = Path(cmd[1]).name
                if script_name == "skill_gate.py":
                    output_path = Path(cmd[cmd.index("--output") + 1])
                    sarif_path = Path(cmd[cmd.index("--sarif-out") + 1])
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(
                        json.dumps({"skill": "codex-agent-builder", "decision": "pass", "exit_code": 0}),
                        encoding="utf-8",
                    )
                    sarif_path.write_text(
                        json.dumps({"version": "2.1.0", "runs": [{"tool": {"driver": {"name": "skill_gate"}}}]}),
                        encoding="utf-8",
                    )
                    return type("Proc", (), {"returncode": 0, "stdout": "{}", "stderr": ""})()
                if script_name == "run_skill_evals.py":
                    scorecard_path = Path(cmd[cmd.index("--scorecard-out") + 1])
                    junit_path = Path(cmd[cmd.index("--junit-out") + 1])
                    scorecard_path.parent.mkdir(parents=True, exist_ok=True)
                    scorecard_path.write_text(
                        json.dumps({"skill": "codex-agent-builder", "cases": [], "tier1_failures": 0}),
                        encoding="utf-8",
                    )
                    junit_path.write_text(
                        "<?xml version='1.0' encoding='utf-8'?><testsuite tests='0' failures='0' />",
                        encoding="utf-8",
                    )
                    return type("Proc", (), {"returncode": 0, "stdout": "{}", "stderr": ""})()
                if script_name == "ci_skill_quality_gate.py":
                    return type(
                        "Proc",
                        (),
                        {"returncode": 0, "stdout": json.dumps({"passed": True, "scorecards": []}), "stderr": ""},
                    )()
                if script_name == "benchmark_skill_portfolio.py":
                    return type(
                        "Proc",
                        (),
                        {"returncode": 0, "stdout": json.dumps({"passed": True, "warnings": []}), "stderr": ""},
                    )()
                raise AssertionError(f"Unexpected command: {cmd}")

            argv = [
                "run_repo_skill_quality.py",
                "--root",
                str(root),
                "--run-evals",
                "--benchmark-mode",
                "warn",
                "--format",
                "json",
            ]

            stdout = io.StringIO()
            with patch.object(run_repo_skill_quality, "find_skill_dirs", return_value=[skill_dir]):
                with patch.object(run_repo_skill_quality, "choose_python", return_value=sys.executable):
                    with patch.object(run_repo_skill_quality, "run_cmd", side_effect=fake_run_cmd):
                        with patch.object(sys, "argv", argv):
                            with redirect_stdout(stdout):
                                exit_code = run_repo_skill_quality.main()

            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(len(payload["structure_reports"]), 1)
            self.assertEqual(len(payload["structure_sarif_reports"]), 1)
            self.assertEqual(len(payload["scorecards"]), 1)
            self.assertEqual(len(payload["eval_junit_reports"]), 1)
            self.assertTrue(Path(payload["aggregate_sarif"]).exists())
            self.assertTrue(Path(payload["repo_artifact_index"]).exists())

            skill_gate_cmd = next(cmd for cmd in recorded_commands if Path(cmd[1]).name == "skill_gate.py")
            self.assertIn("--sarif-out", skill_gate_cmd)
            eval_cmd = next(cmd for cmd in recorded_commands if Path(cmd[1]).name == "run_skill_evals.py")
            self.assertIn("--junit-out", eval_cmd)
            expected_reports_suffix = Path("artifacts/reports/skills/codex-agent-builder")
            self.assertTrue(
                any(expected_reports_suffix.as_posix() in value for value in skill_gate_cmd),
                msg=f"expected canonical reports dir in skill gate command: {skill_gate_cmd}",
            )
            self.assertTrue(
                any(expected_reports_suffix.as_posix() in value for value in eval_cmd),
                msg=f"expected canonical reports dir in eval command: {eval_cmd}",
            )


if __name__ == "__main__":
    unittest.main()
