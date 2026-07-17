from __future__ import annotations

import importlib.util
import re
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
    body = validator.FIELD_LINE_RE.sub(
        lambda match: f"- {match.group('label')}: repo-relative evidence"
        if match.group("value").strip() == ""
        else match.group(0),
        body,
    )
    return body


def test_accepts_filled_canonical_template_shape() -> None:
    validator = _load_validator()

    errors = validator.validate_pr_body(_template(), _filled_template_body())

    assert errors == []


def test_template_contract_tracks_release_boundary_section_and_fields() -> None:
    validator = _load_validator()
    contract = validator._template_contract(_template())

    assert contract.sections == [
        "What Problem This Solves",
        "Release Boundary",
        "Why This Change Was Made",
        "Behavior Proof",
        "Work performed",
        "Checklist",
        "Testing",
        "Review artifacts",
        "Notes",
    ]
    assert contract.fields_by_section["Release Boundary"] == [
        "Release mode",
        "Done line",
        "Explicit non-goals",
        "Allowed polish",
        "Deferred polish / follow-up work",
        "Promotion rule",
    ]


def test_rejects_missing_required_field_from_each_templated_section() -> None:
    validator = _load_validator()
    contract = validator._template_contract(_template())
    body = _filled_template_body()

    for section, fields in contract.fields_by_section.items():
        section_block = validator._section_blocks(body)[section]
        for field in fields:
            candidate = body.replace(
                section_block,
                re.sub(
                    rf"^- {re.escape(field)}:.*(?:\n|$)",
                    "",
                    section_block,
                    count=1,
                    flags=re.MULTILINE,
                ),
                1,
            )
            errors = validator.validate_pr_body(_template(), candidate)

            assert f"Missing required field in ## {section}: {field}:" in errors


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
    assert "Missing required section: ## What Problem This Solves" in errors
    assert "Missing required section: ## Why This Change Was Made" in errors
    assert "Missing required section: ## Behavior Proof" in errors
    assert "Missing required section: ## Work performed" in errors
    assert any("Checklist item text/order must match" in error for error in errors)


def test_rejects_body_with_template_section_reordered() -> None:
    validator = _load_validator()
    body = _filled_template_body().replace("## What Problem This Solves", "## What Problem This Solves Renamed", 1)

    errors = validator.validate_pr_body(_template(), body)

    assert any("PR body sections must match" in error for error in errors)
    assert "Missing required section: ## What Problem This Solves" in errors


def test_rejects_unresolved_placeholder_tokens() -> None:
    validator = _load_validator()
    body = _filled_template_body().replace("repo-relative evidence", "<link / artifact path / comment ID>", 1)

    errors = validator.validate_pr_body(_template(), body)

    assert "Replace unresolved placeholder token: <link / artifact path / comment ID>" in errors


def test_rejects_empty_required_fields() -> None:
    validator = _load_validator()
    body = _filled_template_body().replace("- Problem: repo-relative evidence", "- Problem:", 1)

    errors = validator.validate_pr_body(_template(), body)

    assert "Required field in ## Why This Change Was Made is empty: Problem:" in errors


def test_rejects_duplicate_required_fields() -> None:
    validator = _load_validator()
    body = _filled_template_body().replace(
        "- Problem: repo-relative evidence",
        "- Problem: repo-relative evidence\n- Problem: duplicate evidence",
        1,
    )

    errors = validator.validate_pr_body(_template(), body)

    assert "Duplicate field in ## Why This Change Was Made: Problem:" in errors


def test_accepts_required_field_with_nested_continuation_content() -> None:
    validator = _load_validator()
    body = _filled_template_body()
    body = body.replace(
        "- Any other command(s): repo-relative evidence",
        "- Any other command(s):\n  - Command: `pytest` -> pass",
        1,
    )

    errors = validator.validate_pr_body(_template(), body)

    assert errors == []


def test_accepts_unchecked_checklist_item_with_status_marker() -> None:
    body = _filled_template_body()
    body = body.replace(
        "- [x] Any CodeRabbit Semgrep findings were either fixed or explicitly justified when warning-level-only.",
        "- [ ] **(N/A)** Any CodeRabbit Semgrep findings were either fixed or explicitly justified when warning-level-only.",
        1,
    )
    validator = _load_validator()

    errors = validator.validate_pr_body(_template(), body)

    assert errors == []


def test_accepts_angle_tokens_not_owned_by_template() -> None:
    validator = _load_validator()
    body = _filled_template_body().replace(
        "repo-relative evidence",
        "See <https://github.com/jscraik/Agent-Skills/pull/275> for hosted proof.",
        1,
    )

    errors = validator.validate_pr_body(_template(), body)

    assert not any("Replace unresolved placeholder token" in error for error in errors)


def test_accepts_standard_dependabot_body_and_html_markup() -> None:
    validator = _load_validator()
    body = """Bumps the pip group with 1 update in the /Infrastructure/scripts directory: [mcp](https://github.com/modelcontextprotocol/python-sdk).

Updates `mcp` from 1.27.2 to 1.28.1
<details>
<summary>Release notes</summary>
<p><a href="https://github.com/modelcontextprotocol/python-sdk/releases"><code>mcp</code></a></p>
</details>

Dependabot will resolve any conflicts with this PR as long as you don't alter it yourself.

@dependabot show <dependency name> ignore conditions
@dependabot ignore <dependency name> <ignore condition>
"""

    errors = validator.validate_pr_body(_template(), body, author="dependabot[bot]")

    assert errors == []


def test_rejects_dependabot_like_body_without_generated_markers() -> None:
    validator = _load_validator()
    body = """Bumps the pip group with 1 update in the /Infrastructure/scripts directory: [mcp](https://github.com/modelcontextprotocol/python-sdk).

Updates `mcp` from 1.27.2 to 1.28.1
"""

    errors = validator.validate_pr_body(_template(), body)

    assert any("PR body sections must match" in error for error in errors)
    assert any("Missing required section" in error for error in errors)


def test_rejects_dependabot_shape_for_human_author() -> None:
    validator = _load_validator()
    body = """Bumps actions/checkout from 4.2.2 to 4.2.3

Dependabot will resolve any conflicts with this PR as long as you don't alter it yourself.
"""

    errors = validator.validate_pr_body(_template(), body, author="jscraik")

    assert errors == ["Dependabot body exception requires the trusted Dependabot PR author."]


def test_accepts_ungrouped_dependabot_body_for_bot_author() -> None:
    validator = _load_validator()
    body = """Bumps actions/checkout from 4.2.2 to 4.2.3

Dependabot will resolve any conflicts with this PR as long as you don't alter it yourself.
"""

    errors = validator.validate_pr_body(_template(), body, author="dependabot[bot]")

    assert errors == []


def test_rejects_placeholder_nested_inside_safe_html_attribute() -> None:
    validator = _load_validator()
    body = _filled_template_body().replace(
        "repo-relative evidence",
        '<a href="<link / artifact path / comment ID>">proof</a>',
        1,
    )

    errors = validator.validate_pr_body(_template(), body)

    assert 'Replace unresolved placeholder token: <a href="<link / artifact path / comment ID>' in errors
