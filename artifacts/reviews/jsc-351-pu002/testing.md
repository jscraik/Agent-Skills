# PU-002 Testing Review

## Findings

### medium — Missing error-path test when generated handle check fails without explicit violations
- Evidence:
  - [Infrastructure/scripts/lib/ask/commands/repo_impl.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/repo_impl.py:497) computes `generated_check_pass` from `command_handle_check.status`.
  - [Infrastructure/scripts/lib/ask/commands/repo_impl.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/repo_impl.py:499) blocks when `generated_check_pass` is false, even if no violations are listed.
  - [Infrastructure/scripts/lib/ask/commands/repo_impl.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/repo_impl.py:521) falls through to generic `command_handle_validation_failed` when `generated_violations` is empty.
  - Existing generated-handle tests only cover the non-empty violation case ([Infrastructure/tests/test_ask_repo_doctor.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/tests/test_ask_repo_doctor.py:818)); they do not cover `command_handle_check.status="fail"` with `violations=[]`.
- Risk:
  - A real command-handle check failure that returns no per-item violations could regress classification or summary behavior without test detection, reducing confidence that repo-doctor remains deterministic for this branch.
- Remediation:
  - Add a focused unit test that patches `skills_handles` to return:
    - `command_surface.status="pass"`
    - `command_surface_projection_check.status="pass"`
    - `command_handle_check.status="fail"`
    - `command_handle_check.violations=[]`
  - Assert repo doctor blocks and emits the expected fallback classification (`failure_code="command_handle_validation_failed"`) with `next_command` equal to `COMMAND_HANDLE_CHECK_COMMAND`.

## Residual Risks / Test Gaps
- Live evidence in notes confirms pre-existing projection drift classification works, but unit coverage still lacks the zero-violation generated-check-failure branch above.
- No additional blocker or high issues found in the scoped PU-002 files.

WROTE: artifacts/reviews/jsc-351-pu002/testing.md
