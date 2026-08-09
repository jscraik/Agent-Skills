from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "Infrastructure/scripts/validation-and-linting/run_oss_cloud_smoke.py"
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.cloud_smoke_contract import cloud_smoke_receipt_findings  # noqa: E402


def _load_runner() -> object:
    spec = importlib.util.spec_from_file_location("run_oss_cloud_smoke", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_executable(path: Path, contents: str) -> None:
    path.write_text(contents, encoding="utf-8")
    path.chmod(0o755)


def _write_profile(path: Path, *, model: str = "deepseek-v4-flash:cloud", provider: str = "ollama-cloud") -> None:
    path.write_text(
        f'model = "{model}"\nmodel_provider = "{provider}"\n',
        encoding="utf-8",
    )


def _write_auth_wrapper(bin_dir: Path) -> Path:
    path = bin_dir / "run-auth-backed.sh"
    _write_executable(
        path,
        "#!/bin/sh\n"
        "while [ \"$1\" != \"--\" ]; do shift; done\n"
        "shift\n"
        "exec \"$@\"\n",
    )
    return path


def _write_codex_exec_wrapper(bin_dir: Path) -> Path:
    path = bin_dir / "run-codex-exec.sh"
    _write_executable(
        path,
        "#!/bin/sh\n"
        "printf 'CODEX_OSS_CLOUD_OK\\n'\n"
        "exit 0\n",
    )
    return path


def _write_env_probe_wrapper(bin_dir: Path) -> tuple[Path, Path]:
    state_path = bin_dir / "codex-config-home-state.txt"
    path = bin_dir / "run-codex-exec-probe.sh"
    _write_executable(
        path,
        "#!/bin/sh\n"
        f"if [ \"${{CODEX_CONFIG_HOME+x}}\" = x ]; then printf 'present' > {shlex.quote(str(state_path))}; "
        f"else printf 'unset' > {shlex.quote(str(state_path))}; fi\n"
        "printf 'CODEX_OSS_CLOUD_OK\\n'\n"
        "exit 0\n",
    )
    return path, state_path


def _run_cloud_smoke(
    root: Path,
    profile: Path,
    env_file: Path,
    *,
    auth_wrapper: Path,
    codex_exec_wrapper: Path,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(RUNNER),
        "--profile-source",
        str(profile),
        "--env-file",
        str(env_file),
        "--auth-wrapper",
        str(auth_wrapper),
        "--codex-exec-wrapper",
        str(codex_exec_wrapper),
        "--output-dir",
        str(root / "out"),
        "--json",
    ]
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

    def test_approved_env_requires_a_fifo_without_reading_it(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            regular = Path(temp_dir) / "regular.env"
            regular.write_text("OLLAMA_API_KEY=op://vault/item/credential\n", encoding="utf-8")
            self.assertIsNone(self.runner._approved_env_file(regular))

    @unittest.skipIf(not hasattr(os, "mkfifo"), "FIFO support unavailable")
    def test_approved_env_accepts_1password_fifo(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / "codex.env"
            os.mkfifo(env_file)

            self.assertEqual(self.runner._approved_env_file(env_file), env_file)
            self.assertEqual(self.runner._auth_source(env_file), "1password_desktop_fifo")

    def test_profile_findings_reject_wrong_model_and_provider(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "oss-cloud.config.toml"
            _write_profile(path, model="minimax-m2.7:cloud", provider="ollama")

            findings = self.runner._profile_findings(path)

        self.assertEqual(
            {finding["code"] for finding in findings},
            {"oss_cloud_model_mismatch", "oss_cloud_provider_mismatch"},
        )

    def test_profile_parser_accepts_toml_spacing_and_comments(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "oss-cloud.config.toml"
            path.write_text(
                'model="deepseek-v4-flash:cloud" # selected model\nmodel_provider = "ollama-cloud"\n',
                encoding="utf-8",
            )

            findings = self.runner._profile_findings(path)

        self.assertEqual(findings, [])

    def test_command_uses_an_isolated_codex_home(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            profile = root / "profiles" / "oss-cloud.config.toml"
            profile.parent.mkdir()
            _write_profile(profile)
            args = self.runner._parser().parse_args(["--profile-source", str(profile)])
            paths = self.runner._paths(str(root / "out"))

            command = self.runner._command(args, paths, root / "env")
            isolated_home = paths["codex_home"]
            self.assertIn("env", command)
            self.assertIn(f"CODEX_HOME={isolated_home}", command)
            self.assertIn("--skip-git-repo-check", command)
            self.assertIn("--strict-config", command)
            self.assertIn("--sandbox", command)
            self.assertIn("--ephemeral", command)
            self.assertTrue((isolated_home / "config.toml").is_file())
            self.assertTrue((isolated_home / "oss-cloud.config.toml").is_file())
            self.assertNotIn(f"CODEX_HOME={profile.parent.resolve()}", command)

    def test_command_writes_allowlisted_profile_into_isolated_codex_home(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source" / "profile.toml"
            projected = root / "projection" / "oss-cloud.config.toml"
            source.parent.mkdir()
            projected.parent.mkdir()
            source.write_text(
                'model = "deepseek-v4-flash:cloud"\n'
                'model_provider = "ollama-cloud"\n'
                "\n[mcp_servers.untrusted]\n"
                'command = "untrusted-mcp"\n'
                "enabled = false\n",
                encoding="utf-8",
            )
            projected.symlink_to(source)
            args = self.runner._parser().parse_args(["--profile-source", str(projected)])
            paths = self.runner._paths(str(root / "out"))

            command = self.runner._command(args, paths, root / "env")
            isolated_home = paths["codex_home"]
            self.assertIn(f"CODEX_HOME={isolated_home}", command)
            self.assertEqual(
                (isolated_home / "oss-cloud.config.toml").read_text(encoding="utf-8"),
                self.runner.ISOLATED_CODEX_CONFIG,
            )
            self.assertNotIn("mcp_servers", (isolated_home / "oss-cloud.config.toml").read_text(encoding="utf-8"))
            self.assertNotIn(f"CODEX_HOME={source.parent.resolve()}", command)

    @unittest.skipIf(not hasattr(os, "mkfifo"), "FIFO support unavailable")
    def test_receipt_retains_complete_redacted_execution_argv(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            profile = root / "oss-cloud.config.toml"
            _write_profile(profile)
            env_file = root / "env"
            os.mkfifo(env_file)
            args = self.runner._parser().parse_args(
                ["--profile-source", str(profile), "--env-file", str(env_file)]
            )
            paths = self.runner._paths(str(root / "out"))
            command = self.runner._command(args, paths, env_file)
            receipt = self.runner._receipt(
                args, paths, profile, [], command=command, exit_code=0,
                duration_seconds=0.1, provider_invoked=True,
            )
            self.assertEqual(receipt["execution_argv"], receipt["command"])
            self.assertTrue(any(token.endswith("run-auth-backed.sh") for token in receipt["execution_argv"]))
            self.assertTrue(any(token.endswith("run-codex-exec.sh") for token in receipt["execution_argv"]))
            self.assertNotIn(str(env_file), receipt["execution_argv"])

    def test_command_resolves_relative_profile_from_caller_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            profile = root / "profiles" / "oss-cloud.config.toml"
            profile.parent.mkdir()
            _write_profile(profile)
            previous_cwd = Path.cwd()
            try:
                os.chdir(root)
                args = self.runner._parser().parse_args(
                    [
                        "--profile-source",
                        "profiles/oss-cloud.config.toml",
                    ]
                )
                paths = self.runner._paths(str(root / "out"))
                command = self.runner._command(args, paths, root / "env")
                self.assertIn(f"CODEX_HOME={paths['codex_home']}", command)
            finally:
                os.chdir(previous_cwd)

    def test_isolated_config_disables_context_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            profile = root / "oss-cloud.config.toml"
            _write_profile(profile)
            paths = self.runner._paths(str(root / "out"))

            self.runner._isolated_codex_home(profile, paths)
            config = (paths["codex_home"] / "config.toml").read_text(encoding="utf-8")

        self.assertIn("plugins = false", config)
        self.assertIn("apps = false", config)
        self.assertNotIn("developer_instructions", config)

    def test_isolated_config_disables_loopback_network_access(self) -> None:
        config = self.runner.ISOLATED_CODEX_CONFIG

        self.assertIn("allow_local_binding = false", config)
        self.assertIn('"ollama.com" = "allow"', config)
        self.assertNotIn('"localhost" = "allow"', config)
        self.assertNotIn('"127.0.0.1" = "allow"', config)

    @unittest.skipIf(not hasattr(os, "mkfifo"), "FIFO support unavailable")
    def test_marker_child_cannot_inherit_codex_config_home(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            profile = root / "oss-cloud.config.toml"
            env_file = root / "oss-cloud.env"
            bin_dir = root / "bin"
            bin_dir.mkdir()
            _write_profile(profile)
            os.mkfifo(env_file)
            auth_wrapper = _write_auth_wrapper(bin_dir)
            codex_exec_wrapper, state_path = _write_env_probe_wrapper(bin_dir)
            args = self.runner._parser().parse_args([
                "--profile-source", str(profile),
                "--auth-wrapper", str(auth_wrapper),
                "--codex-exec-wrapper", str(codex_exec_wrapper),
            ])
            paths = self.runner._paths(str(root / "out"))
            command = self.runner._command(args, paths, env_file)

            with patch.dict(os.environ, {"CODEX_CONFIG_HOME": str(root / "inherited")}):
                exit_code, _ = self.runner._run(command, paths, args)

            self.assertEqual(exit_code, 0)
            self.assertEqual(state_path.read_text(encoding="utf-8"), "unset")

    def test_profile_findings_accept_projected_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.toml"
            projected = root / "oss-cloud.config.toml"
            _write_profile(source)
            projected.symlink_to(source)

            findings = self.runner._profile_findings(projected)

        self.assertEqual(findings, [])

    @unittest.skipIf(not hasattr(os, "mkfifo"), "FIFO support unavailable")
    def test_runner_uses_configs_wrappers_and_emits_redacted_pass_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            profile = root / "oss-cloud.config.toml"
            env_file = root / "oss-cloud.env"
            bin_dir = root / "bin"
            bin_dir.mkdir()
            _write_profile(profile)
            os.mkfifo(env_file)
            auth_wrapper = _write_auth_wrapper(bin_dir)
            codex_exec_wrapper = _write_codex_exec_wrapper(bin_dir)
            env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            proc = _run_cloud_smoke(
                root, profile, env_file, auth_wrapper=auth_wrapper,
                codex_exec_wrapper=codex_exec_wrapper, env=env,
            )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        receipt = json.loads(proc.stdout)
        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["model"], "deepseek-v4-flash:cloud")
        self.assertEqual(receipt["model_provider"], "ollama-cloud")
        self.assertEqual(receipt["auth_source"], "1password_desktop_fifo")
        self.assertNotIn("OLLAMA_API_KEY=", json.dumps(receipt))
        self.assertNotIn(str(env_file), json.dumps(receipt))

    def test_runner_blocks_regular_env_before_provider_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            profile = root / "oss-cloud.config.toml"
            regular_env = root / "oss-cloud.env"
            bin_dir = root / "bin"
            bin_dir.mkdir()
            _write_profile(profile)
            regular_env.write_text("OLLAMA_API_KEY=op://vault/item/credential\n", encoding="utf-8")
            auth_wrapper = _write_auth_wrapper(bin_dir)
            codex_exec_wrapper = _write_codex_exec_wrapper(bin_dir)
            env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            proc = _run_cloud_smoke(
                root, profile, regular_env, auth_wrapper=auth_wrapper,
                codex_exec_wrapper=codex_exec_wrapper, env=env,
            )

        self.assertEqual(proc.returncode, 1)
        receipt = json.loads(proc.stdout)
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual({finding["code"] for finding in receipt["findings"]}, {"oss_cloud_auth_stream_missing"})
        self.assertFalse(receipt["provider_invoked"])

    def test_cloud_metadata_fallback_is_a_warning_when_marker_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = self.runner._paths(str(root / "out"))
            paths["stdout"].write_text("CODEX_OSS_CLOUD_OK\n", encoding="utf-8")
            paths["stderr"].write_text(
                "warning: Model metadata for deepseek-v4-flash:cloud not found. Defaulting to fallback metadata.\n"
                "tokens used\n14916\n",
                encoding="utf-8",
            )
            profile = root / "oss-cloud.config.toml"
            _write_profile(profile)
            args = self.runner._parser().parse_args(["--profile-source", str(profile)])

            receipt = self.runner._receipt(
                args,
                paths,
                profile,
                [],
                command=["bash", "run-auth-backed.sh"],
                exit_code=0,
                duration_seconds=1.0,
                provider_invoked=True,
            )

        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["findings"], [])
        self.assertEqual(
            [warning["code"] for warning in receipt["warnings"]],
            ["codex_runtime_metadata_fallback"],
        )

    def test_secret_shaped_output_blocks_the_smoke_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = self.runner._paths(str(root / "out"))
            paths["stdout"].write_text("CODEX_OSS_CLOUD_OK\n", encoding="utf-8")
            paths["stderr"].write_text("OLLAMA_API_KEY=redacted-test-value\n", encoding="utf-8")
            profile = root / "oss-cloud.config.toml"
            _write_profile(profile)
            args = self.runner._parser().parse_args(["--profile-source", str(profile)])

            receipt = self.runner._receipt(
                args,
                paths,
                profile,
                [],
                command=["bash", "run-auth-backed.sh"],
                exit_code=0,
                duration_seconds=1.0,
                provider_invoked=True,
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertTrue(receipt["secret_value_observed"])
        self.assertEqual(receipt["secret_observation"]["status"], "blocked")
        self.assertIn("oss_cloud_secret_output_observed", {finding["code"] for finding in receipt["findings"]})

    def test_secret_marker_after_shell_prefix_blocks_the_smoke_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = self.runner._paths(str(root / "out"))
            paths["stdout"].write_text("CODEX_OSS_CLOUD_OK\n", encoding="utf-8")
            paths["stderr"].write_text("+ export OLLAMA_API_KEY=redacted-test-value\n", encoding="utf-8")
            profile = root / "oss-cloud.config.toml"
            _write_profile(profile)
            args = self.runner._parser().parse_args(["--profile-source", str(profile)])

            receipt = self.runner._receipt(
                args,
                paths,
                profile,
                [],
                command=["bash", "run-auth-backed.sh"],
                exit_code=0,
                duration_seconds=1.0,
                provider_invoked=True,
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertTrue(receipt["secret_value_observed"])

    def test_cloud_smoke_rejects_codex_wrapper_nested_after_child_argument(self) -> None:
        payload = {
            "schema_version": "skills-sdk.oss-cloud-smoke-run.v0", "observed_at": "2026-08-06T12:00:00+00:00",
            "status": "pass", "lane": "oss-cloud", "codex_profile": "oss-cloud", "model": "deepseek-v4-flash:cloud",
            "model_provider": "ollama-cloud", "auth_source": "1password_desktop_fifo", "provider_invoked": True,
            "execution_argv": [
                "bash", "/Users/jamiecraik/dev/configs/codex/scripts/run-auth-backed.sh", "--env-file",
                "<operator-approved-opaque-env-stream>", "--require-env", "OLLAMA_API_KEY", "--", "env", "-u",
                "CODEX_CONFIG_HOME", "CODEX_HOME=/tmp/codex-home", "bash", "other-wrapper",
                "/Users/jamiecraik/dev/configs/codex/scripts/run-codex-exec.sh", "--profile", "oss-cloud",
                "--strict-config", "--sandbox", "read-only", "--ephemeral", "--model", "deepseek-v4-flash:cloud",
                "Reply exactly CODEX_OSS_CLOUD_OK",
            ],
            "exit_code": 0, "marker": "CODEX_OSS_CLOUD_OK", "warnings": [], "findings": [],
            "secret_value_observed": False,
            "secret_observation": {"status": "clear", "source": "captured_output_scan", "redacted": True},
        }

        self.assertIn("codex_exec_wrapper_contract", cloud_smoke_receipt_findings(payload))

    def test_cloud_smoke_rejects_duplicate_contract_flags(self) -> None:
        payload = {
            "schema_version": "skills-sdk.oss-cloud-smoke-run.v0", "observed_at": "2026-08-06T12:00:00+00:00",
            "status": "pass", "lane": "oss-cloud", "codex_profile": "oss-cloud", "model": "deepseek-v4-flash:cloud",
            "model_provider": "ollama-cloud", "auth_source": "1password_desktop_fifo", "provider_invoked": True,
            "execution_argv": [
                "bash", "/Users/jamiecraik/dev/configs/codex/scripts/run-auth-backed.sh", "--env-file",
                "<operator-approved-opaque-env-stream>", "--require-env", "OLLAMA_API_KEY", "--", "env", "-u",
                "CODEX_CONFIG_HOME", "CODEX_HOME=/tmp/codex-home", "bash",
                "/Users/jamiecraik/dev/configs/codex/scripts/run-codex-exec.sh", "--profile", "oss-cloud",
                "--strict-config", "--sandbox", "read-only", "--sandbox", "workspace-write", "--ephemeral",
                "--model", "deepseek-v4-flash:cloud", "-c", 'approval_policy="on-request"',
                "Reply exactly CODEX_OSS_CLOUD_OK",
            ],
            "exit_code": 0, "marker": "CODEX_OSS_CLOUD_OK", "warnings": [], "findings": [],
            "secret_value_observed": False,
            "secret_observation": {"status": "clear", "source": "captured_output_scan", "redacted": True},
        }

        findings = cloud_smoke_receipt_findings(payload)
        self.assertIn("missing_or_nonadjacent:--sandbox", findings)

    def test_isolated_config_disables_loopback_binding_and_removes_loopback_hosts(self) -> None:
        config_text = self.runner.ISOLATED_CODEX_CONFIG
        self.assertIn("allow_local_binding = false", config_text)
        self.assertNotIn('"localhost"', config_text)
        self.assertNotIn('"127.0.0.1"', config_text)
        self.assertIn('"ollama.com"', config_text)

    def test_command_explicitly_unsets_codex_config_home_env_var(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            profile = root / "oss-cloud.config.toml"
            env_file = root / ".env"
            _write_profile(profile)
            env_file.write_text("OLLAMA_API_KEY=test\n", encoding="utf-8")
            args = self.runner._parser().parse_args(["--profile-source", str(profile)])
            paths = self.runner._paths(str(root / "out"))

            command = self.runner._command(args, paths, env_file)

            env_index = command.index("env")
            self.assertIn("-u", command[env_index:])
            self.assertIn("CODEX_CONFIG_HOME", command[env_index:])
            u_index = command.index("-u", env_index)
            self.assertEqual(command[u_index + 1], "CODEX_CONFIG_HOME")

    def test_run_uses_empty_temporary_work_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = self.runner._paths(str(root / "out"))
            args = self.runner._parser().parse_args([])
            observed_cwd: list[str] = []

            def fake_run(*_command: object, **kwargs: object) -> object:
                observed_cwd.append(str(kwargs["cwd"]))
                return type("Completed", (), {"returncode": 0})()

            with patch.object(self.runner.subprocess, "run", side_effect=fake_run):
                exit_code, _ = self.runner._run(["true"], paths, args)

            self.assertEqual(exit_code, 0)
            self.assertEqual(len(observed_cwd), 1)
            self.assertNotEqual(Path(observed_cwd[0]).resolve(), REPO_ROOT.resolve())
            self.assertFalse(Path(observed_cwd[0]).exists())

if __name__ == "__main__":
    unittest.main()
