import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = (
    REPO_ROOT / "Infrastructure" / "scripts" / "runtime-separation" / "build_runtime_separation_current.py"
)


def _load_runtime_separation_module():
    spec = importlib.util.spec_from_file_location("build_runtime_separation_current", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module spec from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestBuildRuntimeSeparationCurrent(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_runtime_separation_module()

    def test_collect_plugin_targets_merges_doctor_and_baseline(self) -> None:
        baseline = {
            "summary": {
                "command_checks": {
                    "plugins_status": {
                        "skill-factory": {},
                    }
                }
            }
        }
        doctor_fields = {
            "installed_plugins": [{"name": " github "}, {"name": "skill-factory"}],
            "activation_plugins": [{"name": "openai-docs"}, {"name": "github"}],
        }

        targets = self.module._collect_plugin_targets(baseline, doctor_fields)

        self.assertEqual(targets, ["github", "openai-docs", "skill-factory"])

    def test_collect_plugin_targets_falls_back_when_empty(self) -> None:
        targets = self.module._collect_plugin_targets({}, {})
        self.assertEqual(
            targets,
            ["coderabbit", "harness-engineering", "openai-curated", "plugin-factory", "skill-factory"],
        )

    def test_nonzero_command_checks_become_structured_issues(self) -> None:
        checks = {
            "repo_doctor_catalog": {
                "blocker_id": "catalog:abc123",
                "drift_class": "command_exit_nonzero",
                "normalized_fields": {
                    "decision_status": "blocked_catalog_parity",
                },
                "returncode": 2,
            }
        }

        issues = [
            self.module._command_check_issue(check_name, check)
            for check_name, check in checks.items()
            if isinstance(check, dict) and not self.module._command_check_passed_or_skipped(check)
        ]

        self.assertEqual(
            issues,
            [
                {
                    "check": "repo_doctor_catalog",
                    "returncode": 2,
                    "drift_class": "command_exit_nonzero",
                    "decision_status": "blocked_catalog_parity",
                    "blocker_id": "catalog:abc123",
                }
            ],
        )

    def test_recursive_guard_returncode_is_skipped_only_with_skip_status(self) -> None:
        skipped = {
            "returncode": self.module.SKIPPED_RETURN_CODE,
            "normalized_fields": {"status": "not_run_recursive_guard"},
        }
        failed = {
            "returncode": self.module.SKIPPED_RETURN_CODE,
            "normalized_fields": {"status": "error"},
        }

        self.assertTrue(self.module._command_check_passed_or_skipped(skipped))
        self.assertFalse(self.module._command_check_passed_or_skipped(failed))

    def test_runtime_commands_use_public_python_selecting_wrapper(self) -> None:
        self.assertEqual(
            self.module._public_ask_command("repo", "status", "--json"),
            ["bin/ask", "repo", "status", "--json"],
        )
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertNotIn('["Infrastructure/bin/ask"', source)


if __name__ == "__main__":
    unittest.main()
