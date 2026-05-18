---
schema_version: 1
artifact_id: agent-skills-jsc-329-skill-sdk-doctor-contract-decision-deepening-technical-review
artifact_type: he-code-review
type: he-code-review
canonical_slug: jsc-329-skill-sdk-doctor-contract
title: Agent Skills Kit JSC-329 Decision Deepening Technical Review
harness_stage: he-code-review
status: complete
date: 2026-05-17
origin: .harness/plan/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-plan.md
reviewed_artifact: .harness/plan/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-plan.md
companion_spec: .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md
traceability_required: true
linear_status: Triage
linear_issue: JSC-329
linear_issue_url: https://linear.app/jscraik/issue/JSC-329/harden-skills-doctor-contract-fixture-for-context7
linear_team: JSC
linear_workspace: Jscraik
review_result: approved_for_he_work_with_decision_constraints
---

# Agent Skills Kit JSC-329 Decision Deepening Technical Review

## Command Summary

BLUF: This artifact gives he-work implementers, reviewers, and Jamie the decision review for the four areas that could otherwise make JSC-329 either too permissive or too broad: waiver authority, schema-file creation, production `sdk_layer` exposure, and imagegen fallback. Its job is to convert those decisions into implementation constraints that can be checked during PU-001 through PU-006 instead of rediscovered during closeout. It matters because these are the places where a plan can look governed while still allowing self-approved exceptions, hidden test-only contracts, premature schema ownership, or unrelated image-tool friction to distort implementation. The decision is to approve he-work only with the encoded constraints: external waiver authority, no RF-1 schema files without a decision record, production JSON layer fields for known readiness classes, and image generation treated as auxiliary evidence.

Decision Needed: No further plan/spec rewrite is needed for these four areas unless implementation discovers a canonical schema home, a required waiver, or a different configured imagegen backend.

Top Risks: The implementation can still fail by treating fixture-side `sdk_layer` mapping as enough, creating schema files without ownership proof, or writing a waiver that cites no external authority.

Next Action: Start PU-001 only after preserving FR-021 through FR-024 in the implementation checklist and review plan.

## Review Verdict

Approved for he-work with the decision constraints now encoded in the plan and spec.

## Reviewed Artifacts

- .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md
- .harness/plan/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-plan.md

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
| Companion spec | .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md |
| Review result | Approved for he-work with decision constraints; not implementation closure evidence |

## Linear / Spec / Plan / PR Traceability

| Linear issue | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
| --- | --- | --- | --- | --- |
| JSC-329 | FR-021, FR-022, FR-023, FR-024, SA-016, SA-017, SA-018, SA-019 | PU-001, PU-003, PU-005, PU-006 | waiver authority, schema-file decision record, production `sdk_layer`, auxiliary imagegen fallback | PR evidence pending implementation. |

## Decision Review Matrix

| Decision Area | Reviewed Position | Result |
| --- | --- | --- |
| Waiver authority | A waiver cannot be self-approved by the implementation agent. It must cite Jamie, the Linear owner or assignee, or a repo-owned named authority source with approver, authority evidence, date, scope, reason, expiry or revisit condition, and follow-up. | Approved. This closes the failure mode where an agent converts a blocked validation gate into an unaudited exception. |
| Concrete schema files | RF-1 should not create concrete schema files unless a canonical schema home is discovered or file-backed schemas are required to keep tests truthful. Any exception requires a schema-file decision record. | Approved. This keeps JSC-329 on doctor-contract proof instead of premature schema stewardship. |
| `sdk_layer` exposure | Known readiness signals must expose `sdk_layer` in production `data.skill_doctor` JSON. Fixture-side mapping is only acceptable for legacy or unknown classes with a reason. | Approved. This makes the SDK layer model consumable by harness clients rather than hidden in tests. |
| Image generation fallback | Image generation is auxiliary. CLI fallback may run only with explicit user authorization and credentials for the configured imagegen backend. Missing imagegen access is not a JSC-329 failure. | Approved. This prevents external artifact friction from blocking the SDK doctor contract. |

## Findings

### Finding 1: `sdk_layer` Language Was Weaker In Plan Than Spec

Severity: Medium
Status: Fixed

Evidence:

- The spec requires known doctor readiness signals to expose `sdk_layer` in production `data.skill_doctor` JSON.
- The plan now states that known checks must carry `sdk_layer` in production JSON and that fixture-only mapping is limited to unknown legacy classes.

Why it mattered:

If the plan allowed test-only layer mapping, the future harness could not consume the layered SDK contract from real doctor output.

### Finding 2: Waiver Authority Needed Recognized Source Rules

Severity: Medium
Status: Fixed

Evidence:

- The spec now lists recognized owner sources for waiver authority.
- The plan requires waiver closeout to include approver, authority source path or link, verbatim authority evidence, date, waived gate, reason, scope, expiry or revisit condition, and follow-up issue or artifact.

Why it mattered:

Without authority-source rules, a waiver would look rigorous while still being self-authored or socially ambiguous.

### Finding 3: Schema-File Exceptions Needed A Decision Record

Severity: Low
Status: Fixed

Evidence:

- The spec now requires a schema-file decision record before RF-1 creates concrete schema files.
- The plan validation gates include a schema-file scope check over schema-like paths and require justification if new schema files appear.

Why it mattered:

Schema files create public contract ownership. JSC-329 should not accidentally expand from doctor payload proof into repository-wide schema governance.

### Finding 4: Imagegen Fallback Needed To Avoid Hardcoding One Credential Shape

Severity: Low
Status: Fixed

Evidence:

- The plan now checks credentials for the configured imagegen backend if fallback is requested.
- The spec treats image generation as blocked auxiliary evidence when credentials or tool access are unavailable.

Why it mattered:

The imagegen surface may not always use one environment variable or provider. The plan should enforce explicit authorization and credential presence without binding JSC-329 to a specific backend.

## Residual Risks

- The exact source of Linear owner or assignee authority must be verified during implementation closeout if a waiver is used.
- The production `sdk_layer` field still requires implementation and focused tests before this contract is proven.
- A canonical schema home may be discovered during implementation; if so, the decision record must explain why RF-1 cannot defer file-backed schema work.
- Image generation remains blocked unless the active environment exposes a built-in image tool or the user authorizes a credentialed CLI fallback.

## Required Follow-Through

- Keep FR-021 through FR-024 aligned between spec and plan during implementation.
- In PU-001, test production `data.skill_doctor` JSON for `sdk_layer` on known readiness classes.
- In PU-005 and PU-006, treat missing waiver authority metadata as a blocked gate.
- In closeout, report imagegen status separately as generated, blocked, or skipped.

