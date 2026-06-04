import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers.schema_validator import _validate_schema_subset


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.install_preview import build_install_preview  # noqa: E402


TARGET = "Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md"
INSTALL_SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/install-preview.v1.schema.json"
LOCKFILE_SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/lockfile-preview.v1.schema.json"


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("XDG_CACHE_HOME", "/private/tmp/agent-skills-xdg-cache")
    env.setdefault("XDG_STATE_HOME", "/private/tmp/agent-skills-xdg-state")
    env.setdefault("MISE_CACHE_DIR", "/private/tmp/agent-skills-mise-cache")
    env.setdefault("UV_CACHE_DIR", "/private/tmp/agent-skills-uv-cache")
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    return env


def _run_json_command(*args: str) -> dict:
    process = subprocess.run(
        list(args),
        cwd=REPO_ROOT,
        env=_command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        raise AssertionError(
            f"{' '.join(args)} failed with {process.returncode}\nSTDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
        )
    return json.loads(process.stdout)


class TestSkillsSdkInstallPreview(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.install_schema = json.loads(INSTALL_SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.lockfile_schema = json.loads(LOCKFILE_SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.schemas = {
            "install-preview": cls.install_schema,
            "lockfile-preview": cls.lockfile_schema,
            "lockfile-preview.v1.schema.json": cls.lockfile_schema,
        }

    def assert_schema_valid(self, payload: dict) -> None:
        _validate_schema_subset(self.install_schema, payload, self.schemas)

    def test_ask_sdk_install_preview_emits_schema_valid_read_only_payload(self) -> None:
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "install",
            TARGET,
            "--preview",
            "--json",
            "--robot",
        )
        preview = payload["data"]["skills_sdk_install_preview"]["preview"]

        self.assert_schema_valid(preview)
        self.assertEqual(payload["data"]["skills_sdk_install_preview"]["status"], "preview")
        self.assertFalse(preview["mutation_performed"])
        self.assertEqual(preview["lockfile_delta_preview"]["lockfile_path"], "skills.lock.json")
        self.assertFalse(preview["lockfile_delta_preview"]["would_write"])
        self.assertIn(".agents/skills/valid_skill", preview["target_paths"])
        self.assertIn("skills.lock.json", preview["target_paths"])

    def test_public_wrapper_preserves_install_preview_contract(self) -> None:
        ask_payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "install",
            TARGET,
            "--preview",
            "--json",
            "--robot",
        )
        wrapper_payload = _run_json_command(
            sys.executable,
            "bin/skills-sdk",
            "install",
            TARGET,
            "--preview",
            "--json",
            "--robot",
        )

        ask_preview = ask_payload["data"]["skills_sdk_install_preview"]["preview"]
        wrapper_preview = wrapper_payload["data"]["skills_sdk_install_preview"]["preview"]
        self.assertEqual(wrapper_preview, ask_preview)
        self.assertEqual(wrapper_payload["metadata"]["command"], f"sdk install {TARGET} --preview --json --robot")

    def test_sdk_install_without_preview_is_blocked(self) -> None:
        process = subprocess.run(
            [sys.executable, "Infrastructure/bin/ask", "sdk", "install", TARGET, "--json", "--robot"],
            cwd=REPO_ROOT,
            env=_command_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(process.returncode, 2, process.stdout)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "error")
        self.assertIn("--preview", payload["errors"][0]["message"])

    def test_preview_builder_does_not_write_lockfile_trust_projection_or_global_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            source_dir = repo_root / "Skills" / "sample"
            source_dir.mkdir(parents=True)
            source = source_dir / "SKILL.md"
            source.write_text("---\nname: sample\ndescription: sample\n---\n\n# Sample\n", encoding="utf-8")
            watched_paths = [
                repo_root / "skills.lock.json",
                repo_root / ".agents" / "skills" / "sample",
                repo_root / ".codex" / "skills" / "sample",
                repo_root / ".harness" / "receipts" / "skills-sdk" / "install-preview" / "sample.json",
            ]

            preview = build_install_preview(
                repo_root,
                query="Skills/sample/SKILL.md",
                scope="project",
                source_path=source,
                target_info={"source_path": "Skills/sample/SKILL.md", "handle": None},
            )

            self.assert_schema_valid(preview)
            self.assertFalse(preview["mutation_performed"])
            for path in watched_paths:
                self.assertFalse(path.exists(), f"preview unexpectedly wrote {path}")


if __name__ == "__main__":
    unittest.main()
