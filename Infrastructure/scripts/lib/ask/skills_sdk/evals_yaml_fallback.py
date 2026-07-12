from __future__ import annotations

from typing import Any


def load_minimal_metadata(text: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    release_scenario_sets = _load_minimal_release_scenario_sets(text)
    if release_scenario_sets:
        metadata["release_scenario_sets"] = release_scenario_sets
    evaluation_lane_policy = _load_minimal_evaluation_lane_policy(text)
    if evaluation_lane_policy:
        metadata["evaluation_lane_policy"] = evaluation_lane_policy
    return metadata


def _load_minimal_release_scenario_sets(text: str) -> list[dict[str, Any]]:
    rows = _section_rows(text, "release_scenario_sets")
    return [_parse_release_set(block) for block in _list_blocks(rows, 2)]


def _parse_release_set(block: list[tuple[str, int]]) -> dict[str, Any]:
    result: dict[str, Any] = {"groups": {}}
    for stripped, indent in block:
        if indent == 2 and stripped.startswith("- "):
            _assign_pair(result, stripped[2:])
        elif indent == 4 and ":" in stripped and stripped not in {"groups:", "cases:"}:
            _assign_pair(result, stripped)
    groups, cases = _parse_release_children(block)
    result["groups"] = groups
    if cases is not None:
        result["cases"] = cases
    return result


def _parse_release_children(block: list[tuple[str, int]]) -> tuple[dict[str, list[str]], list[str] | None]:
    return _parse_group_lists(block), _parse_case_list(block)


def _parse_group_lists(block: list[tuple[str, int]]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    active = False
    group: str | None = None
    for stripped, indent in block:
        if indent == 4 and stripped == "groups:":
            active, group = True, None
        elif active:
            if indent == 4:
                break
            if indent == 6 and stripped.endswith(":"):
                group = stripped[:-1].strip()
                groups[group] = []
            if indent != 8 or not stripped.startswith("- ") or group is None:
                continue
            groups[group].append(_parse_scalar(stripped[2:].strip()))
    return groups


def _parse_case_list(block: list[tuple[str, int]]) -> list[str] | None:
    cases: list[str] | None = None
    active = False
    for stripped, indent in block:
        if indent == 4 and stripped == "cases:":
            cases, active = [], True
        elif active and indent == 4:
            break
        elif active and indent == 6 and stripped.startswith("- ") and cases is not None:
            cases.append(_parse_scalar(stripped[2:].strip()))
    return cases


def _load_minimal_evaluation_lane_policy(text: str) -> dict[str, Any]:
    rows = _section_rows(text, "evaluation_lane_policy")
    policy = _parse_policy_scalars(rows)
    for section in ("model_routing", "pools"):
        policy[section] = _parse_policy_map(rows, section)
    return policy


def _parse_policy_scalars(rows: list[tuple[str, int]]) -> dict[str, Any]:
    policy: dict[str, Any] = {}
    for stripped, indent in rows:
        if indent != 2 or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        if key in {"model_routing", "pools"}:
            continue
        if key == "baseline_identity_fields":
            policy[key] = _indented_list(rows, 4)
        else:
            policy[key] = _parse_scalar(value.strip())
    return policy


def _parse_policy_map(rows: list[tuple[str, int]], section: str) -> dict[str, dict[str, Any]]:
    section_rows = _child_rows(rows, section, 2)
    return {_map_key(block): _parse_policy_row(block) for block in _map_blocks(section_rows, 4)}


def _parse_policy_row(block: list[tuple[str, int]]) -> dict[str, Any]:
    row: dict[str, Any] = {}
    for stripped, indent in block:
        if indent != 6 or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        row[key] = _indented_list(block, 8) if key == "cases" and not value.strip() else _parse_scalar(value.strip())
    return row


def _map_key(block: list[tuple[str, int]]) -> str:
    first = block[0][0][:-1].strip()
    return first


def _section_rows(text: str, heading: str) -> list[tuple[str, int]]:
    rows: list[tuple[str, int]] = []
    active = False
    for raw_line in text.splitlines():
        stripped, indent = _minimal_line(raw_line)
        if indent == 0 and stripped == f"{heading}:":
            active = True
            continue
        if active and indent == 0:
            break
        if active and stripped:
            rows.append((stripped, indent))
    return rows


def _child_rows(rows: list[tuple[str, int]], heading: str, heading_indent: int) -> list[tuple[str, int]]:
    start = next((index for index, (stripped, indent) in enumerate(rows) if indent == heading_indent and stripped == f"{heading}:"), None)
    if start is None:
        return []
    result: list[tuple[str, int]] = []
    for stripped, indent in rows[start + 1 :]:
        if indent == heading_indent:
            break
        if stripped:
            result.append((stripped, indent))
    return result


def _list_blocks(rows: list[tuple[str, int]], item_indent: int) -> list[list[tuple[str, int]]]:
    blocks: list[list[tuple[str, int]]] = []
    for row in rows:
        if row[1] == item_indent and row[0].startswith("- "):
            blocks.append([row])
        elif blocks:
            blocks[-1].append(row)
    return blocks


def _map_blocks(rows: list[tuple[str, int]], item_indent: int) -> list[list[tuple[str, int]]]:
    blocks: list[list[tuple[str, int]]] = []
    for row in rows:
        if row[1] == item_indent and row[0].endswith(":"):
            blocks.append([row])
        elif blocks:
            blocks[-1].append(row)
    return blocks


def _indented_list(rows: list[tuple[str, int]], item_indent: int) -> list[str]:
    return [_parse_scalar(stripped[2:].strip()) for stripped, indent in rows if indent == item_indent and stripped.startswith("- ")]


def _assign_pair(target: dict[str, Any], pair: str) -> None:
    if ":" not in pair:
        return
    key, value = pair.split(":", 1)
    target[key.strip()] = _parse_scalar(value.strip())


def _minimal_line(raw_line: str) -> tuple[str, int]:
    line = raw_line.split("#", 1)[0].rstrip()
    return line.strip(), len(line) - len(line.lstrip(" "))


def _parse_scalar(value: str) -> Any:
    if value in {"true", "false"}:
        return value == "true"
    if value.isdigit():
        return int(value)
    return value.strip("'\"")
