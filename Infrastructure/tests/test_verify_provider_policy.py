import importlib.util
import json
import tempfile
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

    def test_matches_allowed_trailing_slash_matches_directory_node(self) -> None:
        module = load_verify_provider_policy_module()
        self.assertTrue(
            module._matches_allowed(  # pylint: disable=protected-access
                "Infrastructure/artifacts",
                ["Infrastructure/artifacts/"],
            )
        )

    def test_iter_repo_paths_excludes_generated_runtime_prefixes(self) -> None:
        module = load_verify_provider_policy_module()
        sampled_paths = list(module._iter_repo_paths())  # pylint: disable=protected-access
        self.assertNotIn(".agents/skills/example/SKILL.md", sampled_paths)
        self.assertFalse(any(path.startswith(".agents/") for path in sampled_paths))
        self.assertFalse(any(path.startswith(".skillsets/") for path in sampled_paths))
        self.assertFalse(any(path.startswith("Infrastructure/artifacts/") for path in sampled_paths))

    def test_build_report_requires_default_provider_in_allowed_runtime_providers(self) -> None:
        module = load_verify_provider_policy_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            policy_path = Path(tmpdir) / "provider-policy.json"
            policy_path.write_text(
                json.dumps(
                    {
                        "default_provider": "openai",
                        "allowed_runtime_providers": ["anthropic"],
                        "blocked_active_path_terms": ["claude"],
                        "allowed_path_prefixes": ["Infrastructure/artifacts/"],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(SystemExit) as context:
                module.build_report(policy_path)
            self.assertIn("must be present in 'allowed_runtime_providers'", str(context.exception))

    def test_build_report_requires_non_empty_list_fields(self) -> None:
        module = load_verify_provider_policy_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            policy_path = Path(tmpdir) / "provider-policy.json"
            policy_path.write_text(
                json.dumps(
                    {
                        "default_provider": "openai",
                        "allowed_runtime_providers": ["openai"],
                        "blocked_active_path_terms": [],
                        "allowed_path_prefixes": ["Infrastructure/artifacts/"],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(SystemExit) as context:
                module.build_report(policy_path)
            self.assertIn("blocked_active_path_terms", str(context.exception))


if __name__ == "__main__":
    unittest.main()
