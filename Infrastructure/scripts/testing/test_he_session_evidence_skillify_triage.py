from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
HE_ROOT = REPO_ROOT / "Plugins" / "harness-engineering"
TRIAGE_REF = HE_ROOT / "references" / "session-evidence-skillify-triage.md"
SESSION_CONTRACT = HE_ROOT / "references" / "session-evidence-contract.md"
ROUTING_MAP = HE_ROOT / "references" / "routing-map.json"
HE_IMPROVE = HE_ROOT / "skills" / "he-improve" / "SKILL.md"
HE_ROUTER = HE_ROOT / "skills" / "he-router" / "SKILL.md"


def test_session_evidence_contract_links_skillify_triage() -> None:
    contract = SESSION_CONTRACT.read_text(encoding="utf-8")

    assert "session-evidence-skillify-triage.md" in contract
    assert "skill-factory:skillify" in contract
    assert "only invoke" in contract


def test_session_evidence_contract_requires_stage_and_blocker_corroboration() -> None:
    contract = SESSION_CONTRACT.read_text(encoding="utf-8")

    assert "stage_invocation_templates" in contract
    assert "unmapped_signal" in contract
    assert "broad blocker labels" in contract
    assert "same command family" in contract
    assert "evidence-classifier hygiene" in contract


def test_skillify_triage_reference_requires_gates_and_decisions() -> None:
    triage = TRIAGE_REF.read_text(encoding="utf-8")

    required_terms = [
        "coverage-gap",
        "workflow-capture",
        "skillify-new-skill",
        "update-existing-stage",
        "add-reference-material",
        "add-validation-script",
        "no-action-noise",
        "redaction-report.json",
        "Do not pass raw transcripts",
    ]

    for term in required_terms:
        assert term in triage


def test_routing_map_sends_coverage_gap_to_he_improve_first() -> None:
    routing = json.loads(ROUTING_MAP.read_text(encoding="utf-8"))

    decision_rules = {
        rule["rule"]: rule for rule in routing["deterministic_decision_order"]
    }
    triage_rule = decision_rules["coverage-gap-to-skillify-triage"]
    assert triage_rule["route"] == "he-improve before skill-factory:skillify"
    assert "coverage-gap" in triage_rule["signals"]

    routes = {route["intent"]: route for route in routing["routes"]}
    triage_route = routes["coverage-gap-to-skillify-triage"]
    assert triage_route["skill"] == "he-improve"
    assert "skillify-new-skill" in triage_route["output"]
    assert any("redaction" in item for item in triage_route["required_inputs"])


def test_he_entrypoints_reference_triage_guardrails() -> None:
    improve = HE_IMPROVE.read_text(encoding="utf-8")
    router = HE_ROUTER.read_text(encoding="utf-8")

    assert "session-evidence-skillify-triage.md" in improve
    assert "coverage-gap" in improve
    assert "before any new skill package is proposed" in router
    assert "path fragments and bundle names are evidence labels" in router
