from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "Infrastructure/scripts/validation-and-linting/check_oss_local_smoke_output.py"
RUNNER = REPO_ROOT / "Infrastructure/scripts/validation-and-linting/run_oss_local_smoke.py"


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

    def test_check_fails_codex_jsonl_reasoning_and_usage_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            transcript = Path(tmp_dir) / "smoke.jsonl"
            transcript.write_text(
                json.dumps({"type": "item.completed", "item": {"type": "reasoning", "text": "thinking"}})
                + "\n"
                + json.dumps({"type": "turn.completed", "usage": {"input_tokens": 8231, "output_tokens": 53}})
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

        self.assertEqual(proc.returncode, 1)
        payload = json.loads(proc.stdout)
        codes = {finding["code"] for finding in payload["findings"]}
        self.assertEqual(codes, {"codex_runtime_visible_thinking", "codex_runtime_token_budget_exceeded"})

    def test_runner_passes_with_fake_codex_clean_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            proc = _run_fake_codex_smoke(Path(tmp_dir), bad=False)

        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["schema_version"], "skills-sdk.oss-local-smoke-run.v0")
        self.assertEqual(payload["status"], "pass")
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
