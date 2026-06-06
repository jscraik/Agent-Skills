# PU-011 Trace Plan Adversarial Review

## Findings

1. **High** - The plan lets the live robot envelope stay loose because the only executable proof it names does not scan the real envelope module.
   - **Evidence:** The spec says robot response envelopes are in scope and that public SDK contract modules must not use `Any` (FR-001 and FR-004 at [.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:149-153]). The trace plan's typed-contract rows mention robot envelopes and no-`Any` enforcement, but the validation block only runs `Infrastructure/tests/test_skills_sdk_typed_contracts.py`, `Infrastructure/tests/test_skills_sdk_schema_spine.py`, `Infrastructure/tests/test_skills_sdk_capability_status.py`, and `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py` ([.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:55-60](.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:55-60) and [.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:128-157](.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:128-157)). The actual envelope module still contains `Any` at [Infrastructure/scripts/lib/ask/envelope.py:73-84](Infrastructure/scripts/lib/ask/envelope.py:73-84), and the existing envelope-format proof lives in [Infrastructure/tests/test_ask_cli_impl.py:50-83](Infrastructure/tests/test_ask_cli_impl.py:50-83), which the plan does not run.
   - **Problem:** A change can leave `CallResult.metadata`, `CallResult.data`, or `CallResult.telemetry` untyped and still pass the listed plan checks. The top-level `--json --robot` envelope can drift while the trace plan reports success.
   - **Impact:** PU-011 can close with a green status/HTML/typed-contract lane while the public robot envelope still accepts loose shapes or keeps `Any` in the live emitter.
   - **Remediation:** Add an explicit no-`Any` scan or AST check for `Infrastructure/scripts/lib/ask/envelope.py`, and include the envelope-format CLI test or a dedicated envelope contract test in the required validation block.
   - **Confidence:** 96/100
   - **Validation ownership:** pre-existing plan gap

2. **High** - Install and rollback are covered, but uninstall never gets its own executable proof.
   - **Evidence:** FR-009 requires validation for real install, rollback, uninstall, check, risk, and lifecycle outputs, and AC-003 through AC-005 require install receipt, cleanup receipt, and lockfile validation ([.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:157-158](.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:157-158) and [.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:371-373](.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:371-373)). The trace plan's TR-006 says install, rollback, uninstall, check, risk, and lifecycle outputs should all be covered, but the validation block only runs `Infrastructure/tests/test_skills_sdk_typed_contracts.py` and does not include [Infrastructure/tests/test_skills_sdk_project_cleanup.py](Infrastructure/tests/test_skills_sdk_project_cleanup.py), which is the test file that actually exercises uninstall preview/apply and cleanup receipt semantics at [Infrastructure/tests/test_skills_sdk_project_cleanup.py:101-212](Infrastructure/tests/test_skills_sdk_project_cleanup.py:101-212).
   - **Problem:** The plan can validate install receipts and lockfiles through the typed-contract smoke test, but uninstall receipts and lockfile-bound removal semantics never get a direct execution step.
   - **Impact:** A regression in the uninstall receipt schema or uninstall runtime path can remain hidden while the listed validation still passes.
   - **Remediation:** Add `Infrastructure/tests/test_skills_sdk_project_cleanup.py` to the required validation block, or split TR-006 into separate install, rollback, and uninstall rows with explicit executable proof for each.
   - **Confidence:** 94/100
   - **Validation ownership:** pre-existing plan gap

3. **Medium** - The root package-manager boundary is only prose-backed; the validation recipe never stages a forbidden root manifest, so the failure mode is not actually proven.
   - **Evidence:** The spec requires the root package-manager files to remain absent and says the validation must fail if they appear (FR-031 and AC-021 at [.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:180-181](.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:180-181) and [.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:389-390](.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:389-390)). The trace plan's TR-013 names the boundary check ([.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:67](.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:67)), but the validation block only runs the current-tree commands in [.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:139-157](.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:139-157). None of those steps injects a temporary root `package.json`, lockfile, or root `pyproject.toml` to prove the negative case.
   - **Problem:** The plan can report green against the current checkout while never proving that a newly introduced forbidden root package manifest would be rejected.
   - **Impact:** A later regression that reintroduces root package-manager state can slip past the PU-011 lane until someone manually notices the new files.
   - **Remediation:** Add a temp-fixture negative test or an explicit file-injection step that writes a forbidden root package manifest into a scratch copy and asserts the `skills-sdk` validation scope fails closed, while still allowing `Infrastructure/pyproject.toml` and `Infrastructure/uv.lock`.
   - **Confidence:** 90/100
   - **Validation ownership:** pre-existing plan gap

## Residual Risks

- The plan is better bounded than a broad refactor, but the `skills-sdk` scope still has to be made real before its validation command can be treated as executable proof.
- I did not execute implementation validation; this review is based on current repo evidence and the plan/spec text.

## Verdict

changes_requested

## Accountability Receipt

- status: complete
- artifact_paths:
  - /Users/jamiecraik/dev/agent-skills/.harness/review-artifacts/pu-011-trace-plan-adversarial-contract-runtime.md
- manifest_path: artifacts/agent-runs/adversarial-reviewer-20260606-pu011-trace-contract-runtime/manifest.json
- findings: 3
- failures_or_blockers: none
- improvement_opportunities: add executable proof for the live robot envelope, cover uninstall receipts directly, and turn the root package-manager boundary into a negative test instead of prose-only policy.
- strengths: the trace plan already keeps local proof separate from PR/CI truth, keeps mutation authority bounded, and identifies the key scope gaps instead of widening into unrelated work.
- validation_evidence: reviewed [.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md](.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md), [.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md](.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md), [Infrastructure/scripts/lib/ask/envelope.py](Infrastructure/scripts/lib/ask/envelope.py), [Infrastructure/tests/test_ask_cli_impl.py](Infrastructure/tests/test_ask_cli_impl.py), [Infrastructure/tests/test_skills_sdk_typed_contracts.py](Infrastructure/tests/test_skills_sdk_typed_contracts.py), and [Infrastructure/tests/test_skills_sdk_project_cleanup.py](Infrastructure/tests/test_skills_sdk_project_cleanup.py).
- next_action: update the trace plan so each acceptance boundary has a concrete executable check and rerun the validation block against the updated plan.
- useful_findings: the plan's existing trace rows are close, but the execution block omits the tests that prove the envelope and uninstall paths.
- avoided_false_positive: I did not flag the skills-sdk scope command itself as a defect because the plan already records that scope wiring is a P0 gap to be implemented.
- evidence_quality: high; the relevant tests and envelope implementation exist in-tree and the plan's validation block omits them.
- followed_scope: yes; findings stayed within contract/runtime traceability, public envelope/no-Any enforcement, receipt coverage, and package-boundary validation.
- reusable_learning: when a trace plan lists a contract surface, the required validation block must name the exact test or negative fixture that would fail if that surface regressed.
- coordinator_score: 9/10

WROTE: /Users/jamiecraik/dev/agent-skills/.harness/review-artifacts/pu-011-trace-plan-adversarial-contract-runtime.md
