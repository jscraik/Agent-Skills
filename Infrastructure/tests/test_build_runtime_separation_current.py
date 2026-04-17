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


if __name__ == "__main__":
    unittest.main()
