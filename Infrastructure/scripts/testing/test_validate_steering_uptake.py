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


def write(path: Path, text: str) -> None:
    """
    Write the given text to the specified file, creating any missing parent directories.
    
    Parameters:
        path (Path): Destination file path to write to. Parent directories will be created if they do not exist.
        text (str): Text content to write to the file (written using UTF-8 encoding).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_validate_current_repo_surfaces() -> None:
    """
    Ensure the steering uptake validator reports no findings for the current repository.
    
    Asserts that calling validate_steering_uptake.validate() returns an empty findings list.
    """
    findings = validate_steering_uptake.validate()
    assert findings == []


def test_rejects_missing_ledger_row(tmp_path: Path) -> None:
    """
    Verifies that validation reports a missing ledger row when the steering uptake ledger contains only the header.
    
    Creates a minimal repository under `tmp_path`: an agent feedback document referencing `validate_steering_uptake.py`, a steering uptake ledger file containing only the header row, and an agents README entry. Runs `validate_steering_uptake.validate(tmp_path)` and asserts that at least one finding has `code == "STEERING_LEDGER_EMPTY"`.
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
    """
    Verifies that a ledger row marked "validated" but lacking validator evidence triggers a weak-validation finding.
    
    Creates a minimal repository under `tmp_path` with an agent feedback document that references `validate_steering_uptake.py`, a steering uptake ledger containing a single data row whose `Validation` column is "not run" while `Status` is "validated", and a README linking the agent document; then runs `validate_steering_uptake.validate()` and asserts that at least one finding has `code == "STEERING_LEDGER_VALIDATION_WEAK"`.
    
    Parameters:
        tmp_path (Path): Temporary filesystem path used as the root of the test repository.
    """
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
