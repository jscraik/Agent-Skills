from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "Infrastructure/scripts/validation-and-linting/classify_codex_exec_security_lane.py"


def _write_jsonl(root: Path, name: str, lines: list[str]) -> Path:
    path = root / name
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _run(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(path), "--json"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class TestClassifyCodexExecSecurityLane(unittest.TestCase):
    def test_classifies_app_server_startup_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = _write_jsonl(
                Path(temp_dir),
                "startup.jsonl",
                ["Error: failed to initialize in-process app-server client: Operation not permitted (os error 1)"],
            )

            process = _run(path)

        self.assertEqual(process.returncode, 2)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["blocker"], "codex_app_server_startup")
        self.assertTrue(payload["startup_failed"])

    def test_classifies_incompatible_tool_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = _write_jsonl(
                Path(temp_dir),
                "tool.jsonl",
                [
                    '{"type":"thread.started","thread_id":"t"}',
                    "ERROR codex_core::tools::router: error=Fatal error: tool exec invoked with incompatible payload",
                    '{"type":"item.completed","item":{"type":"agent_message","text":"could not run"}}',
                ],
            )

            process = _run(path)

        self.assertEqual(process.returncode, 2)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["blocker"], "model_tool_call_payload")
        self.assertTrue(payload["incompatible_payload"])

    def test_requires_receipt_for_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = _write_jsonl(
                Path(temp_dir),
                "pass.jsonl",
                [
                    '{"type":"thread.started","thread_id":"t"}',
                    '{"status":"success","data":{"skills_sdk_security_lane":{"status":"pass"}}}',
                ],
            )

            process = _run(path)

        self.assertEqual(process.returncode, 0, process.stdout)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["lane_success_seen"])


if __name__ == "__main__":
    unittest.main()
