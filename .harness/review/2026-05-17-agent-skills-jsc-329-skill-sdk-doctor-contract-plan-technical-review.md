---
schema_version: 1
artifact_id: agent-skills-jsc-329-skill-sdk-doctor-contract-plan-technical-review
artifact_type: he-code-review
type: he-code-review
canonical_slug: jsc-329-skill-sdk-doctor-contract
title: Agent Skills Kit JSC-329 Skill SDK Doctor Contract Plan Technical Review
harness_stage: he-code-review
status: complete
date: 2026-05-17
origin: .harness/plan/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-plan.md
reviewed_artifact: .harness/plan/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-plan.md
traceability_required: true
linear_status: Triage
linear_issue: JSC-329
linear_issue_url: https://linear.app/jscraik/issue/JSC-329/harden-skills-doctor-contract-fixture-for-context7
linear_team: JSC
linear_workspace: Jscraik
review_result: approved_for_he_work
---

# Agent Skills Kit JSC-329 Skill SDK Doctor Contract Plan Technical Review

## Review Verdict

Approved for he-work.

The deepened plan is implementation-ready after one review fix: it now requires explicit environment/tooling failure classification before substituting an interpreter when canonical python3 hangs or cannot start. The plan preserves the spec technical review's core correction by making data.skill_doctor the contract object, keeps the work bounded to ask doctor implementation/tests/evidence, and includes separate units for field assertions, status and next_command semantics, signal separation, dynamic-field normalization, representativeness, pattern sweep, and closeout validation.

No blocking findings remain.

## Reviewed Artifacts

- .harness/plan/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-plan.md
- .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md
- .harness/review/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec-technical-review.md
- Infrastructure/tests/test_ask_skills_doctor.py
- Infrastructure/tests/test_ask_skills_package.py
- Infrastructure/scripts/lib/ask/commands/skills_impl.py
- Plugins/harness-engineering/skills/he-plan/SKILL.md
- Plugins/harness-engineering/references/skills/he-plan/plan-artifact-contract.md

## Linear Work Item Contract

| Field | Value |
| --- | --- |
| Linear issue | JSC-329 |
| URL | https://linear.app/jscraik/issue/JSC-329/harden-skills-doctor-contract-fixture-for-context7 |
| Team | JSC |
| Workspace | Jscraik |
| Status | Triage |
| Priority | High |
| Reviewed artifact | .harness/plan/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-plan.md |
| Review result | Approved for he-work; not implementation closure evidence |

## Linear / Spec / Plan / PR Traceability

| Linear issue | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
| --- | --- | --- | --- | --- |
| JSC-329 | SA-001 through SA-010 | PU-001 through PU-006 | data.skill_doctor required fields, status precedence, next_command semantics, signal separation, dynamic-field normalization, representativeness, RF-0 steering validation | PR evidence pending implementation. |

## Findings

### Finding 1: Validation Runtime Substitution Needed A Stop Rule

Severity: Medium
Status: Fixed in plan
Finding tier: safe_auto

Evidence:

- During plan validation, plain python3 hung in the current sandbox while /Users/jamiecraik/.venvs/pyyaml/bin/python completed artifact validators.
- The first plan version listed canonical python3 validation commands but did not say what to do if the interpreter itself hangs or cannot start.
- The fixed plan now adds a PU-006 step, risk-register row, and observability requirement to classify interpreter/runtime substitution as an environment/tooling failure before using an alternate interpreter for artifact validation.

Why it mattered:

Without this stop rule, a future agent could silently swap runtimes and report green validation without preserving the real blocker. That repeats the exact class of operating failure this SDK work is trying to remove.

Review result:

Resolved. he-work should prefer canonical repo wrappers for implementation validation and explicitly report any interpreter substitution.

## Current Plan Strengths

### Work Units Preserve Source Traceability

Severity: Informational
Status: Pass

Evidence:

- PU-001 through PU-006 map to SA-001 through SA-010 and the relevant FR/NFR IDs.
- Each PU has objective, allowed paths, forbidden paths, steps, validation, stop condition, rollback, and handoff state.

Operational impact:

he-work can start at PU-001 without re-planning the slice.

### API Contract Boundary Is Correct

Severity: Informational
Status: Pass

Evidence:

- PU-001 explicitly asserts data.skill_doctor and preserves the outer ask robot envelope.
- The review plan calls out data.skill_doctor vs envelope-root confusion as a review item.

Operational impact:

The implementation should not accidentally flatten or destabilize the ask robot envelope.

### Scope Is Kept Narrow

Severity: Informational
Status: Pass

Evidence:

- Scope excludes runtime projection edits, broad metadata migration, coding-harness consumer work, remote execution, and package publication.
- PU-003 stops if proving separation requires changing package readiness semantics beyond doctor consumption.

Operational impact:

JSC-329 remains a contract-fixture slice instead of becoming a general SDK migration.

### Transferable Feedback Is Built Into Execution

Severity: Informational
Status: Pass

Evidence:

- PU-005 requires a bounded pattern sweep for similar JSON-path assertions, status precedence assertions, and next_command assumptions.
- The plan requires disposition classes instead of only fixing the named issue.

Operational impact:

The implementation path directly addresses Jamie's repeated feedback about models applying a local correction without updating similar cases.

## Residual Risks

- The exact fixture strategy remains an implementation-time choice: helper-backed tests first, fixture files only if snapshots become bulky.
- The representativeness handle defaults to he-plan, but he-work must still verify the handle before using it.
- If focused tests expose missing production behavior, skills_impl.py changes should stay field-preserving and local to skills_doctor.
- The current plain python3 hang should be treated as environment/tooling evidence if it persists during he-work, not as a JSC-329 product failure.

## Pattern Sweep Disposition

| Feedback Pattern | Scope Searched | Disposition |
| --- | --- | --- |
| Plan asserted wrong JSON contract path | PU-001, Review Plan, Source Contract | Already fixed in plan; data.skill_doctor is explicit. |
| Validation substitution could hide environment blocker | PU-006, Risk Register, Observability and Evidence | Fixed in plan. |
| One-line feedback handling | PU-005, Review Plan, Risk Register | Encoded as bounded pattern sweep with disposition classes. |
| Broad migration drift | Scope, Work Units, Stop Conditions | Blocked from he-work unless a new plan is created. |

## Handoff

schema_version: 1
interactive_status: autonomous_assumption
route: he-work
source_plan: .harness/plan/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-plan.md
review_result: approved_for_he_work
first_unit: PU-001
required_closeout:
  - assert required fields at data.skill_doctor
  - preserve the outer ask robot envelope
  - classify non-zero doctor exit caused by blocked readiness separately from command failure
  - report interpreter/runtime used for validation
  - run RF-0 steering uptake validation
  - include pattern-sweep disposition
