# PU-005 Testing Review

## Scope
- Changed behavior: source-modeled preview basis, truncation status, and public skills codex-preview command discovery.
- Test review mode: coordinator-run validation artifact because the initial reviewer batch consumed worker slots without artifact output.

## Selected Proof
- Exact unit/CLI proof is the correct smallest gate because the change is in one service module, one command-family wrapper, command metadata, and focused CLI tests.

## Commands
- Command: python3 -m pytest Infrastructure/tests/test_ask_skills_codex_preview.py -q -> pass (25 passed, including human-output false-success, scan-error status, and blocker-sync regressions).
- Command: ./bin/ask skills codex-preview --help -> pass (public help renders).
- Command: ./bin/ask skills codex-preview --json --robot -> pass (command-family payload reports source-derived partial status, source_identity, source_basis, blocked_checks, and not_a_validation_result).
- Command: ./bin/ask skills render-preview --context-window 50 --json --robot >/tmp/jsc-364-pu005-render-preview.json -> pass.
- Command: jq '.data.codex_render_preview | {status, source_basis, truncation}' /tmp/jsc-364-pu005-render-preview.json -> pass (source_basis.basis is source_modeled, live_runtime_parity is not_claimed, blocked check ids include live runtime limits, and truncation.status is truncated).
- Command: python3 -m py_compile touched Python modules -> pass.
- Command: python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py Docs/goals/jsc-364-agent-skills-codex-runtime-proof-plane -> pass.

## Coverage Assessment
- Infrastructure/tests/test_ask_skills_codex_preview.py:73 covers source identity and source basis in load preview.
- Infrastructure/tests/test_ask_skills_codex_preview.py:96 covers scan-error status degradation and source_basis blocker propagation.
- Infrastructure/tests/test_ask_skills_codex_preview.py:137 covers token-budget omission/truncation behavior.
- Infrastructure/tests/test_ask_skills_codex_preview.py:164 covers non-truncated default character-budget behavior.
- Infrastructure/tests/test_ask_skills_codex_preview.py:183 covers public help reachability.
- Infrastructure/tests/test_ask_skills_codex_preview.py:195 covers human-output non-validation disclaimer and parity line.
- Infrastructure/tests/test_ask_skills_codex_preview.py:208 covers command-family discoverability.
- Infrastructure/tests/test_ask_skills_codex_preview.py:228 covers the false-success regression where missing Codex source identity must make the public command-family payload partial, not pass.
- Infrastructure/tests/test_ask_skills_codex_preview.py:279, :347, and :473 cover source_basis blocked-check synchronization for config, inject, and implicit parse-error paths.

## Residual Risks
- Full broad-suite validation is not a PU-005 acceptance gate while known broad-lane blockers remain unrelated to this slice. Re-run the broad gate before final goal closeout or if PU-006 touches shared proof command behavior.

## Verdict
Pass. The focused tests and public CLI proofs exercise the changed behavior directly.

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-005/testing-reviewer.md
