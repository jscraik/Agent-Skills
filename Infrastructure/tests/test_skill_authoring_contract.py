import sys
import tempfile
import unittest
from copy import deepcopy
from shutil import copytree
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.contracts import read_skill_frontmatter_fields  # noqa: E402
from ask.skills_sdk.package_contracts import read_reference_contract  # noqa: E402
from ask.skills_sdk.package_verify import (  # noqa: E402
    _quality_blockers,
    _sdk_quality_values,
    verify_skill_directory,
)
from ask.skills_sdk.skill_authoring_contract_markdown import (  # noqa: E402
    duplicate_nonempty_paragraphs,
)
from ask.skills_sdk.skill_authoring_contract import authoring_contract  # noqa: E402


EXTENDED_CANONICAL_CASES = (
    ("entrypoint budget", lambda authoring: authoring["entrypoint"].update({"max_lines": 1}), "authoring_entrypoint_not_minimal"),
    ("stable vocabulary use", lambda authoring: authoring["steering_terms"][0].update({"term": "absent canonical term"}), "authoring_steering_vocabulary_invalid"),
    ("phase separation", lambda authoring: authoring["phase_model"].update({"kind": "phased"}), "authoring_phase_model_invalid"),
    ("decision boundary", lambda authoring: authoring["decision_boundaries"][0].update({"statement": "Missing explicit boundary."}), "authoring_decision_boundaries_incomplete"),
    ("blocker matrix", lambda authoring: authoring["blocker_matrix"]["coverage"].pop("tool"), "authoring_blocker_matrix_incomplete"),
    ("output provenance", lambda authoring: authoring["output_contract"].pop("provenance_fields"), "authoring_output_contract_incomplete"),
    ("behavior proof", lambda authoring: authoring["behavior_proof"].update({"command_template": "./bin/ask evals run unrelated"}), "authoring_behavior_proof_incomplete"),
    ("deletion test", lambda authoring: authoring["mutation_targets"][0].pop("removal_test"), "authoring_mutation_targets_incomplete"),
    ("readiness lanes", lambda authoring: authoring["readiness_evidence"].pop("not_ready_statement"), "authoring_readiness_evidence_incomplete"),
)


def _write_missing_scenario_skill(root: Path) -> Path:
    skill_md = root / "Skills" / "agent-ops" / "example" / "SKILL.md"
    (skill_md.parent / "references").mkdir(parents=True)
    skill_md.write_text(
        "---\nname: example\ndescription: Use when an author asks for an example package.\n---\n\n"
        "# Example\n\n## Failure Mode\n\n"
        "Return a typed blocker when evidence is missing because guessed evidence would be false proof.\n",
        encoding="utf-8",
    )
    (skill_md.parent / "references" / "detail.md").write_text("# Detail\n", encoding="utf-8")
    (skill_md.parent / "references" / "evals.yaml").write_text("cases:\n- id: happy\n", encoding="utf-8")
    return skill_md


def _missing_scenario_contract() -> dict[str, object]:
    return {
        "rubric_profile": "skills-sdk.gold-standard.v1",
        "authoring_contract": {
            "schema_version": "skills-sdk.authoring-contract.v1",
            "primary_job": {"outcome": "Do one thing.", "refusal_boundary": "Refuse unrelated work."},
            "invocation": {"mode": "both", "rationale": "The request can be routed or directly invoked."},
            "steering_terms": [{"term": "proof gap", "definition": "Missing proof."}],
            "critical_rules": [{
                "id": "no-silent-fallback", "rationale_source": "SKILL.md#failure-mode",
                "rationale_text": "guessed evidence would be false proof.", "typed_outcome": "blocked",
                "scenario_ids": ["missing"],
            }],
            "reference_routes": [{"id": "detail", "path": "references/detail.md", "read_when": "Detail is needed."}],
            "output_contract": {"required_fields": ["outcome", "evidence", "validation", "residual_risk"]},
            "mutation_targets": [{"kind": "critical_rule", "target": "no-silent-fallback", "scenario_ids": ["missing"]}],
            "focused_proof": "./bin/ask sdk eval scenario-quality Skills/agent-ops/example --preview --json --robot",
        },
    }


class SkillAuthoringContractTests(unittest.TestCase):
    def test_current_gold_standard_packages_declare_a_passing_authoring_contract(self) -> None:
        paths = (
            "Skills/agent-ops/simplify/SKILL.md",
            "Skills/agent-ops/improve-agent-native/SKILL.md",
            "Skills/product-strategy/devrel-hack-coach/SKILL.md",
        )
        for relative in paths:
            with self.subTest(skill=relative):
                skill_md = REPO_ROOT / relative
                receipt = authoring_contract(
                    REPO_ROOT,
                    skill_md,
                    read_skill_frontmatter_fields(skill_md),
                    read_reference_contract(skill_md),
                    skill_md.read_text(encoding="utf-8"),
                )
                self.assertTrue(receipt["required_for_package_readiness"])
                self.assertEqual(receipt["status"], "pass", receipt["blockers"])

    def test_gold_standard_package_without_contract_is_blocked(self) -> None:
        receipt = authoring_contract(
            REPO_ROOT,
            None,
            {},
            {"rubric_profile": "skills-sdk.gold-standard.v1"},
            "# Example\n",
        )
        self.assertEqual(receipt["status"], "blocked_validation")
        self.assertEqual(receipt["blockers"][0]["rule_id"], "authoring_contract_missing")

    def test_plural_gold_profile_requires_the_authoring_contract(self) -> None:
        skill_md = REPO_ROOT / "Skills" / "agent-ops" / "simplify" / "SKILL.md"
        contract = deepcopy(read_reference_contract(skill_md))
        contract.pop("authoring_contract")
        contract.pop("rubric_profile")
        contract["rubric_profiles"] = ["skills-sdk.gold-standard.v1"]
        receipt = authoring_contract(
            REPO_ROOT,
            skill_md,
            read_skill_frontmatter_fields(skill_md),
            contract,
            skill_md.read_text(encoding="utf-8"),
        )

        self.assertEqual(receipt["status"], "blocked_validation")
        self.assertEqual(receipt["blockers"][0]["rule_id"], "authoring_contract_missing")

    def test_critical_rule_rationale_must_appear_in_its_declared_skill_section(
        self,
    ) -> None:
        skill_md = REPO_ROOT / "Skills" / "agent-ops" / "simplify" / "SKILL.md"
        contract = deepcopy(read_reference_contract(skill_md))
        contract["authoring_contract"]["critical_rules"][0]["rationale_text"] = (
            "This text is absent from the failure mode."
        )
        receipt = authoring_contract(
            REPO_ROOT,
            skill_md,
            read_skill_frontmatter_fields(skill_md),
            contract,
            skill_md.read_text(encoding="utf-8"),
        )

        self.assertEqual(receipt["status"], "blocked_validation")
        self.assertIn(
            "authoring_critical_rules_incomplete",
            {item["rule_id"] for item in receipt["blockers"]},
        )

    def test_claim_id_cannot_substitute_for_a_controlled_scenario(self) -> None:
        skill_md = REPO_ROOT / "Skills" / "agent-ops" / "simplify" / "SKILL.md"
        contract = deepcopy(read_reference_contract(skill_md))
        authoring = contract["authoring_contract"]
        for rule in authoring["critical_rules"]:
            rule["scenario_ids"] = ["simplify.behavior-preservation"]
        for target in authoring["mutation_targets"]:
            target["scenario_ids"] = ["simplify.behavior-preservation"]
        receipt = authoring_contract(
            REPO_ROOT,
            skill_md,
            read_skill_frontmatter_fields(skill_md),
            contract,
            skill_md.read_text(encoding="utf-8"),
        )

        self.assertEqual(receipt["status"], "blocked_validation")
        self.assertIn(
            "authoring_critical_rules_incomplete",
            {item["rule_id"] for item in receipt["blockers"]},
        )

    def test_malformed_scenario_yaml_returns_a_typed_authoring_blocker(self) -> None:
        skill_md = REPO_ROOT / "Skills" / "agent-ops" / "simplify" / "SKILL.md"
        with patch(
            "ask.skills_sdk.scenario_quality._yaml_safe_load",
            side_effect=ValueError("malformed evals"),
        ):
            receipt = authoring_contract(
                REPO_ROOT,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
                read_reference_contract(skill_md),
                skill_md.read_text(encoding="utf-8"),
            )

        self.assertEqual(receipt["status"], "blocked_validation")
        self.assertIn(
            "authoring_critical_rules_incomplete",
            {item["rule_id"] for item in receipt["blockers"]},
        )

    def test_non_utf8_scenario_yaml_returns_a_typed_authoring_blocker(self) -> None:
        skill_md = REPO_ROOT / "Skills" / "agent-ops" / "simplify" / "SKILL.md"
        body = skill_md.read_text(encoding="utf-8")
        frontmatter = read_skill_frontmatter_fields(skill_md)
        contract = read_reference_contract(skill_md)
        with patch.object(
            Path,
            "read_text",
            side_effect=UnicodeDecodeError("utf-8", b"\\xff", 0, 1, "invalid start byte"),
        ):
            receipt = authoring_contract(
                REPO_ROOT,
                skill_md,
                frontmatter,
                contract,
                body,
            )

        self.assertEqual(receipt["status"], "blocked_validation")
        self.assertIn(
            "authoring_critical_rules_incomplete",
            {item["rule_id"] for item in receipt["blockers"]},
        )

    def test_focused_proof_must_be_the_skill_bound_scenario_preview(self) -> None:
        skill_md = REPO_ROOT / "Skills" / "agent-ops" / "simplify" / "SKILL.md"
        contract = deepcopy(read_reference_contract(skill_md))
        contract["authoring_contract"]["focused_proof"] = (
            "./bin/ask nonexistent arbitrary --dangerously-skip-proof"
        )
        receipt = authoring_contract(
            REPO_ROOT,
            skill_md,
            read_skill_frontmatter_fields(skill_md),
            contract,
            skill_md.read_text(encoding="utf-8"),
        )

        self.assertEqual(receipt["status"], "blocked_validation")
        self.assertIn(
            "authoring_focused_proof_missing",
            {item["rule_id"] for item in receipt["blockers"]},
        )

    def test_extended_canonical_rules_fail_closed_when_a_contract_link_is_missing(
        self,
    ) -> None:
        skill_md = REPO_ROOT / "Skills" / "agent-ops" / "simplify" / "SKILL.md"
        for name, mutate, rule_id in EXTENDED_CANONICAL_CASES:
            with self.subTest(rule=name):
                contract = deepcopy(read_reference_contract(skill_md))
                mutate(contract["authoring_contract"])
                receipt = authoring_contract(REPO_ROOT, skill_md, read_skill_frontmatter_fields(skill_md), contract, skill_md.read_text(encoding="utf-8"))
                self.assertEqual(receipt["status"], "blocked_validation")
                self.assertIn(rule_id, {item["rule_id"] for item in receipt["blockers"]})

    def test_reference_routes_must_stay_under_the_skill_reference_root(self) -> None:
        skill_md = REPO_ROOT / "Skills" / "agent-ops" / "simplify" / "SKILL.md"
        contract = deepcopy(read_reference_contract(skill_md))
        route = contract["authoring_contract"]["reference_routes"][0]
        route["path"] = "references/../../../../README.md"
        text = skill_md.read_text(encoding="utf-8") + "\nreferences/../../../../README.md\n"
        receipt = authoring_contract(
            REPO_ROOT,
            skill_md,
            read_skill_frontmatter_fields(skill_md),
            contract,
            text,
        )

        self.assertEqual(receipt["status"], "blocked_validation")
        self.assertIn(
            "authoring_reference_routes_incomplete",
            {item["rule_id"] for item in receipt["blockers"]},
        )

    def test_rationale_cannot_be_satisfied_by_a_nested_heading(self) -> None:
        skill_md = REPO_ROOT / "Skills" / "agent-ops" / "simplify" / "SKILL.md"
        contract = deepcopy(read_reference_contract(skill_md))
        contract["authoring_contract"]["critical_rules"][0]["rationale_text"] = (
            "Nested-only rationale."
        )
        text = skill_md.read_text(encoding="utf-8") + "\n### Failure Mode\n\nNested-only rationale.\n"
        receipt = authoring_contract(
            REPO_ROOT,
            skill_md,
            read_skill_frontmatter_fields(skill_md),
            contract,
            text,
        )

        self.assertEqual(receipt["status"], "blocked_validation")
        self.assertIn(
            "authoring_critical_rules_incomplete",
            {item["rule_id"] for item in receipt["blockers"]},
        )

    def test_rationale_cannot_be_satisfied_by_a_fenced_example(self) -> None:
        skill_md = REPO_ROOT / "Skills" / "agent-ops" / "simplify" / "SKILL.md"
        contract = deepcopy(read_reference_contract(skill_md))
        contract["authoring_contract"]["critical_rules"][0]["rationale_text"] = (
            "Fenced-only rationale."
        )
        text = skill_md.read_text(encoding="utf-8") + "\n```md\nFenced-only rationale.\n```\n"
        receipt = authoring_contract(
            REPO_ROOT,
            skill_md,
            read_skill_frontmatter_fields(skill_md),
            contract,
            text,
        )

        self.assertEqual(receipt["status"], "blocked_validation")
        self.assertIn(
            "authoring_critical_rules_incomplete",
            {item["rule_id"] for item in receipt["blockers"]},
        )

    def test_critical_rule_rationale_must_occur_exactly_once(self) -> None:
        skill_md = REPO_ROOT / "Skills" / "agent-ops" / "simplify" / "SKILL.md"
        contract = deepcopy(read_reference_contract(skill_md))
        rationale = contract["authoring_contract"]["critical_rules"][0]["rationale_text"]
        text = skill_md.read_text(encoding="utf-8").replace(
            "the behavior-preservation proof false.",
            f"the behavior-preservation proof false. {rationale}",
            1,
        )
        receipt = authoring_contract(
            REPO_ROOT,
            skill_md,
            read_skill_frontmatter_fields(skill_md),
            contract,
            text,
        )

        self.assertEqual(receipt["status"], "blocked_validation")
        self.assertIn(
            "authoring_critical_rules_incomplete",
            {item["rule_id"] for item in receipt["blockers"]},
        )

    def test_fenced_text_cannot_satisfy_steering_or_decision_claims(self) -> None:
        skill_md = REPO_ROOT / "Skills" / "agent-ops" / "simplify" / "SKILL.md"
        contract = deepcopy(read_reference_contract(skill_md))
        authoring = contract["authoring_contract"]
        authoring["steering_terms"][0]["term"] = "fenced-only steering"
        authoring["decision_boundaries"][0]["statement"] = "Fenced-only scope boundary."
        authoring["readiness_evidence"]["not_ready_statement"] = "Fenced-only readiness claim."
        text = skill_md.read_text(encoding="utf-8") + (
            "\n```md\n"
            "fenced-only steering\n"
            "Fenced-only scope boundary.\n"
            "Fenced-only readiness claim.\n"
            "```\n"
        )
        receipt = authoring_contract(
            REPO_ROOT,
            skill_md,
            read_skill_frontmatter_fields(skill_md),
            contract,
            text,
        )

        self.assertEqual(receipt["status"], "blocked_validation")
        self.assertTrue(
            {
                "authoring_steering_vocabulary_invalid",
                "authoring_decision_boundaries_incomplete",
                "authoring_readiness_evidence_incomplete",
            }
            <= {item["rule_id"] for item in receipt["blockers"]},
        )

    def test_explicit_phases_cannot_be_downgraded_to_single(self) -> None:
        skill_md = REPO_ROOT / "Skills" / "product-strategy" / "devrel-hack-coach" / "SKILL.md"
        contract = deepcopy(read_reference_contract(skill_md))
        contract["authoring_contract"]["phase_model"] = {
            "kind": "single",
            "rationale": "Claim a single loop.",
            "phases": [],
        }
        receipt = authoring_contract(
            REPO_ROOT,
            skill_md,
            read_skill_frontmatter_fields(skill_md),
            contract,
            skill_md.read_text(encoding="utf-8"),
        )

        self.assertEqual(receipt["status"], "blocked_validation")
        self.assertIn(
            "authoring_phase_model_invalid",
            {item["rule_id"] for item in receipt["blockers"]},
        )

    def test_phase_headings_must_be_live_and_in_declared_order(self) -> None:
        skill_md = REPO_ROOT / "Skills" / "product-strategy" / "devrel-hack-coach" / "SKILL.md"
        contract = deepcopy(read_reference_contract(skill_md))
        text = skill_md.read_text(encoding="utf-8").replace(
            "### Phase 1 - Interrogate",
            "### Fenced phase",
            1,
        ) + "\n```md\n### Phase 1 - Interrogate\n```\n"
        receipt = authoring_contract(
            REPO_ROOT,
            skill_md,
            read_skill_frontmatter_fields(skill_md),
            contract,
            text,
        )

        self.assertEqual(receipt["status"], "blocked_validation")
        self.assertIn(
            "authoring_phase_model_invalid",
            {item["rule_id"] for item in receipt["blockers"]},
        )

    def test_blocker_matrix_rejects_arbitrary_not_applicable_prose(self) -> None:
        skill_md = REPO_ROOT / "Skills" / "agent-ops" / "simplify" / "SKILL.md"
        contract = deepcopy(read_reference_contract(skill_md))
        matrix = contract["authoring_contract"]["blocker_matrix"]
        matrix["coverage"] = {}
        matrix["not_applicable"] = {
            category: "anything" for category in ("tool", "input", "credential", "permission", "evidence")
        }
        receipt = authoring_contract(
            REPO_ROOT,
            skill_md,
            read_skill_frontmatter_fields(skill_md),
            contract,
            skill_md.read_text(encoding="utf-8"),
        )

        self.assertEqual(receipt["status"], "blocked_validation")
        self.assertIn(
            "authoring_blocker_matrix_incomplete",
            {item["rule_id"] for item in receipt["blockers"]},
        )

    def test_deletion_test_must_match_its_declared_target_scenarios(self) -> None:
        skill_md = REPO_ROOT / "Skills" / "agent-ops" / "simplify" / "SKILL.md"
        contract = deepcopy(read_reference_contract(skill_md))
        target = contract["authoring_contract"]["mutation_targets"][1]
        target["scenario_ids"] = ["edge-empty-diff"]
        target["removal_test"]["scenario_ids"] = ["edge-empty-diff"]
        receipt = authoring_contract(
            REPO_ROOT,
            skill_md,
            read_skill_frontmatter_fields(skill_md),
            contract,
            skill_md.read_text(encoding="utf-8"),
        )

        self.assertEqual(receipt["status"], "blocked_validation")
        self.assertIn(
            "authoring_mutation_targets_incomplete",
            {item["rule_id"] for item in receipt["blockers"]},
        )

    def test_short_duplicate_entrypoint_text_is_not_ignored(self) -> None:
        skill_md = REPO_ROOT / "Skills" / "agent-ops" / "simplify" / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8") + "\nProof matters.\n\nProof matters.\n"
        receipt = authoring_contract(
            REPO_ROOT,
            skill_md,
            read_skill_frontmatter_fields(skill_md),
            read_reference_contract(skill_md),
            text,
        )

        self.assertEqual(receipt["status"], "blocked_validation")
        self.assertIn(
            "authoring_entrypoint_not_minimal",
            {item["rule_id"] for item in receipt["blockers"]},
        )

    def test_fenced_content_keeps_adjacent_paragraphs_separate(self) -> None:
        text = (
            "Repeated paragraph outside the fence.\n"
            "```md\n"
            "Example only.\n"
            "```\n"
            "Repeated paragraph outside the fence.\n"
        )

        self.assertEqual(duplicate_nonempty_paragraphs(text), [])

    def test_missing_scenario_or_typed_fallback_rule_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_md = _write_missing_scenario_skill(root)
            contract = _missing_scenario_contract()
            receipt = authoring_contract(
                root,
                skill_md,
                read_skill_frontmatter_fields(skill_md),
                contract,
                skill_md.read_text(encoding="utf-8"),
            )

        self.assertEqual(receipt["status"], "blocked_validation")
        self.assertIn(
            "authoring_critical_rules_incomplete",
            {item["rule_id"] for item in receipt["blockers"]},
        )

    def test_package_verify_surfaces_authoring_contract_blockers(self) -> None:
        quality = _sdk_quality_values(
            {
                "values": {
                    "authoring_contract": {
                        "status": "blocked_validation",
                        "blockers": [{"rule_id": "authoring_contract_missing"}],
                    }
                }
            }
        )
        blockers = _quality_blockers(quality)

        self.assertEqual(blockers[0]["rule_id"], "skill_authoring_contract_blocked")
        self.assertEqual(
            blockers[0]["evidence"]["blockers"][0]["rule_id"],
            "authoring_contract_missing",
        )

    def test_package_verify_blocks_gold_standard_skill_without_authoring_contract(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = REPO_ROOT / "Skills" / "agent-ops" / "simplify"
            skill_dir = root / "Skills" / "agent-ops" / "simplify"
            copytree(source, skill_dir)
            contract_path = skill_dir / "references" / "contract.yaml"
            contract_text = contract_path.read_text(encoding="utf-8")
            start = contract_text.index("authoring_contract:")
            end = contract_text.index("inputs:", start)
            contract_path.write_text(contract_text[:start] + contract_text[end:], encoding="utf-8")

            receipt = verify_skill_directory(
                root,
                skill_dir / "SKILL.md",
                "Skills/agent-ops/simplify",
                trusted_sources={"internal"},
            )

        self.assertIn(
            "skill_authoring_contract_blocked",
            {item["rule_id"] for item in receipt["blockers"]},
        )


if __name__ == "__main__":
    unittest.main()
