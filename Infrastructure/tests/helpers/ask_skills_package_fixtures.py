import json
from pathlib import Path


_AGENTS_OPENAI = """interface:
  short_description: Test package fixture.
dependencies: {}
policy:
  permissions: read-only
"""
_CONTRACT_YAML = """schema_version: 1
purpose: Test SDK package contract.
inputs: [user_request]
outputs: [package_readiness]
quality_criteria:
  package_readiness:
    purpose: Measures whether the package reports complete install and share readiness.
    why_it_matters: Package readiness must be evidenced before a skill enters a runtime or distribution lane.
    observable_evidence:
      - The package report names install readiness.
      - The package report names share readiness.
    scoring:
      5: Reports both readiness fields with current package evidence.
      4: Reports both readiness fields with a minor evidence gap.
      3: Reports package readiness but leaves one field implicit.
      2: Reports partial package metadata without a readiness decision.
      1: Does not report package readiness.
automatic_failure_conditions:
  - Missing or contradictory package readiness evidence.
evidence_requirements:
  - Package reports must cite install and share readiness evidence.
commands:
  - "./bin/ask skills package packaged-skill --json --robot"
permission_profile:
  filesystem:
    read:
      - "target skill package"
      - "repo validation scripts"
    write: []
observability: "Report package validation status and blockers."
"""
_EVALS_COMPLETE = """schema_version: "2.0"
skill_name: packaged-skill
claims:
  - id: package.fixture.ready
    statement: "The fixture reports package readiness from declared metadata and SDK companions."
    source: "SKILL.md"
    claim_type: governance
    risk: medium
    hard_gate: true
    evidence_required: ["package output"]
cases:
  - id: package-smoke
    name: package smoke
    category: happy
    should_trigger: true
    given: "A skill with complete package metadata and SDK companion files."
    prompt: "Package this skill."
    expected_behavior: "Reports package readiness."
    acceptance:
      - "The package report includes install readiness."
      - "The package report includes share readiness."
"""
_EVALS_INCOMPLETE = """schema_version: "2.0"
skill_name: packaged-skill
claims:
  - id: package.fixture.ready
    statement: "The fixture reports package readiness from declared metadata and SDK companions."
    source: "SKILL.md"
    claim_type: governance
    risk: medium
    hard_gate: true
    evidence_required: ["package output"]
cases:
  - id: package-smoke
    name: package smoke
    category: happy
    should_trigger: true
    prompt: "Package this skill."
    expected_behavior: "Reports package readiness."
"""
_EVALS_GOLD = """schema_version: "2.0"
skill_name: packaged-skill
claims:
  - id: package.fixture.ready
    statement: "The fixture reports package readiness from declared metadata and SDK companions."
    source: "SKILL.md"
    claim_type: governance
    risk: medium
    hard_gate: true
    evidence_required: ["package output"]
cases:
  - id: package-smoke
    name: package smoke
    category: happy
    eval_modes: [smoke]
    should_trigger: true
    realistic: true
    unit: package verification
    given: "A complete SDK package fixture with declared metadata and references."
    should: "Report package readiness without runtime mutation."
    prompt: "Verify this staged skill package and report package blockers."
    expected_evidence: ["package readiness", "no runtime mutation"]
    acceptance:
      - {type: expected_signal, value: "Reports package readiness from declared metadata."}
"""
_TASK_PROFILE = """{
  "schema_version": "1.0",
  "profile_id": "package-fixture",
  "criteria": [
    {"id": "package_readiness", "threshold": 0.8, "weight": 1.0, "critical": true}
  ]
}
"""
_GOLD_SKILL = """---
name: packaged-skill
description: "Validate packaged skills when a user asks for SDK package readiness, writing-quality rubric evidence, or no-mutation verification."
version: "2.0.0"
metadata:
  compatible_roles:
    - worker
  runtime_needs:
    - filesystem
  maturity: beta
  provenance: internal
  share_readiness: ready
---

# Packaged Skill

Validate one staged skill package and report package blockers without mutating runtime roots.

## Workflow

1. Resolve the staged skill source and package companion files.
2. Run package verification and capture blocker evidence before any install lane.

## Validation

Command: ./bin/ask skills package verify <skill-path> --json --robot -> pass|fail|blocked.

## Progressive Disclosure

- Read `references/contract.yaml` for package inputs, outputs, commands, and permission profile.
- Read `references/evals.yaml` for the gold-standard scenario alignment cases.
"""
_PACKAGE_SKILL = """---
name: packaged-skill
description: Use when packaging skills to validate package readiness metadata.
version: "2.0.0"
{metadata}---

# Packaged Skill

Validate package metadata and report readiness without mutating runtime roots.

## Workflow

1. Resolve the staged skill source and package companion files.
2. Run package verification and capture readiness evidence before any install lane.

## Validation

Command: ./bin/ask skills package verify <skill-path> --json --robot -> pass|fail|blocked.

## Progressive Disclosure

- Read `references/contract.yaml` for package inputs, outputs, and evidence requirements.
"""


def write_minimal_sdk_package_companions(skill_dir: Path, *, complete_evals: bool = True) -> None:
    agents_dir = skill_dir / "agents"
    references_dir = skill_dir / "references"
    agents_dir.mkdir(parents=True, exist_ok=True)
    references_dir.mkdir(parents=True, exist_ok=True)
    (agents_dir / "openai.yaml").write_text(_AGENTS_OPENAI, encoding="utf-8")
    (references_dir / "contract.yaml").write_text(_CONTRACT_YAML, encoding="utf-8")
    (references_dir / "evals.yaml").write_text(_EVALS_COMPLETE if complete_evals else _EVALS_INCOMPLETE, encoding="utf-8")
    (references_dir / "task-profile.json").write_text(_TASK_PROFILE, encoding="utf-8")


def write_gold_scenario_sdk_companions(skill_dir: Path) -> None:
    write_minimal_sdk_package_companions(skill_dir)
    (skill_dir / "references" / "evals.yaml").write_text(_EVALS_GOLD, encoding="utf-8")


def write_gold_quality_skill(skill_dir: Path) -> None:
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(_GOLD_SKILL, encoding="utf-8")
    write_gold_scenario_sdk_companions(skill_dir)


def _package_metadata(
    nested_metadata: bool,
    roles: tuple[str, ...],
    runtime_needs: tuple[str, ...],
    share_readiness: str,
) -> str:
    if nested_metadata:
        role_lines = "".join(f"    - {role}\n" for role in roles)
        runtime_lines = "".join(f"    - {need}\n" for need in runtime_needs)
        return "".join(("metadata:\n", f"  compatible_roles:\n{role_lines}", f"  runtime_needs:\n{runtime_lines}", "  maturity: beta\n", "  provenance: internal\n", f"  share_readiness: {share_readiness}\n"))
    return "".join((f"compatible_roles: [{', '.join(roles)}]\n", f"runtime_needs: [{', '.join(runtime_needs)}]\n", "maturity: beta\n", "provenance: internal\n", f"share_readiness: {share_readiness}\n"))


def write_package_metadata_skill(
    skill_dir: Path,
    *,
    nested_metadata: bool = True,
    roles: tuple[str, ...] = ("worker",),
    runtime_needs: tuple[str, ...] = ("filesystem",),
    share_readiness: str = "ready",
) -> None:
    skill_dir.mkdir(parents=True, exist_ok=True)
    metadata = _package_metadata(nested_metadata, roles, runtime_needs, share_readiness)
    (skill_dir / "SKILL.md").write_text(_PACKAGE_SKILL.format(metadata=metadata), encoding="utf-8")


def write_plugin_manifest(plugin_root: Path, hooks_value: str | None = "./hooks/hooks.json") -> None:
    manifest_dir = plugin_root / ".codex-plugin"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"schema_version": 1, "name": plugin_root.name, "version": "0.1.0", "description": "Plugin compatibility fixture.", "skills": "./skills/", "interface": {"displayName": "Plugin Fixture", "shortDescription": "Validate plugin compatibility fixtures", "category": "Productivity"}}
    if hooks_value is not None:
        manifest["hooks"] = hooks_value
    (manifest_dir / "plugin.json").write_text(json.dumps(manifest), encoding="utf-8")


def write_plugin_hooks(plugin_root: Path, hook: dict[str, object]) -> None:
    hooks_dir = plugin_root / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    (hooks_dir / "hooks.json").write_text(json.dumps({"hooks": {"SessionStart": [{"hooks": [hook]}]}}), encoding="utf-8")
