# PU-005 Testing Review

## Findings

No blocker, high, or medium testing findings remain after remediation.

- remediated medium - Infrastructure/tests/test_ask_skills_codex_preview.py:111
  - Evidence: the test suite now covers the default character-budget/full-render branch with test_render_preview_reports_full_strategy_with_default_character_budget.
  - Remediation applied: added direct assertions for budget.kind=characters, render_strategy=full, zero omissions, and no warning.

- remediated medium - Infrastructure/tests/test_ask_skills_codex_preview.py:219
  - Evidence: the test suite now covers reader-command attribution through cat .agents/skills/alpha/SKILL.md.
  - Remediation applied: added direct assertions that reader-command attribution selects the expected skill.

- remediated medium - Infrastructure/tests/test_ask_skills_codex_preview.py:237
  - Evidence: the test suite now covers relative workdir path resolution for implicit preview.
  - Remediation applied: added a nested working-directory fixture and assertion that workdir resolves to the expected absolute path.

- remediated low - Infrastructure/tests/test_ask_skills_codex_preview.py:298
  - Evidence: the test suite now exercises skills config missing and invalid sub-action behavior through the public CLI entrypoint.
  - Remediation applied: added subprocess coverage for missing config_action and invalid config_action.

- informational - Infrastructure/tests/test_ask_skills_codex_preview.py:277
  - Evidence: the test suite covers shell parse failure as a structured blocked check without traceback.
  - Remediation: none required.

## Validation Notes

- python3 -m pytest Infrastructure/tests/test_ask_skills_codex_preview.py -q passed with 13 reported test outcomes.
- python3 -m pytest Infrastructure/tests -q -k 'preview or codex_parity or invocation or render' is blocked in the default interpreter by missing PyYAML during unrelated test collection.
- UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache uv run --python 3.12 --with pyyaml --with pytest python -m pytest Infrastructure/tests -q -k 'preview or codex_parity or invocation or render' passed with 31 tests and 1482 deselected.
- Command smokes for load-preview, render-preview, config explain, inject-preview, and implicit-preview all exit 0.

## Residual Risk

This slice still does not prove live Codex runtime behavior. It proves the repo-side model and explicitly reports parity blockers. Live runtime proof remains a later governed slice only if it is implemented as executable Codex runtime smoke, not as a stronger claim on these preview commands.

WROTE: artifacts/reviews/jsc-351-pu005/testing.md
