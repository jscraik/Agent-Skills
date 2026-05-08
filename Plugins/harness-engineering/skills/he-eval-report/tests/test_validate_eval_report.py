from pathlib import Path
import sys


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from report_sections import REQUIRED_SECTIONS  # noqa: E402
from validate_eval_report import validate  # noqa: E402


BASE_FIELDS = """Linear Project: Harness
Linear Milestone: Eval hardening
Linear Parent Issue: JSC-1
Linear Sub-Issues: none
Linear Status Recommendation: Complete
Proof Artifact Links: local

Gate: eval
Expected: pass
Actual: pass
Status: pass
Evidence: command output
Confidence: high
Blocks Closure: no
Required Action: none

Evaluated Capability / Task: authorization validator
Task Validity: task exercises protected side effects
Outcome Validity: blocked actions cannot pass
Trajectory / Transcript Evidence: transcript reviewed
Grader Coverage: deterministic and transcript
Trial Policy: single deterministic run
Pass@k / Pass^k Reporting: not applicable
Authorization Validator: enabled
Saturation / Maintenance Signal: no saturation
Blocks Completion: no
Required Action: none

Architecture Drift: Neutral
Routing Drift: Neutral
Context Drift: Neutral
Governance Drift: Neutral
Agent-Native Drift: Neutral
Moat Drift: Neutral

Linear Completion Recommendation: Complete"""


def write_minimal_report(tmp_path: Path, side_effect_block: str) -> Path:
    report = tmp_path / ".harness" / "evals" / "report.md"
    report.parent.mkdir(parents=True)
    bodies = {
        "Linear Backlink Map": BASE_FIELDS,
        "Eval Gate Matrix": BASE_FIELDS,
        "Agentic Eval Validity": BASE_FIELDS,
        "Drift Validation": BASE_FIELDS,
        "Linear Completion Recommendation": BASE_FIELDS,
        "Side-Effect Authorization": side_effect_block,
    }
    sections = "\n\n".join(
        f"# {section}\n\n{bodies.get(section, 'Checked.')}" for section in REQUIRED_SECTIONS
    )
    report.write_text(
        sections,
        encoding="utf-8",
    )
    return report


def test_template_report_passes_with_path_warning() -> None:
    report = Path(__file__).resolve().parents[1] / "references" / "eval-report-template.md"

    errors, warnings = validate(report)

    assert errors == []
    assert warnings == ["report path is outside .harness/evals/"]


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
