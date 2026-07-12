from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date
from pathlib import Path
from types import ModuleType


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
    def test_new_public_interface_with_six_parameters_is_rejected(self) -> None:
        validator = _load_validator()
        issues = validator._check_source(
            "Infrastructure/scripts/example.py",
            "def publish(a, b, c, d, e, f):\n    return None\n",
            None,
        )
        self.assertIn("publish public interface is too wide", "\n".join(issues))

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

    def test_waiver_metadata_is_required_and_expiry_is_enforced(self) -> None:
        validator = _load_validator()
        self.assertIn(
            "missing field(s): ticket",
            validator._check_waiver_metadata(
                {
                    "Infrastructure/scripts/example.py:broad-exception": {
                        "owner": "tests",
                        "rule_id": "program-design",
                        "reason": "fixture",
                        "expires": "2099-01-01",
                    }
                },
                validation_date=date(2026, 7, 12),
            )[0],
        )
        self.assertIn(
            "expired on 2020-01-01",
            validator._check_waiver_metadata(
                {
                    "Infrastructure/scripts/example.py:broad-exception": {
                        "owner": "tests",
                        "rule_id": "program-design",
                        "ticket": "TEST-1",
                        "reason": "fixture",
                        "expires": "2020-01-01",
                    }
                },
                validation_date=date(2026, 7, 12),
            )[0],
        )

    def test_valid_waiver_suppresses_only_the_registered_rule(self) -> None:
        validator = _load_validator()
        source = "def run(value, enabled=False):\n    try:\n        return value\n    except Exception:\n        return None\n"
        waivers = {
            "Infrastructure/scripts/example.py:boolean-flag:run:enabled": {
                "owner": "tests",
                "rule_id": "program-design",
                "ticket": "TEST-2",
                "reason": "fixture",
                "expires": "2099-01-01",
            }
        }
        issues = validator._check_source("Infrastructure/scripts/example.py", source, "", waivers=waivers)
        rendered = "\n".join(issues)
        self.assertNotIn("boolean flag argument", rendered)
        self.assertIn("broad exception handler", rendered)

    def test_finding_identity_ignores_line_shifts(self) -> None:
        validator = _load_validator()
        source = "def run(value):\n    try:\n        return value\n    except Exception:\n        return None\n"

        self.assertEqual(validator._check_source("Infrastructure/scripts/example.py", "\n" + source, source), [])

    def test_waiver_is_scoped_to_one_finding(self) -> None:
        validator = _load_validator()
        source = "def run(value, enabled=False, verbose=False):\n    return value\n"
        waivers = {
            "Infrastructure/scripts/example.py:boolean-flag:run:enabled": {
                "owner": "tests",
                "rule_id": "program-design",
                "ticket": "TEST-3",
                "reason": "fixture",
                "expires": "2099-01-01",
            }
        }

        issues = validator._check_source("Infrastructure/scripts/example.py", source, "", waivers=waivers)

        self.assertNotIn("run(enabled=bool)", "\n".join(issues))
        self.assertIn("run(verbose=bool)", "\n".join(issues))

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

    def test_extensionless_python_entrypoint_is_selected(self) -> None:
        validator = _load_validator()
        with self.subTest("python shebang"):
            path = REPO_ROOT / "Infrastructure" / "bin" / "ask"
            self.assertTrue(validator._is_production_python("Infrastructure/bin/ask", path=path))


if __name__ == "__main__":
    unittest.main()
