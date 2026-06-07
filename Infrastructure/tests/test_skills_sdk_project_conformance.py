import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers.schema_validator import _validate_schema_subset


REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET = "Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md"
CONFORMANCE_SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/project-conformance-receipt.v1.schema.json"


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


def _run_process(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=REPO_ROOT,
        env=_command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _run_json_command(*args: str) -> dict:
    process = _run_process(*args)
    if process.returncode != 0:
        raise AssertionError(
            f"{' '.join(args)} failed with {process.returncode}\nSTDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
        )
    return json.loads(process.stdout)


def _marked_project(tmp_path: Path) -> Path:
    project_root = tmp_path / "target-project"
    project_root.mkdir()
    (project_root / "AGENTS.md").write_text("# Target Project\n", encoding="utf-8")
    return project_root


def _install_valid_skill(project_root: Path) -> dict:
    return _run_json_command(
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


class TestSkillsSdkProjectConformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(CONFORMANCE_SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.schemas = {"project-conformance-receipt.v1.schema.json": cls.schema}

    def assert_receipt_valid(self, payload: dict) -> None:
        _validate_schema_subset(self.schema, payload, self.schemas)

    def test_status_accepts_empty_marked_project_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            payload = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "project",
                "status",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )

            receipt = payload["data"]["skills_sdk_project_conformance"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertEqual(receipt["status"], "pass")
            self.assertTrue(receipt["project_managed"])
            self.assertEqual(receipt["installed_skill_count"], 0)
            self.assertFalse(receipt["mutation_performed"])
            self.assertFalse((project_root / "skills.lock.json").exists())

    def test_status_reports_installed_skill_cleanup_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)

            payload = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "project",
                "status",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )

            receipt = payload["data"]["skills_sdk_project_conformance"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertEqual(receipt["status"], "pass")
            self.assertEqual(receipt["installed_skill_count"], 1)
            self.assertEqual(receipt["rollback_ready_count"], 1)
            self.assertEqual(receipt["uninstall_ready_count"], 1)
            self.assertEqual(receipt["installed_skills"][0]["status"], "healthy")
            self.assertTrue(receipt["installed_skills"][0]["rollback_ready"])

    def test_doctor_blocks_on_modified_installed_file_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)
            skill_file = project_root / ".agents/skills/valid_skill/SKILL.md"
            before_lockfile = (project_root / "skills.lock.json").read_text(encoding="utf-8")
            skill_file.write_text(skill_file.read_text(encoding="utf-8") + "\n# Local edit\n", encoding="utf-8")

            process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "project",
                "doctor",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )

            self.assertEqual(process.returncode, 2, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_conformance"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertEqual(receipt["status"], "blocked")
            self.assertIn("installed_file_modified", receipt["installed_skills"][0]["issue_codes"][0])
            self.assertFalse(receipt["mutation_performed"])
            self.assertEqual((project_root / "skills.lock.json").read_text(encoding="utf-8"), before_lockfile)

    def test_status_blocks_on_missing_install_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)
            (project_root / ".harness/receipts/skills-sdk/install/valid_skill.json").unlink()

            process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "project",
                "status",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )

            self.assertEqual(process.returncode, 2, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_conformance"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertEqual(receipt["status"], "blocked")
            self.assertIn("missing_receipt", receipt["installed_skills"][0]["issue_codes"])
            self.assertFalse(receipt["installed_skills"][0]["rollback_ready"])

    def test_status_refuses_unmarked_project_root_before_reading_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "unmarked"
            project_root.mkdir()

            process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "project",
                "status",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )

            self.assertEqual(process.returncode, 2, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_conformance"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertFalse(receipt["project_managed"])
            self.assertIn("missing_project_marker", receipt["issues"][0]["code"])
            self.assertFalse((project_root / "skills.lock.json").exists())

    def test_status_blocks_on_malformed_lockfile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            (project_root / "skills.lock.json").write_text("{broken", encoding="utf-8")

            process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "project",
                "status",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )

            self.assertEqual(process.returncode, 2, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_conformance"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertEqual(receipt["lockfile_status"], "invalid")
            self.assertEqual(receipt["issues"][0]["code"], "malformed_lockfile")

    def test_public_wrapper_matches_ask_project_status(self) -> None:
        with tempfile.TemporaryDirectory() as ask_tmp, tempfile.TemporaryDirectory() as wrapper_tmp:
            ask_root = _marked_project(Path(ask_tmp))
            wrapper_root = _marked_project(Path(wrapper_tmp))

            ask_payload = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "project",
                "status",
                "--project-root",
                str(ask_root),
                "--json",
                "--robot",
            )
            wrapper_payload = _run_json_command(
                sys.executable,
                "bin/skills-sdk",
                "project",
                "status",
                "--project-root",
                str(wrapper_root),
                "--json",
                "--robot",
            )

            ask_receipt = ask_payload["data"]["skills_sdk_project_conformance"]["receipt"]
            wrapper_receipt = wrapper_payload["data"]["skills_sdk_project_conformance"]["receipt"]
            ask_receipt["project_root"] = "<normalized>"
            ask_receipt["project_root_identity"] = {"identity_kind": "realpath", "realpath": "<normalized>", "exists": True}
            wrapper_receipt["project_root"] = "<normalized>"
            wrapper_receipt["project_root_identity"] = {"identity_kind": "realpath", "realpath": "<normalized>", "exists": True}
            self.assertEqual(wrapper_receipt, ask_receipt)
            self.assertEqual(wrapper_payload["metadata"]["command"], "sdk project status --project-root " + str(wrapper_root) + " --json --robot")


if __name__ == "__main__":
    unittest.main()
