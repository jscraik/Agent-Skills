from __future__ import annotations

from pathlib import Path
from typing import Any


SCENARIO_QUALITY_SCHEMA_VERSION = "skills-sdk.scenario-quality-receipt.v0"
SCENARIO_QUALITY_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/scenario-quality-receipt.v0.schema.json"
)
SCENARIO_QUALITY_ACCEPTANCE_TRACE = ["PU-030", "FR-003", "FR-008", "SA-003", "VP-030"]
RAW_SECRET_PATTERNS = ("api_key=", "password=", "secret=", "token=")


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
        return _load_minimal_evals_yaml(text)
    return yaml.safe_load(text)


def _load_minimal_evals_yaml(text: str) -> dict[str, Any]:
    state: dict[str, Any] = {"cases": [], "current": None, "current_list": None, "current_mapping": None}
    for raw_line in text.splitlines():
        stripped, indent = _minimal_line(raw_line)
        if not stripped or stripped == "cases:":
            continue
        if _consume_minimal_line(state, stripped, indent) or stripped.startswith(("schema_version:", "skill_name:")):
            continue
        else:
            raise ValueError("minimal_yaml_parse_unsupported")
    return {"cases": state["cases"]}


def _minimal_line(raw_line: str) -> tuple[str, int]:
    line = raw_line.split("#", 1)[0].rstrip()
    return line.strip(), len(line) - len(line.lstrip(" "))


def _consume_minimal_line(state: dict[str, Any], stripped: str, indent: int) -> bool:
    if indent == 2 and stripped.startswith("- "):
        return _start_minimal_case(state, stripped[2:])
    if state["current"] is None:
        return False
    return _consume_case_field(state, stripped, indent) or _consume_nested_value(state, stripped, indent)


def _start_minimal_case(state: dict[str, Any], item: str) -> bool:
    current: dict[str, Any] = {}
    state["cases"].append(current)
    state["current"] = current
    state["current_list"] = None
    state["current_mapping"] = None
    _assign_inline_pair(current, item)
    return True


def _consume_case_field(state: dict[str, Any], stripped: str, indent: int) -> bool:
    if indent != 4 or ":" not in stripped:
        return False
    current = state["current"]
    key, value = stripped.split(":", 1)
    if value.strip():
        current[key] = _parse_scalar(value.strip())
        state["current_list"] = state["current_mapping"] = None
    elif key in {"eval_modes", "acceptance"}:
        state["current_list"] = current[key] = []
        state["current_mapping"] = None
    else:
        state["current_mapping"] = current[key] = {}
        state["current_list"] = None
    return True


def _consume_nested_value(state: dict[str, Any], stripped: str, indent: int) -> bool:
    if indent < 6:
        return False
    if state["current_list"] is not None and stripped.startswith("- "):
        state["current_list"].append(_parse_list_item(stripped[2:]))
        return True
    if state["current_list"] is not None and ":" in stripped:
        latest = state["current_list"][-1] if state["current_list"] else None
        if isinstance(latest, dict):
            key, value = stripped.split(":", 1)
            latest[key] = _parse_scalar(value.strip())
            return True
    if state["current_mapping"] is not None:
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            state["current_mapping"][key] = _parse_scalar(value.strip()) if value.strip() else True
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
    result: dict[str, Any] = {}
    for part in item.split(","):
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


def _scenario_checks(case: dict[str, Any], index: int) -> list[dict[str, Any]]:
    scenario_id = _scenario_id(case, index)
    prompt = case.get("prompt")
    acceptance = _list_field(case, "acceptance")
    eval_modes = _list_field(case, "eval_modes")
    deterministic_checks = case.get("deterministic_checks")
    prompt_text = prompt if isinstance(prompt, str) else ""
    return [
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


def _quality_checks(repo_root: Path, evals_path: Path, case_list: list[Any], load_error: str | None, row_errors: list[str]) -> list[dict[str, Any]]:
    return [
        _check("evals_yaml_present", "pass" if evals_path.is_file() else "blocker", "Skill must carry references/evals.yaml.", [_repo_relative(repo_root, evals_path)]),
        _check("evals_yaml_parse", "blocker" if load_error else "pass", "references/evals.yaml must parse as YAML object.", [load_error] if load_error else []),
        _check("cases_present", "pass" if case_list else "blocker", "references/evals.yaml must contain one or more cases.", [_repo_relative(repo_root, evals_path)]),
        _check("cases_are_objects", "blocker" if row_errors else "pass", "Every eval case must be an object.", row_errors),
    ]


def _receipt(
    repo_root: Path,
    *,
    query: str,
    skill_md: Path,
    evals_path: Path,
    scenario_rows: list[dict[str, Any]],
    receipt_checks: list[dict[str, Any]],
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
        "scenario_rows": scenario_rows,
        "quality_checks": receipt_checks,
        "blockers": blockers,
        "mutation_performed": False,
        "promotion_performed": False,
        "acceptance_trace": SCENARIO_QUALITY_ACCEPTANCE_TRACE,
        "agent_summary": f"scenario quality preview checked {len(scenario_rows)} scenario(s) for {query}.",
    }


def build_scenario_quality_receipt(repo_root: Path, *, source_path: Path, query: str) -> dict[str, Any]:
    skill_md = source_path if source_path.name == "SKILL.md" else source_path / "SKILL.md"
    evals_path = skill_md.parent / "references" / "evals.yaml"
    evals_payload, load_error = _load_evals(evals_path) if evals_path.is_file() else (None, "missing_evals_yaml")
    cases = evals_payload.get("cases") if isinstance(evals_payload, dict) else None
    case_list = cases if isinstance(cases, list) else []
    scenario_rows, row_errors = _rows(case_list)
    receipt_checks = _quality_checks(repo_root, evals_path, case_list, load_error, row_errors)
    receipt = _receipt(repo_root, query=query, skill_md=skill_md, evals_path=evals_path, scenario_rows=scenario_rows, receipt_checks=receipt_checks)
    if receipt["blockers"]:
        raise ScenarioQualityError(receipt)
    return receipt
