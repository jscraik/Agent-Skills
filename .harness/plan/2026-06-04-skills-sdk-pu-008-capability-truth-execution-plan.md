---
schema_version: 1
artifact_id: sy-execution-plan-2026-06-04-skills-sdk-pu-008-capability-truth
artifact_type: sy-execution-plan
canonical_slug: skills-sdk-pu-008-capability-truth
harness_stage: sy-execution-plan
title: "PU-008: Skills SDK Capability Truth and Pipeline Status Execution Plan"
status: execution_plan_ready
date: 2026-06-04
source_spec: .harness/specs/2026-06-04-skills-sdk-pu-008-capability-truth-spec.md
source_trace_plan: .harness/plan/2026-06-04-skills-sdk-pu-008-capability-truth-trace-plan.md
source_pipeline_artifact: artifacts/recommended-skills-sdk-pipeline.html
source_v1_spec: .harness/specs/2026-06-03-skills-sdk-v1-product-spec.md
source_v1_plan: .harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md
source_goal: Docs/goals/skills-sdk-v1-0-product-implementation/state.yaml
origin: user_requested_sy_execution_plan
risk: medium
traceability_required: true
repo_mutation_scope: implementation_plan_artifact_only
external_mutation_status: not_authorized
---

# PU-008: Skills SDK Capability Truth and Pipeline Status Execution Plan

## Command Summary

BLUF: Implement PU-008 as a bounded capability-truth slice. The first code change should be the canonical matrix and schema. The second should be the runtime status loader and CLI route. The third should be the browser pipeline and V1.0 closeout updates that consume the same vocabulary. The final step is validation that proves local SDK truth, wrapper parity, HTML coverage, and regression safety without claiming PR, CI, review-thread, tracker, registry, marketplace, signing, sandbox, eval, or install-write readiness.

Decision: Use a clean feature worktree and keep the primary checkout as an orientation surface. Do not mix this implementation into the current dirty branch.

Next Action: Create or refresh main, create branch codex/skills-sdk-pu-008-capability-truth, and check out worktree /private/tmp/agent-skills-skills-sdk-pu-008-capability-truth. Then start Slice 1 with the status schema and matrix.

## Stage Contract

schema_version: 1

stage: sy-execution-plan

target: PU-008: Skills SDK Capability Truth and Pipeline Status

execution_plan: this artifact

next_stage: governed implementation in a feature worktree

## Evidence Checked

| Evidence | Observation | Planning consequence |
| --- | --- | --- |
| .harness/specs/2026-06-04-skills-sdk-pu-008-capability-truth-spec.md | Approved scope is a truth/status slice with ask sdk status, skills-sdk status, matrix, schema, tests, HTML overlay, and V1.0 closeout encoding. | Plan is implementation sequencing only; no new product capability execution is added. |
| .harness/plan/2026-06-04-skills-sdk-pu-008-capability-truth-trace-plan.md | Trace plan already maps pipeline lanes to capability rows and required validation. | Reuse row list, vocabulary, validation gates, and worktree handoff. |
| Infrastructure/scripts/lib/ask/commands/sdk.py | Current SDK actions are check, install, and lifecycle; dispatch is centralized in this file. | Add status parser and dispatcher here. |
| bin/skills-sdk | Wrapper delegates directly to Infrastructure/bin/ask sdk. | Wrapper parity should work once ask sdk status exists; add tests to prove it. |
| Infrastructure/scripts/lib/ask/skills_sdk/placeholder_lifecycle.py | Lifecycle placeholder receipts already encode surfaces, risk tiers, feature_executed false, and mutation-free behavior. | Status rows for refs, evals, signing, sandbox, security adapter, and explorer should align with this module. |
| Infrastructure/scripts/lib/ask/skills_sdk/package_verify.py | Package verification exists as a local package safety surface. | During implementation, classify package_verify from live tests/code as implemented or preview_only, then encode the exact status in the matrix. |
| UBIQUITOUS_LANGUAGE.md | ask CLI, Feature Worktree, Runtime Projection, and Canonical Skill Source have precise repo meanings. | Use repo vocabulary consistently and avoid editing generated runtime projections. |
| Current git status | Primary checkout is dirty with unrelated skill-system/plugin-root work plus the new PU-008 planning artifacts. | Implementation must start from a separate clean worktree. |

## Slice Boundaries

| Slice | Purpose | Primary output | Required proof before next slice |
| --- | --- | --- | --- |
| 0 | Prepare isolated implementation surface. | Clean feature worktree and branch from refreshed main. | git status --short --branch in the worktree shows only intended PU-008 changes after setup. |
| 1 | Define the capability truth contract. | Schema and canonical matrix files. | Matrix schema tests pass and every required capability id appears exactly once. |
| 2 | Expose status through runtime code. | capability_status.py, ask sdk status, and wrapper parity. | CLI JSON validates and wrapper output matches the ask route. |
| 3 | Bind browser pipeline artifact to matrix truth. | Visible status section or overlay in recommended-skills-sdk-pipeline.html. | HTML tests prove every major pipeline section maps to matrix capability ids and uses approved vocabulary. |
| 4 | Back-encode V1.0 closeout into harness docs. | V1.0 spec and plan closeout/status sections. | Tests or focused scans prove the docs distinguish completed V1.0 surfaces from future V1.x work. |
| 5 | Run final local validation and closeout. | Validation evidence and PR-ready local state. | Focused SDK tests, existing SDK tests, codestyle, and repo validation report pass or clearly classified blockers. |

## Files Likely To Change

| Path | Intended change |
| --- | --- |
| Infrastructure/config/schemas/skills-sdk/capability-status.v1.schema.json | Add the versioned schema for capability rows and command payload. |
| Infrastructure/config/skills-sdk/capability-matrix.v1.json | Add the canonical status matrix for PU-008 capability truth. |
| Infrastructure/scripts/lib/ask/skills_sdk/capability_status.py | Add deterministic matrix loading, validation-facing normalization, summary counts, and agent summary output. |
| Infrastructure/scripts/lib/ask/commands/sdk.py | Add status parser and dispatch route. |
| Infrastructure/tests/test_skills_sdk_capability_status.py | Add schema, matrix, CLI, wrapper parity, and negative tests. |
| Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py | Add HTML matrix coverage and overclaim-prevention tests. |
| artifacts/recommended-skills-sdk-pipeline.html | Add visible capability status section or overlay with stable capability ids. |
| .harness/specs/2026-06-03-skills-sdk-v1-product-spec.md | Add V1.0 status and deferred-lane closeout section. |
| .harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md | Add final closeout section and mark PU-001 through PU-007 as completed historical slices. |

## Files That Must Not Change In This Slice

| Path or surface | Boundary |
| --- | --- |
| .agents/skills/** | Runtime Projection; do not hand-edit. |
| skills-system/** unrelated to PU-008 | Existing dirty work in the primary checkout; leave untouched unless refreshed from clean main in the feature worktree for direct PU-008 need. |
| Plugins/** | No plugin or skill-factory changes are part of PU-008. |
| Trust stores, user runtime links, global skill installs | PU-008 is status-only and must not mutate them. |
| GitHub, Linear, review threads, CI settings | External mutation is outside this plan without a separate approval. |

## Slice 0: Worktree Setup

1. In the primary checkout, record current state without staging unrelated work: git status --short --branch.
2. Refresh local main: git fetch origin main.
3. Create the feature worktree: git worktree add /private/tmp/agent-skills-skills-sdk-pu-008-capability-truth -b codex/skills-sdk-pu-008-capability-truth origin/main.
4. Copy or recreate only the approved PU-008 trace/spec/execution planning artifacts into the feature worktree if they are not already on main.
5. Verify the worktree is isolated: git status --short --branch.

Stop condition: If the feature worktree cannot be created cleanly, stop before editing code and report the exact git blocker.

Rollback: Remove the feature worktree and branch only after confirming no intended PU-008 changes live solely there.

## Slice 1: Capability Schema And Matrix

1. Add Infrastructure/config/schemas/skills-sdk/capability-status.v1.schema.json.
2. Add Infrastructure/config/skills-sdk/capability-matrix.v1.json with deterministic ordering and the approved status vocabulary: implemented, preview_only, placeholder_optional, placeholder_blocked, blocked_missing_adapter, deferred, and out_of_scope.
3. Include every required capability id from the spec: authoring, check, manifest_schema, receipt_schema, risk_classification, install_preview, lockfile_preview, real_install, trust_store, refs_ingestion, evals, package_verify, signing, sandbox, security_adapter, static_docs, skill_explorer, schema_registry, registry, marketplace, publish, rollback, uninstall, compiled_package_pipeline, emitters, ci_adoption_gates, and package_hardening.
4. Encode each row with capability id, title, status, owner surface, feature_executed, mutation_performed, evidence references, next-slice hint, and notes.
5. Add tests first or alongside the matrix using uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_capability_status.py -q.

Required assertions:

| Given | Should prove |
| --- | --- |
| Matrix is loaded | Every required capability id appears exactly once. |
| Row has feature_executed false | Status cannot be implemented. |
| Row has mutation_performed true | The row is rejected for PU-008 unless explicitly allow-listed by the schema/test. |
| Evidence references are present | Every row points to local commands, files, goal receipts, or artifacts. |
| Status vocabulary is loaded | Unknown statuses are rejected. |

Stop condition: If a capability cannot be honestly classified from current repo evidence, set its status to deferred with a next-slice hint rather than upgrading the claim.

Rollback: Remove the schema, matrix, and tests from this slice.

## Slice 2: Runtime Status Command

1. Add Infrastructure/scripts/lib/ask/skills_sdk/capability_status.py.
2. Implement a small, deterministic loader that loads the matrix, validates invariant rules, computes summary counts by status, includes source_artifacts, validation_commands, and agent_summary, and keeps output stable for fixture-style assertions.
3. Add status to Infrastructure/scripts/lib/ask/commands/sdk.py.
4. Confirm the ask route with ./bin/ask sdk status --json --robot.
5. Confirm wrapper parity with ./bin/skills-sdk status --json --robot.
6. Add tests in Infrastructure/tests/test_skills_sdk_capability_status.py for ask route success, JSON envelope shape, payload schema shape, summary counts, wrapper parity, and invariant failures for invalid fixture rows.

Stop condition: If the ask envelope structure differs from the spec expectation, follow the existing ask command envelope convention and record the exact shape in the execution notes or closeout.

Rollback: Remove the route and loader; keep the schema/matrix branch changes only if Slice 1 is still useful and passing.

## Slice 3: Browser Pipeline Artifact Status

1. Update artifacts/recommended-skills-sdk-pipeline.html with a visible status section or overlay.
2. Use stable capability ids that tests can compare against the matrix, preferably as data-capability-id attributes and visible labels.
3. Keep the artifact static and local-file friendly. It must not require a dev server or external network call for status inspection.
4. Add Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py to prove every major pipeline section maps to at least one capability id, every capability id referenced in HTML exists in the matrix, status labels come from the approved vocabulary, and deferred or out-of-scope labels do not imply install writes, publishing, registry availability, signing, sandbox execution, or eval execution.

Validation: uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q.

Stop condition: If the current HTML structure is too brittle for fine-grained parsing, add one explicit status table near the top and test that table instead of rewriting the entire artifact.

Rollback: Revert only the HTML status section and its test.

## Slice 4: V1.0 Spec And Plan Closeout Encoding

1. Update .harness/specs/2026-06-03-skills-sdk-v1-product-spec.md with a V1.0 implementation status section that names completed executable surfaces, preview-only surfaces, placeholder and blocked-adapter surfaces, deferred and out-of-scope surfaces, and links to the PU-008 capability matrix and V1.0 goal board.
2. Update .harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md with a final closeout section that preserves historical planning context, marks PU-001 through PU-007 as completed historical slices, points at final validation evidence and implementation notes, and separates local code/test truth from PR, CI, review-thread, tracker, and merge readiness.
3. Add focused tests or scans to catch stale future-tense claims in the updated closeout sections. Prefer a Python test in Infrastructure/tests/test_skills_sdk_capability_status.py if the assertion is tightly related to PU-008.

Validation: uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_capability_status.py -q.

Stop condition: Do not erase the history of the original spec/plan. Add closeout/status sections and clarify current state.

Rollback: Revert the closeout sections and their focused tests.

## Slice 5: Final Validation And Handoff

Run validation from the PU-008 feature worktree in this order:

1. python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py Docs/goals/skills-sdk-v1-0-product-implementation
2. ./bin/ask sdk status --json --robot
3. ./bin/skills-sdk status --json --robot
4. uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q
5. uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_schema_spine.py Infrastructure/tests/test_skills_sdk_check_facade.py Infrastructure/tests/test_skills_sdk_install_preview.py Infrastructure/tests/test_skills_sdk_placeholder_lifecycle.py Infrastructure/tests/test_pr_skills_sdk_artifacts.py -q
6. bash scripts/validate-codestyle.sh
7. ./bin/ask repo validate --json --robot

Closeout must report each lane as pass, fail, or blocked. Local validation does not prove external PR, CI, review-thread, tracker, merge, deployment, marketplace, registry, or hosted explorer readiness.

## Review And Green Sweep Handoff

After implementation validation passes locally:

1. Create a PR from codex/skills-sdk-pu-008-capability-truth.
2. Run the project PR green-sweep lane if requested for this slice.
3. Triage review feedback by ownership: introduced by PU-008 patch, pre-existing, unrelated dirty worktree, or environment/tooling failure.
4. Do not claim merge readiness until the live PR, CI, review-thread, and mergeability lanes are checked in the same closeout window.

## Open Risks

| Risk | Control |
| --- | --- |
| Capability matrix becomes stale. | Generate status command output from the matrix and test matrix-to-HTML coverage. |
| Browser artifact continues to read as full product availability. | Add visible labels and tests for deferred/out-of-scope rows. |
| V1.0 spec/plan edits rewrite history. | Add closeout/status sections instead of deleting historical context. |
| Wrapper parity is assumed from delegation. | Test ./bin/skills-sdk status --json --robot directly. |
| Package verification classification is ambiguous. | Classify it from live code and tests during Slice 1; choose the lower-authority status if evidence is mixed. |
| Dirty primary checkout contaminates implementation. | Work only in the clean feature worktree for code changes. |

## Rollback Plan

Rollback is an ordinary git revert of the PU-008 branch or selected slice commits. Because PU-008 must not mutate install state, trust stores, registry, marketplace, signing keys, sandbox providers, hosted explorers, or external trackers, rollback should only remove local schema, matrix, code, tests, HTML status labels, and harness closeout sections.

## Completion Criteria

PU-008 implementation is complete when:

- ./bin/ask sdk status --json --robot emits schema-valid capability truth.
- ./bin/skills-sdk status --json --robot emits equivalent capability data.
- Every required capability row is present exactly once.
- No false execution or mutation claim can pass tests.
- The browser pipeline artifact displays the same status vocabulary and capability ids.
- The V1.0 spec and plan encode closeout status clearly.
- Existing SDK behavior tests still pass.
- Repo validation gates either pass or have a classified blocker with evidence.

## Next Stage

Recommended next stage: governed implementation in codex/skills-sdk-pu-008-capability-truth using /private/tmp/agent-skills-skills-sdk-pu-008-capability-truth.
