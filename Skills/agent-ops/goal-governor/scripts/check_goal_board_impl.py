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
IMPLEMENTATION_NOTES_STATUSES = {"present", "verified"}
IMPLEMENTATION_NOTES_PREVIEW_STATUSES = {"verified", "blocked"}
IMPLEMENTATION_NOTES_LIVE_UPDATE_STATUSES = {"enabled", "blocked"}
IMPLEMENTATION_NOTES_REQUIRED_HEADINGS = (
    "Deep Module Topology",
    "Current Slice Insertion Map",
    "Runtime Truth Surface",
    "Blast Radius View",
    "Validation Coverage",
)
IMPLEMENTATION_NOTES_REQUIRED_COMPONENTS = (
    "DeepModuleMap",
    "InsertionPoint",
    "RuntimeCardState",
    "BlastRadiusMap",
    "ValidatorCoverage",
)
NATIVE_STATUSES = {
    "active",
    "paused",
    "blocked",
    "usageLimited",
    "usage_limited",
    "budgetLimited",
    "budget_limited",
    "complete",
    None,
}
CONTINUATION_NATIVE_STATUSES = {
    "active",
    "paused",
    "budgetLimited",
    "budget_limited",
    "usageLimited",
    "usage_limited",
    "complete",
    "unknown",
    "blocked",
}
GATE_STATUS = {"pass", "blocked", "unknown"}
QUEUE_STATUS = {"absent", "present", "unknown"}
AUTO_CONTINUE_STATUS = {"yes", "no", "unknown"}
CLAIM_ROUTES = {"reproduced", "approximate", "proxy", "blocked"}
CLAIM_STATUSES = {"confirmed", "supported", "approximate", "blocked", "uncertain"}
MAX_NATIVE_OBJECTIVE_CHARS = 4_000
TASK_ID = re.compile(r"^T\d{3}$")
CLAIM_ID = re.compile(r"^C\d{3}$")
NATIVE_GOAL_ID = re.compile(r"^[A-Za-z0-9_-]+$")


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


class SimpleYamlParser:
    """Parse the strict YAML subset emitted by Goal Governor templates."""

    def __init__(self, text: str) -> None:
        self.rows = self._tokenize(text)

    @staticmethod
    def _tokenize(text: str) -> list[tuple[int, str]]:
        rows: list[tuple[int, str]] = []
        for raw_line in text.splitlines():
            if not raw_line.strip() or raw_line.lstrip().startswith("#"):
                continue
            indent = len(raw_line) - len(raw_line.lstrip(" "))
            rows.append((indent, raw_line.strip()))
        return rows

    def parse(self) -> Any:
        parsed, final_index = self._parse_block(0, self.rows[0][0] if self.rows else 0)
        if final_index != len(self.rows):
            raise ValueError("could not parse entire state.yaml")
        return parsed

    def _parse_block(self, index: int, indent: int) -> tuple[Any, int]:
        if index >= len(self.rows):
            return {}, index
        if self.rows[index][1].startswith("- "):
            return self._parse_sequence(index, indent)
        return self._parse_mapping(index, indent)

    def _parse_sequence(self, index: int, indent: int) -> tuple[list[Any], int]:
        values: list[Any] = []
        while self._is_sequence_item(index, indent):
            item, index = self._parse_sequence_item(index, indent)
            values.append(item)
        return values, index

    def _is_sequence_item(self, index: int, indent: int) -> bool:
        return (
            index < len(self.rows)
            and self.rows[index][0] == indent
            and self.rows[index][1].startswith("- ")
        )

    def _parse_sequence_item(self, index: int, indent: int) -> tuple[Any, int]:
        item_text = self.rows[index][1][2:].strip()
        index += 1
        if not item_text:
            return self._parse_block(index, indent + 2)
        if ":" not in item_text:
            return parse_scalar(item_text), index
        item = self._parse_inline_mapping_item(item_text)
        return self._parse_mapping_children(item, index, indent + 2)

    def _parse_inline_mapping_item(self, item_text: str) -> dict[str, Any]:
        key, value = item_text.split(":", 1)
        value = value.strip()
        return {key.strip(): parse_scalar(value) if value else None}

    def _parse_mapping_children(
        self, item: dict[str, Any], index: int, indent: int
    ) -> tuple[dict[str, Any], int]:
        while index < len(self.rows) and self.rows[index][0] >= indent:
            child_indent, child_text = self.rows[index]
            if child_indent != indent or ":" not in child_text:
                break
            child_key, child_value = child_text.split(":", 1)
            index += 1
            child_value = child_value.strip()
            if child_value:
                item[child_key.strip()] = parse_scalar(child_value)
                continue
            child, index = self._parse_block(index, indent + 2)
            item[child_key.strip()] = child
        return item, index

    def _parse_mapping(self, index: int, indent: int) -> tuple[dict[str, Any], int]:
        mapping: dict[str, Any] = {}
        while self._is_mapping_item(index, indent):
            key, value = self.rows[index][1].split(":", 1)
            index = self._assign_mapping_value(mapping, key.strip(), value.strip(), index + 1, indent)
        return mapping, index

    def _is_mapping_item(self, index: int, indent: int) -> bool:
        return (
            index < len(self.rows)
            and self.rows[index][0] == indent
            and not self.rows[index][1].startswith("- ")
            and ":" in self.rows[index][1]
        )

    def _assign_mapping_value(
        self,
        mapping: dict[str, Any],
        key: str,
        value: str,
        index: int,
        indent: int,
    ) -> int:
        if value:
            mapping[key] = parse_scalar(value)
            return index
        child, index = self._parse_block(index, indent + 2)
        mapping[key] = child
        return index


def parse_simple_yaml(text: str) -> Any:
    return SimpleYamlParser(text).parse()


def load_yaml(path: Path) -> Any:
    if yaml is None:
        return parse_simple_yaml(path.read_text(encoding="utf-8"))
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def board_project_root(goal_dir: Path) -> Path:
    if goal_dir.parent.name == "goals" and goal_dir.parent.parent.name in {"docs", "Docs"}:
        return goal_dir.parent.parent.parent
    return goal_dir.parent


def has_worker_task(tasks: Any) -> bool:
    return any(isinstance(task, dict) and task.get("type") == "worker" for task in as_list(tasks))


def safe_relative_path(value: str) -> bool:
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


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
            if receipt_id in receipts:
                raise ValueError(
                    f"receipts.jsonl:{line_number}: duplicate receipt id {receipt_id}"
                )
            receipts[receipt_id] = receipt
    return receipts


def validate_done_receipt_schema(task: dict[str, Any], receipt: dict[str, Any]) -> list[str]:
    task_id = str(task.get("id") or "task")
    task_type = task.get("type")
    errors: list[str] = []
    if task_type == "worker":
        if not isinstance(receipt.get("summary"), str) or not receipt["summary"].strip():
            errors.append(f"{task_id} worker receipt missing summary")
        changed_files = as_list(receipt.get("changed_files"))
        if not changed_files or not all(isinstance(x, str) and x.strip() for x in changed_files):
            errors.append(f"{task_id} worker receipt missing changed_files")
        commands = as_list(receipt.get("commands"))
        if not commands or not all(isinstance(x, str) and x.strip() for x in commands):
            errors.append(f"{task_id} worker receipt missing commands")
    if task_type == "judge":
        if not isinstance(receipt.get("decision"), str) or not receipt["decision"].strip():
            errors.append(f"{task_id} judge receipt missing decision")
        if not isinstance(receipt.get("summary"), str) or not receipt["summary"].strip():
            errors.append(f"{task_id} judge receipt missing summary")
        evidence = as_list(receipt.get("evidence"))
        if not evidence or not all(isinstance(x, str) and x.strip() for x in evidence):
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
        errors.append(
            "goal.native_status must be active, paused, blocked, usageLimited, "
            "usage_limited, budgetLimited, budget_limited, or complete"
        )

    native_goal_id = goal.get("native_goal_id")
    if native_goal_id is not None:
        if not isinstance(native_goal_id, str) or not NATIVE_GOAL_ID.match(native_goal_id):
            errors.append("goal.native_goal_id must be a non-empty opaque id when present")

    for field in ("tokens_used", "time_used_seconds"):
        value = goal.get(field)
        if value is not None and (not isinstance(value, int) or value < 0):
            errors.append(f"goal.{field} must be a non-negative integer when present")

    token_budget = goal.get("token_budget")
    if token_budget is not None and (not isinstance(token_budget, int) or token_budget <= 0):
        errors.append("goal.token_budget must be a positive integer when present")

    for field in ("native_created_at", "native_updated_at"):
        value = goal.get(field)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            errors.append(f"goal.{field} must be a non-empty string when present")

    return errors, str(goal_status) if isinstance(goal_status, str) else None


def require_non_empty_string(mapping: dict[str, Any], field: str, label: str, errors: list[str]) -> None:
    value = mapping.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}.{field} must be a non-empty string")


def require_non_empty_string_list(mapping: dict[str, Any], field: str, label: str, errors: list[str]) -> None:
    values = mapping.get(field)
    if not isinstance(values, list) or not values or not all(isinstance(item, str) and item.strip() for item in values):
        errors.append(f"{label}.{field} must be a non-empty list of strings")


def validate_completion_contract(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    contract = state.get("completion_contract")
    if not isinstance(contract, dict):
        return ["completion_contract must be a mapping"]

    require_non_empty_string(contract, "outcome", "completion_contract", errors)
    require_non_empty_string_list(contract, "verification_surface", "completion_contract", errors)
    require_non_empty_string_list(contract, "constraints", "completion_contract", errors)
    require_non_empty_string_list(contract, "boundaries", "completion_contract", errors)
    require_non_empty_string(contract, "iteration_policy", "completion_contract", errors)
    require_non_empty_string(contract, "blocked_stop_condition", "completion_contract", errors)
    return errors


def validate_continuation_gate(state: dict[str, Any]) -> list[str]:
    gate = state.get("continuation_gate")
    if gate is None:
        return []
    if not isinstance(gate, dict):
        return ["continuation_gate must be a mapping when present"]

    errors: list[str] = []
    if gate.get("native_status") not in CONTINUATION_NATIVE_STATUSES:
        errors.append(
            "continuation_gate.native_status must be active, paused, budgetLimited, "
            "budget_limited, usageLimited, usage_limited, complete, unknown, or blocked"
        )
    for field in ("thread_idle", "goal_active"):
        if gate.get(field) not in GATE_STATUS:
            errors.append(f"continuation_gate.{field} must be pass, blocked, or unknown")
    for field in ("queued_user_input", "pending_work"):
        if gate.get(field) not in QUEUE_STATUS:
            errors.append(f"continuation_gate.{field} must be absent, present, or unknown")
    if gate.get("auto_continue_allowed") not in AUTO_CONTINUE_STATUS:
        errors.append("continuation_gate.auto_continue_allowed must be yes, no, or unknown")
    return errors


def validate_claims(state: dict[str, Any]) -> list[str]:
    claims = state.get("claims")
    if claims is None:
        return []
    if not isinstance(claims, list):
        return ["claims must be a list when present"]

    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, claim in enumerate(claims, start=1):
        if not isinstance(claim, dict):
            errors.append(f"claim {index} must be a mapping")
            continue
        claim_id = claim.get("id")
        label = claim_id if isinstance(claim_id, str) else f"claim {index}"
        if not isinstance(claim_id, str) or not CLAIM_ID.match(claim_id):
            errors.append(f"claim {index} has invalid id")
        elif claim_id in seen_ids:
            errors.append(f"duplicate claim id {claim_id}")
        else:
            seen_ids.add(claim_id)
        require_non_empty_string(claim, "claim", label, errors)
        require_non_empty_string_list(claim, "evidence_surface", label, errors)
        if claim.get("route") not in CLAIM_ROUTES:
            errors.append(f"{label}.route must be reproduced, approximate, proxy, or blocked")
        if claim.get("status") not in CLAIM_STATUSES:
            errors.append(f"{label}.status must be confirmed, supported, approximate, blocked, or uncertain")
        require_non_empty_string_list(claim, "remaining_uncertainty", label, errors)
    return errors


def validate_implementation_notes_artifact(
    state: dict[str, Any],
    goal_dir: Path,
) -> list[str]:
    tasks = state.get("tasks")
    if not has_worker_task(tasks):
        return []

    errors: list[str] = []
    artifacts = state.get("artifacts")
    if not isinstance(artifacts, dict):
        return ["artifacts.implementation_notes is required when Worker tasks exist"]

    notes = artifacts.get("implementation_notes")
    if not isinstance(notes, dict):
        return ["artifacts.implementation_notes is required when Worker tasks exist"]

    path_value = notes.get("path")
    if not isinstance(path_value, str) or not path_value.strip():
        errors.append("artifacts.implementation_notes.path must be a non-empty string")
        path_value = ""
    elif not safe_relative_path(path_value):
        errors.append("artifacts.implementation_notes.path must be a safe relative path")
    elif not path_value.startswith(".harness/implementation-notes/"):
        errors.append("artifacts.implementation_notes.path must be under .harness/implementation-notes/")
    elif not path_value.endswith(".mdx"):
        errors.append("artifacts.implementation_notes.path must use .mdx")

    if notes.get("format") != "mdx":
        errors.append("artifacts.implementation_notes.format must be mdx")
    if notes.get("status") not in IMPLEMENTATION_NOTES_STATUSES:
        errors.append("artifacts.implementation_notes.status must be present or verified")

    preview = notes.get("browser_preview")
    if not isinstance(preview, dict):
        errors.append("artifacts.implementation_notes.browser_preview must be a mapping")
    else:
        if preview.get("surface") != "localhost":
            errors.append("artifacts.implementation_notes.browser_preview.surface must be localhost")
        preview_status = preview.get("status")
        if preview_status not in IMPLEMENTATION_NOTES_PREVIEW_STATUSES:
            errors.append(
                "artifacts.implementation_notes.browser_preview.status must be verified or blocked"
            )
        if preview_status == "verified":
            require_non_empty_string(
                preview,
                "url",
                "artifacts.implementation_notes.browser_preview",
                errors,
            )
        if preview_status == "blocked":
            require_non_empty_string(
                preview,
                "blocker",
                "artifacts.implementation_notes.browser_preview",
                errors,
            )
        live_update = preview.get("live_update")
        if not isinstance(live_update, dict):
            errors.append(
                "artifacts.implementation_notes.browser_preview.live_update must be a mapping"
            )
        else:
            live_status = live_update.get("status")
            if live_status not in IMPLEMENTATION_NOTES_LIVE_UPDATE_STATUSES:
                errors.append(
                    "artifacts.implementation_notes.browser_preview.live_update.status must be enabled or blocked"
                )
            if preview_status == "verified" and live_status != "enabled":
                errors.append(
                    "verified browser preview requires live_update.status enabled"
                )
            if live_status == "enabled":
                require_non_empty_string(
                    live_update,
                    "command",
                    "artifacts.implementation_notes.browser_preview.live_update",
                    errors,
                )
                require_non_empty_string(
                    live_update,
                    "watched_path",
                    "artifacts.implementation_notes.browser_preview.live_update",
                    errors,
                )
                if live_update.get("watched_path") != path_value:
                    errors.append(
                        "artifacts.implementation_notes.browser_preview.live_update.watched_path must match artifacts.implementation_notes.path"
                    )
            if live_status == "blocked":
                require_non_empty_string(
                    live_update,
                    "blocker",
                    "artifacts.implementation_notes.browser_preview.live_update",
                    errors,
                )

    if path_value and safe_relative_path(path_value):
        note_path = board_project_root(goal_dir) / path_value
        if not note_path.is_file():
            errors.append(f"implementation notes artifact missing: {path_value}")
        else:
            note_text = note_path.read_text(encoding="utf-8")
            if "schema_version:" not in note_text[:500]:
                errors.append("implementation notes artifact must declare schema_version frontmatter")
            missing_headings = [
                heading
                for heading in IMPLEMENTATION_NOTES_REQUIRED_HEADINGS
                if f"## {heading}" not in note_text and f"# {heading}" not in note_text
            ]
            if missing_headings:
                errors.append(
                    "implementation notes artifact missing required sections: "
                    + ", ".join(missing_headings)
                )
            missing_components = [
                component
                for component in IMPLEMENTATION_NOTES_REQUIRED_COMPONENTS
                if f"<{component}" not in note_text
            ]
            if missing_components:
                errors.append(
                    "implementation notes artifact missing required components: "
                    + ", ".join(missing_components)
                )

    allowed_files = {
        str(path)
        for task in as_list(tasks)
        if isinstance(task, dict) and task.get("type") == "worker"
        for path in as_list(task.get("allowed_files"))
    }
    if path_value and path_value not in allowed_files:
        errors.append("Worker allowed_files must include artifacts.implementation_notes.path")

    return errors


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
    tasks_by_id: dict[str, dict[str, Any]] = {}
    for index, task in enumerate(tasks, start=1):
        if not isinstance(task, dict):
            errors.append(f"task {index} must be a mapping")
            continue
        task_errors, is_active = validate_task(task, index, ids, receipts)
        errors.extend(task_errors)
        if is_active:
            active_tasks.append(task)
        task_id = task.get("id")
        if task_id:
            tasks_by_id[task_id] = task

    if goal_status != "done" and not active_tasks_are_parallel_workers(active_tasks, rules):
        errors.append(
            "non-done goals require exactly one active task unless parallel active workers have disjoint allowed_files"
        )

    if goal_status == "done":
        if active_tasks:
            errors.append("done goals cannot have active tasks")
        final_receipts = []
        for receipt_id, receipt in receipts.items():
            if (
                receipt.get("decision") == "complete"
                and receipt.get("assignee") in {"Judge", "PM"}
                and receipt.get("task_id") in ids
            ):
                task_id = receipt.get("task_id")
                task = tasks_by_id.get(task_id)
                if task and task.get("status") == "done" and task.get("receipt_id") == receipt_id:
                    final_receipts.append(receipt)
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
    errors.extend(validate_completion_contract(state))
    errors.extend(validate_continuation_gate(state))
    errors.extend(validate_claims(state))
    errors.extend(validate_implementation_notes_artifact(state, goal_dir))

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
