"""Prove current README count refresh through the workspace-sync entrypoint."""

from types import SimpleNamespace
from unittest import TestCase, mock

from tests import test_ask_skills_sync_security as sync_fixture

skills_commands = sync_fixture.skills_commands


class TestWorkspaceCatalogMarker(TestCase):
    setUp = sync_fixture.TestAskSkillsSyncSecurity.setUp
    tearDown = sync_fixture.TestAskSkillsSyncSecurity.tearDown

    def test_flat_workspace_preserves_intro_and_dry_run_then_refreshes_marker(self) -> None:
        path = self.repo_root / "README.md"
        before = "# Agent Skills Kit\n\nTransitional introduction.\n**120 canonical skills**\n"
        before = before.replace("**120", "Catalog parity marker: **120")
        path.write_text(before, encoding="utf-8")
        (self.source_dir / "SKILL.md").write_text(
            "---\nname: safe-skill\ndescription: Safe skill.\n---\n", encoding="utf-8"
        )
        entry = SimpleNamespace(name="safe-skill", source_dir=self.source_dir,
                                category="Skills/agent-ops", description="Safe skill.")
        with mock.patch.object(skills_commands, "discover_catalog_entries", return_value=[entry]):
            preview = skills_commands.sync_skills(
                self.repo_root, scope="workspace", dry_run=True, projection="flat"
            )
            self.assertEqual(preview.status, "success")
            self.assertEqual(path.read_text(encoding="utf-8"), before)
            result = skills_commands.sync_skills(
                self.repo_root, scope="workspace", dry_run=False, projection="flat"
            )
        self.assertEqual(result.status, "success")
        self.assertEqual(path.read_text(encoding="utf-8"), before.replace("120", "1"))
        self.assertIn("`total_skills`: 1", (self.repo_root / "SKILL.md").read_text())

    def test_workspace_sync_preserves_unrecognised_project_readme(self) -> None:
        """Ordinary project READMEs are caller content, not catalogue projections."""
        path = self.repo_root / "README.md"
        before = "# My Project\n\nApplication setup and user-owned notes.\n"
        path.write_text(before, encoding="utf-8")
        (self.source_dir / "SKILL.md").write_text(
            "---\nname: safe-skill\ndescription: Safe skill.\n---\n", encoding="utf-8"
        )
        for dry_run in (True, False):
            result = skills_commands.sync_skills(
                self.repo_root, scope="workspace", dry_run=dry_run, projection="flat"
            )
            self.assertEqual(result.status, "success")
            self.assertEqual(path.read_text(encoding="utf-8"), before)
