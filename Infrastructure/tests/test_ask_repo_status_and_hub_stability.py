"""
Unit tests for new functions in ask.commands.repo added in this PR:
  - repo_status
  - check_hub_stability
  - provider_audit
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"))

from ask.commands.repo import repo_status, repo_yaml_inspect, check_hub_stability, provider_audit
from ask.commands.repo_impl import _managed_pyyaml_python_command


# ---------------------------------------------------------------------------
# repo_status
# ---------------------------------------------------------------------------

class TestRepoStatus(unittest.TestCase):
    def test_repo_status_returns_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            result = repo_status(repo)
        self.assertEqual(result.status, "success")

    def test_repo_status_reports_repo_root_as_dot(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            result = repo_status(repo)
        self.assertEqual(result.data["repo_root"], ".")

    def test_repo_status_resolved_path_is_absolute(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            result = repo_status(repo)
        self.assertTrue(Path(result.data["repo_root_resolved"]).is_absolute())

    def test_repo_status_is_git_true_when_git_dir_exists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            (repo / ".git").mkdir()
            result = repo_status(repo)
        self.assertTrue(result.data["is_git"])

    def test_repo_status_is_git_false_when_no_git_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            result = repo_status(repo)
        self.assertFalse(result.data["is_git"])

    def test_repo_status_skills_synced_false_when_no_agents_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            result = repo_status(repo)
        self.assertFalse(result.data["skills_synced"])

    def test_repo_status_skills_synced_false_when_skills_dir_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            skills_dir = repo / ".agents" / "skills"
            skills_dir.mkdir(parents=True)
            result = repo_status(repo)
        self.assertFalse(result.data["skills_synced"])

    def test_repo_status_skills_synced_true_when_skills_dir_has_entry(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            skills_dir = repo / ".agents" / "skills"
            skills_dir.mkdir(parents=True)
            (skills_dir / "my-skill").mkdir()
            result = repo_status(repo)
        self.assertTrue(result.data["skills_synced"])

    def test_repo_status_skills_synced_true_with_file_in_skills_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            skills_dir = repo / ".agents" / "skills"
            skills_dir.mkdir(parents=True)
            (skills_dir / "SKILL.md").write_text("# skill", encoding="utf-8")
            result = repo_status(repo)
        self.assertTrue(result.data["skills_synced"])

    def test_repo_status_resolved_path_matches_actual_tmpdir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            result = repo_status(repo)
        # resolve() canonicalizes the path
        self.assertEqual(result.data["repo_root_resolved"], str(repo.resolve()))

    def test_repo_status_data_keys_present(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            result = repo_status(repo)
        for key in ("repo_root", "repo_root_resolved", "is_git", "skills_synced"):
            with self.subTest(key=key):
                self.assertIn(key, result.data)


class TestRepoYamlInspect(unittest.TestCase):
    def test_managed_pyyaml_python_command_prefers_local_python_bin(self):
        calls = []

        def fake_run(cmd, **_kwargs):
            calls.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, "", "")

        with patch.dict("os.environ", {"PYTHON_BIN": "/tmp/local-python"}, clear=False):
            with patch("ask.commands.repo_impl.subprocess.run", side_effect=fake_run):
                command = _managed_pyyaml_python_command()

        self.assertEqual(command, ["/tmp/local-python"])
        self.assertEqual(calls[0], ["/tmp/local-python", "-c", "import yaml"])

    def test_repo_yaml_inspect_reads_yaml_with_managed_pyyaml(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            (repo / "sample.yaml").write_text("cases:\n  - id: alpha\n", encoding="utf-8")

            result = repo_yaml_inspect(repo, "sample.yaml", query="cases.0.id")

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["yaml"]["query_value"], "alpha")
        self.assertIn("repo yaml-inspect sample.yaml", result.data["validation_commands"][0])

    def test_repo_yaml_inspect_converts_yaml_objects_to_jsonable_values(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            (repo / "sample.yaml").write_text(
                "created: 2024-01-15\nmy_set: !!set\n  alpha: null\n",
                encoding="utf-8",
            )

            timestamp = repo_yaml_inspect(repo, "sample.yaml", query="created")
            yaml_set = repo_yaml_inspect(repo, "sample.yaml", query="my_set")

        self.assertEqual(timestamp.status, "success")
        self.assertEqual(timestamp.data["yaml"]["query_value"], "2024-01-15")
        self.assertEqual(yaml_set.status, "success")
        self.assertIn("alpha", yaml_set.data["yaml"]["query_value"])
        json.dumps(yaml_set.data["yaml"]["query_value"])

    def test_repo_yaml_inspect_rejects_paths_outside_repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            result = repo_yaml_inspect(repo, "../outside.yaml")

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_PATH_TRAVERSAL")


# ---------------------------------------------------------------------------
# check_hub_stability
# ---------------------------------------------------------------------------

def _write_stable_skill_md(path: Path, with_name: bool = True, with_description: bool = True):
    """
    Write a SKILL.md file marking the skill as stable, optionally including a name and a description.
    
    Parameters:
        path (Path): Destination path for SKILL.md.
        with_name (bool): If True, include a `name` field in the front matter.
        with_description (bool): If True, include a `description` field in the front matter.
    """
    lines = ["---", "stability: stable"]
    if with_name:
        lines.append("name: my-skill")
    if with_description:
        lines.append("description: A very useful skill that does something important.")
    lines.extend(["---", "", "# My Skill", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_unstable_skill_md(path: Path):
    """
    Create a SKILL.md file at the given path that does not declare stability.
    
    The file contains YAML front matter with `name` and `description` and a simple markdown body; it intentionally omits a `stability: stable` field.
    
    Parameters:
        path (Path): Destination file path where the SKILL.md will be written.
    """
    path.write_text(
        "---\nname: unstable-skill\ndescription: Not marked stable.\n---\n# Unstable Skill\n",
        encoding="utf-8",
    )


class TestCheckHubStability(unittest.TestCase):
    def test_returns_success_with_no_skill_mds(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            result = check_hub_stability(repo)
        self.assertEqual(result.status, "success")

    def test_detects_zero_stable_skills_in_empty_repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            result = check_hub_stability(repo)
        self.assertEqual(result.data["stable_count"], 0)
        self.assertEqual(result.data["stable_skills"], [])

    def test_detects_stable_skill(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            skill_dir = repo / "Skills" / "my-skill"
            skill_dir.mkdir(parents=True)
            _write_stable_skill_md(skill_dir / "SKILL.md")
            result = check_hub_stability(repo)
        self.assertEqual(result.data["stable_count"], 1)
        self.assertIn("my-skill", result.data["stable_skills"])

    def test_ignores_non_stable_skills(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            skill_dir = repo / "Skills" / "unstable"
            skill_dir.mkdir(parents=True)
            _write_unstable_skill_md(skill_dir / "SKILL.md")
            result = check_hub_stability(repo)
        self.assertEqual(result.data["stable_count"], 0)

    def test_checked_files_zero_when_no_changed_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            result = check_hub_stability(repo)
        self.assertEqual(result.data["checked_files"], 0)

    def test_checked_files_counts_passed_changed_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            result = check_hub_stability(repo, changed_files=["Skills/a/SKILL.md", "Skills/b/SKILL.md"])
        self.assertEqual(result.data["checked_files"], 2)

    def test_stable_skill_missing_name_field_raises_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            skill_dir = repo / "Skills" / "broken-skill"
            skill_dir.mkdir(parents=True)
            _write_stable_skill_md(skill_dir / "SKILL.md", with_name=False)
            result = check_hub_stability(
                repo,
                changed_files=["Skills/broken-skill/SKILL.md"]
            )
        self.assertEqual(result.status, "error")
        self.assertTrue(
            any("STABLE SKILL MISSING 'name'" in e for e in result.data.get("errors", []))
        )

    def test_stable_skill_missing_description_field_raises_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            skill_dir = repo / "Skills" / "no-desc"
            skill_dir.mkdir(parents=True)
            _write_stable_skill_md(skill_dir / "SKILL.md", with_description=False)
            result = check_hub_stability(
                repo,
                changed_files=["Skills/no-desc/SKILL.md"]
            )
        self.assertEqual(result.status, "error")
        self.assertTrue(
            any("STABLE SKILL MISSING 'description'" in e for e in result.data.get("errors", []))
        )

    def test_stable_skill_with_all_fields_passes_validation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            skill_dir = repo / "Skills" / "complete-skill"
            skill_dir.mkdir(parents=True)
            _write_stable_skill_md(skill_dir / "SKILL.md")
            result = check_hub_stability(
                repo,
                changed_files=["Skills/complete-skill/SKILL.md"]
            )
        self.assertEqual(result.status, "success")
        self.assertNotIn("errors", result.data)

    def test_changed_file_not_skill_md_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            (repo / "Skills" / "some-skill").mkdir(parents=True)
            (repo / "Skills" / "some-skill" / "README.md").write_text("readme", encoding="utf-8")
            result = check_hub_stability(
                repo,
                changed_files=["Skills/some-skill/README.md"]
            )
        self.assertEqual(result.status, "success")

    def test_deleted_stable_skill_without_edges_file_is_safe(self):
        """Deleting a file not present on disk without edges file should not add errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            # File does not exist (simulates deletion)
            result = check_hub_stability(
                repo,
                changed_files=["Skills/deleted-skill/SKILL.md"]
            )
        # No edges file exists, so no error should be reported
        self.assertEqual(result.status, "success")

    def test_deleted_stable_skill_found_in_edges_raises_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            edges_dir = repo / "ops" / "metrics" / "graph"
            edges_dir.mkdir(parents=True)
            edges = {
                "nodes": [
                    {"id": "deleted-stable", "stability": "stable"},
                    {"id": "other-skill", "stability": "unstable"},
                ]
            }
            (edges_dir / "skill-edges.json").write_text(
                json.dumps(edges), encoding="utf-8"
            )
            result = check_hub_stability(
                repo,
                changed_files=["Skills/deleted-stable/SKILL.md"]
            )
        self.assertEqual(result.status, "error")
        self.assertTrue(
            any("STABLE SKILL DELETED" in e for e in result.data.get("errors", []))
        )

    def test_deleted_non_stable_skill_in_edges_does_not_raise_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            edges_dir = repo / "ops" / "metrics" / "graph"
            edges_dir.mkdir(parents=True)
            edges = {
                "nodes": [
                    {"id": "regular-skill", "stability": "unstable"},
                ]
            }
            (edges_dir / "skill-edges.json").write_text(
                json.dumps(edges), encoding="utf-8"
            )
            result = check_hub_stability(
                repo,
                changed_files=["Skills/regular-skill/SKILL.md"]
            )
        self.assertEqual(result.status, "success")

    def test_error_objects_have_err_validation_code(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            skill_dir = repo / "Skills" / "broken"
            skill_dir.mkdir(parents=True)
            _write_stable_skill_md(skill_dir / "SKILL.md", with_name=False)
            result = check_hub_stability(repo, changed_files=["Skills/broken/SKILL.md"])
        for err in result.errors:
            self.assertEqual(err.code, "ERR_VALIDATION")

    def test_multiple_stable_skills_detected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            for skill_name in ("skill-a", "skill-b", "skill-c"):
                skill_dir = repo / "Skills" / skill_name
                skill_dir.mkdir(parents=True)
                _write_stable_skill_md(skill_dir / "SKILL.md")
            result = check_hub_stability(repo)
        self.assertEqual(result.data["stable_count"], 3)
        self.assertEqual(result.data["stable_skills"], sorted(["skill-a", "skill-b", "skill-c"]))

    def test_stable_skills_list_is_sorted(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            for skill_name in ("z-skill", "a-skill", "m-skill"):
                skill_dir = repo / "Skills" / skill_name
                skill_dir.mkdir(parents=True)
                _write_stable_skill_md(skill_dir / "SKILL.md")
            result = check_hub_stability(repo)
        self.assertEqual(result.data["stable_skills"], sorted(result.data["stable_skills"]))

    def test_unstable_changed_file_does_not_cause_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            skill_dir = repo / "Skills" / "not-stable"
            skill_dir.mkdir(parents=True)
            _write_unstable_skill_md(skill_dir / "SKILL.md")
            result = check_hub_stability(
                repo,
                changed_files=["Skills/not-stable/SKILL.md"]
            )
        self.assertEqual(result.status, "success")


# ---------------------------------------------------------------------------
# provider_audit
# ---------------------------------------------------------------------------

class TestProviderAudit(unittest.TestCase):
    def _make_fake_run(self, returncode: int, stdout: str, stderr: str = ""):
        """
        Create a fake subprocess.run implementation that returns a subprocess.CompletedProcess with the specified returncode, stdout, and stderr.
        
        Parameters:
            returncode (int): The exit code to set on the returned CompletedProcess.
            stdout (str): The stdout content to set on the returned CompletedProcess.
            stderr (str): The stderr content to set on the returned CompletedProcess (default: "").
        
        Returns:
            function: A callable compatible with subprocess.run that returns a subprocess.CompletedProcess whose
            `args` is taken from the first positional argument passed to the callable and whose `returncode`, `stdout`,
            and `stderr` are set to the provided values.
        """
        def fake_run(*args, **kwargs):
            """
            Create a fake subprocess.CompletedProcess for use in tests.
            
            Parameters:
                *args: Positional arguments passed to the fake run; the first positional argument is used as the CompletedProcess.args value.
                **kwargs: Ignored.
            
            Returns:
                completed (subprocess.CompletedProcess): A CompletedProcess whose `returncode`, `stdout`, and `stderr` are those captured from the surrounding test context and whose `args` is set to the first positional argument.
            """
            return subprocess.CompletedProcess(
                args=args[0],
                returncode=returncode,
                stdout=stdout,
                stderr=stderr,
            )
        return fake_run

    def test_provider_audit_success_when_script_returns_pass(self):
        report = {"status": "pass", "findings": []}
        fake_run = self._make_fake_run(0, json.dumps(report))
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("ask.commands.repo.subprocess.run", side_effect=fake_run):
                result = provider_audit(Path(tmpdir))
        self.assertEqual(result.status, "success")

    def test_provider_audit_error_when_script_exits_nonzero(self):
        report = {"status": "fail", "findings": ["legacy path found"]}
        fake_run = self._make_fake_run(1, json.dumps(report))
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("ask.commands.repo.subprocess.run", side_effect=fake_run):
                result = provider_audit(Path(tmpdir))
        self.assertEqual(result.status, "error")

    def test_provider_audit_error_when_report_status_is_fail(self):
        report = {"status": "fail"}
        fake_run = self._make_fake_run(0, json.dumps(report))
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("ask.commands.repo.subprocess.run", side_effect=fake_run):
                result = provider_audit(Path(tmpdir))
        self.assertEqual(result.status, "error")

    def test_provider_audit_stores_report_under_provider_policy(self):
        report = {"status": "pass", "findings": []}
        fake_run = self._make_fake_run(0, json.dumps(report))
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("ask.commands.repo.subprocess.run", side_effect=fake_run):
                result = provider_audit(Path(tmpdir))
        self.assertIn("provider_policy", result.data)
        self.assertEqual(result.data["provider_policy"]["status"], "pass")

    def test_provider_audit_handles_invalid_json_output(self):
        fake_run = self._make_fake_run(0, "not valid json", "some stderr")
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("ask.commands.repo.subprocess.run", side_effect=fake_run):
                result = provider_audit(Path(tmpdir))
        self.assertEqual(result.status, "error")
        self.assertIn("provider_policy", result.data)
        self.assertEqual(result.data["provider_policy"]["status"], "fail")

    def test_provider_audit_error_includes_err_validation_code(self):
        report = {"status": "fail"}
        fake_run = self._make_fake_run(1, json.dumps(report))
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("ask.commands.repo.subprocess.run", side_effect=fake_run):
                result = provider_audit(Path(tmpdir))
        self.assertTrue(len(result.errors) > 0)
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")

    def test_provider_audit_preserves_raw_stdout_on_json_error(self):
        raw = "not-json-output"
        fake_run = self._make_fake_run(0, raw, "stderr text")
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("ask.commands.repo.subprocess.run", side_effect=fake_run):
                result = provider_audit(Path(tmpdir))
        policy = result.data["provider_policy"]
        self.assertEqual(policy["raw_stdout"], raw)
        self.assertEqual(policy["raw_stderr"], "stderr text")


if __name__ == "__main__":
    unittest.main()
