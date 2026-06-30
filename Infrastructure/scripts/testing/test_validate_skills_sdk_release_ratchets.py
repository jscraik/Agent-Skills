from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "validate_skills_sdk_release_ratchets.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("validate_skills_sdk_release_ratchets", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_fixture(
    root: Path,
    *,
    leak_package_ref: bool = False,
    include_security: bool = True,
    mention_capsule_routing: bool = False,
    include_evidence: bool = True,
) -> None:
    _write_central_rubric(root)
    _write_pattern_report(root)
    _write_steering_ledger(root)
    skill = root / "Skills" / "agent-ops" / "fixture-skill"
    refs = skill / "references"
    refs.mkdir(parents=True)
    _write_skill_entrypoint(skill, leak_package_ref, mention_capsule_routing)
    _write_contract(refs, include_security)
    _write_reference_files(refs)
    if include_evidence:
        _write_release_evidence(root, skill)


def _write_central_rubric(root: Path) -> None:
    central = root / "Infrastructure" / "config" / "skills-sdk"
    central.mkdir(parents=True)
    (central / "gold-standard-rubric.v1.json").write_text(
        json.dumps(
            {
                "schema_version": "skills-sdk.gold-standard-rubric.v1",
                "rubric_id": "skills-sdk.gold-standard.v1",
                "rubric_version": "v1",
                "quality_criteria": {
                    "domain_artifact_classification": {},
                    "trigger_boundary": {},
                    "construction_structure_steering_pruning": {},
                    "reference_invocation": {},
                    "progressive_disclosure": {},
                    "scenario_evidence_quality": {},
                    "evidence_lane_separation": {},
                },
            }
        ),
        encoding="utf-8",
    )


def _write_pattern_report(root: Path) -> None:
    reports = root / ".harness" / "reports"
    reports.mkdir(parents=True)
    patterns = [
        "central-rubric-drift",
        "knowledgeos-reference-shape-drift",
        "reference-heading-invocation-drift",
        "yaml-parser-parity-drift",
        "reference-boundary-drift",
        "tessl-lane-overclaim",
        "skill-factory-pipeline-drift",
        "security-lane-gap",
        "advisory-carry-forward",
        "stale-runtime-handle",
    ]
    (reports / "skills-sdk-ratchet-patterns.json").write_text(
        json.dumps({"schema_version": "skills-sdk-ratchet-patterns/v1", "patterns": [{"id": p} for p in patterns]}),
        encoding="utf-8",
    )


def _write_steering_ledger(root: Path) -> None:
    quality = root / ".harness" / "quality"
    quality.mkdir(parents=True)
    (quality / "steering-uptake.md").write_text(
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-06-29 | stale wait handle | stale wait recurrence | direct commands only | validator | pass | validated |\n",
        encoding="utf-8",
    )


def _write_skill_entrypoint(skill: Path, leak_package_ref: bool, mention_capsule_routing: bool) -> None:
    package_ref_line = "- Read references/source-context.yaml for package context.\n" if leak_package_ref else ""
    routing_line = "- Read references/knowledge-capsule-routing.md before capsule bodies.\n" if mention_capsule_routing else ""
    (skill / "SKILL.md").write_text(
        f"""---
name: fixture-skill
description: Use when a user asks to test release ratchets.
---

# Fixture Skill

## Workflow

Run the fixture.

## Progressive Disclosure

- Read references/details.md for task detail.
{routing_line}
{package_ref_line}""",
        encoding="utf-8",
    )


def _contract_commands(include_security: bool) -> list[str]:
    commands = [
        '  - "./bin/ask skills package verify Skills/agent-ops/fixture-skill --json --robot"',
        '  - "./bin/ask sdk eval scenario-quality Skills/agent-ops/fixture-skill --preview --json --robot"',
    ]
    if include_security:
        commands.append('  - "./bin/ask sdk security risk-modes Skills/agent-ops/fixture-skill --preview --json --robot"')
    return commands


def _write_contract(refs: Path, include_security: bool) -> None:
    (refs / "contract.yaml").write_text(
        "\n".join(
            [
                "schema_version: 1",
                "skill: fixture-skill",
                "rubric_profile: skills-sdk.gold-standard.v1",
                "purpose: Test release ratchets.",
                "inputs:",
                "  - user_request",
                "  - capability",
                "outputs:",
                "  - result",
                "  - capability",
                "quality_criteria:",
                "  capability_selection:",
                "    alpha: alpha task",
                "evidence_requirements:",
                "  - Evidence is required.",
                "commands:",
                *_contract_commands(include_security),
                'source_context: "references/source-context.yaml"',
                'source_provenance: "references/source-provenance.md"',
            ]
        ),
        encoding="utf-8",
    )


def _write_reference_files(refs: Path) -> None:
    (refs / "details.md").write_text("# Fixture Skill Details\n", encoding="utf-8")
    (refs / "source-context.yaml").write_text("source: fixture\n", encoding="utf-8")
    (refs / "source-provenance.md").write_text("# Source Provenance\n", encoding="utf-8")
    (refs / "evals.yaml").write_text(
        """schema_version: "2.0"
cases:
- id: happy-main
  category: happy
  eval_modes:
  - smoke
  - release
  prompt: Run the fixture.
  task: Run the fixture.
  given: A valid fixture request.
  should: Return fixture evidence.
  acceptance:
  - type: expected_signal
    value: Artifact evidence is present.
  - type: not_regex
    value: "(?i)unsafe"
  deterministic_checks:
    forbidden_commands:
    - curl
""",
        encoding="utf-8",
    )


def _write_release_evidence(root: Path, skill: Path) -> None:
    evidence = root / ".harness" / "evidence" / "handoff" / "fixture-skill"
    evidence.mkdir(parents=True)
    gate = root / ".harness" / "evidence" / "factory-gates" / "fixture-skill"
    gate.mkdir(parents=True)
    _write_factory_gate(gate)
    _write_scenario_sources(evidence)
    _write_security_receipt(evidence)
    _write_plugin_shape(evidence)
    _write_repair_loop(evidence)
    _write_gate_chain(root, evidence)


def _write_factory_gate(gate: Path) -> None:
    (gate / "factory-gate.json").write_text(
        json.dumps(
            {
                "schema_version": "factory-gate/v1",
                "target": "Skills/agent-ops/fixture-skill",
                "operation": "harden",
                "user_outcome": "Release a fixture skill through the SDK pipeline.",
                "copied_assumption": "Do not copy a template without proof.",
                "smallest_effective_mechanism": "IMPROVE_EXISTING",
                "artifact_decision": "IMPROVE_EXISTING",
                "proof_needed": ["package verify", "scenario parity", "security preview"],
            }
        ),
        encoding="utf-8",
    )


def _write_scenario_sources(evidence: Path) -> None:
    scenario_ids = ["happy-main"]
    (evidence / "scenario-sources.json").write_text(
        json.dumps(
            {
                "schema_version": "skills-sdk.scenario-sources.v1",
                "scenario_ids": scenario_ids,
                "receipts": [
                    {"lane": "oss-local", "scenario_ids": scenario_ids},
                    {"lane": "oss-cloud", "scenario_ids": scenario_ids},
                    {"lane": "tessl-dry-run", "scenario_ids": scenario_ids},
                    {"lane": "tessl-score", "scenario_ids": scenario_ids},
                ],
                "exclusions": [],
            }
        ),
        encoding="utf-8",
    )


def _write_security_receipt(evidence: Path) -> None:
    security_payload = {
        "schema_version": "skills-sdk.security-risk-modes.v1",
        "status": "pass",
        "command": "./bin/ask sdk security risk-modes Skills/agent-ops/fixture-skill --preview --json --robot",
        "preview": True,
        "risk_modes": {
            "prompt_injection": "pass",
            "unsafe_command_escalation": "pass",
            "secret_redaction": "pass",
            "external_url_trust": "pass",
            "local_path_leakage": "pass",
            "permission_profile": "pass",
            "mcp_tool_side_effects": "pass",
        },
    }
    (evidence / "security-risk-modes.json").write_text(json.dumps(security_payload), encoding="utf-8")


def _write_plugin_shape(evidence: Path) -> None:
    (evidence / "plugin-shape.json").write_text(
        json.dumps(
            {
                "schema_version": "skills-sdk.plugin-shape-parity.v1",
                "target_kind": "standalone_skill",
                "workspace": "jscraik",
                "private": True,
                "openai_skill_shape": "pass",
                "tessl_plugin_shape": "not_applicable",
                "files": ["SKILL.md", "agents/openai.yaml", "references/contract.yaml"],
            }
        ),
        encoding="utf-8",
    )


def _write_repair_loop(evidence: Path) -> None:
    (evidence / "repair-loop.json").write_text(
        json.dumps({"schema_version": "skills-sdk.repair-loop.v1", "attempts": []}),
        encoding="utf-8",
    )


def _write_gate_chain(root: Path, evidence: Path) -> None:
    gate_ids = [
        "sdk_start",
        "strict_audit",
        "package_verify",
        "security_risk_modes",
        "scenario_quality",
        "scorer_quality",
        "scorer_calibration",
        "oss_local",
        "oss_cloud",
        "tessl_local_proof",
        "tessl_dry_run",
        "handoff_readiness",
    ]
    gates = []
    for index, gate_id in enumerate(gate_ids):
        receipt = _write_gate_receipt(evidence, gate_id)
        gates.append(_gate_chain_entry(root, gate_ids, index, gate_id, receipt))
    (evidence / "gate-chain.json").write_text(
        json.dumps(
            {
                "schema_version": "skills-sdk.gate-chain.v1",
                "target": "Skills/agent-ops/fixture-skill",
                "repo_head": "fixture-head",
                "gates": gates,
            }
        ),
        encoding="utf-8",
    )


def _write_gate_receipt(evidence: Path, gate_id: str) -> Path:
    receipt = evidence / f"{gate_id}.json"
    receipt.write_text(
        json.dumps(
            {
                "schema_version": "skills-sdk.receipt.v1",
                "status": "pass",
                "gate_id": gate_id,
                "tessl_lane": _tessl_lane(gate_id),
                "scenario_ids": ["happy-main"] if gate_id in {"oss_local", "oss_cloud", "tessl_dry_run"} else [],
            }
        ),
        encoding="utf-8",
    )
    return receipt


def _tessl_lane(gate_id: str) -> str | None:
    if gate_id == "tessl_local_proof":
        return "local_proof"
    if gate_id == "tessl_dry_run":
        return "dry_run"
    return None


def _gate_chain_entry(root: Path, gate_ids: list[str], index: int, gate_id: str, receipt: Path) -> dict[str, object]:
    return {
        "id": gate_id,
        "status": "pass",
        "command": f"./bin/ask fixture {gate_id}",
        "receipt_path": receipt.relative_to(root).as_posix(),
        "previous_gate": gate_ids[index - 1] if index else None,
        "next_allowed_gate": gate_ids[index + 1] if index + 1 < len(gate_ids) else None,
        "what_this_proves": [f"{gate_id} evidence exists"],
        "what_this_does_not_prove": ["external registry release"],
    }


def test_release_ratchets_pass_for_valid_fixture() -> None:
    module = _load_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_fixture(root)

        payload = module.validate(root, "Skills/agent-ops/fixture-skill")

    assert payload["status"] == "pass"
    assert payload["finding_count"] == 0


def test_release_ratchets_allow_target_gate_prefix_without_future_receipts() -> None:
    module = _load_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_fixture(root)
        evidence = root / ".harness" / "evidence" / "handoff" / "fixture-skill"
        chain = evidence / "gate-chain.json"
        payload = json.loads(chain.read_text(encoding="utf-8"))
        payload["gates"] = payload["gates"][:4]
        chain.write_text(json.dumps(payload), encoding="utf-8")
        for future_receipt in (
            "scenario-sources.json",
            "scenario_quality.json",
            "scorer_quality.json",
            "scorer_calibration.json",
            "oss_local.json",
            "oss_cloud.json",
            "tessl_local_proof.json",
            "tessl_dry_run.json",
            "handoff_readiness.json",
            "repair-loop.json",
        ):
            path = evidence / future_receipt
            if path.exists():
                path.unlink()

        prefix_payload = module.validate(root, "Skills/agent-ops/fixture-skill", target_gate="security_risk_modes")
        full_payload = module.validate(root, "Skills/agent-ops/fixture-skill")

    assert prefix_payload["status"] == "pass"
    assert prefix_payload["target_gate"] == "security_risk_modes"
    assert prefix_payload["finding_count"] == 0
    assert full_payload["status"] == "fail"
    full_gate = next(check for check in full_payload["checks"] if check["code"] == "ordered_gate_chain")
    assert "scenario_quality" in full_gate["evidence"]["missing_gates"]


def test_release_ratchets_target_gate_ignores_future_gate_failures() -> None:
    module = _load_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_fixture(root)
        chain = root / ".harness" / "evidence" / "handoff" / "fixture-skill" / "gate-chain.json"
        payload = json.loads(chain.read_text(encoding="utf-8"))
        for gate in payload["gates"]:
            if gate["id"] == "oss_cloud":
                gate["status"] = "fail"
                gate["what_this_proves"] = ""
        chain.write_text(json.dumps(payload), encoding="utf-8")

        prefix_payload = module.validate(root, "Skills/agent-ops/fixture-skill", target_gate="security_risk_modes")
        full_payload = module.validate(root, "Skills/agent-ops/fixture-skill")

    assert prefix_payload["status"] == "pass"
    full_gate = next(check for check in full_payload["checks"] if check["code"] == "ordered_gate_chain")
    assert "oss_cloud" in full_gate["evidence"]["bad_status"]


def test_release_ratchets_target_gate_maps_receipt_filenames_before_advisory_filtering() -> None:
    module = _load_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_fixture(root)
        evidence = root / ".harness" / "evidence" / "handoff" / "fixture-skill"
        scenario_sources = evidence / "scenario-sources.json"
        payload = json.loads(scenario_sources.read_text(encoding="utf-8"))
        payload["advisories"] = [{"id": "future-scenario-advisory"}]
        scenario_sources.write_text(json.dumps(payload), encoding="utf-8")

        package_payload = module.validate(root, "Skills/agent-ops/fixture-skill", target_gate="package_verify")
        full_payload = module.validate(root, "Skills/agent-ops/fixture-skill")

    assert package_payload["status"] == "pass"
    carried = next(check for check in full_payload["checks"] if check["code"] == "no_carried_advisories")
    assert ".harness/evidence/handoff/fixture-skill/scenario-sources.json:advisories" in carried["evidence"]["carried"]


def test_release_ratchets_allow_skill_to_point_at_capsule_routing() -> None:
    module = _load_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_fixture(root, mention_capsule_routing=True)

        payload = module.validate(root, "Skills/agent-ops/fixture-skill")

    boundary = next(check for check in payload["checks"] if check["code"] == "reference_boundary")
    assert boundary["status"] == "pass"


def test_release_ratchets_fail_for_boundary_and_security_drift() -> None:
    module = _load_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_fixture(root, leak_package_ref=True, include_security=False)

        payload = module.validate(root, "Skills/agent-ops/fixture-skill")

    assert payload["status"] == "fail"
    failed = {check["code"] for check in payload["checks"] if check["status"] != "pass"}
    assert "reference_boundary" in failed
    assert "skill_factory_pipeline_commands" in failed
    assert "security_risk_mode_lane" in failed


def test_release_ratchets_fail_without_factory_gate_receipt() -> None:
    module = _load_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_fixture(root)
        gate = root / ".harness" / "evidence" / "factory-gates" / "fixture-skill" / "factory-gate.json"
        gate.unlink()

        payload = module.validate(root, "Skills/agent-ops/fixture-skill")

    failed = {check["code"] for check in payload["checks"] if check["status"] != "pass"}
    assert "factory_gate_receipt" in failed


def test_release_ratchets_fail_when_gate_chain_is_out_of_order() -> None:
    module = _load_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_fixture(root)
        chain = root / ".harness" / "evidence" / "handoff" / "fixture-skill" / "gate-chain.json"
        payload = json.loads(chain.read_text(encoding="utf-8"))
        payload["gates"][1], payload["gates"][2] = payload["gates"][2], payload["gates"][1]
        chain.write_text(json.dumps(payload), encoding="utf-8")

        result = module.validate(root, "Skills/agent-ops/fixture-skill")

    gate_chain = next(check for check in result["checks"] if check["code"] == "ordered_gate_chain")
    assert gate_chain["status"] == "fail"
    assert gate_chain["evidence"]["order_ok"] is False


def test_release_ratchets_fail_on_carried_advisories() -> None:
    module = _load_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_fixture(root)
        receipt = root / ".harness" / "evidence" / "handoff" / "fixture-skill" / "scenario_quality.json"
        receipt.write_text(json.dumps({"status": "pass", "advisories": [{"id": "weak-case"}]}), encoding="utf-8")

        payload = module.validate(root, "Skills/agent-ops/fixture-skill")

    failed = {check["code"] for check in payload["checks"] if check["status"] != "pass"}
    assert "no_carried_advisories" in failed
    assert "ordered_gate_chain" in failed


def test_release_ratchets_fail_on_scenario_set_drift() -> None:
    module = _load_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_fixture(root)
        sources = root / ".harness" / "evidence" / "handoff" / "fixture-skill" / "scenario-sources.json"
        payload = json.loads(sources.read_text(encoding="utf-8"))
        payload["receipts"][0]["scenario_ids"] = ["different-case"]
        sources.write_text(json.dumps(payload), encoding="utf-8")

        result = module.validate(root, "Skills/agent-ops/fixture-skill")

    parity = next(check for check in result["checks"] if check["code"] == "scenario_set_parity")
    assert parity["status"] == "fail"
    assert parity["evidence"]["receipt_mismatches"][0]["lane"] == "oss-local"


def test_release_ratchets_fail_on_unrouted_reference() -> None:
    module = _load_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_fixture(root)
        refs = root / "Skills" / "agent-ops" / "fixture-skill" / "references"
        (refs / "unrouted-reference.md").write_text("# Unrouted Reference\n", encoding="utf-8")

        payload = module.validate(root, "Skills/agent-ops/fixture-skill")

    failed = {check["code"] for check in payload["checks"] if check["status"] != "pass"}
    assert "reference_routing_completeness" in failed


def test_release_ratchets_fail_on_incomplete_security_receipt() -> None:
    module = _load_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_fixture(root)
        receipt = root / ".harness" / "evidence" / "handoff" / "fixture-skill" / "security-risk-modes.json"
        payload = json.loads(receipt.read_text(encoding="utf-8"))
        del payload["risk_modes"]["prompt_injection"]
        receipt.write_text(json.dumps(payload), encoding="utf-8")

        result = module.validate(root, "Skills/agent-ops/fixture-skill")

    security = next(check for check in result["checks"] if check["code"] == "security_package_gate")
    assert security["status"] == "fail"
    assert "prompt_injection" in security["evidence"]["missing_modes"]


def test_release_ratchets_fail_on_plugin_shape_policy_drift() -> None:
    module = _load_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_fixture(root)
        receipt = root / ".harness" / "evidence" / "handoff" / "fixture-skill" / "plugin-shape.json"
        payload = json.loads(receipt.read_text(encoding="utf-8"))
        payload["target_kind"] = "plugin"
        payload["private"] = False
        payload["files"] = ["SKILL.md"]
        receipt.write_text(json.dumps(payload), encoding="utf-8")

        result = module.validate(root, "Skills/agent-ops/fixture-skill")

    shape = next(check for check in result["checks"] if check["code"] == "plugin_shape_parity")
    assert shape["status"] == "fail"
    assert shape["evidence"]["private_ok"] is False


def test_release_ratchets_fail_on_unclassified_repair_regression() -> None:
    module = _load_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_fixture(root)
        repair = root / ".harness" / "evidence" / "handoff" / "fixture-skill" / "repair-loop.json"
        repair.write_text(
            json.dumps(
                {
                    "schema_version": "skills-sdk.repair-loop.v1",
                    "attempts": [
                        {
                            "id": "pass-2",
                            "fixed_cases": ["a"],
                            "regressed_cases": [{"id": "happy-main"}],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        result = module.validate(root, "Skills/agent-ops/fixture-skill")

    repair_loop = next(check for check in result["checks"] if check["code"] == "repair_loop_monotonicity")
    assert repair_loop["status"] == "fail"
    assert repair_loop["evidence"]["unclassified_regressions"]


def test_release_ratchets_ignore_missing_regressed_cases_on_no_regression_attempt() -> None:
    module = _load_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_fixture(root)
        repair = root / ".harness" / "evidence" / "handoff" / "fixture-skill" / "repair-loop.json"
        repair.write_text(
            json.dumps(
                {
                    "schema_version": "skills-sdk.repair-loop.v1",
                    "attempts": [
                        {
                            "id": "pass-2",
                            "fixed_cases": ["a"],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        result = module.validate(root, "Skills/agent-ops/fixture-skill")

    repair_loop = next(check for check in result["checks"] if check["code"] == "repair_loop_monotonicity")
    assert repair_loop["status"] == "pass"


def test_release_ratchets_fail_unjustified_legacy_knowledgeos_capsule_subdir() -> None:
    module = _load_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_fixture(root)
        refs = root / "Skills" / "agent-ops" / "fixture-skill" / "references"
        capsules = refs / "knowledge-capsules"
        capsules.mkdir()
        (capsules / "one.md").write_text("# One\n", encoding="utf-8")
        (refs / "knowledge-capsule.manifest.yaml").write_text(
            """schema_version: knowledge-os.knowledge-capsule-manifest.v1
capsules:
  - target_path: references/knowledge-capsules/one.md
""",
            encoding="utf-8",
        )
        (refs / "knowledge-capsule-routing.md").write_text(
            "# Routing\n\n- references/knowledge-capsules/one.md\n",
            encoding="utf-8",
        )

        payload = module.validate(root, "Skills/agent-ops/fixture-skill")

    failed = {check["code"] for check in payload["checks"] if check["status"] != "pass"}
    assert "knowledgeos_reference_shape" in failed


def test_release_ratchets_fail_non_invocable_reference_headings() -> None:
    module = _load_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_fixture(root)
        refs = root / "Skills" / "agent-ops" / "fixture-skill" / "references"
        (refs / "details.md").write_text("# Details\n", encoding="utf-8")

        payload = module.validate(root, "Skills/agent-ops/fixture-skill")

    heading = next(check for check in payload["checks"] if check["code"] == "reference_heading_invocation")
    assert heading["status"] == "fail"
    assert heading["evidence"]["weak_headings"] == [
        {
            "path": "Skills/agent-ops/fixture-skill/references/details.md",
            "title": "Details",
            "reason": "missing_generic_or_filename_misaligned_h1",
        }
    ]


def test_release_ratchets_accept_justified_legacy_knowledgeos_capsule_subdir() -> None:
    module = _load_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        _write_fixture(root)
        refs = root / "Skills" / "agent-ops" / "fixture-skill" / "references"
        capsules = refs / "knowledge-capsules"
        capsules.mkdir()
        (capsules / "one.md").write_text("# One\n", encoding="utf-8")
        (refs / "knowledge-capsule.manifest.yaml").write_text(
            """schema_version: knowledge-os.knowledge-capsule-manifest.v1
capsule_storage:
  allow_legacy_subdirectory: true
  justification: compatibility migration for an existing package layout
capsules:
  - target_path: references/knowledge-capsules/one.md
""",
            encoding="utf-8",
        )
        (refs / "knowledge-capsule-routing.md").write_text(
            "# Routing\n\n- references/knowledge-capsules/one.md\n",
            encoding="utf-8",
        )

        payload = module.validate(root, "Skills/agent-ops/fixture-skill")

    shape = next(check for check in payload["checks"] if check["code"] == "knowledgeos_reference_shape")
    assert shape["status"] == "pass"
