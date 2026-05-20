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

    def test_catalog_source_uses_canonical_repo_discovery_not_flat_runtime(self) -> None:
        repo_skill = self._write_skill("Skills/agent-ops/shared-skill", "Canonical repo skill.")
        self._write_skill(".agents/skills/shared-skill", "Flat runtime skill.")
        system_dir = self._write_skill(".agents/skills/.system/imagegen", "System bridge skill.")

        with self._patched_repo(default_visible={"shared-skill", "imagegen"}):
            entries = skill_discovery.discover_skill_entries(source="catalog", visibility="default")

        by_name = {entry.name: entry.source_dir for entry in entries}
        self.assertEqual(sorted(by_name), ["imagegen", "shared-skill"])
        self.assertEqual(by_name["shared-skill"], repo_skill.resolve())
        self.assertEqual(by_name["imagegen"], system_dir.resolve())

    def test_flat_runtime_system_lane_prefers_runtime_projection(self) -> None:
        runtime_system_dir = self._write_skill(".agents/skills/.system/imagegen", "Runtime system skill.")
        self._write_skill("skills-system/imagegen", "Tracked system skill.")

        with self._patched_repo(default_visible={"imagegen"}):
            entries = skill_discovery.discover_skill_entries(source="flat", visibility="default")

        selected = [entry for entry in entries if entry.name == "imagegen"]
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].source_dir, runtime_system_dir.resolve())

    def test_runtime_budget_allows_default_visible_system_skill(self) -> None:
        imagegen_dir = self._write_skill("skills-system/imagegen", "Default visible system skill.")
        hidden_bridge_dir = self._write_skill("skills-system/skill-creator", "Hidden bridge skill.")

        with (
            self._patched_repo(default_visible={"imagegen"}),
            mock.patch.object(verify_runtime_budget, "BRIDGE_SKILLS", {"imagegen", "skill-creator"}),
        ):
            report = verify_runtime_budget.build_report()

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["default_visible_skill_names"], ["imagegen"])
        self.assertEqual(report["effective_default_policy_skill_names"], ["imagegen"])
        self.assertIn(
            {
                "category": "skills-system",
                "name": "skill-creator",
                "path": hidden_bridge_dir.relative_to(self.repo_root).as_posix(),
            },
            report["hidden_system_entries"],
        )
        self.assertIn(
            {
                "category": "skills-system",
                "name": "imagegen",
                "path": imagegen_dir.relative_to(self.repo_root).as_posix(),
            },
            report["hidden_system_entries"],
        )

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

    def test_runtime_budget_baselines_curated_agents_sdk_collision(self) -> None:
        self.assertEqual(
            verify_runtime_budget._scope_collision_baseline_path(
                "Plugins/cache/openai-curated/cloudflare/rotating-version/skills/agents-sdk"
            ),
            "Plugins/cache/openai-curated/cloudflare/skills/agents-sdk",
        )
        self.assertEqual(
            verify_runtime_budget._scope_collision_baseline_path(
                "Plugins/cache/openai-curated/openai-developers/another-version/extra/skills/agents-sdk"
            ),
            "Plugins/cache/openai-curated/openai-developers/skills/agents-sdk",
        )
        self._write_skill(
            "Plugins/cache/openai-curated/cloudflare/rotating-version/skills/agents-sdk",
            "Cloudflare Agents SDK skill.",
        )
        self._write_skill(
            "Plugins/cache/openai-curated/openai-developers/another-version/skills/agents-sdk",
            "OpenAI Agents SDK skill.",
        )

        with self._patched_repo(default_visible=set()):
            report = verify_runtime_budget.build_report()

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["unresolved_scope_collisions"], [])
        self.assertEqual(len(report["baselined_scope_collisions"]), 1)
        self.assertEqual(report["baselined_scope_collisions"][0]["name"], "agents-sdk")

    def test_runtime_budget_baselines_curated_chatgpt_apps_collisions(self) -> None:
        self._write_skill(
            "Plugins/cache/openai-curated/chatgpt-apps/rotating-version/skills/build-chatgpt-app",
            "ChatGPT Apps build skill.",
        )
        self._write_skill(
            "Plugins/cache/openai-curated/openai-developers/another-version/skills/build-chatgpt-app",
            "OpenAI Developers ChatGPT Apps build skill.",
        )
        self._write_skill(
            "Plugins/cache/openai-curated/chatgpt-apps/rotating-version/skills/chatgpt-app-submission",
            "ChatGPT Apps submission skill.",
        )
        self._write_skill(
            "Plugins/cache/openai-curated/openai-developers/another-version/skills/chatgpt-app-submission",
            "OpenAI Developers ChatGPT Apps submission skill.",
        )

        with self._patched_repo(default_visible=set()):
            report = verify_runtime_budget.build_report()

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["unresolved_scope_collisions"], [])
        self.assertEqual(
            {collision["name"] for collision in report["baselined_scope_collisions"]},
            {"build-chatgpt-app", "chatgpt-app-submission"},
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

    def test_partial_rooted_runtime_reports_mixed_projection_mode(self) -> None:
        partial_root = next(iter(verify_runtime_budget.ROOT_SKILL_SETS))
        self._write_skill(f".agents/skills/{partial_root}", f"{partial_root} root skill set.")

        with self._patched_repo(default_visible=set()):
            report = verify_runtime_budget.build_report()

        self.assertEqual(report["projection_mode"], "mixed")


if __name__ == "__main__":
    unittest.main()
