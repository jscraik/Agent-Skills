# PR #216 Correctness Review

## Findings (Severity-ordered)

### 1. High - Inline acceptance parser drops regex criteria containing braces
- Evidence: `Infrastructure/scripts/lib/ask/commands/evals.py:530`
- Impacted behavior:
  - `_parse_inline_acceptance_sequence` extracts inline map items with `re.findall(r"\{([^{}]+)\}", text)`.
  - This pattern rejects any item body containing `{` or `}`.
  - Real acceptance regex values commonly include quantifiers like `{2,}` or `{1,3}`.
  - When such a case appears in malformed/compat YAML (the fallback parser path), `acceptance` can parse as empty.
  - Empty/partial acceptance then flows to `_tessl_criteria_from_case` and degrades scoring to generic fallback criteria instead of intended rubric checks.
- Remediation:
  - Replace brace-delimited regex extraction with a parser that respects quoted strings and balanced braces, or parse the inline sequence via YAML/JSON parser fallback instead of regex tokenization.
  - Add a regression test using compat inline acceptance with a regex value containing quantifier braces (for example `value: "(?i)item{2,}"`) and assert criteria checklist preserves that exact regex.
- Confidence: 90
- Validation ownership: introduced by current patch

## Residual Risks
- The eval path changes are broad (staging, project-link, live-private score gating). I spot-checked high-risk parsing and routing areas, but did not execute full Tessl live-private flows in this review turn.

## Validation Recommendations
- Add/extend tests in `Infrastructure/tests/test_ask_evals_command.py` covering compat inline acceptance with brace-quantifier regex.
- Run:
  - `python3 -m pytest Infrastructure/tests/test_ask_evals_command.py -q`
  - `python3 -m pytest Infrastructure/tests/test_route_skillset_deterministic.py -q`

WROTE: artifacts/reviews/pr216-correctness.md
