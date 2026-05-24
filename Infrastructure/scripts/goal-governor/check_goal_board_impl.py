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
    """
    Emit a standardized failure message to stderr and return exit code 1.
    
    Parameters:
        message (str): Human-readable failure description to include in the printed message.
    
    Returns:
        int: Exit code `1`.
    """
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def parse_scalar(value: str) -> Any:
    """
    Parse a simple scalar token from a YAML-like inline representation into the corresponding Python value.
    
    Parameters:
        value (str): A single-token scalar as found in the simplified YAML lines (e.g. unquoted numeric text, quoted string, boolean or null literals).
    
    Returns:
        The parsed Python value: `None` for `null`/`None`/`~`, `True` for `true`, `False` for `false`, an `int` when the token is an integer, or a `str` for quoted or other text.
    """
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
        """
        Initialize the parser for a strict subset of YAML text and tokenize it into rows.
        
        Parameters:
            text (str): The YAML-like input to parse. The parser accepts the limited format produced by Goal Governor templates.
        
        The instance attribute `rows` is a list of (indent, stripped_line) tuples produced by tokenization; blank lines and comment lines beginning with `#` are omitted.
        """
        self.rows = self._tokenize(text)

    @staticmethod
    def _tokenize(text: str) -> list[tuple[int, str]]:
        """
        Convert multiline YAML-like text into a list of non-empty, non-comment rows with their leading-space indentation.
        
        Parameters:
            text (str): Input text to tokenize; may contain blank lines and lines starting with `#`.
        
        Returns:
            list[tuple[int, str]]: A list of tuples `(indent, line)` where `indent` is the number of leading space characters and `line` is the trimmed line content. Blank lines and lines that are comments (start with `#` after optional leading space) are omitted.
        """
        rows: list[tuple[int, str]] = []
        for raw_line in text.splitlines():
            if not raw_line.strip() or raw_line.lstrip().startswith("#"):
                continue
            indent = len(raw_line) - len(raw_line.lstrip(" "))
            rows.append((indent, raw_line.strip()))
        return rows

    def parse(self) -> Any:
        """
        Parse the tokenized YAML-like input and return the resulting Python data structure.
        
        Parses from the beginning of the token stream produced during initialization and verifies that the entire input is consumed; if any unparsed lines remain a ValueError is raised.
        
        Returns:
            The parsed Python object representing the document (mapping, list, or scalar).
        
        Raises:
            ValueError: if the parser does not consume all input rows (error message: "could not parse entire state.yaml").
        """
        parsed, final_index = self._parse_block(0, self.rows[0][0] if self.rows else 0)
        if final_index != len(self.rows):
            raise ValueError("could not parse entire state.yaml")
        return parsed

    def _parse_block(self, index: int, indent: int) -> tuple[Any, int]:
        """
        Parse a YAML block starting at the given row index and indentation level.
        
        Delegates to the sequence parser if the current line begins with "- ", otherwise delegates to the mapping parser. Returns the parsed Python value for the block and the index of the next unconsumed row.
        
        Parameters:
            index (int): Row index in the tokenized input to start parsing from.
            indent (int): Expected indentation level for the block.
        
        Returns:
            tuple[Any, int]: A tuple of (parsed_value, next_index) where `parsed_value` is the mapping or sequence parsed from the block and `next_index` is the index of the first row not consumed by this block.
        """
        if index >= len(self.rows):
            return {}, index
        if self.rows[index][1].startswith("- "):
            return self._parse_sequence(index, indent)
        return self._parse_mapping(index, indent)

    def _parse_sequence(self, index: int, indent: int) -> tuple[list[Any], int]:
        """
        Parse a YAML sequence starting at the given token index and indentation level.
        
        Parameters:
            index (int): Index in the token stream where the sequence begins.
            indent (int): Expected indentation level for sequence items.
        
        Returns:
            tuple[list[Any], int]: A tuple (values, next_index) where `values` is the list of parsed sequence items and `next_index` is the index of the first token not consumed by this sequence.
        """
        values: list[Any] = []
        while self._is_sequence_item(index, indent):
            item, index = self._parse_sequence_item(index, indent)
            values.append(item)
        return values, index

    def _is_sequence_item(self, index: int, indent: int) -> bool:
        """
        Determine whether the row at `index` is a YAML sequence item at the specified `indent`.
        
        Parameters:
            index (int): Row index to check.
            indent (int): Expected indentation level.
        
        Returns:
            True if the row exists, has indentation equal to `indent`, and its text starts with "- ", False otherwise.
        """
        return (
            index < len(self.rows)
            and self.rows[index][0] == indent
            and self.rows[index][1].startswith("- ")
        )

    def _parse_sequence_item(self, index: int, indent: int) -> tuple[Any, int]:
        """
        Parse a single YAML sequence item at the given row index and indentation, and return the parsed value with the next row index.
        
        Parameters:
        	index (int): Current row index in the tokenized input.
        	indent (int): Expected indentation (number of spaces) for items at this sequence level.
        
        Returns:
        	tuple[Any, int]: A pair where the first element is the parsed item (a scalar, mapping, or nested block structure) and the second element is the index of the next unconsumed row.
        """
        item_text = self.rows[index][1][2:].strip()
        index += 1
        if not item_text:
            return self._parse_block(index, indent + 2)
        if ":" not in item_text:
            return parse_scalar(item_text), index
        item = self._parse_inline_mapping_item(item_text)
        return self._parse_mapping_children(item, index, indent + 2)

    def _parse_inline_mapping_item(self, item_text: str) -> dict[str, Any]:
        """
        Parse an inline mapping item of the form "key: value" into a single-key dictionary.
        
        The input is split at the first colon; leading/trailing whitespace is removed from the key and value. If the value is empty the returned value is None; otherwise the value is parsed as a simple scalar (e.g. null/~ → None, "true"/"false" → booleans, unquoted numerals → int, quoted strings → stripped string).
        
        Parameters:
            item_text (str): A single inline mapping item, e.g. "name: Alice" or "flag:".
        
        Returns:
            dict[str, Any]: A dictionary with the stripped key mapped to the parsed value or None when the value is empty.
        """
        key, value = item_text.split(":", 1)
        value = value.strip()
        return {key.strip(): parse_scalar(value) if value else None}

    def _parse_mapping_children(
        self, item: dict[str, Any], index: int, indent: int
    ) -> tuple[dict[str, Any], int]:
        """
        Populate `item` by parsing consecutive mapping children from `self.rows` starting at `index` for the given `indent`.
        
        Parameters:
            item (dict[str, Any]): Mapping to be populated with parsed child key/value pairs.
            index (int): Row index in `self.rows` where child parsing begins.
            indent (int): Expected indentation level for mapping children.
        
        Returns:
            tuple[dict[str, Any], int]: The updated `item` and the index of the next unconsumed row.
        """
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
        """
        Parse a contiguous mapping block from the parser's tokenized rows starting at the given index and indentation.
        
        Parameters:
        	index (int): Row index at which to begin parsing the mapping.
        	indent (int): Expected indentation level for mapping items.
        
        Returns:
        	tuple[dict[str, Any], int]: A mapping of parsed keys to values and the index of the first row not consumed by this mapping.
        """
        mapping: dict[str, Any] = {}
        while self._is_mapping_item(index, indent):
            key, value = self.rows[index][1].split(":", 1)
            index = self._assign_mapping_value(mapping, key.strip(), value.strip(), index + 1, indent)
        return mapping, index

    def _is_mapping_item(self, index: int, indent: int) -> bool:
        """
        Determine whether the row at the given index is a mapping item (a `key: value` line) at the specified indentation level.
        
        Parameters:
            index (int): Zero-based index of the row to check.
            indent (int): Expected indentation level for the mapping item.
        
        Returns:
            bool: `True` if the row exists, has the given indentation, does not start a sequence (`- `), and contains a colon (`:`); `False` otherwise.
        """
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
        """
        Assign a value into `mapping` for `key` using either a parsed scalar `value` or a nested block parsed from the token stream.
        
        If `value` is a non-empty string it is converted via `parse_scalar` and stored; otherwise a nested block beginning at the next indentation level is parsed and stored.
        
        Parameters:
            mapping (dict[str, Any]): Target mapping to receive the key/value.
            key (str): Key to set in `mapping`.
            value (str): Inline value text following the ':' on the current line; may be empty to indicate a nested block.
            index (int): Current token index in the parser; used as the starting point for nested parsing.
            indent (int): Current line indentation level; used to determine the nested block indentation.
        
        Returns:
            int: Updated token index after consuming any nested block (or the original `index` if a scalar was assigned).
        """
        if value:
            mapping[key] = parse_scalar(value)
            return index
        child, index = self._parse_block(index, indent + 2)
        mapping[key] = child
        return index


def parse_simple_yaml(text: str) -> Any:
    """
    Parse a strict subset of YAML into native Python objects.
    
    Parses text written in the limited YAML dialect produced by Goal Governor templates and returns the corresponding Python value: mappings to dict, sequences to list, scalars to str/int/bool/None.
    
    Parameters:
        text (str): YAML content to parse.
    
    Returns:
        The Python object representation of the parsed YAML (dict, list, or scalar).
    """
    return SimpleYamlParser(text).parse()


def load_yaml(path: Path) -> Any:
    """
    Load and parse YAML content from the given file path, using PyYAML if available and falling back to the bundled simple YAML parser otherwise.
    
    Parameters:
        path (Path): Path to the YAML file; the file is read using UTF-8 encoding.
    
    Returns:
        Any: The parsed Python representation of the YAML content (mapping, sequence, scalar, or None).
    """
    if yaml is None:
        return parse_simple_yaml(path.read_text(encoding="utf-8"))
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def as_list(value: Any) -> list[Any]:
    """
    Normalize a value to a list.
    
    Parameters:
        value (Any): The value to normalize.
    
    Returns:
        list[Any]: `value` if it is a list, otherwise an empty list.
    """
    return value if isinstance(value, list) else []


def active_tasks_are_parallel_workers(
    active_tasks: list[dict[str, Any]], rules: dict[str, Any]
) -> bool:
    """
    Check whether the provided active tasks qualify as parallel worker tasks with disjoint allowed_files under the given rules.
    
    Evaluates whether multiple active tasks can run in parallel by requiring each active task to be of type "worker", to have a non-empty `allowed_files` list, and for those file sets to be pairwise disjoint. The rules mapping can override default constraints: if `rules["one_active_task"]` is not False and `rules["parallel_workers"]` is not True, parallel workers are disallowed.
    
    Parameters:
    	active_tasks (list[dict[str, Any]]): Active task mappings to evaluate.
    	rules (dict[str, Any]): Optional rules that may contain `one_active_task` and `parallel_workers` keys to permit or forbid parallel worker tasks.
    
    Returns:
    	`true` if the tasks meet the parallel-worker requirements (or a single active task), `false` otherwise.
    """
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
    """
    Validate and load receipts from a JSONL file.
    
    Parameters:
        path (Path): Path to a receipts.jsonl file.
    
    Returns:
        dict[str, dict[str, Any]]: Mapping from receipt `id` to the parsed receipt object. Returns an empty dict if the file does not exist.
    
    Raises:
        ValueError: If a non-blank line is invalid JSON, not an object, missing/empty `id`, has an invalid `task_id` (must match TASK_ID), or contains a duplicate `id`. Error messages are prefixed with "receipts.jsonl:<line>:".
    """
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
                raise ValueError(f"receipts.jsonl:{line_number}: duplicate id")
            receipts[receipt_id] = receipt
    return receipts


def validate_done_receipt_schema(task: dict[str, Any], receipt: dict[str, Any]) -> list[str]:
    """
    Validate fields required in a "done" receipt according to the task's type.
    
    For tasks with type "worker" this requires a non-empty `summary` string, a
    non-empty `changed_files` list, and a non-empty `commands` list. For tasks with
    type "judge" this requires a non-empty `decision` string, a non-empty `summary`
    string, and a non-empty `evidence` list. Each missing or invalid field produces
    one error message prefixed with the task's id (or "task" if id is absent).
    
    Parameters:
        task (dict): Task mapping containing at least the keys `"id"` and `"type"`.
        receipt (dict): Receipt mapping to validate for required fields.
    
    Returns:
        list[str]: List of error messages for missing or invalid fields; empty if the
        receipt satisfies the requirements for the task's type.
    """
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
    """
    Validate that a goal directory contains the expected top-level entries and correct types.
    
    Performs these checks:
    - Reports unexpected top-level entries (allowed: goal.md, state.yaml, receipts.jsonl, notes).
    - Ensures goal.md and state.yaml are present and are files.
    - Ensures notes is present and is a directory.
    - Reports any missing required entries.
    
    Returns:
        errors (list[str]): A list of error messages describing layout or type problems; empty if the directory is valid.
    """
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
    """
    Validate the `goal` section of a parsed state mapping and collect semantic errors.
    
    Checks that `state["goal"]` is a mapping and enforces constraints on fields such as
    `status`, `native_objective`, `native_status`, `native_goal_id`, numeric counters,
    `token_budget`, and timestamp strings. Returns any validation errors and the
    string value of `goal.status` when present and a string.
    
    Parameters:
    	state (dict[str, Any]): Parsed top-level state mapping from `state.yaml`.
    
    Returns:
    	errors (list[str]): List of human-readable validation error messages (empty if valid).
    	goal_status (str | None): The string value of `state["goal"]["status"]` if present and a string, otherwise `None`.
    """
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
    """
    Append an error to `errors` when a mapping's specified field is missing or not a non-empty string.
    
    Parameters:
        mapping (dict[str, Any]): Mapping to check for the field.
        field (str): Key name to validate within `mapping`.
        label (str): Prefix used in the error message (reported as "<label>.<field> must be a non-empty string").
        errors (list[str]): List that will receive the error message when validation fails.
    """
    value = mapping.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}.{field} must be a non-empty string")


def require_non_empty_string_list(mapping: dict[str, Any], field: str, label: str, errors: list[str]) -> None:
    """
    Append an error if the specified mapping field is not a non-empty list of non-empty strings.
    
    Parameters:
    	mapping (dict[str, Any]): Mapping to validate.
    	field (str): Key in `mapping` whose value should be validated.
    	label (str): Prefix used in the error message (typically the section name).
    	errors (list[str]): Mutable list to which an error message will be appended when validation fails.
    """
    values = mapping.get(field)
    if not isinstance(values, list) or not values or not all(isinstance(item, str) and item.strip() for item in values):
        errors.append(f"{label}.{field} must be a non-empty list of strings")


def validate_completion_contract(state: dict[str, Any]) -> list[str]:
    """
    Validate the `completion_contract` section of the parsed state mapping.
    
    Checks that `state["completion_contract"]` is a mapping and that it contains the required non-empty fields:
    - `outcome` (non-empty string)
    - `verification_surface` (non-empty list of strings)
    - `constraints` (non-empty list of strings)
    - `boundaries` (non-empty list of strings)
    - `iteration_policy` (non-empty string)
    - `blocked_stop_condition` (non-empty string)
    
    Parameters:
        state (dict[str, Any]): Parsed state mapping from `state.yaml`.
    
    Returns:
        list[str]: A list of validation error messages. Empty if `completion_contract` is present, a mapping, and all required fields are valid. If `completion_contract` is missing or not a mapping, returns `["completion_contract must be a mapping"]`.
    """
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
    """
    Validate the optional `continuation_gate` section of the state mapping.
    
    Checks that `continuation_gate`, if present, is a mapping and that its fields belong to the allowed enumerations:
    - `native_status` must be one of the continuation native status values.
    - `thread_idle` and `goal_active` must be one of the gate status values.
    - `queued_user_input` and `pending_work` must be one of the queue status values.
    - `auto_continue_allowed` must be one of the auto-continue status values.
    
    Parameters:
        state (dict[str, Any]): The parsed state mapping from `state.yaml`.
    
    Returns:
        list[str]: A list of validation error messages; empty if `continuation_gate` is absent or valid.
    """
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
    """
    Validate the optional "claims" section of a goal board state mapping.
    
    Checks that when present `state["claims"]` is a list of claim mappings and that each claim:
    - has a unique `id` matching the `CLAIM_ID` pattern,
    - has a non-empty `claim` string,
    - has a non-empty `evidence_surface` list of strings,
    - has a `route` value in the allowed claim routes,
    - has a `status` value in the allowed claim statuses,
    - has a non-empty `remaining_uncertainty` list of strings.
    
    Parameters:
        state (dict): The parsed board state (typically loaded from state.yaml).
    
    Returns:
        list[str]: A list of validation error messages; empty if no problems were found.
    """
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


def validate_task(
    task: dict[str, Any],
    index: int,
    ids: set[str],
    receipts: dict[str, dict[str, Any]],
) -> tuple[list[str], bool]:
    """
    Validate a single task mapping and report schema and cross-reference errors.
    
    Parameters:
        task (dict[str, Any]): The task object to validate.
        index (int): One-based index of the task in the tasks list (used in error messages).
        ids (set[str]): Set of already-seen task IDs; this function will add the task's id if valid.
        receipts (dict[str, dict[str, Any]]): Mapping of receipt id to receipt objects for cross-checks.
    
    Returns:
        tuple[list[str], bool]: A pair where the first element is a list of validation error messages
        (empty if the task is valid), and the second element is `True` if the task's status is "active",
        `False` otherwise.
    """
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
    """
    Validate the tasks list, ensure per-task receipt consistency, and enforce goal-level task rules.
    
    Checks that `tasks` is a non-empty list, runs per-task validation (via validate_task), collects active tasks, and enforces:
    - For non-done goals: there must be exactly one active task unless multiple active worker tasks are allowed and have disjoint `allowed_files` according to `rules`.
    - For done goals: there must be no active tasks and there must exist at least one receipt from a Judge or PM with `decision == "complete"` referencing an existing task.
    
    Parameters:
        tasks (Any): The parsed `tasks` value from state; expected to be a non-empty list of task mappings.
        receipts (dict[str, dict[str, Any]]): Mapping of receipt id to receipt objects for cross-checking `receipt_id` and receipt fields.
        rules (dict[str, Any]): Goal-level rules that may alter active-task constraints (e.g., parallel worker allowances).
        goal_status (str | None): The goal's status string (e.g., "done") used to apply goal-level validations.
    
    Returns:
        list[str]: A list of validation error messages; empty if no errors were found.
    """
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
    """
    Validate a Goal Governor board directory and return any validation errors.
    
    Performs the full board validation pass: checks the directory layout, parses and validates
    state.yaml (including version and goal section), validates completion contract,
    continuation gate, and claims, loads and validates receipts.jsonl, and validates tasks
    against receipts and board-level rules.
    
    Parameters:
    	goal_dir (Path): Path to the goal board directory to validate.
    
    Returns:
    	errors (list[str]): A list of validation error messages; an empty list indicates the board is valid.
    """
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
    """
    Validate a Goal Governor goal directory specified on the command-line and return an exit code.
    
    If the argument count is incorrect this prints a usage failure and returns 1. Runs full board validation for the directory path given as argv[1]; if validation errors are found it prints each error prefixed with "FAIL: " to stderr and returns 1. On successful validation it prints "PASS: goal board is valid" to stdout and returns 0.
    
    Returns:
        int: 0 on successful validation, 1 on validation failure or incorrect usage.
    """
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
