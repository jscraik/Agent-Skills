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
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.skill_intake import build_skill_intake_receipt  # noqa: E402


VALID_SKILL = "Infrastructure/tests/fixtures/skills_sdk/valid_skill"
SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/skill-intake-receipt.v0.schema.json"


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
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


class TestSkillsSdkSkillIntake(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def assert_schema_valid(self, payload: dict) -> None:
        _validate_schema_subset(self.schema, payload, {"skill-intake-receipt": self.schema})

    def test_builder_inspects_directory_without_execution_or_install(self) -> None:
        receipt = build_skill_intake_receipt(REPO_ROOT, source=VALID_SKILL)

        self.assert_schema_valid(receipt)
        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["operation"], "skill_intake_inspect")
        self.assertEqual(receipt["skill_id"], "skills-sdk-valid-fixture")
        self.assertGreaterEqual(receipt["file_count"], 1)
        self.assertTrue(all(check["severity"] == "pass" for check in receipt["intake_checks"]))
        self.assertFalse(receipt["execution_performed"])
        self.assertFalse(receipt["install_performed"])
        self.assertFalse(receipt["projection_mutation_performed"])
        self.assertFalse(receipt["mutation_performed"])
        self.assertEqual(receipt["blockers"], [])

    def test_public_cli_emits_schema_valid_intake_receipt(self) -> None:
        payload = _run_json_command(
            sys.executable,
            "Infrastructure/bin/ask",
            "sdk",
            "intake",
            "inspect",
            VALID_SKILL,
            "--preview",
            "--json",
            "--robot",
        )

        receipt = payload["data"]["skills_sdk_intake_inspect"]["receipt"]
        self.assert_schema_valid(receipt)
        self.assertEqual(payload["data"]["skills_sdk_intake_inspect"]["status"], "preview")
        self.assertFalse(receipt["execution_performed"])
        self.assertFalse(receipt["install_performed"])
        self.assertFalse(receipt["projection_mutation_performed"])

    def test_builder_blocks_unapproved_top_level_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "external"
            source.mkdir()
            (source / "SKILL.md").write_text("---\nname: external\ndescription: external\n---\n\n# External\n", encoding="utf-8")
            (source / "README.md").write_text("unexpected", encoding="utf-8")
            hidden = source / "unexpected"
            hidden.mkdir()
            (hidden / "secret.txt").write_text("do not inspect", encoding="utf-8")

            receipt = build_skill_intake_receipt(REPO_ROOT, source=source.as_posix())

        self.assert_schema_valid(receipt)
        self.assertEqual(receipt["status"], "blocked")
        self.assertTrue(any(check["id"] == "approved_top_level_paths" for check in receipt["blockers"]))
        self.assertTrue(all(check["severity"] == "blocker" for check in receipt["blockers"]))
        self.assertNotIn("unexpected/secret.txt", {item["path"] for item in receipt["inspected_files"]})
        self.assertFalse(receipt["execution_performed"])
        self.assertFalse(receipt["mutation_performed"])

    def test_builder_does_not_walk_rejected_top_level_subtrees(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "external"
            source.mkdir()
            (source / "SKILL.md").write_text(
                "---\nname: external\ndescription: external\n---\n\n# External\n",
                encoding="utf-8",
            )
            rejected = source / "node_modules"
            rejected.mkdir()
            (rejected / "large-tree.txt").write_text("do not inspect", encoding="utf-8")

            with mock.patch.object(Path, "rglob", side_effect=AssertionError("unexpected recursive walk")):
                receipt = build_skill_intake_receipt(REPO_ROOT, source=source.as_posix())

        self.assert_schema_valid(receipt)
        self.assertEqual(receipt["status"], "blocked")
        self.assertTrue(any(check["id"] == "approved_top_level_paths" for check in receipt["blockers"]))
        self.assertEqual({item["path"] for item in receipt["inspected_files"]}, {"SKILL.md"})

    def test_builder_blocks_symlink_source_root_before_resolving(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            real_source = Path(tmp) / "real"
            real_source.mkdir()
            (real_source / "SKILL.md").write_text(
                "---\nname: external\ndescription: external\n---\n\n# External\n",
                encoding="utf-8",
            )
            symlink_source = Path(tmp) / "link"
            try:
                symlink_source.symlink_to(real_source, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")

            receipt = build_skill_intake_receipt(REPO_ROOT, source=symlink_source.as_posix())

        self.assert_schema_valid(receipt)
        self.assertEqual(receipt["status"], "blocked")
        self.assertTrue(any(check["id"] == "source_root_not_symlink" for check in receipt["blockers"]))
        self.assertFalse(receipt["execution_performed"])
        self.assertFalse(receipt["mutation_performed"])

    def test_builder_blocks_broad_filesystem_roots_before_scanning(self) -> None:
        receipt = build_skill_intake_receipt(REPO_ROOT, source=Path("/").as_posix())

        self.assert_schema_valid(receipt)
        self.assertEqual(receipt["status"], "blocked")
        self.assertTrue(any(check["id"] == "source_root_not_broad" for check in receipt["blockers"]))
        self.assertEqual(receipt["inspected_files"], [])
        self.assertFalse(receipt["execution_performed"])
        self.assertFalse(receipt["mutation_performed"])

    def test_archive_intake_is_explicitly_deferred(self) -> None:
        receipt = build_skill_intake_receipt(
            REPO_ROOT,
            source="external-skill.zip",
            source_kind="archive",
        )

        self.assert_schema_valid(receipt)
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["source_kind"], "archive")
        self.assertTrue(any(check["id"] == "source_kind_supported" for check in receipt["blockers"]))
        self.assertFalse(receipt["execution_performed"])
        self.assertFalse(receipt["install_performed"])


if __name__ == "__main__":
    unittest.main()
