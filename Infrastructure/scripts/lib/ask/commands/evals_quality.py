from __future__ import annotations

from .evals_staging_parse import *  # noqa: F403

def _acceptance_type(item: object) -> str:
    if not isinstance(item, dict):
        return ""
    return str(_normalize_tessl_acceptance_item(item).get("type") or "acceptance").strip().lower()


def _is_provenance_only_signal(value: str) -> bool:
    normalized = " ".join(value.split())
    return (
        bool(PROVENANCE_FIXTURE_PATH_RE.search(normalized))
        and bool(PROVENANCE_ONLY_VERBS_RE.search(normalized))
        and "evidence" in normalized.lower()
    )


def _case_has_behavioral_acceptance(case: dict[str, object]) -> bool:
    acceptance = case.get("acceptance")
    if not isinstance(acceptance, list):
        return False
    types = {_acceptance_type(item) for item in acceptance}
    return bool(types & BEHAVIORAL_TESSL_ACCEPTANCE_TYPES)


def _case_has_skill_lift_acceptance(case: dict[str, object]) -> bool:
    acceptance = case.get("acceptance")
    if not isinstance(acceptance, list):
        return False
    for item in acceptance:
        if not isinstance(item, dict):
            continue
        normalized = _normalize_tessl_acceptance_item(item)
        item_type = str(normalized.get("type") or "acceptance").strip().lower()
        value = str(normalized.get("value") or normalized.get("expected_skill") or "").strip()
        if item_type in {"skill_selected", "artifact_exists", "artifact_contains", "command_success", "output_schema"}:
            return True
        if item_type.startswith(("forbidden", "must_not")):
            return True
        if (
            item_type == "expected_signal"
            and value
            and not _is_provenance_only_signal(value)
            and not GENERIC_EXPECTED_SIGNAL_RE.match(value)
        ):
            return True
    return False


def _case_has_keyword_only_acceptance(case: dict[str, object]) -> bool:
    acceptance = case.get("acceptance")
    if not isinstance(acceptance, list) or not acceptance:
        return False
    types = {_acceptance_type(item) for item in acceptance}
    return bool(types) and types <= KEYWORD_ONLY_TESSL_ACCEPTANCE_TYPES


def _case_has_shallow_routing_oracle(case: dict[str, object]) -> bool:
    acceptance = case.get("acceptance")
    if not isinstance(acceptance, list) or not acceptance:
        return False
    normalized_items = [
        _normalize_tessl_acceptance_item(item)
        for item in acceptance
        if isinstance(item, dict)
    ]
    types = {str(item.get("type") or "acceptance").strip().lower() for item in normalized_items}
    if not types or not types <= {"skill_selected", "skill_not_selected", "expected_signal"}:
        return False
    expected_values = [
        str(item.get("value") or "").strip().lower()
        for item in normalized_items
        if str(item.get("type") or "").strip().lower() == "expected_signal"
    ]
    if not expected_values:
        return True
    return all(value in SHALLOW_EXPECTED_SIGNAL_VALUES for value in expected_values)


def _case_has_fixture_path_acceptance(case: dict[str, object]) -> bool:
    acceptance = case.get("acceptance")
    if not isinstance(acceptance, list):
        return False
    for item in acceptance:
        if not isinstance(item, dict):
            continue
        normalized = _normalize_tessl_acceptance_item(item)
        value = str(normalized.get("value") or normalized.get("expected_skill") or "").strip()
        if _is_provenance_only_signal(value):
            return True
    return False


def _case_has_prompt_scoring_mechanics(case: dict[str, object]) -> bool:
    prompt = str(case.get("prompt") or "")
    scoring_mechanics = (
        "Use the skill to handle this reviewed generated scenario",
        "Scenario fixture:",
        "Uses the generated scenario fixture as evidence",
    )
    return any(mechanic in prompt for mechanic in scoring_mechanics)


def _case_has_answer_leakage(case: dict[str, object]) -> bool:
    visible_text = "\n".join(
        str(case.get(field) or "") for field in ("prompt", "unit", "given", "should")
    ).lower()
    acceptance = case.get("acceptance")
    if not isinstance(acceptance, list):
        return False
    for item in acceptance:
        if not isinstance(item, dict):
            continue
        normalized = _normalize_tessl_acceptance_item(item)
        item_type = str(normalized.get("type") or "acceptance").strip().lower()
        if item_type.startswith(("must_not", "forbidden")):
            continue
        value = str(normalized.get("value") or normalized.get("expected_skill") or "").strip()
        if len(value) >= 80 and value.lower() in visible_text:
            return True
    return False


def _case_has_unstaged_repo_path_reference(case: dict[str, object]) -> bool:
    text_parts = [
        str(case.get(field) or "") for field in ("prompt", "unit", "given", "should")
    ]
    acceptance = case.get("acceptance")
    if isinstance(acceptance, list):
        for item in acceptance:
            if not isinstance(item, dict):
                continue
            normalized = _normalize_tessl_acceptance_item(item)
            text_parts.extend([
                str(normalized.get("value") or ""),
                str(normalized.get("expected_skill") or ""),
            ])
    return bool(UNSTAGED_TESSL_REPO_PATH_RE.search("\n".join(text_parts)))


def _case_text_for_quality(case: dict[str, object]) -> str:
    text_parts = [
        str(case.get(field) or "")
        for field in (
            "id",
            "name",
            "category",
            "unit",
            "given",
            "should",
            "prompt",
            "expected_artifact",
            "raw_response_artifact",
            "judge_detail_artifact",
            "judge_raw_output_artifact",
            "judge_parse_error_artifact",
            "judge_schema_error_artifact",
            "positive_example_artifact",
            "negative_example_artifact",
            "source_policy_artifact",
            "risk_dimension",
            "label",
        )
    ]
    acceptance = case.get("acceptance")
    if isinstance(acceptance, list):
        for item in acceptance:
            if not isinstance(item, dict):
                continue
            normalized = _normalize_tessl_acceptance_item(item)
            text_parts.extend([
                str(normalized.get("type") or ""),
                str(normalized.get("value") or ""),
                str(normalized.get("expected_skill") or ""),
            ])
    expected_signals = case.get("expected_signals")
    if isinstance(expected_signals, dict):
        for value in expected_signals.values():
            if isinstance(value, list):
                text_parts.extend(str(item) for item in value)
            else:
                text_parts.append(str(value))
    return "\n".join(text_parts)


def _case_has_guardrail_calibration_shape(case: dict[str, object]) -> bool:
    case_text = _case_text_for_quality(case)
    if not GUARDRAIL_CASE_RE.search(case_text):
        return True
    has_structured_output = bool(GUARDRAIL_STRUCTURED_OUTPUT_RE.search(case_text))
    acceptance = case.get("acceptance")
    if isinstance(acceptance, list):
        has_structured_output = has_structured_output or any(
            _acceptance_type(item) == "output_schema" for item in acceptance
        )
    return (
        bool(GUARDRAIL_LABEL_RE.search(case_text))
        and bool(GUARDRAIL_DIMENSION_RE.search(case_text))
        and has_structured_output
    )


def _case_has_paired_calibration_examples(case: dict[str, object]) -> bool:
    case_text = _case_text_for_quality(case)
    if not JUDGE_CASE_RE.search(case_text):
        return True
    positive = case.get("positive_example_artifact") or case.get("passing_example_artifact")
    negative = case.get("negative_example_artifact") or case.get("failing_example_artifact")
    if positive and negative:
        return True
    return not GUARDRAIL_CASE_RE.search(case_text)


def _terms_present(text: str, terms: tuple[str, ...]) -> set[str]:
    present: set[str] = set()
    for term in terms:
        pattern = r"(?i)(?<![A-Za-z0-9_-])" + re.escape(term) + r"(?![A-Za-z0-9_-])"
        if re.search(pattern, text):
            present.add(term)
    return present


def _case_has_mixed_guardrail_terms(case: dict[str, object]) -> bool:
    case_text = _case_text_for_quality(case)
    if not JUDGE_CASE_RE.search(case_text):
        return False
    role_terms = _terms_present(case_text, ROLE_TERMS)
    # In guardrail/judge prompts, multiple role names often make the scorer's
    # target ambiguous. Source-authority terms are intentionally not enforced
    # here because "source-of-truth policy" is a useful composite phrase.
    return len(role_terms) > 1


def _case_has_guardrail_failure_outcomes(case: dict[str, object]) -> bool:
    case_text = _case_text_for_quality(case)
    if not GUARDRAIL_CASE_RE.search(case_text):
        return True
    raw_output = case.get("judge_raw_output_artifact") or case.get("raw_response_artifact")
    return bool(raw_output) and all(term in case_text.lower() for term in GUARDRAIL_OUTCOME_TERMS)


def _case_has_guardrail_response_schema(case: dict[str, object]) -> bool:
    case_text = _case_text_for_quality(case)
    if not GUARDRAIL_CASE_RE.search(case_text):
        return True
    normalized = case_text.lower()
    return (
        all(term in normalized for term in GUARDRAIL_RESPONSE_SCHEMA_TERMS)
        and bool(GUARDRAIL_FAIL_CLOSED_RE.search(case_text))
    )


def _case_has_source_reference_quality(case: dict[str, object]) -> bool:
    case_text = _case_text_for_quality(case)
    if not GUARDRAIL_CASE_RE.search(case_text):
        return True
    return bool(SOURCE_REFERENCE_PASS_RE.search(case_text)) and bool(FAIL_RATIONALE_RE.search(case_text))


def _has_sampling_count(case: dict[str, object]) -> bool:
    return bool(case.get("judge_runs") or case.get("sample_count"))


def _case_has_judge_sampling_policy(case: dict[str, object]) -> bool:
    case_text = _case_text_for_quality(case)
    if not JUDGE_CASE_RE.search(case_text):
        return True
    if case.get("judge_temperature") is not None and not _has_sampling_count(case):
        return False
    return True


def _truthy_metadata(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _synthetic_guardrail_label_balance_findings(cases: list[dict[str, object]]) -> list[dict[str, str]]:
    synthetic_cases = [
        case
        for case in cases
        if _truthy_metadata(case.get("synthetic"))
        and GUARDRAIL_CASE_RE.search(_case_text_for_quality(case))
    ]
    labeled_cases = [
        case
        for case in synthetic_cases
        if str(case.get("label") or "").strip().lower() in {"pass", "fail"}
    ]
    labels = {str(case.get("label") or "").strip().lower() for case in labeled_cases}
    if len(labeled_cases) < 2 or len(labels) >= 2:
        return []
    case_ids = ", ".join(str(case.get("id") or "unknown") for case in labeled_cases[:8])
    return [{
        "case_id": "synthetic_guardrail_suite",
        "code": "guardrail_synthetic_label_imbalance",
        "message": (
            "Synthetic guardrail eval selections must include both pass and fail labels "
            f"before acting as release evidence; selected one-class cases: {case_ids}."
        ),
    }]


def _case_has_scenario_context(case: dict[str, object]) -> bool:
    fields = [str(case.get(field) or "").strip() for field in ("unit", "given", "should")]
    if all(fields):
        return True
    prompt = str(case.get("prompt") or "").strip()
    return prompt.count("\n") >= 3 and len(prompt) >= 240


def _tessl_eval_quality_findings(cases: list[dict[str, object]]) -> list[dict[str, str]]:
    return tessl_eval_quality_findings(cases)


def _assert_tessl_eval_quality(cases: list[dict[str, object]], *, source: Path) -> None:
    if not cases:
        raise ValueError(
            f"Tessl eval quality gate failed for {source}: no Tessl eval cases were selected. "
            "Add structured behavioural scenarios before staging or uploading Tessl assessments."
        )
    findings = _tessl_eval_quality_findings(cases)
    if not findings:
        return
    summary = "; ".join(
        f"{finding['case_id']}:{finding['code']}" for finding in findings[:12]
    )
    if len(findings) > 12:
        summary += f"; +{len(findings) - 12} more"
    raise ValueError(
        f"Tessl eval quality gate failed for {source}: {summary}. "
        "Convert seed or internal evals into structured, skill-specific behavioural scenarios "
        "before staging or uploading Tessl assessments."
    )


def _case_tessl_enabled(raw_case: dict[object, object], *, lane: str) -> bool:
    flat_key = f"tessl_{lane}"
    flat_value = raw_case.get(flat_key)
    if flat_value is False or str(flat_value).strip().lower() == "false":
        return False
    tessl = raw_case.get("tessl")
    if not isinstance(tessl, dict):
        return True
    lane_value = tessl.get(lane)
    if lane_value is False:
        return False
    enabled = tessl.get("enabled")
    return enabled is not False


def _write_tessl_scenarios_from_evals(source_root: Path, staged_root: Path) -> list[str]:
    copied: list[str] = []
    evals_path = source_root / "references" / "evals.yaml"
    cases, scenario_manifest = _merge_tessl_cases_with_generated_fixtures(
        source_root,
        _parse_tessl_eval_cases(evals_path),
        require_generated=False,
    )
    scenario_manifest_path = staged_root / "scenario-sources.json"
    scenario_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    scenario_manifest_path.write_text(json.dumps(scenario_manifest, indent=2) + "\n", encoding="utf-8")
    copied.append(str(scenario_manifest_path.relative_to(staged_root)))
    for case in cases:
        case_id = str(case["id"]).replace("/", "-")
        case_root = staged_root / "scenarios" / case_id
        case_root.mkdir(parents=True, exist_ok=True)
        task_path = case_root / "task.md"
        task_path.write_text(_tessl_task_markdown(case), encoding="utf-8")
        criteria_path = case_root / "criteria.json"
        criteria_path.write_text(json.dumps(_tessl_criteria_from_case(case), indent=2) + "\n", encoding="utf-8")
        copied.extend([
            str(task_path.relative_to(staged_root)),
            str(criteria_path.relative_to(staged_root)),
        ])
    return copied


def _tessl_plugin_project_slug(source_root: Path) -> str | None:
    parts = source_root.parts
    for index, part in enumerate(parts):
        if part == "Plugins" and index + 2 < len(parts) and parts[index + 2] == "skills":
            return _safe_slug(parts[index + 1].lower())
    return None


def _tessl_project_slug(source_root: Path) -> str:
    plugin_slug = _tessl_plugin_project_slug(source_root)
    if plugin_slug:
        return plugin_slug
    return _safe_slug(source_root.name.lower())


def _tessl_project_identity(source_root: Path, workspace: str | None = None) -> dict[str, str | None]:
    slug = _tessl_project_slug(source_root)
    owner_type = "plugin" if _tessl_plugin_project_slug(source_root) else "standalone_skill"
    return {
        "owner_type": owner_type,
        "project": slug,
        "workspace": workspace,
        "name": f"{workspace}/{slug}" if workspace else slug,
    }


def _write_tessl_project_marker(
    source_root: Path,
    staged_root: Path,
    workspace: str | None = None,
) -> list[str]:
    marker_path = staged_root / "tessl.json"
    identity = _tessl_project_identity(source_root, workspace)
    marker_path.write_text(
        json.dumps({"name": identity["name"], "mode": "managed", "dependencies": {}}, indent=2) + "\n",
        encoding="utf-8",
    )
    return ["tessl.json"]


def _validate_tessl_workspace(workspace: str | None) -> str:
    if workspace is None or not workspace.strip():
        raise ValueError(f"Tessl live-private evals require workspace {TESSL_DEFAULT_WORKSPACE}.")
    normalized = workspace.strip()
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", normalized):
        raise ValueError(
            "Tessl workspace must be lowercase and contain only letters, numbers, '.', '_', or '-'."
        )
    if "/" in normalized:
        raise ValueError("Tessl workspace must be the workspace name only, not workspace/tile.")
    if normalized != TESSL_DEFAULT_WORKSPACE:
        raise ValueError(
            f"Skills SDK Tessl lanes must use workspace {TESSL_DEFAULT_WORKSPACE}; "
            f"received {normalized}."
        )
    return normalized


def _default_tessl_workspace_from_env() -> tuple[str | None, str | None]:
    for name in ("ASK_TESSL_WORKSPACE", "TESSL_WORKSPACE", "TESSL_WORKSPACE_NAME"):
        value = os.environ.get(name)
        if value is not None and value.strip():
            return _validate_tessl_workspace(value), name
    return TESSL_DEFAULT_WORKSPACE, "default"


def _tessl_eval_case_id(case_id: str) -> str:
    return _safe_slug(case_id.replace("/", "-"))


def _tessl_task_markdown(case: dict[str, object]) -> str:
    lines: list[str] = []
    for label, field in (("Unit", "unit"), ("Given", "given"), ("Should", "should")):
        value = str(case.get(field) or "").strip()
        if value:
            lines.append(f"{label}: {value}")
    if lines:
        lines.append("")
    lines.append(str(case.get("prompt") or "").rstrip())
    return "\n".join(lines).rstrip() + "\n"


def _normalize_tessl_acceptance_item(item: dict[object, object]) -> dict[str, str]:
    return normalize_tessl_acceptance_item(item)


def _tessl_acceptance_description(
    item: dict[str, str],
    case: dict[str, object],
    *,
    source_item: dict[object, object] | None = None,
) -> str:
    criterion_type = str(item.get("type") or "").strip().lower()
    if criterion_type.startswith("text_field_"):
        field = str(item.get("field") or item.get("path") or item.get("name") or "").strip()
        expected_values = str(
            item.get("value")
            or item.get("expected")
            or item.get("expected_value")
            or item.get("values")
            or ""
        ).strip()
        parts = [f"type={criterion_type}"]
        if field:
            parts.append(f"field={field}")
        if expected_values:
            parts.append(f"expected={expected_values}")
        return "; ".join(parts)
    if criterion_type == "semantic_requirements":
        requirements = (source_item or {}).get("requirements")
        if isinstance(requirements, list):
            rendered: list[str] = []
            for requirement in requirements:
                if not isinstance(requirement, dict):
                    continue
                requirement_id = str(requirement.get("id") or "").strip()
                required = requirement.get("all_of")
                alternatives = requirement.get("any_of")
                clauses: list[str] = []
                if isinstance(required, list) and required:
                    terms = [str(term).strip() for term in required if str(term).strip()]
                    clauses.append("all_of=" + ", ".join(terms))
                if isinstance(alternatives, list) and alternatives:
                    terms = [str(term).strip() for term in alternatives if str(term).strip()]
                    clauses.append("any_of=" + ", ".join(terms))
                if clauses:
                    rendered.append(f"{requirement_id}: " + "; ".join(clauses))
            if rendered:
                return "semantic_requirements: " + " | ".join(rendered)
        return "semantic_requirements: satisfy every declared requirement."
    return str(
        item.get("value")
        or item.get("expected_skill")
        or case.get("expected_artifact")
        or "Satisfies acceptance criterion."
    ).strip()

__all__ = [name for name in globals() if not name.startswith("__")]
