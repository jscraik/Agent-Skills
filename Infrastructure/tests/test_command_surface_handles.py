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
import diagnose_skill as diagnose_skill_module  # noqa: E402
from ask.commands.skills import skills_handles, skills_proof  # noqa: E402


def tearDownModule() -> None:  # noqa: N802 - unittest module hook
    sys.path[:] = _ORIGINAL_SYS_PATH
    sys.modules.pop("command_surface", None)
    sys.modules.pop("diagnose_skill", None)
    sys.modules.pop("ask.commands.skills", None)


class SdkSkillRegistryTempDirTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sdk-skill-registry-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)


def _write_skill_source(
    repo_root: Path,
    handle: str,
    *,
    root: str = "Skills/agent-ops",
    heading: str | None = None,
) -> Path:
    source = repo_root / root / handle
    source.mkdir(parents=True, exist_ok=True)
    source.joinpath("SKILL.md").write_text(
        "---\n"
        f"name: {handle}\n"
        "description: Test skill.\n"
        "---\n"
        f"# {heading or handle}\n",
        encoding="utf-8",
    )
    return source


def _link_flat_projection(repo_root: Path, handle: str, source_dir: Path) -> Path:
    skills_dir = repo_root / ".agents" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    target = skills_dir / handle
    target.symlink_to(source_dir)
    return skills_dir


class TestSdkSkillResolution(SdkSkillRegistryTempDirTestCase):
    def test_resolution_rejects_retired_skill_handles(self) -> None:
        payload = command_surface.resolve_skill_handle("he-heartbeat", repo_root_path=REPO_ROOT)

        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["error_code"], "unknown_handle")
        self.assertEqual(payload["handle"], "he-heartbeat")

    def test_resolution_prefers_sdk_flat_registry(self) -> None:
        repo_root = self.temp_dir / "repo"
        source = _write_skill_source(repo_root, "agents-md")
        _link_flat_projection(repo_root, "agents-md", source)

        payload = command_surface.resolve_skill_handle("agents-md", repo_root_path=repo_root)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["handle"], "agents-md")
        self.assertEqual(payload["handle_source"], "sdk_flat_registry")
        self.assertEqual(payload["runtime_visibility"], "flat")
        self.assertEqual(payload["provenance"]["projection_mode"], "flat")
        self.assertEqual(payload["runtime_projection_path"], ".agents/skills/agents-md/SKILL.md")
        self.assertNotIn("command_visibility", payload)
        self.assertNotIn("invoke_via", payload)
        self.assertNotIn("command_handle", json.dumps(payload))

    def test_sdk_resolution_preserves_docs_expert_legacy_handle(self) -> None:
        repo_root = self.temp_dir / "repo"
        source = _write_skill_source(repo_root, "technical-writer")
        _link_flat_projection(repo_root, "technical-writer", source)

        payload = command_surface.resolve_skill_handle("docs-expert", repo_root_path=repo_root)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["handle"], "technical-writer")
        self.assertEqual(payload["requested_handle"], "docs-expert")
        self.assertEqual(payload["alias_resolution"], "technical-writer")
        self.assertEqual(payload["source_path"], "Skills/agent-ops/technical-writer/SKILL.md")

    def test_sdk_resolution_keeps_hidden_runtime_skills_private(self) -> None:
        repo_root = self.temp_dir / "repo"
        skill_dir = _write_skill_source(repo_root, "he-phase-heartbeat", root="Plugins/harness-engineering/skills")
        skill_dir.joinpath("SKILL.md").write_text(
            "---\n"
            "name: he-phase-heartbeat\n"
            "description: Hidden runtime lane.\n"
            "runtime_visibility: hidden\n"
            "---\n"
            "# he-phase-heartbeat\n",
            encoding="utf-8",
        )
        _link_flat_projection(repo_root, "he-phase-heartbeat", skill_dir)

        payload = command_surface.resolve_skill_handle("he-phase-heartbeat", repo_root_path=repo_root)

        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["error_code"], "unknown_handle")

    def test_sdk_discovery_honors_repo_root_path(self) -> None:
        repo_root = self.temp_dir / "repo"
        source = _write_skill_source(repo_root, "foo")
        _link_flat_projection(repo_root, "foo", source)

        payload = command_surface.resolve_skill_handle("foo", repo_root_path=repo_root)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["handle"], "foo")
        self.assertEqual(payload["source_path"], "Skills/agent-ops/foo/SKILL.md")
        self.assertEqual(payload["runtime_projection_path"], ".agents/skills/foo/SKILL.md")

    def test_sdk_handle_validation_detects_distinct_duplicate_sources(self) -> None:
        repo_root = self.temp_dir / "repo"
        first = _write_skill_source(repo_root, "duplicate-skill", root="Skills/agent-ops")
        _write_skill_source(repo_root, "duplicate-skill", root="Plugins/example/skills")
        _link_flat_projection(repo_root, "duplicate-skill", first)

        report = command_surface.handles_report(repo_root_path=repo_root)
        result = skills_handles(repo_root, check=True)

        self.assertEqual(report["status"], "fail")
        self.assertIn(
            "DUPLICATE_SDK_SKILL_HANDLE",
            {violation["code"] for violation in report["violations"]},
        )
        self.assertEqual(result.status, "error")
        self.assertIn(
            "DUPLICATE_SDK_SKILL_HANDLE",
            {violation["code"] for violation in result.data["violations"]},
        )

    def test_keep_qualified_plugin_collisions_use_sdk_flat_names(self) -> None:
        repo_root = self.temp_dir / "repo"
        _write_skill_source(
            repo_root,
            "agents-sdk",
            root="Plugins/cache/openai-curated/cloudflare/3e1ccdb3/skills",
        )
        _write_skill_source(
            repo_root,
            "agents-sdk",
            root="Plugins/cache/openai-curated/openai-developers/3e1ccdb3/skills",
        )
        _write_skill_source(
            repo_root,
            "agents-sdk",
            root="Plugins/cache/openai-curated-remote/openai-developers/1.2.2/skills",
        )

        report = command_surface.handles_report(repo_root_path=repo_root)
        handles = {entry["handle"] for entry in report["handles"]}
        cloudflare = command_surface.resolve_skill_handle("cloudflare:agents-sdk", repo_root_path=repo_root)
        openai = command_surface.resolve_skill_handle("openai-developers:agents-sdk", repo_root_path=repo_root)
        raw = command_surface.resolve_skill_handle("agents-sdk", repo_root_path=repo_root)

        self.assertEqual(report["status"], "pass")
        self.assertIn("cloudflare:agents-sdk", handles)
        self.assertIn("openai-developers:agents-sdk", handles)
        self.assertNotIn("agents-sdk", handles)
        self.assertEqual(cloudflare["status"], "ok")
        self.assertEqual(openai["status"], "ok")
        self.assertEqual(raw["status"], "error")
        self.assertEqual(raw["error_code"], "unknown_handle")

    def test_suppress_duplicate_plugin_collision_prefers_canonical_cache_record(self) -> None:
        repo_root = self.temp_dir / "repo"
        _write_skill_source(
            repo_root,
            "github",
            root="Plugins/cache/openai-curated/github/3e1ccdb3/skills",
        )
        _write_skill_source(
            repo_root,
            "github",
            root="Plugins/cache/openai-curated-remote/github/0.1.2/skills",
        )

        report = command_surface.handles_report(repo_root_path=repo_root)
        payload = command_surface.resolve_skill_handle("github", repo_root_path=repo_root)

        self.assertEqual(report["status"], "pass")
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(
            payload["source_path"],
            "Plugins/cache/openai-curated/github/3e1ccdb3/skills/github/SKILL.md",
        )
        self.assertNotIn("openai-curated-remote", payload["source_path"])

    def test_primary_runtime_cloudflare_cache_collisions_are_policy_managed(self) -> None:
        repo_root = self.temp_dir / "repo"
        duplicate_handles = (
            "cloudflare",
            "durable-objects",
            "sandbox-sdk",
            "web-perf",
            "workers-best-practices",
            "wrangler",
        )
        for handle in duplicate_handles:
            source = _write_skill_source(repo_root, handle, root=".agents/skills")
            _write_skill_source(
                repo_root,
                handle,
                root="Plugins/cache/openai-curated/cloudflare/6fe38d4f/skills",
            )
            _write_skill_source(
                repo_root,
                handle,
                root="Plugins/cache/openai-curated-remote/cloudflare/0.1.2/skills",
            )
            self.assertEqual(source, repo_root / ".agents" / "skills" / handle)

        report = command_surface.handles_report(repo_root_path=repo_root)
        result = skills_handles(repo_root, check=True)

        self.assertEqual(report["status"], "pass")
        self.assertEqual(result.status, "success")
        handles = {entry["handle"]: entry for entry in report["handles"]}
        for handle in duplicate_handles:
            self.assertEqual(handles[handle]["source_path"], f".agents/skills/{handle}/SKILL.md")

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

    def test_removed_command_surface_symbols_are_absent(self) -> None:
        for symbol in (
            "CommandHandle",
            "build_skill_handles",
            "build_command_surface_handles",
            "command_surface_projection",
            "write_command_surface_projection",
            "check_command_surface_projection",
            "parse_command_handles",
        ):
            with self.subTest(symbol=symbol):
                self.assertFalse(hasattr(command_surface, symbol))

    def test_aggregate_diagnostics_do_not_require_generated_workspace_projection(self) -> None:
        repo_root = self.temp_dir / "repo"
        source = _write_skill_source(repo_root, "foo")
        _link_flat_projection(repo_root, "foo", source)

        with (
            mock.patch.object(diagnose_skill_module, "REPO_ROOT", repo_root),
            mock.patch.object(diagnose_skill_module, "SKILLS_DIR", repo_root / ".agents-missing" / "skills"),
            mock.patch.object(diagnose_skill_module, "SKILL_INDEX", repo_root / "SKILL.md"),
            mock.patch.object(
                diagnose_skill_module,
                "CODEX_SKILLS",
                self.temp_dir / "home" / ".codex" / "skills",
            ),
            mock.patch.object(
                diagnose_skill_module,
                "AGENTS_SKILLS",
                self.temp_dir / "home" / ".agents" / "skills",
            ),
        ):
            targeted = diagnose_skill_module.diagnose_skill("foo")
            aggregate = diagnose_skill_module.diagnose_skill("foo", require_workspace_projection=False)

        targeted_projection = next(result for result in targeted if result.check == "workspace projection")
        aggregate_projection = next(result for result in aggregate if result.check == "workspace projection")

        self.assertEqual(targeted_projection.status, "fail")
        self.assertEqual(aggregate_projection.status, "warn")
        self.assertIn("skills sync --scope workspace", aggregate_projection.details)


class TestSdkSkillProof(SdkSkillRegistryTempDirTestCase):
    def _assert_runtime_card_valid(self, repo_root: Path, card_path: Path) -> None:
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
        repo_root = self.temp_dir / "repo"
        source = _write_skill_source(repo_root, "he-phase-work", root="Plugins/harness-engineering/skills")
        _link_flat_projection(repo_root, "he-phase-work", source)

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
        recovery_commands = proof["runtime_diagnostics"]["recovery_commands"]
        self.assertEqual(
            recovery_commands[0]["command"],
            "./bin/ask skills sync --scope user --projection flat --dry-run --json --robot",
        )
        self.assertEqual(
            recovery_commands[1]["command"],
            "./bin/ask skills sync --scope workspace --projection flat --json --robot",
        )
        self.assertEqual(
            recovery_commands[2]["command"],
            "./bin/ask skills sync --scope user --projection flat --json --robot",
        )

    def test_skills_proof_passes_when_agents_runtime_is_linked(self) -> None:
        repo_root = self.temp_dir / "repo"
        source = _write_skill_source(repo_root, "he-phase-work", root="Plugins/harness-engineering/skills")
        skills_dir = _link_flat_projection(repo_root, "he-phase-work", source)

        home = self.temp_dir / "home"
        agents_skills = home / ".agents" / "skills"
        agents_skills.parent.mkdir(parents=True)
        agents_skills.symlink_to(skills_dir)

        with mock.patch("pathlib.Path.home", return_value=home):
            result = skills_proof(repo_root, "he-phase-work")

        proof = result.data["proof"]
        self.assertEqual(result.status, "success")
        self.assertEqual(proof["status"], "pass")
        self.assertEqual(proof["schema_version"], "sdk-skill-proof.v1")
        self.assertTrue(proof["gates"]["agents_user_link"])
        self.assertTrue(proof["gates"]["agents_user_runtime_ready"])
        self.assertTrue(proof["gates"]["user_runtime_ready"])
        self.assertEqual(result.data["runtime_evidence"]["status"], "skipped")
        self.assertFalse((repo_root / ".harness" / "evidence").exists())

    def test_skills_proof_uses_projection_path_for_qualified_handles(self) -> None:
        repo_root = self.temp_dir / "repo"
        source = _write_skill_source(
            repo_root,
            "agents-sdk",
            root="Plugins/cache/openai-curated/cloudflare/3e1ccdb3/skills",
        )
        skills_dir = _link_flat_projection(repo_root, "agents-sdk", source)

        home = self.temp_dir / "home"
        agents_skills = home / ".agents" / "skills"
        agents_skills.parent.mkdir(parents=True)
        agents_skills.symlink_to(skills_dir)

        with mock.patch("pathlib.Path.home", return_value=home):
            result = skills_proof(repo_root, "cloudflare:agents-sdk", runtime_target="agents")

        proof = result.data["proof"]
        direct_projection = proof["runtime_diagnostics"]["direct_runtime_projection"]
        self.assertEqual(result.status, "success")
        self.assertEqual(proof["status"], "pass")
        self.assertTrue(proof["gates"]["direct_runtime_projection"])
        self.assertTrue(direct_projection["path"].endswith(".agents/skills/agents-sdk/SKILL.md"))
        self.assertNotIn("cloudflare:agents-sdk", direct_projection["path"])

    def test_skills_proof_runtime_target_agents_writes_runtime_card(self) -> None:
        repo_root = self.temp_dir / "repo"
        source = _write_skill_source(repo_root, "he-phase-work", root="Plugins/harness-engineering/skills")
        skills_dir = _link_flat_projection(repo_root, "he-phase-work", source)

        home = self.temp_dir / "home"
        agents_skills = home / ".agents" / "skills"
        agents_skills.parent.mkdir(parents=True)
        agents_skills.symlink_to(skills_dir)

        with mock.patch("pathlib.Path.home", return_value=home):
            result = skills_proof(repo_root, "he-phase-work", runtime_target="agents")

        runtime_evidence = result.data["runtime_evidence"]
        card_path = repo_root / runtime_evidence["runtime_card_path"]
        receipt_path = repo_root / runtime_evidence["evidence_receipt_path"]
        probe_path = repo_root / runtime_evidence["probe_artifact_path"]
        self.assertEqual(result.status, "success")
        self.assertEqual(runtime_evidence["status"], "implemented_enforced")
        self.assertTrue(card_path.is_file())
        self.assertTrue(receipt_path.is_file())
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
        repo_root = self.temp_dir / "repo"
        source = _write_skill_source(repo_root, "he-phase-work", root="Plugins/harness-engineering/skills")
        skills_dir = _link_flat_projection(repo_root, "he-phase-work", source)

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
        runtime_evidence = result.data["runtime_evidence"]
        card_path = repo_root / runtime_evidence["runtime_card_path"]
        receipt_path = repo_root / runtime_evidence["evidence_receipt_path"]
        self.assertTrue(card_path.is_file())
        self.assertTrue(receipt_path.is_file())

        card = json.loads(card_path.read_text(encoding="utf-8"))
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(card["runtime_status"], "blocked_runtime")
        self.assertEqual(card["runtime_target"], "codex")
        self.assertEqual(receipt["claim_status"], "blocked")
        self.assertEqual(receipt["runtime_status"], "blocked_runtime")
        self._assert_runtime_card_valid(repo_root, card_path)

    def test_skills_proof_rejects_split_brain_user_runtime_aliases(self) -> None:
        repo_root = self.temp_dir / "repo"
        source = _write_skill_source(repo_root, "he-phase-work", root="Plugins/harness-engineering/skills")
        skills_dir = _link_flat_projection(repo_root, "he-phase-work", source)
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


if __name__ == "__main__":
    unittest.main()
