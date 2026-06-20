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
    """
    Write UTF-8 text to the given file path, creating any missing parent directories.

    Parameters:
        path (Path): Destination file path to write to. Parent directories will be created if they do not exist.
        text (str): Text content to write; existing file content will be overwritten.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _make_valid_root(tmp_path: Path) -> Path:
    """
    Create and populate a temporary repository root containing the valid steering-uptake surfaces.

    Writes three files into the given directory:
    - Docs/agents/19-high-signal-steering-feedback.md with predefined steering document content.
    - .harness/quality/steering-uptake.md with a valid ledger table.
    - Docs/agents/README.md with an index link to the steering document.

    Parameters:
        tmp_path (Path): Directory path to populate.

    Returns:
        Path: The same `tmp_path` that was populated.
    """
    write(tmp_path / "Docs/agents/19-high-signal-steering-feedback.md", _VALID_DOC)
    write(tmp_path / ".harness/quality/steering-uptake.md", _VALID_LEDGER)
    write(tmp_path / "Docs/agents/README.md", _VALID_README)
    write(tmp_path / "AGENTS.md", _VALID_AGENTS)
    return tmp_path


def test_validate_current_repo_surfaces() -> None:
    findings = validate_steering_uptake.validate()
    assert findings == []


def test_rejects_missing_ledger_row(tmp_path: Path) -> None:
    """
    Verify that validation reports STEERING_LEDGER_EMPTY when the ledger contains only headers and no data rows.

    Creates a minimal steering feedback document, a ledger file containing only the header and separator (no data rows), and a README linking the steering doc; runs validate_steering_uptake.validate(tmp_path) and asserts at least one finding has code "STEERING_LEDGER_EMPTY".

    Parameters:
        tmp_path (Path): Temporary filesystem root used as the repository root for the test.
    """
    write(
        tmp_path / "Docs/agents/19-high-signal-steering-feedback.md",
        "# High-Signal Steering Feedback\n\n## Stop Rule\n\n## Uptake Loop\n\n## Required Evidence\n\nvalidate_steering_uptake.py\n",
    )
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n| --- | --- | --- | --- | --- | --- | --- |\n",
    )
    write(
        tmp_path / "Docs/agents/README.md",
        "[19-high-signal-steering-feedback](/Docs/agents/19-high-signal-steering-feedback.md)\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    assert any(finding.code == "STEERING_LEDGER_EMPTY" for finding in findings)


def test_rejects_validated_row_without_validator_evidence(tmp_path: Path) -> None:
    write(
        tmp_path / "Docs/agents/19-high-signal-steering-feedback.md",
        "# High-Signal Steering Feedback\n\n## Stop Rule\n\n## Uptake Loop\n\n## Required Evidence\n\nvalidate_steering_uptake.py\n",
    )
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-05-19 | steering | repeated feedback | missing guard | Docs/agents/19-high-signal-steering-feedback.md | not run | validated |\n",
    )
    write(
        tmp_path / "Docs/agents/README.md",
        "[19-high-signal-steering-feedback](/Docs/agents/19-high-signal-steering-feedback.md)\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    assert any(finding.code == "STEERING_LEDGER_VALIDATION_WEAK" for finding in findings)


# ---------------------------------------------------------------------------
# Missing file tests
# ---------------------------------------------------------------------------


def test_rejects_missing_steering_doc(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    (tmp_path / "Docs/agents/19-high-signal-steering-feedback.md").unlink()

    findings = validate_steering_uptake.validate(tmp_path)

    codes = {f.code for f in findings}
    assert "STEERING_DOC_MISSING" in codes


def test_rejects_missing_ledger(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    (tmp_path / ".harness/quality/steering-uptake.md").unlink()

    findings = validate_steering_uptake.validate(tmp_path)

    codes = {f.code for f in findings}
    assert "STEERING_LEDGER_MISSING" in codes


def test_rejects_missing_readme(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    (tmp_path / "Docs/agents/README.md").unlink()

    findings = validate_steering_uptake.validate(tmp_path)

    codes = {f.code for f in findings}
    assert "AGENT_DOC_INDEX_MISSING" in codes


def test_rejects_missing_agents_steering_routing(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    (tmp_path / "AGENTS.md").unlink()

    findings = validate_steering_uptake.validate(tmp_path)

    codes = {f.code for f in findings}
    assert "AGENTS_STEERING_ROUTING_MISSING" in codes


def test_rejects_agents_without_same_turn_read_rule(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / "AGENTS.md",
        "Use [High-Signal Steering Feedback](./Docs/agents/19-high-signal-steering-feedback.md). "
        "Record uptake in `.harness/quality/steering-uptake.md`; validate with "
        "`python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json`.\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    weak = [finding for finding in findings if finding.code == "AGENTS_STEERING_ROUTING_WEAK"]
    assert any("opening and reading it in the current turn" in finding.message for finding in weak)


# ---------------------------------------------------------------------------
# Steering doc content tests
# ---------------------------------------------------------------------------


def test_rejects_doc_missing_stop_rule(tmp_path: Path) -> None:
    """
    Verifies that a STEERING_DOC_INCOMPLETE finding is produced when the steering doc omits the "Stop Rule" section.

    Sets up a valid repository surface, rewrites the steering document without the "Stop Rule" section, runs the validator, and asserts at least one finding with code `STEERING_DOC_INCOMPLETE` contains "Stop Rule" in its message.

    Parameters:
        tmp_path (Path): pytest temporary directory used as the repository root.
    """
    _make_valid_root(tmp_path)
    write(
        tmp_path / "Docs/agents/19-high-signal-steering-feedback.md",
        "## Uptake Loop\n\n## Required Evidence\n\nvalidate_steering_uptake.py\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    incomplete = [f for f in findings if f.code == "STEERING_DOC_INCOMPLETE"]
    assert any("Stop Rule" in f.message for f in incomplete)


def test_rejects_doc_missing_scope_closure_authority(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / "Docs/agents/19-high-signal-steering-feedback.md",
        "# High-Signal Steering Feedback\n\n"
        "## Stop Rule\n\n"
        "## Proof Before Proceeding\n\n"
        "## Uptake Loop\n\n"
        "## Required Evidence\n\n"
        "validate_steering_uptake.py\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    incomplete = [f for f in findings if f.code == "STEERING_DOC_INCOMPLETE"]
    assert any("Scope Closure Authority" in f.message for f in incomplete)


def test_rejects_doc_missing_closeout_caveat_rule(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / "Docs/agents/19-high-signal-steering-feedback.md",
        "# High-Signal Steering Feedback\n\n"
        "## Stop Rule\n\n"
        "## Proof Before Proceeding\n\n"
        "## Scope Closure Authority\n\n"
        "full implementation\n"
        "explicitly approves that scope change\n"
        "claim-vs-evidence closeout check\n"
        "changes future behavior\n\n"
        "## Uptake Loop\n\n"
        "## Required Evidence\n\n"
        "validate_steering_uptake.py\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    incomplete = [f for f in findings if f.code == "STEERING_DOC_INCOMPLETE"]
    assert any("closeout caveat" in f.message for f in incomplete)


def test_rejects_doc_missing_changed_future_behavior_rule(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / "Docs/agents/19-high-signal-steering-feedback.md",
        "# High-Signal Steering Feedback\n\n"
        "## Stop Rule\n\n"
        "## Proof Before Proceeding\n\n"
        "## Scope Closure Authority\n\n"
        "full implementation\n"
        "explicitly approves that scope change\n"
        "claim-vs-evidence closeout check\n"
        "closeout caveat\n\n"
        "## Uptake Loop\n\n"
        "## Required Evidence\n\n"
        "validate_steering_uptake.py\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    incomplete = [f for f in findings if f.code == "STEERING_DOC_INCOMPLETE"]
    assert any("changes future behavior" in f.message for f in incomplete)


def test_rejects_doc_missing_uptake_loop(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / "Docs/agents/19-high-signal-steering-feedback.md",
        "## Stop Rule\n\n## Required Evidence\n\nvalidate_steering_uptake.py\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    incomplete = [f for f in findings if f.code == "STEERING_DOC_INCOMPLETE"]
    assert any("Uptake Loop" in f.message for f in incomplete)


def test_rejects_doc_missing_systemic_feedback_contract(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / "Docs/agents/19-high-signal-steering-feedback.md",
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
        "## Required Evidence\n\n"
        "validate_steering_uptake.py\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    incomplete = [f for f in findings if f.code == "STEERING_DOC_INCOMPLETE"]
    missing_messages = {f.message for f in incomplete}
    assert any("local or systemic" in message for message in missing_messages)
    assert any("not doing what Jamie wants" in message for message in missing_messages)
    assert any("feedback signal" in message for message in missing_messages)
    assert any("root operational failure" in message for message in missing_messages)


def test_rejects_doc_missing_required_evidence(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / "Docs/agents/19-high-signal-steering-feedback.md",
        "## Stop Rule\n\n## Uptake Loop\n\nvalidate_steering_uptake.py\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    incomplete = [f for f in findings if f.code == "STEERING_DOC_INCOMPLETE"]
    assert any("Required Evidence" in f.message for f in incomplete)


def test_rejects_doc_missing_validator_script_reference(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / "Docs/agents/19-high-signal-steering-feedback.md",
        "## Stop Rule\n\n## Uptake Loop\n\n## Required Evidence\n\nsome other tool\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    incomplete = [f for f in findings if f.code == "STEERING_DOC_INCOMPLETE"]
    assert any("validate_steering_uptake.py" in f.message for f in incomplete)


# ---------------------------------------------------------------------------
# Ledger structure tests
# ---------------------------------------------------------------------------


def test_rejects_wrong_ledger_headers(tmp_path: Path) -> None:
    """
    Verifies that a ledger file with incorrect table headers is flagged.

    Writes a steering ledger containing the wrong header row and asserts that validation reports a finding with code `STEERING_LEDGER_HEADERS`.
    """
    _make_valid_root(tmp_path)
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Ledger\n\n"
        "| Date | Note | Status |\n"
        "| --- | --- | --- |\n"
        "| 2026-05-19 | test | open |\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    codes = {f.code for f in findings}
    assert "STEERING_LEDGER_HEADERS" in codes


def test_rejects_row_with_too_few_cells(tmp_path: Path) -> None:
    """
    Verifies that a ledger data row with too few table cells is reported as a row-width error.

    Writes a steering ledger containing a data row with fewer columns than the required table header, runs the validator, and asserts that at least one finding has the code "STEERING_LEDGER_ROW_WIDTH".

    Parameters:
        tmp_path (Path): Temporary filesystem path used as the repository root for the test.
    """
    _make_valid_root(tmp_path)
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-05-19 | trigger | pattern |\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    codes = {f.code for f in findings}
    assert "STEERING_LEDGER_ROW_WIDTH" in codes


def test_rejects_row_with_too_many_cells(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-05-19 | t | p | m | g | v | open | extra-cell |\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    codes = {f.code for f in findings}
    assert "STEERING_LEDGER_ROW_WIDTH" in codes


def test_rejects_row_with_empty_field(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-05-19 | trigger |  | mechanism | guardrail | python3 validate_steering_uptake.py --json | validated |\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    field_empty = [f for f in findings if f.code == "STEERING_LEDGER_FIELD_EMPTY"]
    assert any("Failure pattern" in f.message for f in field_empty)


def test_rejects_row_with_none_value(tmp_path: Path) -> None:
    """
    Verifies that a ledger row with the Mechanism value set to 'none' is reported as a missing/empty field.

    Creates a steering ledger containing a row where the "Mechanism" cell is the literal `none` and asserts that validation produces at least one finding with code `STEERING_LEDGER_FIELD_EMPTY` whose message references "Mechanism".

    Parameters:
        tmp_path (Path): Temporary filesystem path used as the repository root for the test.
    """
    _make_valid_root(tmp_path)
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-05-19 | trigger | pattern | none | guardrail | python3 validate_steering_uptake.py --json | validated |\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    field_empty = [f for f in findings if f.code == "STEERING_LEDGER_FIELD_EMPTY"]
    assert any("Mechanism" in f.message for f in field_empty)


def test_rejects_row_with_na_value(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-05-19 | trigger | pattern | mechanism | n/a | python3 validate_steering_uptake.py --json | validated |\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    field_empty = [f for f in findings if f.code == "STEERING_LEDGER_FIELD_EMPTY"]
    assert any("Durable guardrail" in f.message for f in field_empty)


def test_rejects_row_with_todo_value(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-05-19 | trigger | pattern | mechanism | guardrail | TODO | validated |\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    field_empty = [f for f in findings if f.code == "STEERING_LEDGER_FIELD_EMPTY"]
    assert any("Validation" in f.message for f in field_empty)


def test_rejects_row_with_invalid_status(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-05-19 | trigger | pattern | mechanism | guardrail | python3 validate_steering_uptake.py --json | done |\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    codes = {f.code for f in findings}
    assert "STEERING_LEDGER_STATUS" in codes


def test_rejects_unknown_failure_category(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-05-19 | trigger | pattern | mechanism. Category: process vibes. | guardrail Improvement type: validator. | python3 validate_steering_uptake.py --json | validated |\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    codes = {f.code for f in findings}
    assert "STEERING_LEDGER_CATEGORY_UNKNOWN" in codes


def test_rejects_unknown_improvement_type(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-05-19 | trigger | pattern | mechanism. Category: missing guardrails. | guardrail Improvement type: nice reminder. | python3 validate_steering_uptake.py --json | validated |\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    codes = {f.code for f in findings}
    assert "STEERING_LEDGER_IMPROVEMENT_TYPE_UNKNOWN" in codes


def test_rejects_readme_without_steering_doc_link(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(tmp_path / "Docs/agents/README.md", "# Agent Docs\n\nNo link here.\n")

    findings = validate_steering_uptake.validate(tmp_path)

    codes = {f.code for f in findings}
    assert "STEERING_DOC_NOT_INDEXED" in codes


def test_rejects_readme_plain_text_steering_doc_mention(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / "Docs/agents/README.md",
        "# Agent Docs\n\nMention 19-high-signal-steering-feedback without a link.\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    codes = {f.code for f in findings}
    assert "STEERING_DOC_NOT_INDEXED" in codes


def test_accepts_markdown_steering_doc_link(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)

    findings = validate_steering_uptake.validate(tmp_path)

    codes = {f.code for f in findings}
    assert "STEERING_DOC_NOT_INDEXED" not in codes


# ---------------------------------------------------------------------------
# Valid status variants
# ---------------------------------------------------------------------------


def test_accepts_open_status_row_with_remaining_proof(tmp_path: Path) -> None:
    """
    Verify that a ledger row with Status 'open' is accepted when it names remaining proof.

    Creates a valid repository root, writes a ledger with a single row whose `Status` is `open`,
    runs the validator, and asserts there are no findings with codes `STEERING_LEDGER_STATUS`
    or `STEERING_LEDGER_VALIDATION_WEAK`.
    """
    _make_valid_root(tmp_path)
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-05-19 | trigger | pattern | mechanism. Category: missing guardrails. | guardrail Improvement type: validator. | command to run; next proof: rerun the production gate | open |\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    status_findings = [
        f for f in findings
        if f.code in {"STEERING_LEDGER_STATUS", "STEERING_LEDGER_VALIDATION_WEAK", "STEERING_LEDGER_OPEN_UNCLEAR"}
    ]
    assert status_findings == []


def test_accepts_open_status_row_with_documented_hyphenated_marker(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-05-19 | trigger | pattern | mechanism. Category: missing guardrails. | guardrail Improvement type: validator. | command to run; next-proof: rerun the production gate | open |\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    assert not any(finding.code == "STEERING_LEDGER_OPEN_UNCLEAR" for finding in findings)


def test_rejects_open_status_row_without_remaining_proof(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-05-19 | trigger | pattern | mechanism. Category: missing guardrails. | guardrail Improvement type: validator. | command to run | open |\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    assert any(finding.code == "STEERING_LEDGER_OPEN_UNCLEAR" for finding in findings)


def test_accepts_blocked_status_row(tmp_path: Path) -> None:
    """
    Verifies that a ledger row with a 'blocked' status is treated as valid.

    Creates a valid repository layout and overwrites the ledger with a single row where the
    Status cell is `blocked` (and the Validation cell contains a blocked reason), then
    asserts no findings are produced for status or weak validation (`STEERING_LEDGER_STATUS`,
    `STEERING_LEDGER_VALIDATION_WEAK`).
    """
    _make_valid_root(tmp_path)
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-05-19 | trigger | pattern | mechanism | guardrail | blocked: reason | blocked |\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    status_findings = [f for f in findings if f.code in {"STEERING_LEDGER_STATUS", "STEERING_LEDGER_VALIDATION_WEAK"}]
    assert status_findings == []


def test_accepts_validated_row_with_validator_evidence(tmp_path: Path) -> None:
    _make_valid_root(tmp_path)
    # _make_valid_root already has a validated row with validate_steering_uptake.py in Validation

    findings = validate_steering_uptake.validate(tmp_path)

    assert findings == []


# ---------------------------------------------------------------------------
# main() function tests
# ---------------------------------------------------------------------------


def test_main_returns_zero_on_pass() -> None:
    # Real repo surfaces are valid; main() with no args should pass.
    exit_code = validate_steering_uptake.main([])
    assert exit_code == 0


def test_main_returns_one_on_failure(monkeypatch) -> None:
    # Stub validate() to return a synthetic finding so main() sees a failure.
    """
    Verify that main() signals failure when validation yields a finding.

    Replaces the module's `validate()` with a stub that returns a single synthetic
    `Finding` and asserts that `main([])` returns exit code 1.
    """
    stub_finding = validate_steering_uptake.Finding(
        code="STEERING_DOC_MISSING",
        message="Test finding",
        path="Docs/agents/19-high-signal-steering-feedback.md",
    )
    monkeypatch.setattr(validate_steering_uptake, "validate", lambda: [stub_finding])

    exit_code = validate_steering_uptake.main([])
    assert exit_code == 1


def test_main_json_output_structure(capsys) -> None:
    # Real repo; verify the JSON envelope shape on a passing run.
    """
    Verify that running the CLI with `--json` on the real repository emits a JSON envelope indicating a passing run and containing the expected keys.

    Parses stdout as JSON and asserts that `status` equals `"pass"`, that the keys `findings` and `checked` are present, and that `findings` is an empty list.
    """
    validate_steering_uptake.main(["--json"])

    captured = capsys.readouterr()
    import json
    payload = json.loads(captured.out)
    assert payload["status"] == "pass"
    assert "findings" in payload
    assert "checked" in payload
    assert payload["findings"] == []


def test_main_json_output_on_failure(monkeypatch, capsys) -> None:
    stub_finding = validate_steering_uptake.Finding(
        code="STEERING_DOC_MISSING",
        message="Test finding",
        path="Docs/agents/19-high-signal-steering-feedback.md",
    )
    monkeypatch.setattr(validate_steering_uptake, "validate", lambda: [stub_finding])

    validate_steering_uptake.main(["--json"])

    captured = capsys.readouterr()
    import json
    payload = json.loads(captured.out)
    assert payload["status"] == "fail"
    assert len(payload["findings"]) == 1
    finding = payload["findings"][0]
    assert finding["code"] == "STEERING_DOC_MISSING"
    assert "message" in finding
    assert "path" in finding


def test_main_plain_output_pass(capsys) -> None:
    validate_steering_uptake.main([])

    captured = capsys.readouterr()
    assert captured.out.strip() == "pass"


def test_main_plain_output_fail_includes_finding_code(monkeypatch, capsys) -> None:
    stub_finding = validate_steering_uptake.Finding(
        code="STEERING_LEDGER_MISSING",
        message="Missing ledger",
        path=".harness/quality/steering-uptake.md",
    )
    monkeypatch.setattr(validate_steering_uptake, "validate", lambda: [stub_finding])

    validate_steering_uptake.main([])

    captured = capsys.readouterr()
    assert "fail" in captured.out
    assert "STEERING_LEDGER_MISSING" in captured.out
