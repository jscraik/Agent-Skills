from __future__ import annotations

import re


BEHAVIORAL_TESSL_ACCEPTANCE_TYPES = {
    "expected_signal",
    "skill_selected",
    "artifact_exists",
    "artifact_contains",
    "command_success",
    "discovery_question",
    "forbidden_signal",
    "must_not",
    "must_not_claim",
    "must_not_do",
    "not_contains",
    "output_schema",
}
KEYWORD_ONLY_TESSL_ACCEPTANCE_TYPES = {"regex", "not_regex", "contains", "not_contains"}
CONCRETE_OUTPUT_ARTIFACT_RE = re.compile(r"(?i)(?<![A-Za-z0-9_.-])[A-Za-z0-9_.-]+\.(?:md|json|txt|yaml|yml)(?![A-Za-z0-9_.-])")
PROVENANCE_FIXTURE_PATH_RE = re.compile(r"(?i)\breferences/evals/[^\s]+\.md\b")
PROVENANCE_ONLY_VERBS_RE = re.compile(r"(?i)\b(names?|cites?|references?|points?\s+to|lists?)\b")
CASE_INPUT_PATH_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9_./-])(?:canonical|generated|fixtures?|inputs?|sources?)/[^\s,;:)\]}\"']+\.(?:md|json|txt|yaml|yml)\b"
)
SIDE_EFFECT_FILE_PROMPT_RE = re.compile(
    r"(?is)\b(?:write|save|create|produce)\b[^\n]{0,100}\b[A-Za-z0-9_.-]+\.(?:md|json|txt|yaml|yml)\b"
)
FINAL_ANSWER_FILE_MARKER_RE = re.compile(r"(?i)\b(?:return|provide|include|show)\b[^\n]{0,80}\b(?:contents?|final answer|response)\b")
INLINE_INPUT_MARKERS = (
    "<file",
    "```",
    "canonical excerpt",
    "generated excerpt",
    "file contents",
    "inline input",
)
GENERIC_EXPECTED_SIGNAL_RE = re.compile(
    r"(?is)^\s*demonstrates\s+the\s+skill-specific\s+behavior\s+in\s+this\s+case\s+should\s+contract\s*:"
)
SHALLOW_EXPECTED_SIGNAL_VALUES = {
    "mission-grounded next step",
    "direct non-workspace handling",
    "skill-specific next step",
    "safe next step",
    "validation evidence",
}
SUPPORTING_ONLY_ACCEPTANCE_TYPES = {"regex", "not_regex", "contains", "not_contains", "skill_selected", "skill_not_selected"}
NEGATIVE_ACCEPTANCE_TYPES = {"not_regex", "not_contains", "must_not", "must_not_claim", "must_not_do", "forbidden_signal"}
NO_INVENTION_CONSTRAINT_RE = re.compile(r"(?i)\b(?:do not invent|use only the supplied|missing evidence as blocked)\b")
NO_INVENTION_SUPPORT_RE = re.compile(r"(?i)\b(?:support channels?|slack)\b")
NO_INVENTION_COMMAND_RE = re.compile(r"(?i)\b(?:setup commands?|validation commands?|commands?)\b")
BROAD_SUPPORT_CHANNEL_NEGATIVE_RE = re.compile(
    r"(?i)(?:#\[[^\]]+\]|#[a-z][\w-]*|slack\s+(?:channel|support)|support\s+channel)"
)
BROAD_COMMAND_NEGATIVE_RE = re.compile(
    r"(?i)(?:pytest|uv|mise|npm|pnpm|yarn|\./bin/ask|setup\s+command|validation\s+command)"
)
GUARDRAIL_CASE_RE = re.compile(
    r"(?i)\b(?:hallucinat(?:e|ion|ions|ed|ing)|faithfulness|"
    r"(?:judge|grader|scorer|factual|source-of-truth|source of truth|"
    r"policy|safety|security)\s+guardrail|"
    r"guardrail\s+(?:judge|grader|scorer|eval|evaluation|check))\b"
)
GUARDRAIL_LABEL_RE = re.compile(
    r"(?i)\b(?:label(?:ed|led)?|human labels?|pass/fail|ordinary|adversarial|"
    r"true-positive|true-negative|false-positive|false-negative|precision|recall|held-out|calibrat(?:e|ed|ion))\b"
)
GUARDRAIL_DIMENSION_RE = re.compile(
    r"(?i)\b(?:sentence-level|per-sentence|factual accuracy|knowledge accuracy|"
    r"source-of-truth|relevance|policy compliance|contextual coherence)\b"
)
GUARDRAIL_STRUCTURED_OUTPUT_RE = re.compile(r"(?i)\b(?:machine-readable|structured|json|schema)\b")
GUARDRAIL_OUTCOME_TERMS = ("judge_parse_error", "judge_schema_error", "judge_semantic_fail", "judge_pass")
GUARDRAIL_RESPONSE_SCHEMA_TERMS = (
    "sentence_results",
    "overall_verdict",
    "failure_reason",
    "source_references",
)
GUARDRAIL_FAIL_CLOSED_RE = re.compile(
    r"(?i)\b(?:fail-closed|fail closed|unsupported factual claim|unsupported claim)\b"
)
SOURCE_REFERENCE_PASS_RE = re.compile(
    r"(?is)\b(?:exact|supporting)\b.*\b(?:source_references|source references|references?)\b.*\bpass\b|"
    r"\bpass\b.*\b(?:exact|supporting)\b.*\b(?:source_references|source references|references?)\b"
)
FAIL_RATIONALE_RE = re.compile(r"(?is)\b(?:rationale|failure_reason|reason)\b.*\bfail\b|\bfail\b.*\b(?:rationale|failure_reason|reason)\b")
JUDGE_CASE_RE = re.compile(
    r"(?i)\b(?:judge|grader|hallucinat(?:e|ion|ions|ed|ing)|faithfulness|"
    r"(?:judge|grader|scorer|factual|source-of-truth|source of truth|"
    r"policy|safety|security)\s+guardrail|"
    r"guardrail\s+(?:judge|grader|scorer|eval|evaluation|check))\b"
)
ROLE_TERMS = ("assistant", "agent", "model", "skill")
LEAKAGE_STOP_WORDS = {
    "about",
    "across",
    "after",
    "against",
    "also",
    "and",
    "any",
    "are",
    "artifact",
    "artifacts",
    "audit",
    "audits",
    "before",
    "being",
    "between",
    "case",
    "cases",
    "check",
    "checks",
    "claim",
    "claims",
    "command",
    "commands",
    "concrete",
    "criteria",
    "current",
    "decision",
    "does",
    "evidence",
    "file",
    "files",
    "final",
    "from",
    "given",
    "have",
    "into",
    "must",
    "name",
    "names",
    "next",
    "not",
    "one",
    "output",
    "proof",
    "repo",
    "repository",
    "return",
    "review",
    "scenario",
    "score",
    "scored",
    "scorecard",
    "skill",
    "state",
    "status",
    "that",
    "the",
    "this",
    "through",
    "used",
    "using",
    "validation",
    "what",
    "when",
    "with",
    "without",
}
SKILL_VALUE_CONTEXT_RE = re.compile(
    r"(?i)\b(?:agent|assistant|repo|repository|harness|readiness|validation|"
    r"workflow|tool|mcp|context|proof|evidence|guardrail|steering|"
    r"ci|pr|review|security|package|plugin|tessl|sdk|knowledge|capsule)\b"
)
UNRELATED_CREATIVE_RE = re.compile(
    r"(?i)\b(?:poem|haiku|sonnet|story|joke|song|recipe|lighthouse|"
    r"creative writing)\b"
)
SAFETY_OR_REFUSAL_RE = re.compile(
    r"(?i)\b(?:prompt injection|secret|credential|unsafe|malicious|hostile|"
    r"untrusted|override|ignore previous|delete|remove|exfiltrat|refuse)\b"
)
UNSTAGED_TESSL_REPO_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_./-])"
    r"(?:Infrastructure|Skills|Plugins|Docs|docs|skills-system|runtime|\.agents|\.codex|\.harness|\.skillsets)"
    r"/[^\s,;:)\]}\"']+"
)
CASE_TEXT_FIELDS = (
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


def normalize_tessl_acceptance_item(item: dict[object, object]) -> dict[str, str]:
    normalized = {str(key).strip(): str(value).strip() for key, value in item.items()}
    if "type" in normalized or "value" in normalized or "expected_skill" in normalized:
        return normalized

    recovered: dict[str, str] = {}
    for key, value in normalized.items():
        text = f"{key}: {value}".strip().strip("{} ")
        for match in re.finditer(
            r"(type|value|expected_skill)\s*:\s*(.*?)(?=,\s*(?:type|value|expected_skill)\s*:|$)",
            text,
        ):
            field = match.group(1)
            raw = match.group(2).strip().rstrip("}").strip()
            recovered[field] = raw.strip("\"'")
    return recovered or normalized


def _acceptance_type(item: object) -> str:
    if not isinstance(item, dict):
        return ""
    return str(normalize_tessl_acceptance_item(item).get("type") or "acceptance").strip().lower()


def _normalized_acceptance_items(case: dict[str, object]) -> list[dict[str, str]]:
    acceptance = case.get("acceptance")
    if not isinstance(acceptance, list):
        return []
    return [
        normalize_tessl_acceptance_item(item)
        for item in acceptance
        if isinstance(item, dict)
    ]


def _acceptance_value(item: dict[str, str]) -> str:
    return str(item.get("value") or item.get("expected_skill") or "").strip()


def _is_provenance_only_signal(value: str) -> bool:
    normalized = " ".join(value.split())
    return (
        bool(PROVENANCE_FIXTURE_PATH_RE.search(normalized))
        and bool(PROVENANCE_ONLY_VERBS_RE.search(normalized))
        and "evidence" in normalized.lower()
    )


def _case_has_behavioral_acceptance(case: dict[str, object]) -> bool:
    types = {str(item.get("type") or "acceptance").strip().lower() for item in _normalized_acceptance_items(case)}
    return bool(types & BEHAVIORAL_TESSL_ACCEPTANCE_TYPES)


def _acceptance_item_tests_skill_lift(item: dict[str, str]) -> bool:
    item_type = str(item.get("type") or "acceptance").strip().lower()
    value = _acceptance_value(item)
    if item_type in {
        "skill_selected",
        "artifact_exists",
        "artifact_contains",
        "command_success",
        "discovery_question",
        "output_schema",
    }:
        return True
    if item_type.startswith(("forbidden", "must_not")):
        return True
    return (
        item_type == "expected_signal"
        and bool(value)
        and not _is_provenance_only_signal(value)
        and not GENERIC_EXPECTED_SIGNAL_RE.match(value)
    )


def _case_has_skill_lift_acceptance(case: dict[str, object]) -> bool:
    return any(_acceptance_item_tests_skill_lift(item) for item in _normalized_acceptance_items(case))


def _case_scores_skill_name_as_primary_proof(case: dict[str, object]) -> bool:
    normalized_items = _normalized_acceptance_items(case)
    if not normalized_items:
        return False
    types = {str(item.get("type") or "acceptance").strip().lower() for item in normalized_items}
    if not (types & {"skill_selected", "skill_not_selected"}):
        return False
    if types <= SUPPORTING_ONLY_ACCEPTANCE_TYPES:
        return True
    substantive_types = types - SUPPORTING_ONLY_ACCEPTANCE_TYPES
    return not bool(substantive_types & {"expected_signal", "artifact_exists", "artifact_contains", "command_success", "output_schema", "must_not", "must_not_claim", "must_not_do", "forbidden_signal"})


def _case_has_keyword_only_acceptance(case: dict[str, object]) -> bool:
    acceptance = _normalized_acceptance_items(case)
    if not acceptance:
        return False
    types = {str(item.get("type") or "acceptance").strip().lower() for item in acceptance}
    return bool(types) and types <= KEYWORD_ONLY_TESSL_ACCEPTANCE_TYPES


def _case_has_concrete_output_artifact(case: dict[str, object]) -> bool:
    artifact_text = "\n".join(
        str(case.get(field) or "")
        for field in ("actual_artifact", "expected_artifact", "raw_response_artifact", "judge_detail_artifact")
    )
    if CONCRETE_OUTPUT_ARTIFACT_RE.search(artifact_text):
        return True
    prompt_text = "\n".join(str(case.get(field) or "") for field in ("prompt", "task"))
    for match in CONCRETE_OUTPUT_ARTIFACT_RE.finditer(prompt_text):
        prefix = prompt_text[max(0, match.start() - 80):match.start()]
        if re.search(r"(?i)\b(write|produce|create|save|output)\b", prefix):
            return True
    acceptance = _normalized_acceptance_items(case)
    return any(str(item.get("type") or "").strip().lower() in {"artifact_exists", "artifact_contains", "output_schema"} for item in acceptance)


def _case_depends_on_hidden_reference_read(case: dict[str, object]) -> bool:
    text = _case_text_for_quality(case)
    if not re.search(r"(?i)\b(discovery|round one|underspecified|ask one|smallest useful question)\b", text):
        return False
    return bool(re.search(r"(?i)\breferences/[^\s]+\.(?:md|yaml|yml|json)\b", text)) and not _case_has_concrete_output_artifact(case)


def _shallow_expected_signal_values(items: list[dict[str, str]]) -> list[str]:
    return [
        _acceptance_value(item).lower()
        for item in items
        if str(item.get("type") or "").strip().lower() == "expected_signal"
    ]


def _case_has_shallow_routing_oracle(case: dict[str, object]) -> bool:
    normalized_items = _normalized_acceptance_items(case)
    if not normalized_items:
        return False
    types = {str(item.get("type") or "acceptance").strip().lower() for item in normalized_items}
    if not types or not types <= {"skill_selected", "skill_not_selected", "expected_signal"}:
        return False
    expected_values = _shallow_expected_signal_values(normalized_items)
    if not expected_values:
        return True
    return all(value in SHALLOW_EXPECTED_SIGNAL_VALUES for value in expected_values)


def _case_has_fixture_path_acceptance(case: dict[str, object]) -> bool:
    return any(_is_provenance_only_signal(_acceptance_value(item)) for item in _normalized_acceptance_items(case))


def _case_has_prompt_scoring_mechanics(case: dict[str, object]) -> bool:
    prompt = str(case.get("prompt") or "")
    scoring_mechanics = (
        "Use the skill to handle this reviewed generated scenario",
        "Scenario fixture:",
        "Uses the generated scenario fixture as evidence",
    )
    return any(mechanic in prompt for mechanic in scoring_mechanics)


def _case_has_answer_leakage(case: dict[str, object]) -> bool:
    visible_text = "\n".join(str(case.get(field) or "") for field in ("prompt", "unit", "given", "should")).lower()
    for item in _normalized_acceptance_items(case):
        item_type = str(item.get("type") or "acceptance").strip().lower()
        if item_type.startswith(("must_not", "forbidden")):
            continue
        value = _acceptance_value(item)
        if len(value) >= 80 and value.lower() in visible_text:
            return True
    return False


def _token_stem(token: str) -> str:
    for suffix in ("iness", "ation", "ments", "ment", "ing", "ed", "es", "s"):
        if len(token) > len(suffix) + 4 and token.endswith(suffix):
            return token[: -len(suffix)]
    return token


def _leakage_tokens(text: str) -> set[str]:
    tokens: set[str] = set()
    for raw in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{3,}", text.lower()):
        if raw in LEAKAGE_STOP_WORDS:
            continue
        tokens.add(_token_stem(raw.replace("_", "-")))
    return tokens


def _positive_acceptance_values(case: dict[str, object]) -> list[str]:
    values: list[str] = []
    for item in _normalized_acceptance_items(case):
        item_type = str(item.get("type") or "acceptance").strip().lower()
        if item_type != "expected_signal":
            continue
        if item_type.startswith(("must_not", "forbidden", "not_")):
            continue
        value = _acceptance_value(item)
        if value:
            values.append(value)
    return values


def _case_has_semantic_answer_leakage(case: dict[str, object]) -> bool:
    visible_text = "\n".join(str(case.get(field) or "") for field in ("prompt", "task"))
    visible_tokens = _leakage_tokens(visible_text)
    if not visible_tokens:
        return False
    for value in _positive_acceptance_values(case):
        value_tokens = _leakage_tokens(value)
        if len(value_tokens) < 6:
            continue
        overlap = value_tokens & visible_tokens
        if len(overlap) >= 5 and len(overlap) / len(value_tokens) >= 0.35:
            return True
    return False


def _case_is_low_value_negative(case: dict[str, object]) -> bool:
    if str(case.get("category") or "").strip().lower() != "negative":
        return False
    eval_modes = case.get("eval_modes")
    modes = {str(mode).strip().lower() for mode in eval_modes} if isinstance(eval_modes, list) else set()
    if "release" not in modes:
        return False
    instruction_text = "\n".join(str(case.get(field) or "") for field in ("prompt", "given"))
    if SAFETY_OR_REFUSAL_RE.search(instruction_text):
        return False
    if SKILL_VALUE_CONTEXT_RE.search(instruction_text):
        return False
    return bool(UNRELATED_CREATIVE_RE.search(instruction_text))


def _case_has_unstaged_repo_path_reference(case: dict[str, object]) -> bool:
    text_parts = [str(case.get(field) or "") for field in ("prompt", "unit", "given", "should")]
    text_parts.extend(_acceptance_value(item) for item in _normalized_acceptance_items(case))
    return bool(UNSTAGED_TESSL_REPO_PATH_RE.search("\n".join(text_parts)))


def _case_depends_on_hidden_input_file(case: dict[str, object]) -> bool:
    prompt = str(case.get("prompt") or "")
    task = str(case.get("task") or "")
    visible_text = "\n".join([prompt, task])
    if not CASE_INPUT_PATH_RE.search(visible_text):
        return False
    lowered = visible_text.lower()
    if any(marker in lowered for marker in INLINE_INPUT_MARKERS):
        return False
    return bool(re.search(r"(?i)\b(inspect|read|review|compare|audit|use|open)\b", visible_text))


def _case_requires_file_side_effect_without_final_answer_path(case: dict[str, object]) -> bool:
    visible_text = "\n".join(str(case.get(field) or "") for field in ("prompt", "task"))
    if not SIDE_EFFECT_FILE_PROMPT_RE.search(visible_text):
        return False
    return not FINAL_ANSWER_FILE_MARKER_RE.search(visible_text)


def _case_acceptance_text_parts(case: dict[str, object]) -> list[str]:
    text_parts: list[str] = []
    for item in _normalized_acceptance_items(case):
        text_parts.extend([
            str(item.get("type") or ""),
            str(item.get("value") or ""),
            str(item.get("expected_skill") or ""),
        ])
    return text_parts


def _case_expected_signal_text_parts(case: dict[str, object]) -> list[str]:
    expected_signals = case.get("expected_signals")
    if not isinstance(expected_signals, dict):
        return []
    text_parts: list[str] = []
    for value in expected_signals.values():
        if isinstance(value, list):
            text_parts.extend(str(item) for item in value)
        else:
            text_parts.append(str(value))
    return text_parts


def _case_text_for_quality(case: dict[str, object]) -> str:
    text_parts = [str(case.get(field) or "") for field in CASE_TEXT_FIELDS]
    text_parts.extend(_case_acceptance_text_parts(case))
    text_parts.extend(_case_expected_signal_text_parts(case))
    return "\n".join(text_parts)


def _case_instruction_text(case: dict[str, object]) -> str:
    fields = ("id", "name", "category", "unit", "given", "should", "prompt", "task")
    return "\n".join(str(case.get(field) or "") for field in fields)


def _case_has_guardrail_calibration_shape(case: dict[str, object]) -> bool:
    case_text = _case_text_for_quality(case)
    if not GUARDRAIL_CASE_RE.search(case_text):
        return True
    has_structured_output = bool(GUARDRAIL_STRUCTURED_OUTPUT_RE.search(case_text))
    acceptance = case.get("acceptance")
    if isinstance(acceptance, list):
        has_structured_output = has_structured_output or any(_acceptance_type(item) == "output_schema" for item in acceptance)
    return bool(GUARDRAIL_LABEL_RE.search(case_text)) and bool(GUARDRAIL_DIMENSION_RE.search(case_text)) and has_structured_output


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
    return all(term in normalized for term in GUARDRAIL_RESPONSE_SCHEMA_TERMS) and bool(GUARDRAIL_FAIL_CLOSED_RE.search(case_text))


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


def _case_has_scenario_context(case: dict[str, object]) -> bool:
    fields = [str(case.get(field) or "").strip() for field in ("unit", "given", "should")]
    if all(fields):
        return True
    prompt = str(case.get("prompt") or "").strip()
    return prompt.count("\n") >= 3 and len(prompt) >= 240


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


def _missing_behavioral_acceptance(case: dict[str, object]) -> bool:
    return not _case_has_behavioral_acceptance(case)


def _missing_skill_lift_acceptance(case: dict[str, object]) -> bool:
    return _case_has_behavioral_acceptance(case) and not _case_has_skill_lift_acceptance(case)


def _missing_scenario_context(case: dict[str, object]) -> bool:
    return not _case_has_scenario_context(case)


def _release_case_missing_output_artifact(case: dict[str, object]) -> bool:
    eval_modes = case.get("eval_modes")
    modes = {str(mode) for mode in eval_modes} if isinstance(eval_modes, list) else set()
    mode = case.get("mode")
    if mode:
        modes.add(str(mode))
    return "release" in modes and not _case_has_concrete_output_artifact(case)


def _case_has_broad_no_invention_negative_acceptance(case: dict[str, object]) -> bool:
    case_text = _case_instruction_text(case)
    if not NO_INVENTION_CONSTRAINT_RE.search(case_text):
        return True
    negative_text = "\n".join(
        _acceptance_value(item)
        for item in _normalized_acceptance_items(case)
        if str(item.get("type") or "").strip().lower() in NEGATIVE_ACCEPTANCE_TYPES
    )
    if not negative_text.strip():
        return False
    if NO_INVENTION_SUPPORT_RE.search(case_text) and not BROAD_SUPPORT_CHANNEL_NEGATIVE_RE.search(negative_text):
        return False
    if NO_INVENTION_COMMAND_RE.search(case_text) and not BROAD_COMMAND_NEGATIVE_RE.search(negative_text):
        return False
    return True


TESSL_CASE_FINDING_RULES = (
    (
        _missing_scenario_context,
        "missing_scenario_context",
        "Tessl eval cases must include unit/given/should context or an equivalent structured prompt so the scorer can judge behaviour, not only keywords.",
    ),
    (
        _missing_behavioral_acceptance,
        "missing_behavioral_acceptance",
        "Tessl eval cases must include at least one behavioural acceptance item such as expected_signal, skill_selected, artifact_exists, command_success, or a must_not/forbidden signal.",
    ),
    (
        _missing_skill_lift_acceptance,
        "missing_skill_lift_acceptance",
        "Tessl eval cases must include at least one acceptance item that tests the skill's behaviour. Provenance-only fixture-path signals are useful supporting evidence, but they do not prove the skill improves the answer.",
    ),
    (
        _case_has_keyword_only_acceptance,
        "keyword_only_acceptance",
        "Regex and contains checks are allowed only as supporting evidence; they cannot be the whole Tessl scoring contract because baseline runs can pass them without demonstrating skill lift.",
    ),
    (
        _case_scores_skill_name_as_primary_proof,
        "skill_name_primary_proof",
        "Skill selection or skill-name mentions are supporting routing evidence only. Tessl criteria must score the observable behavior or output artifact that the skill should improve.",
    ),
    (
        _release_case_missing_output_artifact,
        "missing_concrete_output_artifact",
        "Release Tessl scenarios must request or name a concrete output artifact such as a markdown report, JSON receipt, or schema output so scoring is based on final files rather than hidden process traces.",
    ),
    (
        _case_depends_on_hidden_reference_read,
        "hidden_reference_dependency",
        "Discovery scenarios must be scoreable from the visible task and final artifact. Do not require isolated runners to read hidden references before producing the expected discovery question.",
    ),
    (
        _case_has_shallow_routing_oracle,
        "shallow_routing_oracle",
        "Tessl live-private evals must not rely only on skill selection plus generic expected signals. Add scenario-specific behavior, artifact, safety, or refusal criteria that create a plausible baseline failure path.",
    ),
    (
        _case_has_fixture_path_acceptance,
        "fixture_path_acceptance",
        "Tessl eval cases must not score provenance-only fixture path mentions. Fixture paths belong in scenario metadata, while acceptance must test observable behaviour that distinguishes skill lift from baseline output.",
    ),
    (
        _case_has_prompt_scoring_mechanics,
        "prompt_exposes_scoring_mechanics",
        "Tessl eval prompts must read like realistic user tasks and must not expose scenario fixture mechanics or tell the agent it is handling a generated scoring fixture.",
    ),
    (
        _case_has_answer_leakage,
        "answer_leakage",
        "Tessl eval task text must not contain the long-form expected answer that is later used as the scoring signal. Keep expected behaviour in hidden metadata or acceptance criteria, not in the agent-visible task.",
    ),
    (
        _case_has_semantic_answer_leakage,
        "semantic_answer_leakage",
        "Tessl eval task text must not preview the same answer dimensions later scored by positive criteria. Move expected dimensions into criteria and keep the visible task realistic.",
    ),
    (
        _case_is_low_value_negative,
        "low_value_negative_scenario",
        "Release scenarios should not spend live Tessl budget on unrelated creative negative prompts. Keep such cases in local routing smoke or rewrite them into realistic safety, authority, or boundary pressure.",
    ),
    (
        _case_has_unstaged_repo_path_reference,
        "unstaged_repo_path_reference",
        "Tessl live-private evals stage a controlled skill package copy, not the live repository. Use package-relative paths such as SKILL.md or references/contract.yaml, or provide an explicit fixture artifact before scoring repo-root paths.",
    ),
    (
        _case_depends_on_hidden_input_file,
        "hidden_input_file_dependency",
        "SDK and Tessl release scenarios must inline required input file contents or provide a staged fixture artifact; do not ask isolated runners to inspect package-relative files that are absent from the visible task.",
    ),
    (
        _case_requires_file_side_effect_without_final_answer_path,
        "read_only_file_artifact_side_effect",
        "OSS read-only release scenarios must ask for file artifact contents in the final answer rather than requiring the agent to write, save, create, or produce files in the sandbox.",
    ),
    (
        lambda case: not _case_has_broad_no_invention_negative_acceptance(case),
        "narrow_no_invention_negative_acceptance",
        "No-invention scenarios must include broad negative acceptance for the forbidden support paths or command families they name, so plausible invented Slack channels, setup commands, validation commands, owners, dates, recovery paths, or acceptance criteria cannot pass by synonym.",
    ),
)

TESSL_NEGATED_CASE_FINDING_RULES = (
    (
        _case_has_guardrail_calibration_shape,
        "guardrail_missing_calibration_shape",
        "Hallucination or guardrail eval cases must name the source-of-truth and sentence-level failure dimensions, include labeled ordinary or adversarial examples for calibration, and require machine-readable output before the guardrail can become release evidence.",
    ),
    (
        _case_has_paired_calibration_examples,
        "guardrail_missing_paired_examples",
        "Hallucination and subjective guardrail evals must include both positive_example_artifact and negative_example_artifact, or stay advisory until paired calibration examples exist.",
    ),
    (
        _case_has_guardrail_failure_outcomes,
        "guardrail_missing_judge_outcomes",
        "Guardrail evals must distinguish judge_parse_error, judge_schema_error, judge_semantic_fail, and judge_pass, and preserve raw judge output when parsing or schema validation fails.",
    ),
    (
        _case_has_guardrail_response_schema,
        "guardrail_missing_response_schema",
        "Guardrail evals must require sentence_results[], overall_verdict, failure_reason, source_references[], and a fail-closed aggregation rule for unsupported factual claims.",
    ),
    (
        _case_has_source_reference_quality,
        "guardrail_missing_source_reference_quality",
        "Guardrail evals must require exact supporting source references for pass decisions and keep fail rationales separate from pass references.",
    ),
    (
        _case_has_judge_sampling_policy,
        "judge_sampling_missing_repeat_count",
        "Judge evals that set judge_temperature must also capture judge_runs or sample_count so stochastic pass-rate gates remain advisory until calibrated.",
    ),
)


def _finding(case_id: str, code: str, message: str) -> dict[str, str]:
    return {"case_id": case_id, "code": code, "message": message}


def _case_rule_findings(case: dict[str, object]) -> list[dict[str, str]]:
    case_id = str(case.get("id") or "unknown")
    findings = [
        _finding(case_id, code, message)
        for predicate, code, message in TESSL_CASE_FINDING_RULES
        if predicate(case)
    ]
    findings.extend(
        _finding(case_id, code, message)
        for predicate, code, message in TESSL_NEGATED_CASE_FINDING_RULES
        if not predicate(case)
    )
    if _case_has_mixed_guardrail_terms(case):
        findings.append(_finding(
            case_id,
            "guardrail_mixed_terminology",
            "Guardrail and judge eval prompts must use consistent role and source-authority terms so the scorer knows what actor and evidence surface it is judging.",
        ))
    return findings


def tessl_eval_quality_findings(cases: list[dict[str, object]]) -> list[dict[str, str]]:
    findings = [finding for case in cases for finding in _case_rule_findings(case)]
    findings.extend(_synthetic_guardrail_label_balance_findings(cases))
    return findings
