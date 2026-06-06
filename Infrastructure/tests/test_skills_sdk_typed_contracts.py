import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure/scripts/lib"))

from ask.skills_sdk.typed_contracts import (  # noqa: E402
    validate_cleanup_receipt,
    validate_install_receipt,
    validate_lockfile,
)


TARGET = "Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md"


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    env.setdefault("ASK_SKILLS_SDK_INSTALL_TIMESTAMP", "2026-06-05T00:00:00Z")
    return env


def _run_json_command(*args: str) -> dict[str, object]:
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
    payload = json.loads(process.stdout)
    if not isinstance(payload, dict):
        raise AssertionError("ask sdk command returned a non-object JSON payload")
    return payload


def _marked_project(tmp_path: Path) -> Path:
    project_root = tmp_path / "target-project"
    project_root.mkdir()
    (project_root / "AGENTS.md").write_text("# Target Project\n", encoding="utf-8")
    return project_root


class TestSkillsSdkTypedContracts(unittest.TestCase):
    def test_install_lockfile_and_cleanup_outputs_validate_as_typed_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            install_payload = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "install",
                TARGET,
                "--apply",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )
            install_data = install_payload["data"]
            if not isinstance(install_data, dict):
                raise AssertionError("install payload data is not an object")
            install_result = install_data["skills_sdk_project_install"]
            if not isinstance(install_result, dict):
                raise AssertionError("install result is not an object")
            install_receipt = validate_install_receipt(install_result["receipt"])

            lockfile = validate_lockfile(json.loads((project_root / "skills.lock.json").read_text(encoding="utf-8")))
            self.assertIn("valid_skill", lockfile.entries)
            self.assertEqual(install_receipt.status, "success")

            rollback_payload = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "rollback",
                "--receipt",
                str(project_root / ".harness/receipts/skills-sdk/install/valid_skill.json"),
                "--preview",
                "--json",
                "--robot",
            )
            rollback_data = rollback_payload["data"]
            if not isinstance(rollback_data, dict):
                raise AssertionError("rollback payload data is not an object")
            rollback_result = rollback_data["skills_sdk_project_rollback"]
            if not isinstance(rollback_result, dict):
                raise AssertionError("rollback result is not an object")
            rollback_receipt = validate_cleanup_receipt(rollback_result["receipt"])

            self.assertEqual(rollback_receipt.operation, "rollback")
            self.assertEqual(rollback_receipt.status, "preview")
            self.assertIsNone(rollback_receipt.cleanup_journal_name)
            self.assertEqual(rollback_receipt.directory_prune_results, [])


if __name__ == "__main__":
    unittest.main()
