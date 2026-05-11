---
schema_version: 1
artifact_id: agent-skills-he-trust-defect-repair-plan
artifact_type: he-plan
canonical_slug: agent-skills-he-trust-defect-repair
title: HE Trust Defect Repair Plan
harness_stage: he-plan
status: implemented
date: 2026-05-09
traceability_required: false
origin: .harness/specs/2026-05-09-agent-skills-he-trust-defect-repair-spec.md
linear_issue: JSC-299
linear_status: created
linear_mutation_status: created
linear_milestone: HE Authority And Proof Hardening
risk: architecture_sensitive
depth: deep
ui: false
---

# HE Trust Defect Repair Plan

## Mode Decision

```yaml
interactive_status: autonomous_assumption
selection_evidence:
  - .harness/specs/2026-05-09-agent-skills-he-trust-defect-repair-spec.md
  - .harness/review/2026-05-10-agent-skills-he-trust-defect-repair-spec-technical-review.md
  - .harness/linear/2026-05-09-agent-skills-he-authority-proof-hardening-linear-plan.md
route: he-plan
stage: he-plan
scope: "Bounded implementation plan for the local-only Now slice: [agent-skills] Repair HE trust defects before new capability."
traceability: "live_linear_issue_jsc_299_created_for_focused_slice"
validation: "plan artifact lints, focused recapture commands, and he-plan strict audit"
safe_to_continue: true
blocked_reason: "Implementation was authorized and locally validated; plugin-wide Codex-runner release confidence remains blocked as follow-up."
```

## Executive Plan Summary

This plan implements only the first HE Authority And Proof Hardening slice:
repair the current trust defects before adding any new Harness Engineering
capability.

Fresh pre-plan recapture on 2026-05-10 changes the implementation shape from
the older draft plan:

- SA-001 packaging hygiene still fails and is the only active implementation
  blocker.
- SA-002 and SA-008 eval-report not-run closure behavior currently pass.
- SA-003 missing-`ask` degraded-mode behavior currently passes through focused
  release-runner tests.
- SA-004 required router sample happy path and negative summary behavior
  currently pass.

The plan therefore does not redesign working validators. It clears generated
cache artifacts, preserves the passing trust checks with fresh evidence, runs a
recurrence check after representative validation, and then writes the closure
eval artifact.

No Linear mutation, new HE stage, threat-model skill, tool-audit skill, evidence
ledger, artifact index, or parallel-agent workflow is included.

## Source Evidence

| Source | Evidence Used | Planning Impact |
| --- | --- | --- |
| `.harness/specs/2026-05-09-agent-skills-he-trust-defect-repair-spec.md` | Defines SA-001 through SA-008, local-only Linear closure rules, pre-plan recapture, and defect-specific owner surfaces. | Primary implementation contract. |
| `.harness/review/2026-05-10-agent-skills-he-trust-defect-repair-spec-technical-review.md` | Approves the spec for `he-plan` with active SA-001 blocker and SA-004 closure proof requirements. | Confirms planning may proceed but implementation closure is not approved. |
| `.harness/linear/2026-05-09-agent-skills-he-authority-proof-hardening-linear-plan.md` | Routes this as the proposed Now parent issue and keeps broader work in Next/Later. | Confirms this plan covers only the first repair slice. |
| `Plugins/harness-engineering/scripts/check_packaging_hygiene.py` | Rejects generated clutter under the HE plugin tree, including `__pycache__` and `.pyc`. | Source of truth for SA-001. |
| `Plugins/harness-engineering/skills/he-eval-report/tests/test_validate_eval_report.py` | Contains the not-run side-effect validator fixture and currently passes. | Preserve for SA-002 and SA-008. |
| `Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py` | Contains missing/non-executable `ask` tests and router-sample failing-gate summary test. | Preserve for SA-003 and SA-004 negative-path proof. |
| `Plugins/harness-engineering/scripts/validate_routing_map.py` | Owns router sample execution. | Preserve ownership; do not duplicate routing logic in the release runner. |
| `Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py` | Classifies missing `ask` and records `router_samples` failing gate when required sample proof fails. | Preserve release confidence accounting. |

## Pre-Plan Recapture

| Check | Command | Result | Plan Decision |
| --- | --- | --- | --- |
| Packaging hygiene | `bash -lc 'python3 Plugins/harness-engineering/scripts/check_packaging_hygiene.py --json'` | fail | PU-001 must clear generated cache artifacts and prove they do not recur after representative validation. |
| Eval-report validator | `bash -lc 'python3 -m pytest Plugins/harness-engineering/skills/he-eval-report/tests/test_validate_eval_report.py -q'` | pass: `6 passed in 0.02s` | No production edit planned unless recapture fails during he-work. |
| Router samples | `bash -lc 'python3 Plugins/harness-engineering/scripts/validate_routing_map.py --run-router-samples --json'` | pass | Preserve routing-map ownership and cite as SA-004 positive proof. |
| Release runner missing-ask and router negative path | `bash -lc 'python3 -m pytest Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py -q'` | pass: `4 passed in 0.01s` | No production edit planned unless recapture fails during he-work. |
| Controlled missing-ask proof | Controlled `_run_ask_eval` invocation against temp repo root without `bin/ask` | pass: `status: blocked`, `decision: blocked`, `ERR_ASK_UNAVAILABLE` | Confirms SA-003 degraded-mode behavior. |
| Dirty owner-surface check | `git status --short -- <owner surfaces>` | no tracked owner-surface changes reported; unrelated untracked JSC-167 plan exists under `.harness/plan` | Do not touch unrelated JSC-167 artifact. |

Current SA-001 blockers:

```text
Plugins/harness-engineering/scripts/__pycache__
Plugins/harness-engineering/scripts/__pycache__/run_lifecycle_release_evals.cpython-312.pyc
Plugins/harness-engineering/skills/he-eval-report/scripts/__pycache__
Plugins/harness-engineering/skills/he-eval-report/scripts/__pycache__/*.pyc
Plugins/harness-engineering/skills/he-eval-report/tests/__pycache__
Plugins/harness-engineering/skills/he-eval-report/tests/__pycache__/test_validate_eval_report.cpython-312-pytest-9.0.3.pyc
```

## Stage Context

```yaml
stage_context:
  selected_stage: he-plan
  selected_slice: "[agent-skills] Repair HE trust defects before new capability"
  slice_status: resolved
  tracker_status: created_jsc_299
  artifact_identity_status: pass
  artifact_route_status: pass
  evidence_freshness: fresh_as_of_2026-05-10
  session_trace_status: not_applicable
  linear_delta_status: not_applicable_local_only
  domain_skill_status: not_applicable
  steering_status: conservative_plan_only
  coding_harness_status: not_applicable
  project_brain_status: not_checked
  validation_status: focused_slice_validated_after_he_work
  blocker: "No focused-slice implementation blocker remains; Codex-runner release confidence remains a follow-up blocker."
```

## Post-Implementation State

This plan has been executed for the approved focused slice. PU-001 through
PU-004 are locally validated by the linked eval artifact:
`.harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md`.

Current state:

- SA-001 packaging hygiene is repaired when representative Python validation
  routes bytecode outside the HE plugin tree and hygiene runs last.
- SA-002 and SA-008 eval-report not-run closure behavior remain preserved.
- SA-003 missing-`ask` degraded-mode behavior remains covered by focused tests.
- SA-004 router sample proof remains covered by focused tests plus live routing
  sample execution.

Remaining blockers are not implementation blockers for this focused slice:

- live Linear issue `JSC-299` exists for this focused repair slice;
- Codex-runner smoke and full plugin release confidence remain blocked;
- phase-exit review must confirm artifact state before closure.

## Boundary

### In Scope

- Delete generated HE plugin `__pycache__` directories and `.pyc` files.
- Preserve the passing not-run side-effect closure behavior.
- Preserve missing-`ask` blocked degraded-mode behavior.
- Preserve router-sample positive proof and release-runner negative summary
  proof.
- Run recurrence checks after representative validation commands.
- Produce a closure eval artifact after implementation evidence exists.

### Out Of Scope

- Editing `side_effect_consistency.py`, `validate_eval_report.py`,
  `run_lifecycle_release_evals.py`, or `validate_routing_map.py` while the
  recaptured tests remain passing.
- New HE stages, handles, authority schemas, threat-model/tool-audit capability,
  evidence ledgers, artifact indexes, plugin hooks, or parallel-agent workflows.
- Linear creation, update, closure, or PR creation.
- The unrelated untracked JSC-167 plan under `.harness/plan`.

## First-Principles Planning Check

```yaml
first_principles_check:
  verified_failure: "SA-001 packaging hygiene fails because generated cache artifacts exist under the HE plugin tree."
  fundamental_constraint: "Do not refactor passing trust checks when the active defect is generated artifact hygiene."
  assumption_being_challenged: "All four original trust defects still need implementation edits."
  smallest_effective_mechanism: "Delete generated cache artifacts, run representative commands with bytecode suppression where needed, rerun hygiene, and record closure proof."
  analogy_or_template_rejected: "Do not expand into authority, risk, or ledger infrastructure before the current hygiene gate is clean."
  proof_required: "Packaging hygiene passes after recurrence check; focused preservation tests still pass; eval artifact records the evidence."
  context_load_effect: reduced
  routing_effect: clearer
  decision_type: Type 2
  outcome: proceed_to_he_work_when_authorized
```

## Implementation Units

### PU-000: Verify-First Recapture

Objective:

Before edits, rerun the current evidence checks and stop if they no longer
match this plan.

Actions:

1. Re-run packaging hygiene.
2. Re-run focused eval-report tests.
3. Re-run release-runner helper tests.
4. Re-run router sample proof.
5. Inspect owner-surface dirty state.

Owner surfaces:

- `Plugins/harness-engineering/scripts/check_packaging_hygiene.py`
- `Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py`
- `Plugins/harness-engineering/scripts/validate_routing_map.py`
- `Plugins/harness-engineering/references/routing-map.json`
- `Plugins/harness-engineering/skills/he-eval-report/scripts/**`
- `Plugins/harness-engineering/skills/he-eval-report/tests/**`
- `Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py`

Acceptance IDs:

- SA-001 through SA-008

Stop rule:

If SA-002, SA-003, or SA-004 no longer pass, pause and re-plan the affected unit
instead of blindly deleting caches.

### PU-001: Clear Generated HE Plugin Cache Artifacts

Objective:

Remove generated cache artifacts that make `check_packaging_hygiene.py` fail.

Actions:

1. Delete only generated `__pycache__` directories and `.pyc` files under
   `Plugins/harness-engineering`.
2. Re-run `find Plugins/harness-engineering -path '*__pycache__*' -o -name '*.pyc'`.
3. Re-run packaging hygiene.
4. Run representative Python validation with `PYTHONDONTWRITEBYTECODE=1` where
   commands import HE plugin modules.
5. Re-run packaging hygiene after representative validation to prove cache
   artifacts did not recur.

Touched paths:

- `Plugins/harness-engineering/scripts/__pycache__/`
- `Plugins/harness-engineering/skills/he-eval-report/scripts/__pycache__/`
- `Plugins/harness-engineering/skills/he-eval-report/tests/__pycache__/`

Acceptance IDs:

- SA-001
- SA-005
- SA-007

Validation:

```bash
find Plugins/harness-engineering -path '*__pycache__*' -o -name '*.pyc'
bash -lc 'python3 Plugins/harness-engineering/scripts/check_packaging_hygiene.py --json'
bash -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -m pytest Plugins/harness-engineering/skills/he-eval-report/tests/test_validate_eval_report.py -q'
bash -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -m pytest Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py -q'
bash -lc 'PYTHONDONTWRITEBYTECODE=1 python3 Plugins/harness-engineering/scripts/validate_routing_map.py --run-router-samples --json'
bash -lc 'python3 Plugins/harness-engineering/scripts/check_packaging_hygiene.py --json'
```

Rollback:

Do not restore generated cache artifacts. If an expected command recreates
cache files, keep the work blocked and either run that command with bytecode
suppression or route a separate tooling fix.

### PU-002: Preserve Eval-Report Not-Run Closure Blocking

Objective:

Keep the passing not-run side-effect validator behavior stable while SA-001 is
repaired.

Actions:

1. Do not edit eval-report validator logic if recapture still passes.
2. Re-run the focused tests with bytecode suppression.
3. Confirm the test suite still covers both the mixed pass/not-run warning and
   the hard completion-blocking error.

Owner surfaces:

- `Plugins/harness-engineering/skills/he-eval-report/scripts/side_effect_consistency.py`
- `Plugins/harness-engineering/skills/he-eval-report/scripts/validate_eval_report.py`
- `Plugins/harness-engineering/skills/he-eval-report/tests/test_validate_eval_report.py`

Acceptance IDs:

- SA-002
- SA-007
- SA-008

Validation:

```bash
bash -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -m pytest Plugins/harness-engineering/skills/he-eval-report/tests/test_validate_eval_report.py -q'
```

Rollback:

If this test fails after cache cleanup, stop and re-plan. Do not weaken the
hard error `side-effect authorization not-run validator decisions must block
completion`.

### PU-003: Preserve Release-Runner Degraded Mode And Router Negative Proof

Objective:

Keep the currently passing SA-003 and SA-004 release-runner proof stable.

Actions:

1. Do not edit `run_lifecycle_release_evals.py` if focused recapture still
   passes.
2. Re-run release-runner helper tests.
3. Confirm the test suite still covers:
   - missing `bin/ask`;
   - non-executable `bin/ask`;
   - executable wrapper classification;
   - required router sample failing gate summary.

Owner surfaces:

- `Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py`
- `Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py`

Acceptance IDs:

- SA-003
- SA-004
- SA-005
- SA-007

Validation:

```bash
bash -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -m pytest Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py -q'
bash -lc 'PYTHONDONTWRITEBYTECODE=1 python3 Plugins/harness-engineering/scripts/validate_routing_map.py --run-router-samples --json'
```

Rollback:

If these tests fail, stop and re-plan the release-runner surface before any
closure artifact is written.

### PU-004: Produce Closure Eval Artifact

Objective:

Create the HE eval artifact only after the implementation evidence exists.

Touched path:

- `.harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md`

Actions:

1. Record exact command outcomes for SA-001 through SA-004.
2. Record scope proof for SA-005.
3. Mark Linear tracking as `JSC-299` while keeping plugin-wide release
   confidence as a separate blocker.
4. Validate the eval artifact with HE eval-report and artifact lints.

Acceptance IDs:

- SA-006

Validation:

```bash
bash -lc 'python3 Plugins/harness-engineering/skills/he-eval-report/scripts/validate_eval_report.py .harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md'
bash -lc 'python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md'
bash -lc 'python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md'
bash -lc 'python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md'
```

Rollback:

If evidence is incomplete, keep the eval artifact as `blocked` or do not create
it. Do not convert missing proof into `complete_with_follow_up`.

## Plan Unit Traceability

| Plan Unit | Acceptance IDs | Required Proof |
| --- | --- | --- |
| PU-000 | SA-001 through SA-008 | Fresh command recapture and owner-surface dirty check before edits. |
| PU-001 | SA-001, SA-005, SA-007 | Packaging hygiene passes after cache deletion and recurrence check. |
| PU-002 | SA-002, SA-007, SA-008 | Eval-report focused tests pass without weakening hard not-run blocking. |
| PU-003 | SA-003, SA-004, SA-005, SA-007 | Release-runner helper tests and router sample proof pass. |
| PU-004 | SA-006 | Eval artifact exists, records evidence, and passes HE artifact validation. |

## Validation Plan

Focused implementation validation:

```bash
find Plugins/harness-engineering -path '*__pycache__*' -o -name '*.pyc'
bash -lc 'python3 Plugins/harness-engineering/scripts/check_packaging_hygiene.py --json'
bash -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -m pytest Plugins/harness-engineering/skills/he-eval-report/tests/test_validate_eval_report.py -q'
bash -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -m pytest Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py -q'
bash -lc 'PYTHONDONTWRITEBYTECODE=1 python3 Plugins/harness-engineering/scripts/validate_routing_map.py --run-router-samples --json'
bash -lc 'python3 Plugins/harness-engineering/scripts/check_packaging_hygiene.py --json'
git diff --check -- Plugins/harness-engineering Infrastructure/scripts/testing .harness/evals
```

Plan artifact validation:

```bash
bash -lc 'python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/plan/2026-05-09-agent-skills-he-trust-defect-repair-plan.md'
bash -lc 'python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/plan/2026-05-09-agent-skills-he-trust-defect-repair-plan.md'
bash -lc 'python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/2026-05-09-agent-skills-he-trust-defect-repair-plan.md'
./bin/ask skills audit Plugins/harness-engineering/skills/he-plan --level strict --json --robot
git diff --check -- .harness/plan/2026-05-09-agent-skills-he-trust-defect-repair-plan.md
```

Eval artifact validation after PU-004:

```bash
bash -lc 'python3 Plugins/harness-engineering/skills/he-eval-report/scripts/validate_eval_report.py .harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md'
bash -lc 'python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md'
bash -lc 'python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md'
bash -lc 'python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md'
```

## Risk And Rollback

| Risk | Mitigation | Rollback |
| --- | --- | --- |
| Cache artifacts reappear after tests. | Run representative commands with `PYTHONDONTWRITEBYTECODE=1` and rerun packaging hygiene last. | Keep SA-001 blocked and route a tooling fix; do not restore cache artifacts. |
| Passing validator behavior regresses during cleanup. | PU-002 and PU-003 rerun focused tests before closure. | Stop and re-plan the affected validator surface. |
| Plan drifts into later authority/proof roadmap. | SA-005 diff review blocks new stages, schemas, ledgers, indexes, and Linear mutation. | Split the expanded work into a later plan. |
| Focused Linear tracker becomes mistaken for plugin-wide release closure. | PU-004 eval must link `JSC-299` while keeping Codex-runner release confidence as blocked follow-up. | Update or supersede artifacts only after release-confidence follow-up is fixed or waived. |

## Handoff

```yaml
post_plan_handoff:
  state: focused_slice_validated
  selected_next_stage: he-code-review
  evidence: ".harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md"
  next_action: "Run phase-exit review, link PR evidence to JSC-299, and keep Codex-runner release confidence as a follow-up blocker."
  interactive_status: autonomous_assumption
  implementation_authorization: received
  implementation_status: focused_slice_validated
  slack_policy: blocked_until_phase_exit_review_and_pr_traceability
```

## Blackboard Delta

```yaml
blackboard_delta:
  active_slice: agent-skills-he-trust-defect-repair
  current_stage: he-eval-report
  recommended_next_stage: he-code-review
  active_blockers:
    - codex_runner_release_confidence_blocked
    - phase_exit_review_pending
    - pr_traceability_pending
  preserved_passing_surfaces:
    - sa_001_packaging_hygiene_when_bytecode_is_routed_out_of_tree
    - sa_002_sa_008_eval_report_not_run_closure_behavior
    - sa_003_missing_ask_degraded_mode
    - sa_004_router_sample_positive_and_negative_release_runner_proof
  intentionally_deferred:
    - authority_schema
    - threat_model_skill
    - tool_audit_skill
    - evidence_ledger
    - artifact_index
    - parallel_agent_workflow
```
