# PU-002 Architecture Re-Review

## Architecture Overview
PU-002 governs `repo_doctor` command-handle integrity checks in the control-plane aggregation path. The architectural intent is fail-closed behavior when generated command-handle validation evidence is missing or failing, with deterministic machine-readable failure classification.

## Findings (severity-ranked)

### informational: Prior fail-open architecture issue is resolved
- Evidence:
  - [Infrastructure/scripts/lib/ask/commands/repo_impl.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/repo_impl.py:469) computes `missing_required_checks` by requiring both `command_surface_projection_check` and `command_handle_check` payloads to be dicts.
  - [Infrastructure/scripts/lib/ask/commands/repo_impl.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/repo_impl.py:513) blocks pass state unless `missing_required_checks` is empty.
  - [Infrastructure/scripts/lib/ask/commands/repo_impl.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/repo_impl.py:530) emits `failure_code = "command_handle_subcheck_missing"` when required subchecks are absent.
  - [Infrastructure/tests/test_ask_repo_doctor.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/tests/test_ask_repo_doctor.py:995) covers missing-subcheck behavior asserting `state="block"` and `failure_code="command_handle_subcheck_missing"`.
- Assessment:
  - The previous high-severity fail-open path (missing subreports treated as implicit pass) is now closed.
  - Current pass criteria are aligned with deterministic control-plane gating.

### informational: Status-failure taxonomy gap is resolved
- Evidence:
  - [Infrastructure/scripts/lib/ask/commands/repo_impl.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/repo_impl.py:537) now classifies generated-check status failure without violations as `generated_command_handle_check_status_failed`.
  - [Infrastructure/scripts/lib/ask/commands/repo_impl.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lib/ask/commands/repo_impl.py:540) now classifies projection-check status failure without violations as `command_surface_projection_check_status_failed`.
  - [Infrastructure/tests/test_ask_repo_doctor.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/tests/test_ask_repo_doctor.py:943) validates generated-check status-failure classification without explicit violations.
  - [Infrastructure/tests/test_ask_repo_doctor.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/tests/test_ask_repo_doctor.py:969) validates projection-check status-failure classification without explicit violations.
- Assessment:
  - The previous low-severity diagnostic taxonomy concern is remediated with explicit and test-backed failure codes.

## Change Assessment
- The remediation fits the existing architecture without boundary drift:
  - No new subsystem coupling was introduced.
  - Validation remains inside command-signal composition.
  - Doctor-level orchestration behavior stays deterministic and additive.

## Compliance Check
- Upheld:
  - Fail-closed control-plane contract for required command-handle subchecks.
  - Stable component boundaries (`repo_doctor` orchestration + signal helpers + tests).
  - Consistent machine-readable failure reporting pattern for violations and status-only failures.
- Violations:
  - No blocker, high, or medium architectural violations identified in this slice.

## Risk Analysis
- Blocker/high/medium residual risk in PU-002:
  - None identified.
- Residual low risk:
  - None identified in the reviewed scope.
- Confidence:
  - High, based on direct implementation and test-evidence inspection in scoped files.

## Recommendations
1. Accept PU-002 remediation as architecturally compliant for the prior high-severity fail-open concern.
2. Keep the explicit status-failure codes as part of the stable `repo_doctor` diagnostic contract for downstream automation.

WROTE: artifacts/reviews/jsc-351-pu002/architecture-rereview.md
