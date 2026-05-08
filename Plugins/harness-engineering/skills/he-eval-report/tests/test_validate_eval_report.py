from pathlib import Path
import sys


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from validate_eval_report import validate  # noqa: E402


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
