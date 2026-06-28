from __future__ import annotations

from typing import Any


def build_release_scenario_set_checks(evals_payload: dict[str, Any] | None, case_list: list[Any]) -> list[dict[str, Any]]:
    if not isinstance(evals_payload, dict):
        return []
    release_sets = evals_payload.get("release_scenario_sets")
    if release_sets is None:
        return []
    if not isinstance(release_sets, list) or not release_sets:
        return [_check("release_scenario_sets_valid", "blocker", "release_scenario_sets must be a non-empty list when provided.", ["release_scenario_sets"])]
    checks = [_release_scenario_set_default_check(release_sets), _release_scenario_set_ids_unique_check(release_sets)]
    case_by_id = _case_by_id(case_list)
    for index, item in enumerate(release_sets, start=1):
        checks.extend(_release_scenario_set_entry_checks(index, item, case_by_id))
    return checks


def _check(check_id: str, status: str, message: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {"id": check_id, "status": status, "severity": "blocker", "message": message, "evidence": evidence or []}


def _case_by_id(case_list: list[Any]) -> dict[str, dict[str, Any]]:
    return {
        _scenario_id(case, index): case
        for index, case in enumerate(case_list)
        if isinstance(case, dict)
    }


def _scenario_id(case: dict[str, Any], index: int) -> str:
    value = case.get("id")
    return str(value) if isinstance(value, str) and value.strip() else f"case-{index}"


def _case_has_release_mode(case: dict[str, Any]) -> bool:
    return "release" in {str(mode) for mode in _list_field(case, "eval_modes")}


def _list_field(case: dict[str, Any], field: str) -> list[Any]:
    value = case.get(field)
    return value if isinstance(value, list) else []


def _release_scenario_set_default_check(release_sets: list[Any]) -> dict[str, Any]:
    default_count = sum(1 for item in release_sets if isinstance(item, dict) and item.get("default") is True)
    return _check(
        "release_scenario_set_default_unique",
        "pass" if default_count == 1 else "blocker",
        "Exactly one release scenario set should be marked default.",
        [f"default_count:{default_count}"] if default_count != 1 else [],
    )


def _release_scenario_set_ids_unique_check(release_sets: list[Any]) -> dict[str, Any]:
    ids = [
        str(item.get("id")).strip()
        for item in release_sets
        if isinstance(item, dict) and isinstance(item.get("id"), str) and str(item.get("id")).strip()
    ]
    duplicates = sorted({set_id for set_id in ids if ids.count(set_id) > 1})
    return _check(
        "release_scenario_set_ids_unique",
        "blocker" if duplicates else "pass",
        "Release scenario set ids must be unique.",
        duplicates,
    )


def _release_scenario_set_entry_checks(index: int, item: Any, case_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(item, dict):
        return [_release_scenario_set_entry_object_check(index)]
    set_id = str(item.get("id") or "").strip()
    checks = _release_scenario_set_identity_checks(index, set_id)
    groups = item.get("groups")
    if not isinstance(groups, dict):
        checks.append(_release_scenario_set_groups_check(index, set_id))
        return checks
    checks.extend(_release_scenario_set_group_checks(item, set_id, groups, case_by_id))
    return checks


def _release_scenario_set_entry_object_check(index: int) -> dict[str, Any]:
    return _check("release_scenario_set_entry_object", "blocker", "Every release scenario set must be an object.", [f"entry:{index}"])


def _release_scenario_set_identity_checks(index: int, set_id: str) -> list[dict[str, Any]]:
    if set_id:
        return []
    return [_check("release_scenario_set_id_present", "blocker", "Release scenario sets must have stable ids.", [f"entry:{index}"])]


def _release_scenario_set_groups_check(index: int, set_id: str) -> dict[str, Any]:
    return _check(
        "release_scenario_set_groups_present",
        "blocker",
        "Release scenario sets must declare grouped case ids.",
        [set_id or f"entry:{index}"],
    )


def _release_scenario_set_group_checks(
    item: dict[str, Any],
    set_id: str,
    groups: dict[str, Any],
    case_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    foundation = _string_list(groups.get("foundation_smoke"))
    behavioral = _string_list(groups.get("behavioral_release"))
    case_ids = [*foundation, *behavioral]
    minimum = item.get("minimum_scenarios")
    minimum_value = minimum if isinstance(minimum, int) and not isinstance(minimum, bool) else 20
    return [
        _release_scenario_set_minimum_check(set_id, case_ids, minimum_value),
        _release_scenario_set_split_check(set_id, foundation, behavioral),
        _release_scenario_set_missing_ids_check(set_id, case_ids, case_by_id),
        _release_scenario_set_release_mode_check(set_id, case_ids, case_by_id),
        _release_scenario_set_unique_ids_check(set_id, case_ids),
    ]


def _release_scenario_set_minimum_check(set_id: str, case_ids: list[str], minimum_value: int) -> dict[str, Any]:
    blocked = len(case_ids) < minimum_value or minimum_value < 20
    return _check(
        "release_scenario_set_minimum_count",
        "blocker" if blocked else "pass",
        "Default release scenario sets must contain at least the declared minimum and never fewer than 20 cases.",
        [f"{set_id}:count:{len(case_ids)}:minimum:{minimum_value}"] if blocked else [],
    )


def _release_scenario_set_split_check(set_id: str, foundation: list[str], behavioral: list[str]) -> dict[str, Any]:
    blocked = len(foundation) != 5 or len(behavioral) != 15
    return _check(
        "release_scenario_set_split_5_15",
        "blocker" if blocked else "pass",
        "Technical-writer release set uses the approved 5 foundation smoke plus 15 behavioral release split.",
        [f"{set_id}:foundation:{len(foundation)}:behavioral:{len(behavioral)}"] if blocked else [],
    )


def _release_scenario_set_missing_ids_check(
    set_id: str,
    case_ids: list[str],
    case_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    missing = [case_id for case_id in case_ids if case_id not in case_by_id]
    return _check(
        "release_scenario_set_ids_exist",
        "blocker" if missing else "pass",
        "Every release scenario set case id must exist in references/evals.yaml.",
        [f"{set_id}:missing:{case_id}" for case_id in missing],
    )


def _release_scenario_set_release_mode_check(
    set_id: str,
    case_ids: list[str],
    case_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    non_release = [
        case_id
        for case_id in case_ids
        if case_id in case_by_id and not _case_has_release_mode(case_by_id[case_id])
    ]
    return _check(
        "release_scenario_set_cases_are_release_mode",
        "blocker" if non_release else "pass",
        "Every release scenario set case must be eligible for release mode.",
        [f"{set_id}:non_release:{case_id}" for case_id in non_release],
    )


def _release_scenario_set_unique_ids_check(set_id: str, case_ids: list[str]) -> dict[str, Any]:
    duplicate_count = len(case_ids) - len(set(case_ids))
    return _check(
        "release_scenario_set_ids_unique",
        "blocker" if duplicate_count else "pass",
        "Release scenario set case ids must be unique.",
        [f"{set_id}:duplicates:{duplicate_count}"] if duplicate_count else [],
    )


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]
