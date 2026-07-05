from __future__ import annotations

import importlib.util
import io
import json
import os
import shlex
import subprocess
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stdout
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "Infrastructure/scripts/validation-and-linting/run_oss_security_codex_exec_lane.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("run_oss_security_codex_exec_lane", SCRIPT)
assert SPEC is not None
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
PASSING_RECEIPT_REVIEWER = textwrap.dedent(
    """
    import json
    import sys
    from pathlib import Path

    args = sys.argv
    prompt = sys.stdin.read()
    digest = prompt.split('"security_lane_digest": "')[1].split('"', 1)[0]
    last_path = Path(args[args.index("--output-last-message") + 1])
    last_path.write_text(json.dumps({
        "schema_version": "skills-sdk.oss-security-review-input.v0",
        "review_status": "pass",
        "risk_summary": "reviewed deterministic receipt",
        "required_followups": [],
        "evidence_digest_seen": digest,
        "reviewer_model_boundary": "static receipt review only"
    }), encoding="utf-8")
    print(json.dumps({"type": "turn.completed"}))
    raise SystemExit(0)
    """
)
PASSING_LANE_RUNNER = textwrap.dedent(
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
)


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
        capture_output=True,
        check=False,
    )


def _run_receipt_first(root: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--target",
            "Infrastructure/tests/fixtures/skills_sdk/valid_skill",
            "--output-dir",
            str(root / "out"),
            "--mode",
            "receipt-first",
            "--json",
        ],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def _sandbox_env(root: Path, bin_dir: Path) -> dict[str, str]:
    configs_root = root / "configs" / "codex"
    configs_root.mkdir(parents=True)
    (configs_root / "config.toml").write_text("", encoding="utf-8")
    (configs_root / "oss-security.config.toml").write_text(
        'model = "h4rithd/coder:14b"\n',
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
    env["XDG_CACHE_HOME"] = str(root / "xdg-cache")
    env["UV_CACHE_DIR"] = str(root / "uv-cache")
    env["ASK_OSS_SECURITY_CONFIGS_ROOT"] = str(configs_root)
    return env


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
            env = _sandbox_env(root, bin_dir)

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
            env = _sandbox_env(root, bin_dir)

            process = _run(root, env)

        self.assertEqual(process.returncode, 0, process.stdout)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["classification"]["lane_success_seen"])
        self.assertEqual(payload["codex_profile"], "oss-security")

    def test_receipt_first_runner_passes_with_digest_matching_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bin_dir = _fake_codex(root, PASSING_RECEIPT_REVIEWER)
            env = _sandbox_env(root, bin_dir)

            process = _run_receipt_first(root, env)

        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["mode"], "receipt_first")
        self.assertEqual(payload["deterministic_lane_status"], "pass")
        self.assertEqual(payload["review_validation"]["status"], "pass")

    def test_receipt_first_runner_blocks_when_review_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bin_dir = _fake_codex(
                root,
                textwrap.dedent(
                    """
                    import sys
                    from pathlib import Path

                    args = sys.argv
                    sys.stdin.read()
                    last_path = Path(args[args.index("--output-last-message") + 1])
                    last_path.write_text("not json", encoding="utf-8")
                    raise SystemExit(0)
                    """
                ),
            )
            env = _sandbox_env(root, bin_dir)

            process = _run_receipt_first(root, env)

        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["review_validation"]["status"], "blocked")
        self.assertIn("oss-security profile did not produce", payload["blockers"][0])

    def test_prompt_shell_quotes_target_inside_json_encoded_exec_source(self) -> None:
        target = "Skills/example with spaces/quote'\nnext"
        quoted_target = shlex.quote(target)

        prompt = MODULE._prompt(target)

        self.assertIn(
            json.dumps(
                f"./bin/ask sdk security run-lane {quoted_target} --preview --profile oss-security --json --robot"
            ),
            prompt,
        )

    def test_codex_command_json_quotes_model_overrides(self) -> None:
        command = MODULE._codex_command(
            sandbox="read-only",
            last_message_path=Path("/tmp/out.txt"),
            model='local/model"withquote',
            model_catalog_json='{"model":"x"}',
        )

        self.assertIn('-c', command)
        self.assertIn('model="local/model\\"withquote"', command)
        self.assertIn('model_catalog_json="{\\"model\\":\\"x\\"}"', command)

    def test_auto_created_output_dir_is_cleaned_after_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bin_dir = _fake_codex(root, PASSING_LANE_RUNNER)
            env = _sandbox_env(root, bin_dir)
            created_paths: list[Path] = []
            original_mkdtemp = MODULE.tempfile.mkdtemp

            def fake_mkdtemp(*, prefix: str) -> str:
                path = Path(original_mkdtemp(prefix=prefix, dir=root))
                created_paths.append(path)
                return str(path)

            MODULE.tempfile.mkdtemp = fake_mkdtemp
            original_env = os.environ.copy()
            os.environ.update(env)
            try:
                with redirect_stdout(io.StringIO()):
                    exit_code = MODULE.main(["--target", "Infrastructure/tests/fixtures/skills_sdk/valid_skill", "--json"])
            finally:
                MODULE.tempfile.mkdtemp = original_mkdtemp
                os.environ.clear()
                os.environ.update(original_env)

        self.assertEqual(exit_code, 0)
        self.assertEqual(len(created_paths), 1)
        self.assertFalse(created_paths[0].exists())


if __name__ == "__main__":
    unittest.main()
