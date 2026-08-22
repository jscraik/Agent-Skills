from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest import mock

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = REPO_ROOT / "Infrastructure/scripts/validation-and-linting/verify_program_design.py"


def _load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("verify_program_design", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load program-design validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestProgramDesign(unittest.TestCase):
    def test_exact_move_baseline_handles_invalid_current_source(self) -> None:
        validator = _load_validator()
        path = validator.REPO_ROOT / "Infrastructure/scripts/example_helper.py"
        self.assertIsNone(validator._exact_move_baseline(path, "def broken(:\n", "origin/main"))

    def test_new_public_interface_with_six_parameters_is_rejected(self) -> None:
        validator = _load_validator()
        issues = validator._check_source(
            "Infrastructure/scripts/example.py",
            "def publish(a, b, c, d, e, f):\n    return None\n",
            None,
        )
        self.assertIn("publish public interface is too wide", "\n".join(issues))

    def test_boolean_default_findings_require_aligned_arguments(self) -> None:
        validator = _load_validator()
        with pytest.raises(ValueError, match="same length"):
            validator._boolean_default_findings("run", [], [None])

    def test_existing_wide_interface_is_ratchet_only(self) -> None:
        validator = _load_validator()
        source = "def publish(a, b, c, d, e, f):\n    return None\n"
        self.assertEqual(validator._check_source("Infrastructure/scripts/example.py", source, source), [])

    def test_new_flag_broad_except_global_and_mutable_state_are_rejected(self) -> None:
        validator = _load_validator()
        issues = validator._check_source(
            "Infrastructure/scripts/example.py",
            "cache = {}\n\ndef run(value, enabled=False):\n    global cache\n    try:\n        return value\n    except Exception:\n        return None\n",
            "",
        )
        rendered = "\n".join(issues)
        self.assertIn("boolean flag argument", rendered)
        self.assertIn("broad exception handler", rendered)
        self.assertIn("global statement", rendered)
        self.assertIn("module mutable state", rendered)

    def test_tuple_unpacked_mutable_state_is_rejected(self) -> None:
        validator = _load_validator()
        issues = validator._check_source(
            "Infrastructure/scripts/example.py",
            "cache, items = {}, []\n",
            "",
        )
        rendered = "\n".join(issues)
        self.assertIn("module mutable state cache", rendered)
        self.assertIn("module mutable state items", rendered)

    def test_tuple_unpacked_mutable_state_pairs_targets_with_values(self) -> None:
        validator = _load_validator()
        issues = validator._check_source(
            "Infrastructure/scripts/example.py",
            "cache, version = {}, 1\n",
            "",
        )
        rendered = "\n".join(issues)
        self.assertIn("module mutable state cache", rendered)
        self.assertNotIn("module mutable state version", rendered)

    def test_uppercase_mutable_state_is_rejected(self) -> None:
        validator = _load_validator()
        issues = validator._check_source(
            "Infrastructure/scripts/example.py",
            "CACHE = {}\n",
            "",
        )
        self.assertIn("module mutable state CACHE", "\n".join(issues))

    def test_broad_exception_inside_tuple_is_rejected(self) -> None:
        validator = _load_validator()
        issues = validator._check_source(
            "Infrastructure/scripts/example.py",
            "def run(value):\n    try:\n        return value\n    except (ValueError, Exception):\n        return None\n",
            "",
        )
        self.assertIn("broad exception handler", "\n".join(issues))

    def test_existing_findings_are_not_repeated_when_another_file_changes(self) -> None:
        validator = _load_validator()
        source = "def run(value, enabled=False):\n    return value\n"
        self.assertEqual(validator._check_source("Infrastructure/scripts/example.py", source, source), [])

    def test_finding_identity_ignores_line_shifts(self) -> None:
        validator = _load_validator()
        source = "def run(value):\n    try:\n        return value\n    except Exception:\n        return None\n"

        self.assertEqual(validator._check_source("Infrastructure/scripts/example.py", "\n" + source, source), [])

    def test_new_duplicate_broad_exception_is_reported(self) -> None:
        validator = _load_validator()
        baseline = """try:
    first()
except Exception:
    pass
"""
        current = baseline + """
try:
    second()
except Exception:
    pass
"""

        issues = validator._check_source("Infrastructure/scripts/example.py", current, baseline)

        rendered = "\n".join(issues)
        self.assertEqual(rendered.count("broad exception handler"), 1)
        self.assertIn(":8:broad exception handler", rendered)

    def test_non_production_paths_are_not_selected(self) -> None:
        validator = _load_validator()
        self.assertEqual(
            validator._changed_paths(
                (
                    "Infrastructure/tests/example.py",
                    "Docs/example.py",
                    "Plugins/cache/example.py",
                    "Infrastructure/scripts/../../outside.py",
                )
            ),
            [],
        )

    def test_nested_module_mutable_state_and_constructors_are_rejected(self) -> None:
        validator = _load_validator()
        source = """
if True:
    cache = dict()
try:
    items = list()
except Exception:
    seen = set()
"""
        issues = validator._check_source("Infrastructure/scripts/example.py", source, "")
        rendered = "\n".join(issues)
        self.assertIn("module mutable state cache", rendered)
        self.assertIn("module mutable state items", rendered)
        self.assertIn("module mutable state seen", rendered)

    def test_qualified_defaultdict_factory_is_rejected(self) -> None:
        validator = _load_validator()
        issues = validator._check_source(
            "Infrastructure/scripts/example.py",
            "import collections\ncache = collections.defaultdict(list)\n",
            "",
        )
        self.assertIn("module mutable state cache", "\n".join(issues))

    def test_standard_mutable_collection_constructors_are_rejected(self) -> None:
        validator = _load_validator()
        issues = validator._check_source(
            "Infrastructure/scripts/example.py",
            "import collections\nfrom collections import Counter\n"
            "cache = collections.deque()\ncounts = Counter()\n",
            "",
        )
        rendered = "\n".join(issues)
        self.assertIn("module mutable state cache", rendered)
        self.assertIn("module mutable state counts", rendered)

    def test_private_helpers_are_skipped_and_public_methods_are_qualified(self) -> None:
        validator = _load_validator()
        source = """
class A:
    def run(self, enabled=False):
        return enabled

class B:
    def run(self, enabled=False):
        return enabled

def outer():
    def helper(enabled=False):
        return enabled
    return helper()
"""
        metrics = validator._metrics(source)
        self.assertEqual(set(metrics.public_parameters), {"A.run", "B.run", "outer"})
        issues = validator._check_source("Infrastructure/scripts/example.py", source, "")
        rendered = "\n".join(issues)
        self.assertIn("A.run(enabled=bool)", rendered)
        self.assertIn("B.run(enabled=bool)", rendered)
        self.assertNotIn("helper(enabled=bool)", rendered)

    def test_private_class_methods_are_skipped(self) -> None:
        validator = _load_validator()
        source = """
class _Internal:
    def run(self, enabled=False):
        return enabled

class Public:
    def run(self, enabled=False):
        return enabled
"""
        metrics = validator._metrics(source)
        self.assertEqual(set(metrics.public_parameters), {"Public.run"})
        self.assertNotIn("_Internal.run(enabled=bool)", "\n".join(
            validator._check_source("Infrastructure/scripts/example.py", source, "")
        ))

    def test_public_protocol_dunders_are_checked(self) -> None:
        validator = _load_validator()
        source = """
class CallableService:
    def __call__(self, enabled=False):
        return enabled
"""
        metrics = validator._metrics(source)
        self.assertEqual(set(metrics.public_parameters), {"CallableService.__call__"})
        self.assertIn(
            "CallableService.__call__(enabled=bool)",
            "\n".join(validator._check_source("Infrastructure/scripts/example.py", source, "")),
        )

    def test_class_attributes_are_checked_for_shared_mutable_state(self) -> None:
        validator = _load_validator()
        source = "class Registry:\n    cache = {}\n"
        self.assertIn(
            "module mutable state cache",
            "\n".join(validator._check_source("Infrastructure/scripts/example.py", source, "")),
        )

    def test_staticmethod_first_self_parameter_is_counted(self) -> None:
        validator = _load_validator()
        source = """
class Factory:
    @staticmethod
    def build(cls, a, b, c, d, e):
        return cls, a, b, c, d, e
"""
        metrics = validator._metrics(source)
        self.assertEqual(metrics.public_parameters["Factory.build"][0], 6)
        self.assertIn(
            "Factory.build public interface is too wide",
            "\n".join(validator._check_source("Infrastructure/scripts/example.py", source, "")),
        )

    def test_public_constructor_is_checked(self) -> None:
        validator = _load_validator()
        source = "class Service:\n    def __init__(self, enabled=False):\n        self.enabled = enabled\n"
        metrics = validator._metrics(source)
        self.assertEqual(set(metrics.public_parameters), {"Service.__init__"})
        self.assertIn("Service.__init__(enabled=bool)", "\n".join(validator._check_source(
            "Infrastructure/scripts/example.py", source, ""
        )))

    def test_invalid_baseline_is_a_controlled_validation_result(self) -> None:
        validator = _load_validator()
        issues = validator._check_source(
            "Infrastructure/scripts/example.py",
            "def run(value):\n    return value\n",
            "def run(:\n",
        )
        self.assertIn("baseline could not parse pre-change Python", "\n".join(issues))

    def test_invalid_git_baseline_is_rejected_before_file_scan(self) -> None:
        validator = _load_validator()
        with self.assertRaises(validator.BaselineUnavailable):
            validator._validate_baseline_ref("not-a-real-revision")

    def test_exact_helper_extraction_reuses_baseline_design_metrics(self) -> None:
        validator = _load_validator()
        original = """CACHE = {}

def publish(a, b, c, d, e, f, enabled=False):
    try:
        return enabled
    except Exception:
        return None
"""
        extracted = """from original import dependency

__all__ = ["publish"]

def publish(a, b, c, d, e, f, enabled=False):
    try:
        return enabled
    except Exception:
        return None
"""
        path = validator.REPO_ROOT / "Infrastructure/scripts/example_helper.py"

        with mock.patch.object(validator, "_baseline_sibling_sources", return_value=(original,)):
            self.assertEqual(
                validator._exact_move_baseline(path, extracted, "origin/main"),
                extracted,
            )

    def test_changed_helper_body_is_not_treated_as_an_exact_move(self) -> None:
        validator = _load_validator()
        original = """def publish(value):
    return value
"""
        changed = """def publish(value):
    return str(value)
"""
        path = validator.REPO_ROOT / "Infrastructure/scripts/example_helper.py"

        with mock.patch.object(validator, "_baseline_sibling_sources", return_value=(original,)):
            self.assertIsNone(validator._exact_move_baseline(path, changed, "origin/main"))

    def test_exact_helper_extraction_ignores_docstring_layout_cleanup(self) -> None:
        validator = _load_validator()
        original = 'def publish(value):\n    """\n    \tReturn the supplied value.   \n    """\n    return value\n'
        extracted = 'def publish(value):\n    """\n        Return the supplied value.\n    """\n    return value\n'
        path = validator.REPO_ROOT / "Infrastructure/scripts/example_helper.py"

        with mock.patch.object(validator, "_baseline_sibling_sources", return_value=(original,)):
            self.assertEqual(
                validator._exact_move_baseline(path, extracted, "origin/main"),
                extracted,
            )

    def test_exact_helper_extraction_keeps_docstring_content_significant(self) -> None:
        validator = _load_validator()
        original = 'def publish(value):\n    """Return the supplied value."""\n    return value\n'
        changed = 'def publish(value):\n    """Return a converted value."""\n    return value\n'
        path = validator.REPO_ROOT / "Infrastructure/scripts/example_helper.py"

        with mock.patch.object(validator, "_baseline_sibling_sources", return_value=(original,)):
            self.assertIsNone(validator._exact_move_baseline(path, changed, "origin/main"))

    def test_staged_source_uses_head_as_default_baseline(self) -> None:
        validator = _load_validator()
        self.assertEqual(validator._default_baseline_ref(staged_source=True), "HEAD")

    def test_head_source_uses_tracked_upstream_as_default_baseline(self) -> None:
        validator = _load_validator()
        result = mock.Mock(returncode=0, stdout="abc123\n", stderr="")
        with mock.patch.object(validator.subprocess, "run", return_value=result) as run:
            self.assertEqual(validator._default_baseline_ref(source_ref="HEAD"), "@{upstream}")

        self.assertEqual(
            run.call_args.args[0],
            ["git", "rev-parse", "--verify", "@{upstream}^{commit}"],
        )

    def test_baseline_path_uses_cached_staged_rename_map(self) -> None:
        validator = _load_validator()
        validator._rename_map.cache_clear()
        result = mock.Mock(
            returncode=0,
            stdout="R100\tInfrastructure/scripts/old.py\tInfrastructure/scripts/new.py\n",
            stderr="",
        )

        with mock.patch.object(validator.subprocess, "run", return_value=result) as run:
            self.assertEqual(
                validator._baseline_path("Infrastructure/scripts/new.py", "origin/main"),
                "Infrastructure/scripts/old.py",
            )
            self.assertEqual(
                validator._baseline_path("Infrastructure/scripts/new.py", "origin/main"),
                "Infrastructure/scripts/old.py",
            )

        self.assertEqual(run.call_count, 1)
        self.assertIn("--cached", run.call_args.args[0])

    def test_baseline_path_does_not_carry_excluded_staged_rename_baseline(self) -> None:
        validator = _load_validator()
        validator._rename_map.cache_clear()
        staged_result = mock.Mock(
            returncode=0,
            stdout="R100\tInfrastructure/tests/helper.py\tInfrastructure/scripts/helper.py\n",
            stderr="",
        )
        non_staged_result = mock.Mock(returncode=0, stdout="", stderr="")

        with mock.patch.object(validator.subprocess, "run", side_effect=[staged_result, non_staged_result]) as run:
            self.assertEqual(
                validator._baseline_path("Infrastructure/scripts/helper.py", "origin/main"),
                "Infrastructure/scripts/helper.py",
            )

        self.assertEqual(run.call_count, 2)
        self.assertIn("--cached", run.call_args_list[0].args[0])
        self.assertNotIn("--cached", run.call_args_list[1].args[0])

    def test_named_expression_module_state_is_rejected(self) -> None:
        validator = _load_validator()
        issues = validator._check_source(
            "Infrastructure/scripts/example.py",
            "if (cache := {}):\n    cache['ready'] = True\n",
            "",
        )
        self.assertIn("module mutable state cache", "\n".join(issues))

    def test_named_expression_in_definition_default_is_rejected(self) -> None:
        validator = _load_validator()
        issues = validator._check_source(
            "Infrastructure/scripts/example.py",
            "def build(value=(cache := {})):\n    return value\n",
            "",
        )
        self.assertIn("module mutable state cache", "\n".join(issues))

    def test_named_expression_in_lambda_body_is_ignored(self) -> None:
        validator = _load_validator()
        issues = validator._check_source(
            "Infrastructure/scripts/example.py",
            "factory = lambda: (items := [])\n",
            "",
        )
        self.assertNotIn("module mutable state items", "\n".join(issues))

    def test_baseline_path_falls_back_to_non_staged_rename_map(self) -> None:
        validator = _load_validator()
        validator._rename_map.cache_clear()
        staged_result = mock.Mock(returncode=0, stdout="", stderr="")
        non_staged_result = mock.Mock(
            returncode=0,
            stdout="R100\tInfrastructure/scripts/old.py\tInfrastructure/scripts/new.py\n",
            stderr="",
        )

        with mock.patch.object(validator.subprocess, "run", side_effect=[staged_result, non_staged_result]) as run:
            self.assertEqual(
                validator._baseline_path("Infrastructure/scripts/new.py", "origin/main"),
                "Infrastructure/scripts/old.py",
            )

        self.assertEqual(run.call_count, 2)
        self.assertIn("--cached", run.call_args_list[0].args[0])
        self.assertNotIn("--cached", run.call_args_list[1].args[0])

    def test_baseline_path_does_not_carry_excluded_rename_baseline(self) -> None:
        validator = _load_validator()
        validator._rename_map.cache_clear()
        staged_result = mock.Mock(returncode=0, stdout="", stderr="")
        non_staged_result = mock.Mock(
            returncode=0,
            stdout="R100\tInfrastructure/tests/helper.py\tInfrastructure/scripts/helper.py\n",
            stderr="",
        )

        with mock.patch.object(validator.subprocess, "run", side_effect=[staged_result, non_staged_result]):
            self.assertEqual(
                validator._baseline_path("Infrastructure/scripts/helper.py", "origin/main"),
                "Infrastructure/scripts/helper.py",
            )

    def test_current_source_text_reads_staged_blob(self) -> None:
        validator = _load_validator()
        validator._staged_paths.cache_clear()
        staged_listing = mock.Mock(returncode=0, stdout="Infrastructure/scripts/example.py\n", stderr="")
        index_listing = mock.Mock(
            returncode=0,
            stdout="100644 abc123 0\tInfrastructure/scripts/example.py\0",
            stderr="",
        )
        staged_source = mock.Mock(returncode=0, stdout="def run(value):\n    return value\n", stderr="")

        with mock.patch.object(
            validator.subprocess,
            "run",
            side_effect=[staged_listing, index_listing, staged_source],
        ) as run:
            source = validator._current_source_text(
                validator.REPO_ROOT / "Infrastructure/scripts/example.py",
                staged_source=True,
            )

        self.assertEqual(source, staged_source.stdout)
        self.assertIn("--cached", run.call_args_list[0].args[0])
        self.assertEqual(run.call_args_list[1].args[0], ["git", "ls-files", "--stage", "-z"])
        self.assertEqual(run.call_args_list[2].args[0], ["git", "show", ":Infrastructure/scripts/example.py"])

    def test_staged_paths_keep_only_regular_index_entries(self) -> None:
        validator = _load_validator()
        validator._staged_paths.cache_clear()
        changed = mock.Mock(
            returncode=0,
            stdout="Infrastructure/scripts/regular.py\nInfrastructure/scripts/link.py\n",
            stderr="",
        )
        index = mock.Mock(
            returncode=0,
            stdout=(
                "100644 abc123 0\tInfrastructure/scripts/regular.py\0"
                "120000 def456 0\tInfrastructure/scripts/link.py\0"
            ),
            stderr="",
        )

        with mock.patch.object(validator.subprocess, "run", side_effect=[changed, index]) as run:
            self.assertEqual(
                validator._staged_paths(),
                frozenset({"Infrastructure/scripts/regular.py"}),
            )

        self.assertIn("--diff-filter=ACMRT", run.call_args_list[0].args[0])
        self.assertEqual(run.call_args_list[1].args[0], ["git", "ls-files", "--stage", "-z"])

    def test_staged_paths_do_not_resolve_worktree_symlinks(self) -> None:
        validator = _load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            scripts = root / "Infrastructure" / "scripts"
            scripts.mkdir(parents=True)
            target = root / "target.py"
            target.write_text("VALUE = 1\n", encoding="utf-8")
            candidate = scripts / "changed.py"
            candidate.symlink_to(target)
            relpath = "Infrastructure/scripts/changed.py"
            with (
                mock.patch.object(validator, "REPO_ROOT", root),
                mock.patch.object(validator, "_staged_paths", return_value=frozenset({relpath})),
            ):
                paths = validator._changed_paths((relpath,), staged_source=True)

        self.assertEqual(paths, [candidate])

    def test_staged_symlink_is_excluded_even_when_target_is_python(self) -> None:
        validator = _load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            scripts = root / "Infrastructure" / "scripts"
            scripts.mkdir(parents=True)
            target = root / "target.py"
            target.write_text("VALUE = 1\n", encoding="utf-8")
            candidate = scripts / "changed.py"
            candidate.symlink_to(target)
            relpath = "Infrastructure/scripts/changed.py"
            with (
                mock.patch.object(validator, "REPO_ROOT", root),
                mock.patch.object(validator, "_staged_paths", return_value=frozenset()),
            ):
                paths = validator._changed_paths((relpath,), staged_source=True)

        self.assertEqual(paths, [])

    def test_current_source_text_uses_worktree_outside_staged_lane(self) -> None:
        validator = _load_validator()
        validator._staged_paths.cache_clear()
        path = validator.REPO_ROOT / "Infrastructure/scripts/example.py"
        with (
            mock.patch.object(Path, "read_text", return_value="worktree source") as read_text,
            mock.patch.object(validator.subprocess, "run") as run,
        ):
            source = validator._current_source_text(path)

        self.assertEqual(source, "worktree source")
        read_text.assert_called_once_with(encoding="utf-8")
        run.assert_not_called()

    def test_current_source_text_reads_explicit_source_revision(self) -> None:
        validator = _load_validator()
        path = validator.REPO_ROOT / "Infrastructure/scripts/example.py"
        source = mock.Mock(returncode=0, stdout="def run(value):\n    return value\n", stderr="")
        with mock.patch.object(validator.subprocess, "run", return_value=source) as run:
            result = validator._current_source_text(path, source_ref="HEAD")

        self.assertEqual(result, source.stdout)
        self.assertEqual(run.call_args.args[0], ["git", "show", "HEAD:Infrastructure/scripts/example.py"])

    def test_staged_source_selects_deleted_extensionless_python_path(self) -> None:
        validator = _load_validator()
        relpath = "Infrastructure/scripts/staged_deleted_program_design_fixture"
        path = validator.REPO_ROOT / relpath
        with (
            mock.patch.object(validator, "_staged_paths", return_value=frozenset({relpath})),
            mock.patch.object(validator, "_current_source_text", return_value="#!/usr/bin/env python3\n") as source_text,
        ):
            paths = validator._changed_paths((relpath,), staged_source=True)

        self.assertEqual(paths, [path])
        source_text.assert_called_once_with(path, staged_source=True, source_ref=None)

    def test_excluded_path_skips_source_revision_lookup(self) -> None:
        validator = _load_validator()
        relpath = "Infrastructure/references/fixtures/retired/evals.yaml"
        path = validator.REPO_ROOT / relpath

        with mock.patch.object(validator, "_current_source_text") as source_text:
            selected = validator._is_changed_production_python(
                relpath,
                path,
                frozenset(),
                staged_source=False,
                source_ref="HEAD",
            )

        self.assertFalse(selected)
        source_text.assert_not_called()

    def test_extensionless_python_entrypoint_is_selected(self) -> None:
        validator = _load_validator()
        with self.subTest("python shebang"):
            path = REPO_ROOT / "Infrastructure" / "bin" / "ask"
            self.assertTrue(validator._is_production_python("Infrastructure/bin/ask", path=path))

    def test_canonical_skills_python_scripts_are_selected(self) -> None:
        validator = _load_validator()
        self.assertTrue(validator._is_production_python("Skills/agent-ops/example/scripts/run.py"))

    def test_fixture_trees_are_not_selected_as_production_python(self) -> None:
        validator = _load_validator()
        self.assertFalse(validator._is_production_python("Plugins/harness-engineering/fixtures/scripts/run.py"))

    def test_testing_support_trees_are_not_selected_as_production_python(self) -> None:
        validator = _load_validator()
        self.assertFalse(validator._is_production_python("Infrastructure/scripts/testing/support.py"))

    def test_pyw_without_shebang_is_selected(self) -> None:
        validator = _load_validator()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pyw", encoding="utf-8") as handle:
            handle.write("# generated fixture\n")
            handle.flush()
            self.assertTrue(validator._is_production_python("Plugins/example/scripts/run.pyw", path=Path(handle.name)))


if __name__ == "__main__":
    unittest.main()
