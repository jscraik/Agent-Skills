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
            receipt_id = receipt.get("id")
            task_id = receipt.get("task_id")
            if not isinstance(receipt_id, str) or not receipt_id:
                raise ValueError(f"receipts.jsonl:{line_number}: missing id")
            if not isinstance(task_id, str) or not TASK_ID.match(task_id):
                raise ValueError(f"receipts.jsonl:{line_number}: invalid task_id")
            receipts[receipt_id] = receipt
    return receipts


def validate_board(goal_dir: Path) -> list[str]:
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

    goal = state.get("goal")
    if not isinstance(goal, dict):
        errors.append("goal must be a mapping")
    elif goal.get("status") not in {"active", "paused", "blocked", "done"}:
        errors.append("goal.status must be active, paused, blocked, or done")

    tasks = state.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        errors.append("tasks must be a non-empty list")
        return errors

    try:
        receipts = validate_receipts(goal_dir / "receipts.jsonl")
    except ValueError as exc:
        errors.append(str(exc))
        receipts = {}

    ids: set[str] = set()
    active_tasks: list[dict[str, Any]] = []
    for index, task in enumerate(tasks, start=1):
        if not isinstance(task, dict):
            errors.append(f"task {index} must be a mapping")
            continue
        task_id = task.get("id")
        if not isinstance(task_id, str) or not TASK_ID.match(task_id):
            errors.append(f"task {index} has invalid id")
        elif task_id in ids:
            errors.append(f"duplicate task id {task_id}")
        else:
            ids.add(task_id)
        if task.get("type") not in TASK_TYPES:
            errors.append(f"{task_id or f'task {index}'} has invalid type")
        if task.get("assignee") not in ASSIGNEES:
            errors.append(f"{task_id or f'task {index}'} has invalid assignee")
        status = task.get("status")
        if status not in STATUSES:
            errors.append(f"{task_id or f'task {index}'} has invalid status")
        if not isinstance(task.get("objective"), str) or not task["objective"].strip():
            errors.append(f"{task_id or f'task {index}'} missing objective")
        if status == "active":
            active_tasks.append(task)
        if task.get("type") == "worker":
            for field in ("allowed_files", "verify", "stop_if"):
                if not as_list(task.get(field)):
                    errors.append(f"{task_id or f'task {index}'} worker missing {field}")
        if status == "done" and task.get("receipt_id") not in receipts:
            errors.append(f"{task_id or f'task {index}'} done without matching receipt")

    if goal.get("status") != "done" and len(active_tasks) != 1:
        errors.append("non-done goals require exactly one active task")

    if goal.get("status") == "done":
        final_receipts = [
            receipt
            for receipt in receipts.values()
            if receipt.get("decision") == "complete"
            and receipt.get("assignee") in {"Judge", "PM"}
        ]
        if not final_receipts:
            errors.append("done goal requires final Judge or PM receipt with decision=complete")

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
