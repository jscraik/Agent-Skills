from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import importlib.util
from argparse import Namespace


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "Infrastructure/scripts/validation-and-linting/check_oss_local_smoke_output.py"
RUNNER = REPO_ROOT / "Infrastructure/scripts/validation-and-linting/run_oss_local_smoke.py"

sys.path.insert(0, RUNNER.parent.as_posix())
RUNNER_SPEC = importlib.util.spec_from_file_location("run_oss_local_smoke", RUNNER)
assert RUNNER_SPEC and RUNNER_SPEC.loader
RUNNER_MODULE = importlib.util.module_from_spec(RUNNER_SPEC)
RUNNER_SPEC.loader.exec_module(RUNNER_MODULE)


def _finding_codes(stdout: str) -> set[str]:
    return {finding["code"] for finding in json.loads(stdout)["findings"]}


def _run_fake_codex_smoke(tmp: Path, *, bad: bool) -> subprocess.CompletedProcess[str]:
    profile = tmp / "oss-local.config.toml"
    profile.write_text('model = "qwen3.5:9b-mlx"\nmodel_provider = "ollama"\n', encoding="utf-8")
    bin_dir = _write_fake_codex(tmp, _fake_codex_script(bad=bad))
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
    return subprocess.run(
        [sys.executable, str(RUNNER), "--profile-source", str(profile), "--output-dir", str(tmp / "out"), "--json"],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        text=True,
        capture_output=True,
    )


def _write_fake_codex(tmp: Path, script_body: str) -> Path:
    bin_dir = tmp / "bin"
    bin_dir.mkdir()
    codex = bin_dir / "codex"
    codex.write_text(script_body, encoding="utf-8")
    codex.chmod(0o755)
    return bin_dir


def _fake_codex_script(*, bad: bool) -> str:
    header = "#!/bin/sh\nlast=''\nwhile [ $# -gt 0 ]; do\n  if [ \"$1\" = \"--output-last-message\" ]; then shift; last=\"$1\"; fi\n  shift\ndone\n"
    if not bad:
        return header + "printf 'CODEX_OSS_LOCAL_OK\\n'\nprintf 'CODEX_OSS_LOCAL_OK\\n' > \"$last\"\nprintf 'tokens used\\n3814\\n' >&2\n"
    return header + (
        "printf 'warning: Model metadata for qwen3.5:9b-mlx not found. Defaulting to fallback metadata.\\n' >&2\n"
        "printf '<think>working</think>\\n'\nprintf 'tokens used\\n24039\\n' >&2\nprintf 'CODEX_OSS_LOCAL_OK\\n' > \"$last\"\n"
    )


class TestOssLocalSmokeOutputCheck(unittest.TestCase):
    def test_runner_command_uses_json_and_ignores_rules_for_marker_smoke(self) -> None:
        command = RUNNER_MODULE._codex_command(Path("/tmp/last-message.txt"), "CODEX_OSS_LOCAL_OK")

        self.assertIn("--json", command)
        self.assertIn("--ignore-rules", command)
        self.assertIn("--skip-git-repo-check", command)
        self.assertIn("--output-last-message", command)
        self.assertEqual(command[-1], "Reply exactly CODEX_OSS_LOCAL_OK")

    def test_runner_resolves_output_paths_before_changing_workdir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            profile = Path(tmp_dir) / "oss-local.config.toml"
            profile.write_text('model = "qwen3.5:9b-mlx"\nmodel_provider = "ollama"\n', encoding="utf-8")
            args = Namespace(output_dir=str(Path(tmp_dir) / "relative-out"), profile_source=str(profile))

            paths = RUNNER_MODULE._prepare_paths(args)
            copied_profile = paths["codex_home"] / "oss-local.config.toml"
            catalog = paths["codex_home"] / "local-model-catalog.json"
            self.assertTrue(paths["root"].is_absolute())
            self.assertTrue(paths["codex_home"].is_absolute())
            self.assertTrue(paths["last_message"].is_absolute())
            self.assertTrue(catalog.is_file())
            profile_text = copied_profile.read_text(encoding="utf-8")
            catalog_payload = json.loads(catalog.read_text(encoding="utf-8"))

        self.assertIn('model_catalog_json = "', profile_text)
        self.assertIn('model_context_window = 262144', profile_text)
        self.assertIn('hide_agent_reasoning = true', profile_text)
        self.assertEqual(catalog_payload["models"][0]["slug"], "qwen3.5:9b-mlx")
        self.assertEqual(catalog_payload["models"][0]["default_reasoning_level"], "none")

    def test_check_passes_clean_marker_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            transcript = Path(tmp_dir) / "smoke.txt"
            transcript.write_text("CODEX_OSS_LOCAL_OK\ntokens used\n412\n", encoding="utf-8")

            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(transcript), "--json"],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["findings"], [])

    def test_check_fails_fallback_thinking_and_token_blowout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            transcript = Path(tmp_dir) / "smoke.txt"
            transcript.write_text(
                "model: qwen3.5:9b-mlx\n"
                "provider: ollama\n"
                "approval: never\n"
                "sandbox: read-only\n"
                "session id: 019f241c-b505-79a1-bb69-8a4efceda0a4\n"
                "warning: Model metadata for qwen3.5:9b-mlx not found. Defaulting to fallback metadata.\n"
                "<think>working</think>\n"
                "CODEX_OSS_LOCAL_OK\n"
                "tokens used\n24,039\n",
                encoding="utf-8",
            )

            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(transcript), "--json"],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

        self.assertEqual(proc.returncode, 1)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "fail")
        codes = {finding["code"] for finding in payload["findings"]}
        self.assertEqual(
            codes,
            {
                "codex_runtime_metadata_fallback",
                "codex_runtime_visible_thinking",
                "codex_runtime_token_budget_exceeded",
            },
        )
        self.assertEqual(
            payload["runtime_observations"],
            {
                "model": "qwen3.5:9b-mlx",
                "provider": "ollama",
                "approval": "never",
                "sandbox": "read-only",
                "session_id": "019f241c-b505-79a1-bb69-8a4efceda0a4",
                "tokens_used": 24039,
                "codex_jsonl_reasoning_event_observed": False,
                "metadata_fallback_observed": True,
                "visible_thinking_observed": True,
            },
        )

    def test_check_allows_codex_jsonl_reasoning_telemetry_but_tracks_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            transcript = Path(tmp_dir) / "smoke.jsonl"
            transcript.write_text(
                json.dumps({"type": "item.completed", "item": {"type": "reasoning", "text": "thinking"}})
                + "\n"
                + json.dumps({"type": "turn.completed", "usage": {"input_tokens": 3721, "output_tokens": 53}})
                + "\n",
                encoding="utf-8",
            )

            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(transcript), "--json"],
                cwd=REPO_ROOT,
                check=False,
                text=True,
                capture_output=True,
            )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["findings"], [])
        self.assertEqual(payload["runtime_observations"]["tokens_used"], 3774)
        self.assertTrue(payload["runtime_observations"]["codex_jsonl_reasoning_event_observed"])
        self.assertFalse(payload["runtime_observations"]["visible_thinking_observed"])

    def test_runner_passes_with_fake_codex_clean_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            proc = _run_fake_codex_smoke(Path(tmp_dir), bad=False)

        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["schema_version"], "skills-sdk.oss-local-smoke-run.v0")
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["codex_profile"], "oss-local")
        self.assertEqual(payload["model"], "qwen3.5:9b-mlx")
        self.assertEqual(payload["model_provider"], "ollama")
        self.assertIsInstance(payload["duration_seconds"], float)
        self.assertEqual(payload["findings"], [])

    def test_runner_fails_with_fake_codex_bad_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            proc = _run_fake_codex_smoke(Path(tmp_dir), bad=True)

        self.assertEqual(proc.returncode, 1)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertEqual(
            _finding_codes(proc.stdout),
            {
                "codex_runtime_metadata_fallback",
                "codex_runtime_visible_thinking",
                "codex_runtime_token_budget_exceeded",
            },
        )


if __name__ == "__main__":
    unittest.main()
