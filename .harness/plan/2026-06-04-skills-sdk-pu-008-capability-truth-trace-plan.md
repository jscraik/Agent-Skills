---
schema_version: 1
artifact_id: sy-trace-plan-2026-06-04-skills-sdk-pu-008-capability-truth
artifact_type: sy-trace-plan
canonical_slug: skills-sdk-pu-008-capability-truth
harness_stage: sy-trace-plan
title: "PU-008: Skills SDK Capability Truth and Pipeline Status Trace Plan"
status: trace_ready_for_work
date: 2026-06-04
source_pipeline_artifact: artifacts/recommended-skills-sdk-pipeline.html
source_spec: .harness/specs/2026-06-03-skills-sdk-v1-product-spec.md
source_plan: .harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md
source_goal: Docs/goals/skills-sdk-v1-0-product-implementation/state.yaml
origin: user_requested_sy_trace_plan
risk: medium
traceability_required: true
repo_mutation_scope: planning_artifact_only
external_mutation_status: not_authorized
---

# PU-008: Skills SDK Capability Truth and Pipeline Status Trace Plan

## Command Summary

BLUF: PU-008 should create the truth bridge between the broad Skills SDK pipeline vision and the current executable SDK surface. The browser artifact at `artifacts/recommended-skills-sdk-pipeline.html` describes the target pipeline, while the current SDK exposes `check`, read-only `install --preview`, and honest lifecycle placeholders. This slice should add a machine-readable capability matrix and `skills-sdk status` command, then back-encode the spec, plan, and browser pipeline artifact so future agents can see which capabilities are executable, preview-only, placeholder, blocked by missing adapters, deferred, or out of scope.

Decision: Plan PU-008 as a truth-surface and closeout-encoding slice. Do not add registry, marketplace, package signing, sandbox execution, eval execution, real install writes, or hosted explorer publishing in this slice.

Next action: Start a clean worktree from `main`, add the capability status schema and matrix, expose `ask sdk status` plus `bin/skills-sdk status`, then update the spec, plan, and pipeline HTML with the same status vocabulary.

## Source Evidence Checked

| Evidence | Observation | Use in PU-008 |
| --- | --- | --- |
| `artifacts/recommended-skills-sdk-pipeline.html` | Contains broad pipeline sections covering author path, lifecycle, release gates, public SDK surface, knowledge, eval ops, compiled package pipeline, emitters, CI/adoption, and hardening. | Source list for capability rows. |
| `./bin/ask sdk --help` | Current SDK actions are `check`, `install`, and `lifecycle`. | Defines executable command surface already present. |
| `./bin/ask sdk lifecycle --json --robot` | Refs, evals, security adapter, and explorer report `skipped_optional`; signing and sandbox report `not_run`; every lifecycle surface has `feature_executed: false`. | Defines placeholder and blocked-adapter status truth. |
| `Infrastructure/scripts/lib/ask/skills_sdk/*` | Existing SDK modules cover conformance, contracts, install preview, package contracts, package verify, placeholder lifecycle, risk, and runtime adapters. | Defines likely owners for status generation. |
| `Infrastructure/tests/test_skills_sdk_*` | Existing focused tests cover schema spine, check facade, risk classifier, install preview, placeholder lifecycle, boundaries, scaffold, and package artifacts. | Defines regression suite to preserve. |
| `Docs/goals/skills-sdk-v1-0-product-implementation/state.yaml` | Goal is closed and references implementation notes, browser notes, and final validation. | Source of V1.0 closeout evidence to encode back into plan/spec. |

## Traceability Map

| Requirement | Source | Owner Surface | Artifact | Validation | Status |
| --- | --- | --- | --- | --- | --- |
| Map every major pipeline lane to a runtime status. | `recommended-skills-sdk-pipeline.html` sections | `skills-sdk status` | capability matrix JSON | matrix schema test | planned |
| Distinguish executable, preview-only, placeholder, blocked-adapter, deferred, and out-of-scope capabilities. | Current SDK lifecycle output | SDK status model | capability status schema | status command JSON test | planned |
| Show current executable SDK layer. | `./bin/ask sdk --help` | `ask sdk`, `bin/skills-sdk` | status output | CLI smoke and parser tests | partially covered today |
| Tie install preview to pipeline truth. | `sdk install --preview` | install preview module | capability row | no-write tests | covered by current tests, needs matrix row |
| Tie lifecycle placeholders to pipeline truth. | `sdk lifecycle` | placeholder lifecycle module | capability rows | placeholder lifecycle tests | covered by current tests, needs matrix rows |
| Back-encode V1.0 implementation status into the plan. | V1.0 goal board and receipts | harness plan | updated closeout section | stale-language validator | planned |
| Back-encode V1.0 implementation status into the spec. | V1 spec plus V1.0 goal board | harness spec | implementation status matrix | stale-language validator | planned |
| Prevent browser artifact overclaim. | pipeline HTML | HTML artifact | lane status overlay or section | HTML artifact test | planned |
| Keep browser-notes truth separate from live MDX preview truth. | goal board artifact block | implementation notes | state and notes references | goal board validator | partially covered today |
| Avoid claiming registry, marketplace, signing, sandbox, eval execution, real install writes, or hosted explorer publishing in PU-008. | V1.0 scope boundary | SDK status output | deferred/out-of-scope rows | negative tests | planned |

## Proposed Capability Status Vocabulary

| Status | Meaning |
| --- | --- |
| `implemented` | Command or artifact path exists and has validation evidence. |
| `preview_only` | The SDK can model intended state without mutating project, workspace, global, trust-store, registry, or hosted surfaces. |
| `placeholder_optional` | The SDK reports the lane honestly as reserved, skipped, or optional for the current risk tier. |
| `placeholder_blocked` | The SDK reports the lane honestly as unavailable for the current risk tier. |
| `blocked_missing_adapter` | The selected risk tier requires an adapter that is absent or unavailable. |
| `deferred` | The lane is part of the broader SDK roadmap, but outside the approved PU-008 scope. |
| `out_of_scope` | The lane is explicitly not part of V1.0 or PU-008. |

## Required Capability Rows

PU-008 should cover at least these rows: authoring, check, manifest_schema, receipt_schema, risk_classification, install_preview, lockfile_preview, real_install, trust_store, refs_ingestion, evals, package_verify, signing, sandbox, security_adapter, static_docs, skill_explorer, schema_registry, registry, marketplace, publish, rollback, uninstall, compiled_package_pipeline, emitters, ci_adoption_gates, and package_hardening.

Each row should include a capability id, status, owner surface, `feature_executed`, `mutation_performed`, evidence commands or artifacts, next-slice hint, and operator notes.

## Proposed File Changes For PU-008

| Path | Purpose |
| --- | --- |
| `Infrastructure/config/schemas/skills-sdk/capability-status.v1.schema.json` | Schema for capability status rows and status output. |
| `Infrastructure/config/skills-sdk/capability-matrix.v1.json` | Canonical matrix mapping pipeline lanes to current runtime truth. |
| `Infrastructure/scripts/lib/ask/skills_sdk/capability_status.py` | Runtime loader and normalizer for status output. |
| `Infrastructure/scripts/lib/ask/commands/sdk.py` | Add `status` subcommand. |
| `bin/skills-sdk` | Existing wrapper should delegate `status` through `./bin/ask sdk status`. |
| `Infrastructure/tests/test_skills_sdk_capability_status.py` | Schema, loader, command, and negative tests. |
| `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py` | HTML pipeline capability coverage and overclaim tests. |
| `.harness/specs/2026-06-03-skills-sdk-v1-product-spec.md` | Add V1.0 implementation status matrix. |
| `.harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md` | Add final closeout status and remove pre-execution wording for the completed V1.0 slice. |
| `artifacts/recommended-skills-sdk-pipeline.html` | Add visible capability status overlay or section using the same vocabulary. |

## Acceptance Criteria

| ID | Requirement |
| --- | --- |
| PU008-SA-001 | Every major section in `recommended-skills-sdk-pipeline.html` maps to at least one capability row. |
| PU008-SA-002 | Every capability row has a status, evidence reference, owner surface, and next slice hint. |
| PU008-SA-003 | No capability with `feature_executed: false` is marked `implemented`. |
| PU008-SA-004 | `./bin/ask sdk status --json --robot` emits schema-valid capability truth. |
| PU008-SA-005 | `./bin/skills-sdk status --json --robot` emits equivalent capability truth through the wrapper. |
| PU008-SA-006 | The spec and plan include V1.0 closeout status and no longer describe the completed V1.0 slice as pre-execution work. |
| PU008-SA-007 | The browser pipeline artifact shows current executable, preview, placeholder, blocked-adapter, deferred, and out-of-scope lanes. |
| PU008-SA-008 | Registry, marketplace, signing, sandbox execution, eval execution, real install writes, and hosted explorer publishing remain deferred or out of scope unless a later approved slice changes that boundary. |

## Validation Plan

| Command | Expected outcome |
| --- | --- |
| `python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py Docs/goals/skills-sdk-v1-0-product-implementation` | pass |
| `./bin/ask sdk status --json --robot` | pass with schema-valid capability matrix |
| `./bin/skills-sdk status --json --robot` | pass with equivalent data payload |
| `uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q` | pass |
| `uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_schema_spine.py Infrastructure/tests/test_skills_sdk_check_facade.py Infrastructure/tests/test_skills_sdk_install_preview.py Infrastructure/tests/test_skills_sdk_placeholder_lifecycle.py Infrastructure/tests/test_pr_skills_sdk_artifacts.py -q` | pass |
| `bash scripts/validate-codestyle.sh` | pass |
| `./bin/ask repo validate --json --robot` | pass |

## Worktree Handoff

| Field | Value |
| --- | --- |
| Branch | `codex/skills-sdk-pu-008-capability-truth` |
| Worktree | `/private/tmp/agent-skills-skills-sdk-pu-008-capability-truth` |
| Base | clean, refreshed `main` |
| First implementation step | Add capability status schema and matrix before changing spec, plan, or HTML. |
| Stop condition | Any output implies deferred capability execution without command proof. |

## Out Of Scope For PU-008

- Registry implementation.
- Marketplace implementation.
- Package signing implementation.
- Sandbox execution implementation.
- Eval execution implementation.
- Real install writes.
- Trust-store mutation.
- Hosted docs or Skill Explorer publishing.
- Tracker, PR, or external service mutation without explicit owner approval.

## Closeout Proof Required

PU-008 is ready for handoff only when the PR evidence can show:

- Capability matrix validates.
- `ask sdk status` and `skills-sdk status` agree.
- Pipeline HTML contains the status vocabulary and capability IDs.
- Spec and plan reference the V1.0 closeout evidence.
- Existing SDK behavior tests still pass.
- Repo validation reports no required failures.
