# pylint: disable=import-error,import-outside-toplevel,wrong-import-position
import json
import shutil
import subprocess
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


def _write_runtime_projection(repo_root: Path, handle: str = "he-phase-work") -> Path:
    skills_dir = repo_root / ".agents" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    source_dir = repo_root / "Plugins" / "harness-engineering" / "skills" / handle
    (skills_dir / handle).symlink_to(source_dir)
    return skills_dir


def _write_command_surface_metadata(repo_root: Path) -> Path:
    command_surface.write_command_surface_projection(repo_root_path=repo_root, dry_run=False)
    skills_dir = repo_root / ".agents" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    return skills_dir


class TestCommandSurfaceResolution(CommandSurfaceTempDirTestCase):
    def test_command_surface_rejects_retired_skill_handles(self) -> None:
        payload = command_surface.resolve_skill_handle("he-heartbeat", repo_root_path=REPO_ROOT)

        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["error_code"], "unknown_handle")
        self.assertEqual(payload["handle"], "he-heartbeat")

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
        self.assertNotIn("command_handle_path", handles[0].to_dict())

    def test_system_bridge_handles_resolve_from_canonical_sources(self) -> None:
        handles = {
            row.handle: row
            for row in command_surface.build_skill_handles(repo_root_path=REPO_ROOT)
            if row.handle in command_surface.SYSTEM_BRIDGE_SKILL_NAMES
        }

        self.assertGreaterEqual(len(handles), 1)
        for bridge_name, handle in handles.items():
            with self.subTest(bridge_name=bridge_name):
                self.assertNotIn("command_handle_path", handle.to_dict())
                self.assertTrue((handle.source_path or "").endswith("/SKILL.md"))

    def test_command_surface_projection_is_generated_from_rooted_manifests(self) -> None:
        payload = command_surface.command_surface_projection(repo_root_path=REPO_ROOT)

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["generated_from"], "rooted_manifests")
        self.assertEqual(payload["projection_path"], ".skillsets/command-surface.json")
        self.assertNotIn("generated_command_handle_count", payload)

        handles = {handle["handle"]: handle for handle in payload["handles"]}
        hidden_handles = {handle["handle"]: handle for handle in payload["hidden_handles"]}
        self.assertIn("he-phase-work", handles)
        self.assertNotIn("he-compound", handles)
        self.assertNotIn("he-phase-heartbeat", handles)
        self.assertIn("he-phase-heartbeat", hidden_handles)
        self.assertTrue(all(handle.get("command_visibility") != "none" for handle in payload["handles"]))

    def test_command_surface_marks_skill_factory_router_as_orchestrator(self) -> None:
        payload = command_surface.resolve_skill_handle("skill-factory-router", repo_root_path=REPO_ROOT)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["handle"], "skill-factory-router")
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
                owner="skill-factory",
                description="Guide skill creation.",
                invoke_via="skill-factory",
            ),
        ]

        deduped = command_surface._drop_shadowed_system_bridge_handles(handles)

        self.assertEqual(len(deduped), 1)
        self.assertEqual(deduped[0].owner, "skill-factory")


class TestCommandSurfaceNoWrapperGeneration(CommandSurfaceTempDirTestCase):
    def test_command_surface_does_not_export_wrapper_paths(self) -> None:
        payload = command_surface.command_surface_projection(repo_root_path=REPO_ROOT)

        self.assertEqual(payload["status"], "pass")
        self.assertNotIn("generated_command_handle_count", payload)
        self.assertTrue(payload["handles"])
        self.assertTrue(all("command_handle_path" not in row for row in payload["handles"]))
        self.assertTrue(all("command_handle_path" not in row for row in payload["hidden_handles"]))

    def test_wrapper_generation_apis_are_absent(self) -> None:
        self.assertFalse(hasattr(command_surface, "write_command_handles"))
        self.assertFalse(hasattr(command_surface, "check_command_handles"))
        self.assertFalse(hasattr(command_surface, "render_skill_command_handle"))
        self.assertFalse(hasattr(command_surface, "render_openai_yaml"))

    def test_command_surface_validation_rejects_duplicate_normalized_handles(self) -> None:
        handles = [
            command_surface.CommandHandle(
                handle="duplicate-handle",
                kind="skill",
                command_visibility="target",
                runtime_visibility="latent",
                source_path="Plugins/harness-engineering/skills/he-phase-heartbeat/SKILL.md",
                owner="harness-engineering",
                description="one",
                invoke_via="harness-engineering",
            ),
            command_surface.CommandHandle(
                handle="duplicate_handle",
                kind="skill",
                command_visibility="target",
                runtime_visibility="latent",
                source_path="Plugins/harness-engineering/skills/he-phase-heartbeat/SKILL.md",
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
    def _write_he_phase_work_source(self, repo_root: Path) -> None:
        """
        Create a minimal `he-phase-work` skill source under `Plugins/harness-engineering/skills` in the given repository.
        
        Writes a `SKILL.md` file containing frontmatter with `name: he-phase-work` and a heading, creating parent directories as needed.
        
        Parameters:
        	repo_root (Path): Filesystem path to the repository root where the plugin source directory will be created.
        """
        source = repo_root / "Plugins" / "harness-engineering" / "skills" / "he-phase-work"
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text(
            "---\nname: he-phase-work\n---\n# HE Phase Work\n",
            encoding="utf-8",
        )

    def _write_direct_first_party_source(self, repo_root: Path) -> None:
        source = repo_root / "Skills" / "agent-ops" / "improve-agent-native"
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text(
            "---\n"
            "name: improve-agent-native\n"
            "metadata:\n"
            "  runtime_visibility: flat\n"
            "  command_visibility: target\n"
            "---\n"
            "# Improve Agent Native\n",
            encoding="utf-8",
        )

    def _assert_runtime_card_valid(self, repo_root: Path, card_path: Path) -> None:
        """
        Validate a runtime card file using the repository's runtime-card validator.
        
        Runs the project's validate_runtime_cards.py against card_path with the
        --require-shared-workspace and --workspace-root set to repo_root, asserting
        the validator exits with code 0. On failure the assertion message includes
        the validator's combined stdout and stderr.
        
        Parameters:
            repo_root (Path): Repository root used as the workspace root for validation.
            card_path (Path): Path to the runtime card file to validate.
        """
        validation = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting" / "validate_runtime_cards.py"),
                str(card_path),
                "--require-shared-workspace",
                "--workspace-root",
                str(repo_root),
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)

    def test_skills_proof_requires_user_runtime_link(self) -> None:
        """skills_proof must fail when user runtime handles exist but are not symlinked to workspace."""
        repo_root = self.temp_dir / "repo"
        self._write_he_phase_work_source(repo_root)
        _write_command_surface_metadata(repo_root)

        home = self.temp_dir / "home"
        codex_skills = home / ".codex" / "skills"
        agents_skills = home / ".agents" / "skills"
        (codex_skills / "he-phase-work").mkdir(parents=True)
        (agents_skills / "he-phase-work").mkdir(parents=True)
        (codex_skills / "he-phase-work" / "SKILL.md").write_text("# stale\n", encoding="utf-8")
        (agents_skills / "he-phase-work" / "SKILL.md").write_text("# stale\n", encoding="utf-8")

        with mock.patch("pathlib.Path.home", return_value=home):
            result = skills_proof(repo_root, "he-phase-work")

        proof = result.data["proof"]
        self.assertEqual(proof["status"], "fail")
        self.assertTrue(proof["gates"]["resolver"])
        self.assertTrue(proof["gates"]["canonical_source_exists"])
        self.assertFalse(proof["gates"]["agents_user_runtime_ready"])
        self.assertFalse(proof["gates"]["codex_user_runtime_ready"])
        self.assertFalse(proof["gates"]["codex_user_link"])
        self.assertFalse(proof["gates"]["agents_user_link"])

    def test_skills_proof_requires_direct_picker_projection_for_direct_handles(self) -> None:
        repo_root = self.temp_dir / "repo"
        self._write_direct_first_party_source(repo_root)
        skills_dir = _write_command_surface_metadata(repo_root)

        home = self.temp_dir / "home"
        agents_skills = home / ".agents" / "skills"
        agents_skills.parent.mkdir(parents=True)
        agents_skills.symlink_to(skills_dir)

        with mock.patch("pathlib.Path.home", return_value=home):
            result = skills_proof(repo_root, "improve-agent-native")

        proof = result.data["proof"]
        self.assertEqual(result.status, "error")
        self.assertEqual(proof["status"], "fail")
        self.assertTrue(proof["gates"]["resolver"])
        self.assertTrue(proof["gates"]["canonical_source_exists"])
        self.assertFalse(proof["gates"]["direct_runtime_projection"])
        self.assertEqual(proof["runtime_failure"]["failed_check_id"], "direct_runtime_projection")
        self.assertIn("direct_runtime_projection", proof["gate_policy"]["required"])

    def test_skills_proof_passes_when_agents_runtime_is_linked(self) -> None:
        """
        Verify that an Agents user runtime root symlink satisfies reachability.
        
        When the workspace `.agents/skills` is linked into the user's home, `skills_proof`
        for the given handle reports passing gates for resolver, canonical source
        existence, and user runtime readiness; marks `agents_user_link` as true
        and `codex_user_link` as false; records `schema_version` `"command-handle-proof.v2"`;
        reports `runtime_evidence` as skipped with a reason mentioning explicit codex or agents;
        and does not create a `.harness/evidence` directory in the repository.
        """
        repo_root = self.temp_dir / "repo"
        self._write_he_phase_work_source(repo_root)
        _write_command_surface_metadata(repo_root)
        skills_dir = repo_root / ".agents" / "skills"

        home = self.temp_dir / "home"
        agents_skills = home / ".agents" / "skills"
        agents_skills.parent.mkdir(parents=True)
        agents_skills.symlink_to(skills_dir)

        with mock.patch("pathlib.Path.home", return_value=home):
            result = skills_proof(repo_root, "he-phase-work")

        proof = result.data["proof"]
        self.assertEqual(proof["status"], "pass")
        self.assertTrue(proof["gates"]["resolver"])
        self.assertTrue(proof["gates"]["canonical_source_exists"])
        self.assertFalse(proof["gates"]["codex_user_link"])
        self.assertFalse(proof["gates"]["codex_user_runtime_ready"])
        self.assertTrue(proof["gates"]["agents_user_link"])
        self.assertTrue(proof["gates"]["agents_user_runtime_ready"])
        self.assertTrue(proof["gates"]["user_runtime_ready"])
        self.assertEqual(proof["schema_version"], "command-handle-proof.v2")
        self.assertIn("user_runtime_ready", proof["gate_policy"]["required"])
        self.assertIn("either supported user runtime link", proof["gate_policy"]["required_semantics"])
        self.assertIn("agents_user_link", proof["gate_policy"]["supporting_runtime_diagnostics"])
        self.assertEqual(result.data["runtime_evidence"]["status"], "skipped")
        self.assertIn("explicit codex or agents", result.data["runtime_evidence"]["reason"])
        self.assertFalse((repo_root / ".harness" / "evidence").exists())

    def test_skills_proof_runtime_target_agents_writes_runtime_card(self) -> None:
        """Explicit Agents-targeted proof writes schema-valid evidence artifacts."""
        repo_root = self.temp_dir / "repo"
        self._write_he_phase_work_source(repo_root)
        _write_command_surface_metadata(repo_root)
        skills_dir = repo_root / ".agents" / "skills"

        home = self.temp_dir / "home"
        agents_skills = home / ".agents" / "skills"
        agents_skills.parent.mkdir(parents=True)
        agents_skills.symlink_to(skills_dir)

        with mock.patch("pathlib.Path.home", return_value=home):
            result = skills_proof(repo_root, "he-phase-work", runtime_target="agents")

        runtime_evidence = result.data["runtime_evidence"]
        card_path = repo_root / runtime_evidence["runtime_card_path"]
        receipt_path = repo_root / runtime_evidence["evidence_receipt_path"]
        artifact_path = repo_root / runtime_evidence["artifact_record_path"]
        probe_path = repo_root / runtime_evidence["probe_artifact_path"]
        self.assertEqual(result.status, "success")
        self.assertEqual(runtime_evidence["status"], "implemented_enforced")
        self.assertTrue(card_path.is_file())
        self.assertTrue(receipt_path.is_file())
        self.assertTrue(artifact_path.is_file())
        self.assertTrue(probe_path.is_file())

        card = json.loads(card_path.read_text(encoding="utf-8"))
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(card["runtime_target"], "agents")
        self.assertEqual(card["runtime_status"], "implemented_enforced")
        self.assertEqual(card["evidence_receipts"][0]["claim_status"], "pass")
        self.assertEqual(receipt["runtime_target"], "agents")
        self.assertEqual(receipt["probe_artifact_path"], runtime_evidence["probe_artifact_path"])

        self._assert_runtime_card_valid(repo_root, card_path)

    def test_skills_proof_runtime_target_codex_rejects_agents_only_runtime(self) -> None:
        """Codex-targeted proof must not pass because the agents runtime is linked."""
        repo_root = self.temp_dir / "repo"
        self._write_he_phase_work_source(repo_root)
        _write_command_surface_metadata(repo_root)
        skills_dir = repo_root / ".agents" / "skills"

        home = self.temp_dir / "home"
        agents_skills = home / ".agents" / "skills"
        agents_skills.parent.mkdir(parents=True)
        agents_skills.symlink_to(skills_dir)

        with mock.patch("pathlib.Path.home", return_value=home):
            result = skills_proof(repo_root, "he-phase-work", runtime_target="codex")

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
            ["./bin/ask skills proof he-phase-work --runtime-target codex --json --robot"],
        )
        runtime_evidence = result.data["runtime_evidence"]
        card_path = repo_root / runtime_evidence["runtime_card_path"]
        receipt_path = repo_root / runtime_evidence["evidence_receipt_path"]
        probe_path = repo_root / runtime_evidence["probe_artifact_path"]
        self.assertTrue(card_path.is_file())
        self.assertTrue(receipt_path.is_file())
        self.assertTrue(probe_path.is_file())

        card = json.loads(card_path.read_text(encoding="utf-8"))
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(card["runtime_status"], "blocked_runtime")
        self.assertEqual(card["runtime_target"], "codex")
        self.assertEqual(card["visibility_status"], "user_observable")
        self.assertEqual(
            card["artifacts"][0]["source_identity"]["source_paths"][0],
            "Plugins/harness-engineering/skills/he-phase-work/SKILL.md",
        )
        self.assertEqual(receipt["claim_status"], "blocked")
        self.assertEqual(receipt["runtime_status"], "blocked_runtime")
        self.assertEqual(receipt["blocker_class"], "blocked_runtime")
        self.assertEqual(receipt["probe_artifact_path"], runtime_evidence["probe_artifact_path"])

        self._assert_runtime_card_valid(repo_root, card_path)

    def test_skills_proof_passes_with_linked_codex_runtime(self) -> None:
        """skills_proof must pass when the Codex Desktop runtime link reaches the workspace."""
        repo_root = self.temp_dir / "repo"
        self._write_he_phase_work_source(repo_root)
        _write_command_surface_metadata(repo_root)
        skills_dir = repo_root / ".agents" / "skills"

        home = self.temp_dir / "home"
        codex_skills = home / ".codex" / "skills"
        codex_skills.parent.mkdir(parents=True)
        codex_skills.symlink_to(skills_dir)

        with mock.patch("pathlib.Path.home", return_value=home):
            result = skills_proof(repo_root, "he-phase-work")

        proof = result.data["proof"]
        self.assertEqual(proof["status"], "pass")
        self.assertTrue(proof["gates"]["resolver"])
        self.assertTrue(proof["gates"]["canonical_source_exists"])
        self.assertTrue(proof["gates"]["codex_user_link"])
        self.assertTrue(proof["gates"]["codex_user_runtime_ready"])

    def test_skills_proof_dedupes_codex_and_agents_aliases(self) -> None:
        """Codex and Agents home roots are duplicate aliases when they resolve to one projection."""
        repo_root = self.temp_dir / "repo"
        self._write_he_phase_work_source(repo_root)
        _write_command_surface_metadata(repo_root)
        skills_dir = repo_root / ".agents" / "skills"

        home = self.temp_dir / "home"
        codex_skills = home / ".codex" / "skills"
        agents_skills = home / ".agents" / "skills"
        codex_skills.parent.mkdir(parents=True)
        agents_skills.parent.mkdir(parents=True)
        codex_skills.symlink_to(skills_dir)
        agents_skills.symlink_to(skills_dir)

        with mock.patch("pathlib.Path.home", return_value=home):
            result = skills_proof(repo_root, "he-phase-work")

        proof = result.data["proof"]
        aliases = proof["runtime_diagnostics"]["runtime_aliases"]
        self.assertEqual(result.status, "success")
        self.assertTrue(proof["gates"]["user_runtime_alias_consistent"])
        self.assertEqual(aliases["status"], "deduped_aliases")
        self.assertEqual(aliases["distinct_runtime_identity_count"], 1)
        self.assertEqual(aliases["dedupe_identity"], str(skills_dir.resolve()))

    def test_skills_proof_rejects_split_brain_user_runtime_aliases(self) -> None:
        """User runtime roots must not silently point at different SDK projections."""
        repo_root = self.temp_dir / "repo"
        self._write_he_phase_work_source(repo_root)
        _write_command_surface_metadata(repo_root)
        skills_dir = repo_root / ".agents" / "skills"
        stale_runtime = self.temp_dir / "stale" / ".agents" / "skills"
        stale_runtime.mkdir(parents=True)

        home = self.temp_dir / "home"
        codex_skills = home / ".codex" / "skills"
        agents_skills = home / ".agents" / "skills"
        codex_skills.parent.mkdir(parents=True)
        agents_skills.parent.mkdir(parents=True)
        codex_skills.symlink_to(skills_dir)
        agents_skills.symlink_to(stale_runtime)

        with mock.patch("pathlib.Path.home", return_value=home):
            result = skills_proof(repo_root, "he-phase-work")

        proof = result.data["proof"]
        aliases = proof["runtime_diagnostics"]["runtime_aliases"]
        self.assertEqual(result.status, "error")
        self.assertEqual(proof["status"], "fail")
        self.assertFalse(proof["gates"]["user_runtime_alias_consistent"])
        self.assertEqual(proof["runtime_failure"]["failed_check_id"], "user_runtime_alias_consistent")
        self.assertEqual(aliases["status"], "split_brain")
        self.assertEqual(aliases["distinct_runtime_identity_count"], 2)

    def test_skills_proof_runtime_target_codex_passes_with_codex_runtime(self) -> None:
        """Codex-targeted proof must pass when the Codex runtime link reaches the workspace."""
        repo_root = self.temp_dir / "repo"
        self._write_he_phase_work_source(repo_root)
        _write_command_surface_metadata(repo_root)
        skills_dir = repo_root / ".agents" / "skills"

        home = self.temp_dir / "home"
        codex_skills = home / ".codex" / "skills"
        codex_skills.parent.mkdir(parents=True)
        codex_skills.symlink_to(skills_dir)

        with mock.patch("pathlib.Path.home", return_value=home):
            result = skills_proof(repo_root, "he-phase-work", runtime_target="codex")

        proof = result.data["proof"]
        self.assertEqual(result.status, "success")
        self.assertEqual(proof["status"], "pass")
        self.assertEqual(proof["runtime_target"], "codex")
        self.assertEqual(proof["runtime_satisfied_by"], "codex_user_runtime")
        self.assertIn("codex_user_runtime_ready", proof["gate_policy"]["required"])
        runtime_evidence = result.data["runtime_evidence"]
        card = json.loads((repo_root / runtime_evidence["runtime_card_path"]).read_text(encoding="utf-8"))
        self.assertEqual(runtime_evidence["status"], "implemented_enforced")
        self.assertEqual(card["runtime_status"], "implemented_enforced")
        self.assertEqual(card["evidence_receipts"][0]["claim_status"], "pass")

    def test_skills_proof_runtime_target_codex_downgrades_degraded_observability(self) -> None:
        """Explicit Codex proof must not stay green when attached observability is degraded."""
        repo_root = self.temp_dir / "repo"
        self._write_he_phase_work_source(repo_root)
        _write_command_surface_metadata(repo_root)
        skills_dir = repo_root / ".agents" / "skills"

        home = self.temp_dir / "home"
        codex_skills = home / ".codex" / "skills"
        codex_skills.parent.mkdir(parents=True)
        codex_skills.symlink_to(skills_dir)
        stats_path = home / ".agents" / "otel-collector" / "data" / "processed" / "stats.json"
        stats_path.parent.mkdir(parents=True)
        stats_path.write_text(
            json.dumps(
                {
                    "skill_invocation_event_count": 0,
                    "plugin_backed_skill_invocation_count": 0,
                    "telemetry_confidence": {
                        "overall_status": "degraded",
                        "live_presence_by_signal": {"logs": {"codex": True}},
                    },
                }
            )
            + "\n",
            encoding="utf-8",
        )

        with mock.patch("pathlib.Path.home", return_value=home):
            result = skills_proof(repo_root, "he-phase-work", runtime_target="codex")

        proof = result.data["proof"]
        runtime_evidence = result.data["runtime_evidence"]
        card = json.loads((repo_root / runtime_evidence["runtime_card_path"]).read_text(encoding="utf-8"))
        self.assertEqual(result.status, "error")
        self.assertEqual(proof["status"], "fail")
        self.assertEqual(runtime_evidence["status"], "partial")
        self.assertEqual(runtime_evidence["claim_status"], "partial")
        self.assertEqual(runtime_evidence["failed_check_id"], "runtime_observability_degraded")
        self.assertEqual(card["runtime_status"], "partial")
        self.assertEqual(card["evidence_receipts"][0]["claim_status"], "partial")
        self.assertIn("observability is degraded", result.data["runtime_failure"]["message"])

    def test_skills_proof_runtime_target_codex_rejects_per_handle_runtime_symlink(self) -> None:
        """Codex-targeted proof requires the user runtime root to point at the workspace."""
        repo_root = self.temp_dir / "repo"
        self._write_he_phase_work_source(repo_root)
        _write_command_surface_metadata(repo_root)
        handle_dir = repo_root / ".agents" / "skills" / "he-phase-work"

        home = self.temp_dir / "home"
        codex_skills = home / ".codex" / "skills"
        codex_skills.mkdir(parents=True)
        (codex_skills / "he-phase-work").symlink_to(handle_dir)

        with mock.patch("pathlib.Path.home", return_value=home):
            result = skills_proof(repo_root, "he-phase-work", runtime_target="codex")

        proof = result.data["proof"]
        diagnostics = proof["runtime_diagnostics"]
        self.assertEqual(result.status, "error")
        self.assertEqual(proof["status"], "fail")
        self.assertFalse(proof["gates"]["codex_user_link"])
        self.assertFalse(proof["gates"]["codex_user_runtime_ready"])
        self.assertIsNone(proof["runtime_satisfied_by"])
        self.assertEqual(diagnostics["runtime_modes"]["codex_user_runtime"], "foreign_or_unmanaged_root")


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
        self.assertIn("hidden_handles", payload)
        self.assertIsInstance(payload["hidden_handles"], list)
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

    def test_committed_command_surface_exports_no_handle_rows(self) -> None:
        """The committed command surface must not preserve old skill handle rows."""
        surface_path = REPO_ROOT / ".skillsets" / "command-surface.json"
        if not surface_path.exists():
            self.skipTest("command-surface.json not present in repo")

        payload = json.loads(surface_path.read_text(encoding="utf-8"))

        self.assertEqual(payload.get("handle_count"), 0)
        self.assertEqual(payload.get("handles"), [])
        self.assertEqual(payload.get("hidden_handles"), [])

    def test_committed_command_surface_has_no_generated_wrapper_fields(self) -> None:
        """The command surface must stay metadata-only, with no generated wrapper fields."""
        surface_path = REPO_ROOT / ".skillsets" / "command-surface.json"
        if not surface_path.exists():
            self.skipTest("command-surface.json not present in repo")

        payload = json.loads(surface_path.read_text(encoding="utf-8"))
        self.assertNotIn("generated_command_handle_count", payload)
        self.assertTrue(all("command_handle_path" not in row for row in payload["handles"]))
        self.assertTrue(all("command_handle_path" not in row for row in payload.get("hidden_handles", [])))

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
