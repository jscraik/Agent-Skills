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
SDK_STAGE_HEADINGS = [
    "When to use",
    "Required inputs",
    "Deliverables",
    "Procedure",
    "Validation",
    "Handoff",
    "Failure modes",
    "Gotchas",
    "References",
]

REMOVED_GOVERNANCE_HEADINGS = {
    "Stage Contract",
    "When not to use",
    "Preconditions",
    "Allowed writes",
    "Forbidden writes",
    "Exit criteria",
    "Execution boundaries",
    "Examples",
}


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


def _h2_headings(content: str) -> list[str]:
    return [
        line.removeprefix("## ").strip()
        for line in content.splitlines()
        if line.startswith("## ")
    ]


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
            self.assertIn("lifecycle_state: active", content)
            self.assertIn("maturity: experimental", content)
            self.assertIn('owner: "Agent Skills Team"', content)
            self.assertIn('review_cadence: "monthly"', content)
            self.assertIn("last_reviewed:", content)
            self.assertIn("metadata_source: frontmatter", content)
            self.assertIn("sdk_stage: example-skill", content)
            self.assertIn("command_visibility: orchestrator", content)
            self.assertIn("./references/source-context.yaml", content)
            self.assertEqual(SDK_STAGE_HEADINGS, _h2_headings(content))
            self.assertFalse(REMOVED_GOVERNANCE_HEADINGS.intersection(_h2_headings(content)))
            self.assertIn("### Package Checks", content)
            self.assertIn("### Repo Checks", content)
            self.assertIn("### External Review", content)
            self.assertIn("## Gotchas", content)
            self.assertIn("## References", content)
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
            source_context = (skill_dir / "references" / "source-context.yaml").read_text(
                encoding="utf-8"
            )
            openai_yaml = (skill_dir / "agents" / "openai.yaml").read_text(
                encoding="utf-8"
            )

            self.assertIn("skill: \"example-skill\"", contract_yaml)
            self.assertIn("stage: \"example-skill\"", contract_yaml)
            self.assertIn("preconditions:", contract_yaml)
            self.assertIn("allowed_writes:", contract_yaml)
            self.assertIn("forbidden_writes:", contract_yaml)
            self.assertIn("execution_boundaries:", contract_yaml)
            self.assertIn("exit_criteria:", contract_yaml)
            self.assertIn("triggers:", contract_yaml)
            self.assertIn("non_goals:", contract_yaml)
            self.assertIn("risks:", contract_yaml)
            self.assertIn("rollback_procedure:", contract_yaml)
            self.assertIn("observability:", contract_yaml)
            self.assertIn("min_review_score: 95", contract_yaml)

            self.assertIn('schema_version: "2.0"', evals_yaml)
            self.assertIn('skill: "example-skill"', evals_yaml)
            self.assertIn('stage: "example-skill"', evals_yaml)
            self.assertIn('skill_name: "example-skill"', evals_yaml)
            self.assertIn("eval_scenarios:", evals_yaml)
            self.assertIn("success_criteria:", evals_yaml)
            self.assertIn("prompt-injection-pressure", evals_yaml)
            self.assertIn("tessl-staging-awareness", evals_yaml)
            self.assertIn("/tmp/ask-tessl-evals", evals_yaml)
            self.assertIn("tessl.json", evals_yaml)
            self.assertIn("should_trigger: false", evals_yaml)

            self.assertIn("skill: \"example-skill\"", source_context)
            self.assertIn("stage: \"example-skill\"", source_context)
            self.assertIn("heading_contract: sdk-compact-stage-v1", source_context)
            self.assertIn("original_references:", source_context)
            self.assertIn("references:", source_context)
            self.assertIn("allowed_claims:", source_context)
            self.assertIn("forbidden_claims:", source_context)
            self.assertIn("freshness:", source_context)
            self.assertIn("context_budget:", source_context)
            self.assertIn("claim_scope:", source_context)
            self.assertIn("bounded_unit: true", source_context)
            self.assertEqual(task_profile["skill"], "example-skill")
            self.assertEqual(task_profile["stage"], "example-skill")
            self.assertEqual(task_profile["task_type"], "governed_sdk_stage_skill")
            self.assertIn("inputs", task_profile)
            self.assertIn("outputs", task_profile)
            self.assertIn("validation_profile", task_profile)
            self.assertEqual(task_profile["scope_skill"], "example-skill")
            self.assertEqual(task_profile["thresholds"]["tessl_review_min"], 95)
            self.assertTrue(task_profile["openai_lint"]["openai_yaml_required"])
            self.assertIn("schema_version: 1", openai_yaml)
            self.assertIn('skill: "example-skill"', openai_yaml)
            self.assertIn('stage: "example-skill"', openai_yaml)
            self.assertIn("role: governed_sdk_stage_agent", openai_yaml)
            self.assertIn("instructions:", openai_yaml)
            self.assertIn("tool_policy:", openai_yaml)
            self.assertIn("output_contract:", openai_yaml)

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
