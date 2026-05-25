# Adversarial Post-fix Review (PU-005)

## Findings

### Medium - Human-mode codex-preview output can still be misread as runtime validation success
- Evidence:
  1. `skills_codex_preview` correctly marks the payload with `not_a_validation_result: true` and source-basis `live_runtime_parity: "not_claimed"` ([Infrastructure/scripts/lib/ask/commands/skills_impl.py:2585](Infrastructure/scripts/lib/ask/commands/skills_impl.py:2585), [Infrastructure/scripts/lib/ask/commands/skills_impl.py:2618](Infrastructure/scripts/lib/ask/commands/skills_impl.py:2618)).
  2. The non-JSON CLI renderer for `ask skills codex-preview` only prints `status=<...>` and validation commands, without printing either `not_a_validation_result` or `live_runtime_parity: not_claimed` ([Infrastructure/bin/ask:1144](Infrastructure/bin/ask:1144) to [Infrastructure/bin/ask:1151](Infrastructure/bin/ask:1151)).
  3. This creates a composition failure between machine-safe JSON semantics and human-safe terminal semantics: an operator using default output can still interpret `status=pass` as "runtime validated," recreating the original false-success narrative through a different output surface.
- Remediation suggestion:
  - Print an explicit terminal warning in this branch, e.g. `NOTE: source-modeled preview only; not a runtime validation result`, and include source-basis parity state in the human output.

## Residual risks
- `build_codex_load_preview` status is derived only from `blocked_checks`; scan/read errors are carried in `errors` but do not currently degrade `status` ([Infrastructure/scripts/lib/ask/services/codex_preview.py:542](Infrastructure/scripts/lib/ask/services/codex_preview.py:542) to [Infrastructure/scripts/lib/ask/services/codex_preview.py:555](Infrastructure/scripts/lib/ask/services/codex_preview.py:555)). This can still yield "pass with errors" semantics in adjacent preview commands.
- The new truncation summary is present and stable, but tests do not currently assert warning-message behavior for shortened-description truncation thresholds, leaving edge-message regressions possible.

## Validation notes
- Ran: `python3 -m pytest -q Infrastructure/tests/test_ask_skills_codex_preview.py`
- Result: 23 passed

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-005/adversarial-postfix-reviewer.md
