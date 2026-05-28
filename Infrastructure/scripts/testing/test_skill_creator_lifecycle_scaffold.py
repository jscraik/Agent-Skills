#!/usr/bin/env python3
"""Regression tests for lifecycle-aware skill scaffolding."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "skills-system" / "skill-creator" / "scripts" / "init_skill.py"
DESCRIPTION_AUDIT = (
    REPO_ROOT
    / "skills-system"
    / "skill-creator"
    / "scripts"
    / "audit_skill_descriptions.py"
)


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SCRIPT), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _audit(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(DESCRIPTION_AUDIT), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class SkillCreatorLifecycleScaffoldTests(unittest.TestCase):
    def test_creates_skill_with_lifecycle_metadata_and_honest_starter_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = _run(
                "example-skill",
                "--path",
                tmpdir,
                "--description",
                "Use when a repo needs example-skill workflow help.",
                "--owner",
                "Agent Skills Team",
                "--review-cadence",
                "monthly",
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

            skill_md = Path(tmpdir) / "example-skill" / "SKILL.md"
            content = skill_md.read_text(encoding="utf-8")
            self.assertIn("lifecycle_state: incubating", content)
            self.assertIn("maturity: experimental", content)
            self.assertIn('owner: "Agent Skills Team"', content)
            self.assertIn('review_cadence: "monthly"', content)
            self.assertIn("last_reviewed:", content)
            self.assertIn("metadata_source: frontmatter", content)
            self.assertIn("## Skill Procedure", content)
            self.assertIn("## Evidence Output", content)
            self.assertIn("### Package Checks", content)
            self.assertIn("### Repo Checks", content)
            self.assertIn("### External Review", content)
            self.assertIn("## Gotchas", content)
            self.assertIn("## Deep Context", content)
            self.assertIn("## See Also", content)
            self.assertIn("**Topic map:**", content)
            self.assertIn("/tmp/ask-tessl-evals", content)
            self.assertIn("tessl.json", content)
            self.assertNotIn("[TODO:", content)
            self.assertNotIn("TODO", content)

            skill_dir = Path(tmpdir) / "example-skill"
            contract_yaml = (skill_dir / "references" / "contract.yaml").read_text(
                encoding="utf-8"
            )
            evals_yaml = (skill_dir / "references" / "evals.yaml").read_text(
                encoding="utf-8"
            )
            task_profile = json.loads(
                (skill_dir / "references" / "task-profile.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertIn("triggers:", contract_yaml)
            self.assertIn("non_goals:", contract_yaml)
            self.assertIn("risks:", contract_yaml)
            self.assertIn("rollback_procedure:", contract_yaml)
            self.assertIn("observability:", contract_yaml)
            self.assertIn("min_review_score: 95", contract_yaml)

            self.assertIn('schema_version: "2.0"', evals_yaml)
            self.assertIn('skill_name: "example-skill"', evals_yaml)
            self.assertIn("prompt-injection-pressure", evals_yaml)
            self.assertIn("tessl-staging-awareness", evals_yaml)
            self.assertIn("/tmp/ask-tessl-evals", evals_yaml)
            self.assertIn("tessl.json", evals_yaml)
            self.assertIn("should_trigger: false", evals_yaml)

            self.assertEqual(task_profile["scope_skill"], "example-skill")
            self.assertEqual(task_profile["thresholds"]["tessl_review_min"], 95)
            self.assertTrue(task_profile["openai_lint"]["openai_yaml_required"])

    def test_requires_owner_for_governed_scaffold(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = _run(
                "example-skill",
                "--path",
                tmpdir,
                "--description",
                "Use when a repo needs example-skill workflow help.",
                "--review-cadence",
                "monthly",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--owner", result.stderr)

    def test_rejects_waffly_or_non_trigger_description(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = _run(
                "example-skill",
                "--path",
                tmpdir,
                "--description",
                "Guide for creating effective skills with comprehensive specialized knowledge.",
                "--owner",
                "Agent Skills Team",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Invalid --description", result.stdout)
            self.assertIn('must start with "Use when "', result.stdout)

        with tempfile.TemporaryDirectory() as tmpdir:
            result = _run(
                "example-skill",
                "--path",
                tmpdir,
                "--description",
                "Use when a repo needs comprehensive and powerful skill workflow help.",
                "--owner",
                "Agent Skills Team",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("waffle term", result.stdout)

    def test_description_audit_reports_without_breaking_migration(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            valid_result = _run(
                "valid-skill",
                "--path",
                tmpdir,
                "--description",
                "Use when a repo needs valid skill validation, eval coverage, or release evidence.",
                "--owner",
                "Agent Skills Team",
            )
            self.assertEqual(valid_result.returncode, 0, valid_result.stderr or valid_result.stdout)

            invalid_dir = Path(tmpdir) / "invalid-skill"
            invalid_dir.mkdir()
            (invalid_dir / "SKILL.md").write_text(
                "---\n"
                "name: invalid-skill\n"
                "description: Guide for comprehensive specialized knowledge.\n"
                "---\n\n"
                "# Invalid Skill\n",
                encoding="utf-8",
            )

            report_result = _audit(tmpdir, "--repo-root", tmpdir, "--json")
            self.assertEqual(report_result.returncode, 0, report_result.stderr)
            report = json.loads(report_result.stdout)
            self.assertEqual(report["status"], "warn")
            self.assertEqual(report["summary"]["skills_checked"], 2)
            self.assertEqual(report["summary"]["pass"], 1)
            self.assertEqual(report["summary"]["fail"], 1)

            strict_result = _audit(tmpdir, "--repo-root", tmpdir, "--strict")
            self.assertEqual(strict_result.returncode, 1)
            self.assertIn("invalid-skill/SKILL.md", strict_result.stdout)


if __name__ == "__main__":
    unittest.main()
