#!/usr/bin/env python3
"""Tests for first-principles factory gate validation."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = (
    REPO_ROOT
    / "Infrastructure"
    / "scripts"
    / "validation-and-linting"
    / "validate_first_principles_gate.py"
)


def load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_first_principles_gate", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load validator module from {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


VALID_GATE = """first_principles_gate:
  desired_outcome: "Produce a focused skill."
  user_specific_constraints: ["small context"]
  copied_assumption_rejected: "Copying a broad template."
  fundamental_constraints: ["must validate"]
  smallest_effective_mechanism: "Add one skill."
  artifact_decision: "BUILD_SKILL"
  rejected_alternatives: ["plugin"]
  evidence_required: ["example workflow"]
  validation_proof: ["pytest"]
  stop_or_pivot_condition: "No repeated task."
"""


class FirstPrinciplesGateValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_validator_module()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, rel: str, body: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        return path

    def test_accepts_frontmatter_gate(self) -> None:
        path = self.write(
            "Plugins/skill-factory/skills/example/SKILL.md",
            f"---\n{VALID_GATE}---\n# Example\n",
        )

        result = self.module.validate_gate(path)

        self.assertEqual(result.status, "pass")

    def test_accepts_fenced_yaml_gate(self) -> None:
        path = self.write(
            "Plugins/skill-factory/skills/example/SKILL.md",
            f"# Example\n\n```yaml\n{VALID_GATE}```\n",
        )

        result = self.module.validate_gate(path)

        self.assertEqual(result.status, "pass")

    def test_accepts_labeled_section_gate(self) -> None:
        section = VALID_GATE.replace("first_principles_gate:\n", "")
        path = self.write(
            "Plugins/plugin-factory/skills/example/SKILL.md",
            f"# Example\n\n## First-Principles Gate\n\n{section}\n",
        )

        result = self.module.validate_gate(path)

        self.assertEqual(result.status, "pass")

    def test_missing_key_warns_by_default_and_fails_strict(self) -> None:
        path = self.write(
            "Plugins/skill-factory/skills/example/SKILL.md",
            "---\n" + VALID_GATE.replace('  validation_proof: ["pytest"]\n', "") + "---\n",
        )

        warning = self.module.validate_gate(path)
        strict = self.module.validate_gate(path, strict=True)

        self.assertEqual(warning.status, "warn")
        self.assertEqual(strict.status, "fail")
        self.assertIn("missing required fields", strict.details[0])

    def test_invalid_decision_warns(self) -> None:
        path = self.write(
            "Plugins/plugin-factory/skills/example/SKILL.md",
            f"---\n{VALID_GATE.replace('BUILD_SKILL', 'BUILD_CASTLE')}---\n",
        )

        result = self.module.validate_gate(path)

        self.assertEqual(result.status, "warn")
        self.assertIn("invalid artifact_decision", result.details[0])

    def test_placeholder_value_warns(self) -> None:
        path = self.write(
            "Plugins/skill-factory/skills/example/SKILL.md",
            f"---\n{VALID_GATE.replace('Produce a focused skill.', 'TODO')}---\n",
        )

        result = self.module.validate_gate(path)

        self.assertEqual(result.status, "warn")
        self.assertIn("blank or placeholder fields", result.details[0])

    def test_not_applicable_with_reason_passes(self) -> None:
        path = self.write(
            "Plugins/skill-factory/skills/example/SKILL.md",
            '---\nfirst_principles_gate: not_applicable\nfirst_principles_gate_reason: "metadata-only typo"\n---\n',
        )

        result = self.module.validate_gate(path)

        self.assertEqual(result.status, "pass")

    def test_not_applicable_without_reason_warns(self) -> None:
        path = self.write(
            "Plugins/plugin-factory/skills/example/SKILL.md",
            "---\nfirst_principles_gate: not_applicable\n---\n",
        )

        result = self.module.validate_gate(path)

        self.assertEqual(result.status, "warn")
        self.assertIn("not_applicable requires", result.details[0])

    def test_prose_only_first_principles_mention_is_not_evidence(self) -> None:
        path = self.write(
            "Plugins/plugin-factory/skills/example/SKILL.md",
            "# Example\n\nThis skill thinks from first principles before acting.\n",
        )

        result = self.module.validate_gate(path, strict=True)

        self.assertEqual(result.status, "fail")
        self.assertEqual(result.message, "missing first_principles_gate evidence")

    def test_archive_and_unrelated_paths_are_skipped(self) -> None:
        archive = self.write(
            "Plugins/skill-factory/fixtures/budget-archive/example/SKILL.md",
            "# Old fixture\n",
        )
        unrelated = self.write("Docs/example.md", "# Docs\n")

        archive_result = self.module.validate_gate(archive, strict=True)
        unrelated_result = self.module.validate_gate(unrelated, strict=True)

        self.assertEqual(archive_result.status, "skipped")
        self.assertEqual(unrelated_result.status, "skipped")

    def test_cli_returns_failure_only_for_strict_failures(self) -> None:
        path = self.write(
            "Plugins/skill-factory/skills/example/SKILL.md",
            "# Missing gate\n",
        )

        self.assertEqual(self.module.main([str(path)]), 0)
        self.assertEqual(self.module.main(["--strict", str(path)]), 1)


if __name__ == "__main__":
    unittest.main()
