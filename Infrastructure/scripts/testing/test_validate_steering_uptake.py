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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_validate_current_repo_surfaces() -> None:
    findings = validate_steering_uptake.validate()
    assert findings == []


def test_rejects_missing_ledger_row(tmp_path: Path) -> None:
    write(
        tmp_path / "Docs/agents/19-high-signal-steering-feedback.md",
        "# High-Signal Steering Feedback\n\n## Stop Rule\n\n## Uptake Loop\n\n## Systemic Scope Check\n\nlocal or systemic\nsibling patterns\nenforceable invariant\n\n## Required Evidence\n\nvalidate_steering_uptake.py\n",
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
        "# High-Signal Steering Feedback\n\n## Stop Rule\n\n## Uptake Loop\n\n## Systemic Scope Check\n\nlocal or systemic\nsibling patterns\nenforceable invariant\n\n## Required Evidence\n\nvalidate_steering_uptake.py\n",
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


def test_rejects_row_without_failure_category(tmp_path: Path) -> None:
    write(
        tmp_path / "Docs/agents/19-high-signal-steering-feedback.md",
        "# High-Signal Steering Feedback\n\n"
        "## Stop Rule\n\n"
        "## Proof Before Proceeding\n\n"
        "## Uptake Loop\n\n"
        "## Failure Categories\n\n"
        "## Durable Improvement Types\n\n"
        "## Systemic Scope Check\n\n"
        "local or systemic\nsibling patterns\nenforceable invariant\nclaim-vs-evidence verification\n\n"
        "## Required Evidence\n\n"
        "validate_steering_uptake.py\n",
    )
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-05-19 | steering | repeated feedback | no category marker | Docs/agents/19-high-signal-steering-feedback.md Improvement type: validator. | validate_steering_uptake.py | validated |\n",
    )
    write(
        tmp_path / "Docs/agents/README.md",
        "[19-high-signal-steering-feedback](/Docs/agents/19-high-signal-steering-feedback.md)\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    assert any(finding.code == "STEERING_LEDGER_CATEGORY_MISSING" for finding in findings)


def test_rejects_row_without_durable_improvement_type(tmp_path: Path) -> None:
    write(
        tmp_path / "Docs/agents/19-high-signal-steering-feedback.md",
        "# High-Signal Steering Feedback\n\n"
        "## Stop Rule\n\n"
        "## Proof Before Proceeding\n\n"
        "## Uptake Loop\n\n"
        "## Failure Categories\n\n"
        "## Durable Improvement Types\n\n"
        "## Systemic Scope Check\n\n"
        "local or systemic\nsibling patterns\nenforceable invariant\nclaim-vs-evidence verification\n\n"
        "## Required Evidence\n\n"
        "validate_steering_uptake.py\n",
    )
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-05-19 | steering | repeated feedback | Category: missing guardrails. | Docs/agents/19-high-signal-steering-feedback.md | validate_steering_uptake.py | validated |\n",
    )
    write(
        tmp_path / "Docs/agents/README.md",
        "[19-high-signal-steering-feedback](/Docs/agents/19-high-signal-steering-feedback.md)\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    assert any(finding.code == "STEERING_LEDGER_IMPROVEMENT_TYPE_MISSING" for finding in findings)


def test_rejects_doc_without_proof_before_normal_work_invariant(tmp_path: Path) -> None:
    write(
        tmp_path / "Docs/agents/19-high-signal-steering-feedback.md",
        "# High-Signal Steering Feedback\n\n"
        "## Stop Rule\n\n"
        "## Proof Before Proceeding\n\n"
        "## Uptake Loop\n\n"
        "## Failure Categories\n\n"
        "## Durable Improvement Types\n\n"
        "## Systemic Scope Check\n\n"
        "local or systemic\nsibling patterns\nenforceable invariant\nclaim-vs-evidence verification\n\n"
        "## Required Evidence\n\n"
        "validate_steering_uptake.py\n",
    )
    write(
        tmp_path / ".harness/quality/steering-uptake.md",
        "# Steering Uptake Ledger\n\n"
        "| Date | Trigger | Failure pattern | Mechanism | Durable guardrail | Validation | Status |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 2026-05-19 | steering | repeated feedback | Category: missing guardrails. | Docs/agents/19-high-signal-steering-feedback.md Improvement type: validator. | validate_steering_uptake.py | validated |\n",
    )
    write(
        tmp_path / "Docs/agents/README.md",
        "[19-high-signal-steering-feedback](/Docs/agents/19-high-signal-steering-feedback.md)\n",
    )

    findings = validate_steering_uptake.validate(tmp_path)

    assert any(
        finding.code == "STEERING_DOC_INCOMPLETE"
        and "Do not resume ordinary implementation" in finding.message
        for finding in findings
    )
