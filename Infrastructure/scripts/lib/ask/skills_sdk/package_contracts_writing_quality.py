from __future__ import annotations

from .package_contracts_common import *  # noqa: F403
from .package_contracts_parsing import *  # noqa: F403
from .package_contracts_assets import *  # noqa: F403
from .package_contracts_writing_support import *  # noqa: F403

def _skill_evals_yaml_path(skill_md: Path | None) -> Path | None:
    if not skill_md:
        return None
    candidate = skill_md.parent / "references" / "evals.yaml"
    return candidate if candidate.is_file() else None


def _case_id(case: Any, index: int) -> str:
    if isinstance(case, dict) and case.get("id"):
        return str(case["id"])
    return f"case[{index}]"


def _scenario_cases_from_reference(
    evals_path: Path,
    loaded: dict[str, Any],
) -> list[Any]:
    """Return eval cases, using a small fallback for nested cases YAML."""
    cases = loaded.get("cases")
    if isinstance(cases, list) and cases and all(isinstance(case, dict) for case in cases):
        return cases
    try:
        text = evals_path.read_text(encoding="utf-8")
    except OSError:
        return cases if isinstance(cases, list) else []
    parsed_cases: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    current_list_key: str | None = None
    in_cases = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped == "---" or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if not in_cases:
            if indent == 0 and stripped == "cases:":
                in_cases = True
            continue
        if indent == 0 and not stripped.startswith("- "):
            break
        if indent in {0, 2} and stripped.startswith("- id:"):
            if current is not None:
                parsed_cases.append(current)
            current = {}
            current_list_key = None
            remainder = stripped[2:].strip()
            if ":" in remainder:
                key, value = remainder.split(":", 1)
                current[key.strip()] = parse_frontmatter_scalar(value.strip())
            continue
        if current is None:
            continue
        if current_list_key and indent >= 2 and stripped.startswith("- "):
            values = current.setdefault(current_list_key, [])
            if isinstance(values, list):
                values.append(parse_frontmatter_scalar(stripped[2:].strip()))
            continue
        if indent >= 2 and ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value:
                current[key] = parse_frontmatter_scalar(value)
                current_list_key = None
            else:
                current[key] = []
                current_list_key = key
    if current is not None:
        parsed_cases.append(current)
    return parsed_cases or (cases if isinstance(cases, list) else [])


def _scenario_alignment_checks(
    repo_root: Path | None,
    skill_md: Path | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return deterministic gold-scenario shape checks for references/evals.yaml."""
    checks: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    evals_path = _skill_evals_yaml_path(skill_md)
    rel_path = repo_relative_path(repo_root, evals_path) if repo_root and evals_path else None
    if evals_path is None:
        checks.append(
            _quality_check(
                "scenario_alignment_declared",
                "not_applicable",
                dimension="scenario_alignment",
                evidence={"path": None, "reason": "references/evals.yaml not declared"},
            )
        )
        return checks, blockers

    loaded, error = read_structured_reference(evals_path)
    if error is not None or not isinstance(loaded, dict):
        checks.append(
            _quality_check(
                "scenario_alignment_parse",
                "blocked_validation",
                dimension="scenario_alignment",
                evidence={"path": rel_path, "error": error or "evals.yaml must be a mapping"},
            )
        )
        blockers.append(
            _quality_blocker(
                "scenario_alignment_unparseable",
                "references/evals.yaml must be parseable before scenario quality can be trusted.",
                dimension="scenario_alignment",
                path=rel_path,
            )
        )
        return checks, blockers

    cases = _scenario_cases_from_reference(evals_path, loaded)
    if not isinstance(cases, list) or not cases:
        checks.append(
            _quality_check(
                "scenario_alignment_cases_declared",
                "blocked_validation",
                dimension="scenario_alignment",
                evidence={"path": rel_path, "case_count": 0},
            )
        )
        blockers.append(
            _quality_blocker(
                "scenario_alignment_cases_missing",
                "references/evals.yaml must declare at least one case before scenario-quality can run.",
                dimension="scenario_alignment",
                path=rel_path,
            )
        )
        return checks, blockers

    missing_by_case: list[dict[str, Any]] = []
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            missing_by_case.append({"case": _case_id(case, index), "missing": ["mapping"]})
            continue
        missing: list[str] = []
        for field in ("id", "category"):
            if not str(case.get(field) or "").strip():
                missing.append(field)
        if not str(case.get("prompt") or case.get("user_task") or "").strip():
            missing.append("prompt_or_user_task")
        if not str(case.get("given") or case.get("why_realistic") or "").strip():
            missing.append("given_or_why_realistic")
        if not str(
            case.get("should")
            or case.get("expected_behavior")
            or case.get("expected_evidence")
            or ""
        ).strip():
            missing.append("should_or_expected_behavior")
        acceptance = case.get("acceptance")
        expected_evidence = case.get("expected_evidence")
        if not (
            isinstance(acceptance, list)
            and acceptance
            or isinstance(expected_evidence, list)
            and expected_evidence
        ):
            missing.append("acceptance_or_expected_evidence")
        if missing:
            missing_by_case.append({"case": _case_id(case, index), "missing": missing})

    status = "blocked_validation" if missing_by_case else "pass"
    checks.append(
        _quality_check(
            "scenario_alignment_gold_shape",
            status,
            dimension="scenario_alignment",
            evidence={
                "path": rel_path,
                "case_count": len(cases),
                "missing_by_case": missing_by_case,
            },
        )
    )
    if missing_by_case:
        blockers.append(
            _quality_blocker(
                "scenario_alignment_gold_shape_incomplete",
                "references/evals.yaml cases must include gold-standard fields: id, category, task, given, should, and acceptance evidence.",
                dimension="scenario_alignment",
                path=rel_path,
            )
        )
    return checks, blockers


def _construction_quality_checks(
    *,
    repo_root: Path | None,
    skill_md: Path | None,
    text: str,
    user_invoked: bool,
    description: str,
    procedural: bool,
    references_count: int,
    missing_references: list[Any],
    source_path: str | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return deterministic construction checks from the Predictability glossary."""
    checks: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []

    description_tokens = _token_set(description)
    trigger_boundaries = sorted(description_tokens & CONSTRUCTION_TRIGGER_BOUNDARY_TERMS)
    generic_trigger_terms = sorted(description_tokens & CONSTRUCTION_GENERIC_TRIGGER_TERMS)
    trigger_status = (
        "not_applicable"
        if user_invoked
        else "pass"
        if description
        and text_contains_action_term(description)
        and "when" in description_tokens
        and not generic_trigger_terms
        else "blocked_validation"
    )
    checks.append(
        _quality_check(
            "construction_trigger_boundary",
            trigger_status,
            dimension="invocation",
            evidence={
                "glossary_axis": "Invocation",
                "root_quality": "Predictability",
                "user_invoked": user_invoked,
                "has_description": bool(description),
                "has_action_term": text_contains_action_term(description),
                "trigger_boundaries": trigger_boundaries,
                "generic_trigger_terms": generic_trigger_terms,
            },
        )
    )
    if trigger_status == "blocked_validation":
        blockers.append(
            _quality_blocker(
                "construction_trigger_boundary_missing",
                "Trigger design must use a concrete action-shaped description and avoid generic catch-all routing terms.",
                dimension="invocation",
                path=source_path,
            )
        )

    step_body = _construction_step_body(text)
    step_tokens = _token_set(step_body)
    step_action_terms = sorted(step_tokens & CONSTRUCTION_OBLIGATION_TERMS)
    references_routed = references_count == 0 or "references/" in text
    structure_status = (
        "pass"
        if procedural and step_action_terms and references_routed and not missing_references
        else "blocked_validation"
    )
    checks.append(
        _quality_check(
            "construction_steps_reference_structure",
            structure_status,
            dimension="information_hierarchy",
            evidence={
                "glossary_axis": "Information Hierarchy",
                "root_quality": "Predictability",
                "procedural_heading_declared": procedural,
                "step_action_terms": step_action_terms,
                "reference_count": references_count,
                "references_routed": references_routed,
                "missing_references": missing_references,
            },
        )
    )
    if structure_status == "blocked_validation":
        blockers.append(
            _quality_blocker(
                "construction_steps_reference_structure_missing",
                "Skill construction must separate Steps from Reference with at least one action-shaped workflow step and routed context pointers.",
                dimension="information_hierarchy",
                path=source_path,
            )
        )

    all_tokens = _token_set(text)
    phase_like = bool(all_tokens & {"phase", "step", "stage", "gate"})
    phase_gate_terms = sorted(all_tokens & CONSTRUCTION_PHASE_TERMS)
    steering_status = (
        "not_applicable"
        if not phase_like
        else "pass"
        if phase_gate_terms and bool(all_tokens & {"before", "after", "stop", "block", "validate", "gate"})
        else "blocked_validation"
    )
    checks.append(
        _quality_check(
            "construction_steering_phase_gate",
            steering_status,
            dimension="steering",
            evidence={
                "glossary_axis": "Steering",
                "root_quality": "Predictability",
                "phase_like": phase_like,
                "phase_gate_terms": phase_gate_terms,
            },
        )
    )
    if steering_status == "blocked_validation":
        blockers.append(
            _quality_blocker(
                "construction_steering_phase_gate_missing",
                "Phase or step-based skills must say what blocks advancement, what evidence is required, or when to stop.",
                dimension="steering",
                path=source_path,
            )
        )

    sediment_paragraphs = _long_paragraphs_without_behavior(text)
    duplicate_lines = _duplicate_instruction_lines(text)
    pruning_status = (
        "pass"
        if not sediment_paragraphs and not duplicate_lines
        else "blocked_validation"
    )
    checks.append(
        _quality_check(
            "construction_pruning_sediment",
            pruning_status,
            dimension="pruning",
            evidence={
                "glossary_axis": "Pruning",
                "root_quality": "Predictability",
                "long_paragraphs_without_behavior": sediment_paragraphs,
                "duplicate_instruction_lines": duplicate_lines,
            },
        )
    )
    if sediment_paragraphs:
        blockers.append(
            _quality_blocker(
                "construction_sediment_paragraph",
                "Long skill prose must carry an action, context pointer, completion criterion, output, or evidence obligation; otherwise it is sediment to move or prune.",
                dimension="pruning",
                path=source_path,
            )
        )
    if duplicate_lines:
        blockers.append(
            _quality_blocker(
                "construction_duplicate_instruction",
                "Repeated instruction-shaped lines violate single source of truth and should be deduplicated or moved into one routed reference.",
                dimension="pruning",
                path=source_path,
            )
        )

    fragmented_boundary_sections = [
        heading
        for heading in ("Constraints", "Execution Boundaries", "Validation", "Handoff")
        if markdown_heading_declared(text, heading)
    ]
    boundary_fragmentation_status = (
        "blocked_validation"
        if procedural and len(fragmented_boundary_sections) >= 3
        else "pass"
    )
    checks.append(
        _quality_check(
            "construction_boundary_fragmentation",
            boundary_fragmentation_status,
            dimension="pruning",
            evidence={
                "glossary_axis": "Pruning",
                "root_quality": "Predictability",
                "fragmented_sections": fragmented_boundary_sections,
                "policy": (
                    "Procedural skills should not split the same safety, validation, "
                    "and handoff obligations across overlapping boundary sections."
                ),
            },
        )
    )
    if boundary_fragmentation_status == "blocked_validation":
        blockers.append(
            _quality_blocker(
                "construction_boundary_fragmentation",
                (
                    "Three or more overlapping boundary sections appear in one "
                    "procedural skill; merge completion and boundary rules into a "
                    "concise validation/output section or route detail into references."
                ),
                dimension="pruning",
                path=source_path,
            )
        )

    return checks, blockers


def writing_quality_contract(
    repo_root: Path | None,
    skill_md: Path | None,
    frontmatter: dict[str, Any],
    text: str,
    progressive_disclosure: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic skill-writing rubric checks for package readiness."""
    source_path = repo_relative_path(repo_root, skill_md) if repo_root and skill_md else None
    checks: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []

    user_invoked = _frontmatter_bool(frontmatter, "disable-model-invocation")
    description = str(frontmatter.get("description") or "").strip()
    description_status = "not_applicable"
    if not user_invoked:
        description_status = (
            "pass"
            if description
            and text_contains_action_term(description)
            and "when" in {token.strip(".,:;!?()[]{}\"'").lower() for token in description.split()}
            else "blocked_validation"
        )
        if description_status != "pass":
            blockers.append(
                _quality_blocker(
                    "weak_description_triggers",
                    "Model-invoked skills need a trigger-shaped description with an action verb and a real 'when' branch.",
                    dimension="invocation",
                    path=source_path,
                )
            )
    checks.append(
        _quality_check(
            "description_trigger_shape",
            description_status,
            dimension="invocation",
            evidence={
                "user_invoked": user_invoked,
                "has_description": bool(description),
                "has_action_term": text_contains_action_term(description),
            },
        )
    )

    has_title = markdown_has_title(text)
    checks.append(
        _quality_check(
            "skill_md_title",
            "pass" if has_title else "blocked_validation",
            dimension="information_hierarchy",
            evidence={"headings": markdown_heading_titles(text)[:12]},
        )
    )
    if not has_title:
        blockers.append(
            _quality_blocker(
                "missing_skill_title",
                "SKILL.md must declare a top-level title so agents can identify the entrypoint.",
                dimension="information_hierarchy",
                path=source_path,
            )
        )

    metadata = frontmatter.get("metadata")
    sdk_managed_skill = isinstance(metadata, dict) and bool(
        metadata.get("skill-type")
        or metadata.get("lifecycle_state")
        or metadata.get("metadata_source")
    )
    h2_headings = markdown_heading_titles_for_level(text, 2)
    missing_canonical_headers = [
        heading for heading in CANONICAL_SKILL_H2_HEADERS if heading not in h2_headings
    ]
    allowed_h2_headings = {*CANONICAL_SKILL_H2_HEADERS, *OPTIONAL_SKILL_H2_HEADERS}
    extra_h2_headings = [heading for heading in h2_headings if heading not in allowed_h2_headings]
    canonical_positions = [
        h2_headings.index(heading)
        for heading in CANONICAL_SKILL_H2_HEADERS
        if heading in h2_headings
    ]
    canonical_header_order_ok = canonical_positions == sorted(canonical_positions)
    canonical_header_status = (
        "not_applicable"
        if not sdk_managed_skill
        else "pass"
        if not missing_canonical_headers
        and not extra_h2_headings
        and canonical_header_order_ok
        else "blocked_validation"
    )
    checks.append(
        _quality_check(
            "canonical_skill_headers",
            canonical_header_status,
            dimension="information_hierarchy",
            evidence={
                "sdk_managed_skill": sdk_managed_skill,
                "required_headers": list(CANONICAL_SKILL_H2_HEADERS),
                "optional_headers": list(OPTIONAL_SKILL_H2_HEADERS),
                "actual_h2_headings": h2_headings,
                "missing_headers": missing_canonical_headers,
                "extra_h2_headings": extra_h2_headings,
                "order_ok": canonical_header_order_ok,
            },
        )
    )
    if canonical_header_status == "blocked_validation":
        blockers.append(
            _quality_blocker(
                "canonical_skill_headers_required",
                (
                    "SDK-managed SKILL.md files must use only the canonical H2 "
                    "headers in order: When To Use, Inputs, Outputs, Workflow, "
                    "Failure Mode, Validation, References; optional package "
                    "safety sections may use Gotchas or Execution Boundaries."
                ),
                dimension="information_hierarchy",
                path=source_path,
            )
        )

    procedural = _has_any_heading(text, ("Workflow", "Procedure", "Steps"))
    validation_declared = markdown_heading_declared(text, "Validation")
    output_contract_declared = markdown_heading_declared(text, "Output Contract")
    evidence_contract_declared = markdown_heading_declared(text, "Evidence Contract")
    completion_reference_declared = (
        skill_md is not None
        and package_local_regular_file(skill_md, "references/validation-and-output.md")
        and "references/validation-and-output.md" in text
    )
    validation_body = markdown_section_body(text, "Validation")
    validation_evidence_declared = (
        validation_declared
        and _body_contains_any(validation_body, ("pass", "fail", "blocked", "command:"))
    )
    completion_status = (
        "not_applicable"
        if not procedural
        else "pass"
        if output_contract_declared
        or evidence_contract_declared
        or validation_evidence_declared
        or completion_reference_declared
        else "blocked_validation"
    )
    checks.append(
        _quality_check(
            "procedural_completion_criteria",
            completion_status,
            dimension="completion_criteria",
            evidence={
                "procedural": procedural,
                "validation_declared": validation_declared,
                "output_contract_declared": output_contract_declared,
                "evidence_contract_declared": evidence_contract_declared,
                "completion_reference_declared": completion_reference_declared,
            },
        )
    )
    if completion_status == "blocked_validation":
        blockers.append(
            _quality_blocker(
                "missing_completion_criterion",
                "Procedural skills must declare observable completion evidence through Validation, an Output Contract, an Evidence Contract, or a routed validation-and-output reference.",
                dimension="completion_criteria",
                path=source_path,
            )
        )

    line_count = progressive_disclosure.get("skill_md_line_count", 0)
    entrypoint_compact = bool(progressive_disclosure.get("skill_md_under_250_lines"))
    near_threshold_limit = int(
        progressive_disclosure.get("skill_md_near_threshold_line_limit") or 220
    )
    over_near_threshold = bool(progressive_disclosure.get("skill_md_over_near_threshold"))
    references_count = int(progressive_disclosure.get("progressive_disclosure_reference_count") or 0)
    missing_references = progressive_disclosure.get("progressive_disclosure_missing_references") or []
    near_threshold_sprawl = over_near_threshold and references_count > 0 and not missing_references
    disclosure_status = (
        "blocked_validation"
        if missing_references
        or near_threshold_sprawl
        or (not entrypoint_compact and references_count == 0)
        else "pass"
    )
    checks.append(
        _quality_check(
            "progressive_disclosure_rubric",
            disclosure_status,
            dimension="progressive_disclosure",
            evidence={
                "line_count": line_count,
                "under_250_lines": entrypoint_compact,
                "near_threshold_line_limit": near_threshold_limit,
                "over_near_threshold": over_near_threshold,
                "reference_count": references_count,
                "missing_references": missing_references,
            },
        )
    )
    if missing_references:
        blockers.append(
            _quality_blocker(
                "weak_context_pointer_missing_reference",
                "Progressive Disclosure points at references that are not present in the package.",
                dimension="progressive_disclosure",
                path=source_path,
            )
        )
    elif not entrypoint_compact and references_count == 0:
        blockers.append(
            _quality_blocker(
                "sprawl_without_disclosure",
                "Long SKILL.md entrypoints must route branch-specific or reference material through package-local references.",
                dimension="progressive_disclosure",
                path=source_path,
            )
        )
    elif near_threshold_sprawl:
        blockers.append(
            _quality_blocker(
                "near_threshold_entrypoint_sprawl",
                (
                    "SKILL.md is above the 220-line package-readiness threshold while "
                    "package references are present; move phase detail, examples, or "
                    "reference-backed guidance into package-local references."
                ),
                dimension="progressive_disclosure",
                path=source_path,
            )
        )

    construction_checks, construction_blockers = _construction_quality_checks(
        repo_root=repo_root,
        skill_md=skill_md,
        text=text,
        user_invoked=user_invoked,
        description=description,
        procedural=procedural,
        references_count=references_count,
        missing_references=missing_references,
        source_path=source_path,
    )
    checks.extend(construction_checks)
    blockers.extend(construction_blockers)

    scenario_checks, scenario_blockers = _scenario_alignment_checks(repo_root, skill_md)
    checks.extend(scenario_checks)
    blockers.extend(scenario_blockers)
    advisories = _writing_quality_advisories(
        repo_root,
        skill_md,
        frontmatter,
        text,
        user_invoked=user_invoked,
        description=description,
        procedural=procedural,
        source_path=source_path,
    )

    status = "blocked_validation" if blockers else "pass"
    return {
        "schema_version": "skills-sdk.skill-writing-quality.v1",
        "policy": "predictability_through_invocation_hierarchy_completion_and_scenarios",
        "required_for_package_readiness": True,
        "status": status,
        "rubric": {
            "source": "writing-great-skills",
            "root_quality": "Predictability",
            "dimensions": [
                "invocation",
                "information_hierarchy",
                "steering",
                "pruning",
                "progressive_disclosure",
                "completion_criteria",
                "scenario_alignment",
                "actionability",
                "review_lens",
                "safety_boundary",
                "self_improving",
            ],
        },
        "checks": checks,
        "blockers": blockers,
        "advisories": advisories,
        "what_this_proves": [
            "trigger_shape_checked",
            "construction_trigger_checked",
            "construction_structure_checked",
            "construction_steering_checked",
            "construction_pruning_checked",
            "entrypoint_hierarchy_checked",
            "completion_evidence_checked",
            "reference_disclosure_checked",
            "scenario_shape_checked",
            "advisory_quality_patterns_scored",
        ] if status == "pass" else [],
        "what_this_does_not_prove": [
            "behavioral_eval_pass",
            "runtime_skill_activation",
            "live_tessl_score",
            "cloud_eval_confirmation",
        ],
    }

__all__ = [name for name in globals() if not name.startswith("__")]
