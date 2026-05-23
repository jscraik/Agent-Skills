# PU-002 Governor Disposition

## Decision

pass_with_classified_runtime_blockers

## Scope

PU-002 implemented the generated command-handle gate in repo doctor without mutating generated projections, .agents/**, plugin caches, or runtime caches.

## Findings Disposition

| Finding | Severity | Disposition | Evidence |
|---|---:|---|---|
| Missing generated/projection subreports were treated as implicit pass. | high | fixed | repo_impl.py now requires both subreports, emits command_handle_subcheck_missing, and tests missing-subcheck blocking behavior. |
| Generated command-handle status failure with no explicit violations lacked direct test coverage. | medium | fixed | test_generated_command_handle_check_failure_without_violations_blocks_repo_doctor asserts blocking behavior and generated_command_handle_check_status_failed. |
| Projection status failure with no explicit violations could fall back to generic classification. | low | fixed | test_command_surface_projection_check_failure_without_violations_blocks_repo_doctor asserts command_surface_projection_check_status_failed. |

## Review Evidence

- artifacts/reviews/jsc-351-pu002/architecture.md
- artifacts/reviews/jsc-351-pu002/simplicity.md
- artifacts/reviews/jsc-351-pu002/testing.md
- artifacts/reviews/jsc-351-pu002/architecture-rereview.md
- artifacts/reviews/jsc-351-pu002/testing-rereview.md

No blocker, high, medium, or low findings remain unresolved in the scoped PU-002 code.

## Validation Evidence

| Check | Outcome | Notes |
|---|---:|---|
| python3 -m pytest Infrastructure/tests/test_ask_repo_doctor.py -q | pass | 36 passed in 1.19s. |
| ./bin/ask skills handles --check --check-command-handles --no-handles --json --robot | blocked_pre_existing | Generated command handles passed; command-surface projection is stale with COMMAND_SURFACE_PROJECTION_DRIFT. |
| ./bin/ask repo doctor --json --robot | blocked_pre_existing | Primary blocker is runtime_budget; secondary blocker is command-surface projection drift. The PU-002 command-handle signal is reachable and machine-classified. |

## Governor Decision

PU-002 implementation is complete and independently validated. It may not be used to claim global repo health because live repo doctor remains blocked by runtime budget and command-surface projection drift. Continuation must first govern those live blockers as a separate remediation/classification slice, not proceed blindly to PU-003.

WROTE: artifacts/reviews/jsc-351-pu002/governor-disposition.md
