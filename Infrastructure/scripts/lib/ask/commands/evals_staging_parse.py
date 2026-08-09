from __future__ import annotations

from .evals_policy import *  # noqa: F403

def _should_skip_tessl_staging_path(source_root: Path, source_path: Path) -> bool:
    try:
        relative_parts = source_path.relative_to(source_root).parts
    except ValueError:
        relative_parts = source_path.parts
    return any(part in TESSL_STAGING_IGNORED_NAMES or part in TESSL_STAGING_IGNORED_DIRS for part in relative_parts)


def _copy_if_present(source_root: Path, relative_path: str, target_root: Path) -> list[str]:
    source = source_root / relative_path
    if not source.exists():
        return []
    _reject_tessl_staging_symlink(source_root, source)
    if _should_skip_tessl_staging_path(source_root, source):
        return []
    target = target_root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return [relative_path]


def _copy_tree_files_if_present(source_root: Path, relative_path: str, target_root: Path) -> list[str]:
    source = source_root / relative_path
    if source.is_symlink():
        _reject_tessl_staging_symlink(source_root, source)
    if not source.is_dir():
        return []

    copied: list[str] = []
    for source_file in sorted(source.rglob("*")):
        if source_file.is_symlink():
            _reject_tessl_staging_symlink(source_root, source_file)
        if not source_file.is_file():
            continue
        if _should_skip_tessl_staging_path(source_root, source_file):
            continue
        child_relative = source_file.relative_to(source_root).as_posix()
        target = target_root / child_relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target)
        copied.append(child_relative)
    return copied


def _copy_tree_files_to_relative_root(
    source_root: Path,
    relative_path: str,
    target_root: Path,
    target_relative_root: str,
) -> list[str]:
    source = source_root / relative_path
    if source.is_symlink():
        _reject_tessl_staging_symlink(source_root, source)
    if not source.is_dir():
        return []

    copied: list[str] = []
    for source_file in sorted(source.rglob("*")):
        if source_file.is_symlink():
            _reject_tessl_staging_symlink(source_root, source_file)
        if not source_file.is_file():
            continue
        if _should_skip_tessl_staging_path(source_root, source_file):
            continue
        child_relative = source_file.relative_to(source_root).as_posix()
        target_relative = f"{target_relative_root.rstrip('/')}/{child_relative}"
        target = target_root / target_relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target)
        copied.append(target_relative)
    return copied


def _reject_tessl_staging_symlink(source_root: Path, source_path: Path) -> None:
    if not source_path.is_symlink():
        return
    try:
        label = source_path.relative_to(source_root).as_posix()
    except ValueError:
        label = source_path.as_posix()
    raise ValueError(f"Tessl staging refuses symlinked support path: {label}")


def _yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _yaml_compat_value(value: str) -> object:
    scalar = _yaml_scalar(value)
    lowered = scalar.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "none", "~"}:
        return None
    return scalar


def _consume_yaml_block(lines: list[str], index: int, parent_indent: int, style: str) -> tuple[str, int]:
    raw_block_lines: list[str] = []
    while index < len(lines):
        raw_line = lines[index]
        if not raw_line.strip():
            raw_block_lines.append("")
            index += 1
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent <= parent_indent:
            break
        raw_block_lines.append(raw_line)
        index += 1

    non_empty_indents = [
        len(line) - len(line.lstrip(" "))
        for line in raw_block_lines
        if line.strip()
    ]
    block_indent = min(non_empty_indents) if non_empty_indents else parent_indent + 1
    block_lines = [
        line[block_indent:] if line.strip() else ""
        for line in raw_block_lines
    ]

    if style.startswith(">"):
        folded: list[str] = []
        paragraph: list[str] = []
        for line in block_lines:
            if line.strip():
                paragraph.append(line.strip())
                continue
            if paragraph:
                folded.append(" ".join(paragraph))
                paragraph = []
        if paragraph:
            folded.append(" ".join(paragraph))
        return "\n".join(folded), index
    return "\n".join(block_lines), index


def _consume_yaml_plain_scalar(lines: list[str], index: int, parent_indent: int, raw_value: str) -> tuple[str, int]:
    parts = [_yaml_scalar(raw_value)]
    while index < len(lines):
        raw_line = lines[index]
        if not raw_line.strip():
            break
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()
        if indent <= parent_indent or stripped.startswith("- "):
            break
        if re.match(r"^[A-Za-z0-9_-]+\s*:", stripped):
            break
        parts.append(stripped)
        index += 1
    return " ".join(part for part in parts if part), index


def _consume_yaml_sequence_dicts(lines: list[str], index: int, parent_indent: int) -> tuple[list[dict[str, str]], int]:
    items: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    while index < len(lines):
        raw_line = lines[index]
        if not raw_line.strip():
            index += 1
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent <= parent_indent:
            break
        stripped = raw_line.strip()
        if current is not None and not stripped.startswith("- ") and indent <= parent_indent + 1:
            break
        if stripped.startswith("- "):
            if current:
                items.append(current)
            current = {}
            stripped = stripped[2:].strip()
            if not stripped:
                index += 1
                continue
        if current is not None and ":" in stripped:
            key, raw_value = stripped.split(":", 1)
            key = key.strip()
            raw_value = raw_value.strip()
            if raw_value.startswith((">", "|")):
                current[key], index = _consume_yaml_block(lines, index + 1, indent, raw_value)
                continue
            current[key], index = _consume_yaml_plain_scalar(lines, index + 1, indent, raw_value)
            continue
        index += 1

    if current:
        items.append(current)
    return items, index


def _consume_yaml_mapping(lines: list[str], index: int, parent_indent: int) -> tuple[dict[str, object], int]:
    item: dict[str, object] = {}
    while index < len(lines):
        raw_line = lines[index]
        if not raw_line.strip():
            index += 1
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent <= parent_indent:
            break
        stripped = raw_line.strip()
        if stripped.startswith("- ") or ":" not in stripped:
            index += 1
            continue
        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if raw_value.startswith((">", "|")):
            item[key], index = _consume_yaml_block(lines, index + 1, indent, raw_value)
            continue
        if raw_value:
            value, index = _consume_yaml_plain_scalar(lines, index + 1, indent, raw_value)
            item[key] = _yaml_compat_value(value)
            continue
        item[key] = {}
        index += 1
    return item, index


def _parse_inline_acceptance_sequence(raw_value: str) -> list[dict[str, str]]:
    text = raw_value.strip()
    if not (text.startswith("[") and text.endswith("]")):
        return []
    items: list[dict[str, str]] = []
    raw_items: list[str] = []
    current: list[str] = []
    depth = 0
    quote: str | None = None
    escaped = False
    for char in text[1:-1]:
        if quote:
            current.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {'"', "'"}:
            if depth:
                current.append(char)
            quote = char
            continue
        if char == "{":
            if depth:
                current.append(char)
            depth += 1
            continue
        if char == "}":
            if depth == 0:
                continue
            depth -= 1
            if depth:
                current.append(char)
            else:
                raw_items.append("".join(current))
                current = []
            continue
        if depth:
            current.append(char)

    for raw_item in raw_items:
        item: dict[str, str] = {}
        for match in re.finditer(
            r"(type|value|expected_skill)\s*:\s*(.*?)(?=,\s*(?:type|value|expected_skill)\s*:|$)",
            raw_item,
        ):
            item[match.group(1)] = match.group(2).strip().strip("\"'")
        if item:
            items.append(item)
    return items


def _parse_tessl_eval_cases_compat(text: str) -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    in_cases = False
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        raw_line = lines[index]
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            index += 1
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if stripped == "cases:":
            in_cases = True
            index += 1
            continue
        if not in_cases:
            index += 1
            continue
        if stripped.startswith("- "):
            item_text = stripped[2:].strip()
            if not item_text.startswith("id:") and current is not None:
                index += 1
                continue
            if current and current.get("id") and current.get("prompt"):
                cases.append(current)
            current = {}
            stripped = item_text
        if current is None or ":" not in stripped:
            index += 1
            continue
        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if key == "acceptance":
            if raw_value:
                acceptance = _parse_inline_acceptance_sequence(raw_value)
                index += 1
            else:
                sequence_parent_indent = indent
                for lookahead in lines[index + 1:]:
                    if not lookahead.strip():
                        continue
                    lookahead_indent = len(lookahead) - len(lookahead.lstrip(" "))
                    if lookahead.strip().startswith("- "):
                        sequence_parent_indent = lookahead_indent - 1
                    break
                acceptance, index = _consume_yaml_sequence_dicts(lines, index + 1, sequence_parent_indent)
            current[key] = acceptance  # type: ignore[assignment]
            continue
        if key == "tessl":
            if raw_value:
                index += 1
                continue
            tessl, index = _consume_yaml_mapping(lines, index + 1, indent)
            current[key] = tessl
            continue
        if key not in {
            "id",
            "prompt",
            "unit",
            "given",
            "should",
            "actual_artifact",
            "expected_artifact",
            "reproduce",
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
            "synthetic",
            "judge_temperature",
            "judge_runs",
            "sample_count",
            "pass_rate_calibration_artifact",
            "pass_rate_threshold",
            "tessl_live_private",
        }:
            index += 1
            continue
        if raw_value.startswith((">", "|")):
            current[key], index = _consume_yaml_block(lines, index + 1, indent, raw_value)
            continue
        current[key], index = _consume_yaml_plain_scalar(lines, index + 1, indent, raw_value)

    if current and current.get("id") and current.get("prompt"):
        cases.append(current)
    return cases


def _parse_tessl_eval_cases(evals_path: Path) -> list[dict[str, object]]:
    if not evals_path.exists():
        return []

    text = evals_path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
    except ImportError:
        return _parse_tessl_eval_cases_compat(text)

    try:
        loaded = yaml.safe_load(text) or {}
    except yaml.YAMLError as e:
        compat_cases = _parse_tessl_eval_cases_compat(text)
        if compat_cases and (
            "while parsing a block mapping" in str(e)
            or "expected <block end>" in str(e)
        ):
            return compat_cases
        raise ValueError(f"Failed to parse Tessl eval cases from {evals_path}: {e}") from e
    raw_cases = loaded.get("cases", []) if isinstance(loaded, dict) else []
    cases: list[dict[str, object]] = []
    for raw_case in raw_cases:
        if not isinstance(raw_case, dict):
            continue
        case_id = raw_case.get("id")
        prompt = raw_case.get("prompt")
        if case_id is None or prompt is None:
            continue
        case = {"id": str(case_id), "prompt": str(prompt)}
        for field in (
            "unit",
            "given",
            "should",
            "actual_artifact",
            "expected_artifact",
            "reproduce",
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
            "synthetic",
            "judge_temperature",
            "judge_runs",
            "sample_count",
            "pass_rate_threshold",
            "pass_rate_calibration_artifact",
            "tessl_live_private",
        ):
            if raw_case.get(field) is not None:
                case[field] = raw_case[field]  # type: ignore[assignment]
        acceptance = raw_case.get("acceptance")
        if isinstance(acceptance, list):
            case["acceptance"] = acceptance  # type: ignore[assignment]
        tessl = raw_case.get("tessl")
        if isinstance(tessl, dict):
            case["tessl"] = tessl  # type: ignore[assignment]
        cases.append(case)
    return cases


FIXTURE_FIELD_RE = re.compile(r"^([A-Za-z][A-Za-z ]+):\s*(.*)$")


def _parse_generated_eval_fixture(fixture_path: Path, source_root: Path) -> dict[str, object] | None:
    """Convert a reviewed KnowledgeOS/Tessl markdown fixture into a Tessl case."""
    text = fixture_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    title = ""
    fields: dict[str, str] = {}
    current_key: str | None = None
    for raw_line in lines:
        line = raw_line.rstrip()
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            continue
        match = FIXTURE_FIELD_RE.match(line)
        if match:
            current_key = match.group(1).strip().lower().replace(" ", "_")
            fields[current_key] = match.group(2).strip()
            continue
        if current_key and line.strip() and not line.startswith(("-", "#")):
            fields[current_key] = f"{fields[current_key]} {line.strip()}".strip()

    given = fields.get("given", "")
    should = fields.get("should", "")
    good = fields.get("expected_agent_move") or fields.get("good_answer_patterns") or should
    bad = fields.get("expected_failure") or fields.get("bad_answer_patterns") or fields.get("failure_mode", "")
    if not given or not should or not good:
        return None

    relative_path = fixture_path.relative_to(source_root).as_posix()
    raw_id = title.split(":", 1)[0].strip() if title else fixture_path.stem
    case_id = f"generated-{_safe_slug(raw_id)}"
    display_name = title.split(":", 1)[1].strip() if ":" in title else raw_id
    behavior = fields.get("behavior_under_test") or fields.get("knowledge_claim") or should
    prompt = "\n".join([
        "Evaluate whether the installed skill package covers the reviewed operator boundary case described by the hidden checklist.",
        "Score the package instructions and references, not a freshly generated chat response. Look for the safest next action, the boundary that must be preserved, and the proof or check that would make the next step reliable.",
    ])
    acceptance: list[dict[str, str]] = [
        {
            "type": "expected_signal",
            "value": f"The skill package instructs agents to {good}",
        },
        {
            "type": "expected_signal",
            "value": "The skill package names the proof or validation boundary and cites observable package evidence.",
        },
        {
            "type": "expected_signal",
            "value": "The skill package avoids the expected failure mode and blocks readiness overclaims when proof is missing.",
        },
    ]
    if bad:
        acceptance.append({
            "type": "must_not",
            "value": f"The skill package encourages or permits this failure mode: {bad}",
        })
    return {
        "id": case_id,
        "prompt": prompt,
        "unit": display_name or raw_id,
        "given": given,
        "should": GENERIC_GENERATED_SHOULD,
        "hidden_expected_behavior": should,
        "hidden_review_focus": behavior,
        "expected_artifact": relative_path,
        "reproduce": relative_path,
        "acceptance": acceptance,
        "tessl": {
            "generated": True,
            "reviewed_fixture": relative_path,
            "source": "references/evals/*.md",
        },
        "source": relative_path,
        "source_kind": "generated_fixture",
    }


def _parse_generated_eval_fixtures(source_root: Path) -> list[dict[str, object]]:
    return parse_generated_eval_fixtures(source_root)


def _tessl_structure_only_scenario_policy(source_root: Path) -> bool:
    contract_path = source_root / "references" / "contract.yaml"
    if not contract_path.exists():
        return False
    text = contract_path.read_text(encoding="utf-8")

    def compat_policy_enabled() -> bool:
        in_policy = False
        policy_indent = 0
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            indent = len(line) - len(line.lstrip(" "))
            if re.match(r"^tessl_scenario_policy\s*:\s*$", stripped):
                in_policy = True
                policy_indent = indent
                continue
            if in_policy and indent <= policy_indent:
                in_policy = False
            if in_policy and re.match(r"^(structure_only|structure_check_only)\s*:\s*true\s*$", stripped):
                return True
        return False

    try:
        import yaml  # type: ignore
    except ImportError:
        return compat_policy_enabled()
    try:
        loaded = yaml.safe_load(text) or {}
    except yaml.YAMLError:
        return compat_policy_enabled()
    policy = loaded.get("tessl_scenario_policy") if isinstance(loaded, dict) else None
    return isinstance(policy, dict) and (
        policy.get("structure_only") is True
        or policy.get("structure_check_only") is True
    )


def _merge_tessl_cases_with_generated_fixtures(
    source_root: Path,
    base_cases: list[dict[str, object]],
    *,
    require_generated: bool,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    generated_cases = _parse_generated_eval_fixtures(source_root)
    generated_yaml_cases = [
        case
        for case in base_cases
        if isinstance(case.get("tessl"), dict) and case["tessl"].get("generated") is True
    ]
    by_id: dict[str, dict[str, object]] = {str(case.get("id")): case for case in base_cases}
    duplicate_ids: list[str] = []
    for case in generated_cases:
        case_id = str(case.get("id"))
        if case_id in by_id:
            duplicate_ids.append(case_id)
            continue
        by_id[case_id] = case
    merged = list(by_id.values())
    manifest = {
        "schema_version": "ask-tessl-scenario-sources.v1",
        "skill_owned_cases": len(base_cases),
        "generated_yaml_cases": len(generated_yaml_cases),
        "generated_fixture_cases": len(generated_cases),
        "duplicate_generated_case_ids": duplicate_ids,
        "structure_only_exception": _tessl_structure_only_scenario_policy(source_root),
        "sources": [
            {"path": "references/evals.yaml", "case_count": len(base_cases), "kind": "skill_owned"},
            {"path": "references/evals/*.md", "case_count": len(generated_cases), "kind": "generated_reviewed"},
        ],
    }
    if (
        require_generated
        and not manifest["structure_only_exception"]
        and not generated_cases
        and not generated_yaml_cases
    ):
        raise ValueError(
            "Tessl live-private evals require reviewed generated scenarios before scoring. "
            "Run ./bin/ask evals prepare-tessl-scenarios <skill> --tessl-workspace <workspace> --json --robot, "
            "generate bespoke scenarios with the Tessl scenario skill, review/import them into references/evals/*.md "
            "or references/evals.yaml, then rerun the live Tessl lane. Structure-only packages may set "
            "tessl_scenario_policy.structure_only: true in references/contract.yaml."
        )
    return merged, manifest


def _select_default_tessl_live_cases(
    base_cases: list[dict[str, object]],
    merged_cases: list[dict[str, object]],
    scenario_manifest: dict[str, object],
    release_case_ids: set[str] | None = None,
) -> list[dict[str, object]]:
    if scenario_manifest.get("structure_only_exception"):
        scenario_manifest["default_live_selection"] = {
            "policy": "structure_only_all_reviewed_scenarios",
            "staged_case_count": len(merged_cases),
            "excluded_generated_fixture_case_ids": [],
            "excluded_over_cap_case_ids": [],
        }
        return merged_cases

    base_by_id = {str(case.get("id")): case for case in base_cases}
    generated_fixture_ids = [
        str(case.get("id"))
        for case in merged_cases
        if str(case.get("id")) not in base_by_id
    ]
    selected = (
        [case for case in base_cases if str(case.get("id")) in release_case_ids]
        if release_case_ids
        else list(base_cases)
    )
    over_cap_cases = selected[TESSL_LIVE_PRIVATE_MAX_SCENARIOS:]
    selected = selected[:TESSL_LIVE_PRIVATE_MAX_SCENARIOS]
    scenario_manifest["default_live_selection"] = {
        "policy": (
            "declared_release_set_capped_before_live_budget"
            if release_case_ids
            else "yaml_confirmation_set_capped_before_live_budget"
        ),
        "staged_case_count": len(selected),
        "max_scenarios_default": TESSL_LIVE_PRIVATE_MAX_SCENARIOS,
        "excluded_generated_fixture_case_ids": generated_fixture_ids,
        "excluded_over_cap_case_ids": [str(case.get("id")) for case in over_cap_cases],
    }
    return selected


BEHAVIORAL_TESSL_ACCEPTANCE_TYPES = {
    "expected_signal",
    "skill_selected",
    "artifact_exists",
    "artifact_contains",
    "command_success",
    "forbidden_signal",
    "must_not",
    "must_not_claim",
    "must_not_do",
    "not_contains",
    "output_schema",
}
KEYWORD_ONLY_TESSL_ACCEPTANCE_TYPES = {"regex", "not_regex", "contains", "not_contains"}
PROVENANCE_FIXTURE_PATH_RE = re.compile(r"(?i)\breferences/evals/[^\s]+\.md\b")
PROVENANCE_ONLY_VERBS_RE = re.compile(r"(?i)\b(names?|cites?|references?|points?\s+to|lists?)\b")
GENERIC_EXPECTED_SIGNAL_RE = re.compile(
    r"(?is)^\s*demonstrates\s+the\s+skill-specific\s+behavior\s+in\s+this\s+case\s+should\s+contract\s*:"
)
GENERIC_GENERATED_SHOULD = (
    "Expose package instructions or references that encode the reviewed behavior "
    "under test, preserve safety boundaries, and name the next verifiable action."
)
SHALLOW_EXPECTED_SIGNAL_VALUES = {
    "mission-grounded next step",
    "direct non-workspace handling",
    "skill-specific next step",
    "safe next step",
    "validation evidence",
}
GUARDRAIL_CASE_RE = re.compile(r"(?i)\b(?:guardrail|hallucinat(?:e|ion|ions|ed|ing))\b")
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
JUDGE_CASE_RE = re.compile(r"(?i)\b(?:judge|grader|guardrail|hallucinat(?:e|ion|ions|ed|ing)|faithfulness)\b")
ROLE_TERMS = ("assistant", "agent", "model", "skill")
UNSTAGED_TESSL_REPO_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_./-])"
    r"(?:Infrastructure|Skills|Plugins|Docs|docs|skills-system|runtime|\.agents|\.codex|\.harness|\.skillsets)"
    r"/[^\s,;:)\]}\"']+"
)

__all__ = [name for name in globals() if not name.startswith("__")]
