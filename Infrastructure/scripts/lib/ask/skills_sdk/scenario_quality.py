from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from ask.skills_sdk.release_scenario_sets import build_release_scenario_set_checks, release_scenario_set_case_ids
from ask.skills_sdk.scenario_set_parity import build_scenario_set_parity_checks
from ask.skills_sdk.generated_eval_fixtures import parse_generated_eval_fixtures
from ask.skills_sdk.release_rubric_checks import release_rubric_regex_checks

SCENARIO_QUALITY_SCHEMA_VERSION = "skills-sdk.scenario-quality-receipt.v0"
SCENARIO_QUALITY_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/scenario-quality-receipt.v0.schema.json"
)
SCENARIO_QUALITY_ACCEPTANCE_TRACE = ["PU-030", "FR-003", "FR-008", "SA-003", "VP-030"]
RAW_SECRET_PATTERNS = ("api_key=", "password=", "secret=", "token=")
REGISTRY_DEPENDENCY_CLAIM = "sdk-scenario-generator.registry-dependency"
RUBRIC_FAILURE_TERMS = (
    "avoid",
    "block",
    "blocked",
    "does not",
    "do not",
    "freeze",
    "must not",
    "not claim",
    "refuse",
    "reject",
    "without",
)
RUBRIC_EVIDENCE_TERMS = (
    "artifact",
    "command",
    "criteria",
    "evidence",
    "file",
    "metadata",
    "proof",
    "result",
    "scenario",
    "score",
    "signal",
    "source",
    "validation",
)
TEXT_FIELD_ASSERTION_TYPES = {"text_field_equals", "text_field_in", "text_field_present", "text_field_absent"}
TEXT_OUTPUT_RUNNER_ACCEPTANCE_TYPES = {
    "contains", "not_contains", "regex", "not_regex", "skill_selected", "skill_not_selected",
    "expected_signal", "discovery_question", *TEXT_FIELD_ASSERTION_TYPES,
}
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
PLATFORM_PARITY_GATE_ID_PREFIX = "platform_tessl_quality"

class ScenarioQualityError(ValueError):
    def __init__(self, receipt: dict[str, Any]) -> None:
        super().__init__(receipt["agent_summary"])
        self.receipt = receipt


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _check(check_id: str, status: str, message: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {"id": check_id, "status": status, "severity": "blocker", "message": message, "evidence": evidence or []}


def _yaml_safe_load(text: str) -> Any:
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError:
        except ModuleNotFoundError:
            ruby_loaded = _ruby_yaml_safe_load(text)
            if ruby_loaded is not None:
                return ruby_loaded
            return _load_minimal_evals_yaml(text)
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as exc:  # type: ignore[attr-defined]
        raise ValueError(str(exc)) from exc


def _ruby_yaml_safe_load(text: str) -> Any | None:
    code = "require 'yaml'; require 'json'; print JSON.generate(YAML.safe_load(STDIN.read, permitted_classes: [], aliases: false))"
    try:
        completed = subprocess.run(
            ["ruby", "-e", code],
            input=text,
            text=True,
            capture_output=True,
            check=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"ruby_yaml_json_decode_error: {exc}") from exc


def _load_minimal_evals_yaml(text: str) -> dict[str, Any]:
    state: dict[str, Any] = {
        "cases": [],
        "current": None,
        "current_list": None,
        "current_mapping": None,
        "last_scalar_key": None,
        "in_cases": False,
        "case_indent": None,
    }
    for raw_line in text.splitlines():
        stripped, indent = _minimal_line(raw_line)
        if not stripped:
            continue
        if stripped == "cases:":
            state["in_cases"] = True
            state["current"] = None
            state["current_list"] = None
            state["current_mapping"] = None
            state["last_scalar_key"] = None
            state["case_indent"] = None
            continue
        if not state["in_cases"]:
            continue
        if _consume_minimal_line(state, stripped, indent):
            continue
        else:
            raise ValueError("minimal_yaml_parse_unsupported")
    return {"cases": state["cases"]}


def _minimal_line(raw_line: str) -> tuple[str, int]:
    line = _strip_yaml_comment(raw_line).rstrip()
    return line.strip(), len(line) - len(line.lstrip(" "))


def _strip_yaml_comment(raw_line: str) -> str:
    in_single = False
    in_double = False
    for index, char in enumerate(raw_line):
        if char == "'" and not in_double and _is_yaml_single_quote_delimiter(raw_line, index):
            in_single = not in_single
            continue
        if char == '"' and not in_single and not _is_escaped(raw_line, index):
            in_double = not in_double
            continue
        if _is_yaml_comment_start(raw_line, index, char, in_single, in_double):
            return raw_line[:index]
    return raw_line


def _is_yaml_single_quote_delimiter(text: str, index: int) -> bool:
    previous_char = text[index - 1] if index > 0 else ""
    next_char = text[index + 1] if index + 1 < len(text) else ""
    return not (previous_char.isalnum() and next_char.isalnum())


def _is_escaped(text: str, index: int) -> bool:
    slash_count = 0
    cursor = index - 1
    while cursor >= 0 and text[cursor] == "\\":
        slash_count += 1
        cursor -= 1
    return slash_count % 2 == 1


def _is_yaml_comment_start(text: str, index: int, char: str, in_single: bool, in_double: bool) -> bool:
    return char == "#" and not in_single and not in_double and (index == 0 or text[index - 1].isspace())


def _consume_minimal_line(state: dict[str, Any], stripped: str, indent: int) -> bool:
    case_indent = state.get("case_indent")
    if stripped.startswith("- ") and (case_indent is None or indent == case_indent):
        return _start_minimal_case(state, stripped[2:], indent)
    if state["current"] is None:
        return False
    return _consume_nested_value(state, stripped, indent) or _consume_case_field(state, stripped, indent)


def _start_minimal_case(state: dict[str, Any], item: str, indent: int) -> bool:
    current: dict[str, Any] = {}
    state["cases"].append(current)
    state["current"] = current
    state["current_list"] = None
    state["current_mapping"] = None
    state["last_scalar_key"] = None
    if state.get("case_indent") is None:
        state["case_indent"] = indent
    _assign_inline_pair(current, item)
    return True


def _consume_case_field(state: dict[str, Any], stripped: str, indent: int) -> bool:
    field_indent = int(state.get("case_indent") or 0) + 2
    if indent != field_indent or ":" not in stripped:
        return False
    current = state["current"]
    key, value = stripped.split(":", 1)
    if value.strip():
        current[key] = _parse_scalar(value.strip())
        state["current_list"] = state["current_mapping"] = None
        state["last_scalar_key"] = key
    elif key in {"eval_modes", "acceptance", "claim_ids", "expect"}:
        state["current_list"] = current[key] = []
        state["current_mapping"] = None
        state["last_scalar_key"] = None
    else:
        state["current_mapping"] = current[key] = {}
        state["current_list"] = None
        state["last_scalar_key"] = None
    return True


def _consume_nested_value(state: dict[str, Any], stripped: str, indent: int) -> bool:
    field_indent = int(state.get("case_indent") or 0) + 2
    nested_indent = int(state.get("case_indent") or 0) + 4
    return (
        _consume_list_value(state, stripped, indent, field_indent, nested_indent)
        or _consume_mapping_value(state, stripped, indent, nested_indent)
        or _consume_scalar_continuation(state, stripped, indent, nested_indent)
    )


def _consume_list_value(state: dict[str, Any], stripped: str, indent: int, field_indent: int, nested_indent: int) -> bool:
    current_list = state["current_list"]
    if current_list is None:
        return False
    if stripped.startswith("- "):
        if indent < field_indent:
            return False
        current_list.append(_parse_list_item(stripped[2:]))
        state["last_scalar_key"] = None
        return True
    latest = current_list[-1] if current_list else None
    if isinstance(latest, dict) and ":" in stripped and indent >= nested_indent:
        key, value = stripped.split(":", 1)
        latest[key] = _parse_scalar(value.strip())
        state["last_scalar_key"] = None
        return True
    if isinstance(latest, str) and indent >= nested_indent:
        current_list[-1] = f"{latest} {stripped}"
        state["last_scalar_key"] = None
        return True
    return _consume_latest_dict_continuation(latest, stripped, indent, nested_indent)


def _consume_latest_dict_continuation(latest: Any, stripped: str, indent: int, nested_indent: int) -> bool:
    if not isinstance(latest, dict) or not latest or indent < nested_indent:
        return False
    key = next(reversed(latest))
    prior = latest.get(key)
    if isinstance(prior, str):
        latest[key] = f"{prior} {stripped}"
        return True
    return False


def _consume_mapping_value(state: dict[str, Any], stripped: str, indent: int, nested_indent: int) -> bool:
    current_mapping = state["current_mapping"]
    if current_mapping is None:
        return False
    if indent < nested_indent:
        return False
    if ":" in stripped:
        key, value = stripped.split(":", 1)
        current_mapping[key] = _parse_scalar(value.strip()) if value.strip() else True
    state["last_scalar_key"] = None
    return True


def _consume_scalar_continuation(state: dict[str, Any], stripped: str, indent: int, nested_indent: int) -> bool:
    if indent < nested_indent or not state.get("last_scalar_key") or not isinstance(state["current"], dict):
        return False
    key = str(state["last_scalar_key"])
    prior = state["current"].get(key)
    if isinstance(prior, str):
        state["current"][key] = f"{prior} {stripped}"
        return True
    return False


def _assign_inline_pair(target: dict[str, Any], item: str) -> None:
    if ":" not in item:
        raise ValueError("minimal_yaml_parse_unsupported")
    key, value = item.split(":", 1)
    target[key] = _parse_scalar(value.strip())


def _parse_list_item(item: str) -> Any:
    if ":" not in item:
        return _parse_scalar(item)
    first_key = item.split(":", 1)[0].strip().strip("{}")
    if first_key not in {"type", "value", "values", "field", "fields", "key", "path", "id", "name", "status"}:
        return _parse_scalar(item)
    result: dict[str, Any] = {}
    for part in item.split(","):
        if ":" not in part:
            return _parse_scalar(item)
        key, value = part.split(":", 1)
        result[key.strip().strip("{}")] = _parse_scalar(value.strip().strip("{}"))
    return result


def _parse_scalar(value: str) -> Any:
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith("[") and value.endswith("]"):
        return [item.strip().strip("'\"") for item in value[1:-1].split(",") if item.strip()]
    return value.strip("'\"")


def _load_evals(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        loaded = _yaml_safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, ValueError) as exc:
        return None, str(exc)
    if not isinstance(loaded, dict):
        return None, "evals_yaml_not_object"
    return loaded, None


def _scenario_id(case: dict[str, Any], index: int) -> str:
    raw = case.get("id")
    return raw if isinstance(raw, str) and raw.strip() else f"case-{index}"


def _list_field(case: dict[str, Any], key: str) -> list[Any]:
    value = case.get(key)
    return value if isinstance(value, list) else []


def _text_field(case: dict[str, Any], key: str) -> str:
    value = case.get(key)
    return value if isinstance(value, str) else ""


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def _acceptance_text(case: dict[str, Any]) -> str:
    parts: list[str] = []
    for item in _list_field(case, "acceptance"):
        if isinstance(item, dict):
            value = item.get("value")
            if value is not None:
                parts.append(str(value))
        else:
            parts.append(str(item))
    return " ".join(parts)


def _acceptance_assertion_checks(case: dict[str, Any], scenario_id: str) -> list[dict[str, Any]]:
    malformed_text_fields: list[str] = []
    regex_structured_fields: list[str] = []
    unsupported_text_assertions: list[str] = []
    for index, item in enumerate(_list_field(case, "acceptance"), start=1):
        if not isinstance(item, dict):
            continue
        assertion_type = str(item.get("type") or "")
        marker = f"{scenario_id}:acceptance[{index}]"
        if assertion_type not in TEXT_OUTPUT_RUNNER_ACCEPTANCE_TYPES:
            unsupported_text_assertions.append(f"{marker}:{assertion_type or 'missing_type'}")
        if _text_field_assertion_malformed(item, assertion_type):
            malformed_text_fields.append(marker)
        regex_structured_fields.extend(_regex_structured_field_refs(item, assertion_type, marker))
    return [
        _check(
            "text_output_runner_acceptance_supported",
            "blocker" if unsupported_text_assertions else "pass",
            "Scenario acceptance types must be executable by the text-output skill eval runner before release.",
            unsupported_text_assertions,
        ),
        _check(
            "typed_text_field_assertions_valid",
            "blocker" if malformed_text_fields else "pass",
            "text_field_* assertions must declare field/fields and expected values when required.",
            malformed_text_fields,
        ),
        _check(
            "structured_fields_use_typed_assertions",
            "blocker" if regex_structured_fields else "pass",
            "Known structured output fields must use text_field_* assertions instead of regex.",
            regex_structured_fields,
        ),
    ]


def _platform_parity_checks(case: dict[str, Any], scenario_id: str) -> list[dict[str, Any]]:
    """Apply the Tessl live-private scenario quality gate to SDK scenario rows."""
    try:
        from ask.skills_sdk.tessl_eval_quality import tessl_eval_quality_findings  # noqa: PLC0415
    except Exception as exc:  # pragma: no cover - import failure is a blocker surface.
        return [
            _check(
                "platform_tessl_quality_available",
                "blocker",
                "Scenario-quality must be able to load the shared Tessl quality gate.",
                [f"{scenario_id}:{type(exc).__name__}:{exc}"],
            )
        ]
    findings = tessl_eval_quality_findings([case])
    return [
        _check(
            f"{PLATFORM_PARITY_GATE_ID_PREFIX}:{finding['code']}",
            "blocker",
            "SDK scenario-quality and Tessl live-private staging must repair scenario warnings before the next phase.",
            [f"{scenario_id}:{finding['code']}:{finding['message']}"],
        )
        for finding in findings
    ]


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


def _case_has_release_mode(case: dict[str, Any]) -> bool:
    return "release" in {str(mode) for mode in _list_field(case, "eval_modes")}


def _case_claim_ids(case: dict[str, Any]) -> set[str]:
    return {str(claim) for claim in _list_field(case, "claim_ids")}


def _release_metadata_checks(case: dict[str, Any], scenario_id: str) -> list[dict[str, Any]]:
    if not _case_has_release_mode(case):
        return []
    required_text_fields = ("why_realistic", "given", "should", "actual_artifact", "expected_artifact", "reproduce")
    missing = [field for field in required_text_fields if not _text_field(case, field).strip()]
    missing.extend(["claim_ids"] if not _case_claim_ids(case) else [])
    return [
        _check(
            "release_case_metadata_present",
            "blocker" if missing else "pass",
            "Release scenarios must carry claim ids, realistic context, expected artifacts, and reproduce evidence.",
            [f"{scenario_id}:{field}" for field in missing],
        )
    ]


def _registry_dependency_checks(case: dict[str, Any], scenario_id: str) -> list[dict[str, Any]]:
    if REGISTRY_DEPENDENCY_CLAIM not in _case_claim_ids(case):
        return []
    text = " ".join(
        [
            _text_field(case, "given"),
            _text_field(case, "should"),
            _text_field(case, "prompt"),
            _acceptance_text(case),
        ]
    )
    required_signals = {
        "quality": ("quality", "review score"),
        "impact": ("impact",),
        "security": ("security", "warning"),
        "version_or_pin": ("version", "pinned", "pinning", "commit-specific", "commit source"),
        "local_validation": ("local validation", "target-repo", "target repo", "representative scenario"),
    }
    missing = [name for name, terms in required_signals.items() if not _contains_any(text, terms)]
    blocks_warning = _contains_any(text, ("block", "blocked", "until inspected", "explicitly accepted"))
    return [
        _check(
            "registry_dependency_intake_complete",
            "blocker" if missing else "pass",
            "Registry dependency scenarios must separate quality, impact, security, version or pinning, and local validation evidence.",
            [f"{scenario_id}:{name}" for name in missing],
        ),
        _check(
            "registry_security_warning_blocks_use",
            "pass" if blocks_warning else "blocker",
            "Registry dependency scenarios must block high or critical security warnings until inspected and accepted.",
            [scenario_id] if not blocks_warning else [],
        ),
    ]


def _release_rubric_checks(case: dict[str, Any], scenario_id: str) -> list[dict[str, Any]]:
    if not _case_has_release_mode(case):
        return []
    acceptance = _list_field(case, "acceptance")
    acceptance_text = _acceptance_text(case)
    category = str(case.get("category") or "")
    needs_failure_guard = category in {"pressure", "negative", "edge"}
    has_failure_guard = _contains_any(acceptance_text, RUBRIC_FAILURE_TERMS)
    has_evidence_anchor = _contains_any(acceptance_text, RUBRIC_EVIDENCE_TERMS)
    checks = [
        _check(
            "release_rubric_binary_items",
            "pass" if len(acceptance) >= 2 else "blocker",
            "Release rubrics must split broad quality into at least two binary acceptance checks.",
            [f"{scenario_id}:acceptance_count:{len(acceptance)}"] if len(acceptance) < 2 else [],
        ),
        _check(
            "release_rubric_evidence_anchored",
            "pass" if has_evidence_anchor else "blocker",
            "Release rubrics must anchor scoring in observable evidence, artifacts, files, commands, scores, or proof lanes.",
            [scenario_id] if not has_evidence_anchor else [],
        ),
    ]
    checks.extend(release_rubric_regex_checks(acceptance, scenario_id))
    if needs_failure_guard:
        checks.append(
            _check(
                "release_rubric_failure_guard",
                "pass" if has_failure_guard else "blocker",
                "Pressure, negative, and edge release rubrics must include an explicit reject, block, avoid, or must-not condition.",
                [scenario_id] if not has_failure_guard else [],
            )
        )
    return checks


def _scenario_checks(case: dict[str, Any], index: int) -> list[dict[str, Any]]:
    scenario_id = _scenario_id(case, index)
    prompt = case.get("prompt")
    acceptance = _list_field(case, "acceptance")
    eval_modes = _list_field(case, "eval_modes")
    deterministic_checks = case.get("deterministic_checks")
    prompt_text = prompt if isinstance(prompt, str) else ""
    checks = [
        _check("scenario_id", "pass" if scenario_id != f"case-{index}" else "blocker", "Scenario must declare a stable id.", [scenario_id]),
        _check("prompt_present", "pass" if prompt_text.strip() else "blocker", "Scenario must carry a prompt or stimulus.", [scenario_id]),
        _check("oracle_present", "pass" if acceptance else "blocker", "Scenario must declare acceptance checks as its oracle.", [scenario_id]),
        _check("reproducibility_present", "pass" if eval_modes else "blocker", "Scenario must declare eval modes for reproducible runs.", [scenario_id]),
        _check(
            "safety_boundary_present",
            "pass" if isinstance(deterministic_checks, dict) else "blocker",
            "Scenario must declare deterministic safety checks before promotion.",
            [scenario_id],
        ),
        _check(
            "raw_secret_absent",
            "blocker" if any(pattern in prompt_text.lower() for pattern in RAW_SECRET_PATTERNS) else "pass",
            "Scenario prompt must not embed raw secrets or token-like values.",
            [scenario_id],
        ),
    ]
    checks.extend(_release_metadata_checks(case, scenario_id))
    checks.extend(_release_rubric_checks(case, scenario_id))
    checks.extend(_registry_dependency_checks(case, scenario_id))
    checks.extend(_acceptance_assertion_checks(case, scenario_id))
    checks.extend(_platform_parity_checks(case, scenario_id))
    return checks


def _scenario_row(case: dict[str, Any], index: int) -> dict[str, Any]:
    checks = _scenario_checks(case, index)
    blockers = [check for check in checks if check["status"] == "blocker"]
    return {
        "id": _scenario_id(case, index),
        "category": str(case.get("category") or "unknown"),
        "realistic": case.get("realistic") is True,
        "promotion_status": "blocked_quality_gate" if blockers else "promotion_ready",
        "checks": checks,
        "blockers": blockers,
    }


def _rows(cases: list[Any]) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(cases):
        if not isinstance(item, dict):
            errors.append(f"case:{index}:not_object")
            continue
        row = _scenario_row(item, index)
        if row["id"] in seen:
            row["blockers"].append(_check("scenario_id_unique", "blocker", "Scenario ids must be unique.", [row["id"]]))
            row["promotion_status"] = "blocked_quality_gate"
        seen.add(row["id"])
        rows.append(row)
    return rows, errors


def _quality_checks(
    repo_root: Path,
    evals_path: Path,
    evals_payload: dict[str, Any] | None,
    case_list: list[Any],
    load_error: str | None,
    row_errors: list[str],
) -> list[dict[str, Any]]:
    checks = [
        _check("evals_yaml_present", "pass" if evals_path.is_file() else "blocker", "Skill must carry references/evals.yaml.", [_repo_relative(repo_root, evals_path)]),
        _check("evals_yaml_parse", "blocker" if load_error else "pass", "references/evals.yaml must parse as YAML object.", [load_error] if load_error else []),
        _check("cases_present", "pass" if case_list else "blocker", "references/evals.yaml must contain one or more cases.", [_repo_relative(repo_root, evals_path)]),
        _check("cases_are_objects", "blocker" if row_errors else "pass", "Every eval case must be an object.", row_errors),
    ]
    checks.extend(_release_suite_checks(case_list))
    checks.extend(build_release_scenario_set_checks(evals_payload, case_list))
    return checks


def _release_suite_checks(case_list: list[Any]) -> list[dict[str, Any]]:
    release_count, pressure_count, negative_or_edge_count = _release_suite_counts(case_list)
    has_release_cases = release_count > 0
    return [
        _release_requirement_check(
            "release_minimum_scenario_count",
            has_release_cases,
            release_count,
            20,
            "Release-mode behavioral scenario suites must include at least 20 scenarios unless they are structure-only.",
            "release_cases",
        ),
        _release_requirement_check(
            "release_pressure_coverage",
            has_release_cases,
            pressure_count,
            4,
            "Release-mode scenario suites must include at least 4 pressure or regression cases.",
            "pressure_or_regression",
        ),
        _release_requirement_check(
            "release_negative_edge_coverage",
            has_release_cases,
            negative_or_edge_count,
            2,
            "Release-mode scenario suites must include at least 2 negative or edge boundary cases.",
            "negative_or_edge",
        ),
    ]


def _release_requirement_check(check_id: str, has_release_cases: bool, observed: int, minimum: int, message: str, evidence_label: str) -> dict[str, Any]:
    blocked = has_release_cases and observed < minimum
    return _check(check_id, "blocker" if blocked else "pass", message, [f"{evidence_label}:{observed}"] if blocked else [])


def _release_suite_counts(case_list: list[Any]) -> tuple[int, int, int]:
    release_cases = [case for case in case_list if isinstance(case, dict) and _case_has_release_mode(case)]
    categories = [str(case.get("category") or "") for case in release_cases]
    pressure_count = sum(1 for category in categories if category in {"pressure", "regression"})
    negative_or_edge_count = sum(1 for category in categories if category in {"negative", "edge"})
    return len(release_cases), pressure_count, negative_or_edge_count


def _receipt(
    repo_root: Path,
    *,
    query: str,
    skill_md: Path,
    evals_path: Path,
    scenario_rows: list[dict[str, Any]],
    receipt_checks: list[dict[str, Any]],
    scenario_set_parity: dict[str, Any] | None = None,
) -> dict[str, Any]:
    scenario_blockers = [blocker for row in scenario_rows for blocker in row["blockers"]]
    blockers = [check for check in receipt_checks if check["status"] == "blocker"] + scenario_blockers
    return {
        "schema_version": SCENARIO_QUALITY_SCHEMA_VERSION,
        "schema_uri": SCENARIO_QUALITY_SCHEMA_URI,
        "status": "blocked" if blockers else "preview",
        "operation": "scenario_quality_preview",
        "query": query,
        "skill_path": _repo_relative(repo_root, skill_md),
        "evals_path": _repo_relative(repo_root, evals_path),
        "scenario_count": len(scenario_rows),
        "promotion_ready_count": sum(1 for row in scenario_rows if row["promotion_status"] == "promotion_ready"),
        "blocked_count": sum(1 for row in scenario_rows if row["promotion_status"] == "blocked_quality_gate"),
        "scenario_set_parity": scenario_set_parity,
        "scenario_rows": scenario_rows,
        "quality_checks": receipt_checks,
        "blockers": blockers,
        "mutation_performed": False,
        "promotion_performed": False,
        "acceptance_trace": SCENARIO_QUALITY_ACCEPTANCE_TRACE,
        "agent_summary": f"scenario quality preview checked {len(scenario_rows)} scenario(s) for {query}.",
    }


def _selected_canonical_ids(
    evals_payload: dict[str, Any] | None,
    scenario_set: str | None,
    all_canonical_ids: set[str],
) -> tuple[set[str], list[dict[str, Any]]]:
    selected_release_ids = release_scenario_set_case_ids(evals_payload, scenario_set)
    if scenario_set and not selected_release_ids:
        return set(), [
            _check(
                "release_scenario_set_selector_valid",
                "blocker",
                "Scenario-set parity must use a declared release scenario set when --scenario-set is provided.",
                [f"scenario_set:{scenario_set}:not_found_or_empty"],
            )
        ]
    return selected_release_ids or all_canonical_ids, []


def _scenario_quality_inputs(
    skill_md: Path,
) -> tuple[Path, dict[str, Any] | None, str | None, list[dict[str, Any]]]:
    evals_path = skill_md.parent / "references" / "evals.yaml"
    evals_payload, load_error = _load_evals(evals_path) if evals_path.is_file() else (None, "missing_evals_yaml")
    cases = evals_payload.get("cases") if isinstance(evals_payload, dict) else None
    base_case_list = cases if isinstance(cases, list) else []
    known_ids = {str(case.get("id")) for case in base_case_list if isinstance(case, dict)}
    return evals_path, evals_payload, load_error, [
        *base_case_list,
        *[
            case
            for case in parse_generated_eval_fixtures(skill_md.parent)
            if str(case.get("id")) not in known_ids
        ],
    ]


def _scenario_quality_parity(
    repo_root: Path,
    skill_md: Path,
    evals_payload: dict[str, Any] | None,
    scenario_set: str | None,
    scenario_rows: list[dict[str, Any]],
    tessl_staged_json: Path | None,
    tessl_score_json: Path | None,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    canonical_ids, selector_checks = _selected_canonical_ids(
        evals_payload,
        scenario_set,
        {row["id"] for row in scenario_rows},
    )
    scenario_set_parity, parity_checks = build_scenario_set_parity_checks(
        repo_root, skill_md.parent, canonical_ids, tessl_staged_json, tessl_score_json
    )
    return scenario_set_parity, [*selector_checks, *parity_checks]


def build_scenario_quality_receipt(
    repo_root: Path,
    *,
    source_path: Path,
    query: str,
    tessl_staged_json: Path | None = None,
    tessl_score_json: Path | None = None,
    scenario_set: str | None = None,
) -> dict[str, Any]:
    skill_md = source_path if source_path.name == "SKILL.md" else source_path / "SKILL.md"
    evals_path, evals_payload, load_error, case_list = _scenario_quality_inputs(skill_md)
    scenario_rows, row_errors = _rows(case_list)
    receipt_checks = _quality_checks(repo_root, evals_path, evals_payload, case_list, load_error, row_errors)
    scenario_set_parity, parity_checks = _scenario_quality_parity(
        repo_root, skill_md, evals_payload, scenario_set, scenario_rows, tessl_staged_json, tessl_score_json
    )
    receipt_checks.extend(parity_checks)
    receipt = _receipt(
        repo_root,
        query=query,
        skill_md=skill_md,
        evals_path=evals_path,
        scenario_rows=scenario_rows,
        receipt_checks=receipt_checks,
        scenario_set_parity=scenario_set_parity,
    )
    if receipt["blockers"]:
        raise ScenarioQualityError(receipt)
    return receipt
