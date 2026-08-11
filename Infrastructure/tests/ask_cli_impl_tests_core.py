import unittest
import subprocess
import json
import hashlib
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

sys.path.append(str(Path(__file__).resolve().parents[1] / "scripts" / "lib"))

from ask.cli_errors import build_helpful_error, build_unknown_action_result
from ask.command_metadata import VALID_ACTIONS

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_cli(cmd: list[str], **kwargs):
    kwargs.setdefault("cwd", REPO_ROOT)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30, **kwargs)


def _assert_readiness_overview_ready(
    testcase: unittest.TestCase,
    overview: dict,
    expected_sections: list[str],
) -> None:
    testcase.assertEqual(overview["contract_status"], "ready")
    testcase.assertTrue(overview["contract_ready"])
    testcase.assertEqual(overview["contract_gap_count"], 0)
    testcase.assertFalse(overview["has_contract_gaps"])
    testcase.assertEqual(overview["contract_section_count"], len(expected_sections))
    testcase.assertEqual(
        overview["contract_status_by_section"],
        {section: "ready" for section in expected_sections},
    )
    testcase.assertEqual(
        overview["contract_gap_count_by_section"],
        {section: 0 for section in expected_sections},
    )
    testcase.assertEqual(overview["ready_contract_sections"], expected_sections)
    testcase.assertEqual(overview["blocked_contract_sections"], [])


def _assert_contract_ready(testcase: unittest.TestCase, payload: dict) -> None:
    testcase.assertEqual(payload["contract_gap_count"], 0)
    testcase.assertFalse(payload["has_contract_gaps"])
    testcase.assertEqual(payload["contract_status"], "ready")
    testcase.assertTrue(payload["contract_ready"])


def _write_pass_closeout(tmp: str) -> Path:
    case_dir = Path(tmp) / "01-edge-case"
    case_dir.mkdir()
    (case_dir / "result.json").write_text('{"id":"edge-case","status":"pass"}\n', encoding="utf-8")
    closeout_path = Path(tmp) / "workflow-closeout.json"
    closeout_path.write_text(
        json.dumps(
            {
                "schema_version": "skills-sdk.eval-closeout.v1",
                "status": "pass",
                "skill_path": "Skills/example-skill",
                "mode": "smoke",
                "runner": "codex",
                "blocker_class": None,
                "report_dir": str(Path(tmp)),
                "cases": [{"id": "edge-case", "status": "pass", "result_path": str(case_dir)}],
                "mutation_allowed": False,
                "registry_update_allowed": False,
                "next_reproduce_command": "./bin/ask evals run Skills/example-skill --mode smoke --json --robot",
            }
        ),
        encoding="utf-8",
    )
    return closeout_path

class _AskCliTestBase(unittest.TestCase):
    pass

__all__ = [name for name in globals() if not name.startswith("__")]
