import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from helpers.schema_validator import _validate_schema_subset


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure/scripts/lib"))
from ask.commands.skills_impl import skills_sdk_project_install  # noqa: E402
from ask.skills_sdk.project_install import ProjectInstallError, install_project_skill  # noqa: E402

TARGET = "Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md"
INSTALL_RECEIPT_SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/install-receipt.v1.schema.json"
LOCKFILE_SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/lockfile.v1.schema.json"


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


def _sha256_file(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _marked_project(tmp_path: Path) -> Path:
    project_root = tmp_path / "target-project"
    project_root.mkdir()
    (project_root / "AGENTS.md").write_text("# Target Project\n", encoding="utf-8")
    return project_root


class TestSkillsSdkProjectInstall(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.receipt_schema = json.loads(INSTALL_RECEIPT_SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.lockfile_schema = json.loads(LOCKFILE_SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.schemas = {
            "install-receipt.v1.schema.json": cls.receipt_schema,
            "lockfile.v1.schema.json": cls.lockfile_schema,
        }

    def assert_receipt_valid(self, payload: dict) -> None:
        _validate_schema_subset(self.receipt_schema, payload, self.schemas)

    def assert_lockfile_valid(self, payload: dict) -> None:
        _validate_schema_subset(self.lockfile_schema, payload, self.schemas)

    def test_apply_requires_project_root_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "install",
                TARGET,
                "--apply",
                "--json",
                "--robot",
            )

            self.assertEqual(process.returncode, 2, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_install"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertFalse(receipt["mutation_performed"])
            self.assertFalse((tmp_path / "skills.lock.json").exists())
            self.assertIn("--project-root", payload["errors"][0]["fix_suggestion"])

    def test_apply_refuses_unmarked_project_root_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "target-project"
            project_root.mkdir()
            process = _run_process(
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

            self.assertEqual(process.returncode, 2, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_install"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertFalse(receipt["mutation_performed"])
            self.assertIn("missing_project_marker", receipt["conflicts"])
            self.assertFalse((project_root / "skills.lock.json").exists())

    def test_apply_refuses_file_project_root_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_file = Path(tmp) / "not-a-directory"
            project_file.write_text("not a project root\n", encoding="utf-8")
            process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "install",
                TARGET,
                "--apply",
                "--project-root",
                str(project_file),
                "--json",
                "--robot",
            )

            self.assertEqual(process.returncode, 2, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_install"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertFalse(receipt["mutation_performed"])
            self.assertIn("project_root_not_directory", receipt["conflicts"])
            self.assertFalse(project_file.with_name("skills.lock.json").exists())

    def test_apply_writes_skill_receipt_and_lockfile_inside_marked_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            payload = _run_json_command(
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
            install_payload = payload["data"]["skills_sdk_project_install"]
            receipt = install_payload["receipt"]
            lockfile = json.loads((project_root / "skills.lock.json").read_text(encoding="utf-8"))

            self.assertEqual(payload["status"], "success")
            self.assertEqual(install_payload["status"], "success")
            self.assert_receipt_valid(receipt)
            self.assert_lockfile_valid(lockfile)
            self.assertTrue(receipt["mutation_performed"])
            self.assertEqual(receipt["lockfile_path"], "skills.lock.json")
            self.assertEqual(receipt["lockfile_after_digest"], _sha256_file(project_root / "skills.lock.json"))
            self.assertTrue((project_root / ".agents/skills/valid_skill/SKILL.md").is_file())
            self.assertTrue((project_root / ".harness/receipts/skills-sdk/install/valid_skill.json").is_file())
            self.assertIn("valid_skill", lockfile["entries"])
            self.assertEqual(lockfile["entries"]["valid_skill"]["installed_at"], "2026-06-05T00:00:00Z")
            self.assertIn(".agents/skills/valid_skill/SKILL.md", receipt["target_paths"])

    def test_apply_directory_source_uses_source_directory_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            project_root = _marked_project(tmp_path)
            source_root = tmp_path / "source-skill"
            source_root.mkdir()
            (source_root / "SKILL.md").write_text(
                "---\nname: source-skill\ndescription: source skill\n---\n\n# Source\n",
                encoding="utf-8",
            )

            payload = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "install",
                str(source_root),
                "--apply",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )
            receipt = payload["data"]["skills_sdk_project_install"]["receipt"]
            lockfile = json.loads((project_root / "skills.lock.json").read_text(encoding="utf-8"))

            self.assertTrue((project_root / ".agents/skills/source-skill/SKILL.md").is_file())
            self.assertFalse((project_root / ".agents/skills/tmp/SKILL.md").exists())
            self.assertIn("source-skill", lockfile["entries"])
            self.assertIn(".agents/skills/source-skill/SKILL.md", receipt["target_paths"])

    def test_public_wrapper_preserves_apply_contract(self) -> None:
        with tempfile.TemporaryDirectory() as ask_tmp, tempfile.TemporaryDirectory() as wrapper_tmp:
            ask_root = _marked_project(Path(ask_tmp))
            wrapper_root = _marked_project(Path(wrapper_tmp))
            ask_payload = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "install",
                TARGET,
                "--apply",
                "--project-root",
                str(ask_root),
                "--json",
                "--robot",
            )
            wrapper_payload = _run_json_command(
                sys.executable,
                "bin/skills-sdk",
                "install",
                TARGET,
                "--apply",
                "--project-root",
                str(wrapper_root),
                "--json",
                "--robot",
            )

            ask_receipt = ask_payload["data"]["skills_sdk_project_install"]["receipt"]
            wrapper_receipt = wrapper_payload["data"]["skills_sdk_project_install"]["receipt"]
            self.assertEqual(wrapper_receipt["files_written"], ask_receipt["files_written"])
            self.assertEqual(wrapper_receipt["source_digest"], ask_receipt["source_digest"])
            self.assertEqual(wrapper_receipt["mutation_performed"], ask_receipt["mutation_performed"])
            self.assertEqual(wrapper_payload["metadata"]["command"], f"sdk install {TARGET} --apply --project-root {wrapper_root} --json --robot")

    def test_existing_target_conflict_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            existing = project_root / ".agents/skills/valid_skill/SKILL.md"
            existing.parent.mkdir(parents=True)
            existing.write_text("do not overwrite\n", encoding="utf-8")
            process = _run_process(
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

            self.assertEqual(process.returncode, 4, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_install"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertFalse(receipt["mutation_performed"])
            self.assertEqual(existing.read_text(encoding="utf-8"), "do not overwrite\n")
            self.assertIn("target_exists:.agents/skills/valid_skill", receipt["conflicts"])
            self.assertIn("target_exists:.agents/skills/valid_skill/SKILL.md", receipt["conflicts"])

    def test_existing_install_directory_conflict_refuses_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            existing_dir = project_root / ".agents/skills/valid_skill"
            existing_dir.mkdir(parents=True)
            process = _run_process(
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

            self.assertEqual(process.returncode, 4, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_install"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertFalse(receipt["mutation_performed"])
            self.assertIn("target_exists:.agents/skills/valid_skill", receipt["conflicts"])
            self.assertFalse((existing_dir / "SKILL.md").exists())

    def test_symlinked_install_target_refuses_before_copying(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            target_base = project_root / ".agents/skills/valid_skill"
            target_base.parent.mkdir(parents=True)
            target_base.symlink_to(project_root / "missing-target")
            process = _run_process(
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

            self.assertEqual(process.returncode, 4, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_install"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertFalse(receipt["mutation_performed"])
            self.assertIn("target_symlink:.agents/skills/valid_skill", receipt["conflicts"])
            self.assertFalse((project_root / "missing-target/SKILL.md").exists())

    def test_symlinked_receipt_path_refuses_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            (project_root / ".harness").symlink_to(project_root / "missing-receipts-root")
            process = _run_process(
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

            self.assertEqual(process.returncode, 4, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_install"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertFalse(receipt["mutation_performed"])
            self.assertIn("target_symlink:.harness", receipt["conflicts"])
            self.assertFalse((project_root / "missing-receipts-root").exists())

    def test_invalid_lockfile_path_refuses_before_copying(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            (project_root / "skills.lock.json").mkdir()
            process = _run_process(
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

            self.assertEqual(process.returncode, 4, process.stdout)
            payload = json.loads(process.stdout)
            install_payload = payload["data"]["skills_sdk_project_install"]
            receipt = install_payload["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertEqual(install_payload["status"], "blocked")
            self.assertFalse(receipt["mutation_performed"])
            self.assertIn("metadata_invalid:skills.lock.json", receipt["conflicts"])
            self.assertFalse((project_root / ".agents/skills/valid_skill/SKILL.md").exists())

    def test_partial_receipt_reports_directory_only_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            project_root = _marked_project(tmp_path)
            source_root = tmp_path / "source-skill"
            source_root.mkdir()
            (source_root / "SKILL.md").write_text(
                "---\nname: source-skill\ndescription: source skill\n---\n\n# Source\n",
                encoding="utf-8",
            )

            with mock.patch("ask.skills_sdk.project_install.shutil.copyfile", side_effect=OSError("copy failed")):
                with self.assertRaises(ProjectInstallError) as raised:
                    install_project_skill(
                        REPO_ROOT,
                        query=str(source_root),
                        source_path=source_root,
                        target_info={"source_path": str(source_root)},
                        project_root=str(project_root),
                        installed_at="2026-06-05T00:00:00Z",
                    )

            receipt = raised.exception.receipt
            self.assert_receipt_valid(receipt)
            self.assertEqual(receipt["status"], "partial")
            self.assertTrue(receipt["mutation_performed"])
            self.assertEqual(receipt["files_written"], [])
            self.assertIn(".agents/skills/source-skill", receipt["rollback_metadata"]["installed_files"])
            self.assertTrue((project_root / ".agents/skills/source-skill").is_dir())

    def test_facade_preserves_partial_receipt_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            project_root = _marked_project(tmp_path)
            source_root = tmp_path / "source-skill"
            source_root.mkdir()
            (source_root / "SKILL.md").write_text(
                "---\nname: source-skill\ndescription: source skill\n---\n\n# Source\n",
                encoding="utf-8",
            )

            with mock.patch("ask.skills_sdk.project_install.shutil.copyfile", side_effect=OSError("copy failed")):
                result = skills_sdk_project_install(
                    REPO_ROOT,
                    str(source_root),
                    project_root=str(project_root),
                    scope="project",
                )

            install_payload = result.data["skills_sdk_project_install"]
            receipt = install_payload["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertEqual(result.status, "error")
            self.assertEqual(install_payload["status"], "partial")
            self.assertEqual(receipt["status"], "partial")
            self.assertTrue(receipt["mutation_performed"])

    def test_source_symlink_is_refused_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            project_root = _marked_project(tmp_path)
            source_root = tmp_path / "source-skill"
            source_root.mkdir()
            (source_root / "SKILL.md").write_text(
                "---\nname: source-skill\ndescription: source skill\n---\n\n# Source\n",
                encoding="utf-8",
            )
            scripts_dir = source_root / "scripts"
            scripts_dir.mkdir()
            outside = tmp_path / "outside.txt"
            outside.write_text("outside\n", encoding="utf-8")
            (scripts_dir / "outside.txt").symlink_to(outside)

            process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "install",
                str(source_root),
                "--apply",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )

            self.assertEqual(process.returncode, 2, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_install"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertFalse(receipt["mutation_performed"])
            self.assertIn("source_contains_symlink", receipt["conflicts"])
            self.assertFalse((project_root / ".agents/skills/source-skill").exists())

    def test_unapproved_top_level_source_entry_is_refused_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            project_root = _marked_project(tmp_path)
            source_root = tmp_path / "source-skill"
            source_root.mkdir()
            (source_root / "SKILL.md").write_text(
                "---\nname: source-skill\ndescription: source skill\n---\n\n# Source\n",
                encoding="utf-8",
            )
            (source_root / "README.md").write_text("unapproved\n", encoding="utf-8")

            process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "install",
                str(source_root),
                "--apply",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )

            self.assertEqual(process.returncode, 2, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_install"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertFalse(receipt["mutation_performed"])
            self.assertIn("source_contains_unapproved_top_level", receipt["conflicts"])
            self.assertFalse((project_root / ".agents/skills/source-skill").exists())


if __name__ == "__main__":
    unittest.main()
