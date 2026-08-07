"""Independent deterministic checks for a declared skill authoring contract."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from ask.skills_sdk.skill_authoring_contract_markdown import (
    duplicate_nonempty_paragraphs,
    explicit_phase_headings,
    markdown_heading_position,
    normalized_text,
)
from ask.skills_sdk.skill_authoring_contract_support import (
    BLOCKER_CATEGORIES,
    CheckSpec,
    DECISION_BOUNDARY_KINDS,
    ENTRYPOINT_SECTION_ROLES,
    READINESS_LANES,
    AuthoringContext,
    add_check,
    as_bool,
    contained_regular_reference,
    expected_behavior_proof,
    expected_focused_proof,
    is_nonempty_text,
    valid_scenario_ids,
)


_TYPED_BLOCKER_RE = re.compile(r"^blocked_[a-z0-9_]+$")
_TYPED_OUTCOME_RE = re.compile(
    r"^(?:blocked_[a-z0-9_]+|ask_for_input|no_justified_edit)$"
)


@dataclass(frozen=True)
class RuleBindings:
    ids: set[str]
    scenario_ids: set[str]
    scenarios_by_id: dict[str, set[str]]


@dataclass(frozen=True)
class RouteBindings:
    ids: set[str]
    scenarios_by_id: dict[str, set[str]]


def validate_schema(context: AuthoringContext, expected: str) -> None:
    actual = context.contract.get("schema_version")
    add_check(context, CheckSpec(
        "authoring_contract_schema",
        actual == expected,
        {"actual": actual, "expected": expected},
        "authoring_contract_schema_invalid",
        "authoring_contract must declare the current Skills SDK authoring-contract schema version.",
    ))


def validate_primary_job(context: AuthoringContext) -> None:
    primary_job = context.contract.get("primary_job")
    fields = ("outcome", "refusal_boundary")
    ok = isinstance(primary_job, dict) and all(
        is_nonempty_text(primary_job.get(field)) for field in fields
    )
    add_check(context, CheckSpec(
        "authoring_primary_job",
        ok,
        {"declared": primary_job},
        "authoring_primary_job_incomplete",
        "Declare one primary outcome and one explicit refusal boundary.",
    ))


def validate_invocation(context: AuthoringContext) -> None:
    invocation = _mapping(context.contract.get("invocation"))
    mode = invocation.get("mode")
    disabled = as_bool(context.frontmatter.get("disable-model-invocation"))
    mode_ok = mode in {"user", "model", "both"}
    consistency_ok = mode == "user" if disabled else mode in {"model", "both"}
    load_ok = invocation.get("context_load") in {"low", "bounded", "high"}
    control_ok = is_nonempty_text(invocation.get("load_control"))
    rationale_ok = is_nonempty_text(invocation.get("rationale"))
    add_check(context, CheckSpec(
        "authoring_invocation_mode",
        all([mode_ok, consistency_ok, load_ok, control_ok, rationale_ok]),
        _invocation_evidence(invocation, disabled),
        "authoring_invocation_mode_invalid",
        "Declare user, model, or both invocation with rationale, bounded context/operator load, and a load control consistent with disable-model-invocation.",
    ))


def validate_entrypoint_budget(context: AuthoringContext) -> None:
    entrypoint = _mapping(context.contract.get("entrypoint"))
    max_lines = entrypoint.get("max_lines")
    roles = entrypoint.get("section_roles")
    duplicates = duplicate_nonempty_paragraphs(context.text)
    budget_ok = isinstance(max_lines, int) and 0 < max_lines <= 360
    within_budget = budget_ok and len(context.text.splitlines()) <= max_lines
    roles_ok = _valid_section_roles(roles, context.headings)
    no_duplicates = not context.duplicate_headings and not duplicates
    ok = all([within_budget, roles_ok, entrypoint.get("reject_duplicate_paragraphs") is True, no_duplicates])
    add_check(context, CheckSpec(
        "authoring_entrypoint_budget",
        ok,
        _entrypoint_evidence(context, max_lines, roles, duplicates),
        "authoring_entrypoint_not_minimal",
        "Keep the entrypoint within the 360-line split budget, assign every direct section a routing/action/safety/output/proof/reference role, and remove duplicate paragraphs.",
    ))


def validate_critical_rules(context: AuthoringContext) -> RuleBindings:
    rows = _list(context.contract.get("critical_rules"))
    ids: set[str] = set()
    all_scenarios: set[str] = set()
    bindings: dict[str, set[str]] = {}
    invalid: list[dict[str, Any]] = []
    for row in rows:
        result = _critical_rule_result(row, ids, context)
        if result is None:
            invalid.append(_critical_rule_evidence(row, context))
            continue
        rule_id, cases = result
        ids.add(rule_id)
        all_scenarios.update(cases)
        bindings[rule_id] = cases
    ok = bool(ids) and not invalid and "no-silent-fallback" in ids
    add_check(context, CheckSpec(
        "authoring_critical_rules",
        ok,
        _critical_rules_evidence(ids, invalid, context.scenario_ids),
        "authoring_critical_rules_incomplete",
        "Critical rules need unique IDs, an in-skill rationale sentence, typed blockers, mapped scenarios, and a no-silent-fallback rule.",
    ))
    return RuleBindings(ids, all_scenarios, bindings)


def validate_steering_terms(context: AuthoringContext) -> None:
    rows = _list(context.contract.get("steering_terms"))
    terms: set[str] = set()
    valid = True
    for row in rows:
        term = row.get("term") if isinstance(row, dict) else None
        definition = row.get("definition") if isinstance(row, dict) else None
        row_ok = is_nonempty_text(term) and is_nonempty_text(definition)
        unique = isinstance(term, str) and term.casefold() not in terms
        if not row_ok or not unique:
            valid = False
            continue
        terms.add(term.casefold())
    absent_terms = sorted(term for term in terms if term not in normalized_text(context.entrypoint_text))
    add_check(context, CheckSpec(
        "authoring_steering_vocabulary",
        bool(rows) and valid and not absent_terms,
        {"terms": sorted(terms), "absent_terms": absent_terms},
        "authoring_steering_vocabulary_invalid",
        "Declare stable, uniquely defined steering terms and use each one in the skill entrypoint's critical decisions.",
    ))


def validate_phase_model(context: AuthoringContext) -> None:
    model = _mapping(context.contract.get("phase_model"))
    kind = model.get("kind")
    rows = _list(model.get("phases"))
    phase_data, invalid = _phase_rows(rows, context)
    explicit = explicit_phase_headings(context.entrypoint_text)
    single_ok = kind == "single" and not rows and not explicit
    phased_ok = _valid_phased_model(kind, phase_data, invalid, explicit)
    rationale_ok = is_nonempty_text(model.get("rationale"))
    add_check(context, CheckSpec(
        "authoring_phase_model",
        rationale_ok and (single_ok or phased_ok),
        _phase_evidence(kind, phase_data, explicit, invalid),
        "authoring_phase_model_invalid",
        "Declare whether the skill is single-phase or phased. A phased skill needs ordered named headings, entry conditions, exit artifacts, and controlled scenario bindings.",
    ))


def validate_decision_boundaries(context: AuthoringContext) -> None:
    rows = _list(context.contract.get("decision_boundaries"))
    ids: set[str] = set()
    kinds: set[str] = set()
    invalid: list[dict[str, Any]] = []
    for row in rows:
        result = _decision_boundary_result(row, ids, kinds, context)
        if result is None:
            invalid.append(_boundary_evidence(row))
            continue
        boundary_id, kind = result
        ids.add(boundary_id)
        kinds.add(kind)
    add_check(context, CheckSpec(
        "authoring_decision_boundaries",
        kinds == DECISION_BOUNDARY_KINDS and not invalid,
        {"ids": sorted(ids), "kinds": sorted(kinds), "invalid": invalid},
        "authoring_decision_boundaries_incomplete",
        "State one unambiguous, scenario-bound decision for scope, authority, side effects, stop conditions, and evidence claims.",
    ))


def validate_blocker_matrix(context: AuthoringContext) -> None:
    matrix = _mapping(context.contract.get("blocker_matrix"))
    coverage = _mapping(matrix.get("coverage"))
    not_applicable = _mapping(matrix.get("not_applicable"))
    covered: set[str] = set()
    invalid: list[dict[str, Any]] = []
    for category in BLOCKER_CATEGORIES:
        if _valid_blocker_condition(coverage.get(category), context.scenario_ids):
            covered.add(category)
        elif _valid_blocker_exception(category, not_applicable.get(category), context):
            covered.add(category)
        else:
            invalid.append(_blocker_matrix_failure(category, not_applicable))
    add_check(context, CheckSpec(
        "authoring_blocker_matrix",
        covered == BLOCKER_CATEGORIES and not invalid,
        {"covered": sorted(covered), "invalid": invalid},
        "authoring_blocker_matrix_incomplete",
        "For inputs and evidence, declare scenario-bound typed blockers. Tools, credentials, and permissions may be not applicable only with an in-skill statement, rationale, and scenario binding.",
    ))


def validate_reference_routes(context: AuthoringContext) -> RouteBindings:
    rows = _list(context.contract.get("reference_routes"))
    ids: set[str] = set()
    bindings: dict[str, set[str]] = {}
    invalid: list[dict[str, Any]] = []
    for row in rows:
        result = _reference_route_result(row, ids, context)
        if result is None:
            invalid.append(_route_evidence(row))
            continue
        route_id, cases = result
        ids.add(route_id)
        bindings[route_id] = cases
    add_check(context, CheckSpec(
        "authoring_reference_routes",
        bool(rows) and not invalid,
        {"route_ids": sorted(ids), "invalid": invalid},
        "authoring_reference_routes_incomplete",
        "Every declared authoring reference route needs a unique ID, an in-entrypoint package-local path, and an explicit read_when condition.",
    ))
    return RouteBindings(ids, bindings)


def validate_output_contract(context: AuthoringContext) -> None:
    output = _mapping(context.contract.get("output_contract"))
    fields = _normalized_fields(output.get("required_fields"))
    artifact_locations = output.get("artifact_locations")
    provenance_fields = output.get("provenance_fields")
    has_required_fields = _output_fields_complete(fields)
    artifacts_ok = _nonempty_text_list(artifact_locations)
    provenance_ok = _nonempty_text_list(provenance_fields)
    add_check(context, CheckSpec(
        "authoring_output_contract",
        all([has_required_fields, artifacts_ok, provenance_ok]),
        _output_evidence(fields, artifact_locations, provenance_fields),
        "authoring_output_contract_incomplete",
        "Output contracts must require outcome/status, evidence/provenance, validation, residual risk, artifact locations, and provenance fields.",
    ))


def validate_mutation_targets(
    context: AuthoringContext,
    rules: RuleBindings,
    routes: RouteBindings,
) -> None:
    rows = _list(context.contract.get("mutation_targets"))
    invalid = [
        _mutation_evidence(row)
        for row in rows
        if not _valid_mutation_target(row, rules, routes, context.scenario_ids)
    ]
    add_check(context, CheckSpec(
        "authoring_mutation_targets",
        bool(rows) and not invalid,
        {"target_count": len(rows), "invalid": invalid},
        "authoring_mutation_targets_incomplete",
        "Declare deletion or mutation targets for critical rules or reference routes, bind each to controlled scenarios, and state the removal-test effect.",
    ))


def validate_focused_proof(context: AuthoringContext) -> None:
    proof = context.contract.get("focused_proof")
    expected = expected_focused_proof(context.repo_root, context.skill_md)
    add_check(context, CheckSpec(
        "authoring_focused_proof",
        isinstance(proof, str) and proof == expected,
        {"command": proof, "expected": expected},
        "authoring_focused_proof_missing",
        "Declare the package-bound scenario-quality preview command to rerun after a rule or reference repair.",
    ))


def validate_behavior_proof(context: AuthoringContext) -> None:
    proof = _mapping(context.contract.get("behavior_proof"))
    template = proof.get("command_template")
    cases = proof.get("scenario_ids")
    fields = _normalized_fields(proof.get("observed_fields"))
    expected = expected_behavior_proof(context.repo_root, context.skill_md)
    command_ok = isinstance(template, str) and template == expected
    cases_ok = valid_scenario_ids(cases, context.scenario_ids)
    fields_ok = {"outcome", "evidence", "validation", "residual_risk"} <= fields
    add_check(context, CheckSpec(
        "authoring_behavior_proof",
        all([command_ok, cases_ok, fields_ok]),
        _behavior_proof_evidence(template, expected, cases, proof.get("observed_fields")),
        "authoring_behavior_proof_incomplete",
        "Bind an executable one-case smoke command and observable outcome, evidence, validation, and residual-risk fields to controlled scenarios.",
    ))


def validate_readiness_evidence(context: AuthoringContext) -> None:
    readiness = _mapping(context.contract.get("readiness_evidence"))
    lanes = {
        lane for lane in _list(readiness.get("required_lanes")) if isinstance(lane, str)
    }
    statement = readiness.get("not_ready_statement")
    statement_ok = is_nonempty_text(statement)
    if statement_ok:
        statement_ok = normalized_text(statement) in normalized_text(context.entrypoint_text)
    add_check(context, CheckSpec(
        "authoring_readiness_evidence",
        READINESS_LANES <= lanes and statement_ok,
        {"required_lanes": sorted(lanes), "not_ready_statement": statement, "required_floor": sorted(READINESS_LANES)},
        "authoring_readiness_evidence_incomplete",
        "State that structural, package, behavioral, and runtime evidence are separate readiness lanes, and keep that no-ready claim in the skill entrypoint.",
    ))


def _mapping(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _invocation_evidence(invocation: dict[str, Any], disabled: bool) -> dict[str, Any]:
    return {
        "mode": invocation.get("mode"),
        "disable_model_invocation": disabled,
        "rationale_declared": bool(invocation.get("rationale")),
        "context_load": invocation.get("context_load"),
        "load_control_declared": bool(invocation.get("load_control")),
    }


def _valid_section_roles(roles: object, headings: set[str]) -> bool:
    return (
        isinstance(roles, dict)
        and set(roles) == headings
        and all(isinstance(role, str) and role in ENTRYPOINT_SECTION_ROLES for role in roles.values())
    )


def _entrypoint_evidence(
    context: AuthoringContext,
    max_lines: object,
    roles: object,
    duplicates: list[str],
) -> dict[str, Any]:
    return {
        "line_count": len(context.text.splitlines()),
        "max_lines": max_lines,
        "headings": sorted(context.headings),
        "section_roles": roles,
        "duplicate_headings": sorted(context.duplicate_headings),
        "duplicate_paragraphs": duplicates,
    }


def _critical_rule_result(
    row: object,
    ids: set[str],
    context: AuthoringContext,
) -> tuple[str, set[str]] | None:
    values = _mapping(row)
    rule_id = values.get("id")
    rationale = values.get("rationale_source")
    rationale_text = values.get("rationale_text")
    cases = values.get("scenario_ids")
    anchor = _rationale_anchor(rationale)
    count = _rationale_occurrences(anchor, rationale_text, context.sections)
    shape_ok = is_nonempty_text(rule_id) and rule_id not in ids
    rationale_ok = _valid_rationale(rationale, anchor, rationale_text, count, context)
    outcome_ok = _is_typed_blocker(values.get("typed_outcome"))
    if not all([shape_ok, rationale_ok, outcome_ok, valid_scenario_ids(cases, context.scenario_ids)]):
        return None
    return rule_id, set(cases)


def _critical_rule_evidence(row: object, context: AuthoringContext) -> dict[str, Any]:
    values = _mapping(row)
    rationale = values.get("rationale_source")
    rationale_text = values.get("rationale_text")
    return {
        "id": values.get("id"),
        "rationale_source": rationale,
        "rationale_text": rationale_text,
        "rationale_occurrences": _rationale_occurrences(
            _rationale_anchor(rationale), rationale_text, context.sections
        ),
        "typed_outcome": values.get("typed_outcome"),
        "scenario_ids": values.get("scenario_ids"),
    }


def _rationale_anchor(value: object) -> str:
    if not isinstance(value, str) or "#" not in value:
        return ""
    return value.split("#", 1)[1]


def _rationale_occurrences(
    anchor: str,
    rationale_text: object,
    sections: dict[str, str],
) -> int:
    if anchor not in sections or not is_nonempty_text(rationale_text):
        return 0
    return normalized_text(sections[anchor]).count(normalized_text(rationale_text))


def _valid_rationale(
    source: object,
    anchor: str,
    text: object,
    count: int,
    context: AuthoringContext,
) -> bool:
    return (
        isinstance(source, str)
        and source.startswith("SKILL.md#")
        and anchor in context.headings
        and anchor not in context.duplicate_headings
        and is_nonempty_text(text)
        and count == 1
    )


def _critical_rules_evidence(
    ids: set[str],
    invalid: list[dict[str, Any]],
    declared_scenarios: set[str],
) -> dict[str, Any]:
    return {
        "rule_ids": sorted(ids),
        "invalid": invalid,
        "no_silent_fallback": "no-silent-fallback" in ids,
        "declared_scenario_ids": sorted(declared_scenarios),
    }


def _phase_rows(
    rows: list[Any], context: AuthoringContext
) -> tuple[list[tuple[str, str, int]], list[dict[str, Any]]]:
    valid: list[tuple[str, str, int]] = []
    invalid: list[dict[str, Any]] = []
    ids: set[str] = set()
    for row in rows:
        result = _phase_row_result(row, ids, context)
        if result is None:
            invalid.append(_phase_row_evidence(row))
        else:
            valid.append(result)
            ids.add(result[0])
    return valid, invalid


def _phase_row_result(
    row: object,
    ids: set[str],
    context: AuthoringContext,
) -> tuple[str, str, int] | None:
    values = _mapping(row)
    phase_id = values.get("id")
    heading = values.get("heading")
    position = markdown_heading_position(context.entrypoint_text, heading)
    shape_ok = is_nonempty_text(phase_id) and phase_id not in ids
    heading_ok = is_nonempty_text(heading) and position is not None
    artifact_ok = is_nonempty_text(values.get("entry_condition"))
    exit_ok = is_nonempty_text(values.get("exit_artifact"))
    cases_ok = valid_scenario_ids(values.get("scenario_ids"), context.scenario_ids)
    if not all([shape_ok, heading_ok, artifact_ok, exit_ok, cases_ok]):
        return None
    return phase_id, normalized_text(heading), position


def _phase_row_evidence(row: object) -> dict[str, Any]:
    values = _mapping(row)
    return {
        "id": values.get("id"),
        "heading": values.get("heading"),
        "scenario_ids": values.get("scenario_ids"),
    }


def _valid_phased_model(
    kind: object,
    phases: list[tuple[str, str, int]],
    invalid: list[dict[str, Any]],
    explicit: list[tuple[int, str]],
) -> bool:
    declared_headings = [heading for _, heading, _ in phases]
    positions = [position for _, _, position in phases]
    return (
        kind == "phased"
        and len(phases) >= 2
        and not invalid
        and positions == sorted(positions)
        and declared_headings == [title for _, title in explicit]
    )


def _phase_evidence(
    kind: object,
    phases: list[tuple[str, str, int]],
    explicit: list[tuple[int, str]],
    invalid: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "kind": kind,
        "phases": sorted(phase_id for phase_id, _, _ in phases),
        "declared_headings": [heading for _, heading, _ in phases],
        "entrypoint_phase_headings": [title for _, title in explicit],
        "invalid": invalid,
    }


def _decision_boundary_result(
    row: object,
    ids: set[str],
    kinds: set[str],
    context: AuthoringContext,
) -> tuple[str, str] | None:
    values = _mapping(row)
    boundary_id = values.get("id")
    kind = values.get("kind")
    statement = values.get("statement")
    unique = is_nonempty_text(boundary_id) and boundary_id not in ids
    kind_ok = isinstance(kind, str) and kind in DECISION_BOUNDARY_KINDS and kind not in kinds
    text_ok = is_nonempty_text(statement)
    if text_ok:
        text_ok = normalized_text(statement) in normalized_text(context.entrypoint_text)
    outcome_ok = _is_typed_outcome(values.get("typed_outcome"))
    cases_ok = valid_scenario_ids(values.get("scenario_ids"), context.scenario_ids)
    if not all([unique, kind_ok, text_ok, outcome_ok, cases_ok]):
        return None
    return boundary_id, kind


def _boundary_evidence(row: object) -> dict[str, Any]:
    values = _mapping(row)
    return {
        "id": values.get("id"),
        "kind": values.get("kind"),
        "statement": values.get("statement"),
        "scenario_ids": values.get("scenario_ids"),
    }


def _valid_blocker_condition(value: object, scenarios: set[str]) -> bool:
    condition = _mapping(value)
    return (
        _is_typed_blocker(condition.get("typed_outcome"))
        and valid_scenario_ids(condition.get("scenario_ids"), scenarios)
        and is_nonempty_text(condition.get("rationale"))
    )


def _valid_blocker_exception(
    category: str,
    value: object,
    context: AuthoringContext,
) -> bool:
    if category not in {"tool", "credential", "permission"}:
        return False
    exception = _mapping(value)
    statement = exception.get("statement")
    statement_ok = is_nonempty_text(statement)
    if statement_ok:
        statement_ok = normalized_text(statement) in normalized_text(context.entrypoint_text)
    return all(
        [
            is_nonempty_text(exception.get("rationale")),
            statement_ok,
            valid_scenario_ids(exception.get("scenario_ids"), context.scenario_ids),
        ]
    )


def _blocker_matrix_failure(category: str, exceptions: dict[str, Any]) -> dict[str, Any]:
    if category in {"input", "evidence"} and category in exceptions:
        return {"category": category, "reason": "typed_blocker_required"}
    return {"category": category, "reason": "missing_coverage_or_not_applicable_rationale"}


def _reference_route_result(
    row: object,
    ids: set[str],
    context: AuthoringContext,
) -> tuple[str, set[str]] | None:
    values = _mapping(row)
    route_id = values.get("id")
    path = values.get("path")
    shape_ok = is_nonempty_text(route_id) and route_id not in ids
    path_ok = isinstance(path, str) and path.startswith("references/")
    reference_ok = path_ok and contained_regular_reference(context.skill_md, path)
    text_ok = isinstance(path, str) and path in context.entrypoint_text
    read_ok = is_nonempty_text(values.get("read_when"))
    cases = values.get("scenario_ids")
    if not all([shape_ok, reference_ok, text_ok, read_ok, valid_scenario_ids(cases, context.scenario_ids)]):
        return None
    return route_id, set(cases)


def _route_evidence(row: object) -> dict[str, Any]:
    values = _mapping(row)
    return {
        "id": values.get("id"),
        "path": values.get("path"),
        "read_when": values.get("read_when"),
        "scenario_ids": values.get("scenario_ids"),
    }


def _normalized_fields(value: object) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {field.casefold() for field in value if isinstance(field, str)}


def _output_fields_complete(fields: set[str]) -> bool:
    has_outcome = bool({"outcome", "status", "score", "phase", "state"} & fields)
    has_evidence = bool({"evidence", "provenance", "grounded_state", "validation_evidence"} & fields)
    has_validation = bool({"validation", "validation_evidence"} & fields)
    has_risk = bool({"residual_risk", "risk_note", "skipped_boundary"} & fields)
    return all([has_outcome, has_evidence, has_validation, has_risk])


def _nonempty_text_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(is_nonempty_text(item) for item in value)


def _output_evidence(
    fields: set[str], artifact_locations: object, provenance_fields: object
) -> dict[str, Any]:
    return {
        "required_fields": sorted(fields),
        "artifact_locations": artifact_locations,
        "provenance_fields": provenance_fields,
    }


def _valid_mutation_target(
    row: object,
    rules: RuleBindings,
    routes: RouteBindings,
    scenario_ids: set[str],
) -> bool:
    values = _mapping(row)
    target = values.get("target")
    target_scenarios = _target_scenarios(values.get("kind"), target, rules, routes)
    cases = values.get("scenario_ids")
    cases_ok = valid_scenario_ids(cases, scenario_ids) and set(cases) == target_scenarios
    return bool(target_scenarios) and cases_ok and _valid_removal_test(values.get("removal_test"), target, target_scenarios)


def _target_scenarios(
    kind: object,
    target: object,
    rules: RuleBindings,
    routes: RouteBindings,
) -> set[str]:
    if kind == "critical_rule":
        return rules.scenarios_by_id.get(target, set())
    if kind == "reference_route":
        return routes.scenarios_by_id.get(target, set())
    return set()


def _valid_removal_test(value: object, target: object, expected_cases: set[str]) -> bool:
    removal = _mapping(value)
    effect = removal.get("expected_effect")
    cases = removal.get("scenario_ids")
    return (
        is_nonempty_text(effect)
        and isinstance(target, str)
        and target in effect
        and isinstance(cases, list)
        and bool(cases)
        and set(cases) == expected_cases
    )


def _mutation_evidence(row: object) -> dict[str, Any]:
    values = _mapping(row)
    return {
        "target": values.get("target"),
        "kind": values.get("kind"),
        "scenario_ids": values.get("scenario_ids"),
        "removal_test": values.get("removal_test"),
    }


def _behavior_proof_evidence(
    template: object, expected: str | None, cases: object, fields: object
) -> dict[str, Any]:
    return {
        "command_template": template,
        "expected": expected,
        "scenario_ids": cases,
        "observed_fields": fields,
    }


def _is_typed_blocker(value: object) -> bool:
    return isinstance(value, str) and bool(_TYPED_BLOCKER_RE.fullmatch(value))


def _is_typed_outcome(value: object) -> bool:
    return isinstance(value, str) and bool(_TYPED_OUTCOME_RE.fullmatch(value))
