from __future__ import annotations

from typing import Any

from ask.skills_sdk.ab_profile_contracts import runtime_preflight_identity_matches_lane


def exact_variant_labels(rows: list[Any], *, attr: str = "variant_label") -> bool:
    return len(rows) == 2 and {getattr(row, attr) for row in rows} == {"A", "B"}


def validate_plan_gate_identity(gate: Any) -> None:
    expected_order = 1 if gate.lane == "oss-local" else 2
    if gate.lane != gate.codex_profile or gate.order != expected_order:
        raise ValueError("runtime profile gate identity or order is invalid")
    if gate.judge_profile.codex_profile != gate.codex_profile:
        raise ValueError("judge metadata cannot substitute for the runtime Codex profile")
    if gate.status == "planned" and not runtime_preflight_identity_matches_lane(gate.lane, gate.preflight):
        raise ValueError("planned runtime gate preflight identity does not match its lane")


def validate_plan_gate_packet(gate: Any) -> None:
    _validate_gate_packet_shape(gate)
    if (gate.status == "planned") != (gate.preflight.admission.status == "pass"):
        raise ValueError("runtime profile gate status must match preflight admission")
    if gate.blockers != gate.preflight.admission.blockers:
        raise ValueError("runtime profile gate blockers must match preflight")
    if gate.status == "planned":
        _validate_planned_gate_packet(gate)
    else:
        _validate_blocked_gate_packet(gate)


def run_gate_is_completed(gate: Any) -> bool:
    facts = (
        gate.preflight.profile_config,
        gate.preflight.model_catalog,
        gate.preflight.runtime,
        gate.preflight.auth,
        gate.preflight.catalog,
    )
    return (
        not gate.blockers
        and gate.preflight.admission.status == "pass"
        and not gate.preflight.admission.blockers
        and all(fact.status in {"pass", "not_applicable"} and fact.blocker is None for fact in facts)
        and runtime_preflight_identity_matches_lane(gate.lane, gate.preflight)
        and exact_variant_labels(gate.command_plan)
        and exact_variant_labels(gate.variant_results)
        and all(_variant_result_proves_success(result) for result in gate.variant_results)
        and _gate_results_match_command_plan(gate)
    )


def validate_run_receipt_status(receipt: Any) -> None:
    if receipt.status == "completed":
        _validate_completed_run_receipt(receipt)
        return
    if not receipt.blockers:
        raise ValueError("blocked A/B run receipts must include blockers")
    blocked_seen = False
    for gate in receipt.runtime_profile_gates:
        if gate.status == "completed" and blocked_seen:
            raise ValueError("blocked A/B run receipts cannot complete a gate after a blocked gate")
        if gate.status != "completed":
            blocked_seen = True


def _validate_gate_packet_shape(gate: Any) -> None:
    if gate.command_plan and not exact_variant_labels(gate.command_plan):
        raise ValueError("runtime profile gate command plan must be empty or include both A/B variants")
    if any(plan.codex_profile != gate.codex_profile for plan in gate.command_plan):
        raise ValueError("runtime profile gate command profile mismatch")


def _validate_planned_gate_packet(gate: Any) -> None:
    if gate.blockers:
        raise ValueError("planned runtime profile gates must not include blockers")
    if gate.command_plan and not exact_variant_labels(gate.command_plan):
        raise ValueError("planned runtime profile gates require both command variants when exposed")


def _validate_blocked_gate_packet(gate: Any) -> None:
    if not gate.blockers:
        raise ValueError("blocked runtime profile gates require typed blockers")
    if gate.command_plan:
        raise ValueError("blocked runtime profile gates cannot expose executable command packets")


def _validate_completed_run_receipt(receipt: Any) -> None:
    if receipt.blockers:
        raise ValueError("completed A/B run receipts must not include blockers")
    if not _run_has_evidence(receipt):
        raise ValueError("completed A/B run receipts must include complete run evidence")
    _validate_completed_run_packets(receipt)
    if not _reports_codex_side_effects(receipt):
        raise ValueError("completed A/B run receipts must report Codex execution side effects")


def _validate_completed_run_packets(receipt: Any) -> None:
    if not exact_variant_labels(receipt.command_plan):
        raise ValueError("completed A/B run receipts must include exactly one command plan per variant")
    if not exact_variant_labels(receipt.variant_results):
        raise ValueError("completed A/B run receipts must include exactly one result per variant")
    if set(receipt.command_variant_labels) != {"A", "B"}:
        raise ValueError("completed A/B run receipts must include exact command variant labels")
    if not _run_has_consistent_runtime_gates(receipt):
        raise ValueError("A/B run must preserve ordered runtime gates and matching oss-local results")
    if any(gate.status != "completed" for gate in receipt.runtime_profile_gates):
        raise ValueError("completed A/B run requires both runtime profile gates")


def _run_has_evidence(receipt: Any) -> bool:
    evidence = (
        receipt.skill_a, receipt.skill_b, receipt.fixture, receipt.execution_profile,
        receipt.judge_profile, receipt.evidence_root, receipt.experiment_id,
    )
    return all(item is not None for item in evidence)


def _run_has_consistent_runtime_gates(receipt: Any) -> bool:
    return (
        [gate.lane for gate in receipt.runtime_profile_gates] == ["oss-local", "oss-cloud"]
        and receipt.command_plan == receipt.runtime_profile_gates[0].command_plan
        and receipt.variant_results == receipt.runtime_profile_gates[0].variant_results
        and all(_gate_results_match_command_plan(gate) for gate in receipt.runtime_profile_gates)
    )


def _gate_results_match_command_plan(gate: Any) -> bool:
    plans = {plan.variant_label: plan.command_argv for plan in gate.command_plan}
    return all(plans.get(result.variant_label) == result.command_argv for result in gate.variant_results)


def _variant_result_proves_success(result: Any) -> bool:
    return (
        result.status == "pass"
        and result.exit_code == 0
        and not result.blockers
        and result.output_last_message_digest is not None
    )


def _reports_codex_side_effects(receipt: Any) -> bool:
    return (
        receipt.mutation_performed
        and receipt.provider_invoked
        and receipt.codex_exec_invoked
        and receipt.network_accessed
    )
