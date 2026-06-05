import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Optional

from helpers.schema_validator import _validate_schema_subset


REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET = "Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md"
CLEANUP_RECEIPT_SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/project-cleanup-receipt.v1.schema.json"
INSTALL_RECEIPT_SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/install-receipt.v1.schema.json"
LOCKFILE_SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/lockfile.v1.schema.json"


def _command_env(extra: Optional[dict[str, str]] = None) -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    env.setdefault("ASK_SKILLS_SDK_INSTALL_TIMESTAMP", "2026-06-05T00:00:00Z")
    if extra:
        env.update(extra)
    return env


def _run_process(*args: str, extra_env: Optional[dict[str, str]] = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=REPO_ROOT,
        env=_command_env(extra_env),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _run_json_command(*args: str, extra_env: Optional[dict[str, str]] = None) -> dict:
    process = _run_process(*args, extra_env=extra_env)
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


def _receipt_path(project_root: Path) -> Path:
    return project_root / ".harness/receipts/skills-sdk/install/valid_skill.json"


def _sha256_file(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


class TestSkillsSdkProjectCleanup(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cleanup_schema = json.loads(CLEANUP_RECEIPT_SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.install_schema = json.loads(INSTALL_RECEIPT_SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.lockfile_schema = json.loads(LOCKFILE_SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.schemas = {
            "project-cleanup-receipt.v1.schema.json": cls.cleanup_schema,
            "install-receipt.v1.schema.json": cls.install_schema,
            "lockfile.v1.schema.json": cls.lockfile_schema,
        }

    def assert_cleanup_receipt_valid(self, payload: dict) -> None:
        _validate_schema_subset(self.cleanup_schema, payload, self.schemas)

    def test_rollback_preview_without_project_root_is_receipt_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)
            payload = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "rollback",
                "--receipt",
                str(_receipt_path(project_root)),
                "--preview",
                "--json",
                "--robot",
            )

            receipt = payload["data"]["skills_sdk_project_rollback"]["receipt"]
            self.assert_cleanup_receipt_valid(receipt)
            self.assertEqual(receipt["status"], "preview")
            self.assertFalse(receipt["mutation_performed"])
            self.assertFalse(receipt["live_project_validation"])
            self.assertTrue((project_root / ".agents/skills/valid_skill/SKILL.md").exists())

    def test_rollback_apply_removes_digest_matched_file_and_lock_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)
            payload = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "rollback",
                "--receipt",
                str(_receipt_path(project_root)),
                "--apply",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )

            receipt = payload["data"]["skills_sdk_project_rollback"]["receipt"]
            self.assert_cleanup_receipt_valid(receipt)
            self.assertTrue(receipt["mutation_performed"])
            self.assertFalse((project_root / ".agents/skills/valid_skill/SKILL.md").exists())
            lockfile = json.loads((project_root / "skills.lock.json").read_text(encoding="utf-8"))
            self.assertNotIn("valid_skill", lockfile["entries"])

    def test_rollback_apply_refuses_receipt_not_bound_to_lockfile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)
            copied_receipt = project_root / ".harness/receipts/skills-sdk/install/copied-valid-skill.json"
            copied_receipt.write_text(_receipt_path(project_root).read_text(encoding="utf-8"), encoding="utf-8")

            process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "rollback",
                "--receipt",
                str(copied_receipt),
                "--apply",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )

            self.assertEqual(process.returncode, 4, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_rollback"]["receipt"]
            self.assertFalse(receipt["mutation_performed"])
            self.assertEqual(receipt["files_blocked"][0]["reason"], "mismatched_lockfile_receipt_binding")
            self.assertTrue((project_root / ".agents/skills/valid_skill/SKILL.md").exists())

    def test_uninstall_preview_and_apply_resolve_through_lockfile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)
            preview = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "uninstall",
                "valid_skill",
                "--project-root",
                str(project_root),
                "--preview",
                "--json",
                "--robot",
            )
            preview_receipt = preview["data"]["skills_sdk_project_uninstall"]["receipt"]
            self.assert_cleanup_receipt_valid(preview_receipt)
            self.assertFalse(preview_receipt["mutation_performed"])

            applied = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "uninstall",
                "valid_skill",
                "--project-root",
                str(project_root),
                "--apply",
                "--json",
                "--robot",
            )
            receipt = applied["data"]["skills_sdk_project_uninstall"]["receipt"]
            self.assert_cleanup_receipt_valid(receipt)
            self.assertTrue(receipt["mutation_performed"])
            self.assertFalse((project_root / ".agents/skills/valid_skill/SKILL.md").exists())

    def test_modified_file_is_preserved_as_manual_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)
            skill_file = project_root / ".agents/skills/valid_skill/SKILL.md"
            before_digest = _sha256_file(skill_file)
            skill_file.write_text(skill_file.read_text(encoding="utf-8") + "\n# user edit\n", encoding="utf-8")
            self.assertNotEqual(before_digest, _sha256_file(skill_file))

            payload = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "rollback",
                "--receipt",
                str(_receipt_path(project_root)),
                "--apply",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )
            receipt = payload["data"]["skills_sdk_project_rollback"]["receipt"]
            self.assertEqual(receipt["status"], "partial")
            self.assertTrue(skill_file.exists())
            self.assertEqual(receipt["files_skipped"][0]["reason"], "modified_file_digest_mismatch")
            self.assertTrue(receipt["manual_actions"])
            lockfile = json.loads((project_root / "skills.lock.json").read_text(encoding="utf-8"))
            self.assertIn("valid_skill", lockfile["entries"])

    def test_mode_validation_fails_before_receipt_or_lockfile_loading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "rollback",
                "--receipt",
                str(project_root / "missing.json"),
                "--json",
                "--robot",
            )
            self.assertEqual(process.returncode, 2, process.stdout)
            payload = json.loads(process.stdout)
            self.assertEqual(payload["errors"][0]["code"], "ERR_VALIDATION")
            self.assertIn("exactly one", payload["errors"][0]["message"])

    def test_live_repo_root_is_refused_for_apply(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)
            process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "rollback",
                "--receipt",
                str(_receipt_path(project_root)),
                "--apply",
                "--project-root",
                str(REPO_ROOT),
                "--json",
                "--robot",
            )
            self.assertEqual(process.returncode, 2, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_rollback"]["receipt"]
            self.assertFalse(receipt["mutation_performed"])

    def test_unresolved_cleanup_journal_blocks_rerun(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)
            interrupted = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "rollback",
                "--receipt",
                str(_receipt_path(project_root)),
                "--apply",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
                extra_env={"ASK_SKILLS_SDK_CLEANUP_INTERRUPT_AFTER_JOURNAL": "1"},
            )
            self.assertEqual(interrupted.returncode, 4, interrupted.stdout)
            interrupted_payload = json.loads(interrupted.stdout)
            interrupted_receipt = interrupted_payload["data"]["skills_sdk_project_rollback"]["receipt"]
            self.assertFalse(interrupted_receipt["mutation_performed"])
            self.assertIn("interrupted_after_cleanup_journal", interrupted_receipt["manual_actions"][0]["reason"])
            journals = list((project_root / ".harness/state/skills-sdk/cleanup").glob("*.json"))
            self.assertEqual(len(journals), 1)

            rerun = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "rollback",
                "--receipt",
                str(_receipt_path(project_root)),
                "--apply",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )
            self.assertEqual(rerun.returncode, 4, rerun.stdout)
            payload = json.loads(rerun.stdout)
            receipt = payload["data"]["skills_sdk_project_rollback"]["receipt"]
            self.assertFalse(receipt["mutation_performed"])
            self.assertIn("unresolved_cleanup_journal", receipt["manual_actions"][0]["reason"])

    def test_public_wrapper_preserves_rollback_and_uninstall_preview_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)

            ask_rollback = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "rollback",
                "--receipt",
                str(_receipt_path(project_root)),
                "--preview",
                "--json",
                "--robot",
            )
            wrapper_rollback = _run_json_command(
                sys.executable,
                "bin/skills-sdk",
                "rollback",
                "--receipt",
                str(_receipt_path(project_root)),
                "--preview",
                "--json",
                "--robot",
            )
            self.assertEqual(
                wrapper_rollback["data"]["skills_sdk_project_rollback"],
                ask_rollback["data"]["skills_sdk_project_rollback"],
            )

            ask_uninstall = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "uninstall",
                "valid_skill",
                "--project-root",
                str(project_root),
                "--preview",
                "--json",
                "--robot",
            )
            wrapper_uninstall = _run_json_command(
                sys.executable,
                "bin/skills-sdk",
                "uninstall",
                "valid_skill",
                "--project-root",
                str(project_root),
                "--preview",
                "--json",
                "--robot",
            )
            self.assertEqual(
                wrapper_uninstall["data"]["skills_sdk_project_uninstall"],
                ask_uninstall["data"]["skills_sdk_project_uninstall"],
            )

    def test_uninstall_refuses_duplicate_active_lockfile_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)
            lockfile_path = project_root / "skills.lock.json"
            lockfile = json.loads(lockfile_path.read_text(encoding="utf-8"))
            lockfile["entries"]["duplicate-valid-skill"] = dict(lockfile["entries"]["valid_skill"])
            lockfile_path.write_text(json.dumps(lockfile, indent=2) + "\n", encoding="utf-8")

            process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "uninstall",
                "valid_skill",
                "--project-root",
                str(project_root),
                "--preview",
                "--json",
                "--robot",
            )

            self.assertEqual(process.returncode, 4, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_uninstall"]["receipt"]
            self.assertFalse(receipt["mutation_performed"])
            self.assertEqual(receipt["files_blocked"][0]["reason"], "duplicate_active_skill_id")

    def test_uninstall_refuses_mismatched_lockfile_receipt_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)
            lockfile_path = project_root / "skills.lock.json"
            lockfile = json.loads(lockfile_path.read_text(encoding="utf-8"))
            lockfile["entries"]["valid_skill"]["files"][0]["digest"] = "sha256:0"
            lockfile_path.write_text(json.dumps(lockfile, indent=2) + "\n", encoding="utf-8")

            process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "uninstall",
                "valid_skill",
                "--project-root",
                str(project_root),
                "--apply",
                "--json",
                "--robot",
            )

            self.assertEqual(process.returncode, 4, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_uninstall"]["receipt"]
            self.assertFalse(receipt["mutation_performed"])
            self.assertEqual(receipt["files_blocked"][0]["reason"], "mismatched_lockfile_receipt_binding")

    def test_uninstall_refuses_escaped_lockfile_receipt_ref_as_structured_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)
            lockfile_path = project_root / "skills.lock.json"
            lockfile = json.loads(lockfile_path.read_text(encoding="utf-8"))
            lockfile["entries"]["valid_skill"]["receipt_ref"] = "../outside.json"
            lockfile_path.write_text(json.dumps(lockfile, indent=2) + "\n", encoding="utf-8")

            process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "uninstall",
                "valid_skill",
                "--project-root",
                str(project_root),
                "--preview",
                "--json",
                "--robot",
            )

            self.assertEqual(process.returncode, 2, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_uninstall"]["receipt"]
            self.assertFalse(receipt["mutation_performed"])
            self.assertTrue(receipt["files_blocked"][0]["reason"].startswith("path_escape:"))

    def test_uninstall_refuses_missing_lockfile_receipt_ref_as_structured_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)
            _receipt_path(project_root).unlink()

            process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "uninstall",
                "valid_skill",
                "--project-root",
                str(project_root),
                "--preview",
                "--json",
                "--robot",
            )

            self.assertEqual(process.returncode, 2, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_uninstall"]["receipt"]
            self.assertFalse(receipt["mutation_performed"])
            self.assertEqual(receipt["files_blocked"][0]["reason"], "missing_receipt")

    def test_apply_blocks_symlink_and_hardlink_targets_before_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)
            skill_file = project_root / ".agents/skills/valid_skill/SKILL.md"
            original_content = skill_file.read_bytes()
            skill_file.unlink()
            outside_file = Path(tmp) / "outside-skill.md"
            outside_file.write_bytes(original_content)
            skill_file.symlink_to(outside_file)

            symlink_process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "rollback",
                "--receipt",
                str(_receipt_path(project_root)),
                "--apply",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )
            self.assertEqual(symlink_process.returncode, 4, symlink_process.stdout)
            symlink_payload = json.loads(symlink_process.stdout)
            symlink_receipt = symlink_payload["data"]["skills_sdk_project_rollback"]["receipt"]
            self.assertFalse(symlink_receipt["mutation_performed"])
            self.assertTrue(symlink_receipt["files_blocked"][0]["reason"].startswith("target_symlink"))
            self.assertTrue(outside_file.exists())

        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)
            skill_file = project_root / ".agents/skills/valid_skill/SKILL.md"
            hardlink_peer = project_root / ".agents/skills/valid_skill/SKILL.link"
            hardlink_peer.hardlink_to(skill_file)

            hardlink_process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "rollback",
                "--receipt",
                str(_receipt_path(project_root)),
                "--apply",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )
            self.assertEqual(hardlink_process.returncode, 4, hardlink_process.stdout)
            hardlink_payload = json.loads(hardlink_process.stdout)
            hardlink_receipt = hardlink_payload["data"]["skills_sdk_project_rollback"]["receipt"]
            self.assertFalse(hardlink_receipt["mutation_performed"])
            self.assertEqual(hardlink_receipt["files_blocked"][0]["reason"], "target_hardlink")


if __name__ == "__main__":
    unittest.main()
