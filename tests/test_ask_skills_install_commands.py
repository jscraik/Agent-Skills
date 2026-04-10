import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))

from ask.commands.skills import install_skill
from ask.envelope import CallResult


class TestAskSkillsInstallCommands(unittest.TestCase):
    def setUp(self) -> None:
        """
        Prepare an isolated temporary repository root for each test.
        
        Creates a temporary directory and a nested `repo` directory used as the repository root for tests, storing paths on `self.temp_dir` and `self.repo_root`.
        """
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ask-skills-install-cmds-"))
        self.repo_root = self.temp_dir / "repo"
        self.repo_root.mkdir(parents=True)

    def tearDown(self) -> None:
        """
        Remove the temporary directory created for the test.
        
        Deletes `self.temp_dir` and all its contents, ignoring any errors raised during removal.
        """
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("ask.commands.skills.sync_skills")
    @patch("ask.commands.skills.subprocess.run")
    def test_install_omits_validation_level_for_legacy_installer(self, mock_run, sync_mock) -> None:
        sync_result = CallResult()
        sync_result.status = "success"
        sync_result.data["logs"] = ["synced"]
        sync_mock.return_value = sync_result
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="usage: install\n", stderr=""),
            subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout="Installed sample-skill to /tmp/sample-skill\n",
                stderr="",
            ),
        ]

        result = install_skill(
            self.repo_root,
            url="https://github.com/example/sample-skill",
            dest="github",
        )

        self.assertEqual(result.status, "success")
        install_cmd = mock_run.call_args_list[1][0][0]
        self.assertNotIn("--validation-level", install_cmd)
        sync_mock.assert_called_once()

    @patch("ask.commands.skills.sync_skills")
    @patch("ask.commands.skills.subprocess.run")
    def test_install_passes_validation_level_when_supported(self, mock_run, sync_mock) -> None:
        """
        Verify that install_skill includes the --validation-level flag when the installer advertises support.
        
        Sets up subprocess.run to return a help/usage output containing '--validation-level' and then a successful install, then asserts the call to run the install command contains '--validation-level' and the overall result indicates success.
        """
        sync_result = CallResult()
        sync_result.status = "success"
        sync_result.data["logs"] = ["synced"]
        sync_mock.return_value = sync_result
        mock_run.side_effect = [
            subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout="usage: install [--validation-level {strict,compat}]\n",
                stderr="",
            ),
            subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout="Installed sample-skill to /tmp/sample-skill\n",
                stderr="",
            ),
        ]

        result = install_skill(
            self.repo_root,
            url="https://github.com/example/sample-skill",
            dest="github",
        )

        self.assertEqual(result.status, "success")
        install_cmd = mock_run.call_args_list[1][0][0]
        self.assertIn("--validation-level", install_cmd)

    @patch("ask.commands.skills.sync_skills")
    @patch("ask.commands.skills.subprocess.run")
    def test_install_passes_remediate_when_supported(self, mock_run, sync_mock) -> None:
        """
        Verify that when the installer advertises `--remediate`, install_skill includes `--remediate` in the installation command.
        
        Mocks the installer help output to include `--remediate`, stubs a successful install and sync, calls install_skill with `remediate=True`, and asserts the result is successful and the invoked install command contains `--remediate`.
        """
        sync_result = CallResult()
        sync_result.status = "success"
        sync_result.data["logs"] = ["synced"]
        sync_mock.return_value = sync_result
        mock_run.side_effect = [
            subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout="usage: install [--validation-level {strict,compat}] [--remediate]\n",
                stderr="",
            ),
            subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout="Installed sample-skill to /tmp/sample-skill\n",
                stderr="",
            ),
        ]

        result = install_skill(
            self.repo_root,
            url="https://github.com/example/sample-skill",
            dest="github",
            remediate=True,
        )

        self.assertEqual(result.status, "success")
        install_cmd = mock_run.call_args_list[1][0][0]
        self.assertIn("--remediate", install_cmd)

    @patch("ask.commands.skills.subprocess.run")
    def test_install_rejects_absolute_dest(self, mock_run) -> None:
        """
        Verifies that install_skill rejects an absolute destination path and does not invoke external installers.
        
        Asserts the call returns an error result containing at least one error whose code is `ERR_VALIDATION`, and that no subprocess.run calls were made.
        """
        result = install_skill(
            self.repo_root,
            url="https://github.com/example/sample-skill",
            dest="/tmp/non-canonical",
        )
        self.assertEqual(result.status, "error")
        self.assertTrue(result.errors)
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")
        mock_run.assert_not_called()

    @patch("ask.commands.skills.subprocess.run")
    def test_install_rejects_path_traversal_dest(self, mock_run) -> None:
        """
        Verifies that installing a skill rejects a destination containing path traversal.
        
        Asserts the call returns an error result with at least one error whose code is `ERR_VALIDATION`
        and that no subprocess commands were invoked.
        """
        result = install_skill(
            self.repo_root,
            url="https://github.com/example/sample-skill",
            dest="../outside",
        )
        self.assertEqual(result.status, "error")
        self.assertTrue(result.errors)
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")
        mock_run.assert_not_called()

    @patch("ask.commands.skills.sync_skills")
    @patch("ask.commands.skills.subprocess.run")
    def test_install_runs_workspace_sync_after_success(self, mock_run, sync_mock) -> None:
        """
        Verifies that a successful skill installation triggers a workspace sync and returns the canonical destination.
        
        Mocks the installer to advertise `--validation-level` and to report a successful installation, and stubs `sync_skills` to succeed. Asserts that the overall result is successful, `sync_skills` was invoked once with (repo_root, scope="workspace", dry_run=False), and the returned data contains the expected `canonical_dest`.
        """
        sync_result = CallResult()
        sync_result.status = "success"
        sync_result.data["logs"] = ["workspace synced"]
        sync_mock.return_value = sync_result
        mock_run.side_effect = [
            subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout="usage: install [--validation-level {strict,compat}]\n",
                stderr="",
            ),
            subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout="Installed sample-skill to /tmp/sample-skill\n",
                stderr="",
            ),
        ]

        result = install_skill(
            self.repo_root,
            url="https://github.com/example/sample-skill",
            dest="github",
        )

        self.assertEqual(result.status, "success")
        sync_mock.assert_called_once_with(self.repo_root, scope="workspace", dry_run=False)
        self.assertEqual(result.data.get("canonical_dest"), "github")


if __name__ == "__main__":
    unittest.main()
