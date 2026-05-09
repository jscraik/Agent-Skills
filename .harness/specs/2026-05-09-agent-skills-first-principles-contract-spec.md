---
schema_version: 1
artifact_id: agent-skills-first-principles-contract-spec
artifact_type: he-spec
canonical_slug: agent-skills-first-principles-contract
title: First-Principles Contract Spec
harness_stage: he-spec
status: draft
date: 2026-05-09
traceability_required: false
origin: .harness/linear/2026-05-09-agent-skills-first-principles-contract-linear-plan.md
linear_issue: not_created
linear_milestone: HE First-Principles Gate (proposed)
risk: architecture_sensitive
depth: standard
ui: false
---

# First-Principles Contract Spec

## Mode Decision

This is an untracked Harness Engineering plugin-hardening spec produced from the
proposed `HE First-Principles Gate` Linear plan and the current HE lifecycle
contracts.

The selected execution slice is:

`Add first-principles restraint to Harness Engineering without adding a new stage`

No Linear object has been created. Traceability is marked `false` because the
source Linear plan is a proposal, not an active tracker. A future implementation
may proceed as an untracked repo-hardening slice, but no Linear completion,
milestone closure, or project status change can be recommended until a real
Linear parent issue or milestone exists.

## Problem

Harness Engineering now has strong lifecycle, strategy, domain, eval, Linear,
interactive steering, specialist-routing, and artifact contracts. That power
creates a failure mode: agents can copy serious-looking process from other
systems and expand HE with more stages, artifacts, Linear work, reviews, or
governance without proving that a real HE failure is being prevented.

The plugin needs a small restraint gate that asks what failure the new process
prevents, what the smallest effective mechanism is, and whether an eval can
prove the behavior. The gate must preserve production-grade rigor for risky
work while preventing copied sophistication from increasing context load,
routing ambiguity, or issue volume.

## Goals

- Add a compact first-principles contract for Harness Engineering.
- Make the contract conditionally discoverable through deferred context routing.
- Wire the contract into the lifecycle only where it changes routing, scope, or
  closure behavior.
- Preserve the current HE philosophy: traceable intent, deterministic routing,
  bounded proof, and closure based on evidence.
- Prevent new HE stages, artifacts, Linear objects, or governance from being
  added just because other serious systems have them.
- Add negative eval coverage that proves HE can reject or defer copied process
  when no verified failure exists.
- Keep reversible low-risk work fast.
- Route irreversible architecture, governance, or closure decisions to proof.

## Non-Goals

- Do not create a standalone `he-first-principles` skill.
- Do not rewrite the full HE lifecycle.
- Do not inject the long source article or philosophical prompt into hot-path
  skill entrypoints.
- Do not create Linear objects.
- Do not create one issue per lifecycle skill.
- Do not make first-principles analysis a mandatory artifact for every task.
- Do not replace gate selection, interactive steering, specialist steering, or
  eval-report closure rules.
- Do not use first principles as a reason to bypass validation.

## Linear Contract

Current Linear state:

- Linear project: `agent-skills` proposed.
- Linear milestone: `HE First-Principles Gate` proposed.
- Linear parent issue: not created.
- Linear status: no mutation authorized.

Closure rule:

- This spec may hand off to `he-plan` as an untracked repo-hardening slice.
- If the user wants Linear execution, create or link the parent issue before any
  Linear completion recommendation.
- If implementation finishes without a Linear tracker, the eval report must say
  `Linear closure not applicable` rather than marking work complete in Linear.

## Boundary

### In Scope

- Create `Plugins/harness-engineering/references/first-principles-contract.md`.
- Add one conditional-loading row to
  `Plugins/harness-engineering/references/deferred-context-index.md`.
- Add concise lifecycle references only where the contract prevents bloat or
  unsafe closure.
- Include `he-brainstorm` in the first slice because survivor selection is one
  of the requested negative eval cases.
- Add or update targeted eval fixtures for first-principles restraint.
- Sync projections after canonical source edits.
- Validate source, projection, and behavior with focused commands.

### Out of Scope

- New plugin or skill packaging.
- New HE router stage.
- Cross-repo rollout.
- Linear mutation.
- Broad rewrite of existing strategy/spec/plan/eval prompts.
- Runtime cache edits as source of truth.
- Security review unless the implementation touches permissions, secrets,
  sandboxing, external writes, or user data exposure.

## Baseline

Source evidence:

- `.harness/linear/2026-05-09-agent-skills-first-principles-contract-linear-plan.md`
  proposes the repo-specific slice and explicitly rejects a standalone skill.
- `Plugins/harness-engineering/references/gate-selection-contract.md` already
  defines the smallest proof surface for trivial, standard, architecture,
  closure, domain, security, and mixed-risk work.
- `Plugins/harness-engineering/references/artifact-routing-contract.md` already
  defines dated artifact identity and stable `canonical_slug` behavior.
- `Plugins/harness-engineering/skills/he-spec/SKILL.md` requires source-backed
  acceptance criteria and bounded specs.

Interpretation:

- First principles should sit before expansion decisions as a restraint filter.
- Gate selection remains the mechanism that decides how much proof is required
  after the failure and risk are identified.

Assumption:

- The recurring failure is copied process and artifact expansion, not missing
  philosophical language.

## Domain Model

```yaml
domain_model:
  status: applicable
  bounded_context: Harness Engineering lifecycle governance
  core_domain_relevance: core
  entities:
    - name: verified_failure
      identity_rule: observed repeated, high-risk, or moat-critical HE failure
      lifecycle_states: proposed, evidenced, rejected, deferred, accepted
    - name: lifecycle_expansion
      identity_rule: added skill, stage, artifact, Linear object, eval, reference, or governance rule
      lifecycle_states: requested, gated, planned, implemented, removed
  value_objects:
    - name: first_principles_check
      equality_rule: failure plus smallest mechanism plus proof requirement
      immutability_expectation: stable within one stage decision
    - name: decision_type
      equality_rule: Type 1 irreversible or Type 2 reversible
      immutability_expectation: may change only when evidence changes
  aggregates:
    - name: execution_slice
      root: selected_slice
      invariants:
        - one selected slice drives the stage
        - copied external patterns do not expand scope without HE-specific failure evidence
        - Linear remains execution state, not cognition storage
        - closure requires proof, not implementation status
  domain_services:
    - name: first_principles_gate
      reason: decides whether a proposed HE mechanism deserves to exist before gate selection determines depth
  integration_contexts:
    - context: gate_selection
      translation_rule: first-principles identifies the failure and mechanism; gate selection selects risk and proof
    - context: evals
      translation_rule: negative evals prove restraint, not just capability
    - context: Linear
      translation_rule: only execution state becomes Linear work; cognition stays in .harness
  resolved_model_decisions:
    - include `he-brainstorm` in the first implementation slice because survivor selection is a requested negative eval case
  closure_impact: blocks_plan_if_no_acceptance_matrix
```

## Lifecycle

Expected stage behavior:

1. `he-strategy` uses first principles to separate irreducible core, copied
   assumptions, actual moat, false moat, deletion candidates, and safe rewrite
   zones.
2. `he-spec` uses first principles to define the verified failure, smallest
   effective mechanism, rejected analogy, and proof needed before planning.
3. `he-plan` uses first principles to keep the first slice reversible and proof
   producing.
4. `he-linear-plan` uses first principles to avoid issue explosion and keep
   Linear as execution state rather than cognition storage.
5. `he-eval-report` uses first principles to ask whether implementation solved
   the original failure before recommending completion.
6. `he-brainstorm` uses first principles to force survivor selection back to
   the verified failure, smallest effective mechanism, and context-load effect
   before allowing a new idea to survive.
7. `he-code-review` uses first principles to flag added abstraction or process
   that does not reduce a verified failure.

The lifecycle wiring must remain reference-only. Each skill should load the
contract only when its stage is deciding whether to add, retain, route, close,
or reject a mechanism. Routine use of the skill must not pay the full context
cost of the contract.

## Interfaces

### Reference Contract Interface

Create:

`Plugins/harness-engineering/references/first-principles-contract.md`

Required content:

```yaml
first_principles_check:
  verified_failure: ""
  fundamental_constraint: ""
  assumption_being_challenged: ""
  smallest_effective_mechanism: ""
  analogy_or_template_rejected: ""
  proof_required: ""
  context_load_effect: reduced|neutral|increased|unknown
  routing_effect: clearer|neutral|more_ambiguous|unknown
  decision_type: Type 1|Type 2
  outcome: proceed|ask|defer|reject|delete_or_collapse
```

Required rule:

`If the reason is "because serious systems usually have this", reject or defer.`

### Deferred Context Interface

Update:

`Plugins/harness-engineering/references/deferred-context-index.md`

Add a trigger row that loads the contract only for:

- requested new HE stage, skill, artifact, Linear object, governance rule, eval
  lane, or reference;
- copied process or external-plugin improvement proposals;
- strategy, refactor, Linear, or closure work where multiple valid expansion
  paths exist;
- headless mode where assumptions must be recorded instead of asking.

### Lifecycle Skill Interface

Lifecycle skill entrypoints must stay compact. Wiring should be one or two
sentences plus a reference link, not duplicated contract prose.

Minimum wiring targets:

| Skill | First-principles trigger | Required behavior |
| --- | --- | --- |
| `he-brainstorm` | survivor selection, copied external pattern, multiple viable ideas | ask or record which survivor prevents a verified failure and why lower-leverage ideas are rejected |
| `he-strategy` | strategic direction, moat claims, deletion/core decisions | separate irreducible core from copied assumptions and false moat signals |
| `he-spec` | acceptance criteria for a new mechanism | require verified failure, smallest mechanism, rejected analogy, and proof |
| `he-plan` | implementation sequencing | choose the smallest proof-producing slice and keep Type 2 decisions fast |
| `he-linear-plan` | Linear object creation or routing | keep active set small; classify low-value work as `Do Not Create` |
| `he-eval-report` | completion or closure recommendation | verify the implementation solved the original failure before recommending completion |
| `he-code-review` | review of lifecycle, governance, eval, routing, or abstraction changes | flag process, abstraction, or Linear expansion without verified failure evidence |

Non-targets for the first slice:

- `he-work`: implementation should consume the plan/spec proof but does not need
  first-principles routing unless it starts expanding scope.
- `he-compound`: learning capture should reference the result only after the
  implementation produces durable learning.

## Invariants

- Harness Engineering exists to preserve intent through execution.
- Process is justified only when it prevents a verified HE failure.
- Artifacts are justified only when they improve future reasoning or proof.
- Linear objects are justified only when execution state must be tracked.
- New skills are justified only when routing becomes clearer.
- Governance is justified only when ambiguity, drift, or unsafe closure is
  reduced.
- Reversible low-risk decisions should keep a fast path.
- Irreversible architecture, governance, routing, or closure decisions require
  stronger proof.
- Negative evals must prove restraint as well as capability.

## Failure / Recovery

| Failure | Recovery |
| --- | --- |
| Contract becomes a broad philosophy essay | Compress it to the decision rubric and HE-specific rules. |
| Lifecycle entrypoints become longer | Move detail back to the reference contract. |
| First-principles gate duplicates gate selection | Keep first principles as the existence filter and gate selection as the proof-depth filter. |
| Evals only prove the system can add process | Add negative cases proving reject, defer, delete, or fast-path behavior. |
| Linear plan expands into many issues | Collapse to one parent and minimal sub-issues, or classify as `Do Not Create`. |
| Headless mode asks interactive questions | Record assumptions, confidence, and repair path instead. |
| Implementation creates `he-first-principles` | Treat as scope breach unless explicitly approved after this slice. |

## Observability

The implementation must leave visible proof in:

- source diff showing the new reference contract;
- deferred-context index routing row;
- lifecycle skill references;
- eval fixtures or equivalent test cases;
- projection sync output;
- handle or audit validation output;
- final plan/eval handoff that states whether Linear tracking exists.

## Decision Rules

The contract must force a clear outcome before any new HE process surface is
added.

| Proposed mechanism | Required decision rule | Expected outcome |
| --- | --- | --- |
| New stage or skill | Must identify a repeated or high-risk failure that current stages cannot prevent. | proceed only if routing becomes clearer; otherwise reject or fold into an existing skill |
| New reference contract | Must reduce repeated prompt/context load or encode a reusable invariant. | proceed when it compresses; reject if it only stores prose |
| New eval lane | Must prove behavior that cannot be covered by a targeted fixture. | proceed only for recurring lifecycle risk; otherwise add a small fixture |
| New Linear object | Must track execution state, not cognition state. | create minimal parent/sub-issue set or classify `Do Not Create` |
| New governance rule | Must reduce ambiguity, drift, or unsafe closure with observable enforcement. | proceed with enforcement proof; otherwise defer |
| External template adoption | Must name the HE-specific failure it prevents. | reject or defer when the only reason is analogy |

## Eval Fixture Requirements

The eval layer must prove restraint with negative cases. Capability-only evals
are insufficient.

| Eval case | Input pressure | Expected behavior | Blocking acceptance |
| --- | --- | --- | --- |
| `first-principles-rejects-template-copying` | user asks to copy another plugin's lifecycle stage with no HE failure evidence | asks for the verified failure or rejects/defer; does not create a new stage | yes |
| `first-principles-brainstorm-survivor-selection` | brainstorm produces multiple plausible improvements | survivor choice names verified failure, smallest mechanism, context-load effect, and rejected alternatives | yes |
| `first-principles-compresses-linear-noise` | review produces many observations | classifies into `Now`, `Next`, `Later`, `Do Not Create`; avoids one issue per observation | yes |
| `first-principles-routes-type1-to-proof` | irreversible architecture/governance/routing decision requested | routes to stronger proof and records required evidence before implementation or closure | yes |
| `first-principles-allows-type2-fast-path` | reversible low-risk edit requested | avoids broad strategy/refactor/eval ceremony and records skipped gates | yes |
| `first-principles-records-assumptions-headless` | autonomous/headless mode cannot ask | records assumptions, confidence, and repair path instead of blocking on interactive input | yes |
| `first-principles-eval-closure-challenge` | eval report is asked to recommend Linear completion | asks accept/challenge/rework or records headless equivalent before recommending completion | yes |

Each fixture should assert both the positive action and the forbidden behavior.
For example, the copied-template case must assert that no standalone
`he-first-principles` skill is recommended without explicit evidence and human
approval.

## Gate Profile

```yaml
gate_profile:
  risk_class: architecture_sensitive
  proven_risks:
    - copied_process
    - governance_bloat
    - context_load_growth
    - routing_ambiguity
    - false_completion_confidence
  required_contracts:
    - Plugins/harness-engineering/references/gate-selection-contract.md
    - Plugins/harness-engineering/references/artifact-routing-contract.md
    - Plugins/harness-engineering/references/deferred-context-index.md
    - Plugins/harness-engineering/references/interactive-steering-contract.md
    - Plugins/harness-engineering/references/specialist-skill-steering-contract.md
  skipped_contracts:
    - contract: Plugins/harness-engineering/references/domain-model-production-contract.md
      reason: no product domain model, persistence, account, billing, or business state semantics are changed by this slice
    - contract: Plugins/harness-engineering/skills/he-refactor/SKILL.md
      reason: this is a small contract addition, not a structural migration program
    - contract: codex-security plugin scan
      reason: security is not triggered unless implementation touches permissions, secrets, sandboxing, external writes, or user data exposure
    - contract: Linear mutation
      reason: the current tracker is proposed only and user has not authorized Linear object creation
  minimum_proof_required:
    continue_to_next_stage: spec identity lint passes and acceptance criteria are sufficient for he-plan
    safe_to_close: implementation source, projection sync, handles/audits, and targeted negative evals pass or have explicit blockers
    block_next_stage: missing selected slice, missing acceptance IDs, or pretending proposed Linear work is an active tracker
  evidence_basis: harness
  downstream_route: he-plan
```

## Acceptance Matrix

| ID | Requirement | Evidence | Blocks handoff |
| --- | --- | --- | --- |
| SA-001 | Create `first-principles-contract.md` with a compact HE-specific decision rubric. | File exists, contains required fields, and avoids long copied prompt prose. | yes |
| SA-002 | Add deferred-context routing so the contract loads only for expansion, copied-process, multiple-route, closure, or headless-assumption cases. | `deferred-context-index.md` row references the contract with triggers and proof. | yes |
| SA-003 | Wire the contract into selected lifecycle skills with concise references. | Skill diffs show reference hooks in `he-brainstorm`, `he-strategy`, `he-spec`, `he-plan`, `he-linear-plan`, `he-eval-report`, and `he-code-review`. | yes |
| SA-004 | Do not create a standalone `he-first-principles` skill. | No new skill directory or handle exists for that name. | yes |
| SA-005 | Add negative eval coverage for copied-template rejection. | Eval fixture proves HE rejects or defers a process copied from another system when no verified HE failure exists. | yes |
| SA-006 | Add negative eval coverage for Linear compression. | Eval fixture proves observations become minimal Linear objects or `Do Not Create`, not issue explosion. | yes |
| SA-007 | Add eval coverage for Type 1 and Type 2 routing. | Eval fixtures prove irreversible changes route to proof and reversible low-risk changes fast-path. | yes |
| SA-008 | Add headless/autonomous behavior coverage. | Eval fixture proves assumptions are recorded instead of asking when interactive steering is unavailable. | yes |
| SA-009 | Keep first principles distinct from gate selection. | Contract or lifecycle wording states first principles decides whether the mechanism should exist; gate selection decides proof depth. | yes |
| SA-010 | Sync and validate source-to-projection state. | Sync/projection commands pass or blockers are documented with exact failure text. | yes |
| SA-011 | Preserve dated artifact style and stable identity. | New `.harness` artifacts use date-prefixed filenames, matching frontmatter date, and stable `canonical_slug`. | yes |
| SA-012 | Avoid security overreach. | Security gate is skipped with evidence unless sensitive files or behaviors are touched. | no |
| SA-013 | Assert forbidden behaviors in evals. | Targeted evals check both the expected route and the forbidden expansion, such as creating a new stage from analogy alone. | yes |
| SA-014 | Keep hot-path context bounded. | Lifecycle skill entrypoint diffs add concise trigger/reference wording and do not duplicate the full contract. | yes |

## Proposed Linear Acceptance Mapping

| Proposed Linear object | Acceptance IDs |
| --- | --- |
| `[agent-skills] Add first-principles restraint gate to Harness Engineering` | SA-001 through SA-014 |
| `[agent-skills] Add HE first-principles contract reference` | SA-001, SA-002, SA-009 |
| `[agent-skills] Wire first-principles gate into HE lifecycle skills` | SA-003, SA-004, SA-009, SA-014 |
| `[agent-skills] Add first-principles negative eval coverage` | SA-005, SA-006, SA-007, SA-008, SA-013 |
| `[agent-skills] Validate and sync first-principles HE projection` | SA-010, SA-011, SA-012, SA-014 |

Traceability gap:

- The objects above are proposed by the Linear plan but have not been created.
- If a Linear issue is created later, update this section and set
  `traceability_required: true`.

## Validation Plan

Minimum commands for implementation:

```bash
./bin/ask skills sync --scope workspace --projection rooted --json --robot
./bin/ask skills handles --check --json --robot
./bin/ask skills audit Plugins/harness-engineering/skills/he-strategy --level strict --json --robot
./bin/ask skills audit Plugins/harness-engineering/skills/he-spec --level strict --json --robot
./bin/ask skills audit Plugins/harness-engineering/skills/he-plan --level strict --json --robot
./bin/ask skills audit Plugins/harness-engineering/skills/he-linear-plan --level strict --json --robot
bash Infrastructure/scripts/validation-and-linting/validate_he_progressive_disclosure.sh
python3 Infrastructure/scripts/lifecycle-and-sync/projection_integrity.py verify --scope all
```

Targeted behavioral validation:

- copied template request asks for verified failure or rejects/defer;
- brainstorm survivor selection uses a blocking question when survivor choice
  depends on a Type 1 expansion;
- Linear destination ambiguity asks instead of assuming JSC;
- post-plan handoff asks before work when multiple next stages are valid;
- eval closure asks accept/challenge/rework before recommending completion;
- headless mode records assumptions instead of asking.

The eval implementation must also assert forbidden behavior for each case. A
passing response that adds the correct wording while still creating issue
explosion, a new standalone skill, or closure without proof is a failed eval.

## First Slice

Implement the smallest slice that proves the gate works:

1. Add the first-principles reference contract.
2. Add deferred-context routing.
3. Wire only the selected lifecycle skills, including `he-brainstorm` for
   survivor-selection coverage.
4. Add the targeted negative eval cases.
5. Sync projections and run focused validation.

Do not add second-order lifecycle surfaces. The first slice proves behavior in
existing skills only.

## Questions

- Should the proposed Linear plan be turned into a real Linear parent issue
  before implementation, or should this remain an untracked plugin-hardening
  slice?
- Which existing eval harness path is the canonical place for the new negative
  cases?

## Done

This spec is ready for `he-plan` when:

- artifact identity lint passes;
- acceptance IDs are stable;
- the Linear traceability gap is explicit;
- the gate profile is present;
- open questions are acceptable for planning rather than blocking specification.

Implementation is not complete until:

- SA-001 through SA-014 pass or have justified blockers;
- any touched projections are synced;
- targeted negative evals prove restraint;
- the eval report confirms whether Linear closure is applicable.

## he-plan Handoff

Recommended next stage: `he-plan`.

The plan should include `he-brainstorm` in the first source wiring because one
acceptance case covers survivor selection. Keep the patch bounded and still
avoid creating a standalone first-principles skill.

## Evidence & Traceability

| Claim | Evidence type | Paths | Confidence | Operational impact |
| --- | --- | --- | --- | --- |
| First principles should be a contract, not a standalone skill. | source plan | `.harness/linear/2026-05-09-agent-skills-first-principles-contract-linear-plan.md` | high | avoids route sprawl |
| HE already has proof-depth routing. | source contract | `Plugins/harness-engineering/references/gate-selection-contract.md` | high | avoids duplicating gate selection |
| New artifacts need stable identity and dated style. | source contract | `Plugins/harness-engineering/references/artifact-routing-contract.md` | high | keeps agentic search and traceability reliable |
| The current work is not Linear-tracked. | source plan inspection | `.harness/linear/2026-05-09-agent-skills-first-principles-contract-linear-plan.md` | high | prevents false closure recommendations |
| Security review is not required by default. | reasoned gate selection | no sensitive source path identified in this spec | medium | avoids unnecessary specialist overhead |
