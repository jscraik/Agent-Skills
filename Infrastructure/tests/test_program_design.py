from __future__ import annotations

import importlib.util
import sys
import unittest
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
                }
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
                }
            )[0],
        )

    def test_valid_waiver_suppresses_only_the_registered_rule(self) -> None:
        validator = _load_validator()
        source = "def run(value, enabled=False):\n    try:\n        return value\n    except Exception:\n        return None\n"
        waivers = {
            "Infrastructure/scripts/example.py:boolean-flag": {
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

    def test_non_production_paths_are_not_selected(self) -> None:
        validator = _load_validator()
        self.assertEqual(
            validator._changed_paths(
                ("Infrastructure/tests/example.py", "Docs/example.py", "Plugins/cache/example.py")
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
