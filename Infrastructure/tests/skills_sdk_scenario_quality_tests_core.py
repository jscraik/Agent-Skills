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


def _release_set_8_evals_yaml() -> str:
    foundation = [f"foundation-{index}" for index in range(1, 3)]
    behavioral = [f"behavioral-{index}" for index in range(1, 7)]
    case_ids = foundation + behavioral
    lines = [
        "schema_version: '2.0'",
        "skill_name: sample",
        "release_scenario_sets:",
        "- id: sample-release-8-v1",
        "  default: true",
        "  minimum_scenarios: 5",
        "  target_scenarios: 8",
        "  maximum_scenarios: 10",
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

class _SkillsSdkScenarioQualityBase(unittest.TestCase):
    pass

__all__ = [name for name in globals() if not name.startswith("__")]
