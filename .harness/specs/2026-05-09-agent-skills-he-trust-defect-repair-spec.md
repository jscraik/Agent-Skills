---
schema_version: 1
artifact_id: agent-skills-he-trust-defect-repair-spec
artifact_type: he-spec
canonical_slug: agent-skills-he-trust-defect-repair
title: HE Trust Defect Repair Spec
harness_stage: he-spec
status: draft
date: 2026-05-09
traceability_required: false
origin: .harness/linear/2026-05-09-agent-skills-he-authority-proof-hardening-linear-plan.md
linear_issue: not_created
linear_milestone: HE Authority And Proof Hardening
risk: architecture_sensitive
depth: standard
ui: false
---

# HE Trust Defect Repair Spec

## Mode Decision

This spec covers the `Now` slice from the HE Authority And Proof Hardening
Linear plan:

`[agent-skills] Repair HE trust defects before new capability`

No Linear issue has been created or mutated. Traceability is marked `false`
because the source Linear plan is proposed execution structure, not a live
tracker. If Linear objects are created later, this spec should be linked to the
parent issue before any closure recommendation.

## Stage Context

```yaml
stage_context:
  selected_stage: he-spec
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
  validation_status: not_run_with_reason
  blocker: null
```

## Gate Profile

```yaml
gate_profile:
  risk_class: architecture_sensitive
  proven_risks:
    - HE release and eval confidence can be overstated when gates skip or classify missing validation ambiguously.
    - HE closure can become narrative proof if not-run validators are allowed to coexist with completion claims.
    - Packaging clutter inside the plugin tree weakens plugin release hygiene and skill-builder validation confidence.
  required_contracts:
    - Plugins/harness-engineering/references/gate-selection-contract.md
    - Plugins/harness-engineering/references/first-principles-contract.md
    - Plugins/harness-engineering/skills/he-spec/references/spec-artifact-contract.md
  skipped_contracts:
    - contract: Plugins/harness-engineering/references/plugin-hook-capability-contract.md
      reason: This slice does not add bundled plugin hooks or hook-enforced runtime behavior.
    - contract: Plugins/harness-engineering/references/domain-model-production-contract.md
      reason: The slice changes lifecycle trust behavior, not product/domain semantics.
    - contract: codex-security threat model workflow
      reason: The slice does not change auth, secrets, network access, external tool authority, or data exposure.
  minimum_proof_required:
    continue_to_next_stage: A plan can identify the exact files/tests/scripts needed for the four trust defects without adding new lifecycle capability.
    safe_to_close: All four trust defects pass targeted validation and a HE eval artifact blocks false completion when proof is missing.
    block_next_stage: Any trust defect remains ambiguous, skipped, or unverifiable.
  evidence_basis: harness
  downstream_route: he-plan
```

## First-Principles Check

```yaml
first_principles_check:
  verified_failure: "Current HE confidence can be undermined by packaging clutter, not-run side-effect validator closure, ask-missing ambiguity, and router sample skip semantics."
  fundamental_constraint: "HE must not add new stages or broader governance before current trust defects fail cleanly and prove correctly."
  assumption_being_challenged: "The next improvement should add threat modeling, artifact indexing, or authority infrastructure immediately."
  smallest_effective_mechanism: "Repair the four known hard trust defects and prove them with targeted tests/evals before expanding scope."
  analogy_or_template_rejected: "Do not copy enterprise control-plane breadth or full evidence-ledger infrastructure before the active HE failure modes are closed."
  proof_required: "Packaging hygiene pass, eval-report not-run validator blocker pass, ask-missing degraded-mode pass, router sample skip/fail blocker pass, and eval artifact validation."
  context_load_effect: reduced
  routing_effect: clearer
  decision_type: Type 2
  outcome: proceed
```

## Problem

Harness Engineering has a strong lifecycle model, but the current trust layer
can still allow confidence to outrun proof. The active problem is not missing
new capability. The active problem is that known validation and release defects
must become deterministic before later authority, risk, tool-audit, artifact
index, or parallel-agent work is safe to trust.

The first repair slice exists because the HE plugin should not claim
production-grade confidence while:

- packaging hygiene can fail on generated clutter;
- `he-eval-report` can be tested against a false-completion case involving
  not-run side-effect validators;
- lifecycle release evals can blur missing `ask` command availability with HE
  skill failure;
- required router sample execution can be skipped without creating a hard
  release-confidence blocker.

## Goals

- Repair the known HE trust defects before adding any new HE capability.
- Make missing or skipped validation produce a clear blocked state, not a
  narrative warning that still permits closure confidence.
- Preserve HE's current lifecycle shape while hardening its proof boundaries.
- Keep the slice small enough to plan, implement, review, and evaluate without
  pulling in the later authority/proof/risk roadmap.
- Produce evidence suitable for `he-eval-report` before recommending any Linear
  or milestone closure.

## Non-Goals

- Do not create `he-threat-model`.
- Do not create `he-tool-audit`.
- Do not add parallel-agent planning or merge workflows.
- Do not introduce a full evidence ledger.
- Do not index the entire historical `.harness` tree.
- Do not mutate Linear objects.
- Do not rewrite the full HE lifecycle.
- Do not change plugin hooks or runtime hook behavior.
- Do not treat this slice as permission to alter skill-factory or
  plugin-factory behavior.

## Linear Contract

Proposed Linear destination:

- Project: `agent-skills`
- Milestone: `HE Authority And Proof Hardening`
- Parent issue: `[agent-skills] Repair HE trust defects before new capability`
- Status: not created in this session

If the parent issue is created, link this spec as a source artifact and keep the
first implementation slice mapped to only the four proposed sub-issues:

- `[agent-skills] Clear HE packaging hygiene defects`
- `[agent-skills] Block eval closure on not-run side-effect validators`
- `[agent-skills] Make lifecycle release evals fail cleanly when ask is unavailable`
- `[agent-skills] Treat required router sample skip as release-blocking`

Linear closure is blocked until `he-eval-report` produces an eval artifact for
this slice and the user accepts or challenges the closure recommendation.

## Boundary

### In Scope

- Remove or prevent HE plugin packaging hygiene blockers inside the canonical
  HE plugin tree.
- Ensure the not-run side-effect validator case blocks completion in
  `he-eval-report` validation.
- Ensure lifecycle release eval runner behavior distinguishes missing `ask`
  command availability from HE skill failure.
- Ensure required router sample execution skip/fail semantics are
  release-blocking when the release lane requires sample execution.
- Add or update the smallest targeted tests/fixtures needed to prove those
  behaviors.
- Produce a closure eval artifact after implementation.

### Out Of Scope

- Broad trigger fixture suites.
- Full authority-level schema.
- Evidence wrappers or append-only evidence ledger.
- Active `.harness` artifact index.
- Threat/risk stage creation.
- Tool/MCP supply-chain checks.
- Cross-repo rollout.
- Automatic Linear creation, update, or closure.

## Baseline

Source evidence:

- `.harness/linear/2026-05-09-agent-skills-he-authority-proof-hardening-linear-plan.md`
  routes this as the `Now` slice and keeps broader authority/proof/risk work in
  `Next` or `Later`.
- `.harness/refactors/2026-05-09-agent-skills-he-authority-proof-hardening.md`
  defines Phase 1 as trust defect repair.
- `Plugins/harness-engineering/scripts/check_packaging_hygiene.py` rejects
  blocked plugin-tree names and suffixes such as `__pycache__` and `.pyc`.
- `Plugins/harness-engineering/skills/he-eval-report/tests/test_validate_eval_report.py`
  contains a not-run side-effect validator case that must produce blocking
  errors.
- `Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py` is the
  release eval runner for HE lifecycle skills.
- `Plugins/harness-engineering/scripts/validate_routing_map.py` owns router
  sample execution. Without `--run-router-samples`, it records
  `router sample execution skipped` as a warning.
- `Plugins/harness-engineering/skills/he-eval-report/scripts/side_effect_consistency.py`
  already encodes the hard error for not-run side-effect authorization when
  `Blocks Completion` is not `yes`.

Interpretation:

- The trust defects are close enough to current enforcement surfaces that a
  bounded repair slice is feasible before larger architecture work.
- This slice should primarily change scripts/tests/fixtures and only minimally
  adjust skill wording if enforcement semantics require it.
- Router sample execution must be treated as a routing-map validator behavior
  first and as release-confidence input second. The plan should not force all
  router sample semantics into the lifecycle eval runner if the correct owner
  is `validate_routing_map.py`.

Assumptions:

- The local command surface should expose `./bin/ask` in normal repo operation.
- Missing `ask` should be classified as a degraded environment/recovery issue,
  not silently converted into a passing or skipped HE release result.
- Existing dirty worktree changes may overlap; implementation must inspect live
  diffs before editing and avoid overwriting unrelated user work.

## Current Known Blockers

These blockers are source-evidenced at spec time and should be rechecked before
editing because the worktree is dirty:

| Blocker | Evidence | Expected Planning Response |
| --- | --- | --- |
| Packaging hygiene may fail on Python bytecode/cache artifacts. | `Plugins/harness-engineering/skills/he-eval-report/scripts/__pycache__/*.pyc` exists in the plugin tree. | Remove generated cache artifacts and prevent recurrence through the existing hygiene check, without changing canonical source files unnecessarily. |
| Router sample skip is currently a warning when samples are not requested. | `validate_routing_map.py` appends `router sample execution skipped` when `--run-router-samples` is absent. | Decide where release-required sample execution is enforced: either invoke `validate_routing_map.py --run-router-samples` in the release lane or add an explicit required-samples gate that converts the warning to a release blocker. |
| Missing `ask` is not preflighted before legacy ask eval runs. | `run_lifecycle_release_evals.py` builds `repo_root / "bin" / "ask"` and executes it inside `_run_ask_eval`. | Add a command-surface preflight or deterministic exception classification so missing/non-executable `ask` becomes a blocked environment result with recovery text. |
| Not-run side-effect closure behavior has a focused failing test. | `test_not_run_side_effect_validator_blocks_completion` currently gets the blocking error path but misses the expected mixed pass/not-run warning. | Preserve the hard error and repair or intentionally revise the warning expectation; do not weaken closure blocking to satisfy the test. |

## Domain Model

```yaml
domain_model:
  status: applicable
  bounded_context: Harness Engineering lifecycle proof
  core_domain_relevance: core
  entities:
    - name: trust_defect
      identity_rule: "A known HE validation or release-confidence failure mode that can permit overstated readiness."
      lifecycle_states: identified, specified, planned, repaired, evaluated, closed
    - name: validation_gate
      identity_rule: "A deterministic script, test, or fixture whose failure changes readiness or closure state."
      lifecycle_states: missing, warning_only, blocking, passing
    - name: closure_claim
      identity_rule: "A recommendation that a slice is safe to close, continue, or hand off."
      lifecycle_states: blocked, needs_rework, complete_with_follow_up, complete
  value_objects:
    - name: degraded_mode
      equality_rule: "environment unavailability plus explicit recovery action"
      immutability_expectation: stable within one eval run
    - name: required_sample_execution
      equality_rule: "router sample marked required by release lane"
      immutability_expectation: stable within one release profile
  aggregates:
    - name: he_trust_repair_slice
      root: selected_slice
      invariants:
        - missing required validation cannot support closure
        - not-run side-effect validators must block completion
        - required router sample skips must reduce release confidence to blocked/fail
        - packaging hygiene must pass before plugin release confidence is claimed
  domain_services:
    - name: release_eval_runner
      reason: aggregates skill eval results and classifies release confidence
    - name: eval_report_validator
      reason: prevents false completion in closure artifacts
  integration_contexts:
    - context: Linear
      translation_rule: Linear tracks the proposed parent/sub-issues only after explicit approval.
    - context: he-eval-report
      translation_rule: closure proof is evaluated after implementation, not inferred from plan completion.
```

## Lifecycle

Expected HE flow:

1. `he-spec` defines this bounded behavior contract.
2. `he-plan` converts this spec into a file-level implementation plan.
3. `he-work` implements only the approved plan slice.
4. `he-code-review` checks that enforcement became deterministic and did not
   broaden scope.
5. `he-eval-report` evaluates closure proof for the selected slice.

No stage should promote later `Next` or `Later` work until Phase 1 has an eval
artifact showing the four trust defects are repaired or explicitly blocked by
environment constraints.

## Interfaces

### Packaging Hygiene Interface

The packaging hygiene check must expose:

```json
{
  "schema_version": 1,
  "root": "absolute plugin root",
  "status": "pass | fail",
  "blocked_paths": []
}
```

Acceptance depends on `status: pass` for the canonical HE plugin tree, or a
specific fail result whose blocked paths are intentionally still present and
tracked as blockers.

### Eval Report Validator Interface

The eval report validator must reject closure when a required side-effect
validator is `not-run`.

Required behavior:

- `Validator Decision: not-run` plus `Blocks Completion: no` is invalid for a
  protected side-effect action.
- The validator emits a hard error that says the not-run validator must block
  completion.
- The validator/test suite preserves the mixed pass/not-run warning contract
  when pass statuses coexist with not-run evidence, but the warning cannot
  downgrade the hard error.

### Release Eval Runner Interface

The lifecycle release eval runner must classify command-surface failure
explicitly and must consume router-sample validation as release-confidence
evidence when the release profile requires routing proof.

Required behavior:

- Missing `./bin/ask` or non-executable `./bin/ask` is reported as a degraded
  environment/recovery condition with an actionable message.
- A missing command surface does not masquerade as a skill eval pass.
- Release output distinguishes `skill_failed`, `runner_unavailable`,
  `runner_timeout`, and `validation_skipped`.
- The JSON summary exposes enough status for `he-eval-report` to decide whether
  closure is blocked without parsing stderr.

### Routing Map Sample Interface

Router sample execution remains owned by
`Plugins/harness-engineering/scripts/validate_routing_map.py`.

Required behavior:

- `validate_routing_map.py --run-router-samples --json` fails when a required
  route sample fails or selects the wrong stage.
- A skipped router sample is allowed only when the caller did not request
  sample execution.
- A release lane that claims router confidence must either run
  `validate_routing_map.py --run-router-samples --json` or record release
  confidence as blocked.
- Optional sample skips may remain warnings only outside release-confidence
  claims.

### Eval Report Closure Interface

`he-eval-report` must treat this slice as closure-sensitive after
implementation.

Required behavior:

- The eval report cites command output for SA-001 through SA-004.
- A not-run or skipped required gate maps to `Blocked` or `Needs rework`, not
  `Complete with follow-up`.
- Linear completion remains `not_applicable` unless a live Linear issue is
  created and linked after this spec.

## Invariants

- Missing validation is never proof.
- Not-run required validators block completion.
- Release-confidence runners must distinguish environment blockers from skill
  behavior failures.
- Required samples cannot be skipped silently.
- Packaging hygiene is a release input, not cosmetic cleanup.
- Phase 1 fixes must not create new HE lifecycle stages.
- Linear remains execution tracking; `.harness` remains cognition and proof.

## Failure And Recovery

| Failure | Required Response | Recovery |
| --- | --- | --- |
| Packaging hygiene reports blocked paths | Block release confidence | Remove generated clutter or document an explicit blocker with path evidence. |
| Not-run side-effect validator does not block completion | Block eval-report closure | Fix validator logic/test until hard error is produced. |
| `ask` missing during release evals | Classify as degraded environment, not HE pass | Emit recovery instruction to restore or run through `./bin/ask`; do not claim release pass. |
| Required router sample execution skipped | Block release confidence | Run the required sample or mark the release lane blocked with reason. |
| Validation command unavailable | Mark blocked, not pass | Record exact command and concrete missing dependency. |
| Fix broadens into Next/Later roadmap | Stop implementation | Return to `he-plan` and split work. |
| Existing focused test already passes | Do not rewrite working logic | Record pass evidence and move to the next unmet acceptance criterion. |

## Observability

Implementation should leave enough evidence for a future agent to answer:

- Which trust defect was repaired?
- Which command or test proves it?
- Did the command pass, fail, or block?
- Was the failure caused by HE behavior or environment unavailability?
- Which later work remains intentionally deferred?

The final eval artifact should cite exact validation commands and outcomes. It
must not summarize proof that was not run.

## Acceptance Matrix

| ID | Requirement | Evidence Required | Closure Impact |
| --- | --- | --- | --- |
| SA-001 | Packaging hygiene for the HE plugin tree passes or reports only explicit blockers. | `python3 Plugins/harness-engineering/scripts/check_packaging_hygiene.py --json` outcome. | Blocks closure if failing without an accepted blocker. |
| SA-002 | Not-run protected side-effect validators block `he-eval-report` completion. | Focused `he-eval-report` test or validator invocation proving the hard error. | Blocks closure if not-run can coexist with completion. |
| SA-003 | Lifecycle release evals classify missing `ask` cleanly. | Focused runner test or controlled command result showing degraded-mode classification and recovery text. | Blocks release confidence if missing `ask` is pass/skip/ambiguous. |
| SA-004 | Required router sample skip/fail behavior is release-blocking. | `validate_routing_map.py --run-router-samples --json` proof plus release-lane proof that skipped samples block router confidence when required. | Blocks release confidence if required samples are silently skipped. |
| SA-005 | The fix remains inside Phase 1 trust-defect repair scope. | Diff review showing no new HE stage, broad authority schema, full artifact index, threat-model skill, tool-audit skill, or Linear mutation. | Blocks handoff if scope expands. |
| SA-006 | Closure proof is written as an eval artifact after implementation. | `.harness/evals/YYYY-MM-DD-agent-skills-he-trust-defect-repair-eval.md` with Artifact Identity and frontmatter safety lint pass. | Blocks Linear closure recommendation if absent. |
| SA-007 | Already-passing trust checks are preserved, not churned. | Focused verify-first evidence showing pass, or a diff explaining why the current pass was insufficient. | Blocks handoff if implementation rewrites passing logic without proof. |
| SA-008 | Mixed pass/not-run warning semantics are explicit. | Focused `he-eval-report` test proves the expected warning is emitted or the test is intentionally revised with rationale while the hard error remains. | Blocks handoff if warning semantics are silently dropped or closure blocking is weakened. |

## Candidate Validation Commands

The plan may refine these commands, but must preserve the proof intent:

| Acceptance IDs | Command | Expected Outcome |
| --- | --- | --- |
| SA-001 | `python3 Plugins/harness-engineering/scripts/check_packaging_hygiene.py --json` | `status: pass` and `blocked_paths: []`, or fail with exact blockers recorded before repair. |
| SA-002, SA-007, SA-008 | `python3 -m pytest Plugins/harness-engineering/skills/he-eval-report/tests/test_validate_eval_report.py -q` | Focused tests pass, including `test_not_run_side_effect_validator_blocks_completion`, without weakening the hard not-run completion blocker. |
| SA-003 | Focused test or controlled invocation of `run_lifecycle_release_evals.py` with unavailable/non-executable `ask`. | JSON result classifies the condition as blocked/degraded with recovery text, not pass. |
| SA-004 | `python3 Plugins/harness-engineering/scripts/validate_routing_map.py --run-router-samples --json` | Router samples execute and failures are hard errors. |
| SA-005 | `git diff --check -- <changed files>` plus HE code review. | No out-of-scope roadmap surfaces added. |
| SA-006 | HE eval artifact lint commands. | Identity and frontmatter safety pass; traceability lint passes for untracked or linked Linear state. |

## Proposed Linear Acceptance Mapping

| Proposed Linear Item | Spec Acceptance IDs |
| --- | --- |
| `[agent-skills] Repair HE trust defects before new capability` | SA-001, SA-002, SA-003, SA-004, SA-005, SA-006, SA-007, SA-008 |
| `[agent-skills] Clear HE packaging hygiene defects` | SA-001 |
| `[agent-skills] Block eval closure on not-run side-effect validators` | SA-002, SA-008 |
| `[agent-skills] Make lifecycle release evals fail cleanly when ask is unavailable` | SA-003 |
| `[agent-skills] Treat required router sample skip as release-blocking` | SA-004 |

## First Slice

The first implementation plan should start with live-state verification, not
editing:

- inspect current packaging hygiene output;
- inspect current `he-eval-report` focused test behavior;
- inspect current release runner handling for missing `ask`;
- inspect current router sample skip/fail behavior;
- then patch the smallest failing surfaces.

If one of the four defects is already fixed in the dirty worktree, the plan
should preserve the fix and only add missing validation or artifact traceability.

## Questions

- Does the user want to create the proposed Linear parent issue before
  implementation, or continue as an untracked repo-hardening slice?
- Which release eval command is considered canonical for final confidence if
  the full lifecycle release lane is too slow for the implementation turn?

These are not blockers for `he-plan`; they are blockers only for Linear mutation
or final milestone closure.

## Done

This spec is done when:

- the artifact passes HE artifact identity, frontmatter safety, and Linear
  traceability lint;
- the next stage can produce a bounded implementation plan for SA-001 through
  SA-008;
- no out-of-scope roadmap work is required to satisfy the first slice.

## he-plan Handoff

Use `he-plan` next with this spec as the selected source artifact.

The plan must:

- preserve the four-defect boundary;
- identify exact files and tests before edits;
- treat any dirty overlapping user changes as source evidence, not something to
  overwrite;
- include validation commands for SA-001 through SA-008;
- defer authority schemas, threat-model stages, artifact indexing, and
  parallel-agent workflows.
