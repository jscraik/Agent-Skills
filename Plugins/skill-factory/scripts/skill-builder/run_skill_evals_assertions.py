from run_skill_evals_assertions_core import *  # noqa: F403

def _expected_signal_terms(value: Any) -> List[str]:
    text = _to_text_blob(value).casefold()
    terms: List[str] = []
    seen = set()
    for token in re.findall(r"[a-z0-9][a-z0-9_-]{2,}", text):
        term = token[:-1] if len(token) > 4 and token.endswith("s") else token
        if term in _EXPECTED_SIGNAL_STOPWORDS:
            continue
        if term not in seen:
            seen.add(term)
            terms.append(term)
    return terms


def _evaluate_expected_signal_assertion(output_text: str, expected: Any) -> Optional[str]:
    expected_text = _to_text_blob(expected)
    if _contains_text(output_text, expected_text):
        return None

    expected_terms = _expected_signal_terms(expected_text)
    if not expected_terms:
        return f"expected_signal failed: {expected_text!r}"

    output_terms = set(_expected_signal_terms(output_text))
    matched = [term for term in expected_terms if term in output_terms]
    required_count = max(1, (len(expected_terms) + 1) // 2)
    if len(expected_terms) >= 8:
        required_count = max(4, required_count)

    if len(matched) >= required_count:
        return None

    missing = [term for term in expected_terms if term not in output_terms]
    preview = ", ".join(missing[:6])
    return (
        "expected_signal failed: "
        f"matched {len(matched)}/{len(expected_terms)} signal terms "
        f"(required {required_count}); missing: {preview}"
    )


def _evaluate_skill_selection_assertion(
    assertion: Dict[str, Any],
    *,
    skill_name: str,
    selected: Optional[bool],
) -> Optional[str]:
    t = assertion.get("type")
    expected_skill = assertion.get("expected_skill") or assertion.get("value") or skill_name
    expected_skill = str(expected_skill)

    if expected_skill and expected_skill != skill_name:
        # This eval runner validates the active skill; if another skill is expected, flag explicitly.
        return f"{t} expected_skill mismatch: expected {expected_skill!r}, active skill is {skill_name!r}"

    if selected is None:
        if t == "skill_not_selected":
            return None
        expectation = "selected" if t == "skill_selected" else "not selected"
        return (
            f"{t} failed: expected {skill_name!r} to be {expectation}, "
            "but selection signal was unavailable"
        )

    if t == "skill_selected" and not selected:
        return f"skill_selected failed: expected {skill_name!r} to be selected"

    if t == "skill_not_selected" and selected:
        return f"skill_not_selected failed: expected {skill_name!r} to NOT be selected"

    return None


_DISCOVERY_SCOPE_RE = re.compile(
    r"(?i)\b(?:doc(?:umentation)?|docs?|readme|runbook|surface|scope|path|target|goal|workflow|entit(?:y|ies)|state|storage|canonical|generated|projection|publication|audit-only|audit only|edit goal)\b"
)
_DISCOVERY_EDIT_CLAIM_RE = re.compile(
    r"(?i)\b(?:I changed|I've changed|I updated|I've updated|patched|rewrote|saved|committed)\b"
)
_DISCOVERY_POST_WORK_FRAME_RE = re.compile(
    r"(?i)\b(?:after|once|following)\s+(?:(?:I|we)\s+)?(?:inspect(?:ing|ed)?|edit(?:ing|ed)?|implement(?:ation|ing|ed)?|patch(?:ing|ed)?|rewrit(?:e|ing|ten)|chang(?:e|ing|ed))\b"
)


def _evaluate_discovery_question_assertion(text: str) -> Optional[str]:
    if _DISCOVERY_EDIT_CLAIM_RE.search(text):
        return "discovery_question failed: response claimed an edit before discovery"
    if _DISCOVERY_POST_WORK_FRAME_RE.search(text):
        return "discovery_question failed: response framed discovery after work began"
    if "?" not in text:
        return "discovery_question failed: response did not ask a question"
    if not _DISCOVERY_SCOPE_RE.search(text):
        return "discovery_question failed: response did not name a documentation scope, path, target, or surface"
    return None


def _evaluate_text_pattern_assertion(text: str, assertion: Dict[str, Any]) -> Optional[str]:
    assertion_type = assertion["type"]
    value = _to_text_blob(assertion.get("value", ""))
    if assertion_type == "contains" and not _contains_text(text, value):
        return f"contains failed: {value!r}"
    if assertion_type == "not_contains" and _contains_text(text, value):
        return f"not_contains failed: {value!r}"
    if assertion_type == "regex" and not re.search(value, text, flags=re.MULTILINE):
        return f"regex failed: /{value}/"
    if assertion_type == "not_regex" and re.search(value, text, flags=re.MULTILINE):
        return f"not_regex failed: /{value}/"
    return None


def _evaluate_text_assertion(
    text: str,
    assertion: Dict[str, Any],
    *,
    skill_name: str,
    selected_skill: Optional[bool],
) -> Optional[str]:
    assertion_type = assertion["type"]
    if assertion_type in {"contains", "not_contains", "regex", "not_regex"}:
        return _evaluate_text_pattern_assertion(text, assertion)
    if assertion_type in {"skill_selected", "skill_not_selected"}:
        return _evaluate_skill_selection_assertion(assertion, skill_name=skill_name, selected=selected_skill)
    if assertion_type in {"text_field_equals", "text_field_in", "text_field_present", "text_field_absent"}:
        return _evaluate_text_field_assertion(text, assertion)
    if assertion_type == "expected_signal":
        return _evaluate_expected_signal_assertion(text, assertion.get("value", ""))
    if assertion_type == "semantic_requirements":
        return evaluate_semantic_requirements(text, assertion)
    if assertion_type == "discovery_question":
        return _evaluate_discovery_question_assertion(text)
    return f"unsupported assertion type for text output: {assertion_type!r}"


def evaluate_assertions_text(
    text: str,
    assertions: List[Assertion],
    *,
    skill_name: str,
    selected_skill: Optional[bool],
) -> List[str]:
    failures: List[str] = []
    for raw in assertions:
        message = _evaluate_text_assertion(
            text,
            _normalize_assert(raw),
            skill_name=skill_name,
            selected_skill=selected_skill,
        )
        if message:
            failures.append(message)
    return failures


def _evaluate_json_path_assertion(obj: Any, assertion: Dict[str, Any]) -> Optional[str]:
    assertion_type = assertion["type"]
    path = assertion.get("path")
    if not isinstance(path, str) or not path.strip():
        return f"{assertion_type} missing `path`"
    try:
        actual = _json_get_path(obj, path)
    except KeyError:
        return f"{assertion_type} {'missing path' if assertion_type == 'jsonpath_equals' else 'failed (missing)'}: {path}"
    if assertion_type == "jsonpath_equals" and actual != assertion.get("value"):
        return f"jsonpath_equals failed at {path}: got={actual!r} expected={assertion.get('value')!r}"
    return None


def _evaluate_json_assertion(
    obj: Any,
    assertion: Dict[str, Any],
    *,
    skill_name: str,
    selected_skill: Optional[bool],
) -> Optional[str]:
    assertion_type = assertion["type"]
    if assertion_type in {"contains", "not_contains", "regex", "not_regex", "skill_selected", "skill_not_selected", "expected_signal", "semantic_requirements", "discovery_question"}:
        return _evaluate_text_assertion(json.dumps(obj, ensure_ascii=False, indent=2), assertion, skill_name=skill_name, selected_skill=selected_skill)
    if assertion_type in {"text_field_equals", "text_field_in", "text_field_present", "text_field_absent"}:
        return _evaluate_json_text_field_assertion(obj, assertion)
    if assertion_type in {"jsonpath_equals", "jsonpath_exists"}:
        return _evaluate_json_path_assertion(obj, assertion)
    return f"unsupported assertion type for json output: {assertion_type!r}"


def evaluate_assertions_json(
    obj: Any,
    assertions: List[Assertion],
    *,
    skill_name: str,
    selected_skill: Optional[bool],
) -> List[str]:
    failures: List[str] = []
    for raw in assertions:
        message = _evaluate_json_assertion(obj, _normalize_assert(raw), skill_name=skill_name, selected_skill=selected_skill)
        if message:
            failures.append(message)
    return failures


def _normalize_signal_text(value: Any) -> str:
    text = _to_text_blob(value).casefold()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _score_required_signals(output_index: str, expected: List[str]) -> Dict[str, Any]:
    matched = [item for item in expected if _normalize_signal_text(item) in output_index]
    missing = [item for item in expected if item not in matched]
    score = 100 if not expected else round((len(matched) / len(expected)) * 100)
    return {"score": score, "matched": matched, "missing": missing}


def _score_forbidden_signals(output_index: str, forbidden: List[str]) -> Dict[str, Any]:
    found = [item for item in forbidden if _normalize_signal_text(item) in output_index]
    score = 100 if not forbidden else round(((len(forbidden) - len(found)) / len(forbidden)) * 100)
    return {"score": score, "found": found}


def _score_flow_steps(output_index: str, expected: List[str]) -> Dict[str, Any]:
    positions: List[int] = []
    missing: List[str] = []
    for item in expected:
        pos = output_index.find(_normalize_signal_text(item))
        if pos < 0:
            missing.append(item)
        positions.append(pos)

    present_positions = [pos for pos in positions if pos >= 0]
    present_score = 100 if not expected else round((len(present_positions) / len(expected)) * 100)
    in_order = bool(expected) and not missing and present_positions == sorted(present_positions)
    order_score = 100 if not expected or in_order else 0
    score = round((present_score * 0.65) + (order_score * 0.35))
    return {
        "score": score,
        "expected": expected,
        "missing": missing,
        "positions": positions,
        "in_order": True if not expected else in_order,
    }


def evaluate_expected_signals(output_text: str, expected_signals: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not expected_signals:
        return None

    output_index = _normalize_signal_text(output_text)
    dimensions: Dict[str, Dict[str, Any]] = {}
    missing_signals: List[str] = []
    forbidden_signals_found: List[str] = []
    risk_factors: List[str] = []

    for key, label in EXPECTED_SIGNAL_REQUIRED_DIMENSIONS.items():
        items = expected_signal_items(expected_signals, key)
        if not items:
            continue
        result = _score_required_signals(output_index, items)
        dimensions[key] = result
        missing_signals.extend(f"{label}: {item}" for item in result["missing"])

    for key, label in EXPECTED_SIGNAL_FORBIDDEN_DIMENSIONS.items():
        items = expected_signal_items(expected_signals, key)
        if not items:
            continue
        result = _score_forbidden_signals(output_index, items)
        dimensions[key] = result
        forbidden_signals_found.extend(f"{label}: {item}" for item in result["found"])

    flow_steps = expected_signal_items(expected_signals, EXPECTED_SIGNAL_FLOW_KEY)
    if flow_steps:
        flow_result = _score_flow_steps(output_index, flow_steps)
        dimensions[EXPECTED_SIGNAL_FLOW_KEY] = flow_result
        missing_signals.extend(f"flow step: {item}" for item in flow_result["missing"])
        if not flow_result["in_order"]:
            risk_factors.append("flow_steps out of order or incomplete")

    scores = [int(d["score"]) for d in dimensions.values() if isinstance(d.get("score"), int)]
    composite = round(sum(scores) / len(scores)) if scores else 100
    if composite < 80:
        risk_factors.append("expected signal score below 80")
    if forbidden_signals_found:
        risk_factors.append("forbidden signals present")

    return {
        EXPECTED_SIGNAL_COMPOSITE_KEY: composite,
        "dimensions": dimensions,
        EXPECTED_SIGNAL_MISSING_KEY: missing_signals,
        EXPECTED_SIGNAL_FORBIDDEN_FOUND_KEY: forbidden_signals_found,
        EXPECTED_SIGNAL_RISK_FACTORS_KEY: risk_factors,
    }


def summarize_expected_signal_results(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    scores: List[int] = []
    risky_cases: List[Dict[str, Any]] = []
    for case in cases:
        for runner_name, runner in (case.get("runners") or {}).items():
            expected = ((runner.get("metrics") or {}).get(EXPECTED_SIGNAL_METRIC_KEY) or {})
            score = expected.get(EXPECTED_SIGNAL_COMPOSITE_KEY)
            if not isinstance(score, int):
                continue
            scores.append(score)
            risk_factors = expected.get(EXPECTED_SIGNAL_RISK_FACTORS_KEY) or []
            if score < 80 or risk_factors:
                risky_cases.append(
                    {
                        "case": case.get("id"),
                        "runner": runner_name,
                        "score": score,
                        EXPECTED_SIGNAL_RISK_FACTORS_KEY: risk_factors,
                    }
                )

    return {
        "runs": len(scores),
        "average": round(sum(scores) / len(scores)) if scores else None,
        "minimum": min(scores) if scores else None,
        "risky_cases": risky_cases,
    }


def detect_skill_selected(
    *,
    skill_name: str,
    output_text: str,
    stdout_text: str,
    stderr_text: str,
    events: Optional[List[Dict[str, Any]]],
) -> Optional[bool]:
    """
    Best-effort skill-selection detection from runner artifacts.

    Returns True/False when signals are present, or None when unknown.
    """

    skill_l = skill_name.lower().strip()
    if not skill_l:
        return None

    final_text = output_text or ""
    final_low = final_text.lower()

    explicit_negative_patterns = [
        rf"\b{re.escape(skill_l)}\b\s+is\s+overkill\b",
        rf"\boverkill\b[^\n]{{0,32}}\b{re.escape(skill_l)}\b",
        rf"\b(?:do not|don't|did not|didn't|not)\b[^\n]{{0,32}}\b(?:use|trigger|select|invoke)\b[^\n]{{0,48}}\b{re.escape(skill_l)}\b",
    ]
    if any(re.search(p, final_low, flags=re.IGNORECASE) for p in explicit_negative_patterns):
        return False

    explicit_positive_patterns = [
        rf"\${re.escape(skill_l)}\b",
        rf"\b(?:using|used|invoked|selected|triggered|routed to)\b[^\n]{{0,48}}\$?{re.escape(skill_l)}\b",
    ]
    if any(re.search(p, final_low, flags=re.IGNORECASE) for p in explicit_positive_patterns):
        return True

    blobs = [final_text, stdout_text or "", stderr_text or ""]
    if events:
        event_blob = json.dumps(events, ensure_ascii=False, sort_keys=True)
        blobs.append(event_blob)
    blob = "\n".join(blobs)
    low = blob.lower()

    positive_patterns = [
        rf"\${re.escape(skill_l)}\b",
        rf"\b(?:using|used|invoke(?:d)?|select(?:ed)?|trigger(?:ed)?|route(?:d)?)\b[^\n]{{0,64}}\$?{re.escape(skill_l)}\b",
        rf"\bskill(?:_name| name)?\b[^\n]{{0,40}}{re.escape(skill_l)}\b",
        rf"\b{re.escape(skill_l)}\b[^\n]{{0,30}}\bskill\b",
    ]

    negative_patterns = [
        rf"\b(?:did not|didn't|not|failed to|unable to)\b[^\n]{{0,50}}\b(?:trigger|select|invoke)\b[^\n]{{0,64}}\$?{re.escape(skill_l)}\b",
        rf"\b(?:not selected|not triggered)\b[^\n]{{0,40}}\$?{re.escape(skill_l)}\b",
    ]

    pos = any(re.search(p, low, flags=re.IGNORECASE) for p in positive_patterns)
    neg = any(re.search(p, low, flags=re.IGNORECASE) for p in negative_patterns)

    if pos and not neg:
        return True
    if neg and not pos:
        return False
    if pos and neg:
        # conflicting signal; unknown
        return None

    for event in events or []:
        if not isinstance(event, dict):
            continue

        for key in ("skill", "skill_name", "selected_skill", "selected", "tool_name"):
            value = event.get(key)
            if isinstance(value, str) and skill_l in value.lower():
                event_value = value.strip().lower()
                if key in {"selected", "selected_skill"}:
                    return event_value == skill_l
                if key in {"skill", "skill_name", "tool_name"}:
                    return True

        metadata = event.get("metadata")
        if isinstance(metadata, dict):
            meta_skill = metadata.get("skill") if "skill" in metadata else metadata.get("selected_skill")
            if isinstance(meta_skill, str) and skill_l in meta_skill.lower():
                return True

        tool = event.get("tool")
        if isinstance(tool, dict):
            tool_name = tool.get("name")
            if isinstance(tool_name, str) and skill_l in tool_name.lower():
                return True

    return None


def extract_rubric_metrics(parsed_json: Any) -> Optional[Dict[str, Any]]:
    """
    Extracts rubric-style metrics from a parsed JSON object.

    When the input is a mapping containing any of the keys "overall_pass", "score", or "checks",
    this returns a dictionary with the extracted metrics. The returned mapping may include:
    - "overall_pass": the boolean value from the input when present.
    - "score": the numeric score coerced to a float when present.
    - "checks_count": the number of entries in the "checks" list when present.
    - "checks_passed": count of check entries with a boolean `"pass": true`.
    - "checks_failed": count of check entries with a boolean `"pass": false`.

    Returns:
        A dict with the extracted metrics as described above, or `None` if the input is not a mapping
        or contains none of the recognized rubric fields.
    """
    if not isinstance(parsed_json, dict):
        return None

    has_any = any(k in parsed_json for k in ("overall_pass", "score", "checks"))
    if not has_any:
        return None

    metrics: Dict[str, Any] = {}
    if isinstance(parsed_json.get("overall_pass"), bool):
        metrics["overall_pass"] = parsed_json["overall_pass"]
    if isinstance(parsed_json.get("score"), (int, float)):
        metrics["score"] = float(parsed_json["score"])
    checks = parsed_json.get("checks")
    if isinstance(checks, list):
        metrics["checks_count"] = len(checks)
        passed = 0
        failed = 0
        for item in checks:
            if isinstance(item, dict) and isinstance(item.get("pass"), bool):
                if item["pass"]:
                    passed += 1
                else:
                    failed += 1
        metrics["checks_passed"] = passed
        metrics["checks_failed"] = failed

    return metrics or None


def _parse_agent_self_assessment(output_text: str) -> Optional[bool]:
    """
    Parse agent's explicit self-assessment from output text.

    Looks for patterns like:
    - "Pass/fail: - Fail"
    - "Pass/fail: Pass"
    - "Result: Fail"
    etc.

    Returns:
        True if agent reports pass, False if agent reports fail, None if no clear signal.
    """
    verdict_pattern = re.compile(
        r"(?im)^\s*(?:pass\s*/\s*fail|result|status)\s*:?\s*-?\s*(pass|fail)\b"
    )
    verdicts = verdict_pattern.findall(output_text)
    if not verdicts:
        return None

    return verdicts[-1].lower() == "pass"


def _acceptance_skip_reason(*, exit_code: int, output_text: str) -> Optional[str]:
    """
    Return a skip reason when acceptance assertions should be skipped because the runner failed and produced no final output.

    Parameters:
        exit_code (int): The runner process exit code.
        output_text (str): The runner's final output text.

    Returns:
        Optional[str]: A human-readable skip reason when acceptance checks should be skipped, or `None` when they should be performed.
    """
    if exit_code == 0:
        return None
    if output_text.strip():
        return None
    return "skipped acceptance assertions because the runner exited non-zero and produced no final output"

__all__ = [name for name in globals() if not name.startswith("__")]
