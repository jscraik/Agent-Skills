# PU-002 Architecture Review

## Architecture Overview
PU-002 extends the `repo_doctor` control-plane aggregation to include generated command-handle validation as a first-class blocking signal. The change is implemented in `repo_impl.py` by wiring `skills_handles(..., check=True, include_handles=False, check_command_handle_files=True)` into the doctor signal fan-in and by emitting machine-readable failure codes for command-surface vs generated-handle drift.

## Findings (severity-ranked)

### high: Fail-open behavior if generated subchecks are missing from skills-handles payload
- Evidence:
  - `Infrastructure/scripts/lib/ask/commands/repo_impl.py:497` sets `generated_check_pass = command_handle_check.get("status") in {None, "pass"}`.
  - `Infrastructure/scripts/lib/ask/commands/repo_impl.py:498` sets `projection_check_pass = projection_check.get("status") in {None, "pass"}`.
  - `Infrastructure/scripts/lib/ask/commands/repo_impl.py:499-504` allows full `state="pass"` when both are `None` and main surface says pass.
- Why this is an architectural risk:
  - PU-002 intent is deterministic enforcement for generated command-handle drift. Treating missing subreports as pass introduces a silent bypass path if upstream payload shape regresses (or partial data is returned), violating fail-closed boundary expectations for this gate.
- Remediation:
  - When `repo_doctor` invokes `skills_handles(..., check_command_handle_files=True)`, require explicit presence/status for both `command_handle_check` and `command_surface_projection_check`.
  - If either subreport is missing, return `state="block"` (or `state="error"`) with a dedicated failure code such as `command_handle_check_missing` to preserve deterministic machine behavior.

## Change Assessment
- Good boundary adherence:
  - The doctor orchestration remains additive and does not alter unrelated control-plane signals.
  - Distinct failure-code taxonomy is introduced for generated-handle drift vs projection drift:
    - `generated_command_handle_check_failed`
    - `command_surface_projection_check_failed`
  - Next-command routing remains deterministic via a single repair command surface.
- Test alignment:
  - Tests verify signal wiring and classification paths, including generated drift and projection drift separation.

## Compliance Check
- Upheld:
  - Separation of concerns: diagnosis remains in signal composition, not mixed into execution orchestration.
  - Contract clarity: machine-readable failure-code expansion is aligned with ABI-style reporting.
  - Scope discipline: PU-002 changes stay within allowed files and do not expand into unrelated slices.
- Violated / at risk:
  - Deterministic fail-closed contract is weakened by implicit pass on missing generated/projection subreport fields.

## Risk Analysis
- Residual risk if unaddressed:
  - False-green `repo_doctor` outcomes can occur on payload-shape regression without explicit generated-handle proof.
  - This would shift risk downstream to closeout/triage and reduce trust in doctor as control-plane gate.
- Confidence:
  - High confidence in the identified risk (directly observable in pass-condition logic and not contradicted by tests in scope).

## Recommendations
1. Tighten pass criteria in `_command_handles_signal` to require explicit subreport presence/status when command-handle file checks are requested.
2. Add one focused test in `Infrastructure/tests/test_ask_repo_doctor.py` for missing `command_handle_check` and/or missing `command_surface_projection_check` returning block/error with explicit failure code.
3. Keep current failure-code separation; it is architecturally sound and useful for downstream triage automation.

WROTE: artifacts/reviews/jsc-351-pu002/architecture.md
