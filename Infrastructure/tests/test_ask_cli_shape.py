from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path
from types import ModuleType, SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[2]
ASK_ENTRYPOINT = REPO_ROOT / "Infrastructure" / "bin" / "ask"
SYNC_WRAPPER = REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync" / "sync_skills.sh"
VALIDATOR_PATH = REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting" / "verify_ask_cli_modularity.py"
MAX_ENTRYPOINT_LINES = 1900


def _load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("verify_ask_cli_modularity", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load ask CLI modularity validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestAskCliShape(unittest.TestCase):
    def test_entrypoint_line_budget_does_not_grow(self) -> None:
        line_count = len(ASK_ENTRYPOINT.read_text(encoding="utf-8").splitlines())

        self.assertLessEqual(
            line_count,
            MAX_ENTRYPOINT_LINES,
            (
                "Infrastructure/bin/ask is already at the decomposition limit; "
                "move parser, dispatch, output, or prompt behavior into ask.* modules "
                "before adding more entrypoint code."
            ),
        )

    def test_entrypoint_keeps_output_and_prompt_helpers_extracted(self) -> None:
        content = ASK_ENTRYPOINT.read_text(encoding="utf-8")

        self.assertIn("from ask.cli_output import", content)
        self.assertIn("from ask.cli_prompts import", content)
        self.assertNotIn("def print_first_validation_command", content)
        self.assertNotIn("def prompt_nonempty", content)

    def test_evals_run_exposes_timeout_seconds(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ASK_ENTRYPOINT), "evals", "run", "--help"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )

        self.assertIn("--timeout-seconds", result.stdout)

    def test_evals_run_passes_timeout_seconds_to_runner(self) -> None:
        content = ASK_ENTRYPOINT.read_text(encoding="utf-8")

        self.assertIn("evals_run_parser.add_argument(\"--timeout-seconds\"", content)
        self.assertIn("timeout_seconds=args.timeout_seconds", content)

    def test_sync_wrapper_delegates_without_command_surface_fossils(self) -> None:
        content = SYNC_WRAPPER.read_text(encoding="utf-8")

        self.assertIn('exec bash "$SCRIPT_DIR/sync_skills_impl.sh" "$@"', content)
        self.assertNotIn("Keep legacy lifecycle command-surface text", content)
        self.assertNotIn("selection_policy.py", content)

    def test_function_shape_metrics_include_length_and_complexity(self) -> None:
        validator = _load_validator()
        metrics = validator._function_metrics(
            """
def sample(value):
    if value:
        return 1
    return 0
"""
        )

        self.assertEqual(metrics["sample"], (4, 2))

    def test_function_metrics_preserve_qualified_identity_for_moved_methods(self) -> None:
        validator = _load_validator()
        metrics = validator._function_metrics(
            """
class Runner:
    def execute(self, value):
        if value:
            return 1
        return 0
"""
        )

        self.assertIn("Runner.execute", metrics)
        self.assertNotIn("execute", metrics)

    def test_skills_sdk_evidence_status_and_hook_fixture_fit_shape_budget(self) -> None:
        validator = _load_validator()
        targets = {
            "Infrastructure/scripts/lib/ask/skills_sdk/evidence_status.py": {
                "build_evidence_status_receipt": (40, 12),
                "_build_acceptance_lane": (40, 12),
                "_load_or_build_qa_dispatch_record": (40, 12),
            },
            "Infrastructure/scripts/testing/test_validation_execution_environment.py": {
                "test_prek_reinstalls_when_expected_hooks_path_is_already_configured": (40, 12),
            },
        }

        for relative_path, functions in targets.items():
            metrics = validator._function_metrics(
                (REPO_ROOT / relative_path).read_text(encoding="utf-8")
            )
            for name, (max_lines, max_complexity) in functions.items():
                line_count, complexity = metrics[name]
                self.assertLessEqual(line_count, max_lines, f"{relative_path}:{name}")
                self.assertLessEqual(complexity, max_complexity, f"{relative_path}:{name}")

    def test_file_size_ratchet_allows_existing_oversized_file_only_when_it_shrinks(self) -> None:
        validator = _load_validator()
        args = SimpleNamespace(max_file_lines=3)
        issues: list[str] = []

        validator._check_file_size(VALIDATOR_PATH, "1\n2\n3\n4\n", "1\n2\n3\n4\n5\n", args, issues)
        self.assertEqual(issues, [])

        validator._check_file_size(VALIDATOR_PATH, "1\n2\n3\n4\n5\n6\n", "1\n2\n3\n4\n5\n", args, issues)
        self.assertEqual(len(issues), 1)

    def test_unchanged_oversized_function_is_allowed_by_ratchet(self) -> None:
        validator = _load_validator()
        args = SimpleNamespace(max_function_lines=1, max_complexity=1)
        source = "def sample(value):\n    if value:\n        return 1\n    return 0\n"
        issues: list[str] = []

        validator._check_function_shape(VALIDATOR_PATH, source, source, args, issues)

        self.assertEqual(issues, [])

    def test_growing_function_is_blocked_by_ratchet(self) -> None:
        validator = _load_validator()
        args = SimpleNamespace(max_function_lines=1, max_complexity=1)
        current = "def sample(value):\n    if value:\n        return 1\n    return 0\n"
        baseline = "def sample(value):\n    return 0\n"
        issues: list[str] = []

        validator._check_function_shape(VALIDATOR_PATH, current, baseline, args, issues)

        self.assertEqual(len(issues), 2)
        self.assertIn("function line budget", issues[0])
        self.assertIn("complexity budget", issues[1])

    def test_moved_function_uses_deleted_sibling_as_shape_baseline(self) -> None:
        validator = _load_validator()
        args = SimpleNamespace(max_function_lines=1, max_complexity=1)
        current = "def moved(value):\n    if value:\n        return 1\n    return 0\n"
        issues: list[str] = []

        with unittest.mock.patch.object(
            validator,
            "_moved_function_metrics",
            return_value={"moved": (4, 2)},
        ):
            validator._check_function_shape(VALIDATOR_PATH, current, None, args, issues)

        self.assertEqual(issues, [])

    def test_new_function_still_fails_without_a_move_baseline(self) -> None:
        validator = _load_validator()
        args = SimpleNamespace(max_function_lines=1, max_complexity=1)
        current = "def fresh(value):\n    if value:\n        return 1\n    return 0\n"
        issues: list[str] = []

        with unittest.mock.patch.object(validator, "_moved_function_metrics", return_value={}):
            validator._check_function_shape(VALIDATOR_PATH, current, None, args, issues)

        self.assertEqual(len(issues), 2)
        self.assertIn("function line budget", issues[0])
        self.assertIn("complexity budget", issues[1])

    def test_shape_baseline_failure_is_reported_and_stops_changed_file_scan(self) -> None:
        validator = _load_validator()
        args = SimpleNamespace(
            baseline_ref="HEAD",
            changed_files=("Infrastructure/scripts/validation-and-linting/verify_ask_cli_modularity.py",),
            staged_source=False,
        )
        with unittest.mock.patch.object(
            validator,
            "_shape_baseline",
            side_effect=RuntimeError("wrapper unavailable"),
        ):
            issues = validator._check_python_shape(args)

        self.assertEqual(len(issues), 1)
        self.assertIn("shape baseline unavailable", issues[0])

    def test_shape_baseline_uses_git_without_executing_worktree_cli(self) -> None:
        validator = _load_validator()
        completed = subprocess.CompletedProcess

        def git_result(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            self.assertEqual(command[0], "git")
            self.assertEqual(kwargs["cwd"], REPO_ROOT)
            if command[1] == "diff":
                return completed(command, 0, "deleted.py\nnotes.txt\n", "")
            if command[1] == "ls-tree":
                return completed(command, 0, "Infrastructure/tests/sibling.py\n", "")
            return completed(command, 0, "def baseline():\n    pass\n", "")

        with unittest.mock.patch.object(validator.subprocess, "run", side_effect=git_result) as run:
            baseline = validator._shape_baseline(REPO_ROOT / "Infrastructure/tests/current.py", "BASE")

        self.assertEqual(baseline["deleted_python_paths"], ["deleted.py"])
        self.assertEqual(baseline["sibling_python_paths"], ["Infrastructure/tests/sibling.py"])
        self.assertEqual(set(baseline["head_text"]), {"deleted.py", "Infrastructure/tests/sibling.py"})
        self.assertEqual(run.call_count, 4)
        self.assertIn(
            unittest.mock.call(
                ["git", "ls-tree", "-r", "--name-only", "BASE", "--", "Infrastructure/tests"],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            ),
            run.call_args_list,
        )
        self.assertNotIn("ls-files", [call.args[0][1] for call in run.call_args_list])

    def test_moved_function_metrics_reuses_loaded_parent_baseline(self) -> None:
        validator = _load_validator()
        current_path = REPO_ROOT / "Infrastructure/tests/current.py"
        baseline = {
            "deleted_python_paths": ["Infrastructure/tests/deleted.py"],
            "sibling_python_paths": ["Infrastructure/tests/test_ask_cli_shape.py"],
            "head_text": {
                "Infrastructure/tests/deleted.py": "def moved():\n    return 1\n",
                "Infrastructure/tests/test_ask_cli_shape.py": "def sibling():\n    return 1\n",
            },
        }

        with unittest.mock.patch.object(validator, "_shape_baseline") as load_baseline:
            metrics = validator._moved_function_metrics(current_path, baseline)

        self.assertEqual(metrics, {"moved": (2, 1)})
        load_baseline.assert_not_called()

    def test_moved_function_metrics_disambiguates_duplicate_names_by_syntax(self) -> None:
        validator = _load_validator()
        current_path = REPO_ROOT / "Infrastructure/tests/current.py"
        current = "def main(value):\n    if value:\n        return 1\n    return 0\n"
        baseline = {
            "deleted_python_paths": [
                "Infrastructure/tests/first.py",
                "Infrastructure/tests/second.py",
            ],
            "sibling_python_paths": [],
            "head_text": {
                "Infrastructure/tests/first.py": current,
                "Infrastructure/tests/second.py": "def main(value):\n    return value + 1\n",
            },
        }

        metrics = validator._moved_function_metrics(current_path, baseline, current)

        self.assertEqual(metrics, {"main": (4, 2)})

    def test_moved_function_metrics_rejects_ambiguous_names_without_exact_match(self) -> None:
        validator = _load_validator()
        current_path = REPO_ROOT / "Infrastructure/tests/current.py"
        current = "def main(value):\n    if value:\n        return 1\n    return 0\n"
        baseline = {
            "deleted_python_paths": [
                "Infrastructure/tests/first.py",
                "Infrastructure/tests/second.py",
            ],
            "sibling_python_paths": [],
            "head_text": {
                "Infrastructure/tests/first.py": "def main(value):\n    return value - 1\n",
                "Infrastructure/tests/second.py": "def main(value):\n    return value + 1\n",
            },
        }

        metrics = validator._moved_function_metrics(current_path, baseline, current)

        self.assertEqual(metrics, {})

    def test_python_shape_passes_loaded_baseline_to_move_scan(self) -> None:
        validator = _load_validator()
        args = SimpleNamespace(
            baseline_ref="BASE",
            changed_files=("Infrastructure/tests/test_ask_cli_shape.py",),
            staged_source=False,
        )
        shape_baseline = {
            "deleted_python_paths": [],
            "sibling_python_paths": [],
            "head_text": {},
        }

        with (
            unittest.mock.patch.object(validator, "_shape_baseline", return_value=shape_baseline) as load_baseline,
            unittest.mock.patch.object(validator, "_check_file_size"),
            unittest.mock.patch.object(validator, "_check_function_shape") as check_function_shape,
        ):
            issues = validator._check_python_shape(args)

        self.assertEqual(issues, [])
        load_baseline.assert_called_once_with(
            REPO_ROOT / "Infrastructure/tests/test_ask_cli_shape.py",
            "BASE",
            staged_source=False,
        )
        check_function_shape.assert_called_once_with(
            REPO_ROOT / "Infrastructure/tests/test_ask_cli_shape.py",
            (REPO_ROOT / "Infrastructure/tests/test_ask_cli_shape.py").read_text(encoding="utf-8"),
            None,
            args,
            issues,
            shape_baseline,
        )

    def test_python_shape_reads_staged_source_against_head(self) -> None:
        validator = _load_validator()
        path = REPO_ROOT / "Infrastructure/tests/test_ask_cli_shape.py"
        args = SimpleNamespace(
            baseline_ref=None,
            changed_files=(path.relative_to(REPO_ROOT).as_posix(),),
            staged_source=True,
        )
        shape_baseline = {"deleted_python_paths": [], "sibling_python_paths": [], "head_text": {}}

        with (
            unittest.mock.patch.object(validator, "_staged_paths", return_value=frozenset({args.changed_files[0]})),
            unittest.mock.patch.object(validator, "_current_source", return_value="def staged():\n    return 1\n") as source,
            unittest.mock.patch.object(validator, "_shape_baseline", return_value=shape_baseline) as baseline,
            unittest.mock.patch.object(validator, "_check_file_size"),
            unittest.mock.patch.object(validator, "_check_function_shape"),
        ):
            issues = validator._check_python_shape(args)

        self.assertEqual(issues, [])
        source.assert_called_once_with(path, staged_source=True)
        baseline.assert_called_once_with(path, "HEAD", staged_source=True)

    def test_python_shape_checks_staged_file_missing_from_worktree(self) -> None:
        validator = _load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            self._prepare_staged_missing_worktree_fixture(root)
            args = SimpleNamespace(
                baseline_ref=None,
                changed_files=("staged_only.py",),
                max_complexity=12,
                max_file_lines=800,
                max_function_lines=40,
                staged_source=True,
            )

            with unittest.mock.patch.object(validator, "REPO_ROOT", root):
                issues = validator._check_python_shape(args)

        self.assertEqual(
            issues,
            ["staged_only.py:oversized exceeds function line budget (41 > 40)"],
        )

    def test_python_shape_skips_staged_deletion(self) -> None:
        validator = _load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            self._prepare_staged_deletion_fixture(root)
            args = SimpleNamespace(
                baseline_ref=None,
                changed_files=("deleted.py",),
                max_complexity=12,
                max_file_lines=800,
                max_function_lines=40,
                staged_source=True,
            )
            with unittest.mock.patch.object(validator, "REPO_ROOT", root):
                issues = validator._check_python_shape(args)

        self.assertEqual(issues, [])

    @staticmethod
    def _prepare_staged_missing_worktree_fixture(root: Path) -> None:
        subprocess.run(("git", "init", "-q"), cwd=root, check=True)
        (root / "baseline.py").write_text("VALUE = 1\n", encoding="utf-8")
        subprocess.run(("git", "add", "baseline.py"), cwd=root, check=True)
        subprocess.run(
            (
                "git",
                "-c",
                "user.name=Structural Test",
                "-c",
                "user.email=structural@example.invalid",
                "commit",
                "-qm",
                "test: establish baseline",
            ),
            cwd=root,
            check=True,
        )
        staged_path = root / "staged_only.py"
        staged_path.write_text("def oversized():\n" + "    value = 1\n" * 40, encoding="utf-8")
        subprocess.run(("git", "add", "staged_only.py"), cwd=root, check=True)
        staged_path.unlink()

    @staticmethod
    def _prepare_staged_deletion_fixture(root: Path) -> None:
        subprocess.run(("git", "init", "-q"), cwd=root, check=True)
        deleted_path = root / "deleted.py"
        deleted_path.write_text("VALUE = 1\n", encoding="utf-8")
        subprocess.run(("git", "add", "deleted.py"), cwd=root, check=True)
        subprocess.run(
            (
                "git",
                "-c",
                "user.name=Structural Test",
                "-c",
                "user.email=structural@example.invalid",
                "commit",
                "-qm",
                "test: establish deletion baseline",
            ),
            cwd=root,
            check=True,
        )
        subprocess.run(("git", "rm", "-q", "deleted.py"), cwd=root, check=True)

    def test_default_baseline_uses_merge_base_for_committed_branch_changes(self) -> None:
        validator = _load_validator()
        completed = subprocess.CompletedProcess

        def git_result(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            self.assertEqual(command[:3], ["git", "merge-base", "HEAD"])
            if command[3] == "origin/main":
                return completed(command, 0, "base-sha\n", "")
            return completed(command, 1, "", "missing")

        with unittest.mock.patch.object(validator.subprocess, "run", side_effect=git_result):
            baseline = validator._default_baseline_ref()

        self.assertEqual(baseline, "base-sha")

    def test_python_shape_reuses_one_baseline_per_parent(self) -> None:
        validator = _load_validator()
        paths = (
            REPO_ROOT / "Infrastructure/tests/test_ask_cli_shape.py",
            REPO_ROOT / "Infrastructure/tests/test_git_metadata_preflight.py",
        )
        args = SimpleNamespace(
            baseline_ref="BASE",
            changed_files=tuple(path.relative_to(REPO_ROOT).as_posix() for path in paths),
            staged_source=False,
        )
        shape_baseline = {"deleted_python_paths": [], "sibling_python_paths": [], "head_text": {}}

        with (
            unittest.mock.patch.object(validator, "_shape_baseline", return_value=shape_baseline) as baseline,
            unittest.mock.patch.object(validator, "_check_file_size"),
            unittest.mock.patch.object(validator, "_check_function_shape"),
        ):
            issues = validator._check_python_shape(args)

        self.assertEqual(issues, [])
        baseline.assert_called_once_with(paths[0], "BASE", staged_source=False)


if __name__ == "__main__":
    unittest.main()
