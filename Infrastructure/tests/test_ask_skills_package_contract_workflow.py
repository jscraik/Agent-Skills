from ask_skills_package_contract_test_support import *  # noqa: F403


class TestAskSkillsPackageContract(PackageContractTestCase):
    def test_required_skillflow_missing_blocks_package_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "workflow-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: workflow-skill
description: Workflow skill fixture.
version: "1.0.0"
metadata:
  compatible_roles:
    - worker
  runtime_needs:
    - filesystem
  maturity: beta
  provenance: internal
  share_readiness: ready
---

# Workflow Skill
""",
                encoding="utf-8",
            )
            (references_dir / "contract.yaml").write_text(
                """schema_version: "1.0"
purpose: "Exercise required skillflow blocking."
execution_mode: "deterministic_flow"
inputs:
  - name: task
outputs:
  - name: result
workflow:
  path: "workflows/skillflow.json"
  required: true
  execution_mode: "deterministic_flow"
""",
                encoding="utf-8",
            )

            package = skills_package(
                repo_root,
                "Skills/agent-ops/workflow-skill",
                strict=True,
            ).data["skill_package"]

        workflow_contract = package["package_contract"]["sdk_contract"]["values"]["workflow_contract"]
        self.assertEqual(workflow_contract["status"], "blocked_validation")
        self.assertIn(
            "workflow_contract:skillflow_required_file_missing",
            package["gate_summary"]["blocked_reasons"],
        )
        self.assertIn(
            package["package_contract"]["readiness_level"],
            {"sdk_contract_incomplete", "workflow_contract_incomplete"},
        )

    def test_sdk_contract_accepts_valid_skill_optimization_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "optimizable-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: optimizable-skill
description: Optimizable skill fixture.
---

# Optimizable Skill
""",
                encoding="utf-8",
            )
            optimization_payload = {
                "schema_version": "skill-optimization-contract.v1",
                "enabled": True,
                "target_artifact": "SKILL.md",
                "optimizer_mode": "bounded_patch",
                "roles": {
                    "target_runner": {
                        "may_edit": "none",
                        "sees": ["current_target"],
                    },
                    "optimizer": {
                        "may_edit": "candidate_patch_only",
                        "sees": ["train", "selection"],
                    },
                    "promoter": {
                        "may_edit": "canonical_source_after_review",
                        "sees": ["candidate", "selection", "test"],
                    },
                    "auditor": {
                        "may_edit": "none",
                        "sees": ["diff", "protected_paths"],
                    },
                },
                "splits": {
                    "train": {
                        "path": ".harness/evals/optimizable/train.jsonl",
                        "role": "proposal_generation",
                    },
                    "selection": {
                        "path": ".harness/evals/optimizable/selection.jsonl",
                        "role": "candidate_acceptance",
                    },
                    "test": {
                        "path": ".harness/evals/optimizable/test.jsonl",
                        "role": "final_report_only",
                    },
                    "split_seed": 42,
                },
                "edit_policy": {
                    "mode": "patch",
                    "operations": ["add", "delete", "replace"],
                    "max_edits": 4,
                },
                "acceptance_gate": {
                    "metric": "score",
                    "direction": "maximize",
                    "rule": "strict_improvement",
                    "ties": "reject",
                    "min_delta": 0.01,
                    "noise_runs": 3,
                    "guard_failure": "discard",
                    "report_test_score_only_after_acceptance": True,
                },
                "anti_cheat": {
                    "protected_paths": ["references/evals.yaml", ".harness/evals/**"],
                    "checks": ["protected_path_diff_empty", "held_out_not_visible_to_optimizer"],
                },
                "evidence": {
                    "root": ".harness/evidence/optimizable/<run_tag>",
                    "rollout_jsonl": "rollouts.jsonl",
                    "rejected_buffer_jsonl": "rejected-edits.jsonl",
                    "candidate_artifact": "best_skill.md",
                    "promotion_manifest": "promotion.json",
                    "selection_results": "selection-results.json",
                    "test_results": "test-results.json",
                },
                "promotion": {
                    "canonical_edit_requires_review": True,
                    "required_checks": [
                        "selection_gate_pass",
                        "held_out_test_report",
                        "anti_cheat_pass",
                    ],
                },
            }
            (references_dir / "contract.yaml").write_text(
                """schema_version: "1.0"
purpose: "Exercise valid bounded optimization contract support."
inputs:
  - name: task
outputs:
  - name: result
optimization:
  schema_version: "skill-optimization-contract.v1"
  enabled: true
  target_artifact: "SKILL.md"
  optimizer_mode: "bounded_patch"
  roles:
    target_runner:
      may_edit: "none"
      sees:
        - current_target
    optimizer:
      may_edit: "candidate_patch_only"
      sees:
        - train
        - selection
    promoter:
      may_edit: "canonical_source_after_review"
      sees:
        - candidate
        - selection
        - test
    auditor:
      may_edit: "none"
      sees:
        - diff
        - protected_paths
  splits:
    train:
      path: ".harness/evals/optimizable/train.jsonl"
      role: "proposal_generation"
    selection:
      path: ".harness/evals/optimizable/selection.jsonl"
      role: "candidate_acceptance"
    test:
      path: ".harness/evals/optimizable/test.jsonl"
      role: "final_report_only"
    split_seed: 42
  edit_policy:
    mode: "patch"
    operations:
      - add
      - delete
      - replace
    max_edits: 4
  acceptance_gate:
    metric: "score"
    direction: "maximize"
    rule: "strict_improvement"
    ties: "reject"
    min_delta: 0.01
    noise_runs: 3
    guard_failure: "discard"
    report_test_score_only_after_acceptance: true
  anti_cheat:
    protected_paths:
      - "references/evals.yaml"
      - ".harness/evals/**"
    checks:
      - protected_path_diff_empty
      - held_out_not_visible_to_optimizer
  evidence:
    root: ".harness/evidence/optimizable/<run_tag>"
    rollout_jsonl: "rollouts.jsonl"
    rejected_buffer_jsonl: "rejected-edits.jsonl"
    candidate_artifact: "best_skill.md"
    promotion_manifest: "promotion.json"
    selection_results: "selection-results.json"
    test_results: "test-results.json"
  promotion:
    canonical_edit_requires_review: true
    required_checks:
      - selection_gate_pass
      - held_out_test_report
      - anti_cheat_pass
""",
                encoding="utf-8",
            )

            contract = package_contracts.sdk_package_contract(
                repo_root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
            )

        optimization_contract = contract["values"]["optimization_contract"]
        _validate_schema_subset(
            self.schemas["skill-optimization-contract.v1.schema.json"],
            optimization_payload,
            self.schemas,
        )
        min_delta_payload = json.loads(json.dumps(optimization_payload))
        min_delta_payload["acceptance_gate"] = {
            "metric": "score",
            "direction": "maximize",
            "rule": "min_delta",
            "ties": "reject",
            "guard_failure": "discard",
        }
        with self.assertRaisesRegex(AssertionError, "min_delta"):
            _validate_schema_subset(
                self.schemas["skill-optimization-contract.v1.schema.json"],
                min_delta_payload,
                self.schemas,
            )
        negative_integer_payload = json.loads(json.dumps(optimization_payload))
        negative_integer_payload["edit_policy"]["max_edits"] = -1
        with self.assertRaisesRegex(AssertionError, "minimum"):
            _validate_schema_subset(
                self.schemas["skill-optimization-contract.v1.schema.json"],
                negative_integer_payload,
                self.schemas,
            )
        self.assertEqual(optimization_contract["status"], "pass")
        self.assertTrue(optimization_contract["enabled"])
        self.assertEqual(optimization_contract["optimizer_mode"], "bounded_patch")
        self.assertEqual(optimization_contract["split_seed"], 42)
        self.assertFalse(optimization_contract["blockers"])
        self.assertTrue(contract["progressive_disclosure"]["optimization_declared"])

    def test_incomplete_skill_optimization_contract_blocks_package_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills" / "agent-ops" / "optimizable-skill"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                """---
name: optimizable-skill
description: Optimizable skill fixture.
version: "1.0.0"
metadata:
  compatible_roles:
    - worker
  runtime_needs:
    - filesystem
  maturity: beta
  provenance: internal
  share_readiness: ready
---

# Optimizable Skill
""",
                encoding="utf-8",
            )
            (references_dir / "contract.yaml").write_text(
                """schema_version: "1.0"
purpose: "Exercise incomplete bounded optimization contract blocking."
inputs:
  - name: task
outputs:
  - name: result
optimization:
  enabled: true
  target_artifact: "SKILL.md"
""",
                encoding="utf-8",
            )

            package = skills_package(
                repo_root,
                "Skills/agent-ops/optimizable-skill",
                strict=True,
            ).data["skill_package"]

        optimization_contract = package["package_contract"]["sdk_contract"]["values"][
            "optimization_contract"
        ]
        self.assertEqual(optimization_contract["status"], "blocked_validation")
        self.assertIn(
            "optimization_contract:optimization_optimizer_mode_invalid",
            package["gate_summary"]["blocked_reasons"],
        )
        self.assertIn(
            package["package_contract"]["readiness_level"],
            {"sdk_contract_incomplete", "optimization_contract_incomplete"},
        )

    def test_incomplete_reference_quality_blocks_package_readiness(self) -> None:
        frontmatter = {
            "name": "reference-blocked-skill",
            "description": "Reference blocked skill fixture.",
            "metadata": {
                "version": "1.0.0",
                "compatible_roles": ["worker"],
                "runtime_needs": ["filesystem"],
                "maturity": "beta",
                "provenance": "internal",
                "share_readiness": "ready",
            },
        }
        sdk_contract = {
            "required_fields": {"missing": []},
            "values": {
                "workflow_contract": {"status": "pass"},
                "optimization_contract": {"status": "pass"},
                "reference_quality": {
                    "status": "blocked_validation",
                    "required_for_package_readiness": True,
                    "blockers": [{"rule_id": "reference_contract_incomplete"}],
                },
            },
        }

        with patch.object(package_contracts, "sdk_package_contract", return_value=sdk_contract):
            package = package_contracts.skill_package_readiness(frontmatter)

        self.assertEqual(
            package["readiness_level"],
            "reference_quality_incomplete",
        )
        self.assertIn(
            "reference_quality:reference_contract_incomplete",
            package["install_gate"]["blocked_reasons"],
        )

    def test_incomplete_writing_quality_blocks_package_readiness(self) -> None:
        frontmatter = {
            "name": "writing-blocked-skill",
            "description": "Writing blocked skill fixture.",
            "metadata": {
                "version": "1.0.0",
                "compatible_roles": ["worker"],
                "runtime_needs": ["filesystem"],
                "maturity": "beta",
                "provenance": "internal",
                "share_readiness": "ready",
            },
        }
        sdk_contract = {
            "required_fields": {"missing": []},
            "values": {
                "workflow_contract": {"status": "pass"},
                "optimization_contract": {"status": "pass"},
                "reference_quality": {"status": "pass", "required_for_package_readiness": True},
                "writing_quality": {
                    "status": "blocked_validation",
                    "required_for_package_readiness": True,
                    "blockers": [{"rule_id": "scenario_alignment_gold_shape"}],
                },
            },
        }

        with patch.object(package_contracts, "sdk_package_contract", return_value=sdk_contract):
            package = package_contracts.skill_package_readiness(frontmatter)

        self.assertEqual(package["readiness_level"], "writing_quality_incomplete")
        self.assertFalse(package["install_gate"]["install_ready"])
        self.assertIn(
            "writing_quality:scenario_alignment_gold_shape",
            package["install_gate"]["blocked_reasons"],
        )

    def test_incomplete_openai_platform_compat_blocks_package_readiness(self) -> None:
        frontmatter = {
            "name": "openai-blocked-skill",
            "description": "OpenAI blocked skill fixture.",
            "metadata": {
                "version": "1.0.0",
                "compatible_roles": ["worker"],
                "runtime_needs": ["filesystem"],
                "maturity": "beta",
                "provenance": "internal",
                "share_readiness": "ready",
            },
        }
        sdk_contract = {
            "required_fields": {"missing": []},
            "values": {
                "workflow_contract": {"status": "pass"},
                "optimization_contract": {"status": "pass"},
                "reference_quality": {"status": "pass", "required_for_package_readiness": True},
                "writing_quality": {"status": "pass", "required_for_package_readiness": True},
                "openai_platform_compat": {
                    "status": "blocked_validation",
                    "required_for_package_readiness": True,
                    "blockers": [{"rule_id": "plugin_hooks_unsupported_type"}],
                },
            },
        }

        with patch.object(package_contracts, "sdk_package_contract", return_value=sdk_contract):
            package = package_contracts.skill_package_readiness(frontmatter)

        self.assertEqual(package["readiness_level"], "openai_platform_compat_incomplete")
        self.assertFalse(package["install_gate"]["install_ready"])
        self.assertIn(
            "openai_platform_compat:plugin_hooks_unsupported_type",
            package["install_gate"]["blocked_reasons"],
        )
