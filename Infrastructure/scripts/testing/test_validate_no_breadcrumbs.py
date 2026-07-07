from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "validation-and-linting"
    / "validate_no_breadcrumbs.py"
)
SPEC = importlib.util.spec_from_file_location("validate_no_breadcrumbs", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
validate_no_breadcrumbs = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validate_no_breadcrumbs
SPEC.loader.exec_module(validate_no_breadcrumbs)


def scan(rel_path: str, text: str):
    return validate_no_breadcrumbs._scan_text(rel_path, text)


def test_docs_reject_obvious_breadcrumbs() -> None:
    findings = scan("Docs/agents/example.md", "Ship this later. TODO: wire it later.\n")

    assert len(findings) == 1
    assert findings[0].code == "todo-marker"


def test_docs_skip_fenced_examples_and_blockquotes() -> None:
    fence = chr(96) * 3
    findings = scan(
        "Docs/agents/example.md",
        f"> TODO: quoted external review text\n{fence}python\n# TODO: example fixture\n{fence}\n",
    )

    assert findings == []


def test_code_scans_comments_not_string_literals() -> None:
    findings = scan(
        "Infrastructure/scripts/example.py",
        "message = 'TODO is quoted user input'\n# FIXME: replace this\n",
    )

    assert len(findings) == 1
    assert findings[0].line == 2


def test_allow_marker_suppresses_intentional_policy_example() -> None:
    findings = scan(
        "Docs/agents/example.md",
        "Use TODO here only as an intentional breadcrumb example.\n",
    )

    assert findings == []


def test_historical_receipts_are_out_of_scope() -> None:
    assert not validate_no_breadcrumbs.should_scan_path(
        ".harness/reports/project-pm/example.md"
    )
