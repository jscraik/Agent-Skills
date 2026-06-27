from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "validate_no_command_handles.py"
)
SPEC = importlib.util.spec_from_file_location("validate_no_command_handles", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
validate_no_command_handles = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validate_no_command_handles
SPEC.loader.exec_module(validate_no_command_handles)


def test_runtime_identifier_placeholder_pattern_rejects_fake_wait_ids() -> None:
    pattern = validate_no_command_handles.RUNTIME_IDENTIFIER_PLACEHOLDER_PATTERN

    assert pattern.search('cell_id: "noop"')
    assert pattern.search("session_id = 'placeholder'")
    assert pattern.search('cell_id: "nonexistent2"')
    assert pattern.search('tool_call_id: "fake"')


def test_runtime_identifier_placeholder_pattern_allows_realistic_runtime_ids() -> None:
    pattern = validate_no_command_handles.RUNTIME_IDENTIFIER_PLACEHOLDER_PATTERN

    assert not pattern.search('cell_id: "cell_019e6a4b159776a9"')
    assert not pattern.search("placeholder identifiers must be rejected")


def test_runtime_placeholder_guard_scans_steering_ledger() -> None:
    assert ".harness/quality/steering-uptake.md" in (
        validate_no_command_handles.RUNTIME_IDENTIFIER_PLACEHOLDER_PATHS
    )
