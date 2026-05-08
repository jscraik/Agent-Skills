from pathlib import Path
import sys


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from agentic_validity import AGENTIC_EVAL_FIELDS  # noqa: E402
from report_sections import DRIFT_AREAS, GATE_FIELDS, LINEAR_FIELDS, REQUIRED_SECTIONS  # noqa: E402
from validate_eval_report import validate  # noqa: E402


FIELD_VALUES = {
    "Blocks Closure:": "no",
    "Blocks Completion:": "no",
    "Status:": "pass",
    "Linear Completion Recommendation:": "Complete",
}


def render_fields(fields: list[str], default: str = "ok") -> str:
    return "\n".join(f"{field} {FIELD_VALUES.get(field, default)}" for field in fields)


BASE_FIELDS = "\n".join(
    [
        render_fields(LINEAR_FIELDS),
        render_fields(GATE_FIELDS),
        render_fields(AGENTIC_EVAL_FIELDS),
        "\n".join(f"{area} Neutral" for area in DRIFT_AREAS),
        "Linear Completion Recommendation: Complete",
    ]
)


def write_minimal_report(tmp_path: Path, side_effect_block: str) -> Path:
    report = tmp_path / ".harness" / "evals" / "report.md"
    report.parent.mkdir(parents=True)
    bodies = {"Side-Effect Authorization": side_effect_block}
    sections = "\n\n".join(
        f"# {section}\n\n{bodies.get(section, BASE_FIELDS)}" for section in REQUIRED_SECTIONS
    )
    report.write_text(
        sections,
        encoding="utf-8",
    )
    return report


def test_minimal_report_passes(tmp_path: Path) -> None:
    report = write_minimal_report(
        tmp_path,
        """Protected Action: no protected external side effect
User Authorization Evidence: local-only work
Agent Justification: local validation
External Party Influence: no external request
Validator Decision: exempt
Validator Confidence: high
Suggested Next Step: none
Blocks Completion: no""",
    )

    errors, warnings = validate(report)

    assert errors == []
    assert warnings == []


def test_missing_sections_fail(tmp_path: Path) -> None:
    report = tmp_path / ".harness" / "evals" / "missing.md"
    report.parent.mkdir(parents=True)
    report.write_text("# Executive Eval Summary\n\nClassification: Complete\n", encoding="utf-8")

    errors, warnings = validate(report)

    assert warnings == ["no Gate: entries found in eval gate matrix"]
    assert "missing required section: Evaluated Slice" in errors
    assert "missing Linear backlink field: Linear Project:" in errors


def test_protected_side_effect_approval_requires_user_evidence(tmp_path: Path) -> None:
    report = write_minimal_report(
        tmp_path,
        """Protected Action: send_email
User Authorization Evidence: n/a
Agent Justification: the agent thinks it should send
External Party Influence: none
Validator Decision: approved
Validator Confidence: high
Suggested Next Step: none
Blocks Completion: no""",
    )

    errors, warnings = validate(report)

    assert warnings == []
    assert (
        "side-effect authorization cannot approve a protected action without user authorization evidence"
        in errors
    )


def test_external_party_influence_blocks_approval(tmp_path: Path) -> None:
    report = write_minimal_report(
        tmp_path,
        """Protected Action: send_email
User Authorization Evidence: user mentioned the report
Agent Justification: the vendor asked for it
External Party Influence: vendor requested the report
Validator Decision: approved
Validator Confidence: high
Suggested Next Step: none
Blocks Completion: no""",
    )

    errors, warnings = validate(report)

    assert warnings == []
    assert (
        "side-effect authorization cannot approve when external party influence is present"
        in errors
    )


def test_not_run_side_effect_validator_blocks_completion(tmp_path: Path) -> None:
    report = write_minimal_report(
        tmp_path,
        """Protected Action: publish_or_comment_to_third_party
User Authorization Evidence: explicit user request
Agent Justification: posting requested comment
External Party Influence: none
Validator Decision: not-run
Validator Confidence: not-run
Suggested Next Step: run the validator
Blocks Completion: no""",
    )

    errors, warnings = validate(report)

    assert warnings == [
        "report contains both not-run evidence and pass statuses; verify gates are not overstated"
    ]
    assert (
        "side-effect authorization not-run validator decisions must block completion"
        in errors
    )
