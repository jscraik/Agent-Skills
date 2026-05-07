#!/usr/bin/env python3
"""Validate a Goal Governor board."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised in lean runtimes
    yaml = None


ALLOWED_ROOT = {"goal.md", "state.yaml", "receipts.jsonl", "notes"}
TASK_TYPES = {"scout", "judge", "worker", "pm"}
ASSIGNEES = {"Scout", "Judge", "Worker", "PM"}
STATUSES = {"queued", "active", "blocked", "done"}
NATIVE_STATUSES = {"active", "paused", "budgetLimited", "budget_limited", "complete", None}
MAX_NATIVE_OBJECTIVE_CHARS = 4_000
TASK_ID = re.compile(r"^T\d{3}$")


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def parse_scalar(value: str) -> Any:
    if value in {"null", "None", "~"}:
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        return value


def parse_simple_yaml(text: str) -> Any:
    """Parse the strict YAML subset emitted by Goal Governor templates."""

    rows: list[tuple[int, str]] = []
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        rows.append((indent, raw_line.strip()))

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        if index >= len(rows):
            return {}, index
        _, first = rows[index]
        if first.startswith("- "):
            values: list[Any] = []
            while index < len(rows) and rows[index][0] == indent and rows[index][1].startswith("- "):
                item_text = rows[index][1][2:].strip()
                index += 1
                item: Any
                if not item_text:
                    item, index = parse_block(index, indent + 2)
                elif ":" in item_text:
                    key, value = item_text.split(":", 1)
                    item = {key.strip(): parse_scalar(value.strip()) if value.strip() else None}
                    while index < len(rows) and rows[index][0] >= indent + 2:
                        child_indent, child_text = rows[index]
                        if child_indent != indent + 2 or ":" not in child_text:
                            break
                        child_key, child_value = child_text.split(":", 1)
                        child_key = child_key.strip()
                        child_value = child_value.strip()
                        index += 1
                        if child_value:
                            item[child_key] = parse_scalar(child_value)
                        else:
                            child, index = parse_block(index, indent + 4)
                            item[child_key] = child
                else:
                    item = parse_scalar(item_text)
                values.append(item)
            return values, index

        mapping: dict[str, Any] = {}
        while index < len(rows) and rows[index][0] == indent and not rows[index][1].startswith("- "):
            _, text = rows[index]
            if ":" not in text:
                raise ValueError(f"invalid line: {text}")
            key, value = text.split(":", 1)
            key = key.strip()
            value = value.strip()
            index += 1
            if value:
                mapping[key] = parse_scalar(value)
            else:
                child, index = parse_block(index, indent + 2)
                mapping[key] = child
        return mapping, index

    parsed, final_index = parse_block(0, rows[0][0] if rows else 0)
    if final_index != len(rows):
        raise ValueError("could not parse entire state.yaml")
    return parsed


def load_yaml(path: Path) -> Any:
    if yaml is None:
        return parse_simple_yaml(path.read_text(encoding="utf-8"))
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def active_tasks_are_parallel_workers(
    active_tasks: list[dict[str, Any]], rules: dict[str, Any]
) -> bool:
    if not active_tasks:
        return False
    if len(active_tasks) == 1:
        return True
    if rules.get("one_active_task") is not False and rules.get("parallel_workers") is not True:
        return False
    seen_files: set[str] = set()
    for task in active_tasks:
        if task.get("type") != "worker":
            return False
        allowed_files = as_list(task.get("allowed_files"))
        if not allowed_files:
            return False
        file_set = {str(path) for path in allowed_files}
        if seen_files & file_set:
            return False
        seen_files.update(file_set)
    return True


def validate_receipts(path: Path) -> dict[str, dict[str, Any]]:
    receipts: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return receipts
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                receipt = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"receipts.jsonl:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(receipt, dict):
                raise ValueError(f"receipts.jsonl:{line_number}: receipt must be an object")
            receipt_id = receipt.get("id")
            task_id = receipt.get("task_id")
            if not isinstance(receipt_id, str) or not receipt_id:
                raise ValueError(f"receipts.jsonl:{line_number}: missing id")
            if not isinstance(task_id, str) or not TASK_ID.match(task_id):
                raise ValueError(f"receipts.jsonl:{line_number}: invalid task_id")
            receipts[receipt_id] = receipt
    return receipts


def validate_done_receipt_schema(task: dict[str, Any], receipt: dict[str, Any]) -> list[str]:
    task_id = str(task.get("id") or "task")
    task_type = task.get("type")
    errors: list[str] = []
    if task_type == "worker":
        if not isinstance(receipt.get("summary"), str) or not receipt["summary"].strip():
            errors.append(f"{task_id} worker receipt missing summary")
        if not as_list(receipt.get("changed_files")):
            errors.append(f"{task_id} worker receipt missing changed_files")
        if not as_list(receipt.get("commands")):
            errors.append(f"{task_id} worker receipt missing commands")
    if task_type == "judge":
        if not isinstance(receipt.get("decision"), str) or not receipt["decision"].strip():
            errors.append(f"{task_id} judge receipt missing decision")
        if not isinstance(receipt.get("summary"), str) or not receipt["summary"].strip():
            errors.append(f"{task_id} judge receipt missing summary")
        if not as_list(receipt.get("evidence")):
            errors.append(f"{task_id} judge receipt missing evidence")
    return errors


def validate_root(goal_dir: Path) -> list[str]:
    errors: list[str] = []
    if not goal_dir.exists() or not goal_dir.is_dir():
        return [f"{goal_dir} is not a directory"]

    root_names = {child.name for child in goal_dir.iterdir()}
    unexpected = sorted(root_names - ALLOWED_ROOT)
    if unexpected:
        errors.append(f"unexpected root entries: {', '.join(unexpected)}")
    for required in ("goal.md", "state.yaml", "notes"):
        if required not in root_names:
            errors.append(f"missing {required}")
    for required_file in ("goal.md", "state.yaml"):
        if required_file in root_names and not (goal_dir / required_file).is_file():
            errors.append(f"{required_file} must be a file")
    if "notes" in root_names and not (goal_dir / "notes").is_dir():
        errors.append("notes must be a directory")
    return errors


def validate_goal_section(state: dict[str, Any]) -> tuple[list[str], str | None]:
    errors: list[str] = []
    goal = state.get("goal")
    if not isinstance(goal, dict):
        return ["goal must be a mapping"], None

    goal_status = goal.get("status")
    if goal_status not in {"active", "paused", "blocked", "done"}:
        errors.append("goal.status must be active, paused, blocked, or done")

    native_objective = goal.get("native_objective")
    if native_objective is not None:
        if not isinstance(native_objective, str) or not native_objective.strip():
            errors.append("goal.native_objective must be a non-empty string when present")
        elif len(native_objective) > MAX_NATIVE_OBJECTIVE_CHARS:
            errors.append("goal.native_objective must be at most 4000 characters")

    native_status = goal.get("native_status")
    if native_status not in NATIVE_STATUSES:
        errors.append("goal.native_status must be active, paused, budgetLimited, budget_limited, or complete")

    for field in ("tokens_used", "time_used_seconds"):
        value = goal.get(field)
        if value is not None and (not isinstance(value, int) or value < 0):
            errors.append(f"goal.{field} must be a non-negative integer when present")

    token_budget = goal.get("token_budget")
    if token_budget is not None and (not isinstance(token_budget, int) or token_budget <= 0):
        errors.append("goal.token_budget must be a positive integer when present")

    return errors, str(goal_status) if isinstance(goal_status, str) else None


def validate_task(
    task: dict[str, Any],
    index: int,
    ids: set[str],
    receipts: dict[str, dict[str, Any]],
) -> tuple[list[str], bool]:
    errors: list[str] = []
    task_id = task.get("id")
    if not isinstance(task_id, str) or not TASK_ID.match(task_id):
        errors.append(f"task {index} has invalid id")
    elif task_id in ids:
        errors.append(f"duplicate task id {task_id}")
    else:
        ids.add(task_id)

    label = task_id or f"task {index}"
    if task.get("type") not in TASK_TYPES:
        errors.append(f"{label} has invalid type")
    if task.get("assignee") not in ASSIGNEES:
        errors.append(f"{label} has invalid assignee")
    status = task.get("status")
    if status not in STATUSES:
        errors.append(f"{label} has invalid status")
    if not isinstance(task.get("objective"), str) or not task["objective"].strip():
        errors.append(f"{label} missing objective")
    if task.get("type") == "worker":
        for field in ("allowed_files", "verify", "stop_if"):
            if not as_list(task.get(field)):
                errors.append(f"{label} worker missing {field}")
    if status == "done":
        receipt_id = task.get("receipt_id")
        receipt = receipts.get(receipt_id)
        if receipt is None:
            errors.append(f"{label} done without matching receipt")
        elif receipt.get("task_id") != task_id:
            errors.append(f"{label} done receipt belongs to another task")
        else:
            errors.extend(validate_done_receipt_schema(task, receipt))
    return errors, status == "active"


def validate_tasks_and_receipts(
    tasks: Any,
    receipts: dict[str, dict[str, Any]],
    rules: dict[str, Any],
    goal_status: str | None,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(tasks, list) or not tasks:
        return ["tasks must be a non-empty list"]

    ids: set[str] = set()
    active_tasks: list[dict[str, Any]] = []
    for index, task in enumerate(tasks, start=1):
        if not isinstance(task, dict):
            errors.append(f"task {index} must be a mapping")
            continue
        task_errors, is_active = validate_task(task, index, ids, receipts)
        errors.extend(task_errors)
        if is_active:
            active_tasks.append(task)

    if goal_status != "done" and not active_tasks_are_parallel_workers(active_tasks, rules):
        errors.append(
            "non-done goals require exactly one active task unless parallel active workers have disjoint allowed_files"
        )

    if goal_status == "done":
        if active_tasks:
            errors.append("done goals cannot have active tasks")
        final_receipts = [
            receipt
            for receipt in receipts.values()
            if receipt.get("decision") == "complete"
            and receipt.get("assignee") in {"Judge", "PM"}
            and receipt.get("task_id") in ids
        ]
        if not final_receipts:
            errors.append(
                "done goal requires final Judge or PM receipt with decision=complete for an existing task"
            )

    return errors


def validate_board(goal_dir: Path) -> list[str]:
    errors = validate_root(goal_dir)
    if errors:
        return errors

    try:
        state = load_yaml(goal_dir / "state.yaml")
    except Exception as exc:  # noqa: BLE001 - command should explain any parser failure
        return [str(exc)]

    if not isinstance(state, dict):
        return ["state.yaml must be a mapping"]
    if state.get("version") != 2:
        errors.append("version must be 2")

    goal_errors, goal_status = validate_goal_section(state)
    errors.extend(goal_errors)

    rules = state.get("rules")
    if not isinstance(rules, dict):
        rules = {}

    try:
        receipts = validate_receipts(goal_dir / "receipts.jsonl")
    except ValueError as exc:
        errors.append(str(exc))
        receipts = {}

    errors.extend(validate_tasks_and_receipts(state.get("tasks"), receipts, rules, goal_status))
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        return fail("usage: check_goal_board.py <goal-directory>")
    errors = validate_board(Path(argv[1]))
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: goal board is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
