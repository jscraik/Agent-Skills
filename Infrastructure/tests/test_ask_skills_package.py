import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ask.commands.skills_impl import skills_package, skills_package_verify  # noqa: E402
from ask.skills_sdk.package_verify import _quality_blockers, _quality_checks  # noqa: E402


def _write_minimal_sdk_package_companions(
    skill_dir: Path,
    *,
    complete_evals: bool = True,
) -> None:
    agents_dir = skill_dir / "agents"
    references_dir = skill_dir / "references"
    agents_dir.mkdir(parents=True, exist_ok=True)
    references_dir.mkdir(parents=True, exist_ok=True)
    (agents_dir / "openai.yaml").write_text(
        """interface:
  short_description: Test package fixture.
dependencies: {}
policy:
  permissions: read-only
""",
        encoding="utf-8",
    )
    (references_dir / "contract.yaml").write_text(
        """schema_version: 1
purpose: Test SDK package contract.
inputs: [user_request]
outputs: [package_readiness]
commands:
  - "./bin/ask skills package packaged-skill --json --robot"
permission_profile:
  filesystem:
    read:
      - "target skill package"
      - "repo validation scripts"
    write: []
observability: "Report package validation status and blockers."
""",
        encoding="utf-8",
    )
    evals_text = """schema_version: "2.0"
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
    if not complete_evals:
        evals_text = """schema_version: "2.0"
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
    (references_dir / "evals.yaml").write_text(evals_text, encoding="utf-8")
    (references_dir / "task-profile.json").write_text(
        """{
  "schema_version": "1.0",
  "profile_id": "package-fixture",
  "criteria": [
    {"id": "package_readiness", "threshold": 0.8, "weight": 1.0, "critical": true}
  ]
}
""",
        encoding="utf-8",
    )


def _write_gold_scenario_sdk_companions(skill_dir: Path) -> None:
    _write_minimal_sdk_package_companions(skill_dir)
    (skill_dir / "references" / "evals.yaml").write_text(
        """schema_version: "2.0"
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
""",
        encoding="utf-8",
    )


def _write_gold_quality_skill(skill_dir: Path) -> None:
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        """---
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
""",
        encoding="utf-8",
    )
    _write_gold_scenario_sdk_companions(skill_dir)


def _write_plugin_manifest(plugin_root: Path, hooks_value: str | None = "./hooks/hooks.json") -> None:
    manifest_dir = plugin_root / ".codex-plugin"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": 1,
        "name": plugin_root.name,
        "version": "0.1.0",
        "description": "Plugin compatibility fixture.",
        "skills": "./skills/",
        "interface": {
            "displayName": "Plugin Fixture",
            "shortDescription": "Validate plugin compatibility fixtures",
            "category": "Productivity",
        },
    }
    if hooks_value is not None:
        manifest["hooks"] = hooks_value
    (manifest_dir / "plugin.json").write_text(json.dumps(manifest), encoding="utf-8")


def _write_plugin_hooks(plugin_root: Path, hook: dict[str, object]) -> None:
    hooks_dir = plugin_root / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    payload = {"hooks": {"SessionStart": [{"hooks": [hook]}]}}
    (hooks_dir / "hooks.json").write_text(json.dumps(payload), encoding="utf-8")


class TestAskSkillsPackage(unittest.TestCase):
    def test_package_verify_blocks_weak_skill_writing_quality(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: packaged-skill
description: Helpful package notes.
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

## Workflow

1. Look at the skill.
2. Say what you think.
""",
                encoding="utf-8",
            )
            _write_minimal_sdk_package_companions(skill_dir, complete_evals=False)

            result = skills_package_verify(repo_root, "Skills/agent-ops/packaged-skill")

        self.assertEqual(result.status, "error")
        verification = result.data["skill_package_verification"]
        self.assertEqual(verification["status"], "blocked")
        self.assertEqual(verification["blockers"][0]["rule_id"], "skill_writing_quality_blocked")
        writing_quality = verification["sdk_contract"]["values"]["writing_quality"]
        self.assertEqual(writing_quality["schema_version"], "skills-sdk.skill-writing-quality.v1")
        self.assertEqual(writing_quality["status"], "blocked_validation")
        rule_ids = {blocker["rule_id"] for blocker in writing_quality["blockers"]}
        self.assertIn("weak_description_triggers", rule_ids)
        self.assertIn("missing_completion_criterion", rule_ids)
        self.assertIn("scenario_alignment_gold_shape_incomplete", rule_ids)
        self.assertIn(
            "behavioral_eval_pass",
            writing_quality["what_this_does_not_prove"],
        )

    def test_package_verify_accepts_gold_standard_writing_quality(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            _write_gold_quality_skill(skill_dir)

            result = skills_package_verify(repo_root, "Skills/agent-ops/packaged-skill")

        self.assertEqual(result.status, "success", result.data)
        verification = result.data["skill_package_verification"]
        self.assertEqual(verification["status"], "pass")
        writing_quality = verification["sdk_contract"]["values"]["writing_quality"]
        self.assertEqual(writing_quality["status"], "pass")
        self.assertEqual(writing_quality["blockers"], [])
        self.assertEqual(writing_quality["advisories"], [])
        self.assertIn("writing_quality", [check["name"] for check in verification["checks"]])

    def test_package_verify_reports_writing_quality_advisories_without_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "review-advisory"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: review-advisory
description: "Review and improve things when users need help."
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

# Review Advisory

Review a diff from user-provided input and improve the result.

## Workflow

1. Think about the submitted material.
2. Decide what matters.

## Output Contract

Return schema_version: 1 and a short result summary.

## Progressive Disclosure

- Read references/evals.yaml for gold-standard scenarios.
""",
                encoding="utf-8",
            )
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True, exist_ok=True)
            (references_dir / "orphaned.md").write_text("# Orphaned\n", encoding="utf-8")
            _write_gold_scenario_sdk_companions(skill_dir)

            result = skills_package_verify(repo_root, "Skills/agent-ops/review-advisory")

        self.assertEqual(result.status, "success", result.data)
        verification = result.data["skill_package_verification"]
        writing_quality = verification["sdk_contract"]["values"]["writing_quality"]
        self.assertEqual(writing_quality["status"], "pass")
        self.assertEqual(writing_quality["blockers"], [])
        advisory_ids = {advisory["rule_id"] for advisory in writing_quality["advisories"]}
        self.assertGreaterEqual(
            advisory_ids,
            {
                "description_conflict_risk",
                "content_actionability_weak",
                "review_lens_output_contract_missing",
                "missing_untrusted_input_boundary",
                "improvement_claim_without_before_after_evidence",
                "orphaned_bundle_reference",
            },
        )

    def test_package_verify_accepts_openai_platform_plugin_hook_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            plugin_root = repo_root / "Plugins" / "plugin-fixture"
            skill_dir = plugin_root / "skills" / "packaged-skill"
            _write_gold_quality_skill(skill_dir)
            _write_plugin_manifest(plugin_root)
            _write_plugin_hooks(
                plugin_root,
                {
                    "type": "command",
                    "command": "python3 ${PLUGIN_ROOT}/hooks/session_start.py",
                    "timeout": 5,
                    "statusMessage": "Loading plugin fixture",
                },
            )

            result = skills_package_verify(
                repo_root,
                "Plugins/plugin-fixture/skills/packaged-skill",
            )

        self.assertEqual(result.status, "success", result.data)
        verification = result.data["skill_package_verification"]
        compat = verification["sdk_contract"]["values"]["openai_platform_compat"]
        self.assertEqual(compat["schema_version"], "skills-sdk.openai-platform-compat.v1")
        self.assertEqual(compat["status"], "pass")
        self.assertEqual(compat["target_kind"], "plugin_skill")
        self.assertEqual(compat["blockers"], [])
        self.assertIn(
            "openai_platform_compat",
            [check["name"] for check in verification["checks"]],
        )

    def test_package_verify_treats_absent_plugin_hooks_as_not_applicable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            plugin_root = repo_root / "Plugins" / "plugin-fixture"
            skill_dir = plugin_root / "skills" / "packaged-skill"
            _write_gold_quality_skill(skill_dir)
            _write_plugin_manifest(plugin_root, hooks_value=None)

            result = skills_package_verify(
                repo_root,
                "Plugins/plugin-fixture/skills/packaged-skill",
            )

        self.assertEqual(result.status, "success", result.data)
        verification = result.data["skill_package_verification"]
        compat = verification["sdk_contract"]["values"]["openai_platform_compat"]
        self.assertEqual(compat["status"], "pass")
        self.assertEqual(compat["target_kind"], "plugin_skill")
        self.assertEqual(compat["blockers"], [])
        checks = {check["name"]: check for check in compat["checks"]}
        self.assertEqual(
            checks["plugin_hooks_manifest_declared"]["status"],
            "not_applicable",
        )

    def test_package_verify_blocks_unsupported_openai_platform_plugin_hooks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            plugin_root = repo_root / "Plugins" / "plugin-fixture"
            skill_dir = plugin_root / "skills" / "packaged-skill"
            _write_gold_quality_skill(skill_dir)
            _write_plugin_manifest(plugin_root, hooks_value="./hooks/wrong.json")
            _write_plugin_hooks(
                plugin_root,
                {
                    "type": "prompt",
                    "command": "/Users/jamiecraik/dev/plugin/hooks/session_start.py",
                    "timeoutSec": 5,
                },
            )

            result = skills_package_verify(
                repo_root,
                "Plugins/plugin-fixture/skills/packaged-skill",
            )

        self.assertEqual(result.status, "error")
        verification = result.data["skill_package_verification"]
        self.assertEqual(
            verification["blockers"][0]["rule_id"],
            "openai_platform_compat_blocked",
        )
        compat = verification["sdk_contract"]["values"]["openai_platform_compat"]
        rule_ids = {blocker["rule_id"] for blocker in compat["blockers"]}
        self.assertIn("plugin_hooks_manifest_path_invalid", rule_ids)
        self.assertIn("plugin_hooks_unsupported_type", rule_ids)
        self.assertIn("plugin_hooks_timeoutsec_unsupported", rule_ids)

    def test_package_verify_reports_invalid_utf8_plugin_hooks_as_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            plugin_root = repo_root / "Plugins" / "plugin-fixture"
            skill_dir = plugin_root / "skills" / "packaged-skill"
            _write_gold_quality_skill(skill_dir)
            _write_plugin_manifest(plugin_root, hooks_value="./hooks/hooks.json")
            hooks_dir = plugin_root / "hooks"
            hooks_dir.mkdir(parents=True, exist_ok=True)
            (hooks_dir / "hooks.json").write_bytes(bytes([123, 255]))

            result = skills_package_verify(
                repo_root,
                "Plugins/plugin-fixture/skills/packaged-skill",
            )

        self.assertEqual(result.status, "error")
        compat = result.data["skill_package_verification"]["sdk_contract"]["values"]["openai_platform_compat"]
        blocker = next(blocker for blocker in compat["blockers"] if blocker["rule_id"] == "plugin_hooks_file_unreadable")
        self.assertEqual(blocker["evidence"]["error"], "UnicodeDecodeError")

    def test_package_verify_rejects_placeholder_hooks_with_local_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            plugin_root = repo_root / "Plugins" / "plugin-fixture"
            skill_dir = plugin_root / "skills" / "packaged-skill"
            _write_gold_quality_skill(skill_dir)
            _write_plugin_manifest(plugin_root, hooks_value="./hooks/hooks.json")
            _write_plugin_hooks(
                plugin_root,
                {
                    "type": "command",
                    "command": "python3 $" + "{PLUGIN_ROOT}/hooks/session_start.py /Users/jamie/local",
                    "timeout": True,
                },
            )

            result = skills_package_verify(
                repo_root,
                "Plugins/plugin-fixture/skills/packaged-skill",
            )

        self.assertEqual(result.status, "error")
        compat = result.data["skill_package_verification"]["sdk_contract"]["values"]["openai_platform_compat"]
        rule_ids = {blocker["rule_id"] for blocker in compat["blockers"]}
        self.assertIn("plugin_hooks_command_not_portable", rule_ids)
        self.assertIn("plugin_hooks_timeout_missing", rule_ids)

    def test_package_verify_quality_helpers_block_empty_blocked_validation_details(self) -> None:
        quality = {
            "reference_quality": {"status": "pass", "blockers": []},
            "writing_quality": {"status": "blocked_validation", "blockers": []},
            "openai_platform_compat": {"status": "blocked_validation", "blockers": "malformed"},
        }

        blockers = _quality_blockers(quality)
        blocker_ids = {blocker["rule_id"] for blocker in blockers}
        checks = {check["name"]: check for check in _quality_checks(quality)}

        self.assertIn("skill_writing_quality_blocked", blocker_ids)
        self.assertIn("openai_platform_compat_blocked", blocker_ids)
        self.assertEqual(checks["writing_quality"]["status"], "fail")
        self.assertEqual(checks["openai_platform_compat"]["status"], "fail")

    def test_package_reports_versioned_role_ready_contract(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "skill-factory-router",
            "source_path": "Plugins/skill-factory/skills/skill-factory-router/SKILL.md",
        }):
            result = skills_package(REPO_ROOT, "skill-factory-router")

        self.assertEqual(result.status, "success")
        package = result.data["skill_package"]
        self.assertEqual(package["schema_version"], "skill-package-readiness.v1")
        self.assertEqual(package["gate_summary"]["promotion_status"], "ready_pending_checkout")
        self.assertFalse(package["gate_summary"]["promotion_ready"])
        contract = package["package_contract"]
        self.assertEqual(contract["values"]["version"], "1.0.0")
        self.assertEqual(contract["values"]["maturity"], "canonical")
        self.assertEqual(contract["required_fields"]["missing"], [])
        self.assertTrue(contract["install_gate"]["install_ready"])
        self.assertEqual(contract["install_gate"]["blocked_reasons"], [])
        self.assertEqual(contract["install_gate"]["checkout_test"]["status"], "not_run")
        self.assertEqual(contract["promotion_gate"]["status"], "ready_pending_checkout")
        self.assertFalse(contract["promotion_gate"]["promotion_ready"])
        self.assertTrue(contract["promotion_gate"]["share_ready"])
        self.assertEqual(contract["promotion_gate"]["blocked_reasons"], [])
        self.assertEqual(contract["promotion_gate"]["recommended_next_fields"], [])
        self.assertEqual(package["lifecycle_event"]["event_type"], "package_readiness_checked")
        self.assertEqual(
            [event["event_type"] for event in package["lifecycle_events"]],
            ["skill_loaded", "package_readiness_checked"],
        )
        self.assertNotIn("details", package["lifecycle_events"][0])
        self.assertEqual(
            package["lifecycle_events"][1]["details"]["gate_summary"],
            package["gate_summary"],
        )
        self.assertIn("package_readiness_checked", [event["event_type"] for event in package["lifecycle_events"]])

    def test_package_strict_accepts_complete_package_metadata(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "skill-factory-router",
            "source_path": "Plugins/skill-factory/skills/skill-factory-router/SKILL.md",
        }):
            result = skills_package(REPO_ROOT, "skill-factory-router", strict=True)

        self.assertEqual(result.status, "success")
        package = result.data["skill_package"]
        self.assertEqual(package["status"], "pass")
        self.assertEqual(package["blockers"], [])
        self.assertIn("package_readiness_checked", [event["event_type"] for event in package["lifecycle_events"]])
        self.assertEqual(package["gate_summary"]["promotion_status"], "ready_pending_checkout")
        self.assertEqual(package["package_contract"]["required_fields"]["missing"], [])
        self.assertEqual(result.errors, [])

    def test_package_blocks_missing_source(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "missing-skill",
            "source_path": "Skills/agent-ops/missing-skill/SKILL.md",
        }):
            result = skills_package(REPO_ROOT, "missing-skill")

        self.assertEqual(result.status, "error")
        package = result.data["skill_package"]
        self.assertEqual(package["status"], "blocked")
        self.assertEqual(package["blockers"][0]["class"], "blocked_missing_source")
        self.assertFalse(package["package_contract"]["install_gate"]["install_ready"])
        self.assertEqual(
            package["package_contract"]["install_gate"]["checkout_test"]["status"],
            "not_run",
        )
        self.assertEqual(
            package["package_contract"]["promotion_gate"]["status"],
            "blocked_missing_source",
        )
        self.assertEqual(package["next_command"], "./bin/ask skills doctor missing-skill --json --robot")

    def test_package_checkout_test_blocks_missing_source(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "missing-skill",
            "source_path": "Skills/agent-ops/missing-skill/SKILL.md",
        }):
            result = skills_package(REPO_ROOT, "missing-skill", checkout_test=True)

        self.assertEqual(result.status, "error")
        package = result.data["skill_package"]
        self.assertEqual(package["status"], "blocked")
        self.assertEqual(
            package["package_contract"]["install_gate"]["checkout_test"]["status"],
            "blocked_missing_source",
        )
        self.assertEqual(package["next_command"], "./bin/ask skills doctor missing-skill --json --robot")

    def test_package_reads_nested_block_list_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: packaged-skill
description: Use when packaging skills to validate package readiness metadata.
version: "2.0.0"
metadata:
  compatible_roles:
    - worker
    - reviewer
  runtime_needs:
    - network
    - filesystem
  maturity: beta
  provenance: internal
  share_readiness: ready
---

# Packaged Skill
""",
                encoding="utf-8",
            )
            _write_minimal_sdk_package_companions(skill_dir)

            result = skills_package(repo_root, "Skills/agent-ops/packaged-skill")

        self.assertEqual(result.status, "success")
        package = result.data["skill_package"]
        self.assertEqual(package["status"], "pass")
        self.assertEqual(package["gate_summary"]["promotion_status"], "ready_pending_checkout")
        self.assertFalse(package["gate_summary"]["promotion_ready"])
        self.assertEqual(package["gate_summary"]["checkout_test_status"], "not_run")
        contract = package["package_contract"]
        self.assertEqual(contract["required_fields"]["missing"], [])
        self.assertEqual(contract["role_compatibility"]["roles"], ["worker", "reviewer"])
        self.assertEqual(contract["runtime_contract"]["needs"], ["network", "filesystem"])
        self.assertTrue(contract["install_gate"]["install_ready"])
        self.assertEqual(contract["install_gate"]["blocked_reasons"], [])
        self.assertEqual(contract["install_gate"]["checkout_test"]["status"], "not_run")
        self.assertEqual(contract["promotion_gate"]["status"], "ready_pending_checkout")
        self.assertFalse(contract["promotion_gate"]["promotion_ready"])
        self.assertEqual(contract["promotion_gate"]["checkout_test_status"], "not_run")
        self.assertEqual(contract["promotion_gate"]["blocked_reasons"], [])
        self.assertTrue(contract["promotion_gate"]["share_ready"])

    def test_package_reads_top_level_package_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: packaged-skill
description: Use when packaging skills to validate package readiness metadata.
version: "2.0.0"
compatible_roles: [worker, reviewer]
runtime_needs: [filesystem]
maturity: beta
provenance: internal
share_readiness: ready
---

# Packaged Skill
""",
                encoding="utf-8",
            )
            _write_minimal_sdk_package_companions(skill_dir)

            result = skills_package(repo_root, "Skills/agent-ops/packaged-skill")

        self.assertEqual(result.status, "success")
        contract = result.data["skill_package"]["package_contract"]
        self.assertEqual(contract["required_fields"]["missing"], [])
        self.assertEqual(contract["role_compatibility"]["roles"], ["worker", "reviewer"])
        self.assertEqual(contract["runtime_contract"]["needs"], ["filesystem"])
        self.assertTrue(contract["install_gate"]["install_ready"])

    def test_package_blocks_declared_non_ready_share_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: packaged-skill
description: Use when packaging skills to validate package readiness metadata.
version: "2.0.0"
metadata:
  compatible_roles:
    - worker
  runtime_needs:
    - filesystem
  maturity: beta
  provenance: internal
  share_readiness: draft
---

# Packaged Skill
""",
                encoding="utf-8",
            )
            _write_minimal_sdk_package_companions(skill_dir)

            result = skills_package(repo_root, "Skills/agent-ops/packaged-skill")

        self.assertEqual(result.status, "success")
        package = result.data["skill_package"]
        self.assertEqual(package["status"], "warning")
        contract = package["package_contract"]
        self.assertEqual(contract["required_fields"]["missing"], [])
        self.assertFalse(contract["install_gate"]["install_ready"])
        self.assertIn("share_readiness_not_ready", contract["install_gate"]["blocked_reasons"])
        self.assertEqual(contract["promotion_gate"]["status"], "blocked_validation")
        self.assertFalse(contract["promotion_gate"]["promotion_ready"])
        self.assertFalse(contract["promotion_gate"]["share_ready"])
        self.assertEqual(contract["promotion_gate"]["recommended_next_fields"], ["share_readiness"])

    def test_package_checkout_test_records_local_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: packaged-skill
description: Use when packaging skills to validate package readiness metadata.
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
""",
                encoding="utf-8",
            )
            _write_minimal_sdk_package_companions(skill_dir)

            result = skills_package(repo_root, "Skills/agent-ops/packaged-skill", checkout_test=True)

        self.assertEqual(result.status, "success")
        checkout = result.data["skill_package"]["package_contract"]["install_gate"]["checkout_test"]
        self.assertEqual(checkout["status"], "pass")
        self.assertIn("source_path:Skills/agent-ops/packaged-skill/SKILL.md", checkout["evidence"])
        self.assertIn("package_metadata_complete:true", checkout["evidence"])
        self.assertEqual(
            result.data["skill_package"]["gate_summary"],
            {
                "install_ready": True,
                "checkout_test_status": "pass",
                "promotion_status": "ready",
                "promotion_ready": True,
                "blocked_reasons": [],
            },
        )
        self.assertEqual(
            result.data["skill_package"]["lifecycle_events"][1]["details"]["gate_summary"],
            result.data["skill_package"]["gate_summary"],
        )
        promotion = result.data["skill_package"]["package_contract"]["promotion_gate"]
        self.assertEqual(promotion["status"], "ready")
        self.assertTrue(promotion["promotion_ready"])
        self.assertEqual(promotion["checkout_test_status"], "pass")

    def test_package_checkout_test_records_skill_builder_evidence(self) -> None:
        with patch("ask.commands.skills_impl.resolve_skill_handle", return_value={
            "status": "ok",
            "handle": "skill-factory-router",
            "source_path": "Plugins/skill-factory/skills/skill-factory-router/SKILL.md",
        }):
            result = skills_package(REPO_ROOT, "skill-factory-router", checkout_test=True)

        self.assertEqual(result.status, "success")
        package = result.data["skill_package"]
        self.assertEqual(package["status"], "pass")
        checkout = package["package_contract"]["install_gate"]["checkout_test"]
        self.assertEqual(checkout["status"], "pass")
        self.assertIn(
            "source_path:Plugins/skill-factory/skills/skill-factory-router/SKILL.md",
            checkout["evidence"],
        )
        self.assertIn("package_metadata_complete:true", checkout["evidence"])
        self.assertEqual(package["gate_summary"]["promotion_status"], "ready")
        self.assertTrue(package["gate_summary"]["promotion_ready"])

    def test_package_checkout_test_blocks_incomplete_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
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
""",
                encoding="utf-8",
            )

            result = skills_package(repo_root, "Skills/agent-ops/packaged-skill", strict=True, checkout_test=True)

        self.assertEqual(result.status, "error")
        package = result.data["skill_package"]
        contract = package["package_contract"]
        self.assertEqual(contract["readiness_level"], "incomplete_identity")
        self.assertEqual(contract["install_gate"]["checkout_test"]["status"], "blocked_validation")
        self.assertIn("identity_incomplete", contract["promotion_gate"]["blocked_reasons"])
        self.assertFalse(contract["promotion_gate"]["promotion_ready"])
        self.assertFalse(package["gate_summary"]["promotion_ready"])

    def test_package_checkout_test_blocks_non_ready_share_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "packaged-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: packaged-skill
description: Use when packaging skills to validate package readiness metadata.
version: "2.0.0"
metadata:
  compatible_roles:
    - worker
  runtime_needs:
    - filesystem
  maturity: beta
  provenance: internal
  share_readiness: draft
---

# Packaged Skill
""",
                encoding="utf-8",
            )
            _write_minimal_sdk_package_companions(skill_dir)

            result = skills_package(repo_root, "Skills/agent-ops/packaged-skill", checkout_test=True)

        self.assertEqual(result.status, "success")
        checkout = result.data["skill_package"]["package_contract"]["install_gate"]["checkout_test"]
        self.assertEqual(checkout["status"], "blocked_validation")
        self.assertIn("promotion_gate_blocked:share_readiness_not_ready", checkout["evidence"])


if __name__ == "__main__":
    unittest.main()
