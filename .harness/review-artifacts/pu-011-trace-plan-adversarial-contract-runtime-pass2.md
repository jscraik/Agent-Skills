# PU-011 Trace Plan Adversarial Review Pass 2

## Findings

1. **High** - The new `skills-sdk` scope is still only described, not proven, so the central acceptance command can remain broken while the plan looks executable.
   - **Evidence:** The patched trace plan adds TR-012 for a dedicated `skills-sdk` scope and says the route proof should come from `Infrastructure/tests/test_ask_repo_validate.py` or validation-runner tests, while the required validation block only runs the existing generic repo-validate test file and no dedicated scope fixture or scratch assertion ([.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:70](.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:70), [.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:146-166](.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:146-166)). The current repo test only proves arbitrary scope forwarding for `lint`, not `skills-sdk`, and it never checks the unknown-scope fallback required by AC-016/AC-017 ([Infrastructure/tests/test_ask_repo_validate.py:99-121](Infrastructure/tests/test_ask_repo_validate.py:99-121)). The validation runner itself still only recognizes `all|lint|typecheck|test|audit|check|consistency-advisory|consistency-health` ([Infrastructure/scripts/validate_all_impl.sh:14-17](Infrastructure/scripts/validate_all_impl.sh:14-17), [Infrastructure/scripts/validate_all_impl.sh:97-105](Infrastructure/scripts/validate_all_impl.sh:97-105)).
   - **Problem:** A patch can add the prose for `skills-sdk` routing without adding any runnable proof that `./bin/ask repo validate --scope=skills-sdk --json --robot` is accepted and reaches the typed-artifact lane.
   - **Impact:** The main acceptance command can still fail closed or silently fall back to another scope while the trace plan claims the scope-wiring gap is covered.
   - **Remediation:** Add a dedicated scope-routing test that invokes `skills-sdk`, asserts the typed-artifact lane is selected, and keeps the unknown-scope failure path in the same validation slice.
   - **Confidence:** 92/100
   - **Validation ownership:** pre-existing plan gap

2. **High** - Pydantic versus JSON Schema authority is still only narrated, so a model/schema mismatch can escape the current validation block.
   - **Evidence:** TR-003 promises parity tests for required fields, optional fields, nullability, enums, and extra-key behavior, but the runtime validation block only runs `Infrastructure/tests/test_skills_sdk_schema_spine.py` and `Infrastructure/tests/test_skills_sdk_typed_contracts.py` ([.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:61-63](.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:61-63), [.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:146-166](.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:146-166)). The schema-spine test only checks schema shape and fixtures; it does not compare model output against schema acceptance or rejection rules ([Infrastructure/tests/test_skills_sdk_schema_spine.py:28-64](Infrastructure/tests/test_skills_sdk_schema_spine.py:28-64)). The typed-contract test validates install, lockfile, and rollback payloads, but it does not establish a schema-versus-model authority rule on its own ([Infrastructure/tests/test_skills_sdk_typed_contracts.py:62-116](Infrastructure/tests/test_skills_sdk_typed_contracts.py:62-116)). The spec explicitly requires parity/authority handling and failure on disagreement ([.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:149-176](.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:149-176), [.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:243-255](.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:243-255)).
   - **Problem:** The plan can go green with a schema-only drift, because there is no named executable check that fails when schema and Pydantic disagree on one of the covered contract pairs.
   - **Impact:** The published contract surface can diverge from the Python models without the trace plan catching it.
   - **Remediation:** Add a dedicated schema/model parity test row and validation command that exercises at least one deliberate mismatch fixture for each public contract family that matters here.
   - **Confidence:** 89/100
   - **Validation ownership:** pre-existing plan gap

3. **Medium** - The root package-manager negative case is still prose-first, so the plan does not yet prove the repo fails when forbidden root manifests appear.
   - **Evidence:** TR-013 and AC-021 now state that a scratch-copy or injected negative fixture should prove the root package-manager boundary ([.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:71](.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:71), [.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:125](.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:125), [.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:180-183](.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:180-183), [.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:383-390](.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:383-390)). But the actual validation block still only runs current-tree commands and tests; it never stages a forbidden root `package.json`, lockfile, or root `pyproject.toml` in a scratch repo to prove the negative behavior ([.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:146-166](.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:146-166)).
   - **Problem:** The acceptance criterion can remain untested until someone manually notices a forbidden root manifest.
   - **Impact:** A later regression that reintroduces a root package-manager file can slip past the PU-011 lane.
   - **Remediation:** Add a temp-copy injection test or a fixture-based negative case that writes forbidden root manifests and asserts the skills-sdk validation path fails closed while still allowing `Infrastructure/pyproject.toml` and `Infrastructure/uv.lock`.
   - **Confidence:** 88/100
   - **Validation ownership:** pre-existing plan gap

4. **Medium** - The no-Any requirement is still not pinned to an explicit AST check in the executable slice, so the live envelope path can keep `Any` while the plan appears to cover it.
   - **Evidence:** TR-002 now names `Infrastructure/scripts/lib/ask/envelope.py`, SDK contract modules, and modules that directly construct public robot envelopes, but the validation block still only runs the generic typed-contract test, schema-spine test, project-cleanup test, and a Ruff pass over `Infrastructure/scripts/lib/ask/envelope.py` ([.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:60](.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:60), [.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:149-160](.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md:149-160)). The spec is explicit that the AST test must cover `Infrastructure/scripts/lib/ask/envelope.py` and any module that directly constructs public `--json --robot` output envelopes ([.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:318-327](.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:318-327), [.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:379-386](.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md:379-386)). The current envelope implementation still uses `typing.Any` on the public envelope fields ([Infrastructure/scripts/lib/ask/envelope.py:73-84](Infrastructure/scripts/lib/ask/envelope.py:73-84)).
   - **Problem:** A lint pass over the file is not the same thing as a focused AST ban, so the exact contract the spec asks for can still be missed.
   - **Impact:** The top-level robot envelope can remain loosely typed even if the trace plan is marked green.
   - **Remediation:** Add the explicit AST/no-Any test to the required validation block or name the concrete test file that will own the envelope scan.
   - **Confidence:** 84/100
   - **Validation ownership:** pre-existing plan gap

## What The Patch Did Close

- The uninstall path is now explicitly named in the plan and backed by `Infrastructure/tests/test_skills_sdk_project_cleanup.py`.
- The live robot envelope runtime shape is now named in the validation block through `Infrastructure/tests/test_ask_cli_impl.py`.

## Residual Risks

- The plan is much closer to executable proof than the previous version, but the central scope-wiring and authority questions are still not pinned to exact failing commands.
- I did not run implementation validation; this review is based on current repo evidence plus the patched trace plan.

## Accountability Receipt

- status: complete
- artifact_paths:
  - /Users/jamiecraik/dev/agent-skills/.harness/review-artifacts/pu-011-trace-plan-adversarial-contract-runtime-pass2.md
- manifest_path: artifacts/agent-runs/adversarial-reviewer-20260606-pu011-trace-contract-runtime-pass2/manifest.json
- findings: 4
- failures_or_blockers: none
- improvement_opportunities: add an executable `skills-sdk` scope-routing proof, add a schema/model parity test row, make the root package-manager negative case runnable, and pin the no-Any rule to an explicit AST test.
- strengths: the patch did close the uninstall proof gap and brought the live envelope runtime check into the validation plan; it also tightened the root package-manager requirement from prose into an explicit negative-test requirement.
- validation_evidence: reviewed [.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md](.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md), [.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md](.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md), [Infrastructure/tests/test_ask_cli_impl.py](Infrastructure/tests/test_ask_cli_impl.py), [Infrastructure/tests/test_ask_repo_validate.py](Infrastructure/tests/test_ask_repo_validate.py), [Infrastructure/tests/test_skills_sdk_schema_spine.py](Infrastructure/tests/test_skills_sdk_schema_spine.py), [Infrastructure/tests/test_skills_sdk_typed_contracts.py](Infrastructure/tests/test_skills_sdk_typed_contracts.py), [Infrastructure/tests/test_skills_sdk_project_cleanup.py](Infrastructure/tests/test_skills_sdk_project_cleanup.py), [Infrastructure/scripts/lib/ask/envelope.py](Infrastructure/scripts/lib/ask/envelope.py), and [Infrastructure/scripts/validate_all_impl.sh](Infrastructure/scripts/validate_all_impl.sh).
- next_action: update the trace plan so every acceptance boundary has one named executable proof command or negative fixture that would fail if that boundary regressed.
- useful_findings: the patch did meaningfully improve coverage for uninstall and runtime envelope shape, so the remaining gaps are narrower and more specific.
- avoided_false_positive: I did not re-flag uninstall coverage as a gap because the plan now names the project-cleanup test directly.
- evidence_quality: high; the repo contains concrete tests and runtime code that show where the plan is still relying on description instead of executable proof.
- followed_scope: yes; findings stayed on contract/runtime traceability, robot envelope/no-Any enforcement, schema/model authority, scope wiring, and package-boundary validation.
- reusable_learning: when a trace plan claims a contract surface is covered, the validation block must name the exact test or negative fixture that would fail if that surface regressed.
- coordinator_score: 9/10

WROTE: /Users/jamiecraik/dev/agent-skills/.harness/review-artifacts/pu-011-trace-plan-adversarial-contract-runtime-pass2.md
