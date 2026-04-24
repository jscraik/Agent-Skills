import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = (
    REPO_ROOT
    / "Infrastructure"
    / "scripts"
    / "validation-and-linting"
    / "verify_provider_policy.py"
)


def load_verify_provider_policy_module():
    spec = importlib.util.spec_from_file_location("verify_provider_policy", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VerifyProviderPolicyTests(unittest.TestCase):
    def test_matches_allowed_preserves_dot_prefixed_paths(self) -> None:
        module = load_verify_provider_policy_module()
        self.assertTrue(
            module._matches_allowed(  # pylint: disable=protected-access
                ".agents/plugins-runtime/cache/claude/session.json",
                [".agents/plugins-runtime/cache/"],
            )
        )

    def test_matches_allowed_handles_explicit_dot_slash_prefix(self) -> None:
        module = load_verify_provider_policy_module()
        self.assertTrue(
            module._matches_allowed(  # pylint: disable=protected-access
                "Infrastructure/artifacts/example.json",
                ["./Infrastructure/artifacts/"],
            )
        )


if __name__ == "__main__":
    unittest.main()
