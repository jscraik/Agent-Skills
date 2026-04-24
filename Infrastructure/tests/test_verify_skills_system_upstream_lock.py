import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = (
    REPO_ROOT
    / "Infrastructure"
    / "scripts"
    / "validation-and-linting"
    / "verify_skills_system_upstream_lock.py"
)


def load_verify_lock_module():
    spec = importlib.util.spec_from_file_location("verify_skills_system_upstream_lock", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VerifySkillsSystemUpstreamLockTests(unittest.TestCase):
    def test_local_compatibility_overrides_accepts_structured_override(self) -> None:
        module = load_verify_lock_module()
        payload = {
            "local_compatibility_overrides": [
                {
                    "surface": "openai-docs",
                    "mcp_server": "openaiDeveloperDocs",
                    "tool_prefix": "mcp__openaiDeveloperDocs__",
                }
            ]
        }
        issues: list[str] = []
        module._validate_local_compatibility_overrides(payload, issues)  # pylint: disable=protected-access
        self.assertEqual(issues, [])

    def test_local_compatibility_overrides_rejects_misaligned_tool_prefix(self) -> None:
        module = load_verify_lock_module()
        payload = {
            "local_compatibility_overrides": [
                {
                    "surface": "openai-docs",
                    "mcp_server": "openaiDeveloperDocs",
                    "tool_prefix": "mcp__wrongServer__",
                }
            ]
        }
        issues: list[str] = []
        module._validate_local_compatibility_overrides(payload, issues)  # pylint: disable=protected-access
        self.assertTrue(any("tool_prefix must align with mcp_server" in issue for issue in issues))

    def test_local_compatibility_overrides_rejects_non_string_surface(self) -> None:
        module = load_verify_lock_module()
        payload = {
            "local_compatibility_overrides": [
                {
                    "surface": 123,
                    "mcp_server": "openaiDeveloperDocs",
                    "tool_prefix": "mcp__openaiDeveloperDocs__",
                }
            ]
        }
        issues: list[str] = []
        module._validate_local_compatibility_overrides(payload, issues)  # pylint: disable=protected-access
        self.assertTrue(len(issues) > 0)
        self.assertTrue(any("surface must be a string" in issue for issue in issues))

    def test_local_compatibility_overrides_rejects_non_string_mcp_server(self) -> None:
        module = load_verify_lock_module()
        payload = {
            "local_compatibility_overrides": [
                {
                    "surface": "openai-docs",
                    "mcp_server": None,
                    "tool_prefix": "mcp__openaiDeveloperDocs__",
                }
            ]
        }
        issues: list[str] = []
        module._validate_local_compatibility_overrides(payload, issues)  # pylint: disable=protected-access
        self.assertTrue(len(issues) > 0)
        self.assertTrue(any("mcp_server must be a string" in issue for issue in issues))

    def test_local_compatibility_overrides_rejects_non_string_tool_prefix(self) -> None:
        module = load_verify_lock_module()
        payload = {
            "local_compatibility_overrides": [
                {
                    "surface": "openai-docs",
                    "mcp_server": "openaiDeveloperDocs",
                    "tool_prefix": {},
                }
            ]
        }
        issues: list[str] = []
        module._validate_local_compatibility_overrides(payload, issues)  # pylint: disable=protected-access
        self.assertTrue(len(issues) > 0)
        self.assertTrue(any("tool_prefix must be a string" in issue for issue in issues))

    def test_local_compatibility_overrides_rejects_multiple_non_string_types(self) -> None:
        module = load_verify_lock_module()
        payload = {
            "local_compatibility_overrides": [
                {
                    "surface": 1,
                    "mcp_server": None,
                    "tool_prefix": {},
                }
            ]
        }
        issues: list[str] = []
        module._validate_local_compatibility_overrides(payload, issues)  # pylint: disable=protected-access
        self.assertTrue(len(issues) >= 3)
        self.assertTrue(any("surface must be a string" in issue for issue in issues))
        self.assertTrue(any("mcp_server must be a string" in issue for issue in issues))
        self.assertTrue(any("tool_prefix must be a string" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
