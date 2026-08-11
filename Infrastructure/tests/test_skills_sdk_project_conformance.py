import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ask.commands.skills_impl import init_skill
from helpers.schema_validator import _validate_schema_subset


REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET = "Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md"
CONFORMANCE_SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/project-conformance-receipt.v1.schema.json"


def _command_env() -> dict[str, str]:
    """
    Create a copy of the current process environment with deterministic defaults used by the tests for cache, state, tool caches, trust config, and install timestamp.
    
    The returned mapping preserves existing environment entries and only provides defaults when the corresponding keys are absent:
    - XDG_CACHE_HOME, XDG_STATE_HOME: per-test temporary XDG dirs
    - MISE_CACHE_DIR, UV_CACHE_DIR: per-test tool cache dirs
    - MISE_TRUSTED_CONFIG_PATHS: repository-level trusted mise config path
    - ASK_SKILLS_SDK_INSTALL_TIMESTAMP: fixed ISO timestamp used for deterministic installs
    
    Returns:
        env (dict[str, str]): A modified environment mapping suitable for launching subprocesses in tests.
    """
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("MISE_STATE_DIR", str(temp_base / "mise-state"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    env.setdefault("ASK_SKILLS_SDK_INSTALL_TIMESTAMP", "2026-06-05T00:00:00Z")
    return env


def _run_process(*args: str) -> subprocess.CompletedProcess[str]:
    """
    Execute a subprocess command rooted at the repository and return its completed process result.
    
    Parameters:
        *args (str): Command and arguments to execute (e.g. "git", "status").
    
    Returns:
        subprocess.CompletedProcess[str]: The completed process containing `stdout`, `stderr`, and `returncode`. The subprocess is executed with `cwd` set to the repository root and an environment derived from `_command_env()`, and its stdout/stderr are captured.
    """
    return subprocess.run(
        list(args),
        cwd=REPO_ROOT,
        env=_command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _run_json_command(*args: str) -> dict:
    """
    Run a CLI command and return the JSON object parsed from its stdout.
    
    Parameters:
        *args (str): Command and its arguments to execute (passed to the subprocess runner).
    
    Returns:
        dict: The JSON object parsed from the command's stdout.
    
    Raises:
        AssertionError: If the subprocess exits with a non-zero return code; the exception message includes the command, return code, stdout, and stderr.
    """
    process = _run_process(*args)
    if process.returncode != 0:
        raise AssertionError(
            f"{' '.join(args)} failed with {process.returncode}\nSTDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
        )
    return json.loads(process.stdout)


def _marked_project(tmp_path: Path) -> Path:
    """
    Create a temporary project directory named "target-project" containing an AGENTS.md marker and return its path.
    
    Parameters:
        tmp_path (Path): Base temporary directory in which the project directory will be created.
    
    Returns:
        Path: Path to the created project root (tmp_path / "target-project").
    """
    project_root = tmp_path / "target-project"
    project_root.mkdir()
    (project_root / "AGENTS.md").write_text("# Target Project\n", encoding="utf-8")
    return project_root


def _install_valid_skill(project_root: Path) -> dict:
    """
    Install the validated fixture skill into a given project root using the test CLI wrapper.
    
    Parameters:
        project_root (Path): Path to the target project root where the fixture skill should be installed.
    
    Returns:
        result (dict): Parsed JSON payload emitted by the install command.
    """
    return _run_json_command(
        sys.executable,
        "Infrastructure/bin/ask",
        "sdk",
        "install",
        TARGET,
        "--apply",
        "--project-root",
        str(project_root),
        "--json",
        "--robot",
    )


class TestSkillsSdkProjectConformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """
        Prepare class-level JSON schema fixtures for tests.
        
        Loads the project-conformance receipt schema from CONFORMANCE_SCHEMA_PATH into `cls.schema`
        and populates `cls.schemas` with a mapping from the schema filename
        "project-conformance-receipt.v1.schema.json" to that schema object.
        """
        cls.schema = json.loads(CONFORMANCE_SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.schemas = {"project-conformance-receipt.v1.schema.json": cls.schema}

    def assert_receipt_valid(self, payload: dict) -> None:
        """
        Validate a receipt payload against the test class's loaded conformance schema.
        
        Parameters:
            payload (dict): The receipt JSON object to validate.
        """
        _validate_schema_subset(self.schema, payload, self.schemas)

    def test_init_skill_normalizes_scaffold_startup_failures(self) -> None:
        for error in (OSError("python missing"), subprocess.TimeoutExpired(["python3"], 60)):
            with self.subTest(error=type(error).__name__), patch(
                "ask.commands.skills_impl.subprocess.run",
                side_effect=error,
            ):
                result = init_skill(
                    REPO_ROOT,
                    "test-scaffold-skill",
                    "agent-ops",
                    "Test skill used to prove scaffold startup failures are structured.",
                )

            self.assertEqual(result.status, "error")
            self.assertEqual(result.errors[0].code, "ERR_RUNTIME")
            self.assertIn("could not complete", result.errors[0].message)

    def test_status_accepts_empty_marked_project_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            payload = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "project",
                "status",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )

            receipt = payload["data"]["skills_sdk_project_conformance"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertEqual(receipt["status"], "pass")
            self.assertTrue(receipt["project_managed"])
            self.assertEqual(receipt["installed_skill_count"], 0)
            self.assertFalse(receipt["mutation_performed"])
            self.assertFalse((project_root / "skills.lock.json").exists())

    def test_status_reports_installed_skill_cleanup_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)

            payload = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "project",
                "status",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )

            receipt = payload["data"]["skills_sdk_project_conformance"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertEqual(receipt["status"], "pass")
            self.assertEqual(receipt["installed_skill_count"], 1)
            self.assertEqual(receipt["rollback_ready_count"], 1)
            self.assertEqual(receipt["uninstall_ready_count"], 1)
            self.assertEqual(receipt["installed_skills"][0]["status"], "healthy")
            self.assertTrue(receipt["installed_skills"][0]["rollback_ready"])

    def test_doctor_blocks_on_modified_installed_file_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)
            skill_file = project_root / ".agents/skills/valid_skill/SKILL.md"
            before_lockfile = (project_root / "skills.lock.json").read_text(encoding="utf-8")
            skill_file.write_text(skill_file.read_text(encoding="utf-8") + "\n# Local edit\n", encoding="utf-8")

            process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "project",
                "doctor",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )

            self.assertEqual(process.returncode, 2, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_conformance"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertEqual(receipt["status"], "blocked")
            self.assertTrue(any("installed_file_modified" in code for code in receipt["installed_skills"][0]["issue_codes"]))
            self.assertFalse(receipt["mutation_performed"])
            self.assertEqual((project_root / "skills.lock.json").read_text(encoding="utf-8"), before_lockfile)

    def test_status_blocks_on_missing_install_receipt(self) -> None:
        """
        Verify that `ask sdk project status` blocks when an installed skill's install receipt is missing and reports the correct issue and readiness.
        
        Asserts that the command exits with code 2, the receipt `status` is `"blocked"`, the installed skill's `issue_codes` include `"missing_receipt"`, and the installed skill's `rollback_ready` is `False`.
        """
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)
            (project_root / ".harness/receipts/skills-sdk/install/valid_skill.json").unlink()

            process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "project",
                "status",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )

            self.assertEqual(process.returncode, 2, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_conformance"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertEqual(receipt["status"], "blocked")
            self.assertIn("missing_receipt", receipt["installed_skills"][0]["issue_codes"])
            self.assertFalse(receipt["installed_skills"][0]["rollback_ready"])

    def test_status_refuses_unmarked_project_root_before_reading_cwd(self) -> None:
        """
        Ensure the CLI reports an unmarked project root as unmanaged and exits without creating a lockfile.
        
        Runs `ask sdk project status` with `--project-root` pointing to a directory that lacks the project marker and asserts the command exits with code 2, the returned receipt validates against the conformance schema, `project_managed` is False, the first issue code includes `"missing_project_marker"`, and no `skills.lock.json` file is created.
        """
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "unmarked"
            project_root.mkdir()

            process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "project",
                "status",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )

            self.assertEqual(process.returncode, 2, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_conformance"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertFalse(receipt["project_managed"])
            self.assertIn("missing_project_marker", receipt["issues"][0]["code"])
            self.assertFalse((project_root / "skills.lock.json").exists())

    def test_status_blocks_on_malformed_lockfile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            (project_root / "skills.lock.json").write_text("{broken", encoding="utf-8")

            process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "project",
                "status",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )

            self.assertEqual(process.returncode, 2, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_conformance"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertEqual(receipt["lockfile_status"], "invalid")
            self.assertEqual(receipt["issues"][0]["code"], "malformed_lockfile")

    def test_public_wrapper_matches_ask_project_status(self) -> None:
        """
        Verify the public wrapper CLI produces the same project status receipt as the main `ask` CLI after normalizing variable fields.
        
        Runs `Infrastructure/bin/ask sdk project status` and `bin/skills-sdk project status` against separate marked temporary projects, normalizes the `project_root` and `project_root_identity` fields in both receipts, asserts the normalized receipts are equal, and asserts the wrapper payload's `metadata["command"]` equals the expected command string constructed from the wrapper project root.
        """
        with tempfile.TemporaryDirectory() as ask_tmp, tempfile.TemporaryDirectory() as wrapper_tmp:
            ask_root = _marked_project(Path(ask_tmp))
            wrapper_root = _marked_project(Path(wrapper_tmp))

            ask_payload = _run_json_command(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "project",
                "status",
                "--project-root",
                str(ask_root),
                "--json",
                "--robot",
            )
            wrapper_payload = _run_json_command(
                sys.executable,
                "bin/skills-sdk",
                "project",
                "status",
                "--project-root",
                str(wrapper_root),
                "--json",
                "--robot",
            )

            ask_receipt = ask_payload["data"]["skills_sdk_project_conformance"]["receipt"]
            wrapper_receipt = wrapper_payload["data"]["skills_sdk_project_conformance"]["receipt"]
            ask_receipt["project_root"] = "<normalized>"
            ask_receipt["project_root_identity"] = {"identity_kind": "realpath", "realpath": "<normalized>", "exists": True}
            wrapper_receipt["project_root"] = "<normalized>"
            wrapper_receipt["project_root_identity"] = {"identity_kind": "realpath", "realpath": "<normalized>", "exists": True}
            self.assertEqual(wrapper_receipt, ask_receipt)
            self.assertEqual(wrapper_payload["metadata"]["command"], "sdk project status --project-root " + str(wrapper_root) + " --json --robot")

    def test_status_blocks_on_missing_lockfile_with_installed_evidence(self) -> None:
        """
        Verify that when skills.lock.json is missing but installed evidence exists, status reports missing_with_installed_evidence and blocks.

        Installs a skill, removes the lockfile while leaving receipts and installed files, then asserts the command exits with code 2, lockfile_status is "missing_with_installed_evidence", and conformance status is "blocked".
        """
        with tempfile.TemporaryDirectory() as tmp:
            project_root = _marked_project(Path(tmp))
            _install_valid_skill(project_root)
            (project_root / "skills.lock.json").unlink()

            process = _run_process(
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "project",
                "status",
                "--project-root",
                str(project_root),
                "--json",
                "--robot",
            )

            self.assertEqual(process.returncode, 2, process.stdout)
            payload = json.loads(process.stdout)
            receipt = payload["data"]["skills_sdk_project_conformance"]["receipt"]
            self.assert_receipt_valid(receipt)
            self.assertEqual(receipt["lockfile_status"], "missing_with_installed_evidence")
            self.assertEqual(receipt["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
