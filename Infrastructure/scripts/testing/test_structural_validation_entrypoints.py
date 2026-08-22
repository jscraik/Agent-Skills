from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER = REPO_ROOT / "Infrastructure" / "scripts" / "check-code-size.mjs"
HOOK = REPO_ROOT / "Infrastructure" / "scripts" / "hook-pre-commit.sh"


class StructuralValidationEntrypointTests(unittest.TestCase):
    def test_checker_routes_to_repository_structural_validators(self) -> None:
        """The compatibility checker forwards the owned structural scope."""
        source = CHECKER.read_text(encoding="utf-8")

        self.assertIn("verify_ask_cli_modularity.py", source)
        self.assertIn("verify_program_design.py", source)
        self.assertIn("run-infrastructure-python.sh", source)
        self.assertIn("collectChangedPaths", source)
        self.assertIn('"--changed-files"', source)
        self.assertIn('"--staged-source"', source)
        self.assertNotIn("quality:size", source)
        self.assertNotIn("pnpm", source)
        self.assertNotIn("allowlist", source.lower())
        self.assertNotIn("waiver", source.lower())

    def test_hook_delegates_to_the_canonical_pre_commit_owner(self) -> None:
        """The compatibility hook must not duplicate the canonical hook logic."""
        source = HOOK.read_text(encoding="utf-8")

        self.assertIn('exec bash "$script_dir/hooks/pre-commit.sh"', source)
        self.assertIn("readlink", source)
        self.assertNotIn("quality:size", source)
        self.assertNotIn("npm run", source)
        self.assertNotIn("pnpm", source)

    def test_entrypoints_have_valid_syntax(self) -> None:
        """Both compatibility entrypoints parse before runtime execution."""
        for command in (("node", "--check", str(CHECKER)), ("bash", "-n", str(HOOK))):
            with self.subTest(command=command):
                completed = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
                self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_checker_rejects_conflicting_scope_modes(self) -> None:
        """The checker fails closed before resolving paths for conflicting modes."""
        completed = subprocess.run(
            ("node", str(CHECKER), "--all", "--staged"),
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertIn("--all and --staged are mutually exclusive", completed.stderr)

    def test_checker_forwards_staged_validator_paths_and_index_source(self) -> None:
        """Staged validator edits cannot fall outside their own validation scope."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            checker, validator_paths = self._prepare_staged_validator_repo(root)
            capture = root / "captured.jsonl"
            env = self._capture_environment(root, capture)
            completed = subprocess.run(
                ("node", str(checker), "--staged"),
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)

            invocations = [json.loads(line) for line in capture.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(invocations), 2)
            for invocation in invocations:
                self.assertIn("--changed-files", invocation)
                for path in validator_paths:
                    self.assertIn(path.relative_to(root).as_posix(), invocation)
            self.assertIn("--staged-source", invocations[0])
            self.assertIn("--staged-source", invocations[1])

    def test_checker_all_mode_forwards_only_python_paths(self) -> None:
        """All-mode avoids oversized argv payloads by filtering before spawning."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            checker, validator_paths = self._prepare_staged_validator_repo(root)
            readme = root / "README.md"
            readme.write_text("tracked non-Python input\n", encoding="utf-8")
            self._git(root, "add", readme.relative_to(root).as_posix())
            capture = root / "captured.jsonl"
            completed = subprocess.run(
                ("node", str(checker), "--all"),
                cwd=root,
                env=self._capture_environment(root, capture),
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            invocations = [json.loads(line) for line in capture.read_text(encoding="utf-8").splitlines()]
            for invocation in invocations:
                self.assertNotIn("README.md", invocation)
                for path in validator_paths:
                    self.assertIn(path.relative_to(root).as_posix(), invocation)

    def _prepare_staged_validator_repo(self, root: Path) -> tuple[Path, tuple[Path, Path]]:
        """Create a Git fixture whose two validator edits exist only in the index."""
        scripts_dir = root / "Infrastructure" / "scripts"
        library_dir = scripts_dir / "lib"
        library_dir.mkdir(parents=True)
        checker = shutil.copy2(CHECKER, scripts_dir / CHECKER.name)
        shutil.copy2(
            REPO_ROOT / "Infrastructure/scripts/lib/changed-files.mjs",
            library_dir / "changed-files.mjs",
        )
        validator_dir = root / "scripts/validation-and-linting"
        validator_dir.mkdir(parents=True)
        validators = (
            validator_dir / "verify_ask_cli_modularity.py",
            validator_dir / "verify_program_design.py",
        )
        for path in validators:
            path.write_text("VALUE = 1\n", encoding="utf-8")
        self._git(root, "init")
        self._git(root, "add", ".")
        self._git(root, "-c", "user.name=Structural Test", "-c", "user.email=structural@example.invalid", "commit", "-m", "test: establish baseline")
        for path in validators:
            path.write_text("VALUE = 2\n", encoding="utf-8")
        self._git(root, "add", *[path.relative_to(root).as_posix() for path in validators])
        return Path(checker), validators

    @staticmethod
    def _capture_environment(root: Path, capture: Path) -> dict[str, str]:
        """Return an environment whose Bash executable records wrapper arguments."""
        fake_bin = root / "bin"
        fake_bin.mkdir()
        fake_bash = fake_bin / "bash"
        fake_bash.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, sys\n"
            "with open(os.environ['STRUCTURAL_CAPTURE'], 'a', encoding='utf-8') as handle:\n"
            "    handle.write(json.dumps(sys.argv[1:]) + '\\n')\n",
            encoding="utf-8",
        )
        fake_bash.chmod(0o755)
        env = os.environ.copy()
        env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
        env["STRUCTURAL_CAPTURE"] = str(capture)
        return env

    def test_hook_resolves_a_file_symlink_before_delegating(self) -> None:
        """A projected file symlink delegates beside the physical hook source."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            scripts_dir = root / "Infrastructure" / "scripts"
            hooks_dir = scripts_dir / "hooks"
            hooks_dir.mkdir(parents=True)
            wrapper = scripts_dir / HOOK.name
            shutil.copy2(HOOK, wrapper)
            marker = root / "canonical hook's marker"
            canonical = hooks_dir / "pre-commit.sh"
            canonical.write_text(
                f"#!/usr/bin/env bash\nprintf '%s\\n' canonical > {shlex.quote(str(marker))}\n",
                encoding="utf-8",
            )
            projected = root / "projected-pre-commit"
            projected.symlink_to(wrapper)

            completed = subprocess.run(
                ("bash", str(projected)),
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(marker.read_text(encoding="utf-8"), "canonical\n")

    @staticmethod
    def _git(root: Path, *args: str) -> None:
        """Run one fixture-scoped Git command and fail with its diagnostic."""
        completed = subprocess.run(
            ("git", *args),
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise AssertionError(completed.stderr)


if __name__ == "__main__":
    unittest.main()
