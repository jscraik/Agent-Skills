import shutil
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting"))

import skill_discovery  # noqa: E402
import verify_runtime_budget  # noqa: E402


class TestSkillScopePrecedence(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="skill-scope-precedence-")).resolve()
        self.repo_root = self.temp_dir / "repo"
        self.repo_root.mkdir()
        (self.repo_root / ".agents" / "skills").mkdir(parents=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_skill(self, relative_dir: str, description: str) -> Path:
        skill_dir = self.repo_root / relative_dir
        skill_dir.mkdir(parents=True)
        skill_dir.joinpath("SKILL.md").write_text(
            f"---\nname: {skill_dir.name}\ndescription: {description}\n---\n",
            encoding="utf-8",
        )
        return skill_dir

    @contextmanager
    def _patched_repo(self, *, default_visible: Optional[set[str]] = None) -> Iterator[None]:
        visible = default_visible if default_visible is not None else {"shared-skill"}
        with (
            mock.patch.object(skill_discovery, "REPO_ROOT", self.repo_root),
            mock.patch.object(skill_discovery, "FLAT_SKILLS_DIR", self.repo_root / ".agents" / "skills"),
            mock.patch.object(
                skill_discovery,
                "SYSTEM_LANE_DIR",
                self.repo_root / ".agents" / "skills" / ".system",
            ),
            mock.patch.object(skill_discovery, "REPO_SCAN_ROOTS", ("Skills",)),
            mock.patch.object(skill_discovery, "POLICY_PLUGIN_SKILL_ROOT_GLOB", "./Plugins/*/skills"),
            mock.patch.object(skill_discovery, "HIDDEN_FLAT_SKILL_NAMES", set()),
            mock.patch.object(skill_discovery, "DEFAULT_VISIBLE_FLAT_SKILL_NAMES", set(visible)),
            mock.patch.object(skill_discovery, "PLUGIN_VISIBLE_ROUTER_SKILL_NAMES", set(visible)),
            mock.patch.object(skill_discovery, "PLUGIN_HIDDEN_LANE_SKILL_NAMES", set()),
            mock.patch.object(verify_runtime_budget, "REPO_ROOT", self.repo_root),
            mock.patch.object(verify_runtime_budget, "DEFAULT_VISIBLE_FLAT_SKILL_NAMES", tuple(visible)),
        ):
            yield

    def test_project_overlay_wins_repo_discovery_collision(self) -> None:
        self._write_skill("Skills/agent-ops/shared-skill", "Global skill.")
        self._write_skill("Plugins/local-pack/skills/shared-skill", "Local plugin skill.")
        project_skill = self._write_skill("Skills/project/shared-skill", "Project skill.")

        with self._patched_repo():
            entries = skill_discovery.discover_skill_entries(source="repo", visibility="advanced")
            project_scope = skill_discovery.classify_skill_scope(project_skill)

        selected = [entry for entry in entries if entry.name == "shared-skill"]
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].source_dir, project_skill.resolve())
        self.assertEqual(project_scope, "project")

    def test_local_plugin_wins_global_repo_discovery_collision(self) -> None:
        self._write_skill("Skills/agent-ops/shared-skill", "Global skill.")
        plugin_skill = self._write_skill("Plugins/local-pack/skills/shared-skill", "Local plugin skill.")

        with self._patched_repo():
            entries = skill_discovery.discover_skill_entries(source="repo", visibility="advanced")
            plugin_scope = skill_discovery.classify_skill_scope(plugin_skill)

        selected = [entry for entry in entries if entry.name == "shared-skill"]
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].source_dir, plugin_skill.resolve())
        self.assertEqual(plugin_scope, "local-plugin")

    def test_flat_runtime_discovery_remains_flat_first(self) -> None:
        flat_skill = self._write_skill(".agents/skills/shared-skill", "Flat runtime skill.")
        self._write_skill("Plugins/local-pack/skills/shared-skill", "Local plugin skill.")

        with self._patched_repo():
            entries = skill_discovery.discover_skill_entries(source="flat", visibility="advanced")

        selected = [entry for entry in entries if entry.name == "shared-skill"]
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].source_dir, flat_skill.resolve())

    def test_runtime_budget_fails_unresolved_same_scope_collision(self) -> None:
        self._write_skill("Plugins/alpha/skills/shared-skill", "Alpha local plugin.")
        self._write_skill("Plugins/beta/skills/shared-skill", "Beta local plugin.")

        with self._patched_repo(default_visible=set()):
            report = verify_runtime_budget.build_report()

        self.assertEqual(report["status"], "fail")
        self.assertIn(
            "UNRESOLVED_SCOPE_COLLISIONS",
            {violation["code"] for violation in report["violations"]},
        )

    def test_rooted_runtime_allows_primary_runtime_lane(self) -> None:
        for skill_set in verify_runtime_budget.ROOT_SKILL_SETS:
            self._write_skill(f".agents/skills/{skill_set}", f"{skill_set} root skill set.")
        self._write_skill(".agents/skills/codex-primary-runtime", "Bundled primary runtime skills.")

        with self._patched_repo(default_visible=set()):
            report = verify_runtime_budget.build_report()

        self.assertEqual(report["projection_mode"], "rooted")
        self.assertNotIn(
            "ROOTED_POLICY_NAME_DRIFT",
            {violation["code"] for violation in report["violations"]},
        )


if __name__ == "__main__":
    unittest.main()
