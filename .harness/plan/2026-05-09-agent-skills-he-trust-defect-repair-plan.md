---
schema_version: 1
artifact_id: agent-skills-he-trust-defect-repair-plan
artifact_type: he-plan
canonical_slug: agent-skills-he-trust-defect-repair
title: HE Trust Defect Repair Plan
harness_stage: he-plan
status: draft
date: 2026-05-09
traceability_required: false
origin: .harness/specs/2026-05-09-agent-skills-he-trust-defect-repair-spec.md
linear_issue: not_created
linear_milestone: HE Authority And Proof Hardening
risk: architecture_sensitive
depth: deep
ui: false
---

# HE Trust Defect Repair Plan

## Executive Plan Summary

Implement the first HE Authority And Proof Hardening slice by repairing the
current trust defects before adding new Harness Engineering capability.

The plan intentionally starts with the two confirmed failures:

- HE packaging hygiene fails on generated Python cache artifacts.
- `he-eval-report` focused validation fails because the mixed pass/not-run
  warning contract is not satisfied, even though the hard not-run completion
  blocker still fires.

Then it hardens the remaining release-confidence path:

- missing/non-executable `./bin/ask` must become a clear degraded environment
  result in lifecycle release evals;
- router sample execution remains owned by `validate_routing_map.py`, while any
  release lane claiming router confidence must require that proof.

No Linear mutation, new HE stage, threat-model skill, tool-audit skill, evidence
ledger, artifact index, or parallel-agent workflow is included in this plan.

## Source Evidence

| Source | Evidence Used | Planning Impact |
| --- | --- | --- |
| `.harness/specs/2026-05-09-agent-skills-he-trust-defect-repair-spec.md` | Defines SA-001 through SA-008, current blockers, scope, and validation commands. | Primary implementation contract. |
| `.harness/linear/2026-05-09-agent-skills-he-authority-proof-hardening-linear-plan.md` | Routes this work to the proposed `Now` parent issue and keeps broader work in `Next` or `Later`. | Confirms this plan covers only the first repair slice. |
| `Plugins/harness-engineering/scripts/check_packaging_hygiene.py` | Rejects `__pycache__`, `.pyc`, and other generated clutter. | The first implementation unit should remove current generated blockers and preserve this check. |
| `python3 Plugins/harness-engineering/scripts/check_packaging_hygiene.py --json` | Current result is `fail` with generated cache blockers under `skills/he-eval-report/scripts/__pycache__` and `skills/he-eval-report/tests/__pycache__`. | Confirms SA-001 is live failing evidence and both cache surfaces must be cleared. |
| `Plugins/harness-engineering/skills/he-eval-report/tests/test_validate_eval_report.py` | `test_not_run_side_effect_validator_blocks_completion` expects a hard error plus mixed pass/not-run warning. | Drives PU-002; do not weaken hard completion blocking. |
| `python3 -m pytest Plugins/harness-engineering/skills/he-eval-report/tests/test_validate_eval_report.py -q` | Current result is 1 failed, 5 passed; missing expected warning only. | Confirms SA-002 hard blocker mostly exists and SA-008 is the actual mismatch. |
| `Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py` | Legacy ask runner executes `repo_root / "bin" / "ask"` without an explicit command-surface preflight. | Drives PU-003. |
| `Plugins/harness-engineering/scripts/validate_routing_map.py` | Owns route sample execution and emits a warning when samples are skipped. | Drives PU-004. |
| `python3 Plugins/harness-engineering/scripts/validate_routing_map.py --run-router-samples --json` | Current result is `pass` with no warnings. | Router samples are not currently failing when explicitly run; release integration is the remaining concern. |

## External Verification Inputs

| Source | Verified Fact | Planning Impact |
| --- | --- | --- |
| Python documentation, Programming FAQ: `.pyc` files are created in `__pycache__` under the source file directory when modules are imported and bytecode writing is allowed. | `__pycache__` and `.pyc` files are generated runtime artifacts, not canonical plugin source. | PU-001 may remove generated cache artifacts and should not restore them as source-of-truth files. |
| pytest documentation: `tmp_path` provides a per-test temporary directory as a `pathlib.Path`. | Missing/non-executable `ask` can be tested with a temporary fixture root instead of mutating the real repo command surface. | PU-003 should use `tmp_path` helper tests for command-surface availability. |

## Stage Context

```yaml
stage_context:
  selected_stage: he-plan
  selected_slice: "[agent-skills] Repair HE trust defects before new capability"
  slice_status: resolved
  tracker_status: not_applicable
  artifact_identity_status: pass
  artifact_route_status: pass
  evidence_freshness: fresh
  session_trace_status: not_applicable
  linear_delta_status: not_applicable
  domain_skill_status: not_applicable
  steering_status: not_needed
  coding_harness_status: not_applicable
  project_brain_status: not_checked
  validation_status: fail
  blocker: "SA-001 packaging hygiene and SA-008 eval-report warning semantics currently fail."
```

## First-Principles Planning Check

```yaml
first_principles_check:
  verified_failure: "Known HE trust gates currently fail or can overstate release confidence."
  fundamental_constraint: "Repair active trust defects before adding new lifecycle capability."
  assumption_being_challenged: "Broader authority schemas, threat models, or evidence ledgers should be built now."
  smallest_effective_mechanism: "Remove generated packaging blockers, repair focused eval-report warning semantics, preflight ask runner availability, and wire router-sample proof into release confidence."
  analogy_or_template_rejected: "Do not copy a full control-plane hardening stack before the current HE release/eval blockers are deterministic."
  proof_required: "SA-001 through SA-008 validation passes or records explicit blockers."
  context_load_effect: reduced
  routing_effect: clearer
  decision_type: Type 2
  outcome: proceed
```

## Scope

In scope:

- Remove generated `__pycache__` and `.pyc` blockers from the HE plugin tree.
- Repair the focused `he-eval-report` test/validator mismatch while preserving
  the hard error for not-run side-effect validators.
- Add deterministic command-surface classification for missing or
  non-executable `./bin/ask` in legacy ask eval runs.
- Make router sample proof explicit for release-confidence claims without
  moving sample ownership out of `validate_routing_map.py`.
- Add or update focused tests around the changed script behavior.
- Produce a post-implementation HE eval artifact.

Out of scope:

- New HE stages or handles.
- `he-threat-model` or `he-tool-audit`.
- Full authority schema.
- Append-only evidence ledger.
- Full `.harness` artifact index.
- Parallel-agent execution flows.
- Linear creation, update, or closure.
- Skill-factory or plugin-factory changes.

## Planning Decisions

### Decision 1: Fix Confirmed Failures First

Start with packaging hygiene and the `he-eval-report` focused failure because
they are live, deterministic, and cheap to verify.

This prevents the plan from spending effort on hypothesized release-lane fixes
before the current red gates are clean.

### Decision 2: Preserve The Hard Not-Run Blocker

The current failing `he-eval-report` test proves the missing piece is the
warning contract, not the hard error. Any implementation that removes or
weakens `side-effect authorization not-run validator decisions must block
completion` fails this plan.

### Decision 3: Keep Router Samples In The Routing Validator

`validate_routing_map.py` owns sample execution. `run_lifecycle_release_evals.py`
may consume its result or invoke it as a release preflight, but should not
duplicate the routing-map sample engine.

### Decision 4: Classify Environment Blockers Explicitly

When `./bin/ask` is missing or not executable, the release runner should return
a structured blocked/degraded result with recovery text. It must not report a
pass, silent skip, or ambiguous skill failure.

### Decision 5: Add Testable Seams Before Adding New Release Flags

The release runner currently has no focused test surface and no command-surface
preflight seam. Add the smallest injectable helpers first, then wire CLI
behavior through those helpers. This keeps the fix testable without renaming or
moving the real `./bin/ask`.

### Decision 6: Make Router-Sample Proof An Explicit Release Input

Router samples already pass when explicitly executed. The missing behavior is
not router correctness; it is release-confidence accounting. Add an explicit
`--require-router-samples` release-runner flag so a release result can
distinguish:

- router samples were required and passed;
- router samples were required and failed;
- router samples were required but could not run;
- router samples were not required for this lane.

Do not convert ordinary `validate_routing_map.py` structural validation without
`--run-router-samples` into a global failure. Only release-confidence lanes
should be blocked for missing required router sample proof.

### Decision 7: Use A Dedicated Release-Runner Test Surface

Create `Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py`
for helper-level tests around ask availability and router-sample release
accounting. Use pytest `tmp_path` fixture roots to test missing and
non-executable `bin/ask` states without mutating the real repository command
surface.

## File Ownership And Editing Order

| Order | File Set | Purpose | Notes |
| --- | --- | --- | --- |
| 1 | `Plugins/harness-engineering/skills/he-eval-report/scripts/__pycache__/` | Remove generated packaging blockers. | Delete generated cache artifacts only; do not alter source logic in this unit. |
| 2 | `Plugins/harness-engineering/skills/he-eval-report/scripts/side_effect_consistency.py`, `validate_eval_report.py`, and/or `report_recommendation.py` | Repair mixed pass/not-run warning semantics. | The focused failing fixture is section-level side-effect evidence, not only a `Gate:` matrix entry. Prefer production validator logic over deleting the warning expectation. |
| 3 | `Plugins/harness-engineering/skills/he-eval-report/tests/test_validate_eval_report.py` | Preserve regression assertions. | Keep both assertions: warning is emitted and hard error remains. |
| 4 | `Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py` | Add missing/non-executable `ask` classification and router-sample release proof accounting. | Keep output JSON machine-readable for `he-eval-report`. |
| 5 | `Plugins/harness-engineering/scripts/validate_routing_map.py` | Preserve canonical router sample execution owner. | Avoid duplicating route-sample logic in the release runner. |
| 6 | Focused tests for release-runner helpers | Prove ask availability and router-sample release accounting. | Prefer pure helper tests or temporary fixture roots over destructive changes to real `./bin/ask`. |
| 7 | `.harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md` | Closure proof artifact after implementation. | Write only after code changes and validation evidence exist. |

## Technical Review Of This Plan

### Finding 1: Ask Availability Was Previously Validated Through The Wrong Runner Path

Severity: high

The missing/non-executable `./bin/ask` defect only applies to the legacy
`eval_runner == "ask"` path. A validation command using `--eval-runner codex`
does not exercise `_run_ask_eval()` and therefore cannot prove SA-003.

Plan correction:

- PU-003 must add a focused helper test or controlled invocation that exercises
  the `ask` runner path directly.
- The smoke command using `--eval-runner codex` may remain useful for direct
  skill-builder validation, but it is not acceptance proof for missing `ask`.

### Finding 2: Eval-Report Warning Source Is Section-Level, Not Only Gate-Matrix Level

Severity: medium

`report_recommendation.validate_consistency()` currently warns when a `Gate:`
entry has `Status: pass` and not-run evidence. The failing test fixture expects
a broader warning when the report has global pass/completion claims and the
`Side-Effect Authorization` section reports `Validator Decision: not-run`.

Plan correction:

- PU-002 should inspect the side-effect validation flow first.
- A production fix may require warning generation near
  `side_effect_consistency.py` or the caller in `validate_eval_report.py`, not
  only in `report_recommendation.py`.
- Do not satisfy the test by weakening the existing hard error.

### Finding 3: Router Samples Already Pass; Release Accounting Is The Real Gap

Severity: medium

`validate_routing_map.py --run-router-samples --json` currently passes. The
implementation should not spend effort redesigning route selection. The release
gap is that a release-confidence lane can fail to show whether router samples
were required and executed.

Plan correction:

- PU-004 should add release accounting around router-sample proof, preferably
  by invoking or recording the canonical routing validator result.
- Keep route sample execution in `validate_routing_map.py`.

### Finding 4: Packaging Hygiene Has Two Generated Cache Surfaces

Severity: low

The known packaging failure listed `skills/he-eval-report/scripts/__pycache__`,
but live discovery also showed `skills/he-eval-report/tests/__pycache__`.

Plan correction:

- PU-001 must remove all generated cache artifacts inside the HE plugin tree,
  not only the script cache directory.
- Re-run `check_packaging_hygiene.py --json` as the source of truth after
  deletion.

## Implementation Units

### PU-001: Clear Packaging Hygiene Blockers

Objective:

Remove generated cache artifacts currently causing the HE packaging hygiene
gate to fail.

Touched paths:

- `Plugins/harness-engineering/skills/he-eval-report/scripts/__pycache__/`
- `Plugins/harness-engineering/skills/he-eval-report/tests/__pycache__/`

Actions:

1. Remove all generated `__pycache__` directories and `.pyc` files from the HE
   plugin tree.
2. Re-run packaging hygiene.
3. Inspect `git status --short` to ensure only generated blockers were removed.
4. Add or confirm ignore/hygiene coverage if generated caches recur during the
   validation run.

Acceptance IDs:

- SA-001
- SA-005

Validation:

```bash
python3 Plugins/harness-engineering/scripts/check_packaging_hygiene.py --json
git diff --check -- Plugins/harness-engineering
```

Rollback:

- Do not restore generated cache artifacts. If removal breaks tooling, fix the
  tooling to generate caches outside the plugin tree.

### PU-002: Repair Eval-Report Warning Semantics Without Weakening Closure Blocking

Objective:

Make `test_not_run_side_effect_validator_blocks_completion` pass while keeping
the hard completion-blocking error for not-run side-effect validators.

Touched paths:

- `Plugins/harness-engineering/skills/he-eval-report/scripts/report_recommendation.py`
- `Plugins/harness-engineering/skills/he-eval-report/scripts/side_effect_consistency.py`
- `Plugins/harness-engineering/skills/he-eval-report/scripts/validate_eval_report.py`
- `Plugins/harness-engineering/skills/he-eval-report/tests/test_validate_eval_report.py`

Likely implementation:

1. Inspect `ReportDocument.gate_entries()` parsing and warning generation in
   `report_recommendation.py`.
2. Inspect how `validate_eval_report.py` calls side-effect consistency checks.
3. Determine why the minimal report fixture does not produce the expected
   mixed pass/not-run warning even though it has global pass/completion claims
   and `Validator Decision: not-run`.
4. Prefer a production fix if the warning should still be emitted when report
   body contains completion/pass claims plus not-run side-effect evidence.
5. If the warning expectation is stale, update the test with a comment or
   assertion structure that preserves the hard error and explains why the
   warning no longer applies.

Hard guard:

- The assertion for `side-effect authorization not-run validator decisions must
  block completion` must remain in the focused test.

Acceptance IDs:

- SA-002
- SA-007
- SA-008

Validation:

```bash
python3 -m pytest Plugins/harness-engineering/skills/he-eval-report/tests/test_validate_eval_report.py -q
python3 Plugins/harness-engineering/scripts/check_packaging_hygiene.py --json
```

Rollback:

- Restore prior validator/test logic if the hard not-run completion blocker is
  weakened, or if unrelated eval-report tests begin accepting missing proof.

### PU-003: Add Ask Runner Availability Classification

Objective:

Make lifecycle release evals fail cleanly when `./bin/ask` is missing or not
executable.

Touched paths:

- `Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py`
- focused tests for the release runner, if existing; otherwise add a small
  test file at `Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py`.

Implementation requirements:

1. Add a small helper that checks `repo_root / "bin" / "ask"` before the
   legacy ask eval path executes.
2. Return a structured per-skill result when the command surface is unavailable.
3. Include:
   - `status: "blocked"` or equivalent non-success state;
   - `decision: "blocked"` when available;
   - `errors[0].code`, preferably `ERR_ASK_UNAVAILABLE`;
   - a recovery message naming `./bin/ask`;
   - `returncode` that makes the summary fail.
4. Preserve existing `codex` eval-runner behavior.
5. Add a focused test seam so the missing and non-executable states can be
   exercised against a temporary repo root or helper function.
6. Use pytest `tmp_path` to build temporary fixture roots for:
   - no `bin/ask`;
   - `bin/ask` present but not executable;
   - `bin/ask` present and executable enough for helper classification.

Acceptance IDs:

- SA-003
- SA-005

Validation:

```bash
python3 -m pytest Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py -q
python3 Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py --mode smoke --skill he-router --eval-runner ask --json
```

Add a focused test or controlled invocation for missing/non-executable `ask`
without destructively modifying the real `./bin/ask`.

Rollback:

- Remove the new availability helper if it incorrectly blocks valid local ask
  runs. Preserve any tests that document the desired degraded-mode behavior.

### PU-004: Wire Router Sample Proof Into Release Confidence

Objective:

Ensure a release-confidence claim cannot skip required router sample proof.

Touched paths:

- `Plugins/harness-engineering/scripts/validate_routing_map.py`
- `Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py`
- focused tests for whichever script owns the new release gate

Implementation requirements:

1. Keep sample execution in `validate_routing_map.py`.
2. Ensure `validate_routing_map.py --run-router-samples --json` remains the
   canonical command for router sample proof.
3. Add `--require-router-samples` to the release runner so release confidence
   records router-sample proof as:
   - `pass` when samples are run and pass;
   - `blocked` or `fail` when samples are required but not run;
   - `not_applicable` only when the selected release lane explicitly does not
     claim router confidence.
4. Do not turn the existing non-sample validator mode into a global failure;
   it can still warn when callers are not making release-confidence claims.
5. Prefer invoking `validate_routing_map.py --run-router-samples --json` from
   the release runner when router proof is required, then embed or summarize
   that result in the release JSON.

Acceptance IDs:

- SA-004
- SA-005
- SA-007

Validation:

```bash
python3 Plugins/harness-engineering/scripts/validate_routing_map.py --run-router-samples --json
python3 -m pytest Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py -q
python3 Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py --mode smoke --skill he-router --eval-runner codex --case ambiguous-stage-route --require-router-samples --json
```

Rollback:

- If the release preflight creates excessive runtime cost or flakes, keep
  `validate_routing_map.py --run-router-samples --json` as the required
  separate release gate and document release confidence as blocked unless that
  command has fresh pass evidence.

### PU-005: Produce Closure Eval Artifact

Objective:

Create the closure proof artifact after implementation and validation.

Touched paths:

- `.harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md`

Implementation requirements:

1. Record exact command outcomes for SA-001 through SA-004.
2. Record scope proof for SA-005.
3. Record eval artifact validation for SA-006.
4. Preserve untracked Linear state: `linear_issue: not_created` unless a live
   Linear issue has been created after this plan.
5. Closure recommendation must be `Blocked` or `Needs rework` if any required
   validation remains failing, skipped, timed out, or unavailable.

Acceptance IDs:

- SA-006

Validation:

```bash
python3 Plugins/harness-engineering/skills/he-eval-report/scripts/validate_eval_report.py .harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md
python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md
python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md
```

Rollback:

- If closure evidence is incomplete, keep the eval artifact as `Blocked` rather
  than deleting it or turning missing proof into a pass.

## Plan Unit Traceability

| Plan Unit | Acceptance IDs | Required Proof |
| --- | --- | --- |
| PU-001 | SA-001, SA-005 | Packaging hygiene passes and diff shows only generated clutter removal. |
| PU-002 | SA-002, SA-007, SA-008 | Eval-report focused tests pass and hard not-run blocker remains asserted. |
| PU-003 | SA-003, SA-005 | Missing/non-executable `ask` is classified as blocked/degraded with recovery text. |
| PU-004 | SA-004, SA-005, SA-007 | Router samples pass when run; release confidence cannot claim router proof when samples are skipped. |
| PU-005 | SA-006 | Eval artifact exists and passes HE artifact validation. |

## Validation Plan

Run focused validation after each implementation unit:

```bash
python3 Plugins/harness-engineering/scripts/check_packaging_hygiene.py --json
python3 -m pytest Plugins/harness-engineering/skills/he-eval-report/tests/test_validate_eval_report.py -q
python3 Plugins/harness-engineering/scripts/validate_routing_map.py --run-router-samples --json
python3 -m pytest Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py -q
python3 Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py --mode smoke --skill he-router --eval-runner codex --case ambiguous-stage-route --require-router-samples --json
```

After the eval artifact exists, run:

```bash
python3 Plugins/harness-engineering/skills/he-eval-report/scripts/validate_eval_report.py .harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md
python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md
python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/evals/2026-05-09-agent-skills-he-trust-defect-repair-eval.md
```

Plan artifact validation:

```bash
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/plan/2026-05-09-agent-skills-he-trust-defect-repair-plan.md
python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/plan/2026-05-09-agent-skills-he-trust-defect-repair-plan.md
python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/2026-05-09-agent-skills-he-trust-defect-repair-plan.md
git diff --check -- .harness/plan/2026-05-09-agent-skills-he-trust-defect-repair-plan.md
```

## Risk And Rollback

| Risk | Mitigation | Rollback |
| --- | --- | --- |
| Removing generated cache artifacts reveals they are tracked or expected by another workflow. | Inspect `git status --short` after deletion; rely on source files, not cache artifacts. | Do not restore generated artifacts unless repo policy explicitly requires them. |
| Eval-report warning fix weakens completion blocking. | Keep the hard error assertion in tests. | Revert PU-002 and re-plan around warning-only behavior. |
| Ask preflight blocks valid ask usage. | Add focused tests for present/missing/non-executable command states. | Revert helper while keeping tests as desired behavior documentation. |
| Router sample release gate duplicates routing logic. | Keep sample execution in `validate_routing_map.py`; release runner only consumes or invokes it. | Fall back to requiring the routing validator as a separate release command. |
| Scope expands into authority or threat-model roadmap. | Use SA-005 diff review gate. | Split expanded work into a separate `Next` plan. |

## Confidence Loophole Register

| Loophole | Fix In This Plan | Residual Risk |
| --- | --- | --- |
| Treating generated bytecode as source. | Remove all HE plugin `__pycache__` and `.pyc` artifacts; rely on packaging hygiene as the source of truth. | Caches may recur if tests import modules in-place; hygiene must remain a release gate. |
| Proving missing `ask` through `--eval-runner codex`. | Test and validate the legacy `ask` path directly; keep codex-runner validation separate. | Existing `./bin/ask` may run slowly; helper tests cover availability without requiring full eval completion. |
| Weakening the not-run completion blocker to satisfy the warning test. | Preserve the hard error assertion and repair warning semantics around section-level side-effect evidence. | Warning wording may change; tests should assert the stable contract, not incidental formatting. |
| Duplicating router sample logic in release runner. | Keep route execution in `validate_routing_map.py`; release runner invokes or records the canonical result. | Subprocess wiring can fail; release JSON must expose the routing-validator stderr/stdout or structured errors. |
| Making router samples always mandatory and slowing unrelated lanes. | Add `--require-router-samples`; only release-confidence lanes opt in. | Callers must use the flag when claiming router proof; closure eval must check it was used. |
| Creating a closure eval before evidence exists. | PU-005 is last and must classify missing validation as `Blocked` or `Needs rework`. | Human review still required before Linear closure because no live Linear issue exists yet. |

## Confidence Position

Absolute 100% confidence is not an honest claim before implementation, because
the final proof depends on changed code and post-change validation. The plan is
now high-confidence enough to execute because every known loophole has either:

- a deterministic implementation unit;
- an explicit validation command;
- a rollback path;
- or a closure-blocking residual risk.

The confidence target for implementation is:

```yaml
confidence_target:
  before_implementation: high_confidence_plan
  after_implementation: evidence_backed_confidence
  closure_requires:
    - packaging_hygiene_pass
    - eval_report_tests_pass
    - router_samples_pass
    - release_runner_helper_tests_pass
    - release_runner_required_router_sample_command_pass_or_blocked_with_reason
    - closure_eval_artifact_passes_validation
```

## Post-Plan Handoff

```yaml
post_plan_handoff:
  state: awaiting_user_choice
  selected_next_stage: he-work
  evidence: ".harness/plan/2026-05-09-agent-skills-he-trust-defect-repair-plan.md"
  next_action: "Proceed to he-work only if the user authorizes implementation; otherwise stop at the durable plan."
  interactive_status: awaiting_user_choice
  valid_next_choices:
    - "Proceed to he-work for PU-001 through PU-004."
    - "Run a technical review/deepen-plan pass first."
    - "Create/link Linear objects before implementation."
```

## Blackboard Delta

```yaml
blackboard_delta:
  active_slice: agent-skills-he-trust-defect-repair
  current_stage: he-plan
  recommended_next_stage: he-work
  blocked_by:
    - packaging_hygiene_fail
    - he_eval_report_warning_contract_fail
  intentionally_deferred:
    - authority_schema
    - threat_model_skill
    - tool_audit_skill
    - evidence_ledger
    - artifact_index
    - parallel_agent_workflow
```
