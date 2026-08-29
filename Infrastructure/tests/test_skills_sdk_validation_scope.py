from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATE_ALL_IMPL = REPO_ROOT / "Infrastructure" / "scripts" / "validate_all_impl.sh"
VALIDATOR_PATH = (
    REPO_ROOT
    / "Infrastructure"
    / "scripts"
    / "validation-and-linting"
    / "validate_skills_sdk_typed_artifacts.py"
)


def _load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_skills_sdk_typed_artifacts", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load Skills SDK typed artifact validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestSkillsSdkValidationScope(unittest.TestCase):
    def setUp(self) -> None:
        self.impl_text = VALIDATE_ALL_IMPL.read_text(encoding="utf-8")
        self.validator = _load_validator()

    def test_validate_all_accepts_dedicated_skills_sdk_scope(self) -> None:
        self.assertIn("check|skills-sdk|consistency-advisory", self.impl_text)
        self.assertIn("skills-sdk)", self.impl_text)
        self.assertIn("skills-sdk-typed-artifacts)", self.impl_text)

    def test_validate_all_schedules_skills_sdk_typed_artifact_check(self) -> None:
        self.assertIn("schedule_check required skills-sdk-typed-artifacts", self.impl_text)
        self.assertIn("validate_skills_sdk_typed_artifacts.py --repo-root .", self.impl_text)

    def test_staged_source_scope_reads_extensionless_shebang_from_index(self) -> None:
        self.assertIn('if [[ "$staged_source_mode" -eq 1 ]]; then', self.impl_text)
        self.assertIn('git show ":$changed_file"', self.impl_text)
        self.assertIn('head -c "$shebang_probe_bytes"', self.impl_text)
        self.assertIn("LC_ALL=C sed -n '1p'", self.impl_text)
        self.assertIn('"${probe_status[probe_index]}" -eq 141', self.impl_text)
        self.assertIn('source_has_python_shebang "$changed_file"', self.impl_text)
        self.assertNotIn('staged_source_line="$(', self.impl_text)

    def test_head_source_scope_reads_extensionless_shebang_from_head(self) -> None:
        self.assertIn('elif [[ "$head_source_mode" -eq 1 ]]; then', self.impl_text)
        self.assertIn('git show "HEAD:$changed_file"', self.impl_text)

    def test_changed_file_classifier_matches_required_sdk_surfaces(self) -> None:
        expected_matches = (
            "Infrastructure/config/schemas/skills-sdk/install-receipt.v1.schema.json",
            "Infrastructure/scripts/lib/ask/skills_sdk/typed_contracts.py",
            "Infrastructure/scripts/lib/ask/envelope.py",
            "Infrastructure/scripts/lib/ask/commands/skills_impl.py",
            "Infrastructure/tests/test_skills_sdk_schema_spine.py",
            "Infrastructure/tests/fixtures/skills_sdk/typed_artifacts/fixture-manifest.json",
            ".harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md",
            ".harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-execution-plan.md",
            ".harness/implementation-notes/2026-06-04-skills-sdk-v1-0-product-implementation-notes.html",
            "artifacts/recommended-skills-sdk-pipeline.html",
        )

        for path in expected_matches:
            with self.subTest(path=path):
                self.assertTrue(self.validator.is_skills_sdk_changed_path(path))

    def test_changed_file_classifier_rejects_unrelated_surfaces(self) -> None:
        unrelated = (
            "README.md",
            "Docs/agents/04-validation.md",
            "Infrastructure/tests/test_ask_repo_validate.py",
            "artifacts/random-report.html",
            "Skills/agent-ops/simplify/SKILL.md",
        )

        for path in unrelated:
            with self.subTest(path=path):
                self.assertFalse(self.validator.is_skills_sdk_changed_path(path))

    def test_unknown_scope_still_fails_closed(self) -> None:
        result = subprocess.run(
            ["bash", str(VALIDATE_ALL_IMPL), "--scope", "skills-sdk-misspelled", "--ephemeral"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown validation scope 'skills-sdk-misspelled'", result.stderr)


if __name__ == "__main__":
    unittest.main()
