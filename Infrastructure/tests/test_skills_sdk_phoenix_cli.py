from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_skills_sdk_phoenix_observability import (  # noqa: E402
    REPO_ROOT,
    TestSkillsSdkPhoenixObservability as _ObservabilityTests,
    _command_env,
)


def _write_fake_otel_runtime(
    runtime: Path,
    marker: Path,
    *,
    record_payload: bool = True,
) -> None:
    script = (
        f"""#!/usr/bin/env python3
import json
import pathlib
import sys

payload = json.loads(sys.stdin.read())
pathlib.Path({marker.as_posix()!r}).write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
print(json.dumps({{"status": "pass", "http_status": 200}}))
"""
        if record_payload
        else f"""#!/usr/bin/env python3
import pathlib
pathlib.Path({marker.as_posix()!r}).write_text("called", encoding="utf-8")
print('{{"status":"pass","http_status":200}}')
"""
    )
    runtime.write_text(script, encoding="utf-8")
    runtime.chmod(0o755)


def _run_ask(env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "Infrastructure/bin/ask", *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


class TestSkillsSdkPhoenixCli(unittest.TestCase):
    def _serve_phoenix(self) -> tuple[object, str]:
        return _ObservabilityTests._serve_phoenix(self)

    def _write_receipt(self, directory: Path, *, include_raw: bool = False, codex_exec_invoked: bool = True) -> Path:
        return _ObservabilityTests._write_receipt(
            self,
            directory,
            include_raw=include_raw,
            codex_exec_invoked=codex_exec_invoked,
        )

    def test_public_cli_previews_phoenix_mirror(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            receipt_path = self._write_receipt(Path(temp_dir))
            completed = subprocess.run(
                [
                    sys.executable,
                    "Infrastructure/bin/ask",
                    "sdk",
                    "observability",
                    "phoenix-mirror",
                    "--receipt",
                    receipt_path.as_posix(),
                    "--preview",
                    "--json",
                    "--robot",
                ],
                cwd=REPO_ROOT,
                env=_command_env(),
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        envelope = json.loads(completed.stdout)
        payload = envelope["data"]["skills_sdk_observability_phoenix_mirror"]
        self.assertEqual(payload["status"], "preview")
        self.assertFalse(payload["mutation_performed"])

    def test_public_cli_checks_phoenix_status(self) -> None:
        server, base_url = self._serve_phoenix()
        self.addCleanup(server.shutdown)

        completed = subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "observability",
                "phoenix-status",
                "--base-url",
                base_url,
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            env=_command_env(),
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        envelope = json.loads(completed.stdout)
        payload = envelope["data"]["skills_sdk_observability_phoenix_status"]
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["receipt"]["server_version"], "test-phoenix")

    def test_public_cli_blocks_phoenix_smoke_when_otel_runtime_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            completed = subprocess.run(
                [
                    sys.executable,
                    "Infrastructure/bin/ask",
                    "sdk",
                    "observability",
                    "phoenix-smoke",
                    "--base-url",
                    "http://127.0.0.1:6006",
                    "--otel-python",
                    str(Path(temp_dir) / "missing-python"),
                    "--json",
                    "--robot",
                ],
                cwd=REPO_ROOT,
                env=_command_env(),
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertNotEqual(completed.returncode, 0)
        envelope = json.loads(completed.stdout)
        payload = envelope["data"]["skills_sdk_observability_phoenix_smoke"]
        self.assertEqual(payload["status"], "blocked")
        self.assertIn("otel_python_available", {check["id"] for check in payload["receipt"]["blockers"]})

    def test_public_cli_auto_traces_normal_ask_commands_when_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            marker = Path(temp_dir) / "payload.json"
            runtime = Path(temp_dir) / "fake-otel-python"
            _write_fake_otel_runtime(runtime, marker)
            env = _command_env()
            env.update(
                {
                    "ASK_PHOENIX_AUTO_TRACE": "1",
                    "ASK_PHOENIX_BASE_URL": "http://127.0.0.1:6006",
                    "ASK_PHOENIX_OTEL_PYTHON": runtime.as_posix(),
                    "ASK_PHOENIX_MODEL": "qwen/qwen3-coder",
                    "ASK_PHOENIX_PROVIDER": "local-oss",
                    "ASK_PHOENIX_PROMPT_TOKENS": "3",
                    "ASK_PHOENIX_COMPLETION_TOKENS": "2",
                }
            )
            completed = _run_ask(env, "repo", "status", "--json", "--robot")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            envelope = json.loads(completed.stdout)
            self.assertEqual(envelope["telemetry"]["phoenix_trace_status"], "pass")
            payload = json.loads(marker.read_text(encoding="utf-8"))
            self.assertEqual(payload["model_name"], "qwen/qwen3-coder")
            self.assertEqual(payload["provider"], "local-oss")
            self.assertIn("repo status", payload["command_name"])

    def test_public_cli_auto_trace_skips_when_repo_config_is_disabled_without_env_flag(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            marker = Path(temp_dir) / "payload.json"
            runtime = Path(temp_dir) / "fake-otel-python"
            _write_fake_otel_runtime(runtime, marker)
            env = _command_env()
            env.update({"ASK_PHOENIX_OTEL_PYTHON": runtime.as_posix()})
            env.pop("ASK_PHOENIX_AUTO_TRACE", None)
            completed = _run_ask(env, "repo", "status", "--json", "--robot")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            envelope = json.loads(completed.stdout)
            self.assertNotIn("phoenix_trace_status", envelope["telemetry"])
            self.assertFalse(marker.exists())

    def test_public_cli_auto_trace_skips_phoenix_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            marker = Path(temp_dir) / "payload.json"
            runtime = Path(temp_dir) / "fake-otel-python"
            _write_fake_otel_runtime(runtime, marker, record_payload=False)
            env = _command_env()
            env.update(
                {
                    "ASK_PHOENIX_AUTO_TRACE": "1",
                    "ASK_PHOENIX_BASE_URL": "http://127.0.0.1:6006",
                    "ASK_PHOENIX_OTEL_PYTHON": runtime.as_posix(),
                }
            )
            completed = _run_ask(
                env,
                "sdk",
                "observability",
                "phoenix-status",
                "--base-url",
                "http://127.0.0.1:1",
                "--timeout-seconds",
                "0.01",
                "--json",
                "--robot",
            )

        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(marker.exists())
