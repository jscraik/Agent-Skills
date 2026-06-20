from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validation-and-linting" / "validate_steering_uptake.py"
SPEC = importlib.util.spec_from_file_location("validate_steering_uptake", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
validate_steering_uptake = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validate_steering_uptake
SPEC.loader.exec_module(validate_steering_uptake)


_VALID_DOC = (
    "# High-Signal Steering Feedback\n\n"
    "## Stop Rule\n\n"
    "## Proof Before Proceeding\n\n"
    "## Scope Closure Authority\n\n"
    "full implementation\n"
    "explicitly approves that scope change\n"
    "claim-vs-evidence closeout check\n"
    "closeout caveat\n"
    "changes future behavior\n\n"
    "## Uptake Loop\n\n"
    "local or systemic\n"
    "sibling patterns\n"
    "API philosophy\n"
    "error-handling doctrine\n"
    "runtime safety assumption\n"
    "operational standard\n"
    "lint rule\n"
    "schema constraint\n"
    "style rule\n"
    "CI check\n"
    "shared utility\n"
    "reusable abstraction\n"
    "architectural policy\n"
    "not doing what Jamie wants\n"
    "feedback signal\n"
    "root operational failure\n"
    "durable system improvement\n"
    "explicit remaining proof\n"
    "known taxonomy values\n"
    "## Required Evidence\n\n"
    "validate_steering_uptake.py\n"
)
_VALID_LEDGER = (
    "# Steering Uptake Ledger\n\n"
    "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
    "| --- | --- | --- | --- | --- | --- | --- |\n"
    "| 2026-05-19 | steering trigger | repeated behavior | missing guard. Category: missing guardrails. | Docs/agents/19.md Improvement type: validator. | python3 validate_steering_uptake.py --json | validated |\n"
)
_VALID_README = "[19-high-signal-steering-feedback](/Docs/agents/19-high-signal-steering-feedback.md)\n"
_VALID_AGENTS = (
    "Use [High-Signal Steering Feedback](./Docs/agents/19-high-signal-steering-feedback.md) "
    "by opening and reading it in the current turn before continuing ordinary implementation or PR work. "
    "Record uptake in `.harness/quality/steering-uptake.md`; validate with "
    "`python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json`.\n"
)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _make_valid_root(tmp_path: Path) -> Path:
    write(tmp_path / "Docs/agents/19-high-signal-steering-feedback.md", _VALID_DOC)
    write(tmp_path / ".harness/quality/steering-uptake.md", _VALID_LEDGER)
    write(tmp_path / "Docs/agents/README.md", _VALID_README)
    write(tmp_path / "AGENTS.md", _VALID_AGENTS)
    return tmp_path


# ---------------------------------------------------------------------------
# _table_rows edge cases
# ---------------------------------------------------------------------------


def test_table_rows_empty_content() -> None:
    headers, rows = validate_steering_uptake._table_rows("")
    assert headers == []
    assert rows == []


def test_table_rows_only_header_and_separator() -> None:
    text = "| A | B | C |\n| --- | --- | --- |\n"
    headers, rows = validate_steering_uptake._table_rows(text)
    assert headers == ["A", "B", "C"]
    assert rows == []


def test_table_rows_with_data_row() -> None:
    text = "| A | B | C |\n| --- | --- | --- |\n| 1 | 2 | 3 |\n"
    headers, rows = validate_steering_uptake._table_rows(text)
    assert headers == ["A", "B", "C"]
    assert rows == [["1", "2", "3"]]


def test_table_rows_accepts_table_without_edge_pipes() -> None:
    text = "A | B | C\n--- | --- | ---\n1 | 2 | 3\n"
    headers, rows = validate_steering_uptake._table_rows(text)
    assert headers == ["A", "B", "C"]
    assert rows == [["1", "2", "3"]]


def test_table_rows_rejects_missing_separator_before_data() -> None:
    text = "| A | B | C |\n| 1 | 2 | 3 |\n| 4 | 5 | 6 |\n"
    headers, rows = validate_steering_uptake._table_rows(text)
    assert headers == ["A", "B", "C"]
    assert rows == []


def test_table_rows_allows_escaped_inline_pipe_in_cell() -> None:
    text = (
        "| A | B | C |\n"
        "| --- | --- | --- |\n"
        "| 1 | value \\| fallback | 3 |\n"
    )
    headers, rows = validate_steering_uptake._table_rows(text)
    assert headers == ["A", "B", "C"]
    assert rows == [["1", "value | fallback", "3"]]


def test_table_rows_fewer_than_3_lines() -> None:
    text = "| A | B |\n"
    headers, rows = validate_steering_uptake._table_rows(text)
    assert headers == []
    assert rows == []


def test_table_rows_ignores_non_table_lines() -> None:
    text = "# Heading\n\nsome prose\n\n| A | B |\n| --- | --- |\n| 1 | 2 |\n"
    headers, rows = validate_steering_uptake._table_rows(text)
    assert headers == ["A", "B"]
    assert rows == [["1", "2"]]


def test_table_rows_skips_pipe_prose_before_valid_table() -> None:
    text = "# Heading\n\nrun cmd1 | cmd2 before editing\n\nA | B\n--- | ---\n1 | 2\n"
    headers, rows = validate_steering_uptake._table_rows(text)
    assert headers == ["A", "B"]
    assert rows == [["1", "2"]]


def test_validate_allows_escaped_inline_pipe_in_ledger_cell(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-05-19 | retry \\| fallback | repeated behavior | missing guard. Category: missing guardrails. | Docs/agents/19.md Improvement type: validator. | python3 validate_steering_uptake.py --json | validated |\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    assert {finding.code for finding in findings} == set()


def test_validate_accepts_ledger_table_without_edge_pipes(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status\n"
        "--- | --- | --- | --- | --- | --- | ---\n"
        "2026-05-19 | repeated warning | missed live thread | parser only accepted edge pipes. Category: weak validation. | validate no-edge-pipe ledgers. Improvement type: validator. | python3 validate_steering_uptake.py --json | validated\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    assert findings == []


def test_validate_rejects_missing_ledger_separator_row(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| 2026-05-19 | trigger | pattern | mechanism | guardrail | python3 validate_steering_uptake.py --json | validated |\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    codes = {finding.code for finding in findings}
    assert "STEERING_LEDGER_SEPARATOR" in codes


# ---------------------------------------------------------------------------
# Regression / boundary tests
# ---------------------------------------------------------------------------


def test_multiple_rows_partial_failures_all_reported(tmp_path: Path) -> None:
    """All invalid rows are reported, not just the first."""
    _make_valid_root(tmp_path)
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-05-19 | trigger | pattern | mechanism | guardrail | python3 validate_steering_uptake.py --json | validated |\n"
        "| 2026-05-20 | trigger2 | pattern2 | mechanism2 | guardrail2 | not run | validated |\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    weak_findings = [f for f in findings if f.code == "STEERING_LEDGER_VALIDATION_WEAK"]
    assert len(weak_findings) == 1
    assert "Row 2" in weak_findings[0].message


def test_finding_path_is_relative(tmp_path: Path) -> None:
    """Finding paths should be relative strings, not absolute."""
    _make_valid_root(tmp_path)
    (tmp_path / "Docs/agents/README.md").unlink()

    findings = validate_steering_uptake.validate(tmp_path)

    assert any(f.code == "AGENT_DOC_INDEX_MISSING" for f in findings)
    assert all(not f.path.startswith("/") for f in findings)
    assert any(f.path == "Docs/agents/README.md" for f in findings)


def test_case_insensitive_weak_field_detection(tmp_path: Path) -> None:
    """Weak value detection is case-insensitive for 'none', 'n/a', 'todo'."""
    _make_valid_root(tmp_path)
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-05-19 | trigger | pattern | NONE | guardrail | python3 validate_steering_uptake.py --json | validated |\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    field_empty = [f for f in findings if f.code == "STEERING_LEDGER_FIELD_EMPTY"]
    assert any("Mechanism" in f.message for f in field_empty)

