# pylint: disable=import-error,import-outside-toplevel,wrong-import-position
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
LIFECYCLE_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"
ASK_LIB_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "lib"
_ORIGINAL_SYS_PATH = list(sys.path)
sys.path.insert(0, str(LIFECYCLE_DIR))
sys.path.insert(0, str(ASK_LIB_DIR))

import command_surface  # noqa: E402
from ask.commands.skills import skills_proof  # noqa: E402


def tearDownModule() -> None:  # noqa: N802 - unittest module hook
    sys.path[:] = _ORIGINAL_SYS_PATH
    sys.modules.pop("command_surface", None)
    sys.modules.pop("ask.commands.skills", None)


class CommandSurfaceTempDirTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="command-surface-handles-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestCommandSurfaceResolution(CommandSurfaceTempDirTestCase):
    def test_command_surface_resolves_latent_skill_handles(self) -> None:
        payload = command_surface.resolve_skill_handle("he-heartbeat", repo_root_path=REPO_ROOT)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["handle"], "he-heartbeat")
        self.assertEqual(payload["kind"], "skill")
        self.assertEqual(payload["command_visibility"], "target")
        self.assertEqual(payload["invoke_via"], "harness-engineering")
        self.assertTrue(payload["source_path"].endswith("/he-heartbeat/SKILL.md"))

    def test_command_surface_resolves_folded_he_aliases(self) -> None:
        aliases = {
            "he-phase-heartbeat": "he-phase-work",
            "he-ideate": "he-brainstorm",
            "he-refine": "he-improve",
            "he-technical-review": "he-code-review",
            "he-reliability-review": "he-code-review",
        }

        for alias, canonical in aliases.items():
            with self.subTest(alias=alias):
                payload = command_surface.resolve_skill_handle(alias, repo_root_path=REPO_ROOT)

                self.assertEqual(payload["status"], "ok")
                self.assertEqual(payload["handle"], canonical)
                self.assertEqual(payload["requested_handle"], alias)
                self.assertEqual(payload["alias_resolution"], canonical)

    def test_command_surface_builders_keep_folded_aliases_out_of_canonical_handles(self) -> None:
        canonical_handles = {row.handle for row in command_surface.build_skill_handles(repo_root_path=REPO_ROOT)}
        visible_handles = {row.handle for row in command_surface.build_command_surface_handles(repo_root_path=REPO_ROOT)}

        self.assertNotIn("he-ideate", canonical_handles)
        self.assertNotIn("he-refactor", canonical_handles)
        self.assertIn("he-ideate", visible_handles)
        self.assertIn("he-refactor", visible_handles)
        self.assertIn("he-refine", visible_handles)
        self.assertIn("he-reliability-review", visible_handles)
        self.assertIn("he-technical-review", visible_handles)
        self.assertNotIn("he-phase-heartbeat", visible_handles)

    def test_system_bridge_copy_does_not_shadow_canonical_plugin_handle(self) -> None:
        handles = [
            row
            for row in command_surface.build_skill_handles(repo_root_path=REPO_ROOT)
            if row.handle == "plugin-creator"
        ]

        self.assertEqual(len(handles), 1)
        self.assertEqual(handles[0].owner, "plugin-factory")
        self.assertEqual(
            handles[0].source_path,
            "Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/SKILL.md",
        )
        self.assertIsNone(handles[0].command_handle_path)
        self.assertFalse(command_surface.requires_generated_command_handle(handles[0]))

    def test_system_bridge_handles_do_not_require_first_level_generated_handles(self) -> None:
        handles = {
            row.handle: row
            for row in command_surface.build_skill_handles(repo_root_path=REPO_ROOT)
            if row.handle in command_surface.SYSTEM_BRIDGE_SKILL_NAMES
        }

        self.assertGreaterEqual(len(handles), 1)
        for bridge_name, handle in handles.items():
            with self.subTest(bridge_name=bridge_name):
                self.assertIsNone(handle.command_handle_path)
                self.assertFalse(command_surface.requires_generated_command_handle(handle))

    def test_command_surface_projection_is_generated_from_rooted_manifests(self) -> None:
        payload = command_surface.command_surface_projection(repo_root_path=REPO_ROOT)

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["generated_from"], "rooted_manifests")
        self.assertEqual(payload["projection_path"], ".skillsets/command-surface.json")
        self.assertIsInstance(payload["generated_command_handle_count"], int)
        self.assertGreaterEqual(payload["generated_command_handle_count"], 0)

        handles = {handle["handle"]: handle for handle in payload["handles"]}
        self.assertIn("he-phase-work", handles)
        self.assertNotIn("he-compound", handles)
        self.assertNotIn("he-phase-heartbeat", handles)

    def test_command_surface_marks_skill_builder_as_orchestrator(self) -> None:
        payload = command_surface.resolve_skill_handle("skill-builder", repo_root_path=REPO_ROOT)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["handle"], "skill-builder")
        self.assertEqual(payload["command_visibility"], "orchestrator")
        self.assertIsNone(payload.get("invoke_via"))

    def test_reviewer_resolver_keeps_reviewers_out_of_skill_namespace(self) -> None:
        manifest = self.temp_dir / "agents.json"
        manifest.write_text(
            json.dumps([{"role": "skill-inspector", "source": "test", "output": "agents/skill-inspector.toml"}]),
            encoding="utf-8",
        )

        payload = command_surface.resolve_reviewer_handle("skillinspector", manifest_path=manifest)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["kind"], "reviewer")
        self.assertEqual(payload["canonical_handle"], "skill-inspector")

    def test_command_visibility_preserves_invalid_values(self) -> None:
        """Invalid command_visibility values must be preserved for validation instead of coerced to none."""
        row = {
            "id": "test-skill",
            "command_visibility": "typoed-value",
        }
        visibility = command_surface._command_visibility_for(row)
        self.assertEqual(visibility, "typoed-value")

    def test_system_bridge_handles_do_not_shadow_plugin_canonical_handles(self) -> None:
        handles = [
            command_surface.CommandHandle(
                handle="skill-creator",
                kind="skill",
                command_visibility="target",
                runtime_visibility="latent",
                source_path="skills-system/skill-creator/SKILL.md",
                command_handle_path=".agents/skills/skill-creator/SKILL.md",
                owner="agent-ops",
                description="Create or update a skill.",
                invoke_via="agent-ops",
            ),
            command_surface.CommandHandle(
                handle="skill-creator",
                kind="skill",
                command_visibility="target",
                runtime_visibility="latent",
                source_path="Plugins/skill-factory/skills/scaffolding_templates/skill-creator/SKILL.md",
                command_handle_path=".agents/skills/skill-creator/SKILL.md",
                owner="skill-factory",
                description="Guide skill creation.",
                invoke_via="skill-factory",
            ),
        ]

        deduped = command_surface._drop_shadowed_system_bridge_handles(handles)

        self.assertEqual(len(deduped), 1)
        self.assertEqual(deduped[0].owner, "skill-factory")


class TestCommandHandleGeneration(CommandSurfaceTempDirTestCase):
    def test_command_surface_renders_generated_command_handle(self) -> None:
        payload = command_surface.resolve_skill_handle("he-heartbeat", repo_root_path=REPO_ROOT)
        handle = command_surface.CommandHandle(
            handle=payload["handle"],
            kind=payload["kind"],
            command_visibility=payload["command_visibility"],
            runtime_visibility=payload["runtime_visibility"],
            source_path=payload["source_path"],
            command_handle_path=payload["command_handle_path"],
            owner=payload["owner"],
            description=payload["description"],
            invoke_via=payload["invoke_via"],
            level=payload["level"],
            provenance=payload["provenance"],
        )

        command_handle = command_surface.render_skill_command_handle(handle)

        self.assertIn("Internal activation entrypoint", command_handle)
        self.assertIn("Load `Plugins/harness-engineering/skills/he-heartbeat/SKILL.md` if present", command_handle)
        self.assertIn(str(REPO_ROOT / "Plugins" / "harness-engineering" / "skills" / "he-heartbeat" / "SKILL.md"), command_handle)
        self.assertIn(str(REPO_ROOT / "bin" / "ask") + " skills resolve he-heartbeat --json", command_handle)
        self.assertIn("diagnostic fallback", command_handle)
        self.assertIn("Preserve source checklists/preludes verbatim", command_handle)
        self.assertIn(
            "Source: `Plugins/harness-engineering/skills/he-heartbeat/SKILL.md`.",
            command_handle,
        )
        self.assertIn(
            "Source: `Plugins/harness-engineering/skills/he-heartbeat/SKILL.md`.",
            command_handle,
        )
        self.assertIn("Keep handle/routing/source mechanics out of user replies", command_handle)
        self.assertNotIn("## Procedure", command_handle)
        self.assertEqual(command_surface._validate_command_handle_payload(handle, command_handle), [])

    def test_openai_metadata_uses_useful_picker_description(self) -> None:
        handle = command_surface.CommandHandle(
            handle="he-strategy",
            kind="skill",
            command_visibility="target",
            runtime_visibility="latent",
            source_path="Plugins/harness-engineering/skills/he-strategy/SKILL.md",
            command_handle_path=".agents/skills/he-strategy/SKILL.md",
            owner="harness-engineering",
            description="Compress repo intent, architecture review, triage, strategy, ADR, and core invariant artifacts.",
            invoke_via="harness-engineering",
        )

        metadata = command_surface.render_openai_yaml(handle)

        self.assertIn('display_name: "HE Strategy"', metadata)
        self.assertIn(
            'short_description: "Compress repo intent, architecture review, triage, strategy, ADR, and core invariant artifacts."',
            metadata,
        )
        self.assertIn('default_prompt: "$he-strategy "', metadata)
        self.assertNotIn("HE Strategy entrypoint", metadata)

    def test_openai_metadata_validation_rejects_useless_picker_description(self) -> None:
        handle = command_surface.CommandHandle(
            handle="autofix",
            kind="skill",
            command_visibility="target",
            runtime_visibility="latent",
            source_path="Skills/agent-ops/autofix/SKILL.md",
            command_handle_path=".agents/skills/autofix/SKILL.md",
            owner="agent-ops",
            description="Review and fix PR feedback.",
            invoke_via="agent-ops",
        )
        metadata = '\n'.join(
            [
                "interface:",
                '  display_name: "Autofix"',
                '  short_description: "$autofix - Autofix entrypoint"',
                '  default_prompt: "$autofix "',
            ]
        )

        violations = command_surface._validate_openai_metadata_payload(handle, metadata)

        self.assertEqual(
            violations,
            [{"code": "COMMAND_HANDLE_USELESS_PICKER_DESCRIPTION", "handle": "autofix"}],
        )

    def test_command_handle_dry_run_projects_he_heartbeat_without_writing(self) -> None:
        payload = command_surface.write_command_handles(repo_root_path=REPO_ROOT, dry_run=True)

        self.assertEqual(payload["status"], "pass")
        self.assertGreater(payload["command_handle_count"], 0)
        paths = {row["path"] for row in payload["writes"] if row["handle"] == "he-heartbeat"}
        self.assertEqual(
            paths,
            {
                ".agents/skills/he-heartbeat/SKILL.md",
                ".agents/skills/he-heartbeat/agents/openai.yaml",
            },
        )

    def test_command_handle_write_prunes_obsolete_generated_handles(self) -> None:
        stale = self.temp_dir / ".agents" / "skills" / "old-handle"
        stale.mkdir(parents=True)
        (stale / "SKILL.md").write_text(
            "# Old Handle\n\nInternal activation entrypoint for a child skill under `agent-ops`.\n",
            encoding="utf-8",
        )
        manual = self.temp_dir / ".agents" / "skills" / "manual-skill"
        manual.mkdir()
        (manual / "SKILL.md").write_text("# Manual Skill\n", encoding="utf-8")

        with mock.patch.object(command_surface, "build_skill_handles", return_value=[]):
            payload = command_surface.write_command_handles(repo_root_path=self.temp_dir, dry_run=False)

        self.assertEqual(payload["status"], "pass")
        self.assertFalse(stale.exists())
        self.assertTrue(manual.is_dir())
        self.assertEqual(
            payload["deletes"],
            [{"path": ".agents/skills/old-handle", "reason": "obsolete_generated_command_handle"}],
        )

    def test_command_handle_write_skips_rooted_symlink_lane_without_clobbering_source(self) -> None:
        source_path = "Skills/agent-ops/autofix/SKILL.md"
        source = self.temp_dir / source_path
        source.parent.mkdir(parents=True)
        original_source = "---\nname: autofix\n---\n# Autofix\n"
        source.write_text(original_source, encoding="utf-8")

        runtime_handle = self.temp_dir / ".agents" / "skills" / "autofix"
        runtime_handle.parent.mkdir(parents=True)
        runtime_handle.symlink_to(source.parent)

        handle = command_surface.CommandHandle(
            handle="autofix",
            kind="skill",
            command_visibility="target",
            runtime_visibility="latent",
            source_path=source_path,
            command_handle_path=".agents/skills/autofix/SKILL.md",
            owner="agent-ops",
            description="Autofix.",
            invoke_via="agent-ops",
        )

        with mock.patch.object(command_surface, "build_skill_handles", return_value=[handle]):
            payload = command_surface.write_command_handles(repo_root_path=self.temp_dir, dry_run=False)

        self.assertEqual(payload["status"], "pass")
        self.assertTrue(runtime_handle.is_symlink())
        self.assertEqual(payload["violations"], [])
        self.assertEqual(
            payload["skipped"],
            [
                {
                    "handle": "autofix",
                    "kind": "skill_command_handle",
                    "path": ".agents/skills/autofix/SKILL.md",
                    "reason": "rooted_runtime_symlink",
                },
                {
                    "handle": "autofix",
                    "kind": "openai_metadata",
                    "path": ".agents/skills/autofix/agents/openai.yaml",
                    "reason": "rooted_runtime_symlink",
                },
            ],
        )
        self.assertEqual(source.read_text(encoding="utf-8"), original_source)

        # Assert no generated sidecar files were written into the source tree
        source_parent_files = list(source.parent.iterdir())
        self.assertEqual(len(source_parent_files), 1, "Expected only SKILL.md in source directory")
        self.assertEqual(source_parent_files[0].name, "SKILL.md", "Only SKILL.md should exist in source directory")
        self.assertFalse((source.parent / "agents").exists(), "agents/ directory should not be created in source tree")

    def test_command_handle_check_accepts_rooted_symlink_lane(self) -> None:
        source_path = "Skills/agent-ops/autofix/SKILL.md"
        source = self.temp_dir / source_path
        source.parent.mkdir(parents=True)
        source.write_text("---\nname: autofix\n---\n# Autofix\n", encoding="utf-8")

        runtime_handle = self.temp_dir / ".agents" / "skills" / "autofix"
        runtime_handle.parent.mkdir(parents=True)
        runtime_handle.symlink_to(source.parent)

        handle = command_surface.CommandHandle(
            handle="autofix",
            kind="skill",
            command_visibility="target",
            runtime_visibility="latent",
            source_path=source_path,
            command_handle_path=".agents/skills/autofix/SKILL.md",
            owner="agent-ops",
            description="Autofix.",
            invoke_via="agent-ops",
        )

        with mock.patch.object(command_surface, "build_skill_handles", return_value=[handle]):
            payload = command_surface.check_command_handles(repo_root_path=self.temp_dir)

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["violations"], [])
        self.assertEqual(payload["checked_count"], 0)
        self.assertEqual(
            payload["skipped"],
            [
                {
                    "handle": "autofix",
                    "kind": "skill_command_handle",
                    "path": ".agents/skills/autofix/SKILL.md",
                    "reason": "rooted_runtime_symlink",
                },
                {
                    "handle": "autofix",
                    "kind": "openai_metadata",
                    "path": ".agents/skills/autofix/agents/openai.yaml",
                    "reason": "rooted_runtime_symlink",
                },
            ],
        )

    def test_command_handle_check_rejects_wrong_rooted_symlink_target(self) -> None:
        source_path = "Skills/agent-ops/autofix/SKILL.md"
        source = self.temp_dir / source_path
        source.parent.mkdir(parents=True)
        source.write_text("---\nname: autofix\n---\n# Autofix\n", encoding="utf-8")
        wrong_target = self.temp_dir / "Skills" / "agent-ops" / "wrong-skill"
        wrong_target.mkdir(parents=True)
        (wrong_target / "SKILL.md").write_text("# Wrong Skill\n", encoding="utf-8")

        runtime_handle = self.temp_dir / ".agents" / "skills" / "autofix"
        runtime_handle.parent.mkdir(parents=True)
        runtime_handle.symlink_to(wrong_target)

        handle = command_surface.CommandHandle(
            handle="autofix",
            kind="skill",
            command_visibility="target",
            runtime_visibility="latent",
            source_path=source_path,
            command_handle_path=".agents/skills/autofix/SKILL.md",
            owner="agent-ops",
            description="Autofix.",
            invoke_via="agent-ops",
        )

        with mock.patch.object(command_surface, "build_skill_handles", return_value=[handle]):
            payload = command_surface.check_command_handles(repo_root_path=self.temp_dir)

        self.assertEqual(payload["status"], "fail")
        self.assertEqual(payload["skipped"], [])
        self.assertEqual(payload["checked_count"], 2)
        codes = {violation["code"] for violation in payload["violations"]}
        self.assertIn("COMMAND_HANDLE_DRIFT", codes)
        self.assertIn("COMMAND_HANDLE_MISSING", codes)

    def test_command_handle_check_rejects_out_of_repo_symlink_target(self) -> None:
        source_path = "Skills/agent-ops/autofix/SKILL.md"
        source = self.temp_dir / source_path
        source.parent.mkdir(parents=True)
        source.write_text("---\nname: autofix\n---\n# Autofix\n", encoding="utf-8")
        outside_target = self.temp_dir.parent / f"{self.temp_dir.name}-outside-target"
        outside_target.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(outside_target, ignore_errors=True))
        (outside_target / "SKILL.md").write_text("# Outside Skill\n", encoding="utf-8")

        runtime_handle = self.temp_dir / ".agents" / "skills" / "autofix"
        runtime_handle.parent.mkdir(parents=True)
        runtime_handle.symlink_to(outside_target)

        handle = command_surface.CommandHandle(
            handle="autofix",
            kind="skill",
            command_visibility="target",
            runtime_visibility="latent",
            source_path=source_path,
            command_handle_path=".agents/skills/autofix/SKILL.md",
            owner="agent-ops",
            description="Autofix.",
            invoke_via="agent-ops",
        )

        with mock.patch.object(command_surface, "build_skill_handles", return_value=[handle]):
            payload = command_surface.check_command_handles(repo_root_path=self.temp_dir)

        self.assertEqual(payload["status"], "fail")
        self.assertEqual(payload["skipped"], [])
        self.assertEqual(payload["checked_count"], 2)
        codes = {violation["code"] for violation in payload["violations"]}
        self.assertIn("COMMAND_HANDLE_DRIFT", codes)
        self.assertIn("COMMAND_HANDLE_MISSING", codes)

    def test_command_handle_write_does_not_prune_when_validation_fails(self) -> None:
        stale = self.temp_dir / ".agents" / "skills" / "old-handle"
        stale.mkdir(parents=True)
        (stale / "SKILL.md").write_text(
            "# Old Handle\n\nInternal activation entrypoint for a child skill under `agent-ops`.\n",
            encoding="utf-8",
        )
        source_path = "Plugins/harness-engineering/skills/he-heartbeat/SKILL.md"
        source = self.temp_dir / source_path
        source.parent.mkdir(parents=True)
        source.write_text("---\nname: he-heartbeat\n---\n# HE Heartbeat\n", encoding="utf-8")
        handle = command_surface.CommandHandle(
            handle="he-heartbeat",
            kind="skill",
            command_visibility="target",
            runtime_visibility="latent",
            source_path=source_path,
            command_handle_path=".agents/skills/he-heartbeat/SKILL.md",
            owner="harness-engineering",
            description="Heartbeat.",
            invoke_via="harness-engineering",
        )

        with (
            mock.patch.object(command_surface, "build_skill_handles", return_value=[handle]),
            mock.patch.object(
                command_surface,
                "_validate_command_handle_payload",
                return_value=[{"code": "TEST_GENERATED_HANDLE_INVALID", "handle": "he-heartbeat"}],
            ),
        ):
            payload = command_surface.write_command_handles(repo_root_path=self.temp_dir, dry_run=False)

        self.assertEqual(payload["status"], "fail")
        self.assertTrue(stale.exists())
        self.assertEqual(
            payload["deletes"],
            [{"path": ".agents/skills/old-handle", "reason": "obsolete_generated_command_handle"}],
        )

    def test_command_handle_check_detects_missing_runtime_handle(self) -> None:
        payload = command_surface.check_command_handles(repo_root_path=self.temp_dir)

        self.assertEqual(payload["status"], "fail")
        codes = {violation["code"] for violation in payload["violations"]}
        self.assertIn("COMMAND_HANDLE_MISSING", codes)

    def test_command_handle_check_detects_obsolete_generated_runtime_handle(self) -> None:
        stale = self.temp_dir / ".agents" / "skills" / "old-handle"
        stale.mkdir(parents=True)
        (stale / "SKILL.md").write_text(
            "# Old Handle\n\nInternal activation entrypoint for a child skill under `agent-ops`.\n",
            encoding="utf-8",
        )

        payload = command_surface.check_command_handles(repo_root_path=self.temp_dir)

        self.assertEqual(payload["status"], "fail")
        codes = {violation["code"] for violation in payload["violations"]}
        self.assertIn("COMMAND_HANDLE_OBSOLETE", codes)
        self.assertTrue(stale.exists())

    def test_command_surface_validation_rejects_duplicate_normalized_handles(self) -> None:
        handles = [
            command_surface.CommandHandle(
                handle="he-heartbeat",
                kind="skill",
                command_visibility="target",
                runtime_visibility="latent",
                source_path="Plugins/harness-engineering/skills/he-heartbeat/SKILL.md",
                command_handle_path=".agents/skills/he-heartbeat/SKILL.md",
                owner="harness-engineering",
                description="one",
                invoke_via="harness-engineering",
            ),
            command_surface.CommandHandle(
                handle="he_heartbeat",
                kind="skill",
                command_visibility="target",
                runtime_visibility="latent",
                source_path="Plugins/harness-engineering/skills/he-heartbeat/SKILL.md",
                command_handle_path=".agents/skills/he_heartbeat/SKILL.md",
                owner="harness-engineering",
                description="two",
                invoke_via="harness-engineering",
            ),
        ]

        violations = command_surface.validate_skill_handles(handles, repo_root_path=REPO_ROOT)

        codes = {violation["code"] for violation in violations}
        self.assertIn("INVALID_HANDLE_SLUG", codes)
        self.assertIn("DUPLICATE_NORMALIZED_HANDLE", codes)


class TestCommandHandleProof(CommandSurfaceTempDirTestCase):
    def _write_he_heartbeat_source(self, repo_root: Path) -> None:
        source = repo_root / "Plugins" / "harness-engineering" / "skills" / "he-heartbeat"
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text(
            "---\nname: he-heartbeat\n---\n# HE Heartbeat\n",
            encoding="utf-8",
        )

    def test_skills_proof_requires_user_runtime_link(self) -> None:
        """skills_proof must fail when user runtime handles exist but are not symlinked to workspace."""
        repo_root = self.temp_dir / "repo"
        self._write_he_heartbeat_source(repo_root)
        command_surface.write_command_handles(repo_root_path=repo_root, dry_run=False)

        home = self.temp_dir / "home"
        codex_skills = home / ".codex" / "skills"
        agents_skills = home / ".agents" / "skills"
        (codex_skills / "he-heartbeat").mkdir(parents=True)
        (agents_skills / "he-heartbeat").mkdir(parents=True)
        (codex_skills / "he-heartbeat" / "SKILL.md").write_text("# stale\n", encoding="utf-8")
        (agents_skills / "he-heartbeat" / "SKILL.md").write_text("# stale\n", encoding="utf-8")

        with mock.patch("pathlib.Path.home", return_value=home):
            result = skills_proof(repo_root, "he-heartbeat")

        proof = result.data["proof"]
        self.assertEqual(proof["status"], "fail")
        self.assertTrue(proof["gates"]["resolver"])
        self.assertTrue(proof["gates"]["generated_command_handle_check"])
        self.assertTrue(proof["gates"]["workspace_command_handle_exists"])
        self.assertTrue(proof["gates"]["agents_user_command_handle_exists"])
        self.assertTrue(proof["gates"]["codex_user_command_handle_exists"])
        self.assertFalse(proof["gates"]["codex_user_link"])
        self.assertFalse(proof["gates"]["agents_user_link"])

    def test_skills_proof_passes_when_agents_runtime_is_linked(self) -> None:
        """Either supported user runtime link can satisfy command-handle reachability."""
        repo_root = self.temp_dir / "repo"
        self._write_he_heartbeat_source(repo_root)
        command_surface.write_command_handles(repo_root_path=repo_root, dry_run=False)
        skills_dir = repo_root / ".agents" / "skills"

        home = self.temp_dir / "home"
        agents_skills = home / ".agents" / "skills"
        agents_skills.parent.mkdir(parents=True)
        agents_skills.symlink_to(skills_dir)

        with mock.patch("pathlib.Path.home", return_value=home):
            result = skills_proof(repo_root, "he-heartbeat")

        proof = result.data["proof"]
        self.assertEqual(proof["status"], "pass")
        self.assertEqual(proof["status"], "pass")
        self.assertTrue(proof["gates"]["resolver"])
        self.assertTrue(proof["gates"]["generated_command_handle_check"])
        self.assertTrue(proof["gates"]["workspace_command_handle_exists"])
        self.assertFalse(proof["gates"]["codex_user_link"])
        self.assertFalse(proof["gates"]["codex_user_command_handle_exists"])
        self.assertTrue(proof["gates"]["agents_user_link"])
        self.assertTrue(proof["gates"]["agents_user_command_handle_exists"])
        self.assertTrue(proof["gates"]["user_runtime_ready"])
        self.assertEqual(proof["schema_version"], "command-handle-proof.v2")
        self.assertIn("user_runtime_ready", proof["gate_policy"]["required"])
        self.assertIn("either supported user runtime link", proof["gate_policy"]["required_semantics"])
        self.assertIn("agents_user_link", proof["gate_policy"]["supporting_runtime_diagnostics"])

    def test_skills_proof_runtime_target_codex_rejects_agents_only_runtime(self) -> None:
        """Codex-targeted proof must not pass because the agents runtime is linked."""
        repo_root = self.temp_dir / "repo"
        self._write_he_heartbeat_source(repo_root)
        command_surface.write_command_handles(repo_root_path=repo_root, dry_run=False)
        skills_dir = repo_root / ".agents" / "skills"

        home = self.temp_dir / "home"
        agents_skills = home / ".agents" / "skills"
        agents_skills.parent.mkdir(parents=True)
        agents_skills.symlink_to(skills_dir)

        with mock.patch("pathlib.Path.home", return_value=home):
            result = skills_proof(repo_root, "he-heartbeat", runtime_target="codex")

        proof = result.data["proof"]
        self.assertEqual(result.status, "error")
        self.assertEqual(proof["status"], "fail")
        self.assertEqual(proof["runtime_target"], "codex")
        self.assertTrue(proof["gates"]["agents_user_runtime_ready"])
        self.assertFalse(proof["gates"]["codex_user_runtime_ready"])
        self.assertEqual(proof["available_runtimes"], ["agents_user_runtime"])
        self.assertIsNone(proof["runtime_satisfied_by"])
        self.assertIn("codex_user_runtime_ready", proof["gate_policy"]["required"])
        self.assertEqual(
            proof["validation_commands"],
            ["./bin/ask skills proof he-heartbeat --runtime-target codex --json --robot"],
        )

    def test_skills_proof_passes_with_linked_codex_runtime(self) -> None:
        """skills_proof must pass when the Codex Desktop runtime link reaches the workspace."""
        repo_root = self.temp_dir / "repo"
        self._write_he_heartbeat_source(repo_root)
        command_surface.write_command_handles(repo_root_path=repo_root, dry_run=False)
        skills_dir = repo_root / ".agents" / "skills"

        home = self.temp_dir / "home"
        codex_skills = home / ".codex" / "skills"
        codex_skills.parent.mkdir(parents=True)
        codex_skills.symlink_to(skills_dir)

        with mock.patch("pathlib.Path.home", return_value=home):
            result = skills_proof(repo_root, "he-heartbeat")

        proof = result.data["proof"]
        self.assertEqual(proof["status"], "pass")
        self.assertTrue(proof["gates"]["resolver"])
        self.assertTrue(proof["gates"]["generated_command_handle_check"])
        self.assertTrue(proof["gates"]["workspace_command_handle_exists"])
        self.assertTrue(proof["gates"]["codex_user_link"])
        self.assertTrue(proof["gates"]["codex_user_command_handle_exists"])

    def test_skills_proof_runtime_target_codex_passes_with_codex_runtime(self) -> None:
        """Codex-targeted proof must pass when the Codex runtime link reaches the workspace."""
        repo_root = self.temp_dir / "repo"
        self._write_he_heartbeat_source(repo_root)
        command_surface.write_command_handles(repo_root_path=repo_root, dry_run=False)
        skills_dir = repo_root / ".agents" / "skills"

        home = self.temp_dir / "home"
        codex_skills = home / ".codex" / "skills"
        codex_skills.parent.mkdir(parents=True)
        codex_skills.symlink_to(skills_dir)

        with mock.patch("pathlib.Path.home", return_value=home):
            result = skills_proof(repo_root, "he-heartbeat", runtime_target="codex")

        proof = result.data["proof"]
        self.assertEqual(result.status, "success")
        self.assertEqual(proof["status"], "pass")
        self.assertEqual(proof["runtime_target"], "codex")
        self.assertEqual(proof["runtime_satisfied_by"], "codex_user_runtime")
        self.assertIn("codex_user_runtime_ready", proof["gate_policy"]["required"])


class TestCommittedCommandSurface(CommandSurfaceTempDirTestCase):
    def test_committed_command_surface_matches_rooted_manifests(self) -> None:
        """Committed command-surface projection must match the rooted manifests exactly."""
        surface_path = REPO_ROOT / ".skillsets" / "command-surface.json"
        if not surface_path.exists():
            self.skipTest("command-surface.json not present in repo")

        payload = command_surface.check_command_surface_projection(repo_root_path=REPO_ROOT)

        self.assertEqual(payload["status"], "pass", payload.get("violations"))
        self.assertEqual(payload["violations"], [])

    def test_command_surface_projection_check_reports_drift(self) -> None:
        """Projection check must fail when the committed command surface is stale."""
        repo_root = self.temp_dir / "repo"
        shutil.copytree(REPO_ROOT / ".skillsets", repo_root / ".skillsets")
        (repo_root / ".skillsets" / "command-surface.json").write_text("{}\n", encoding="utf-8")

        payload = command_surface.check_command_surface_projection(repo_root_path=repo_root)

        self.assertEqual(payload["status"], "fail")
        self.assertIn(
            "COMMAND_SURFACE_PROJECTION_DRIFT",
            {violation.get("code") for violation in payload["violations"]},
        )

    def test_command_surface_projection_check_ignores_source_revision_only(self) -> None:
        """Projection check should ignore per-checkout source_revision churn."""
        repo_root = self.temp_dir / "repo"
        shutil.copytree(REPO_ROOT / ".skillsets", repo_root / ".skillsets")
        surface_path = repo_root / ".skillsets" / "command-surface.json"
        payload = command_surface.command_surface_projection(repo_root_path=repo_root)

        for item in payload.get("handles", []):
            provenance = item.get("provenance") if isinstance(item, dict) else None
            if isinstance(provenance, dict) and "source_revision" in provenance:
                provenance["source_revision"] = "0000000"
        surface_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        check = command_surface.check_command_surface_projection(repo_root_path=repo_root)

        self.assertEqual(check["status"], "pass", check.get("violations"))
        self.assertEqual(check["violations"], [])

    def test_committed_command_surface_json_has_valid_structure(self) -> None:
        """The committed .skillsets/command-surface.json must be valid JSON with expected top-level keys."""
        surface_path = REPO_ROOT / ".skillsets" / "command-surface.json"
        if not surface_path.exists():
            self.skipTest("command-surface.json not present in repo")

        payload = json.loads(surface_path.read_text(encoding="utf-8"))

        self.assertIsInstance(payload, dict)
        self.assertIn("handles", payload)
        self.assertIsInstance(payload["handles"], list)
        self.assertIn("generated_from", payload)
        self.assertEqual(payload["generated_from"], "rooted_manifests")

    def test_committed_command_surface_handle_count_matches_list_length(self) -> None:
        """handle_count must equal the number of entries in the handles array."""
        surface_path = REPO_ROOT / ".skillsets" / "command-surface.json"
        if not surface_path.exists():
            self.skipTest("command-surface.json not present in repo")

        payload = json.loads(surface_path.read_text(encoding="utf-8"))

        self.assertEqual(
            payload.get("handle_count"),
            len(payload["handles"]),
            "handle_count must equal len(handles)",
        )

    def test_committed_command_surface_generated_command_handle_count_matches_required_handles(self) -> None:
        """generated_command_handle_count must count handles that need runtime command files."""
        surface_path = REPO_ROOT / ".skillsets" / "command-surface.json"
        if not surface_path.exists():
            self.skipTest("command-surface.json not present in repo")

        payload = json.loads(surface_path.read_text(encoding="utf-8"))
        required_handle_count = sum(
            1
            for handle in command_surface.build_command_surface_handles(repo_root_path=REPO_ROOT)
            if command_surface.requires_generated_command_handle(handle)
        )

        self.assertEqual(
            payload.get("generated_command_handle_count"),
            required_handle_count,
            "generated_command_handle_count must equal visible handles requiring generated command files",
        )

    def test_committed_command_surface_handles_have_required_fields(self) -> None:
        """Every handle in command-surface.json must have required fields."""
        surface_path = REPO_ROOT / ".skillsets" / "command-surface.json"
        if not surface_path.exists():
            self.skipTest("command-surface.json not present in repo")

        payload = json.loads(surface_path.read_text(encoding="utf-8"))
        required_fields = {"handle", "kind", "description", "source_path", "owner", "provenance", "runtime_visibility"}

        for entry in payload["handles"]:
            missing = required_fields - set(entry.keys())
            self.assertFalse(
                missing,
                f"Handle {entry.get('handle')!r} is missing required fields: {missing}",
            )

    def test_committed_command_surface_provenance_uses_current_policy_identity(self) -> None:
        """All handles in command-surface.json must carry the current policy identity."""
        surface_path = REPO_ROOT / ".skillsets" / "command-surface.json"
        if not surface_path.exists():
            self.skipTest("command-surface.json not present in repo")

        from selection_policy import policy_identity  # noqa: PLC0415
        current_identity = policy_identity()
        payload = json.loads(surface_path.read_text(encoding="utf-8"))

        for entry in payload["handles"]:
            prov = entry.get("provenance", {})
            self.assertEqual(
                prov.get("policy_identity"),
                current_identity,
                f"Handle {entry.get('handle')!r} has wrong policy_identity: "
                f"{prov.get('policy_identity')!r}",
            )

    def test_committed_command_surface_handles_have_no_duplicate_slugs(self) -> None:
        """No two handles in command-surface.json may share the same normalized handle name."""
        surface_path = REPO_ROOT / ".skillsets" / "command-surface.json"
        if not surface_path.exists():
            self.skipTest("command-surface.json not present in repo")

        payload = json.loads(surface_path.read_text(encoding="utf-8"))
        slugs = [entry.get("handle", "").replace("-", "_").lower() for entry in payload["handles"]]
        seen: set[str] = set()
        duplicates: list[str] = []
        for slug in slugs:
            if slug in seen:
                duplicates.append(slug)
            seen.add(slug)

        self.assertFalse(duplicates, f"Duplicate normalized handles found: {duplicates}")


if __name__ == "__main__":
    unittest.main()
