from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_validator() -> ModuleType:
    path = REPO_ROOT / ".github" / "scripts" / "validate_pr_template_body.py"
    spec = importlib.util.spec_from_file_location("validate_pr_template_body", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _template() -> str:
    return (REPO_ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")


def _filled_template_body() -> str:
    validator = _load_validator()
    body = _template()
    body = body.replace("- [ ]", "- [x]")
    body = validator.PLACEHOLDER_RE.sub("repo-relative evidence", body)
    replacements = {
        "describe the observable behavior, issue, or n.a. reason": "validated template contract enforcement",
        "list exact commands run here": "python3 .github/scripts/validate_pr_template_body.py --body-file /tmp/body.md",
        "record pass/fail/blocked for each command here": "pass",
        "pass/fail/n.a. with reason": "pass",
        "pass/fail/blocked (reason)": "pass",
        "pass/fail/blocked (<reason>)": "pass",
        "pass/fail/n.a.": "pass",
        "pass/fail": "pass",
        "Add one-paragraph merge rationale here.": "Template validator keeps PR bodies aligned with the repo contract.",
    }
    for before, after in replacements.items():
        body = body.replace(before, after)
    return body


def test_accepts_filled_canonical_template_shape() -> None:
    validator = _load_validator()

    errors = validator.validate_pr_body(_template(), _filled_template_body())

    assert errors == []


def test_rejects_short_body_that_only_matches_legacy_required_sections() -> None:
    validator = _load_validator()
    body = """## Summary

- Add a focused typed-contract regression.

## Checklist

- [x] Code change is scoped.
- [x] Local validation passed.

## Testing

- pytest -> pass

## Review artifacts

- CodeRabbit: pass

## Notes

Intentionally isolated.
"""

    errors = validator.validate_pr_body(_template(), body)

    assert any("PR body sections must match" in error for error in errors)
    assert "Missing required section: ## Motivation" in errors
    assert "Missing required section: ## Behavior Proof" in errors
    assert "Missing required section: ## Work performed" in errors
    assert any("Checklist item text/order must match" in error for error in errors)


def test_rejects_body_with_template_section_reordered() -> None:
    validator = _load_validator()
    body = _filled_template_body().replace("## Motivation", "## Motivation Renamed", 1)

    errors = validator.validate_pr_body(_template(), body)

    assert any("PR body sections must match" in error for error in errors)
    assert "Missing required section: ## Motivation" in errors


def test_rejects_unresolved_placeholder_tokens() -> None:
    validator = _load_validator()
    body = _filled_template_body().replace("repo-relative evidence", "<link / artifact path / comment ID>", 1)

    errors = validator.validate_pr_body(_template(), body)

    assert "Replace unresolved placeholder token: <link / artifact path / comment ID>" in errors
