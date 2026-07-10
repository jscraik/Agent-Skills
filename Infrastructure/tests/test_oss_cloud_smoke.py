from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "Infrastructure/scripts/validation-and-linting/run_oss_cloud_smoke.py"


def _load_runner() -> object:
    spec = importlib.util.spec_from_file_location("run_oss_cloud_smoke", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_executable(path: Path, contents: str) -> None:
    path.write_text(contents, encoding="utf-8")
    path.chmod(0o755)


def _write_profile(path: Path, *, model: str = "minimax-m2.7:cloud", provider: str = "ollama-cloud") -> None:
    path.write_text(
        f'model = "{model}"\nmodel_provider = "{provider}"\n',
        encoding="utf-8",
    )


def _write_op(bin_dir: Path) -> Path:
    path = bin_dir / "op"
    _write_executable(
        path,
        "#!/bin/sh\n"
        "while [ \"$1\" != \"--\" ]; do shift; done\n"
        "shift\n"
        "exec \"$@\"\n",
    )
    return path


def _write_codex(bin_dir: Path) -> Path:
    path = bin_dir / "codex"
    _write_executable(
        path,
        "#!/bin/sh\n"
        "last=''\n"
        "while [ $# -gt 0 ]; do\n"
        "  if [ \"$1\" = \"--output-last-message\" ]; then shift; last=\"$1\"; fi\n"
        "  shift\n"
        "done\n"
        "printf 'CODEX_OSS_CLOUD_OK\\n'\n"
        "printf 'CODEX_OSS_CLOUD_OK\\n' > \"$last\"\n",
    )
    return path


def _run_cloud_smoke(
    root: Path,
    profile: Path,
    env_file: Path,
    *,
    op_bin: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(RUNNER),
        "--profile-source",
        str(profile),
        "--op-env-file",
        str(env_file),
        "--output-dir",
        str(root / "out"),
        "--json",
    ]
    if op_bin is not None:
        command.extend(["--op-bin", str(op_bin)])
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=env,
        check=False,
        text=True,
        capture_output=True,
    )


class TestOssCloudSmoke(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = _load_runner()

    def test_approved_env_requires_ollama_op_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            empty = Path(temp_dir) / "empty.env"
            empty.write_text("", encoding="utf-8")
            self.assertIsNone(self.runner._approved_env_file(empty))

            valid = Path(temp_dir) / "valid.env"
            valid.write_text("OLLAMA_API_KEY=op://vault/item/credential\n", encoding="utf-8")
            self.assertEqual(self.runner._approved_env_file(valid), valid)

    def test_profile_findings_reject_wrong_model_and_provider(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "oss-cloud.config.toml"
            _write_profile(path, model="deepseek-v4-flash", provider="ollama")

            findings = self.runner._profile_findings(path)

        self.assertEqual(
            {finding["code"] for finding in findings},
            {"oss_cloud_model_mismatch", "oss_cloud_provider_mismatch"},
        )

    def test_profile_findings_accept_projected_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.toml"
            projected = root / "oss-cloud.config.toml"
            _write_profile(source)
            projected.symlink_to(source)

            findings = self.runner._profile_findings(projected)

        self.assertEqual(findings, [])

    def test_runner_uses_op_reference_and_emits_redacted_pass_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            profile = root / "oss-cloud.config.toml"
            env_file = root / "oss-cloud.env"
            bin_dir = root / "bin"
            bin_dir.mkdir()
            _write_profile(profile)
            env_file.write_text("OLLAMA_API_KEY=op://vault/item/credential\n", encoding="utf-8")
            op = _write_op(bin_dir)
            _write_codex(bin_dir)
            env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            proc = _run_cloud_smoke(root, profile, env_file, op_bin=op, env=env)

        self.assertEqual(proc.returncode, 0, proc.stderr)
        receipt = json.loads(proc.stdout)
        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["model"], "minimax-m2.7:cloud")
        self.assertEqual(receipt["model_provider"], "ollama-cloud")
        self.assertEqual(receipt["auth_source"], "op_reference")
        self.assertNotIn("OLLAMA_API_KEY=", json.dumps(receipt))

    def test_runner_blocks_empty_env_before_provider_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            profile = root / "oss-cloud.config.toml"
            empty_env = root / "oss-cloud.env"
            bin_dir = root / "bin"
            bin_dir.mkdir()
            _write_profile(profile)
            empty_env.write_text("", encoding="utf-8")
            op = _write_op(bin_dir)
            env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            proc = _run_cloud_smoke(root, profile, empty_env, op_bin=op, env=env)

        self.assertEqual(proc.returncode, 1)
        receipt = json.loads(proc.stdout)
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual({finding["code"] for finding in receipt["findings"]}, {"oss_cloud_credential_reference_missing"})
        self.assertFalse(receipt["provider_invoked"])

if __name__ == "__main__":
    unittest.main()
