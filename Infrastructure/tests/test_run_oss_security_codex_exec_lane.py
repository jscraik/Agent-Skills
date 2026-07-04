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
PASSING_RECEIPT_REVIEWER = textwrap.dedent(
    """
    import json
    import os
    import sys
    from pathlib import Path

    args = sys.argv
    prompt = sys.stdin.read()
    assert os.environ.get("MISE_TRUSTED_CONFIG_PATHS", "").endswith(".mise.toml")
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


def _receipt_reviewer(review_status: str) -> str:
    return textwrap.dedent(
        f"""
        import json
        import sys
        from pathlib import Path

        args = sys.argv
        prompt = sys.stdin.read()
        digest = prompt.split('"security_lane_digest": "')[1].split('"', 1)[0]
        last_path = Path(args[args.index("--output-last-message") + 1])
        last_path.write_text(json.dumps({{
            "schema_version": "skills-sdk.oss-security-review-input.v0",
            "review_status": "{review_status}",
            "risk_summary": "reviewed deterministic receipt",
            "required_followups": ["triage model review"],
            "evidence_digest_seen": digest,
            "reviewer_model_boundary": "static receipt review only"
        }}), encoding="utf-8")
        print(json.dumps({{"type": "turn.completed"}}))
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
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
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
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _run_receipt_first_with_model(root: Path, env: dict[str, str], model: str) -> subprocess.CompletedProcess[str]:
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
            "--model",
            model,
            "--json",
        ],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _sandbox_env(root: Path, bin_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
    env["XDG_CACHE_HOME"] = str(root / "xdg-cache")
    env["UV_CACHE_DIR"] = str(root / "uv-cache")
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

    def test_receipt_first_runner_passes_with_digest_matching_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bin_dir = _fake_codex(root, PASSING_RECEIPT_REVIEWER)
            env = _sandbox_env(root, bin_dir)

            process = _run_receipt_first(root, env)

        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["process_status"], "pass")
        self.assertEqual(payload["mode"], "receipt_first")
        self.assertEqual(payload["deterministic_lane_status"], "pass")
        self.assertEqual(payload["review_extraction_status"], "pass")
        self.assertEqual(payload["model_review_status"], "pass")
        self.assertEqual(payload["security_decision"], "accepted_with_receipt")
        self.assertEqual(payload["security_decision_source"], "model_review_pass")
        self.assertEqual(payload["security_model"], "h4rithd/coder:14b")
        self.assertEqual(payload["review_prompt_contract_version"], "skills-sdk.oss-security-review-prompt.v1")
        self.assertLess(payload["review_input_bytes"], payload["review_input_compact_limit_bytes"])
        self.assertTrue(payload["review_input_compact"])
        self.assertEqual(payload["review_validation"]["status"], "pass")

    def test_receipt_first_runner_blocks_non_security_model_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bin_dir = _fake_codex(root, PASSING_RECEIPT_REVIEWER)
            env = _sandbox_env(root, bin_dir)

            process = _run_receipt_first_with_model(root, env, "qwen3.5:9b-mlx")

        self.assertEqual(process.returncode, 3, process.stdout + process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["process_status"], "blocked")
        self.assertEqual(payload["security_decision"], "blocked")
        self.assertEqual(payload["security_decision_source"], "security_model_policy_violation")
        self.assertEqual(payload["security_model"], "h4rithd/coder:14b")
        self.assertIn("only allows h4rithd/coder:14b", payload["blockers"][0])

    def test_receipt_first_runner_warn_needs_triage_without_process_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bin_dir = _fake_codex(root, _receipt_reviewer("warn"))
            env = _sandbox_env(root, bin_dir)

            process = _run_receipt_first(root, env)

        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["process_status"], "pass")
        self.assertEqual(payload["review_extraction_status"], "pass")
        self.assertEqual(payload["model_review_status"], "warn")
        self.assertEqual(payload["security_decision"], "needs_triage")
        self.assertEqual(payload["security_decision_source"], "model_review_warn_requires_triage")
        self.assertIn("warnings that require triage", payload["blockers"][0])

    def test_receipt_first_runner_fail_blocks_security_decision_without_process_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bin_dir = _fake_codex(root, _receipt_reviewer("fail"))
            env = _sandbox_env(root, bin_dir)

            process = _run_receipt_first(root, env)

        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["process_status"], "pass")
        self.assertEqual(payload["review_extraction_status"], "pass")
        self.assertEqual(payload["model_review_status"], "fail")
        self.assertEqual(payload["security_decision"], "blocked")
        self.assertEqual(payload["security_decision_source"], "model_review_fail_requires_triage")
        self.assertIn("blocks security readiness", payload["blockers"][0])

    def test_receipt_first_runner_model_blocked_blocks_security_decision_without_process_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bin_dir = _fake_codex(root, _receipt_reviewer("blocked"))
            env = _sandbox_env(root, bin_dir)

            process = _run_receipt_first(root, env)

        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["process_status"], "pass")
        self.assertEqual(payload["review_extraction_status"], "pass")
        self.assertEqual(payload["model_review_status"], "blocked")
        self.assertEqual(payload["security_decision"], "blocked")
        self.assertEqual(payload["security_decision_source"], "model_review_blocked_requires_evidence")

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

        self.assertEqual(process.returncode, 3, process.stdout + process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["process_status"], "blocked")
        self.assertEqual(payload["review_extraction_status"], "blocked")
        self.assertIsNone(payload["model_review_status"])
        self.assertEqual(payload["security_decision"], "blocked")
        self.assertEqual(
            payload["security_decision_source"],
            "process_blocked_requires_valid_deterministic_and_review_receipts",
        )
        self.assertEqual(payload["review_validation"]["status"], "blocked")
        self.assertIn("oss-security profile did not produce", payload["blockers"][0])

    def test_receipt_first_runner_blocks_when_last_message_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bin_dir = _fake_codex(
                root,
                textwrap.dedent(
                    """
                    import sys

                    sys.stdin.read()
                    print("no last message written")
                    raise SystemExit(0)
                    """
                ),
            )
            env = _sandbox_env(root, bin_dir)

            process = _run_receipt_first(root, env)

        self.assertEqual(process.returncode, 3, process.stdout + process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["process_status"], "blocked")
        self.assertEqual(payload["review_extraction_status"], "blocked")
        self.assertEqual(payload["security_decision"], "blocked")
        self.assertIn("review output could not be read", payload["review_validation"]["blockers"][0])


if __name__ == "__main__":
    unittest.main()
