#!/usr/bin/env python3
"""Tests for the prepare-worktree.sh path rename PR.

This PR renames the canonical path for prepare-worktree.sh from
  Infrastructure/scripts/lifecycle-and-sync/prepare-worktree.sh
to
  scripts/prepare-worktree.sh

Covers all files modified in the PR:
- Infrastructure/scripts/lifecycle-and-sync/prepare-worktree.sh  (usage() text)
- Infrastructure/scripts/check-environment.sh  (required_support_files array)
- Makefile  (worktree-ready target)
- .harness/restore-manifest.json  (path field)
- .harness/upgrade-manifest.json  (path field)
- .github/CODEOWNERS  (path entry)
- CONTRIBUTING.md  (inline text reference)
- README.md  (no hardcoded skill count)
"""

from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

OLD_PATH = "Infrastructure/scripts/lifecycle-and-sync/prepare-worktree.sh"
NEW_PATH = "scripts/prepare-worktree.sh"

PREPARE_WORKTREE_SCRIPT = (
    REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync" / "prepare-worktree.sh"
)
CHECK_ENV_SCRIPT = REPO_ROOT / "Infrastructure" / "scripts" / "check-environment.sh"
MAKEFILE = REPO_ROOT / "Makefile"
RESTORE_MANIFEST = REPO_ROOT / ".harness" / "restore-manifest.json"
UPGRADE_MANIFEST = REPO_ROOT / ".harness" / "upgrade-manifest.json"
CODEOWNERS = REPO_ROOT / ".github" / "CODEOWNERS"
CONTRIBUTING_MD = REPO_ROOT / "CONTRIBUTING.md"
README_MD = REPO_ROOT / "README.md"


def _bash(snippet: str, env: dict | None = None, cwd: str | None = None) -> subprocess.CompletedProcess:
    """Execute a bash snippet and return the completed process result."""
    base_env = {k: v for k, v in os.environ.items()}
    if env:
        base_env.update(env)
    return subprocess.run(
        ["bash", "-c", snippet],
        capture_output=True,
        text=True,
        env=base_env,
        cwd=cwd,
    )


# ---------------------------------------------------------------------------
# prepare-worktree.sh: usage() text reflects new canonical path
# ---------------------------------------------------------------------------


class TestPrepareWorktreeUsageText(unittest.TestCase):
    """Verify the usage() function in prepare-worktree.sh uses the new path."""

    def test_usage_references_new_path(self) -> None:
        """--help output must show 'scripts/prepare-worktree.sh', not the old nested path."""
        result = _bash(f'bash "{PREPARE_WORKTREE_SCRIPT}" --help')
        self.assertEqual(result.returncode, 0, f"--help exited non-zero: {result.stderr}")
        self.assertIn(NEW_PATH, result.stdout, "usage() must contain the new canonical path")

    def test_usage_does_not_reference_old_path(self) -> None:
        """--help output must NOT contain the old Infrastructure nested path."""
        result = _bash(f'bash "{PREPARE_WORKTREE_SCRIPT}" --help')
        self.assertEqual(result.returncode, 0, f"--help exited non-zero: {result.stderr}")
        self.assertNotIn(
            OLD_PATH,
            result.stdout,
            "usage() must not reference the old path after the rename",
        )

    def test_help_flag_short_form_also_works(self) -> None:
        """-h flag must also show usage with the new path."""
        result = _bash(f'bash "{PREPARE_WORKTREE_SCRIPT}" -h')
        self.assertEqual(result.returncode, 0, f"-h exited non-zero: {result.stderr}")
        self.assertIn(NEW_PATH, result.stdout, "-h usage must contain the new canonical path")

    def test_usage_text_contains_usage_prefix(self) -> None:
        """usage() output must start with 'Usage:' prefix."""
        result = _bash(f'bash "{PREPARE_WORKTREE_SCRIPT}" --help')
        self.assertEqual(result.returncode, 0)
        self.assertIn("Usage:", result.stdout, "usage output must include 'Usage:' prefix")

    def test_usage_mentions_force_install_option(self) -> None:
        """usage() must document the --force-install option."""
        result = _bash(f'bash "{PREPARE_WORKTREE_SCRIPT}" --help')
        self.assertEqual(result.returncode, 0)
        self.assertIn("--force-install", result.stdout, "usage must document --force-install")

    def test_unknown_arg_prints_usage_to_stderr_and_exits_2(self) -> None:
        """Unknown argument must cause exit code 2 and usage text in stderr."""
        result = _bash(f'bash "{PREPARE_WORKTREE_SCRIPT}" --unknown-arg-xyz 2>&1; echo "exit:$?"')
        self.assertIn("exit:2", result.stdout, "unknown arg must exit with code 2")
        self.assertIn(NEW_PATH, result.stdout, "stderr usage message must contain the new path")

    def test_unknown_arg_does_not_show_old_path(self) -> None:
        """Error usage output for unknown arg must NOT contain the old nested path."""
        result = _bash(f'bash "{PREPARE_WORKTREE_SCRIPT}" --unknown-arg-xyz 2>&1')
        self.assertNotIn(OLD_PATH, result.stdout, "error usage must not reference old path")


# ---------------------------------------------------------------------------
# check-environment.sh: required_support_files uses new path
# ---------------------------------------------------------------------------


class TestCheckEnvironmentSupportFiles(unittest.TestCase):
    """Verify check-environment.sh required_support_files array contains the new path."""

    def test_required_support_files_contains_new_path(self) -> None:
        """The required_support_files array in check-environment.sh must include 'scripts/prepare-worktree.sh'."""
        content = CHECK_ENV_SCRIPT.read_text(encoding="utf-8")
        self.assertIn(
            NEW_PATH,
            content,
            "check-environment.sh must reference 'scripts/prepare-worktree.sh' in required_support_files",
        )

    def test_required_support_files_does_not_contain_old_path(self) -> None:
        """The required_support_files array must NOT contain the old nested path."""
        content = CHECK_ENV_SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn(
            OLD_PATH,
            content,
            "check-environment.sh must not reference the old path after rename",
        )

    def test_required_support_files_array_definition_is_present(self) -> None:
        """The required_support_files variable assignment must exist in the script."""
        content = CHECK_ENV_SCRIPT.read_text(encoding="utf-8")
        self.assertIn(
            "required_support_files=",
            content,
            "required_support_files array assignment must be present",
        )

    def test_new_path_appears_in_required_support_files_array_line(self) -> None:
        """The new path must appear on the same line as the required_support_files array definition."""
        content = CHECK_ENV_SCRIPT.read_text(encoding="utf-8")
        for line in content.splitlines():
            if "required_support_files=" in line:
                self.assertIn(
                    NEW_PATH,
                    line,
                    f"New path must be on the required_support_files array line, got: {line!r}",
                )
                break
        else:
            self.fail("required_support_files= line not found in check-environment.sh")

    def test_old_path_absent_from_required_support_files_array_line(self) -> None:
        """The old path must NOT appear on the required_support_files array definition line."""
        content = CHECK_ENV_SCRIPT.read_text(encoding="utf-8")
        for line in content.splitlines():
            if "required_support_files=" in line:
                self.assertNotIn(
                    OLD_PATH,
                    line,
                    "Old path must not appear on required_support_files line after rename",
                )
                break

    def test_check_env_script_has_no_old_path_anywhere(self) -> None:
        """Regression: old path must not appear anywhere in check-environment.sh."""
        content = CHECK_ENV_SCRIPT.read_text(encoding="utf-8")
        occurrences = content.count(OLD_PATH)
        self.assertEqual(
            occurrences,
            0,
            f"Found {occurrences} occurrence(s) of old path in check-environment.sh",
        )


# ---------------------------------------------------------------------------
# Makefile: worktree-ready target uses new path
# ---------------------------------------------------------------------------


class TestMakefileWorktreeReadyTarget(unittest.TestCase):
    """Verify the Makefile worktree-ready target references the new script path."""

    def test_worktree_ready_uses_new_path(self) -> None:
        """worktree-ready target must invoke './scripts/prepare-worktree.sh'."""
        content = MAKEFILE.read_text(encoding="utf-8")
        self.assertIn(
            f"./{NEW_PATH}",
            content,
            "Makefile worktree-ready must call ./scripts/prepare-worktree.sh",
        )

    def test_worktree_ready_does_not_use_old_path(self) -> None:
        """worktree-ready target must NOT reference the old nested path."""
        content = MAKEFILE.read_text(encoding="utf-8")
        self.assertNotIn(
            OLD_PATH,
            content,
            "Makefile must not reference old path after rename",
        )

    def test_worktree_ready_target_is_defined(self) -> None:
        """The worktree-ready target must exist in the Makefile."""
        content = MAKEFILE.read_text(encoding="utf-8")
        self.assertIn(
            "worktree-ready:",
            content,
            "Makefile must define the worktree-ready target",
        )

    def test_worktree_ready_calls_bash(self) -> None:
        """worktree-ready target must call bash to execute the script."""
        content = MAKEFILE.read_text(encoding="utf-8")
        # Find the worktree-ready block and check it uses bash
        lines = content.splitlines()
        in_target = False
        for line in lines:
            if line.startswith("worktree-ready:"):
                in_target = True
                continue
            if in_target:
                if line.startswith("\t"):
                    self.assertIn(
                        "bash",
                        line,
                        "worktree-ready must invoke bash to run the script",
                    )
                    break
                elif line.strip():
                    break  # Next target reached without finding a command

    def test_makefile_has_no_old_path(self) -> None:
        """Regression: old path must not appear anywhere in the Makefile."""
        content = MAKEFILE.read_text(encoding="utf-8")
        occurrences = content.count(OLD_PATH)
        self.assertEqual(
            occurrences,
            0,
            f"Found {occurrences} occurrence(s) of old path in Makefile",
        )


# ---------------------------------------------------------------------------
# .harness/restore-manifest.json: path entry updated
# ---------------------------------------------------------------------------


class TestRestoreManifestPath(unittest.TestCase):
    """Verify restore-manifest.json lists the new prepare-worktree.sh path."""

    def _load(self) -> dict:
        return json.loads(RESTORE_MANIFEST.read_text(encoding="utf-8"))

    def test_new_path_present_in_manifest(self) -> None:
        """restore-manifest.json must contain an entry with path 'scripts/prepare-worktree.sh'."""
        data = self._load()
        entries = data if isinstance(data, list) else data.get("files", data.get("entries", []))
        # Walk all nested lists
        paths = self._collect_paths(data)
        self.assertIn(
            NEW_PATH,
            paths,
            f"restore-manifest.json must list '{NEW_PATH}'",
        )

    def test_old_path_absent_from_manifest(self) -> None:
        """restore-manifest.json must NOT contain the old nested path."""
        raw = RESTORE_MANIFEST.read_text(encoding="utf-8")
        self.assertNotIn(
            OLD_PATH,
            raw,
            "restore-manifest.json must not reference old path after rename",
        )

    def test_new_path_entry_has_action_created(self) -> None:
        """The new path entry in restore-manifest.json must have action='created'."""
        data = self._load()
        entry = self._find_entry(data, NEW_PATH)
        self.assertIsNotNone(entry, f"Entry for '{NEW_PATH}' not found in restore-manifest.json")
        self.assertEqual(
            entry.get("action"),
            "created",
            f"Expected action='created' for '{NEW_PATH}', got: {entry.get('action')!r}",
        )

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _collect_paths(obj: object) -> list[str]:
        """Recursively collect all 'path' values from a JSON structure."""
        paths: list[str] = []
        if isinstance(obj, dict):
            if "path" in obj:
                paths.append(obj["path"])
            for v in obj.values():
                paths.extend(TestRestoreManifestPath._collect_paths(v))
        elif isinstance(obj, list):
            for item in obj:
                paths.extend(TestRestoreManifestPath._collect_paths(item))
        return paths

    @staticmethod
    def _find_entry(obj: object, target_path: str) -> dict | None:
        """Find the first dict with path==target_path anywhere in the JSON structure."""
        if isinstance(obj, dict):
            if obj.get("path") == target_path:
                return obj
            for v in obj.values():
                found = TestRestoreManifestPath._find_entry(v, target_path)
                if found is not None:
                    return found
        elif isinstance(obj, list):
            for item in obj:
                found = TestRestoreManifestPath._find_entry(item, target_path)
                if found is not None:
                    return found
        return None


# ---------------------------------------------------------------------------
# .harness/upgrade-manifest.json: path entry updated
# ---------------------------------------------------------------------------


class TestUpgradeManifestPath(unittest.TestCase):
    """Verify upgrade-manifest.json lists the new prepare-worktree.sh path."""

    def _load(self) -> object:
        return json.loads(UPGRADE_MANIFEST.read_text(encoding="utf-8"))

    def _collect_paths(self, obj: object) -> list[str]:
        paths: list[str] = []
        if isinstance(obj, dict):
            if "path" in obj:
                paths.append(obj["path"])
            for v in obj.values():
                paths.extend(self._collect_paths(v))
        elif isinstance(obj, list):
            for item in obj:
                paths.extend(self._collect_paths(item))
        return paths

    def _find_entry(self, obj: object, target_path: str) -> dict | None:
        if isinstance(obj, dict):
            if obj.get("path") == target_path:
                return obj
            for v in obj.values():
                found = self._find_entry(v, target_path)
                if found is not None:
                    return found
        elif isinstance(obj, list):
            for item in obj:
                found = self._find_entry(item, target_path)
                if found is not None:
                    return found
        return None

    def test_new_path_present_in_upgrade_manifest(self) -> None:
        """upgrade-manifest.json must contain an entry with path 'scripts/prepare-worktree.sh'."""
        data = self._load()
        paths = self._collect_paths(data)
        self.assertIn(
            NEW_PATH,
            paths,
            f"upgrade-manifest.json must list '{NEW_PATH}'",
        )

    def test_old_path_absent_from_upgrade_manifest(self) -> None:
        """upgrade-manifest.json must NOT contain the old nested path."""
        raw = UPGRADE_MANIFEST.read_text(encoding="utf-8")
        self.assertNotIn(
            OLD_PATH,
            raw,
            "upgrade-manifest.json must not reference old path after rename",
        )

    def test_new_path_entry_has_template_hash(self) -> None:
        """The new path entry in upgrade-manifest.json must have a non-empty templateHash."""
        data = self._load()
        entry = self._find_entry(data, NEW_PATH)
        self.assertIsNotNone(entry, f"Entry for '{NEW_PATH}' not found in upgrade-manifest.json")
        template_hash = entry.get("templateHash", "")
        self.assertTrue(
            len(template_hash) > 0,
            f"Expected non-empty templateHash for '{NEW_PATH}'",
        )

    def test_new_path_entry_has_version(self) -> None:
        """The new path entry in upgrade-manifest.json must have a version field."""
        data = self._load()
        entry = self._find_entry(data, NEW_PATH)
        self.assertIsNotNone(entry, f"Entry for '{NEW_PATH}' not found in upgrade-manifest.json")
        self.assertIn("version", entry, f"Entry for '{NEW_PATH}' must have a version field")

    def test_upgrade_manifest_is_valid_json(self) -> None:
        """upgrade-manifest.json must be parseable as valid JSON."""
        try:
            self._load()
        except json.JSONDecodeError as exc:
            self.fail(f"upgrade-manifest.json is not valid JSON: {exc}")

    def test_restore_manifest_is_valid_json(self) -> None:
        """restore-manifest.json must be parseable as valid JSON."""
        try:
            json.loads(RESTORE_MANIFEST.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            self.fail(f"restore-manifest.json is not valid JSON: {exc}")


# ---------------------------------------------------------------------------
# .github/CODEOWNERS: path entry updated
# ---------------------------------------------------------------------------


class TestCodeownersPath(unittest.TestCase):
    """Verify CODEOWNERS references the new prepare-worktree.sh path."""

    def test_new_path_in_codeowners(self) -> None:
        """CODEOWNERS must contain a rule for /scripts/prepare-worktree.sh."""
        content = CODEOWNERS.read_text(encoding="utf-8")
        self.assertIn(
            "/scripts/prepare-worktree.sh",
            content,
            "CODEOWNERS must define ownership for /scripts/prepare-worktree.sh",
        )

    def test_old_path_absent_from_codeowners(self) -> None:
        """CODEOWNERS must NOT reference the old nested path."""
        content = CODEOWNERS.read_text(encoding="utf-8")
        self.assertNotIn(
            "/Infrastructure/scripts/lifecycle-and-sync/prepare-worktree.sh",
            content,
            "CODEOWNERS must not reference the old path after rename",
        )

    def test_codeowners_entry_assigns_owner(self) -> None:
        """The CODEOWNERS entry for the new path must assign at least one owner."""
        content = CODEOWNERS.read_text(encoding="utf-8")
        for line in content.splitlines():
            if "/scripts/prepare-worktree.sh" in line and not line.strip().startswith("#"):
                parts = line.split()
                self.assertGreater(
                    len(parts),
                    1,
                    "CODEOWNERS rule must have at least one owner assigned",
                )
                break
        else:
            self.fail("No non-comment CODEOWNERS rule found for /scripts/prepare-worktree.sh")

    def test_codeowners_new_path_not_duplicated(self) -> None:
        """CODEOWNERS must have exactly one rule for the new path (no duplicates)."""
        content = CODEOWNERS.read_text(encoding="utf-8")
        count = sum(
            1
            for line in content.splitlines()
            if "/scripts/prepare-worktree.sh" in line and not line.strip().startswith("#")
        )
        self.assertEqual(count, 1, f"Expected exactly 1 CODEOWNERS rule for new path, found {count}")


# ---------------------------------------------------------------------------
# CONTRIBUTING.md: text reference updated
# ---------------------------------------------------------------------------


class TestContributingMdPathReference(unittest.TestCase):
    """Verify CONTRIBUTING.md's Recommended policy section references the new prepare-worktree.sh path.

    The PR only updated the 'Treat ... prepare-worktree' line in the Recommended policy section.
    Other sections of CONTRIBUTING.md (e.g. Repo-local verification wrapper) were not in scope.
    """

    def _find_treat_prepare_worktree_line(self) -> str | None:
        """Return the 'Treat ... prepare-worktree' policy line, or None if not found."""
        content = CONTRIBUTING_MD.read_text(encoding="utf-8")
        for line in content.splitlines():
            if "prepare-worktree" in line and "Treat" in line:
                return line
        return None

    def test_new_path_in_recommended_policy_treat_line(self) -> None:
        """The 'Treat ... prepare-worktree' policy line must reference the new path."""
        line = self._find_treat_prepare_worktree_line()
        self.assertIsNotNone(line, "No 'Treat ... prepare-worktree' line found in CONTRIBUTING.md")
        self.assertIn(
            NEW_PATH,
            line,
            f"Bootstrap policy sentence must use the new path; got: {line!r}",
        )

    def test_old_path_absent_from_recommended_policy_treat_line(self) -> None:
        """The 'Treat ... prepare-worktree' policy line must NOT reference the old nested path."""
        line = self._find_treat_prepare_worktree_line()
        self.assertIsNotNone(line, "No 'Treat ... prepare-worktree' line found in CONTRIBUTING.md")
        self.assertNotIn(
            OLD_PATH,
            line,
            f"Bootstrap policy sentence must not use old path; got: {line!r}",
        )

    def test_contributing_treat_line_contains_worktree_bootstrap_description(self) -> None:
        """The policy line must still describe first-push bootstrap intent."""
        line = self._find_treat_prepare_worktree_line()
        self.assertIsNotNone(line, "No 'Treat ... prepare-worktree' line found in CONTRIBUTING.md")
        self.assertIn(
            "worktree",
            line.lower(),
            "Bootstrap policy sentence must still mention 'worktree'",
        )


# ---------------------------------------------------------------------------
# README.md: removed hardcoded skill count
# ---------------------------------------------------------------------------


class TestReadmeMdSkillCount(unittest.TestCase):
    """Verify README.md no longer hardcodes a specific skill count."""

    def test_readme_does_not_hardcode_21_skills(self) -> None:
        """README.md must not contain '21 skills' (the removed hardcoded count)."""
        content = README_MD.read_text(encoding="utf-8")
        self.assertNotIn(
            "21 skills",
            content,
            "README.md must not hardcode '21 skills'; the count should be dynamic or omitted",
        )

    def test_readme_still_describes_skills(self) -> None:
        """README.md must still mention 'skills' (the generic term)."""
        content = README_MD.read_text(encoding="utf-8")
        self.assertIn(
            "skills",
            content.lower(),
            "README.md must still reference 'skills'",
        )

    def test_readme_title_line_uses_generic_skills_phrase(self) -> None:
        """The first line of README.md must reference 'skills' without a leading number."""
        content = README_MD.read_text(encoding="utf-8")
        first_line = content.splitlines()[0] if content.splitlines() else ""
        # Should contain "skills" but not "21 skills"
        self.assertIn("skills", first_line.lower(), "First line must still mention 'skills'")
        self.assertNotIn("21 skills", first_line, "First line must not hardcode '21 skills'")

    def test_readme_introduction_line_has_no_hardcoded_count_before_skills(self) -> None:
        """Regression: the introductory description line must not contain '<number> skills'."""
        import re
        content = README_MD.read_text(encoding="utf-8")
        # Only check the line that was modified in this PR: the opening description line
        # containing 'governed repository of ... skills'
        for line in content.splitlines():
            if "governed repository of" in line and "skills" in line:
                matches = re.findall(r"\b\d+\s+skills\b", line)
                self.assertEqual(
                    matches,
                    [],
                    f"Opening description line still contains a hardcoded count: {matches!r} in {line!r}",
                )
                break


# ---------------------------------------------------------------------------
# Cross-file consistency: same new path everywhere
# ---------------------------------------------------------------------------


class TestCrossFilePathConsistency(unittest.TestCase):
    """Verify that all changed files are consistently updated to the new path."""

    def test_no_file_still_references_old_path(self) -> None:
        """Files fully updated by this PR should not contain the old nested path string.

        CONTRIBUTING.md is excluded because it has a section ('Repo-local verification wrapper')
        that references the old path but was not part of this PR's diff scope.
        """
        files_to_check = [
            CHECK_ENV_SCRIPT,
            MAKEFILE,
            RESTORE_MANIFEST,
            UPGRADE_MANIFEST,
            CODEOWNERS,
        ]
        for fpath in files_to_check:
            if not fpath.exists():
                continue
            content = fpath.read_text(encoding="utf-8")
            self.assertNotIn(
                OLD_PATH,
                content,
                f"{fpath.relative_to(REPO_ROOT)} still contains old path '{OLD_PATH}'",
            )

    def test_prepare_worktree_script_exists_at_old_location(self) -> None:
        """The script at the old location still exists (it was NOT deleted, just updated in references)."""
        self.assertTrue(
            PREPARE_WORKTREE_SCRIPT.exists(),
            f"prepare-worktree.sh must still exist at {PREPARE_WORKTREE_SCRIPT}",
        )

    def test_prepare_worktree_script_is_executable_or_runnable_via_bash(self) -> None:
        """The prepare-worktree.sh script must be syntactically valid bash."""
        result = _bash(f'bash -n "{PREPARE_WORKTREE_SCRIPT}"')
        self.assertEqual(
            result.returncode,
            0,
            f"prepare-worktree.sh has bash syntax errors: {result.stderr}",
        )

    def test_check_environment_script_is_syntactically_valid(self) -> None:
        """check-environment.sh must be syntactically valid bash."""
        result = _bash(f'bash -n "{CHECK_ENV_SCRIPT}"')
        self.assertEqual(
            result.returncode,
            0,
            f"check-environment.sh has bash syntax errors: {result.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
