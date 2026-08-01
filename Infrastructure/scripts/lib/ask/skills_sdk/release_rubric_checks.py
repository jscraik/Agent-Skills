from __future__ import annotations

from typing import Any, Optional


SEMANTIC_ACCEPTANCE_TYPES = {
    "discovery_question",
    "expected_signal",
    "semantic_requirements",
    "text_field_equals",
    "text_field_in",
    "text_field_present",
}
BEHAVIOR_VERBS = {
    "asks",
    "avoids",
    "blocks",
    "cites",
    "classifies",
    "compares",
    "distinguishes",
    "explains",
    "identifies",
    "includes",
    "maps",
    "names",
    "preserves",
    "records",
    "refuses",
    "reports",
    "returns",
    "separates",
    "states",
    "uses",
}


NEGATED_BOUNDARY_PRONE_PHRASES = {
    "ci passed",
    "commands were executed",
    "hosted ci passed",
    "remote checks passed",
    "validation passed",
}
TEXT_FIELD_ASSERTION_TYPES = frozenset(
    {"text_field_equals", "text_field_in", "text_field_present", "text_field_absent"}
)
STRUCTURED_FIELD_ASSERTION_KEYS = (
    "publication_gate_status",
    "publication_status",
    "evidence_level",
    "external_factual_claims",
    "unsupported_external_claims",
    "claim_authority",
    "clarification_state",
    "codexrepo_validation_status",
    "source_confidence",
)


def release_rubric_regex_checks(acceptance: list[Any], scenario_id: str) -> list[dict[str, Any]]:
    positive_regex_items = _acceptance_items_of_type(acceptance, scenario_id, {"regex"})
    semantic_items = _acceptance_items_of_type(acceptance, scenario_id, SEMANTIC_ACCEPTANCE_TYPES)
    brittle_negative_items = _negated_boundary_prone_items(acceptance, scenario_id)
    keyword_list_items = _keyword_list_expected_signal_items(acceptance, scenario_id)
    return [
        {
            "id": "release_rubric_regex_not_primary",
            "status": "blocker" if positive_regex_items else "pass",
            "severity": "blocker",
            "message": "Release rubrics must not use positive regex checks as scorer-facing proof; use behavioral expected_signal or typed assertions.",
            "evidence": positive_regex_items,
        },
        {
            "id": "release_rubric_semantic_coverage",
            "status": "pass" if len(semantic_items) >= 2 else "blocker",
            "severity": "blocker",
            "message": "Release rubrics must include at least two semantic or typed checks so wording variation does not dominate Tessl impact.",
            "evidence": [f"{scenario_id}:semantic_acceptance_count:{len(semantic_items)}"] if len(semantic_items) < 2 else [],
        },
        {
            "id": "release_rubric_negated_boundary_safe",
            "status": "blocker" if brittle_negative_items else "pass",
            "severity": "blocker",
            "message": "Release rubrics must not use phrase-only negative checks for readiness boundary claims because negated safe statements can contain the same phrase.",
            "evidence": brittle_negative_items,
        },
        {
            "id": "release_rubric_expected_signal_behavioral_sentence",
            "status": "blocker" if keyword_list_items else "pass",
            "severity": "blocker",
            "message": "Release expected_signal checks must describe observable behavior, not comma-separated keyword lists that overfit house phrasing.",
            "evidence": keyword_list_items,
        },
    ]


def semantic_requirement_terms(item: dict[str, Any]) -> list[str]:
    requirements = item.get("requirements")
    if not isinstance(requirements, list):
        return []
    return [
        str(term)
        for requirement in requirements
        if isinstance(requirement, dict)
        for key in ("any_of", "all_of")
        for term in requirement.get(key) or []
        if isinstance(term, str)
    ]


def semantic_requirements_malformed(item: dict[str, Any]) -> bool:
    requirements = item.get("requirements")
    return not isinstance(requirements, list) or not requirements or any(
        _semantic_requirement_malformed(requirement) for requirement in requirements
    )


def evaluate_semantic_requirements(output_text: str, item: dict[str, Any]) -> Optional[str]:
    requirements = item.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        return "semantic_requirements missing non-empty requirements list"
    for index, requirement in enumerate(requirements, start=1):
        failure = _evaluate_semantic_requirement(output_text, requirement, index)
        if failure:
            return failure
    return None


def _evaluate_semantic_requirement(output_text: str, requirement: Any, index: int) -> Optional[str]:
    if not isinstance(requirement, dict):
        return f"semantic_requirements requirement #{index} must be an object"
    requirement_id = str(requirement.get("id") or "").strip()
    alternatives = _runtime_terms(requirement, "any_of")
    required = _runtime_terms(requirement, "all_of")
    if not requirement_id:
        return f"semantic_requirements requirement #{index} missing id"
    if alternatives is None or required is None or not (alternatives or required):
        return f"semantic_requirements requirement {requirement_id!r} needs non-empty any_of and/or all_of strings"
    if not _semantic_requirement_matches(output_text, alternatives, required):
        return f"semantic_requirements failed: {requirement_id}"
    return None


def _semantic_requirement_matches(output_text: str, alternatives: list[str], required: list[str]) -> bool:
    alternative_match = not alternatives or any(_runtime_contains(output_text, term) for term in alternatives)
    required_match = not required or all(_runtime_contains(output_text, term) for term in required)
    return alternative_match and required_match


def _runtime_terms(requirement: dict[str, Any], key: str) -> Optional[list[str]]:
    raw_terms = requirement.get(key)
    if raw_terms is None:
        return []
    if not isinstance(raw_terms, list) or not raw_terms:
        return None
    return [term for term in raw_terms if isinstance(term, str) and term.strip()] if all(
        isinstance(term, str) and term.strip() for term in raw_terms
    ) else None


def _runtime_contains(haystack: str, needle: str) -> bool:
    return _normalize_runtime_text(needle) in _normalize_runtime_text(haystack)


def _normalize_runtime_text(value: str) -> str:
    return value.replace("`", "").replace("**", "").casefold()


def _semantic_requirement_malformed(requirement: Any) -> bool:
    if not isinstance(requirement, dict) or not str(requirement.get("id") or "").strip():
        return True
    terms = [requirement.get(key) for key in ("any_of", "all_of")]
    return not any(value is not None for value in terms) or any(
        value is not None and not _semantic_terms_valid(value) for value in terms
    )


def _semantic_terms_valid(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(term, str) and term.strip() for term in value
    )


def acceptance_assertion_shape_checks(
    case: dict[str, Any],
    scenario_id: str,
    supported_types: set[str],
) -> list[dict[str, Any]]:
    entries = [
        (item, str(item.get("type") or ""), f"{scenario_id}:acceptance[{index}]")
        for index, item in enumerate(case.get("acceptance") or [], start=1)
        if isinstance(item, dict)
    ]
    unsupported = [f"{marker}:{kind or 'missing_type'}" for item, kind, marker in entries if kind not in supported_types]
    malformed_fields = [marker for item, kind, marker in entries if _text_field_assertion_malformed(item, kind)]
    malformed_semantic = [marker for item, kind, marker in entries if kind == "semantic_requirements" and semantic_requirements_malformed(item)]
    regex_fields = [ref for item, kind, marker in entries for ref in _regex_structured_field_refs(item, kind, marker)]
    return [
        _shape_check("text_output_runner_acceptance_supported", unsupported, "Scenario acceptance types must be executable by the text-output skill eval runner before release."),
        _shape_check("typed_text_field_assertions_valid", malformed_fields, "text_field_* assertions must declare field/fields and expected values when required."),
        _shape_check("semantic_requirements_shape_valid", malformed_semantic, "semantic_requirements assertions must declare stable ids and non-empty any_of and/or all_of terms."),
        _shape_check("structured_fields_use_typed_assertions", regex_fields, "Known structured output fields must use text_field_* assertions instead of regex."),
    ]


def _shape_check(check_id: str, evidence: list[str], message: str) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": "blocker" if evidence else "pass",
        "severity": "blocker",
        "message": message,
        "evidence": evidence,
    }


def _text_field_assertion_malformed(item: dict[str, Any], assertion_type: str) -> bool:
    if assertion_type not in TEXT_FIELD_ASSERTION_TYPES:
        return False
    field = item.get("field") or item.get("key") or item.get("path")
    fields = item.get("fields")
    has_field = isinstance(field, str) and bool(field.strip())
    has_fields = isinstance(fields, list) and any(isinstance(value, str) and value.strip() for value in fields)
    has_expected = assertion_type in {"text_field_present", "text_field_absent"} or _has_text_field_expected_value(item)
    return not (has_field or has_fields) or not has_expected


def _has_text_field_expected_value(item: dict[str, Any]) -> bool:
    value = item.get("value")
    if isinstance(value, str) and value.strip():
        return True
    values = item.get("values")
    return isinstance(values, list) and any(isinstance(value, str) and value.strip() for value in values)


def _regex_structured_field_refs(item: dict[str, Any], assertion_type: str, marker: str) -> list[str]:
    if assertion_type != "regex":
        return []
    value = str(item.get("value") or "")
    return [f"{marker}:{key}" for key in STRUCTURED_FIELD_ASSERTION_KEYS if key in value][:1]


def _acceptance_items_of_type(acceptance: list[Any], scenario_id: str, accepted_types: set[str]) -> list[str]:
    return [
        f"{scenario_id}:acceptance[{index}]"
        for index, item in enumerate(acceptance, start=1)
        if isinstance(item, dict)
        and str(item.get("type") or "").strip().lower()
        in accepted_types
    ]


def _negated_boundary_prone_items(acceptance: list[Any], scenario_id: str) -> list[str]:
    evidence: list[str] = []
    for index, item in enumerate(acceptance, start=1):
        if not isinstance(item, dict):
            continue
        item_type = str(item.get("type") or "").strip().lower()
        if item_type != "not_contains":
            continue
        value = str(item.get("value") or "").replace("\\ ", " ").lower()
        if "encourages or permits this failure mode" in value:
            continue
        if any(phrase in value for phrase in NEGATED_BOUNDARY_PRONE_PHRASES):
            evidence.append(f"{scenario_id}:acceptance[{index}]")
    return evidence


def _keyword_list_expected_signal_items(acceptance: list[Any], scenario_id: str) -> list[str]:
    evidence: list[str] = []
    for index, item in enumerate(acceptance, start=1):
        if not isinstance(item, dict):
            continue
        item_type = str(item.get("type") or "").strip().lower()
        if item_type != "expected_signal":
            continue
        value = str(item.get("value") or "").strip()
        words = [word for word in value.replace(".", " ").replace(",", " ").split() if word]
        if (value.count(",") >= 2 and len(words) <= 8) or _looks_like_keyword_fragment(value, words):
            evidence.append(f"{scenario_id}:acceptance[{index}]")
    return evidence


def _looks_like_keyword_fragment(value: str, words: list[str]) -> bool:
    if not 2 <= len(words) <= 8:
        return False
    if any(separator in value for separator in [",", ";", ":", ".", "?", "!"]):
        return False
    normalized_words = [word.strip("()[]{}").lower() for word in words]
    if any(word in BEHAVIOR_VERBS for word in normalized_words):
        return False
    return value[:1].islower()
