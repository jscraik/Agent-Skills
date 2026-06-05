---
schema_version: 1
artifact_id: sy-spec-2026-06-04-skills-sdk-pu-008-capability-truth
artifact_type: sy-spec
canonical_slug: skills-sdk-pu-008-capability-truth
harness_stage: sy-spec
title: "PU-008: Skills SDK Capability Truth and Pipeline Status Spec"
status: spec_ready_for_plan
date: 2026-06-04
source_trace_plan: .harness/plan/2026-06-04-skills-sdk-pu-008-capability-truth-trace-plan.md
source_pipeline_artifact: artifacts/recommended-skills-sdk-pipeline.html
source_v1_spec: .harness/specs/2026-06-03-skills-sdk-v1-product-spec.md
source_v1_plan: .harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md
source_goal: Docs/goals/skills-sdk-v1-0-product-implementation/state.yaml
origin: user_requested_sy_spec
risk: medium
ui: true
traceability_required: true
repo_mutation_scope: spec_artifact_only
external_mutation_status: not_authorized
---

# PU-008: Skills SDK Capability Truth and Pipeline Status Spec

## Command Summary

BLUF: PU-008 turns the Skills SDK pipeline vision into an executable truth surface. The current browser artifact describes the larger SDK destination, while the current CLI proves only the V1.0 contract layer: check, read-only install preview, risk and receipt output, and honest lifecycle placeholders. This spec defines a capability matrix, status schema, skills-sdk status command, spec and plan closeout encoding, and browser artifact status overlay so humans and agents can tell which SDK lanes are executable, preview-only, placeholder, blocked by missing adapters, deferred, or out of scope.

Decision: Build PU-008 as a status and governance-encoding slice. Do not add registry behavior, marketplace behavior, package signing, sandbox execution, eval execution, real install writes, trust-store mutation, or hosted explorer publishing.

Next Action: Hand this spec to sy-execution-plan or the project planning lane to produce the implementation plan, then execute in a clean worktree from refreshed main.

## Purpose

The purpose of PU-008 is to prevent the broad pipeline design map from being mistaken for current SDK runtime capability. The slice gives the SDK one canonical answer for what is executable now, what is preview-only, what is represented by honest placeholders, what is blocked by missing adapters, what is deferred beyond the current slice, and what is outside the approved scope.

## Problem Statement

The Skills SDK V1.0 implementation created useful executable surfaces, but the surrounding artifacts do not yet speak with one voice. The pipeline HTML shows the destination, the V1.0 goal board records completed slices, the original spec and plan still read like pre-execution artifacts, and the CLI lifecycle command reports placeholders without a full pipeline capability map.

Without PU-008, future agents can overclaim the SDK by reading the browser pipeline as completed product behavior, or underclaim it by ignoring the working check, install-preview, risk, and receipt layer. The fix is a machine-readable capability truth model with command output, tests, and artifact updates that share the same vocabulary.

## Approved Scope

In scope:

- capability status schema for Skills SDK pipeline lanes
- canonical capability matrix mapping pipeline lanes to current truth
- ./bin/ask sdk status command
- ./bin/skills-sdk status wrapper parity
- tests proving status schema, command output, matrix coverage, and HTML coverage
- browser pipeline artifact status overlay or status section
- V1.0 source spec and plan closeout encoding
- clear separation between executable, preview-only, placeholder, blocked-adapter, deferred, and out-of-scope lanes

Out of scope:

- registry implementation
- marketplace implementation
- package signing implementation
- sandbox execution implementation
- eval execution implementation
- real install writes
- trust-store mutation
- hosted docs or Skill Explorer publishing
- GitHub, Linear, tracker, PR, or external service mutation without separate approval

## Current Evidence

| Evidence | Current observation | Spec consequence |
| --- | --- | --- |
| artifacts/recommended-skills-sdk-pipeline.html | Describes broad SDK pipeline sections including author path, lifecycle, release decision matrix, public SDK surface, knowledge engineering, eval ops, compiled package pipeline, emitters, CI gates, and hardening. | Treat as pipeline vision and coverage source, not runtime proof. |
| ./bin/ask sdk --help | Current actions are check, install, and lifecycle. | status must be added as the fourth SDK action. |
| ./bin/ask sdk lifecycle --json --robot | Refs, evals, security adapter, and explorer are optional placeholders; signing and sandbox are blocked/not-run placeholders; feature execution is false. | Capability matrix must preserve this truth and prevent overclaim. |
| Infrastructure/scripts/lib/ask/skills_sdk/* | Existing modules include contracts, risk, install preview, package verify, placeholder lifecycle, and runtime adapters. | capability_status.py should live with existing SDK modules. |
| Infrastructure/tests/test_skills_sdk_* | Existing tests cover V1.0 command/schema/receipt/risk/preview/placeholder behavior. | PU-008 tests must extend this suite and preserve it. |
| Docs/goals/skills-sdk-v1-0-product-implementation/state.yaml | V1.0 goal is closed and references final notes and validation. | Spec and plan should link to this closeout evidence. |

## Affected Surfaces

| Surface | Classification | Required action |
| --- | --- | --- |
| Infrastructure/config/schemas/skills-sdk/capability-status.v1.schema.json | change | Add schema for status output and capability rows. |
| Infrastructure/config/skills-sdk/capability-matrix.v1.json | change | Add canonical matrix for pipeline truth. |
| Infrastructure/scripts/lib/ask/skills_sdk/capability_status.py | change | Add loader, validator-facing normalization, and summary helpers. |
| Infrastructure/scripts/lib/ask/commands/sdk.py | change | Add status parser and dispatcher route. |
| bin/skills-sdk | read_only_or_change_if_needed | Preserve wrapper delegation and confirm status routes through ask sdk. |
| Infrastructure/tests/test_skills_sdk_capability_status.py | change | Add schema, loader, CLI, wrapper, and negative tests. |
| Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py | change | Add coverage and overclaim tests for the HTML pipeline artifact. |
| artifacts/recommended-skills-sdk-pipeline.html | change | Add visible status overlay or section using matrix vocabulary. |
| .harness/specs/2026-06-03-skills-sdk-v1-product-spec.md | change | Add V1.0 implementation status and deferred-lane matrix. |
| .harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md | change | Add final closeout section and remove pre-execution wording for the completed V1.0 slice. |
| Docs/goals/skills-sdk-v1-0-product-implementation/* | read_only | Use as source evidence; do not rewrite goal history unless a validator requires a link refresh. |
| GitHub, Linear, review threads, CI | not_checked | Do not claim readiness for these lanes unless checked during implementation closeout. |

## Functional Requirements

| ID | Requirement |
| --- | --- |
| FR-001 | The SDK MUST define a versioned capability status schema for pipeline capability rows and command output. |
| FR-002 | The SDK MUST maintain a canonical capability matrix with one row per required pipeline lane. |
| FR-003 | The matrix MUST include status, owner surface, feature execution flag, mutation flag, evidence references, next-slice hint, and notes for every row. |
| FR-004 | The status vocabulary MUST include implemented, preview_only, placeholder_optional, placeholder_blocked, blocked_missing_adapter, deferred, and out_of_scope. |
| FR-005 | The ask sdk status command MUST emit schema-valid JSON in robot mode. |
| FR-006 | The skills-sdk status wrapper MUST delegate to the same SDK route and expose equivalent data. |
| FR-007 | The status command MUST summarize executable, preview-only, placeholder, blocked-adapter, deferred, and out-of-scope counts. |
| FR-008 | Capabilities with feature_executed false MUST NOT use status implemented. |
| FR-009 | Capabilities with mutation_performed true MUST be rejected unless the capability is explicitly allowed by this spec. |
| FR-010 | The browser pipeline artifact MUST display the same status vocabulary used by the matrix. |
| FR-011 | The browser pipeline artifact MUST include capability ids or data attributes that tests can compare against the matrix. |
| FR-012 | The V1 product spec MUST include a V1.0 status section that distinguishes current executable, preview-only, placeholder, blocked-adapter, deferred, and out-of-scope lanes. |
| FR-013 | The V1.0 implementation plan MUST include final closeout evidence and no longer describe PU-001 through PU-007 as future work. |
| FR-014 | PU-008 MUST preserve the existing check, install-preview, and lifecycle behavior and tests. |

## Non-Functional Requirements

| ID | Requirement |
| --- | --- |
| NFR-001 | Status output MUST be deterministic for stable diffs and test fixtures. |
| NFR-002 | Status output MUST be machine-readable without scraping prose. |
| NFR-003 | Human output MUST be concise and must not imply deferred capabilities are executable. |
| NFR-004 | Capability evidence references MUST point to local commands, files, goal receipts, or artifact paths rather than private chat context. |
| NFR-005 | The slice MUST avoid new external service calls in default validation. |
| NFR-006 | The slice MUST preserve the ask CLI as the repo control plane. |

## Capability Rows

| Capability | Required initial status | Evidence expectation |
| --- | --- | --- |
| authoring | implemented | Existing canonical skill source and ask skills evidence. |
| check | implemented | ./bin/ask sdk check target --json --robot. |
| manifest_schema | implemented | Schema fixture tests. |
| receipt_schema | implemented | Check receipt and schema spine tests. |
| risk_classification | implemented | Risk classifier tests and check output. |
| install_preview | preview_only | ./bin/ask sdk install target --preview --json --robot. |
| lockfile_preview | preview_only | Install preview output and no-write tests. |
| real_install | deferred | Explicit V1.0 no-write boundary. |
| trust_store | deferred | Explicit no mutation boundary. |
| refs_ingestion | placeholder_optional | Lifecycle placeholder output. |
| evals | placeholder_optional | Lifecycle placeholder output. |
| package_verify | implemented_or_preview_only | Existing package verify surface must be checked during implementation. |
| signing | placeholder_blocked | Lifecycle placeholder output. |
| sandbox | blocked_missing_adapter | High-risk lifecycle fail-closed output. |
| security_adapter | placeholder_optional | Lifecycle placeholder output. |
| static_docs | preview_only_or_deferred | Pipeline artifact and spec closeout must classify exact scope. |
| skill_explorer | placeholder_optional | Lifecycle placeholder output unless PU-008 proves static read-only surface only. |
| schema_registry | deferred | No public registry surface in PU-008. |
| registry | out_of_scope | Explicit non-goal. |
| marketplace | out_of_scope | Explicit non-goal. |
| publish | out_of_scope | Explicit non-goal. |
| rollback | deferred | No install mutation means no runtime rollback behavior. |
| uninstall | deferred | No install mutation means no runtime uninstall behavior. |
| compiled_package_pipeline | deferred | Pipeline vision only unless existing package verify proves a narrower status. |
| emitters | deferred | Pipeline vision only unless existing code proves a narrower status. |
| ci_adoption_gates | deferred | No CI lane claim without live PR evidence. |
| package_hardening | deferred | Later hardening slice. |

## Interfaces

### CLI Interface

./bin/ask sdk status --json --robot MUST return the standard ask JSON envelope with a data.skills_sdk_status payload.

The payload MUST include schema_version, status, capabilities, summary, source_artifacts, validation_commands, and agent_summary.

./bin/skills-sdk status --json --robot MUST expose equivalent capability data by delegating through the ask sdk status route.

### HTML Interface

artifacts/recommended-skills-sdk-pipeline.html MUST display a visible pipeline status section or overlay. It MUST not require a network service to inspect the status. It SHOULD include stable capability ids in attributes or text so tests can compare the HTML artifact with the JSON matrix.

### Spec And Plan Interface

The V1 product spec and V1.0 plan MUST include a closeout/status section that points to the goal board, receipts, implementation notes, and PU-008 capability matrix. They MUST retain historical context while making current status unambiguous.

## Acceptance Criteria

| ID | Given | When | Then |
| --- | --- | --- | --- |
| AC-001 | The capability matrix exists | tests load it | every required capability row is present exactly once. |
| AC-002 | A row has feature_executed false | validation runs | status implemented is rejected. |
| AC-003 | A row has mutation_performed true | validation runs | the row is rejected unless explicitly allowed by PU-008. |
| AC-004 | The user runs ./bin/ask sdk status --json --robot | command exits | output is schema-valid and includes summary counts. |
| AC-005 | The user runs ./bin/skills-sdk status --json --robot | command exits | output is equivalent to the ask sdk status payload. |
| AC-006 | The HTML pipeline artifact is parsed | tests compare it with the matrix | every major pipeline section maps to at least one capability row. |
| AC-007 | The HTML artifact displays a deferred capability | tests inspect the status label | the label does not imply execution, installation, publishing, signing, sandboxing, or registry availability. |
| AC-008 | The V1.0 plan is inspected | stale-language tests run | it no longer presents PU-001 through PU-007 as future work. |
| AC-009 | The V1 spec is inspected | stale-language tests run | it includes a V1.0 implementation status matrix and keeps future V1.x work separate. |
| AC-010 | Existing SDK tests run | validation completes | check, install-preview, risk, schema, and placeholder behavior remain unchanged except for additive status surfaces. |

## Validation Plan

| Command | Proves | Does not prove |
| --- | --- | --- |
| python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py Docs/goals/skills-sdk-v1-0-product-implementation | Goal board structure remains valid. | Current PR, CI, tracker, or review state. |
| ./bin/ask sdk status --json --robot | SDK status route emits current local capability truth. | External service readiness. |
| ./bin/skills-sdk status --json --robot | Wrapper parity for the status route. | Global installation. |
| uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q | Matrix, schema, command, and HTML coverage rules. | Full repo health. |
| uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_schema_spine.py Infrastructure/tests/test_skills_sdk_check_facade.py Infrastructure/tests/test_skills_sdk_install_preview.py Infrastructure/tests/test_skills_sdk_placeholder_lifecycle.py Infrastructure/tests/test_pr_skills_sdk_artifacts.py -q | Existing SDK behavior remains intact. | Remote CI readiness. |
| bash scripts/validate-codestyle.sh | Repo codestyle gate. | Mergeability. |
| ./bin/ask repo validate --json --robot | Repo validation gate. | Review-thread closure or tracker state. |

## Risks

| Risk | Mitigation |
| --- | --- |
| The matrix becomes another stale artifact. | Generate command output from the matrix and test matrix-to-HTML coverage. |
| The HTML pipeline still reads as full capability. | Add visible status labels and tests for deferred/out-of-scope lanes. |
| Status vocabulary drifts from lifecycle receipts. | Reuse existing lifecycle status truth where possible and test known lifecycle rows. |
| Spec/plan closeout edits rewrite history. | Add closeout/status sections instead of erasing historical planning context. |
| Dirty primary checkout contaminates implementation. | Start PU-008 from clean main in a separate feature worktree. |

## Rollback

Rollback is ordinary git revert of the PU-008 branch. Because PU-008 must not perform install writes, trust-store mutation, publishing, registry mutation, signing, sandbox execution, or external tracker mutation, rollback should only remove the status schema, matrix, command route, tests, and artifact/doc updates.

## Blocked Inputs

No blocker prevents planning. Implementation should stop for owner input only if the team wants PU-008 to also implement a real capability beyond status truth, because that would exceed this spec.

## Next Stage

Recommended next stage: sy-execution-plan or the repository's governed implementation planning lane.

Handoff objective: implement PU-008 as a bounded capability truth/status slice on branch codex/skills-sdk-pu-008-capability-truth in worktree /private/tmp/agent-skills-skills-sdk-pu-008-capability-truth, based on clean refreshed main.
