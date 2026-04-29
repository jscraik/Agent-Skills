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

    def test_command_surface_projection_is_generated_from_rooted_manifests(self) -> None:
        payload = command_surface.command_surface_projection(repo_root_path=REPO_ROOT)

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["generated_from"], "rooted_manifests")
        self.assertEqual(payload["projection_path"], ".skillsets/command-surface.json")
        self.assertIsInstance(payload["generated_command_handle_count"], int)
        self.assertGreaterEqual(payload["generated_command_handle_count"], 0)

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

        self.assertIn("Generated command handle", command_handle)
        self.assertIn("./bin/ask skills resolve he-heartbeat --json", command_handle)
        self.assertIn("If this is the Agent Skills Kit repo and `./bin/ask` exists", command_handle)
        self.assertIn(
            "Canonical source path: `Plugins/harness-engineering/skills/team_automation/he-heartbeat/SKILL.md`.",
            command_handle,
        )
        self.assertIn(
            "Otherwise, load `Plugins/harness-engineering/skills/team_automation/he-heartbeat/SKILL.md` directly.",
            command_handle,
        )
        self.assertNotIn("## Procedure", command_handle)
        self.assertEqual(command_surface._validate_command_handle_payload(handle, command_handle), [])

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
            "# Old Handle\n\nGenerated command handle for a child skill under the `agent-ops` router heading.\n",
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

    def test_command_handle_write_does_not_prune_when_validation_fails(self) -> None:
        stale = self.temp_dir / ".agents" / "skills" / "old-handle"
        stale.mkdir(parents=True)
        (stale / "SKILL.md").write_text(
            "# Old Handle\n\nGenerated command handle for a child skill under the `agent-ops` router heading.\n",
            encoding="utf-8",
        )
        source_path = "Plugins/harness-engineering/skills/team_automation/he-heartbeat/SKILL.md"
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
            "# Old Handle\n\nGenerated command handle for a child skill under the `agent-ops` router heading.\n",
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
                source_path="Plugins/harness-engineering/skills/team_automation/he-heartbeat/SKILL.md",
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
                source_path="Plugins/harness-engineering/skills/team_automation/he-heartbeat/SKILL.md",
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
    def test_skills_proof_requires_user_runtime_link(self) -> None:
        """skills_proof must fail when user runtime handles exist but are not symlinked to workspace."""
        repo_root = self.temp_dir / "repo"
        command_surface.write_command_handles(repo_root_path=repo_root, dry_run=False)
        skills_dir = repo_root / ".agents" / "skills"

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

    def test_skills_proof_passes_with_linked_user_runtime(self) -> None:
        """skills_proof must pass when workspace handle exists and user runtime is symlinked."""
        repo_root = self.temp_dir / "repo"
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
        self.assertTrue(proof["gates"]["resolver"])
        self.assertTrue(proof["gates"]["generated_command_handle_check"])
        self.assertTrue(proof["gates"]["workspace_command_handle_exists"])
        self.assertTrue(proof["gates"]["agents_user_link"])
        self.assertTrue(proof["gates"]["agents_user_command_handle_exists"])


class TestCommittedCommandSurface(unittest.TestCase):
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

    def test_committed_command_surface_generated_command_handle_count_matches_list_length(self) -> None:
        """generated_command_handle_count must equal the number of entries in the handles array."""
        surface_path = REPO_ROOT / ".skillsets" / "command-surface.json"
        if not surface_path.exists():
            self.skipTest("command-surface.json not present in repo")

        payload = json.loads(surface_path.read_text(encoding="utf-8"))

        self.assertEqual(
            payload.get("generated_command_handle_count"),
            len(payload["handles"]),
            "generated_command_handle_count must equal len(handles)",
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
