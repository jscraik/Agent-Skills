# Correctness Review: context-budgeted skill trees

## Findings (severity-ranked)

### 1) HIGH - Context-budget validator can crash on malformed manifest rows instead of returning violations
- Evidence:
  - `Infrastructure/scripts/validation-and-linting/check_context_budget.py:121-123` reads `provenance = row.get(...)` and `source_path = row.get(...)` before confirming `row` is a dict.
  - The same function only checks `isinstance(row, dict)` inline later, but by then `.get` has already been called.
  - Repro produced an uncaught exception (`AttributeError: list object has no attribute get`) when a manifest line parsed as a JSON array.
- Impact:
  - `check_context_budget.py` can hard-crash on a malformed-but-parseable JSON line, failing closed with an exception instead of emitting structured policy violations.
  - This breaks the validator contract and can hide actionable diagnostics in CI.
- Remediation:
  - Guard row type immediately after `json.loads(...)`; if non-dict, append a structured violation (for example `INVALID_SKILLSET_MANIFEST_ROW_TYPE`) and `continue`.
  - Only read `row.get(...)` after the type check.

### 2) HIGH - `ask workouts run` can crash on slow seed/verify commands via uncaught timeout exceptions
- Evidence:
  - `Infrastructure/scripts/lib/ask/commands/workouts.py:193-194` calls `subprocess.run(..., timeout=60)` for both seed and verify.
  - No `try/except subprocess.TimeoutExpired` is present around either call inside `run_workout`.
- Impact:
  - A slow or hanging workout process can raise `TimeoutExpired` and bubble out as an unhandled exception, terminating the command instead of returning a structured `CallResult` error.
  - This is user-visible wrong behavior at the CLI boundary (`ask workouts run`).
- Remediation:
  - Catch `subprocess.TimeoutExpired` per attempt and convert it into a normal failure attempt payload (`outcome: failure`, `failure_type: timeout`, non-zero synthetic exit code).
  - Ensure function always returns a valid `CallResult` envelope, even for timeout paths.

## Residual risks
- Rooted projection/routing behavior is heavily metadata-dependent; malformed manifest row *types* and timeout paths are currently under-covered by tests and should be explicitly added as regression tests.

WROTE: artifacts/reviews/context_tree_correctness_review_2.md
