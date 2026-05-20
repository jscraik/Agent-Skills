---
schema_version: 1
artifact_id: agent-skills-jsc-329-skill-sdk-doctor-contract-spec-technical-review
artifact_type: he-code-review
type: he-code-review
canonical_slug: jsc-329-skill-sdk-doctor-contract
title: Agent Skills Kit JSC-329 Skill SDK Doctor Contract Spec Technical Review
harness_stage: he-code-review
status: complete
date: 2026-05-17
origin: .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md
reviewed_artifact: .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md
traceability_required: true
linear_status: Triage
linear_issue: JSC-329
linear_issue_url: https://linear.app/jscraik/issue/JSC-329/harden-skills-doctor-contract-fixture-for-context7
linear_team: JSC
linear_workspace: Jscraik
review_result: approved_for_he_plan
---

# Agent Skills Kit JSC-329 Skill SDK Doctor Contract Spec Technical Review

## Review Verdict

Approved for he-plan.

The deepened spec is strong enough for planning after one contract precision fix: it now names data.skill_doctor as the public doctor-readiness object inside the standard ask robot envelope. The spec keeps JSC-329 narrow, preserves RF-0 steering uptake as a closeout gate, requires fixture-level status precedence and next-command assertions, separates runtime/package/outcome-proof evidence, and explicitly blocks runtime projection edits plus broad SDK metadata migration.

No blocking findings remain.

## Reviewed Artifacts

- .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md
- .harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md
- .harness/reframes/2026-05-17-agent-skills-skill-sdk-doctor-trust-reframe.md
- .harness/strategy/2026-05-17-agent-skills-sdk-north-star.md
- .harness/quality/steering-uptake.md
- Plugins/harness-engineering/skills/he-spec/SKILL.md
- Plugins/harness-engineering/references/skills/he-spec/spec-artifact-contract.md

## Linear Work Item Contract

| Field | Value |
| --- | --- |
| Linear issue | JSC-329 |
| URL | https://linear.app/jscraik/issue/JSC-329/harden-skills-doctor-contract-fixture-for-context7 |
| Team | JSC |
| Workspace | Jscraik |
| Status | Triage |
| Priority | High |
| Reviewed artifact | .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md |
| Review result | Approved for he-plan; not approved for implementation closure |

## Linear / Spec / Plan / PR Traceability

| Linear issue | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
| --- | --- | --- | --- | --- |
| JSC-329 | SA-001 through SA-010 | he-plan not yet created | SA-001 through SA-010 | Spec technical review approves planning only; implementation and PR evidence are not available yet. |

## Findings

### Finding 1: Robot Envelope Path Was Ambiguous

Severity: High
Status: Fixed in spec
Finding tier: safe_auto

Evidence:

- The first spec version said the required doctor fields were in the JSON object consumed by robots, which could be read as the outer ask robot envelope.
- Live probe evidence from ./bin/ask skills doctor context7 --json --robot shows the readiness contract lives at data.skill_doctor while the outer envelope contains status, trace_id, metadata, and data.
- The fixed spec now states FR-001, Robot JSON Interface, and Required Top-Level Fields apply to data.skill_doctor.

Why it mattered:

If implementation tests asserted fields at the wrong JSON path, they could either fail a valid ask envelope or push the implementation to flatten the robot contract incorrectly.

Review result:

Resolved. he-plan should assert required fields at data.skill_doctor and preserve the outer ask robot envelope.

## Current Spec Strengths

### Scope Is Properly Bounded

Severity: Informational
Status: Pass

Evidence:

- Non-goals exclude broad SDK manifest migration, publishing/sharing/installing, coding-harness consumer work, and runtime projection edits.
- SA-010 requires changed-file review to prove the fixture slice did not become unbounded churn.

Operational impact:

he-plan should stay inside doctor fixture tests, baseline evidence, dynamic-field normalization, and representativeness proof.

### Failure Classes Are Kept Separate

Severity: Informational
Status: Pass

Evidence:

- FR-003 through FR-005 require source/runtime/package/outcome/profile/lifecycle evidence to remain distinct.
- SA-003 and SA-006 specifically block the misleading success mode where package readiness is confused with outcome proof.

Operational impact:

The implementation cannot close by producing a single green report; it has to preserve distinct buckets and command evidence.

### High-Signal Steering Is Now A Validation Requirement

Severity: Informational
Status: Pass

Evidence:

- FR-010 and SA-009 require transferable review feedback to trigger a bounded pattern sweep.
- SA-008 requires RF-0 steering uptake validation before closeout.

Operational impact:

The next plan must include a reviewer-feedback disposition step, which directly addresses the repeated failure mode where agents apply feedback only to a named line.

### Linear Traceability Is Sufficient For Planning

Severity: Informational
Status: Pass

Evidence:

- The spec carries linear_issue JSC-329, linear_status Triage, linear_mutation_status created, and Linear Acceptance Traceability.
- The review maps JSC-329 to SA-001 through SA-010.

Operational impact:

he-plan does not need to rediscover the tracker target before planning implementation units.

## Residual Risks

- he-plan still needs to inspect current ask CLI test conventions before selecting exact fixture and test files.
- The additional representativeness skill class is intentionally unresolved until handle availability is verified.
- contract_schemas may remain field-presence-only in RF-1 unless implementation discovers an existing schema-file home.
- Implementation closeout must classify a non-zero doctor command exit caused by blocked readiness separately from contract-shape failure.

## Pattern Sweep Disposition

| Feedback Pattern | Scope Searched | Disposition |
| --- | --- | --- |
| Required-field JSON path ambiguity | Spec requirements, Robot JSON Interface, and Data / Domain Contract. | Fixed in spec. |
| One-line feedback instead of principle uptake | Acceptance, functional requirements, validation plan, and review closeout. | Encoded as FR-010 and SA-009. |
| Broad SDK migration drift | Goals, non-goals, SA-010, and residual risks. | Blocked from JSC-329 scope. |

## Handoff

schema_version: 1
interactive_status: autonomous_assumption
route: he-plan
source_spec: .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md
review_result: approved_for_he_plan
required_plan_focus:
  - assert required fields at data.skill_doctor
  - preserve the outer ask robot envelope
  - inspect existing ask CLI test conventions before choosing fixture paths
  - capture doctor and package baseline evidence
  - normalize documented dynamic fields only
  - choose one additional read-only skill class after handle verification
  - run RF-0 steering uptake validation before closeout
  - include review-feedback pattern-sweep disposition
