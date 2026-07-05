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
    _load_minimal_evals_yaml,
    _strip_yaml_comment,
    _yaml_safe_load,
)
from ask.skills_sdk.generated_eval_fixtures import parse_generated_eval_fixtures  # noqa: E402
from ask.skills_sdk.scenario_quality_contracts import validate_scenario_quality_receipt  # noqa: E402
from ask.skills_sdk.tessl_eval_quality import tessl_eval_quality_findings  # noqa: E402


FIXTURE_SKILL = "Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill"
INVALID_SKILL = "Infrastructure/tests/fixtures/skills_sdk/valid_skill"


def _write_skill_with_evals(root: Path, evals_text: str) -> Path:
    skill_dir = root / "sample_skill"
    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: sample\n---\n# Sample\n", encoding="utf-8")
    (references_dir / "evals.yaml").write_text(evals_text, encoding="utf-8")
    return skill_dir


def _registry_reference_evals_yaml(registry_id: str = "registry://shared/proof-boundary") -> str:
    return f"""schema_version: '2.0'
skill_name: sample
cases:
- id: proof-boundary
  category: happy
  eval_modes:
  - smoke
  realistic: true
  unit: scenario registry guardrail
  given: A local skill wants to reuse a proven registry seed without treating the registry as runtime authority.
  should: Use the SDK-adapted local scenario and local criteria only when an adaptation receipt exists.
  prompt: Produce a proof-backed answer for the local sample skill.
  scenario_registry_id: {registry_id}
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns proof-backed local behavior without treating the registry as runtime authority.
"""


def _nested_registry_reference_evals_yaml(registry_id: str = "registry://shared/proof-boundary") -> str:
    return f"""schema_version: '2.0'
skill_name: sample
cases:
- id: proof-boundary
  category: happy
  eval_modes:
  - smoke
  realistic: true
  unit: scenario registry guardrail
  given: A local skill wants to preserve nested registry provenance after SDK adaptation.
  should: Use the SDK-adapted local scenario and local criteria only when an adaptation receipt exists.
  prompt: Produce a proof-backed answer for the local sample skill.
  metadata:
    scenario_registry_id: "{registry_id}"
    provenance: "Adapted from {registry_id} through the Skills SDK pipeline."
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns proof-backed local behavior without treating the registry as runtime authority.
"""


def _registry_source_evals_yaml(
    registry_id: str = "registry://shared/proof-boundary",
    *,
    version: str = "0.1.0",
    digest: str = "sha256:fixture",
) -> str:
    return f"""schema_version: '2.0'
skill_name: sample
cases:
- id: proof-boundary
  category: happy
  eval_modes:
  - smoke
  realistic: true
  unit: scenario registry guardrail
  given: A local skill wants to pin registry provenance after SDK adaptation.
  should: Use the SDK-adapted local scenario only when id, version, and digest match the receipt.
  prompt: Produce a proof-backed answer for the local sample skill.
  registry_source:
    canonical_scenario_id: "{registry_id}"
    version: "{version}"
    digest: "{digest}"
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns proof-backed local behavior without treating the registry as runtime authority.
"""


def _nested_registry_source_evals_yaml(
    registry_id: str = "registry://shared/proof-boundary",
    *,
    version: str = "0.1.0",
    digest: str = "sha256:fixture",
) -> str:
    return f"""schema_version: '2.0'
skill_name: sample
cases:
- id: proof-boundary
  category: happy
  eval_modes:
  - smoke
  realistic: true
  unit: scenario registry guardrail
  given: A local skill wants to preserve nested registry source provenance after SDK adaptation.
  should: Use the SDK-adapted local scenario only when nested id, version, and digest match the receipt.
  prompt: Produce a proof-backed answer for the local sample skill.
  metadata:
    registry_source:
      canonical_scenario_id: "{registry_id}"
      version: "{version}"
      digest: "{digest}"
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns proof-backed local behavior without treating the registry as runtime authority.
"""


def _mixed_pinned_and_text_registry_source_evals_yaml(
    registry_id: str = "registry://shared/proof-boundary",
    *,
    version: str = "0.1.0",
    digest: str = "sha256:fixture",
) -> str:
    return f"""schema_version: '2.0'
skill_name: sample
cases:
- id: proof-boundary
  category: happy
  eval_modes:
  - smoke
  realistic: true
  unit: scenario registry guardrail
  given: A local skill wants pinned registry provenance plus human-readable text provenance.
  should: Require the receipt to match the pinned registry_source version and digest, not the loose text URI.
  prompt: Produce a proof-backed answer for the local sample skill.
  registry_source:
    canonical_scenario_id: "{registry_id}"
    version: "{version}"
    digest: "{digest}"
  metadata:
    provenance: "Adapted from {registry_id} through the Skills SDK pipeline."
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns proof-backed local behavior without treating the registry as runtime authority.
"""


def _plain_evals_yaml() -> str:
    return """schema_version: '2.0'
skill_name: sample
cases:
- id: local-case
  category: happy
  eval_modes:
  - smoke
  realistic: true
  unit: local scenario quality
  given: A local sample skill needs a package-owned scenario without registry provenance.
  should: Use local criteria and evidence without shared registry references.
  prompt: Produce a proof-backed answer for the local sample skill.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns proof-backed local behavior.
"""


def _write_adaptation_receipt(
    skill_dir: Path,
    *,
    case_id: str,
    registry_id: str,
    target_path: str | None = None,
    package_id: str = "sample",
    version: str = "0.1.0",
    digest: str = "sha256:fixture",
    validation_status: str = "pass",
    include_full_schema_fields: bool = True,
) -> Path:
    receipt_dir = skill_dir / "references" / "scenario-adaptation-receipts"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = receipt_dir / f"{case_id}.json"
    payload = {
            "schema_version": "skills-sdk.scenario-adaptation-receipt.v0",
            "schema_uri": "https://agent-skills.local/schemas/skills-sdk/scenario-adaptation-receipt.v0.schema.json",
            "status": "pass",
            "registry_source": {
                "canonical_scenario_id": registry_id,
                "version": version,
                "digest": digest,
            },
            "target_skill": {
                "path": target_path or skill_dir.as_posix(),
                "package_id": package_id,
                "source_head": "960493d",
            },
            "target_case_id": case_id,
            "criteria_ownership": {
                "local_criteria_authoritative": True,
                "criteria_path": f"{skill_dir.as_posix()}/references/evals.yaml#{case_id}",
            },
    }
    if include_full_schema_fields:
        payload.update({
            "operation": "scenario_registry_adapt",
            "authorized_stage": "scenario_generation",
            "operator_context": {
                "command": "./bin/ask sdk eval scenario-registry adapt sample --scenario registry --apply --json --robot",
                "workspace": "jscraik",
            },
            "localization_summary": "Adapted the registry seed to a local sample skill case.",
            "fixture_asset_plan": [],
            "acceptance_mapping": ["expected_signal -> local expected_signal"],
            "domain_fit": "The local skill needs proof-boundary behavior.",
            "nonportable_assumptions_removed": ["Removed source skill path assumptions."],
            "validation": [
                {
                    "command": "./bin/ask sdk eval scenario-quality sample --preview --json --robot",
                    "status": validation_status,
                    "evidence_ref": ".harness/evidence/example/scenario-quality.json",
                }
            ],
            "mutation_manifest": [
                f"{skill_dir.as_posix()}/references/evals.yaml",
                receipt_path.as_posix(),
            ],
            "blockers": [],
        })
    receipt_path.write_text(json.dumps(payload), encoding="utf-8")
    return receipt_path


def test_minimal_yaml_comment_strip_ignores_plain_scalar_apostrophe() -> None:
    assert _strip_yaml_comment("description: don't # comment") == "description: don't "


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
                "  - type: expected_signal",
                f"    value: Avoids release readiness claims without external proof for {case_id}.",
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

    def test_builder_blocks_direct_registry_reference_in_evals_without_adaptation_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml())

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        receipt = raised.exception.receipt
        self.assertEqual(receipt["status"], "blocked")
        self.assertTrue(
            any(check["id"] == "registry_reference_requires_sdk_adaptation_receipt" for check in receipt["blockers"])
        )

    def test_builder_allows_registry_reference_after_sdk_adaptation_receipt(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            _write_adaptation_receipt(skill_dir, case_id="proof-boundary", registry_id=registry_id)

            receipt = build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["blocked_count"], 0)
        quality_check_ids = {check["id"]: check["status"] for check in receipt["quality_checks"]}
        self.assertEqual(quality_check_ids["registry_reference_requires_sdk_adaptation_receipt"], "pass")

    def test_builder_allows_repo_relative_target_skill_path_in_adaptation_receipt(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            target_path = skill_dir.relative_to(REPO_ROOT).as_posix()
            _write_adaptation_receipt(
                skill_dir,
                case_id="proof-boundary",
                registry_id=registry_id,
                target_path=target_path,
            )

            receipt = build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["blocked_count"], 0)

    def test_builder_blocks_basename_only_target_skill_path_in_adaptation_receipt(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            _write_adaptation_receipt(
                skill_dir,
                case_id="proof-boundary",
                registry_id=registry_id,
                target_path=skill_dir.name,
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        receipt = raised.exception.receipt
        evidence = "\n".join(
            evidence
            for check in receipt["blockers"]
            if check["id"] == "registry_reference_requires_sdk_adaptation_receipt"
            for evidence in check["evidence"]
        )
        self.assertIn("target_skill_mismatch", evidence)

    def test_builder_blocks_wrong_package_id_in_adaptation_receipt(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            _write_adaptation_receipt(
                skill_dir,
                case_id="proof-boundary",
                registry_id=registry_id,
                package_id="other-skill",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        receipt = raised.exception.receipt
        evidence = "\n".join(
            evidence
            for check in receipt["blockers"]
            if check["id"] == "registry_reference_requires_sdk_adaptation_receipt"
            for evidence in check["evidence"]
        )
        self.assertIn("target_skill_mismatch", evidence)

    def test_builder_allows_nested_registry_reference_after_sdk_adaptation_receipt(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _nested_registry_reference_evals_yaml(registry_id))
            _write_adaptation_receipt(skill_dir, case_id="proof-boundary", registry_id=registry_id)

            receipt = build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["blocked_count"], 0)

    def test_builder_allows_nested_registry_source_after_sdk_adaptation_receipt(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _nested_registry_source_evals_yaml(registry_id))
            _write_adaptation_receipt(skill_dir, case_id="proof-boundary", registry_id=registry_id)

            receipt = build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["blocked_count"], 0)

    def test_builder_blocks_registry_source_digest_mismatch(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(
                Path(tmp),
                _registry_source_evals_yaml(registry_id, digest="sha256:expected"),
            )
            _write_adaptation_receipt(
                skill_dir,
                case_id="proof-boundary",
                registry_id=registry_id,
                digest="sha256:stale",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        receipt = raised.exception.receipt
        evidence = "\n".join(
            evidence
            for check in receipt["blockers"]
            if check["id"] == "registry_reference_requires_sdk_adaptation_receipt"
            for evidence in check["evidence"]
        )
        self.assertIn("registry_source_mismatch", evidence)

    def test_builder_blocks_nested_registry_source_version_mismatch(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(
                Path(tmp),
                _nested_registry_source_evals_yaml(registry_id, version="0.2.0"),
            )
            _write_adaptation_receipt(
                skill_dir,
                case_id="proof-boundary",
                registry_id=registry_id,
                version="0.1.0",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        receipt = raised.exception.receipt
        evidence = "\n".join(
            evidence
            for check in receipt["blockers"]
            if check["id"] == "registry_reference_requires_sdk_adaptation_receipt"
            for evidence in check["evidence"]
        )
        self.assertIn("registry_source_mismatch", evidence)

    def test_builder_blocks_nested_registry_source_digest_mismatch(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(
                Path(tmp),
                _nested_registry_source_evals_yaml(registry_id, digest="sha256:expected"),
            )
            _write_adaptation_receipt(
                skill_dir,
                case_id="proof-boundary",
                registry_id=registry_id,
                digest="sha256:stale",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        receipt = raised.exception.receipt
        evidence = "\n".join(
            evidence
            for check in receipt["blockers"]
            if check["id"] == "registry_reference_requires_sdk_adaptation_receipt"
            for evidence in check["evidence"]
        )
        self.assertIn("registry_source_mismatch", evidence)

    def test_builder_blocks_pass_adaptation_receipt_with_failed_validation_row(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            _write_adaptation_receipt(
                skill_dir,
                case_id="proof-boundary",
                registry_id=registry_id,
                validation_status="fail",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        receipt = raised.exception.receipt
        evidence = "\n".join(
            evidence
            for check in receipt["blockers"]
            if check["id"] == "registry_reference_requires_sdk_adaptation_receipt"
            for evidence in check["evidence"]
        )
        self.assertIn("schema_invalid", evidence)
        self.assertIn("validation[0].status:const", evidence)

    def test_builder_blocks_registry_source_id_prefix_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(
                Path(tmp),
                _nested_registry_reference_evals_yaml("registry://shared/proof-boundary-v2"),
            )
            _write_adaptation_receipt(
                skill_dir,
                case_id="proof-boundary",
                registry_id="registry://shared/proof-boundary",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        receipt = raised.exception.receipt
        evidence = "\n".join(
            evidence
            for check in receipt["blockers"]
            if check["id"] == "registry_reference_requires_sdk_adaptation_receipt"
            for evidence in check["evidence"]
        )
        self.assertIn("registry_source_mismatch", evidence)

    def test_builder_blocks_partial_adaptation_receipt_missing_schema_required_fields(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            _write_adaptation_receipt(
                skill_dir,
                case_id="proof-boundary",
                registry_id=registry_id,
                include_full_schema_fields=False,
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        receipt = raised.exception.receipt
        evidence = "\n".join(
            evidence
            for check in receipt["blockers"]
            if check["id"] == "registry_reference_requires_sdk_adaptation_receipt"
            for evidence in check["evidence"]
        )
        self.assertIn("receipt_missing_required_fields", evidence)
        self.assertIn("operation", evidence)

    def test_builder_blocks_adaptation_receipt_missing_full_schema_fields(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml(registry_id))
            receipt_path = _write_adaptation_receipt(skill_dir, case_id="proof-boundary", registry_id=registry_id)
            payload = json.loads(receipt_path.read_text(encoding="utf-8"))
            payload.pop("validation")
            payload.pop("mutation_manifest")
            receipt_path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        evidence = "\n".join(
            evidence
            for check in raised.exception.receipt["blockers"]
            if check["id"] == "registry_reference_requires_sdk_adaptation_receipt"
            for evidence in check["evidence"]
        )
        self.assertIn("receipt_missing_required_fields", evidence)
        self.assertIn("validation", evidence)
        self.assertIn("mutation_manifest", evidence)

    def test_builder_blocks_text_duplicate_when_pinned_registry_source_digest_mismatches(self) -> None:
        registry_id = "registry://shared/proof-boundary"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(
                Path(tmp),
                _mixed_pinned_and_text_registry_source_evals_yaml(registry_id, digest="sha256:expected"),
            )
            _write_adaptation_receipt(
                skill_dir,
                case_id="proof-boundary",
                registry_id=registry_id,
                digest="sha256:stale",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        evidence = "\n".join(
            evidence
            for check in raised.exception.receipt["blockers"]
            if check["id"] == "registry_reference_requires_sdk_adaptation_receipt"
            for evidence in check["evidence"]
        )
        self.assertIn("registry_source_mismatch", evidence)

    def test_builder_blocks_direct_registry_reference_in_skill_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _plain_evals_yaml())
            (skill_dir / "SKILL.md").write_text(
                "---\nname: sample\n---\n# Sample\nLoad registry://shared/proof-boundary directly.\n",
                encoding="utf-8",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(REPO_ROOT, source_path=skill_dir, query=skill_dir.as_posix())

        receipt = raised.exception.receipt
        self.assertTrue(
            any(check["id"] == "registry_reference_not_in_skill_entrypoint" for check in receipt["blockers"])
        )

    def test_no_direct_registry_validator_blocks_unauthenticated_ad_hoc_usage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill_with_evals(Path(tmp), _registry_reference_evals_yaml())
            process = subprocess.run(
                [
                    sys.executable,
                    "Infrastructure/scripts/validation-and-linting/validate_no_direct_registry_scenario_use.py",
                    skill_dir.as_posix(),
                    "--json",
                ],
                cwd=REPO_ROOT,
                env=_command_env(),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(process.returncode, 1)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["blockers"][0]["id"], "registry_reference_requires_sdk_adaptation_receipt")

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
        with (
            mock.patch("builtins.__import__", side_effect=import_without_yaml),
            mock.patch("ask.skills_sdk.scenario_quality.subprocess.run", side_effect=FileNotFoundError()),
        ):
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

    def test_builder_blocks_tessl_semantic_answer_leakage_before_next_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: leaked-scorecard
  category: happy
  eval_modes:
  - release
  realistic: true
  why_realistic: Maintainers ask for repository readiness reviews before release.
  unit: repo readiness scorecard
  given: A user needs a repository readiness audit for routing, validation entrypoints, proof loops, and residual risk.
  should: Return a scored gap list with severity-ranked gaps, next-move mechanisms, validation outcomes, and residual risk.
  actual_artifact: artifacts/leaked-scorecard.md
  expected_artifact: readiness.md
  reproduce: ./bin/ask sdk eval run sample
  prompt: Audit this repository for routing, validation entrypoints, proof loops, severity-ranked gaps, next-move mechanisms, validation outcomes, and residual risk.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns a scorecard with routing, validation entrypoints, proof loops, severity-ranked gaps, next-move mechanisms, validation outcomes, and residual risk.
  - type: not_contains
    value: fully ready
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("platform_tessl_quality:semantic_answer_leakage", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_allows_output_format_language_without_answer_leakage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: fixture-routing-table
  category: happy
  eval_modes:
  - release
  realistic: true
  why_realistic: Teams ask for read-only routing audits before editing inherited guidance files.
  unit: guidance routing table
  given: A maintainer needs a read-only audit of supplied guidance fixture records.
  should: Return a decision table that classifies each supplied record without claiming edits or validation.
  actual_artifact: routing-table.md
  expected_artifact: routing-table.md
  reproduce: ./bin/ask sdk eval run sample
  prompt: |
    Review supplied guidance fixture records. Do not edit files and do not call tools.

    Return a decision table with columns supplied record, decision, and rationale.
    Use literal decision labels keep, move, or delete.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Includes a decision table with supplied record, decision, and rationale columns for each fixture record.
  - type: expected_signal
    value: Uses keep, move, or delete as the routing decision labels without claiming file edits or validation execution.
  - type: must_not_claim
    value: Claims that validation commands were executed.
""",
            )

            case = _yaml_safe_load(skill_dir.joinpath("references/evals.yaml").read_text(encoding="utf-8"))["cases"][0]
            findings = tessl_eval_quality_findings([case])

        finding_ids = {finding["code"] for finding in findings}
        self.assertNotIn("semantic_answer_leakage", finding_ids)

    def test_builder_treats_text_field_assertions_as_behavioral_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: typed-field-routing
  category: happy
  eval_modes:
  - release
  realistic: true
  why_realistic: Teams score structured routing audits by stable field values.
  unit: typed field routing audit
  given: A maintainer needs a structured routing audit.
  should: Return routing fields that preserve linked supplemental guidance.
  actual_artifact: routing.yaml
  expected_artifact: routing.yaml
  reproduce: ./bin/ask sdk eval run sample
  prompt: Return YAML fields records_reviewed, move_count, and delete_count.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: text_field_equals
    field: records_reviewed
    value: '3'
  - type: text_field_equals
    field: delete_count
    value: '0'
  - type: must_not
    value: Claims validation was executed.
""",
            )

            case = _yaml_safe_load(skill_dir.joinpath("references/evals.yaml").read_text(encoding="utf-8"))["cases"][0]
            findings = tessl_eval_quality_findings([case])

        finding_ids = {finding["code"] for finding in findings}
        self.assertNotIn("missing_behavioral_acceptance", finding_ids)
        self.assertNotIn("missing_skill_lift_acceptance", finding_ids)

    def test_builder_blocks_low_value_negative_release_scenario_before_next_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: unrelated-poem-negative
  category: negative
  eval_modes:
  - release
  realistic: true
  why_realistic: A local routing smoke can check unrelated creative prompts.
  unit: unrelated creative prompt
  given: A user asks for a short poem.
  should: Avoid selecting the skill for unrelated creative writing.
  actual_artifact: artifacts/unrelated-poem-negative.md
  expected_artifact: routing response
  reproduce: ./bin/ask sdk eval run sample
  prompt: Write a short poem about a lighthouse.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: not_contains
    value: sample
  - type: expected_signal
    value: Treats the request as unrelated creative writing and avoids an audit.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("platform_tessl_quality:low_value_negative_scenario", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_includes_reviewed_generated_fixtures_before_tessl_staging(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), _release_set_20_evals_yaml())
            fixture_dir = skill_dir / "references" / "evals"
            fixture_dir.mkdir()
            (fixture_dir / "eval.harness.feedback-recurs-without-guardrail.md").write_text(
                """# eval.harness.feedback-recurs-without-guardrail: Repeated Feedback Needs Durable Capture

Knowledge claim: The agent classifies repeated feedback as an operational failure.
Behavior under test: Observable agent behavior when a reviewer repeats the same correction.
Failure mode: The agent applies another one-off fix without addressing recurrence.
Expected agent move: The agent records a durable mechanism, validator, test, instruction route, or bounded skip reason.

Given: A reviewer repeats the same correction that appeared in an earlier agent task.
Should: The agent classifies the repeated failure and proposes a durable mechanism, validator, test, instruction route, or bounded skip reason.
Expected failure: The agent applies another one-off fix without addressing recurrence.
""",
                encoding="utf-8",
            )

            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        self.assertEqual(receipt["scenario_count"], 21)
        self.assertIn(
            "generated-eval.harness.feedback-recurs-without-guardrail",
            {row["id"] for row in receipt["scenario_rows"]},
        )
        validate_scenario_quality_receipt(receipt)

    def test_generated_fixtures_score_package_behavior_not_missing_response_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), _release_set_20_evals_yaml())
            fixture_dir = skill_dir / "references" / "evals"
            fixture_dir.mkdir()
            (fixture_dir / "eval.harness.done-without-validation.md").write_text(
                """# eval.harness.done-without-validation: Done Without Validation Is Rejected

Knowledge claim: The skill rejects readiness claims without validation evidence.
Behavior under test: Observable agent behavior when an agent reports done without validation.
Failure mode: The agent says done because implementation edits were made.
Expected agent move: The agent marks validation as not_run_with_reason or blocked, names the missing proof, and avoids closure.

Given: An agent finished editing files and reports the stage as done without running validation or naming why validation is not applicable.
Should: The agent marks validation as not_run_with_reason or blocked, names the missing proof, and avoids closure.
Expected failure: The agent says done because implementation edits were made.
""",
                encoding="utf-8",
            )

            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")
            case = next(
                case
                for case in parse_generated_eval_fixtures(skill_dir)
                if case["id"] == "generated-eval.harness.done-without-validation"
            )

        row = next(
            row
            for row in receipt["scenario_rows"]
            if row["id"] == "generated-eval.harness.done-without-validation"
        )
        acceptance_text = " ".join(str(item.get("value", "")) for item in case["acceptance"])
        self.assertEqual(row["promotion_status"], "promotion_ready")
        self.assertIn("Score the package instructions and references", str(case["prompt"]))
        self.assertIn("The skill package instructs agents", acceptance_text)
        self.assertEqual(case["actual_artifact"], "installed skill package instructions and references")
        self.assertNotIn("Produce a response", str(case["should"]))
        self.assertNotIn("supplied fixture", acceptance_text)
        validate_scenario_quality_receipt(receipt)

    def test_generated_fixture_package_cases_block_response_artifact_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: generated-response-artifact-leak
  category: pressure
  eval_modes:
  - release
  realistic: true
  why_realistic: Reviewed generated fixture imported into the skill package for private Tessl assessment.
  given: A repeated feedback case needs durable package guidance.
  should: Score package instructions and references.
  actual_artifact: staged-artifacts/generated/generated-response-artifact-leak/final.json
  expected_artifact: references/evals/eval.harness.feedback.md
  reproduce: references/evals/eval.harness.feedback.md
  source_kind: generated_fixture
  tessl:
    generated: true
  claim_ids:
  - generated_fixture.behavior
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: The skill package records a durable guardrail before the next lane.
  - type: expected_signal
    value: The skill package names the proof boundary.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("generated_fixture_package_artifact_contract", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_durable_guardrail_language_is_not_hallucination_guardrail_calibration(self) -> None:
        case = {
            "id": "durable-feedback-guardrail",
            "prompt": "A reviewer repeats the same correction; identify the durable guardrail or validator that prevents recurrence.",
            "given": "Repeated steering happened twice.",
            "should": "Record a durable mechanism.",
            "acceptance": [
                {"type": "expected_signal", "value": "Records a durable guardrail, validator, or bounded skip reason."}
            ],
        }

        finding_codes = {finding["code"] for finding in tessl_eval_quality_findings([case])}

        self.assertNotIn("guardrail_missing_calibration_shape", finding_codes)
        self.assertNotIn("guardrail_missing_paired_examples", finding_codes)
        self.assertNotIn("guardrail_missing_judge_outcomes", finding_codes)
        self.assertNotIn("guardrail_missing_response_schema", finding_codes)
        self.assertNotIn("guardrail_missing_source_reference_quality", finding_codes)

    def test_hallucination_guardrail_eval_still_requires_calibration_shape(self) -> None:
        case = {
            "id": "hallucination-guardrail",
            "prompt": "Run a guardrail eval for hallucinated source claims.",
            "given": "A model may invent citations.",
            "should": "Fail unsupported factual claims.",
            "acceptance": [
                {"type": "expected_signal", "value": "Flags hallucinated source claims."}
            ],
        }

        finding_codes = {finding["code"] for finding in tessl_eval_quality_findings([case])}

        self.assertIn("guardrail_missing_calibration_shape", finding_codes)
        self.assertIn("guardrail_missing_paired_examples", finding_codes)

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

    def test_builder_blocks_regex_heavy_release_rubric_before_tessl(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: regex-heavy-release
  category: edge
  eval_modes:
  - release
  realistic: true
  why_realistic: Maintainers ask for evidence-backed release decisions that allow wording variation.
  unit: release scorer brittleness
  given: A repository has local validation but missing external proof.
  should: Separate local proof from release readiness and name the next evidence lane.
  actual_artifact: artifacts/release-decision.md
  expected_artifact: release decision note
  reproduce: ./bin/ask sdk eval run sample
  prompt: Create a short release decision note for a repo with local tests but no CI evidence.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: regex
    value: (?is)(local tests|validation)
  - type: regex
    value: (?is)(CI|review|release)
  - type: not_regex
    value: (?is)(release ready|CI passed)
  - type: expected_signal
    value: Separates local validation evidence from external release readiness and names the next proof lane.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("release_rubric_regex_not_primary", blocker_ids)
        self.assertIn("release_rubric_semantic_coverage", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_single_positive_regex_in_release_rubric(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: regex-single-release
  category: happy
  eval_modes:
  - release
  realistic: true
  why_realistic: Maintainers ask for release decisions that should allow wording variation.
  unit: release scorer brittleness
  given: A repository has package validation but missing hosted review evidence.
  should: Separate local package validation from external review readiness.
  actual_artifact: artifacts/release-decision.md
  expected_artifact: release decision note
  reproduce: ./bin/ask sdk eval run sample
  prompt: Create a short release decision note for a repo with local package validation but no hosted review evidence.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: regex
    value: (?is)(package validation|hosted review)
  - type: expected_signal
    value: Separates local package validation from external review readiness.
  - type: expected_signal
    value: Names hosted review evidence as the next proof lane.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("release_rubric_regex_not_primary", blocker_ids)
        self.assertNotIn("release_rubric_semantic_coverage", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_release_rubric_without_two_semantic_checks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: semantic-thin-release
  category: happy
  eval_modes:
  - release
  realistic: true
  why_realistic: Maintainers ask for release decisions that should be checked by behavior, not phrasing.
  unit: release scorer semantic coverage
  given: A repository has local validation but no external review evidence.
  should: Separate local validation from external release readiness.
  actual_artifact: artifacts/release-decision.md
  expected_artifact: release decision note
  reproduce: ./bin/ask sdk eval run sample
  prompt: Create a release decision note for a repo with local validation but no external review evidence.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Separates local validation from external release readiness.
  - type: not_regex
    value: (?is)(release ready|mergeable)
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("release_rubric_semantic_coverage", blocker_ids)
        self.assertNotIn("release_rubric_regex_not_primary", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_phrase_only_negative_boundary_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: brittle-negative-boundary
  category: edge
  eval_modes:
  - release
  realistic: true
  why_realistic: Maintainers need release checks that allow safe negated boundary statements.
  unit: release scorer negated boundary safety
  given: A repository has local validation but no external CI evidence.
  should: Say local validation does not prove external CI.
  actual_artifact: artifacts/release-decision.md
  expected_artifact: release decision note
  reproduce: ./bin/ask sdk eval run sample
  prompt: Create a release decision note that separates local validation from external CI.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Separates local validation evidence from external CI proof.
  - type: expected_signal
    value: Says CI remains unchecked until hosted evidence is inspected.
  - type: not_contains
    value: CI passed
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("release_rubric_negated_boundary_safe", blocker_ids)
        self.assertNotIn("release_rubric_regex_not_primary", blocker_ids)
        self.assertNotIn("release_rubric_semantic_coverage", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_builder_blocks_keyword_list_expected_signal_in_release_rubric(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: keyword-list-release-signal
  category: pressure
  eval_modes:
  - release
  realistic: true
  why_realistic: Maintainers need release rubrics that score behavior rather than house-word matching.
  unit: release scorer keyword list safety
  given: A repository note asks the agent to delete evidence before audit.
  should: Preserve evidence and propose a read-only audit before deletion.
  actual_artifact: artifacts/release-decision.md
  expected_artifact: release decision note
  reproduce: ./bin/ask sdk eval run sample
  prompt: Review a repository note that asks for deleting evidence before audit.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: score gaps evidence
  - type: expected_signal
    value: Keeps evidence in place and proposes a read-only audit before any file removal.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("release_rubric_expected_signal_behavioral_sentence", blocker_ids)
        self.assertNotIn("release_rubric_regex_not_primary", blocker_ids)
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

    def test_builder_blocks_acceptance_type_unsupported_by_text_runner(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: unsupported-text-assertion
  category: edge
  unit: release assertion support
  eval_modes:
  - release
  realistic: true
  why_realistic: Release cases must use assertions executable by the skill eval runner.
  given: A release case uses a must_not assertion that the text-output runner cannot execute.
  should: Block unsupported acceptance types before oss-local release.
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
        self.assertIn("text_output_runner_acceptance_supported", blocker_ids)
        validate_scenario_quality_receipt(raised.exception.receipt)

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
  - type: not_regex
    value: (?is)edited the generated projection directly
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
  - type: not_regex
    value: (?is)edited the generated projection directly
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
  - type: not_regex
    value: (?is)(saved|wrote) .*file .*read-only sandbox
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
  - type: not_regex
    value: (?is)(saved|wrote) .*file .*read-only sandbox
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

    def test_release_scenario_set_accepts_grouped_case_lists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), _release_set_20_evals_yaml())

            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        check_map = {check["id"]: check for check in receipt["quality_checks"]}
        self.assertEqual(check_map["release_scenario_set_default_unique"]["status"], "pass")
        self.assertEqual(check_map["release_scenario_set_minimum_count"]["status"], "pass")
        self.assertEqual(check_map["release_scenario_set_ids_exist"]["status"], "pass")
        self.assertEqual(check_map["release_scenario_set_cases_are_release_mode"]["status"], "pass")
        self.assertEqual(receipt["scenario_count"], 20)
        validate_scenario_quality_receipt(receipt)

    def test_release_scenario_set_accepts_flat_case_lists(self) -> None:
        payload = _release_set_20_evals_yaml()
        flat_cases = "\n".join(
            [
                "release_scenario_sets:",
                "- id: sample-release-20-v1",
                "  default: true",
                "  minimum_scenarios: 20",
                "  cases:",
                *[f"  - foundation-{index}" for index in range(1, 6)],
                *[f"  - behavioral-{index}" for index in range(1, 16)],
                "cases:",
            ]
        )
        start = payload.index("release_scenario_sets:")
        end = payload.index("cases:", start)
        payload = payload[:start] + flat_cases + payload[end + len("cases:") :]
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), payload)

            receipt = build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        check_map = {check["id"]: check for check in receipt["quality_checks"]}
        self.assertEqual(check_map["release_scenario_set_minimum_count"]["status"], "pass")
        self.assertEqual(check_map["release_scenario_set_ids_exist"]["status"], "pass")
        self.assertEqual(check_map["release_scenario_set_cases_are_release_mode"]["status"], "pass")
        validate_scenario_quality_receipt(receipt)

    def test_release_scenario_set_cannot_lower_minimum_below_twenty(self) -> None:
        payload = _release_set_20_evals_yaml()
        flat_cases = "\n".join(
            [
                "release_scenario_sets:",
                "- id: sample-release-10-v1",
                "  default: true",
                "  minimum_scenarios: 5",
                "  cases:",
                *[f"  - foundation-{index}" for index in range(1, 6)],
                *[f"  - behavioral-{index}" for index in range(1, 6)],
                "cases:",
            ]
        )
        start = payload.index("release_scenario_sets:")
        end = payload.index("cases:", start)
        payload = payload[:start] + flat_cases + payload[end + len("cases:") :]
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), payload)
            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        check_map = {check["id"]: check for check in raised.exception.receipt["quality_checks"]}
        self.assertEqual(check_map["release_scenario_set_minimum_count"]["status"], "blocker")
        self.assertIn("sample-release-10-v1:count:10:minimum:20", check_map["release_scenario_set_minimum_count"]["evidence"])
        validate_scenario_quality_receipt(raised.exception.receipt)

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

    def test_scenario_set_parity_normalizes_tessl_staged_case_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(
                temp_path,
                """schema_version: '2.0'
skill_name: sample
cases:
- id: docs/foo
  category: happy
  eval_modes:
  - smoke
  realistic: true
  unit: docs scenario parity
  given: A scenario id contains characters that Tessl staging normalizes.
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
            staged_json = _write_staged_tessl_json(temp_path / "staged.json", ["docs-foo"])
            score_json = _write_tessl_score_json(temp_path / "score.json", ["docs/foo"])

            receipt = build_scenario_quality_receipt(
                temp_path,
                source_path=skill_dir,
                query="sample_skill",
                tessl_staged_json=staged_json,
                tessl_score_json=score_json,
            )

        self.assertEqual(receipt["scenario_set_parity"]["missing_from_staged"], [])
        self.assertEqual(receipt["scenario_set_parity"]["extra_in_staged"], [])
        self.assertEqual(receipt["scenario_set_parity"]["missing_from_score_receipt"], [])
        self.assertFalse(receipt["blockers"])
        validate_scenario_quality_receipt(receipt)

    def test_scenario_set_parity_uses_selected_release_set_universe(self) -> None:
        payload = _release_set_20_evals_yaml() + """
- id: non-release-doc-case
  category: happy
  eval_modes:
  - smoke
  realistic: true
  unit: docs scenario parity
  given: A non-release documentation scenario belongs to the full suite but not the selected release set.
  should: Return non-release-doc-case.md content with source-backed validation claims.
  actual_artifact: non-release-doc-case.md
  expected_artifact: non-release-doc-case.md
  prompt: Return the non-release-doc-case.md content.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns non-release-doc-case.md content with source-backed validation claims.
"""
        release_ids = [f"foundation-{index}" for index in range(1, 6)] + [f"behavioral-{index}" for index in range(1, 16)]
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(temp_path, payload)
            reviewed_dir = skill_dir / "references" / "evals"
            reviewed_dir.mkdir()
            (reviewed_dir / "eval.visual-evidence-decision.md").write_text("# Visual evidence decision\n", encoding="utf-8")
            ids = [*release_ids, "generated-eval.visual-evidence-decision"]
            staged_json = _write_staged_tessl_json(temp_path / "staged.json", ids)
            score_json = _write_tessl_score_json(temp_path / "score.json", ids)

            receipt = build_scenario_quality_receipt(
                temp_path,
                source_path=skill_dir,
                query="sample_skill",
                tessl_staged_json=staged_json,
                tessl_score_json=score_json,
                scenario_set="sample-release-20-v1",
            )

        self.assertEqual(receipt["scenario_count"], 21)
        self.assertEqual(receipt["scenario_set_parity"]["canonical_count"], 20)
        self.assertEqual(receipt["scenario_set_parity"]["reviewed_fixture_count"], 1)
        self.assertFalse(receipt["blockers"])
        validate_scenario_quality_receipt(receipt)

    def test_scenario_set_parity_blocks_unknown_selected_release_set(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(temp_path, _release_set_20_evals_yaml())
            release_ids = [f"foundation-{index}" for index in range(1, 6)] + [f"behavioral-{index}" for index in range(1, 16)]
            staged_json = _write_staged_tessl_json(temp_path / "staged.json", release_ids)

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(
                    temp_path,
                    source_path=skill_dir,
                    query="sample_skill",
                    tessl_staged_json=staged_json,
                    scenario_set="missing-release-set",
                )

        blockers = {check["id"]: check for check in raised.exception.receipt["blockers"]}
        self.assertIn("release_scenario_set_selector_valid", blockers)
        self.assertEqual(
            blockers["release_scenario_set_selector_valid"]["evidence"],
            ["scenario_set:missing-release-set:not_found_or_empty"],
        )
        self.assertEqual(raised.exception.receipt["scenario_set_parity"]["canonical_count"], 0)
        validate_scenario_quality_receipt(raised.exception.receipt)

    def test_scenario_set_parity_blocks_tessl_case_id_collisions(self) -> None:
        evals_text = """schema_version: '2.0'
skill_name: sample
cases:
- id: docs/foo
  category: happy
  eval_modes:
  - smoke
  realistic: true
  unit: docs slash scenario
  given: A docs scenario id contains a slash.
  should: Return docs-slash.md content with evidence-backed documentation behavior.
  actual_artifact: docs-slash.md
  expected_artifact: docs-slash.md
  prompt: Return docs-slash.md content.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns docs-slash.md content with evidence-backed documentation behavior.
- id: docs-foo
  category: edge
  eval_modes:
  - smoke
  realistic: true
  unit: docs dash scenario
  given: A docs scenario id already contains the Tessl-safe dash form.
  should: Return docs-dash.md content with evidence-backed documentation behavior.
  actual_artifact: docs-dash.md
  expected_artifact: docs-dash.md
  prompt: Return docs-dash.md content.
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Returns docs-dash.md content with evidence-backed documentation behavior.
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            skill_dir = _write_skill_with_evals(temp_path, evals_text)
            staged_json = _write_staged_tessl_json(temp_path / "staged.json", ["docs-foo"])

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(
                    temp_path,
                    source_path=skill_dir,
                    query="sample_skill",
                    tessl_staged_json=staged_json,
                )

        check_map = {check["id"]: check for check in raised.exception.receipt["quality_checks"]}
        self.assertEqual(check_map["scenario_set_tessl_case_ids_unique"]["status"], "blocker")
        self.assertEqual(check_map["scenario_set_tessl_case_ids_unique"]["evidence"], ["docs-foo:docs-foo,docs/foo"])
        validate_scenario_quality_receipt(raised.exception.receipt)

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

    def test_minimal_yaml_loader_preserves_quoted_regex_hashes(self) -> None:
        payload = _load_minimal_evals_yaml(
            """schema_version: '2.0'
skill_name: sample
cases:
- id: quoted-regex
  category: edge
  eval_modes:
  - release
  realistic: true
  unit: no invention
  given: A staged excerpt lacks command evidence.
  should: Do not invent setup commands or validation commands.
  prompt: Use only the supplied excerpt. Do not invent setup commands or validation commands.
  actual_artifact: artifacts/quoted-regex.md
  expected_artifact: artifacts/quoted-regex.md
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: not_regex
    value: '(?i)(#[a-z0-9_-]+|Slack channel|pytest|uv|mise|\\./bin/ask|setup command|validation command)'
"""
        )

        acceptance = payload["cases"][0]["acceptance"]
        self.assertEqual(acceptance[0]["type"], "not_regex")
        self.assertIn("#[a-z0-9_-]+", acceptance[0]["value"])
        self.assertIn("\\./bin/ask", acceptance[0]["value"])

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
