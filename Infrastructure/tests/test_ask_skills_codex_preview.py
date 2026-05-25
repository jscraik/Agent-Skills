import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ask.commands import skills_impl  # noqa: E402
from ask.services import codex_preview  # noqa: E402


SOURCE_IDENTITY = {
    "schema_version": "codex-runtime-source-identity.v1",
    "source_repo": "openai/codex",
    "source_files": list(codex_preview.CODEX_PREVIEW_SOURCE_FILES),
    "modeled_rule_version": codex_preview.CODEX_PREVIEW_MODELED_RULE_VERSION,
    "status": "identified",
    "revision": "test-revision",
    "relevant_source_dirty": False,
    "unavailable_reason": None,
}


def _write_skill(root: Path, rel_dir: str, name: str, description: str, script: bool = False) -> Path:
    skill_dir = root / rel_dir
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n",
        encoding="utf-8",
    )
    if script:
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "run.py").write_text("print('ok')\n", encoding="utf-8")
    return skill_md


class CodexPreviewTests(unittest.TestCase):
    def _assert_source_basis_blockers_match(self, preview: dict) -> None:
        """
        Verify that the preview's source basis blocked_check_ids match the ids present in blocked_checks.
        
        Parameters:
            preview (dict): The preview payload whose 'blocked_checks' and 'source_basis.blocked_check_ids' will be compared.
        """
        blocker_ids = {check["id"] for check in preview["blocked_checks"]}
        self.assertEqual(set(preview["source_basis"]["blocked_check_ids"]), blocker_ids)

    def _patched_roots(self, repo_root: Path):
        """
        Return a pair of mocked skill-root descriptors and associated blocked-checks for tests.
        
        Parameters:
            repo_root (Path): Repository root used to construct the mocked skill roots' paths.
        
        Returns:
            tuple: (roots, blockers) where
                - roots is a list containing a single root descriptor dict with keys:
                    `id`, `path`, `scope`, `source`, `source_file`, `identity_path`, `deduped`, `order`, `exists`.
                - blockers is a list containing blocked-check dict(s) produced for the preview, including an entry with id `runtime_plugin_skill_roots` and its related source file references.
        """
        roots = [
            {
                "id": "repo_agents_skills",
                "path": (repo_root / ".agents" / "skills").as_posix(),
                "scope": "Repo",
                "source": "repo_agents_skill_roots",
                "source_file": "codex-rs/core-skills/src/loader.rs",
                "identity_path": (repo_root / ".agents" / "skills").as_posix(),
                "deduped": False,
                "order": 0,
                "exists": True,
            }
        ]
        blockers = [
            codex_preview._codex_preview_blocked_check(
                "runtime_plugin_skill_roots",
                "Plugin roots are runtime supplied in this fixture.",
                ["codex-rs/core-skills/src/loader.rs"],
            )
        ]
        return roots, blockers

    def test_load_preview_scans_repo_agents_skill_root(self) -> None:
        """
        Verify that skills_load_preview scans the repository .agents/skills root and produces a successful codex load preview with expected metadata, blocked checks, and discovered skill entries.
        
        Asserts the result status is "success"; the preview schema version and source identity revision match the codex preview constants; source_basis fields (basis, source_revision, live_runtime_parity) are populated; the `runtime_plugin_skill_roots` blocker appears in both source_basis and blocked_checks; exactly one skill is discovered with the expected name and SKILL.md path.
        """
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _write_skill(repo_root, ".agents/skills/alpha", "alpha", "Alpha skill")
            with (
                patch.object(codex_preview, "_codex_runtime_source_identity", return_value=SOURCE_IDENTITY),
                patch.object(codex_preview, "_codex_preview_root_candidates", side_effect=lambda root: self._patched_roots(root)),
            ):
                result = skills_impl.skills_load_preview(repo_root)

        preview = result.data["codex_load_preview"]
        self.assertEqual(result.status, "success")
        self.assertEqual(preview["schema_version"], codex_preview.CODEX_PREVIEW_SCHEMA_VERSION)
        self.assertEqual(preview["source_identity"]["revision"], "test-revision")
        self.assertEqual(preview["source_basis"]["basis"], "source_modeled")
        self.assertEqual(preview["source_basis"]["source_revision"], "test-revision")
        self.assertEqual(preview["source_basis"]["live_runtime_parity"], "not_claimed")
        self.assertIn("runtime_plugin_skill_roots", preview["source_basis"]["blocked_check_ids"])
        self.assertEqual(preview["skill_count"], 1)
        self.assertEqual(preview["skills"][0]["name"], "alpha")
        self.assertEqual(preview["skills"][0]["path"], ".agents/skills/alpha/SKILL.md")
        self.assertEqual(preview["blocked_checks"][0]["id"], "runtime_plugin_skill_roots")

    def test_load_preview_scan_errors_degrade_status(self) -> None:
        errors = [{"path": "/tmp/blocked-skill-root", "message": "PermissionError: denied"}]
        with (
            patch.object(codex_preview, "_codex_runtime_source_identity", return_value=SOURCE_IDENTITY),
            patch.object(codex_preview, "_codex_preview_root_candidates", return_value=([], [])),
            patch.object(codex_preview, "_scan_preview_skills", return_value=([], errors)),
        ):
            preview = codex_preview.build_codex_load_preview(REPO_ROOT)

        self.assertEqual(preview["status"], "partial")
        self.assertEqual(preview["errors"], errors)
        self.assertIn("preview_scan_errors", [check["id"] for check in preview["blocked_checks"]])
        self.assertIn("preview_scan_errors", preview["source_basis"]["blocked_check_ids"])

    def test_load_preview_preserves_list_valued_agents_openai_metadata(self) -> None:
        """
        Verify that list-valued OpenAI metadata under a skill's agents/ directory is preserved when loading a codex preview.
        
        Asserts that list-valued `dependencies.tools` entries keep their `type` and `name` fields and that `policy.allow_implicit_invocation` is parsed as the boolean `True`.
        """
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            skill_md = _write_skill(repo_root, ".agents/skills/alpha", "alpha", "Alpha skill")
            agents_dir = skill_md.parent / "agents"
            agents_dir.mkdir()
            (agents_dir / "openai.yaml").write_text(
                """dependencies:
  tools:
    - type: mcp
      name: browser
policy:
  allow_implicit_invocation: true
""",
                encoding="utf-8",
            )
            with (
                patch.object(codex_preview, "_codex_runtime_source_identity", return_value=SOURCE_IDENTITY),
                patch.object(codex_preview, "_codex_preview_root_candidates", side_effect=lambda root: self._patched_roots(root)),
            ):
                result = skills_impl.skills_load_preview(repo_root)

        skill = result.data["codex_load_preview"]["skills"][0]
        self.assertEqual(skill["dependencies"]["tools"][0]["type"], "mcp")
        self.assertEqual(skill["dependencies"]["tools"][0]["name"], "browser")
        self.assertIs(skill["policy"]["allow_implicit_invocation"], True)

    def test_render_preview_reports_budget_omissions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            for index in range(6):
                _write_skill(
                    repo_root,
                    f".agents/skills/skill-{index}",
                    f"skill-{index}",
                    "Long description " * 20,
                )
            with (
                patch.object(codex_preview, "_codex_runtime_source_identity", return_value=SOURCE_IDENTITY),
                patch.object(codex_preview, "_codex_preview_root_candidates", side_effect=lambda root: self._patched_roots(root)),
            ):
                result = skills_impl.skills_render_preview(repo_root, context_window=50)

        preview = result.data["codex_render_preview"]
        report = preview["rendered"]["report"]
        self.assertEqual(result.status, "success")
        self.assertEqual(preview["budget"]["kind"], "tokens")
        self.assertGreater(report["omitted_count"], 0)
        self.assertEqual(report["render_strategy"], "minimum_lines_until_budget")
        self.assertEqual(preview["truncation"]["status"], "truncated")
        self.assertEqual(preview["truncation"]["omitted_count"], report["omitted_count"])
        self.assertEqual(preview["truncation"]["budget_kind"], "tokens")
        self.assertIn("Exceeded skills context budget", preview["rendered"]["warning_message"])

    def test_render_preview_reports_full_strategy_with_default_character_budget(self) -> None:
        """
        Verifies that rendering a single short skill uses the full render strategy with the default character budget.
        
        Creates a short skill fixture, patches source identity and root discovery, calls the render-preview command, and asserts:
        - overall status is "success",
        - budget kind is "characters",
        - render strategy is "full" with no omitted items,
        - truncation status is "none",
        - no rendering warning message is produced.
        """
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _write_skill(repo_root, ".agents/skills/alpha", "alpha", "Short alpha skill")
            with (
                patch.object(codex_preview, "_codex_runtime_source_identity", return_value=SOURCE_IDENTITY),
                patch.object(codex_preview, "_codex_preview_root_candidates", side_effect=lambda root: self._patched_roots(root)),
            ):
                result = skills_impl.skills_render_preview(repo_root)

        preview = result.data["codex_render_preview"]
        report = preview["rendered"]["report"]
        self.assertEqual(result.status, "success")
        self.assertEqual(preview["budget"]["kind"], "characters")
        self.assertEqual(report["render_strategy"], "full")
        self.assertEqual(report["omitted_count"], 0)
        self.assertEqual(preview["truncation"]["status"], "none")
        self.assertIsNone(preview["rendered"]["warning_message"])

    def test_codex_preview_command_family_is_publicly_discoverable(self) -> None:
        result = subprocess.run(
            [sys.executable, "Infrastructure/bin/ask", "skills", "codex-preview", "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage: ask skills codex-preview", result.stdout)

    def test_capabilities_command_is_publicly_discoverable(self) -> None:
        """
        Ensure the `ask skills capabilities` CLI command is publicly discoverable and returns a valid capability discovery payload for the `codex` runtime.
        
        Asserts that the process exits successfully and that the parsed JSON payload contains:
        - `schema_version` equal to `capability-discovery.v1`
        - `runtime_target` equal to `codex`
        - an evidence mode with `mode == "runtime_evidence"`
        - a truth boundary entry `live_runtime_parity`
        """
        result = subprocess.run(
            [sys.executable, "Infrastructure/bin/ask", "skills", "capabilities", "--runtime-target", "codex", "--json", "--robot"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        discovery = payload["data"]["capability_discovery"]
        self.assertEqual(discovery["schema_version"], "capability-discovery.v1")
        self.assertEqual(discovery["runtime_target"], "codex")
        self.assertIn("runtime_evidence", {mode["mode"] for mode in discovery["evidence_modes"]})
        self.assertIn("live_runtime_parity", discovery["truth_boundaries"])

    def test_capabilities_command_has_human_output(self) -> None:
        """
        Verify the human-readable output of the `ask skills capabilities` CLI for the `codex` runtime.
        
        Runs the CLI and asserts it exits successfully and that stdout includes a summary line with the target and status, a live runtime parity indication of `not_claimed`, and a suggested "Next:" proof-testing command containing `--runtime-target codex`.
        """
        result = subprocess.run(
            [sys.executable, "Infrastructure/bin/ask", "skills", "capabilities", "--runtime-target", "codex"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Skills capabilities: target=codex status=", result.stdout)
        self.assertIn("Live runtime parity: not_claimed", result.stdout)
        self.assertIn("Next: ./bin/ask skills proof testing --runtime-target codex --json --robot", result.stdout)

    def test_codex_preview_human_output_disclaims_validation_result(self) -> None:
        result = subprocess.run(
            [sys.executable, "Infrastructure/bin/ask", "skills", "codex-preview"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("not a runtime validation result", result.stdout)
        self.assertIn("Live runtime parity: not_claimed", result.stdout)

    def test_codex_preview_command_family_lists_public_preview_commands(self) -> None:
        with (
            patch.object(codex_preview, "_codex_runtime_source_identity", return_value=SOURCE_IDENTITY),
            patch.object(codex_preview, "_codex_preview_root_candidates", side_effect=lambda root: self._patched_roots(root)),
        ):
            result = skills_impl.skills_codex_preview(REPO_ROOT)

        preview = result.data["codex_preview"]
        command_names = [command["name"] for command in preview["commands"]]
        self.assertEqual(result.status, "success")
        self.assertEqual(preview["status"], "partial")
        self.assertIs(preview["not_a_validation_result"], True)
        self.assertEqual(preview["source_basis"]["basis"], "source_modeled")
        self.assertEqual(preview["source_basis"]["live_runtime_parity"], "not_claimed")
        self.assertIn("runtime_plugin_skill_roots", preview["source_basis"]["blocked_check_ids"])
        self.assertIn("render-preview", command_names)
        self.assertIn("load-preview", command_names)
        self.assertIn("config explain", command_names)
        self.assertEqual(preview["modeled_rule_version"], codex_preview.CODEX_PREVIEW_MODELED_RULE_VERSION)

    def test_capabilities_reports_runtime_proof_commands(self) -> None:
        with (
            patch.object(codex_preview, "_codex_runtime_source_identity", return_value=SOURCE_IDENTITY),
            patch.object(codex_preview, "_codex_preview_root_candidates", side_effect=lambda root: self._patched_roots(root)),
        ):
            result = skills_impl.skills_capabilities(REPO_ROOT, runtime_target="codex")

        discovery = result.data["capability_discovery"]
        commands = {command["name"]: command["command"] for command in discovery["supported_commands"]}
        self.assertEqual(result.status, "success")
        self.assertEqual(discovery["status"], "partial")
        self.assertEqual(discovery["truth_boundaries"]["live_runtime_parity"], "not_claimed")
        self.assertIn("skills proof", commands)
        self.assertIn("--runtime-target codex", commands["skills proof"])
        self.assertIn("runtime_plugin_skill_roots", [check["id"] for check in discovery["blocked_checks"]])

    def test_capabilities_any_routes_to_explicit_runtime_targets(self) -> None:
        with (
            patch.object(codex_preview, "_codex_runtime_source_identity", return_value=SOURCE_IDENTITY),
            patch.object(codex_preview, "_codex_preview_root_candidates", side_effect=lambda root: self._patched_roots(root)),
        ):
            result = skills_impl.skills_capabilities(REPO_ROOT, runtime_target="any")

        discovery = result.data["capability_discovery"]
        runtime_commands = [
            command
            for mode in discovery["evidence_modes"]
            if mode["mode"] == "runtime_evidence"
            for command in mode["commands"]
        ]
        self.assertEqual(discovery["status"], "discovery_only")
        self.assertNotIn("./bin/ask skills proof HANDLE --runtime-target any --json --robot", runtime_commands)
        self.assertIn("./bin/ask skills proof HANDLE --runtime-target codex --json --robot", runtime_commands)
        self.assertIn("./bin/ask skills proof HANDLE --runtime-target agents --json --robot", runtime_commands)
        self.assertTrue(all("/any/" not in artifact for artifact in discovery["required_artifacts"]))

    def test_capabilities_agents_carries_source_blockers(self) -> None:
        with (
            patch.object(codex_preview, "_codex_runtime_source_identity", return_value=SOURCE_IDENTITY),
            patch.object(codex_preview, "_codex_preview_root_candidates", side_effect=lambda root: self._patched_roots(root)),
        ):
            result = skills_impl.skills_capabilities(REPO_ROOT, runtime_target="agents")

        discovery = result.data["capability_discovery"]
        self.assertEqual(discovery["status"], "partial")
        self.assertEqual(discovery["truth_boundaries"]["live_runtime_parity"], "not_claimed")
        self.assertIn("runtime_plugin_skill_roots", [check["id"] for check in discovery["blocked_checks"]])

    def test_codex_preview_command_family_reports_source_identity_blocker(self) -> None:
        blocked_identity = {
            **SOURCE_IDENTITY,
            "status": "blocked_missing_codex_repo",
            "revision": None,
            "relevant_source_dirty": None,
            "unavailable_reason": "Codex source checkout not found.",
        }
        with (
            patch.object(codex_preview, "_codex_runtime_source_identity", return_value=blocked_identity),
            patch.object(codex_preview, "_codex_preview_root_candidates", side_effect=lambda root: self._patched_roots(root)),
        ):
            result = skills_impl.skills_codex_preview(REPO_ROOT)

        preview = result.data["codex_preview"]
        self.assertEqual(result.status, "success")
        self.assertEqual(preview["status"], "partial")
        self.assertEqual(preview["source_basis"]["source_identity_status"], "blocked_missing_codex_repo")
        self.assertIn("codex_source_identity", preview["source_basis"]["blocked_check_ids"])
        self.assertIs(preview["not_a_validation_result"], True)

    def test_render_preview_shortens_descriptions_when_minimum_lines_fit(self) -> None:
        """
        Verifies that rendering shortens skill descriptions when the minimum-lines strategy fits the provided context window.
        
        Asserts that the render completes successfully, that the chosen render strategy is "shortened_descriptions", no skills are omitted (omitted_count == 0), and that the rendered skill lines include an entry for the "alpha" skill along with its SKILL.md file reference.
        """
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _write_skill(
                repo_root,
                ".agents/skills/alpha",
                "alpha",
                "Alpha skill description with enough detail to be shortened",
            )
            _write_skill(
                repo_root,
                ".agents/skills/beta",
                "beta",
                "Beta skill description with enough detail to be shortened",
            )
            with (
                patch.object(codex_preview, "_codex_runtime_source_identity", return_value=SOURCE_IDENTITY),
                patch.object(codex_preview, "_codex_preview_root_candidates", side_effect=lambda root: self._patched_roots(root)),
            ):
                result = skills_impl.skills_render_preview(repo_root, context_window=1500)

        preview = result.data["codex_render_preview"]
        report = preview["rendered"]["report"]
        rendered_text = "\n".join(preview["rendered"]["skill_lines"])
        self.assertEqual(result.status, "success")
        self.assertEqual(report["render_strategy"], "shortened_descriptions")
        self.assertEqual(report["omitted_count"], 0)
        self.assertIn("- alpha:", rendered_text)
        self.assertIn("(file: .agents/skills/alpha/SKILL.md)", rendered_text)

    def test_config_explain_has_source_backed_rule_contract_and_blocked_live_layers(self) -> None:
        with patch.object(codex_preview, "_codex_runtime_source_identity", return_value=SOURCE_IDENTITY):
            result = skills_impl.skills_config_explain(REPO_ROOT)

        preview = result.data["codex_config_explain"]
        self.assertEqual(result.status, "success")
        self.assertEqual(preview["config_contract"]["selector_policy"], "exactly_one_of_path_or_name")
        self.assertIn("User", preview["config_contract"]["included_config_layers"])
        self.assertIn("live_skills_config_layers", [check["id"] for check in preview["blocked_checks"]])
        self._assert_source_basis_blockers_match(preview)

    def test_source_identity_blocks_when_sibling_codex_repo_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "workspace" / "agent-skills"
            repo_root.mkdir(parents=True)

            identity = codex_preview._codex_runtime_source_identity(repo_root)

        self.assertEqual(identity["status"], "blocked_missing_codex_repo")
        self.assertIn("../codex", identity["unavailable_reason"])

    def test_source_identity_reports_git_rev_parse_exception(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "workspace" / "agent-skills"
            (repo_root.parent / "codex").mkdir(parents=True)
            repo_root.mkdir()

            with patch.object(codex_preview.subprocess, "run", side_effect=OSError("boom")):
                identity = codex_preview._codex_runtime_source_identity(repo_root)

        self.assertEqual(identity["status"], "blocked_git_error")
        self.assertIn("OSError", identity["unavailable_reason"])

    def test_source_identity_reports_nonzero_git_rev_parse_stderr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "workspace" / "agent-skills"
            (repo_root.parent / "codex").mkdir(parents=True)
            repo_root.mkdir()
            failed = subprocess.CompletedProcess(
                args=["git", "rev-parse", "HEAD"],
                returncode=128,
                stdout="",
                stderr="not a git repo",
            )

            with patch.object(codex_preview.subprocess, "run", return_value=failed):
                identity = codex_preview._codex_runtime_source_identity(repo_root)

        self.assertEqual(identity["status"], "blocked_git_error")
        self.assertEqual(identity["stderr"], "not a git repo")

    def test_load_preview_propagates_source_identity_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "workspace" / "agent-skills"
            (repo_root / ".agents" / "skills").mkdir(parents=True)

            with patch.object(
                codex_preview,
                "_codex_preview_root_candidates",
                side_effect=lambda root: self._patched_roots(root),
            ):
                result = skills_impl.skills_load_preview(repo_root)

        preview = result.data["codex_load_preview"]
        self.assertEqual(result.status, "success")
        self.assertEqual(preview["source_identity"]["status"], "blocked_missing_codex_repo")
        self.assertIn("codex_source_identity", [check["id"] for check in preview["blocked_checks"]])

    def test_inject_preview_selects_unique_plain_skill_mention(self) -> None:
        """
        Verifies that injecting a plain skill mention selects the unique matching skill.
        
        Asserts that the injection result reports success, exactly one selected skill named "alpha",
        that a `structured_userinput_skill_selection` blocked check is present, and that the
        preview's `source_basis.blocked_check_ids` matches the listed `blocked_checks`.
        """
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _write_skill(repo_root, ".agents/skills/alpha", "alpha", "Alpha skill")
            with (
                patch.object(codex_preview, "_codex_runtime_source_identity", return_value=SOURCE_IDENTITY),
                patch.object(codex_preview, "_codex_preview_root_candidates", side_effect=lambda root: self._patched_roots(root)),
            ):
                result = skills_impl.skills_inject_preview(repo_root, "$alpha")

        preview = result.data["codex_inject_preview"]
        self.assertEqual(result.status, "success")
        self.assertEqual(preview["selected_count"], 1)
        self.assertEqual(preview["selected_skills"][0]["name"], "alpha")
        self.assertIn("structured_userinput_skill_selection", [check["id"] for check in preview["blocked_checks"]])
        self._assert_source_basis_blockers_match(preview)

    def test_inject_preview_blocks_ambiguous_plain_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _write_skill(repo_root, ".agents/skills/alpha-one", "alpha", "First alpha")
            _write_skill(repo_root, ".agents/skills/alpha-two", "alpha", "Second alpha")
            with (
                patch.object(codex_preview, "_codex_runtime_source_identity", return_value=SOURCE_IDENTITY),
                patch.object(codex_preview, "_codex_preview_root_candidates", side_effect=lambda root: self._patched_roots(root)),
            ):
                result = skills_impl.skills_inject_preview(repo_root, "$alpha")

        preview = result.data["codex_inject_preview"]
        self.assertEqual(result.status, "success")
        self.assertEqual(preview["selected_count"], 0)
        self.assertEqual(preview["selection_notes"][0]["status"], "blocked_ambiguous_name")

    def test_inject_preview_directory_skill_link_disambiguates_duplicate_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _write_skill(repo_root, ".agents/skills/alpha-one", "alpha", "First alpha")
            _write_skill(repo_root, ".agents/skills/alpha-two", "alpha", "Second alpha")
            with (
                patch.object(codex_preview, "_codex_runtime_source_identity", return_value=SOURCE_IDENTITY),
                patch.object(codex_preview, "_codex_preview_root_candidates", side_effect=lambda root: self._patched_roots(root)),
            ):
                result = skills_impl.skills_inject_preview(repo_root, "[$alpha](skill://.agents/skills/alpha-two)")

        preview = result.data["codex_inject_preview"]
        self.assertEqual(result.status, "success")
        self.assertEqual(preview["selected_count"], 1)
        self.assertEqual(preview["selected_skills"][0]["path"], ".agents/skills/alpha-two/SKILL.md")
        self.assertEqual(preview["selection_notes"][0]["status"], "blocked_ambiguous_name")

    def test_implicit_preview_detects_skill_script_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _write_skill(repo_root, ".agents/skills/alpha", "alpha", "Alpha skill", script=True)
            with (
                patch.object(codex_preview, "_codex_runtime_source_identity", return_value=SOURCE_IDENTITY),
                patch.object(codex_preview, "_codex_preview_root_candidates", side_effect=lambda root: self._patched_roots(root)),
            ):
                result = skills_impl.skills_implicit_preview(
                    repo_root,
                    command="python3 .agents/skills/alpha/scripts/run.py",
                )

        preview = result.data["codex_implicit_preview"]
        self.assertEqual(result.status, "success")
        self.assertEqual(preview["attribution_status"], "matched")
        self.assertEqual(preview["selected_skill"]["name"], "alpha")

    def test_implicit_preview_detects_reader_command_for_skill_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _write_skill(repo_root, ".agents/skills/alpha", "alpha", "Alpha skill")
            with (
                patch.object(codex_preview, "_codex_runtime_source_identity", return_value=SOURCE_IDENTITY),
                patch.object(codex_preview, "_codex_preview_root_candidates", side_effect=lambda root: self._patched_roots(root)),
            ):
                result = skills_impl.skills_implicit_preview(
                    repo_root,
                    command="cat .agents/skills/alpha/SKILL.md",
                )

        preview = result.data["codex_implicit_preview"]
        self.assertEqual(result.status, "success")
        self.assertEqual(preview["attribution_status"], "matched")
        self.assertEqual(preview["selected_skill"]["name"], "alpha")

    def test_implicit_preview_resolves_relative_workdir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _write_skill(repo_root, ".agents/skills/alpha", "alpha", "Alpha skill")
            nested = repo_root / "subdir"
            nested.mkdir()
            with (
                patch.object(codex_preview, "_codex_runtime_source_identity", return_value=SOURCE_IDENTITY),
                patch.object(codex_preview, "_codex_preview_root_candidates", side_effect=lambda root: self._patched_roots(root)),
            ):
                result = skills_impl.skills_implicit_preview(
                    repo_root,
                    command="cat ../.agents/skills/alpha/SKILL.md",
                    workdir="subdir",
                )

        preview = result.data["codex_implicit_preview"]
        self.assertEqual(result.status, "success")
        self.assertEqual(preview["attribution_status"], "matched")
        self.assertEqual(preview["selected_skill"]["name"], "alpha")
        self.assertEqual(preview["workdir"], nested.as_posix())

    def test_implicit_preview_does_not_attribute_regular_ask_package_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _write_skill(repo_root, ".agents/skills/alpha", "alpha", "Alpha skill", script=True)
            with (
                patch.object(codex_preview, "_codex_runtime_source_identity", return_value=SOURCE_IDENTITY),
                patch.object(codex_preview, "_codex_preview_root_candidates", side_effect=lambda root: self._patched_roots(root)),
            ):
                result = skills_impl.skills_implicit_preview(
                    repo_root,
                    command="./bin/ask skills package alpha --json --robot",
                )

        preview = result.data["codex_implicit_preview"]
        self.assertEqual(result.status, "success")
        self.assertEqual(preview["attribution_status"], "none")
        self.assertIsNone(preview["selected_skill"])

    def test_implicit_preview_reports_shell_parse_error_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _write_skill(repo_root, ".agents/skills/alpha", "alpha", "Alpha skill", script=True)
            with (
                patch.object(codex_preview, "_codex_runtime_source_identity", return_value=SOURCE_IDENTITY),
                patch.object(codex_preview, "_codex_preview_root_candidates", side_effect=lambda root: self._patched_roots(root)),
            ):
                result = skills_impl.skills_implicit_preview(
                    repo_root,
                    command="'",
                )

        preview = result.data["codex_implicit_preview"]
        self.assertEqual(result.status, "success")
        self.assertEqual(preview["status"], "partial")
        self.assertEqual(preview["attribution_status"], "none")
        self.assertIsNone(preview["selected_skill"])
        self.assertIn("shell_command_parse_error", [check["id"] for check in preview["blocked_checks"]])
        self.assertIn("shell_parser_exact_parity", [check["id"] for check in preview["blocked_checks"]])
        self._assert_source_basis_blockers_match(preview)

    def test_codex_preview_runtime_adapter_is_not_owned_by_command_module(self) -> None:
        """
        Ensure the Codex runtime adapter implementation resides in the service module and not in the command module.
        
        Asserts that the command module exposes the public builder names but does not define internal adapter helper functions, and that the service module defines the builder functions and does not import ask.commands.
        """
        command_source = (REPO_ROOT / "Infrastructure/scripts/lib/ask/commands/skills_impl.py").read_text(encoding="utf-8")
        service_source = (REPO_ROOT / "Infrastructure/scripts/lib/ask/services/codex_preview.py").read_text(encoding="utf-8")

        self.assertIn("build_codex_load_preview", command_source)
        self.assertIn("build_codex_render_preview", command_source)
        self.assertNotIn("def _codex_preview_load_model", command_source)
        self.assertNotIn("def _render_preview_lines", command_source)
        self.assertNotIn("def _preview_implicit_match", command_source)
        self.assertIn("def build_codex_load_preview", service_source)
        self.assertIn("def build_codex_render_preview", service_source)
        self.assertNotIn("from ask.commands", service_source)

    def test_cli_skills_config_missing_and_unknown_actions_report_validation_errors(self) -> None:
        """
        Verifies the CLI reports validation errors when `ask skills config` is invoked with a missing action and with an unknown action.
        
        Runs the command without an action and with the invalid action `nope`, then asserts both processes exit with code 2, both JSON payloads have `"status": "error"`, and the error messages mention `config_action` for the missing action and `invalid choice: 'nope'` for the unknown action.
        """
        missing = subprocess.run(
            [sys.executable, "Infrastructure/bin/ask", "skills", "config", "--json", "--robot"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        unknown = subprocess.run(
            [sys.executable, "Infrastructure/bin/ask", "skills", "config", "nope", "--json", "--robot"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        missing_payload = json.loads(missing.stdout)
        unknown_payload = json.loads(unknown.stdout)
        self.assertEqual(missing.returncode, 2)
        self.assertEqual(unknown.returncode, 2)
        self.assertEqual(missing_payload["status"], "error")
        self.assertEqual(unknown_payload["status"], "error")
        self.assertIn("config_action", missing_payload["errors"][0]["message"])
        self.assertIn("invalid choice: 'nope'", unknown_payload["errors"][0]["message"])


if __name__ == "__main__":
    unittest.main()
