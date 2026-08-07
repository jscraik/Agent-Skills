from __future__ import annotations

from typing import Any

from ask.skills_sdk.ab_profile_contracts import runtime_preflight_identity_matches_lane


def exact_variant_labels(rows: list[Any], *, attr: str = "variant_label") -> bool:
    return [getattr(row, attr) for row in rows] == ["A", "B"]


def argv_output_last_message_path(argv: list[str]) -> str | None:
    if argv.count("--output-last-message") != 1:
        return None
    option_index = argv.index("--output-last-message")
    if option_index + 1 >= len(argv):
        return None
    return argv[option_index + 1]


def approval_policy_from_argv(argv: list[str], start: int = 0) -> str | None:
    args = argv[start:]
    if "--ask-for-approval" in args:
        index = args.index("--ask-for-approval")
        return args[index + 1] if index + 1 < len(args) else None
    values = [args[index + 1].split("=", 1)[1].strip('"\'') for index, value in enumerate(args[:-1]) if value in {"-c", "--config"} and args[index + 1].startswith("approval_policy=")]
    return values[0] if len(values) == 1 else None


def validate_argv_output_last_message_path(argv: list[str], path: str, *, message: str) -> None:
    if argv_output_last_message_path(argv) != path:
        raise ValueError(message)


def validate_plan_gate_identity(gate: Any) -> None:
    if gate.lane != gate.codex_profile or gate.order not in {1, 2}:
        raise ValueError("runtime profile gate identity or order is invalid")
    if gate.judge_profile.codex_profile != gate.codex_profile:
        raise ValueError("judge metadata cannot substitute for the runtime Codex profile")
    if gate.status == "planned" and not runtime_preflight_identity_matches_lane(gate.lane, gate.preflight):
        raise ValueError("planned runtime gate preflight identity does not match its lane")


def validate_receipt_profile_binding(receipt: Any) -> None:
    if receipt.runtime_profile_gates and receipt.codex_profile != receipt.runtime_profile_gates[0].codex_profile:
        raise ValueError("top-level Codex profile must match the first runtime profile gate")


def validate_runtime_gate_prefix(execution_lane: str, gates: list[Any], *, message: str) -> None:
    expected_lanes = ["oss-local", "oss-cloud"] if execution_lane == "all" else [execution_lane]
    if len(gates) > len(expected_lanes):
        raise ValueError(message)
    actual_lanes = [gate.lane for gate in gates]
    actual_orders = [gate.order for gate in gates]
    if actual_lanes != expected_lanes[:len(gates)] or actual_orders != list(range(1, len(gates) + 1)):
        raise ValueError(message)


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
        and _runtime_gate_preflight_facts_admitted(gate, facts)
        and runtime_preflight_identity_matches_lane(gate.lane, gate.preflight)
        and exact_variant_labels(gate.command_plan)
        and exact_variant_labels(gate.variant_results)
        and all(_variant_result_proves_success(result) for result in gate.variant_results)
        and _gate_results_match_command_plan(gate)
    )


def _runtime_gate_preflight_facts_admitted(gate: Any, facts: tuple[Any, ...]) -> bool:
    keys = ("profile_config", "model_catalog", "runtime", "auth", "catalog")
    return all(
        fact.blocker is None and _fact_status_admitted(gate, key, fact.status)
        for key, fact in zip(keys, facts, strict=True)
    )


def _fact_status_admitted(gate: Any, key: str, status: str) -> bool:
    if status == "pass":
        return True
    if gate.lane == "oss-local" and key == "auth" and status == "not_applicable":
        return True
    return key == "runtime" and status == "not_applicable" and gate.preflight._runtime_is_admitted()


def validate_run_receipt_status(receipt: Any) -> None:
    validate_receipt_profile_binding(receipt)
    if receipt.command_variant_labels and receipt.command_variant_labels != ["A", "B"]:
        raise ValueError("A/B run receipts must preserve ordered command variant labels")
    if receipt.status == "completed":
        _validate_completed_run_receipt(receipt)
        return
    if not receipt.blockers:
        raise ValueError("blocked A/B run receipts must include blockers")
    if not receipt.runtime_profile_gates:
        return
    validate_runtime_gate_prefix(
        receipt.execution_lane,
        receipt.runtime_profile_gates,
        message="blocked A/B run receipts must preserve a valid runtime gate prefix",
    )
    blocked_seen = False
    for gate in receipt.runtime_profile_gates:
        if gate.status == "completed" and blocked_seen:
            raise ValueError("blocked A/B run receipts cannot complete a gate after a blocked gate")
        if gate.status != "completed":
            blocked_seen = True
    if not blocked_seen:
        raise ValueError("blocked A/B run receipts require a non-completed runtime gate")


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
    if receipt.command_variant_labels != ["A", "B"]:
        raise ValueError("completed A/B run receipts must include exact command variant labels")
    if not _run_has_consistent_runtime_gates(receipt):
        raise ValueError("A/B run must preserve ordered runtime gates and matching results")
    if any(gate.status != "completed" for gate in receipt.runtime_profile_gates):
        raise ValueError("completed A/B run requires every selected runtime profile gate")
    if receipt.codex_profile != receipt.runtime_profile_gates[0].codex_profile:
        raise ValueError("top-level codex_profile must match runtime_profile_gates[0].codex_profile")


def _run_has_evidence(receipt: Any) -> bool:
    evidence = (
        receipt.skill_a, receipt.skill_b, receipt.fixture, receipt.execution_profile,
        receipt.judge_profile, receipt.codex_profile, receipt.evidence_root, receipt.experiment_id,
    )
    return all(item is not None for item in evidence)


def _run_has_consistent_runtime_gates(receipt: Any) -> bool:
    expected_lanes = ["oss-local", "oss-cloud"] if receipt.execution_lane == "all" else [receipt.execution_lane]
    expected_orders = list(range(1, len(expected_lanes) + 1))
    return (
        [gate.lane for gate in receipt.runtime_profile_gates] == expected_lanes
        and [gate.order for gate in receipt.runtime_profile_gates] == expected_orders
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
        # Local Ollama execution can be proven without an external network
        # claim; the default all-lane contract still requires network evidence.
        and (receipt.network_accessed or receipt.execution_lane == "oss-local")
    )
