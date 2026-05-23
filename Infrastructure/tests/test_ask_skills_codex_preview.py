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
    def _patched_roots(self, repo_root: Path):
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
        self.assertEqual(preview["skill_count"], 1)
        self.assertEqual(preview["skills"][0]["name"], "alpha")
        self.assertEqual(preview["skills"][0]["path"], ".agents/skills/alpha/SKILL.md")
        self.assertEqual(preview["blocked_checks"][0]["id"], "runtime_plugin_skill_roots")

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
        self.assertIn("Exceeded skills context budget", preview["rendered"]["warning_message"])

    def test_render_preview_reports_full_strategy_with_default_character_budget(self) -> None:
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
        self.assertIsNone(preview["rendered"]["warning_message"])

    def test_render_preview_shortens_descriptions_when_minimum_lines_fit(self) -> None:
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

    def test_codex_preview_runtime_adapter_is_not_owned_by_command_module(self) -> None:
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
        self.assertIn("missing action for topic 'skills config'", missing_payload["errors"][0]["message"])
        self.assertIn("invalid choice: 'nope'", unknown_payload["errors"][0]["message"])


if __name__ == "__main__":
    unittest.main()
