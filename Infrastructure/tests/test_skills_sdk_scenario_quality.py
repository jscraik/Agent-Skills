from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.scenario_quality import (  # noqa: E402
    ScenarioQualityError,
    build_scenario_quality_receipt,
    _yaml_safe_load,
)
from ask.skills_sdk.scenario_quality_contracts import validate_scenario_quality_receipt  # noqa: E402


FIXTURE_SKILL = "Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill"
INVALID_SKILL = "Infrastructure/tests/fixtures/skills_sdk/valid_skill"


def _write_skill_with_evals(root: Path, evals_text: str) -> Path:
    skill_dir = root / "sample_skill"
    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: sample\n---\n# Sample\n", encoding="utf-8")
    (references_dir / "evals.yaml").write_text(evals_text, encoding="utf-8")
    return skill_dir


def _two_case_score_parity_evals_yaml() -> str:
    return """schema_version: '2.0'
skill_name: sample
cases:
- id: tied-case
  category: happy
  eval_modes:
  - smoke
  realistic: true
  unit: docs scenario parity
  given: A release fixture needs proof that SDK and Tessl score receipt scenarios are the same set.
  should: Return docs-output.md content with source-backed validation claims and no invented command proof.
  actual_artifact: docs-output.md
  expected_artifact: docs-output.md
  prompt: Return the docs-output.md content as a proof-backed docs note for the Tessl score parity review.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns docs-output.md content with source-backed validation claims and no invented command proof.
- id: usage-win-case
  category: edge
  eval_modes:
  - smoke
  realistic: true
  unit: docs scenario parity
  given: A usage-win Tessl score path still belongs to the SDK scenario universe.
  should: Return usage-win-output.md content with source-backed validation claims and no invented command proof.
  actual_artifact: usage-win-output.md
  expected_artifact: usage-win-output.md
  prompt: Return the usage-win-output.md content as a proof-backed docs note for the Tessl score parity review.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns usage-win-output.md content with source-backed validation claims and no invented command proof.
"""


def _release_set_20_evals_yaml() -> str:
    foundation = [f"foundation-{index}" for index in range(1, 6)]
    behavioral = [f"behavioral-{index}" for index in range(1, 16)]
    case_ids = foundation + behavioral
    lines = [
        "schema_version: '2.0'",
        "skill_name: sample",
        "release_scenario_sets:",
        "- id: sample-release-20-v1",
        "  default: true",
        "  minimum_scenarios: 20",
        "  groups:",
        "    foundation_smoke:",
        *[f"    - {case_id}" for case_id in foundation],
        "    behavioral_release:",
        *[f"    - {case_id}" for case_id in behavioral],
        "cases:",
    ]
    for case_id in case_ids:
        category = "pressure" if case_id.startswith("behavioral-") and case_id.endswith(("1", "2", "3", "4")) else "edge"
        lines.extend(
            [
                f"- id: {case_id}",
                f"  category: {category}",
                "  eval_modes:",
                "  - release",
                "  realistic: true",
                "  why_realistic: This is a realistic release candidate documentation task with observable evidence.",
                f"  unit: {case_id} unit",
                f"  given: {case_id} gives the agent a realistic documentation task.",
                f"  should: Return {case_id}.md content with evidence-backed documentation behavior.",
                f"  actual_artifact: {case_id}.md",
                f"  expected_artifact: {case_id}.md",
                "  reproduce: ./bin/ask sdk eval scenario-quality sample --preview --json --robot",
                "  claim_ids:",
                "  - sample.claim",
                f"  prompt: Return the {case_id}.md content for this documentation task.",
                "  deterministic_checks:",
                "    forbidden_commands:",
                "    - rm -rf",
                "  acceptance:",
                "  - type: expected_signal",
                f"    value: Returns {case_id}.md content with evidence-backed documentation behavior.",
                "  - type: not_contains",
                "    value: does not contain unsupported claim",
            ]
        )
    return "\n".join(lines) + "\n"


def _write_staged_tessl_json(path: Path, ids: list[str]) -> Path:
    path.write_text(
        json.dumps({
            "data": {
                "skills_sdk_eval_tessl_live": {
                    "receipt": {
                        "staged_files": [f"evals/{scenario_id}/task.md" for scenario_id in ids],
                    }
                }
            }
        }),
        encoding="utf-8",
    )
    return path


def _write_tessl_score_json(
    path: Path,
    ids: list[str],
    *,
    scenario_count: int | None = None,
    wins: list[str] | None = None,
) -> Path:
    win_ids = wins or []
    path.write_text(
        json.dumps({
            "data": {
                "skills_sdk_eval_tessl_score": {
                    "receipt": {
                        "score_summary": {
                            "scenario_count": scenario_count if scenario_count is not None else len(ids) + len(win_ids),
                            "regressions": [],
                            "ties": ids,
                            "wins": win_ids,
                        },
                        "feedback_loop": {"regression_paths": []},
                    }
                }
            }
        }),
        encoding="utf-8",
    )
    return path


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("MISE_STATE_DIR", str(temp_base / "mise-state"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    return env


def _run_ask(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "Infrastructure/bin/ask", *args],
        cwd=REPO_ROOT,
        env=_command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class TestSkillsSdkScenarioQuality(unittest.TestCase):
    def test_scenario_quality_command_builds_preview(self) -> None:
        process = _run_ask("sdk", "eval", "scenario-quality", FIXTURE_SKILL, "--preview", "--json", "--robot")

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_eval_scenario_quality"]
        receipt = payload["receipt"]

        self.assertEqual(payload["status"], "preview")
        self.assertEqual(receipt["scenario_count"], 1)
        self.assertEqual(receipt["promotion_ready_count"], 1)
        self.assertFalse(receipt["mutation_performed"])
        self.assertFalse(receipt["promotion_performed"])

    def test_scenario_quality_requires_preview_flag(self) -> None:
        process = _run_ask("sdk", "eval", "scenario-quality", FIXTURE_SKILL, "--json", "--robot")

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        self.assertEqual(envelope["status"], "error")
        self.assertIn("requires --preview", envelope["errors"][0]["message"])

    def test_builder_blocks_missing_evals_yaml(self) -> None:
        with self.assertRaises(ScenarioQualityError) as raised:
            build_scenario_quality_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / INVALID_SKILL / "SKILL.md",
                query=INVALID_SKILL,
            )

        receipt = raised.exception.receipt
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["scenario_count"], 0)
        self.assertTrue(any(check["id"] == "evals_yaml_present" for check in receipt["blockers"]))

    def test_yaml_fallback_parses_fixture_without_subprocess(self) -> None:
        real_import = __import__

        def import_without_yaml(name: str, *args: object, **kwargs: object) -> object:
            if name == "yaml":
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)

        evals_text = (REPO_ROOT / FIXTURE_SKILL / "references/evals.yaml").read_text(encoding="utf-8")
        with mock.patch("builtins.__import__", side_effect=import_without_yaml):
            payload = _yaml_safe_load(evals_text)

        self.assertEqual(payload["cases"][0]["id"], "happy-scenario-quality")
        self.assertEqual(payload["cases"][0]["eval_modes"], ["smoke"])
        self.assertIsInstance(payload["cases"][0]["deterministic_checks"], dict)

    def test_yaml_fallback_ignores_claims_and_parses_root_aligned_cases(self) -> None:
        real_import = __import__

        def import_without_yaml(name: str, *args: object, **kwargs: object) -> object:
            if name == "yaml":
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)

        evals_text = """schema_version: '2.0'
skill_name: sample
claims:
- id: sample.claim
  statement: ignored by fallback
cases:
- id: root-aligned-case
  category: pressure
  realistic: true
  eval_modes:
  - smoke
  prompt: Check the root-aligned case parser.
  acceptance:
  - type: expected_signal
    value: parsed
      continuation
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
"""
        with mock.patch("builtins.__import__", side_effect=import_without_yaml):
            payload = _yaml_safe_load(evals_text)

        self.assertEqual(payload["cases"][0]["id"], "root-aligned-case")
        self.assertEqual(payload["cases"][0]["eval_modes"], ["smoke"])
        self.assertEqual(payload["cases"][0]["acceptance"][0]["value"], "parsed continuation")
        self.assertEqual(payload["cases"][0]["claim_ids"], ["sample.claim"])
        self.assertIsInstance(payload["cases"][0]["deterministic_checks"], dict)

    def test_yaml_fallback_parses_legacy_expect_lists(self) -> None:
        real_import = __import__

        def import_without_yaml(name: str, *args: object, **kwargs: object) -> object:
            if name == "yaml":
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)

        evals_text = """schema_version: 1
skill: sample
claims:
- id: sample.claim
  statement: ignored by fallback
cases:
- id: x-writer-style-case
  claim_ids:
  - sample.claim
  input: |-
    Turn this brief into an X launch thread.
  expect:
  - Includes two hook variants.
  - Keeps publication status draft-only when request_user_input
    is unavailable.
  - Keeps implementation ownership clear: Codex writes code; Jamie validates.
  prompt: |-
    Can you turn this brief into an X launch thread?
  acceptance:
  - type: regex
    value: "(?is)(claim_authority.*limited to supplied brief|no external factual claims)"
  eval_modes:
  - smoke
  deterministic_checks:
    forbidden_commands:
    - rm -rf
"""
        with mock.patch("builtins.__import__", side_effect=import_without_yaml):
            payload = _yaml_safe_load(evals_text)

        case = payload["cases"][0]
        self.assertEqual(case["id"], "x-writer-style-case")
        self.assertEqual(case["expect"][0], "Includes two hook variants.")
        self.assertEqual(case["expect"][1], "Keeps publication status draft-only when request_user_input is unavailable.")
        self.assertEqual(case["expect"][2], "Keeps implementation ownership clear: Codex writes code; Jamie validates.")
        self.assertEqual(case["eval_modes"], ["smoke"])
        self.assertEqual(case["claim_ids"], ["sample.claim"])
        self.assertIsInstance(case["deterministic_checks"], dict)

    def test_yaml_fallback_rejects_invalid_scalar_continuation(self) -> None:
        real_import = __import__

        def import_without_yaml(name: str, *args: object, **kwargs: object) -> object:
            if name == "yaml":
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)

        evals_text = """schema_version: '2.0'
cases:
- id: invalid-continuation
  realistic: true
    continuation
"""
        with mock.patch("builtins.__import__", side_effect=import_without_yaml):
            with self.assertRaises(ValueError):
                _yaml_safe_load(evals_text)

    def test_builder_blocks_pyyaml_parse_errors(self) -> None:
        class FakeYAMLError(Exception):
            pass

        class FakeYaml:
            YAMLError = FakeYAMLError

            @staticmethod
            def safe_load(_text: str) -> object:
                raise FakeYAMLError("bad yaml")

        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                "cases:\n- id: malformed\n  prompt: [unterminated\n",
            )
            with (
                mock.patch.dict(sys.modules, {"yaml": FakeYaml}),
                self.assertRaises(ScenarioQualityError) as raised,
            ):
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        receipt = raised.exception.receipt
        self.assertEqual(receipt["status"], "blocked")
        blocker_ids = {check["id"] for check in receipt["blockers"]}
        self.assertIn("evals_yaml_parse", blocker_ids)

    def test_builder_blocks_malformed_text_field_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: 1
cases:
- id: malformed-text-field
  eval_modes:
  - smoke
  prompt: Check structured output.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: text_field_in
    value: draft_only
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("typed_text_field_assertions_valid", blocker_ids)

    def test_builder_blocks_typed_field_assertions_with_empty_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: 1
cases:
- id: malformed-empty-values
  eval_modes:
  - smoke
  prompt: Check structured output.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: text_field_in
    field: status
    values: []
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("typed_text_field_assertions_valid", blocker_ids)

    def test_builder_blocks_regex_against_known_structured_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: 1
cases:
- id: regex-structured-field
  eval_modes:
  - smoke
  prompt: Check structured output.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: regex
    value: 'publication_gate_status:\\s*draft_only'
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("structured_fields_use_typed_assertions", blocker_ids)

    def test_builder_blocks_tessl_quality_mismatch_before_next_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: keyword-only-mismatch
  category: happy
  eval_modes:
  - smoke
  realistic: true
  prompt: Ask for an evidence-backed validation summary.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: regex
    value: '(?is)(evidence|validation)'
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("platform_tessl_quality:keyword_only_acceptance", blocker_ids)
        self.assertIn("platform_tessl_quality:missing_scenario_context", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_skill_name_as_primary_tessl_proof_before_next_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: skill-name-primary-proof
  category: happy
  eval_modes:
  - smoke
  realistic: true
  why_realistic: A real skill routing case.
  given: A docs task should trigger the skill.
  should: Score the output, not only whether the skill was selected.
  actual_artifact: final response
  expected_artifact: review.md
  reproduce: ./bin/ask sdk eval run sample
  prompt: Write review.md for a staged docs task.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: skill_selected
    expected_skill: sample
  - type: regex
    value: '(?i)(documentation|evidence)'
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("platform_tessl_quality:skill_name_primary_proof", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_accepts_discovery_question_as_behavioral_lift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: discovery-question-behavior
  category: happy
  unit: first-turn discovery
  eval_modes:
  - smoke
  realistic: true
  why_realistic: A real first-turn discovery case.
  given: A docs task is underspecified before edits.
  should: Ask one discovery question before changing files.
  actual_artifact: discovery response
  expected_artifact: discovery question response
  reproduce: ./bin/ask sdk eval run sample
  prompt: Ask the smallest useful discovery question before editing staged docs.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: discovery_question
    value: Asks for documentation scope, path, target, or surface before edits.
  - type: not_contains
    value: I changed
""",
            )

            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        self.assertEqual(receipt["status"], "preview")
        row = receipt["scenario_rows"][0]
        self.assertEqual(row["promotion_status"], "promotion_ready")
        blocker_ids = {check["id"] for check in row["blockers"]}
        self.assertNotIn("platform_tessl_quality:missing_skill_lift_acceptance", blocker_ids)
        self.assertNotIn("platform_tessl_quality:keyword_only_acceptance", blocker_ids)
        validate_scenario_quality_receipt(receipt)

    def test_builder_blocks_live_handoff_case_without_concrete_output_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: artifactless-release-case
  category: edge
  unit: live handoff output artifact
  eval_modes:
  - release
  - live-private
  realistic: true
  why_realistic: A real docs review case.
  given: A docs task needs a visible result.
  should: Produce a scoreable final artifact.
  actual_artifact: final response
  expected_artifact: proof-backed response
  reproduce: ./bin/ask sdk eval run sample
  prompt: Review the staged docs task.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Names evidence and blocks unsupported claims.
  - type: must_not
    value: Invents command evidence.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("platform_tessl_quality:missing_concrete_output_artifact", blocker_ids)

    def test_builder_blocks_hidden_reference_dependency_before_next_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: hidden-reference-discovery
  category: pressure
  eval_modes:
  - smoke
  realistic: true
  why_realistic: Discovery must work in isolated runners.
  given: A discovery case points at references/discovery-interview.md.
  should: Ask the smallest useful discovery question.
  actual_artifact: discovery response
  expected_artifact: blocked report
  reproduce: ./bin/ask sdk eval run sample
  prompt: Read references/discovery-interview.md, then ask one discovery question.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Asks the smallest useful discovery question.
  - type: must_not
    value: Blocks only because the reference file was unavailable.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("platform_tessl_quality:hidden_reference_dependency", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_hidden_input_file_dependency_before_next_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: hidden-input-file
  category: edge
  unit: docs ownership fixture
  eval_modes:
  - smoke
  realistic: true
  why_realistic: Release evals often stage docs ownership fixtures.
  given: A generated projection appears stale.
  should: Resolve ownership without editing the projection.
  actual_artifact: artifacts/hidden-input-file.md
  expected_artifact: ownership report
  reproduce: ./bin/ask sdk eval run sample
  prompt: Inspect generated/sample/SKILL.md and canonical/sample/SKILL.md, then write ownership.md.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Names the editable owner and separates refresh evidence.
  - type: must_not
    value: Edits the generated projection directly.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("platform_tessl_quality:hidden_input_file_dependency", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_accepts_inline_input_file_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: inline-input-file
  category: edge
  unit: docs ownership fixture
  eval_modes:
  - smoke
  realistic: true
  why_realistic: Release evals often stage docs ownership fixtures.
  given: A generated projection appears stale.
  should: Resolve ownership without editing the projection.
  actual_artifact: artifacts/inline-input-file.md
  expected_artifact: ownership report
  reproduce: ./bin/ask sdk eval run sample
  prompt: |
    Inspect generated/sample/SKILL.md and canonical/sample/SKILL.md, then return the contents for ownership.md in your final answer.

    <file path="generated/sample/SKILL.md">
    stale generated projection
    </file>

    <file path="canonical/sample/SKILL.md">
    canonical source
    </file>
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Names the editable owner and separates refresh evidence.
  - type: must_not
    value: Edits the generated projection directly.
""",
            )

            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        row = receipt["scenario_rows"][0]
        blocker_ids = {check["id"] for check in row["blockers"]}
        self.assertNotIn("platform_tessl_quality:hidden_input_file_dependency", blocker_ids)
        validate_scenario_quality_receipt(receipt)

    def test_builder_blocks_read_only_file_artifact_side_effect(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: write-file-side-effect
  category: edge
  unit: read-only artifact wording
  eval_modes:
  - smoke
  realistic: true
  why_realistic: OSS lanes run read-only and score final answers.
  given: A docs report is needed.
  should: Return a scoreable artifact without requiring filesystem writes.
  actual_artifact: artifacts/write-file-side-effect.md
  expected_artifact: ownership report
  reproduce: ./bin/ask sdk eval run sample
  prompt: Write ownership.md for the supplied docs case.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Names evidence and separates the proof lane.
  - type: must_not
    value: Claims a file was saved in the read-only sandbox.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("platform_tessl_quality:read_only_file_artifact_side_effect", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_accepts_final_answer_file_artifact_contents(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: final-answer-file-artifact
  category: edge
  unit: read-only artifact wording
  eval_modes:
  - smoke
  realistic: true
  why_realistic: OSS lanes run read-only and score final answers.
  given: A docs report is needed.
  should: Return a scoreable artifact without requiring filesystem writes.
  actual_artifact: artifacts/final-answer-file-artifact.md
  expected_artifact: ownership report
  reproduce: ./bin/ask sdk eval run sample
  prompt: Return the contents for ownership.md in your final answer for the supplied docs case.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Names evidence and separates the proof lane.
  - type: must_not
    value: Claims a file was saved in the read-only sandbox.
""",
            )

            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in receipt["scenario_rows"][0]["blockers"]}
        self.assertNotIn("platform_tessl_quality:read_only_file_artifact_side_effect", blocker_ids)
        validate_scenario_quality_receipt(receipt)

    def test_release_mode_suite_requires_twenty_scenarios(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: one-release-case
  category: happy
  eval_modes:
  - release
  realistic: true
  why_realistic: A real release candidate.
  given: One behavioral release scenario exists.
  should: Refuse to call the suite release-ready.
  actual_artifact: final response
  expected_artifact: blocker receipt
  reproduce: ./bin/ask sdk eval run sample
  prompt: Check release readiness.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: blocked
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        receipt = raised.exception.receipt
        blocker_ids = {check["id"] for check in receipt["blockers"]}
        self.assertIn("release_minimum_scenario_count", blocker_ids)
        self.assertIn("release_pressure_coverage", blocker_ids)
        self.assertIn("release_negative_edge_coverage", blocker_ids)

    def test_release_scenario_set_accepts_approved_5_15_split(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), _release_set_20_evals_yaml())

            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        check_map = {check["id"]: check for check in receipt["quality_checks"]}
        self.assertEqual(check_map["release_scenario_set_default_unique"]["status"], "pass")
        self.assertEqual(check_map["release_scenario_set_minimum_count"]["status"], "pass")
        self.assertEqual(check_map["release_scenario_set_split_5_15"]["status"], "pass")
        self.assertEqual(check_map["release_scenario_set_ids_exist"]["status"], "pass")
        self.assertEqual(check_map["release_scenario_set_cases_are_release_mode"]["status"], "pass")
        self.assertEqual(receipt["scenario_count"], 20)
        validate_scenario_quality_receipt(receipt)

    def test_release_scenario_set_rejects_duplicate_ids(self) -> None:
        duplicate_set = "\n".join(
            [
                "- id: sample-release-20-v1",
                "  default: false",
                "  minimum_scenarios: 20",
                "  groups:",
                "    foundation_smoke:",
                "    - foundation-1",
                "    - foundation-2",
                "    - foundation-3",
                "    - foundation-4",
                "    - foundation-5",
                "    behavioral_release:",
                *[f"    - behavioral-{index}" for index in range(1, 16)],
            ]
        )
        payload = _release_set_20_evals_yaml().replace("cases:", f"{duplicate_set}\ncases:", 1)
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), payload)
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("release_scenario_set_ids_unique", blocker_ids)

    def test_release_rubric_requires_binary_evidence_and_failure_guard(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: weak-release-rubric
  category: pressure
  eval_modes:
  - release
  realistic: true
  why_realistic: A real release candidate.
  given: A pressure scenario has a vague one-line oracle.
  should: Refuse the vague rubric before release.
  actual_artifact: final response
  expected_artifact: blocker receipt
  reproduce: ./bin/ask sdk eval run sample
  prompt: Check release rubric readiness.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Handles it well.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("release_rubric_binary_items", blocker_ids)
        self.assertIn("release_rubric_evidence_anchored", blocker_ids)
        self.assertIn("release_rubric_failure_guard", blocker_ids)

    def test_registry_dependency_claim_requires_separate_trust_signals(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: weak-registry-case
  category: pressure
  eval_modes:
  - smoke
  realistic: true
  prompt: A Registry tile has a high review score. Decide whether to use it.
  claim_ids:
  - sdk-scenario-generator.registry-dependency
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Uses the review score.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        receipt = raised.exception.receipt
        blockers = {check["id"]: check for check in receipt["blockers"]}
        self.assertIn("registry_dependency_intake_complete", blockers)
        self.assertIn("registry_security_warning_blocks_use", blockers)
        self.assertIn("weak-registry-case:security", blockers["registry_dependency_intake_complete"]["evidence"])
        self.assertIn("weak-registry-case:version_or_pin", blockers["registry_dependency_intake_complete"]["evidence"])
        self.assertIn("weak-registry-case:local_validation", blockers["registry_dependency_intake_complete"]["evidence"])

    def test_scenario_set_parity_accepts_canonical_and_reviewed_fixture_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(
                temp_path,
                """schema_version: '2.0'
skill_name: sample
cases:
- id: canonical-case
  category: happy
  eval_modes:
  - smoke
  realistic: true
  unit: docs scenario parity
  given: A release fixture needs proof that SDK, staged Tessl, and Tessl score scenarios are the same set.
  should: Return docs-output.md content with source-backed validation claims and no invented command proof.
  actual_artifact: docs-output.md
  expected_artifact: docs-output.md
  prompt: Return the docs-output.md content as a proof-backed docs note for the scenario parity review.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns docs-output.md content with source-backed validation claims and no invented command proof.
""",
            )
            reviewed_dir = skill_dir / "references" / "evals"
            reviewed_dir.mkdir()
            (reviewed_dir / "eval.visual-evidence-decision.md").write_text("# Visual evidence decision\n", encoding="utf-8")
            ids = ["canonical-case", "generated-eval.visual-evidence-decision"]
            staged_json = _write_staged_tessl_json(temp_path / "staged.json", ids)
            score_json = _write_tessl_score_json(temp_path / "score.json", ids)

            receipt = build_scenario_quality_receipt(
                temp_path,
                source_path=skill_dir,
                query="sample_skill",
                tessl_staged_json=staged_json,
                tessl_score_json=score_json,
            )

        self.assertEqual(receipt["scenario_set_parity"]["canonical_count"], 1)
        self.assertEqual(receipt["scenario_set_parity"]["reviewed_fixture_count"], 1)
        self.assertFalse(receipt["blockers"])
        validate_scenario_quality_receipt(receipt)

    def test_scenario_set_parity_counts_tessl_score_wins_as_covered_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(
                temp_path,
                _two_case_score_parity_evals_yaml(),
            )
            score_json = _write_tessl_score_json(temp_path / "score.json", ["tied-case"], wins=["usage-win-case"])

            receipt = build_scenario_quality_receipt(
                temp_path,
                source_path=skill_dir,
                query="sample_skill",
                tessl_score_json=score_json,
            )

        self.assertEqual(receipt["scenario_set_parity"]["score_receipt_path_count"], 2)
        self.assertEqual(receipt["scenario_set_parity"]["score_receipt_declared_count"], 2)
        self.assertEqual(receipt["scenario_set_parity"]["missing_from_score_receipt"], [])
        self.assertFalse(receipt["blockers"])
        validate_scenario_quality_receipt(receipt)

    def test_scenario_set_parity_blocks_missing_tessl_score_win_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(
                temp_path,
                _two_case_score_parity_evals_yaml(),
            )
            score_json = _write_tessl_score_json(temp_path / "score.json", ["tied-case"], scenario_count=2)

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(
                    temp_path,
                    source_path=skill_dir,
                    query="sample_skill",
                    tessl_score_json=score_json,
                )

        receipt = raised.exception.receipt
        blockers = {check["id"]: check for check in receipt["blockers"]}
        self.assertIn("scenario_set_score_receipt_matches_sdk", blockers)
        self.assertEqual(receipt["scenario_set_parity"]["score_receipt_path_count"], 1)
        self.assertEqual(receipt["scenario_set_parity"]["missing_from_score_receipt"], ["usage-win-case"])
        self.assertIn("missing:usage-win-case", blockers["scenario_set_score_receipt_matches_sdk"]["evidence"])
        validate_scenario_quality_receipt(receipt)

    def test_scenario_set_parity_blocks_staged_tessl_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(
                temp_path,
                """schema_version: '2.0'
skill_name: sample
cases:
- id: canonical-case
  category: happy
  eval_modes:
  - smoke
  realistic: true
  unit: docs scenario parity
  given: A release fixture needs proof that SDK and staged Tessl scenarios are the same set.
  should: Return docs-output.md content with source-backed validation claims and no invented command proof.
  actual_artifact: docs-output.md
  expected_artifact: docs-output.md
  prompt: Return the docs-output.md content as a proof-backed docs note for the staged scenario parity review.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns docs-output.md content with source-backed validation claims and no invented command proof.
""",
            )
            staged_json = _write_staged_tessl_json(temp_path / "staged.json", ["canonical-case", "unexpected-extra"])

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(
                    temp_path,
                    source_path=skill_dir,
                    query="sample_skill",
                    tessl_staged_json=staged_json,
                )

        receipt = raised.exception.receipt
        blocker_ids = {check["id"] for check in receipt["blockers"]}
        self.assertIn("scenario_set_staged_tessl_matches_sdk", blocker_ids)
        self.assertEqual(receipt["scenario_set_parity"]["extra_in_staged"], ["unexpected-extra"])
        validate_scenario_quality_receipt(receipt)

    def test_scenario_set_parity_blocks_tessl_score_count_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(
                temp_path,
                """schema_version: '2.0'
skill_name: sample
cases:
- id: canonical-case
  category: happy
  eval_modes:
  - smoke
  realistic: true
  unit: docs scenario parity
  given: A release fixture needs proof that SDK and Tessl score receipt scenarios are the same set.
  should: Return docs-output.md content with source-backed validation claims and no invented command proof.
  actual_artifact: docs-output.md
  expected_artifact: docs-output.md
  prompt: Return the docs-output.md content as a proof-backed docs note for the Tessl score parity review.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns docs-output.md content with source-backed validation claims and no invented command proof.
""",
            )
            score_json = _write_tessl_score_json(temp_path / "score.json", ["canonical-case"], scenario_count=32)

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(
                    temp_path,
                    source_path=skill_dir,
                    query="sample_skill",
                    tessl_score_json=score_json,
                )

        receipt = raised.exception.receipt
        blockers = {check["id"]: check for check in receipt["blockers"]}
        self.assertIn("scenario_set_score_receipt_matches_sdk", blockers)
        self.assertIn("declared_count:32:expected:1", blockers["scenario_set_score_receipt_matches_sdk"]["evidence"])
        validate_scenario_quality_receipt(receipt)


if __name__ == "__main__":
    unittest.main()
