from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "Infrastructure/scripts/validation-and-linting/run_oss_security_codex_exec_lane.py"


def _fake_codex(root: Path, body: str) -> Path:
    bin_dir = root / "bin"
    bin_dir.mkdir()
    codex = bin_dir / "codex"
    codex.write_text("#!/usr/bin/env python3\n" + body, encoding="utf-8")
    codex.chmod(0o755)
    return bin_dir


def _run(root: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--target",
            "Infrastructure/tests/fixtures/skills_sdk/valid_skill",
            "--output-dir",
            str(root / "out"),
            "--json",
        ],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class TestRunOssSecurityCodexExecLane(unittest.TestCase):
    def test_runner_blocks_when_codex_model_does_not_emit_lane_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bin_dir = _fake_codex(
                root,
                textwrap.dedent(
                    """
                    import sys
                    sys.stdin.read()
                    print('Reading prompt from stdin...')
                    print('ERROR codex_core::tools::router: error=Fatal error: tool exec invoked with incompatible payload')
                    raise SystemExit(0)
                    """
                ),
            )
            env = os.environ.copy()
            env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"

            process = _run(root, env)

        self.assertEqual(process.returncode, 2, process.stdout)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["classification"]["blocker"], "model_tool_call_payload")
        self.assertEqual(payload["codex_exit_code"], 0)

    def test_runner_passes_when_codex_output_contains_security_lane_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bin_dir = _fake_codex(
                root,
                textwrap.dedent(
                    """
                    import json
                    import sys
                    sys.stdin.read()
                    print(json.dumps({
                        'status': 'success',
                        'data': {'skills_sdk_security_lane': {'status': 'pass'}}
                    }))
                    raise SystemExit(0)
                    """
                ),
            )
            env = os.environ.copy()
            env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"

            process = _run(root, env)

        self.assertEqual(process.returncode, 0, process.stdout)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["classification"]["lane_success_seen"])
        self.assertEqual(payload["codex_profile"], "oss-security")


if __name__ == "__main__":
    unittest.main()
