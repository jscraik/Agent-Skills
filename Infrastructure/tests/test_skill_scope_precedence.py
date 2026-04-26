import shutil
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from collections.abc import Iterator
from typing import Optional
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
        """
        Remove the temporary test directory created in setUp, ignoring any filesystem errors.
        """
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_skill(self, relative_dir: str, description: str) -> Path:
        """
        Create a skill directory under the test repository and write a `SKILL.md` file containing YAML frontmatter.
        
        Parameters:
            relative_dir (str): Path, relative to the test repository root, where the skill directory will be created.
            description (str): Description text to include in the `SKILL.md` frontmatter.
        
        Returns:
            Path: The filesystem path of the created skill directory.
        """
        skill_dir = self.repo_root / relative_dir
        skill_dir.mkdir(parents=True)
        skill_dir.joinpath("SKILL.md").write_text(
            f"---\nname: {skill_dir.name}\ndescription: {description}\n---\n",
            encoding="utf-8",
        )
        return skill_dir

    @contextmanager
    def _patched_repo(self, *, default_visible: Optional[set[str]] = None) -> Iterator[None]:
        """
        Provide a context manager that temporarily patches skill discovery and runtime-budget configuration constants to point at the test repository.
        
        Parameters:
        	default_visible (Optional[set[str]]): Set of flat skill names treated as visible during the patched context; if omitted, defaults to {"shared-skill"}.
        
        Description:
        	The context manager patches module-level settings in both `skill_discovery` and `verify_runtime_budget` (including repository root, flat skills directory, system lane, scan roots, plugin skill glob, and visibility/hidden name sets) so tests operate against `self.repo_root`. Use in a `with` statement to apply the patches for the block's duration.
        """
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
            mock.patch.object(verify_runtime_budget, "DEFAULT_VISIBLE_FLAT_SKILLS", set(visible)),
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

    def test_runtime_budget_flags_mixed_rooted_and_flat_first_level_runtime(self) -> None:
        self._write_skill(".agents/skills/agent-ops", "Root skill set.")
        self._write_skill(".agents/skills/autofix", "Flat runtime skill.")

        with self._patched_repo(default_visible={"autofix"}):
            report = verify_runtime_budget.build_report()

        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["projection_mode"], "mixed")
        self.assertIn(
            "MIXED_RUNTIME_PROJECTION",
            {violation["code"] for violation in report["violations"]},
        )
        self.assertEqual(report["runtime_surface"]["extra_first_level_names"], ["autofix"])


if __name__ == "__main__":
    unittest.main()
