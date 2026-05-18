---
schema_version: 1
artifact_id: agent-skills-first-principles-contract-plan
artifact_type: he-plan
canonical_slug: agent-skills-first-principles-contract
title: First-Principles Contract Plan
harness_stage: he-plan
status: deepened
date: 2026-05-09
traceability_required: false
origin: .harness/specs/2026-05-09-agent-skills-first-principles-contract-spec.md
linear_issue: not_created
linear_milestone: HE First-Principles Gate (proposed)
risk: architecture_sensitive
depth: standard
ui: false
---

# First-Principles Contract Plan

## Executive Plan Summary

This plan implements a first-principles pressure gate for Harness Engineering without creating a new standalone `he-first-principles` skill.

The implementation should add one reusable reference contract, wire it into the lifecycle skills where copied-process drift is most likely, add negative eval coverage, and validate that source state, routing state, and projected skill manifests remain aligned.

The goal is restraint:

- prevent lifecycle expansion based only on analogy or borrowed process
- force new stages, artifacts, Linear objects, and governance to name the verified failure they prevent
- preserve Harness Engineering's existing philosophy of traceable, proof-backed execution
- keep hot-path skills concise and defer deeper context to references

## Source Evidence

| Source | Evidence Used | Planning Impact |
|---|---|---|
| `.harness/specs/2026-05-09-agent-skills-first-principles-contract-spec.md` | Defines required lifecycle targets, acceptance IDs `SA-001` through `SA-014`, required YAML contract shape, and negative eval scenarios. | Primary execution contract. |
| `.harness/review/2026-05-09-agent-skills-first-principles-contract-technical-review.md` | Approves the spec for `he-plan`, resolves `he-brainstorm` omission, and flags eval-fixture path selection as the remaining implementation unknown. | Confirms this plan should include `he-brainstorm` and resolve eval routing before implementation. |
| `Plugins/harness-engineering/skills/he-plan/SKILL.md` | Requires durable plan artifacts, implementation-unit traceability, validation gates, rollback strategy, and post-plan handoff. | Defines this artifact's structure and closeout requirements. |
| `Plugins/harness-engineering/skills/he-plan/references/plan-artifact-contract.md` | Requires stable implementation IDs, acceptance traceability, concrete validation gates, and explicit unknowns. | Drives `PU-*` and `SA-*` mapping. |
| `Plugins/harness-engineering/scripts/check_gate_selection_wiring.py` | Existing wiring checks expect stage-local eval files and plugin-level lifecycle tracer evals. | Resolves the eval path decision: stage behavior belongs in stage-local `references/evals.yaml`; cross-stage behavior belongs in lifecycle tracer evals. |
| `Docs/agents/16-agent-operating-contract.md` | Confirms `./bin/ask` command contracts for `skills explain`, `skills prove`, `skills audit`, and repo operations. | Verifies planned command shapes before implementation. |
| `Docs/agents/17-skill-management.md` | Requires `UBIQUITOUS_LANGUAGE.md` before changing skills, sync policy, runtime projections, or agent-facing docs. | Adds a pre-implementation source-read gate before skill edits. |
| `Plugins/harness-engineering/references/deferred-context-index.md` | Contains both a Runtime Reference Map and a Conditional Loading Map. | Requires first-principles contract to be wired into both maps, not only one table row. |

## Planning Decisions

### Synthesis Checkpoint

Stated:

- The approved slice is to add a first-principles gate to the Harness Engineering lifecycle.
- The gate must use the original first-principles prompt intent without becoming a new top-level skill.
- The implementation must be validated with eval cases and routed through existing Harness Engineering skill/source conventions.

Inferred:

- The correct implementation shape is a reference contract plus thin lifecycle hooks because the change is cross-cutting behavior, not a new artifact generator.
- Stage-local eval files are the primary home for stage behavior because existing `references/evals.yaml` files already carry stage-owned cases.
- A static validator is necessary because prompt and routing contracts otherwise have no deterministic implementation proof.

Out of scope:

- adding a public `he-first-principles` handle
- treating first-principles thinking as a philosophy document without eval-backed routing behavior
- broad refactors to the Harness Engineering lifecycle while implementing this slice

### Decision 1: Use A Reference Contract, Not A New Skill

Create `Plugins/harness-engineering/references/first-principles-contract.md`.

Do not create:

- `Plugins/harness-engineering/skills/he-first-principles/`
- a new public handle
- a new lifecycle stage

Reason: the desired behavior is a cross-cutting quality gate, not a new artifact-producing phase. A separate skill would add routing surface area and weaken the first-principles objective by creating more process.

### Decision 2: Keep Lifecycle Wiring Thin

Each lifecycle skill should reference the contract with a short operational hook and a reference pointer. The contract content must not be copied into every `SKILL.md`.

Reason: copied contract prose would increase context load, create drift between skills, and make future edits harder to validate.

### Decision 3: Resolve Eval Routing By Stage Ownership

Use stage-local eval files for stage-specific behavior:

- `Plugins/harness-engineering/skills/he-brainstorm/references/evals.yaml`
- `Plugins/harness-engineering/skills/he-strategy/references/evals.yaml`
- `Plugins/harness-engineering/skills/he-spec/references/evals.yaml`
- `Plugins/harness-engineering/skills/he-plan/references/evals.yaml`
- `Plugins/harness-engineering/skills/he-linear-plan/references/evals.yaml`
- `Plugins/harness-engineering/skills/he-eval-report/references/evals.yaml`
- `Plugins/harness-engineering/skills/he-code-review/references/evals.yaml`

Use plugin-level lifecycle evals only for cross-stage routing behavior:

- `Plugins/harness-engineering/references/lifecycle-tracer-evals.yaml`

Reason: this matches the existing Harness Engineering pattern visible in wiring validators and avoids hiding stage expectations in one central file.

Implementation constraint: preserve each eval file's existing schema and local anchors. The sampled stage eval files use `schema_version: "2.0"`, `x_modes`, `x_safe`, `x_accept`/`x_steer`, and `cases`. New cases should follow that local shape rather than introducing a second eval format. The lifecycle tracer file uses `schema_version: "1.0"` with route-oriented `cases`, so the headless cross-stage case must follow that simpler shape.

### Decision 4: Add A Static Wiring Validator

Add `Plugins/harness-engineering/scripts/check_first_principles_contract_wiring.py`.

The validator should check:

- contract file exists
- required contract fields are present
- deferred context index references the contract
- lifecycle skills reference the contract
- required eval case names exist in the expected eval files
- no standalone `he-first-principles` skill directory exists

Reason: the behavior is mostly prompt/routing contract work, so a static wiring check gives deterministic proof that the lifecycle was actually connected.

Implementation constraint: model the validator after `Plugins/harness-engineering/scripts/check_gate_selection_wiring.py`. Keep it dependency-light, JSON-capable, and deterministic so it can run in preflight-style checks without network or plugin runtime state.

## Scope

In scope:

- first-principles reference contract
- deferred-context routing row
- lifecycle skill wiring for the approved target skills
- targeted negative eval scenarios
- a wiring validator for contract, skill, and eval coverage
- projection sync and focused validation
- later eval-report handoff after implementation

Out of scope:

- creating Linear objects
- creating a standalone `he-first-principles` skill
- rewriting the full Harness Engineering lifecycle
- broad plugin-wide eval remediation
- changing unrelated skillset manifests except through required sync/projection commands
- modifying the existing proposed Linear plan beyond using it as source context

Pre-implementation source-read gate:

- Read `UBIQUITOUS_LANGUAGE.md` before changing skills, sync policy, runtime projections, or agent-facing docs.
- Re-check `Docs/agents/16-agent-operating-contract.md` and `Docs/agents/17-skill-management.md` if command or skill-audit assumptions change during implementation.

## File Ownership And Editing Order

| Order | File Set | Owner | Why This Comes Here |
|---|---|---|---|
| 1 | `Plugins/harness-engineering/references/first-principles-contract.md` | canonical reference source | Establishes stable path and vocabulary for all later hooks. |
| 2 | `Plugins/harness-engineering/references/deferred-context-index.md` | deferred context router | Adds the reference to both Runtime Reference Map and Conditional Loading Map so the contract is discoverable and triggerable without loading it by default. |
| 3 | lifecycle `SKILL.md` files | stage entrypoints | Adds thin behavioral hooks after the contract path exists. |
| 4 | stage-local `references/evals.yaml` files | stage eval surfaces | Proves changed behavior where each lifecycle stage owns it. |
| 5 | `Plugins/harness-engineering/references/lifecycle-tracer-evals.yaml` | cross-stage route proof | Captures headless and lifecycle-spanning behavior only. |
| 6 | `Plugins/harness-engineering/scripts/check_first_principles_contract_wiring.py` | deterministic wiring proof | Encodes expected contract, skill, and eval links after final paths are known. |
| 7 | `.skillsets/**` and command-surface projections | generated projection output | Update only through the repo sync command after canonical edits are complete. |

Do not hand-edit `.skillsets/**` projections for this slice. If projection output changes after sync, inspect it and keep only changes traceable to the canonical Harness Engineering sources touched above.

## Implementation Units

### PU-001: Add The First-Principles Reference Contract

Objective: add the canonical contract at `Plugins/harness-engineering/references/first-principles-contract.md`.

Required content:

- definition of first-principles behavior for Harness Engineering
- rule rejecting additions justified only by copied templates or generic best practice language
- required check fields:
  - `verified_failure`
  - `fundamental_constraint`
  - `assumption_being_challenged`
  - `smallest_effective_mechanism`
  - `analogy_or_template_rejected`
  - `proof_required`
  - `context_load_effect`
  - `routing_effect`
  - `decision_type`
  - `outcome`
- autonomous/headless behavior: record assumptions instead of asking
- interaction with risk-based gate selection
- guidance for Type 1 and Type 2 decisions
- examples for proceed, ask, defer, reject, and delete/collapse outcomes

Contract section outline:

1. Purpose
2. When To Load
3. Required First-Principles Check
4. Decision Type Routing
5. Outcome Semantics
6. Headless And Autonomous Mode
7. Lifecycle Application Points
8. Anti-Patterns
9. Minimal Examples

Required anti-patterns:

- adding a stage because another plugin has a similar stage
- creating a Linear issue for cognition-only context
- adding a review or governance step that has no enforcement path
- expanding prompts when a validator or eval would prove the behavior more cheaply
- creating a standalone skill before repeated usage proves a routing need

Acceptance covered:

- `SA-001`
- `SA-002`
- `SA-004`
- `SA-005`
- `SA-008`
- `SA-009`
- `SA-011`
- `SA-012`

Validation:

- `python3 Plugins/harness-engineering/scripts/check_first_principles_contract_wiring.py`
- manual inspection that the contract remains reference-sized and does not become a lifecycle essay

Rollback:

- remove the reference file and remove all downstream references added in later units

### PU-002: Add Deferred Context Routing

Objective: make the contract discoverable without loading it by default.

Edit:

- `Plugins/harness-engineering/references/deferred-context-index.md`

Required behavior:

- add `references/first-principles-contract.md` to the Runtime Reference Map in the closest relevant category
- add a Conditional Loading Map row for lifecycle expansion, copied-template risk, new stage/artifact/Linear object requests, and governance additions
- keep the deferred index as routing metadata only

Acceptance covered:

- `SA-003`
- `SA-010`

Validation:

- `python3 Plugins/harness-engineering/scripts/check_first_principles_contract_wiring.py`
- `rg -n "first-principles-contract" Plugins/harness-engineering/references/deferred-context-index.md`

Rollback:

- remove the deferred index row and any associated route wording

### PU-003: Wire The Contract Into Main Lifecycle Skills

Objective: apply the contract at the lifecycle points where process copying, stage expansion, Linear noise, or false closure are most likely.

Edit:

- `Plugins/harness-engineering/skills/he-brainstorm/SKILL.md`
- `Plugins/harness-engineering/skills/he-strategy/SKILL.md`
- `Plugins/harness-engineering/skills/he-spec/SKILL.md`
- `Plugins/harness-engineering/skills/he-plan/SKILL.md`
- `Plugins/harness-engineering/skills/he-linear-plan/SKILL.md`
- `Plugins/harness-engineering/skills/he-eval-report/SKILL.md`
- `Plugins/harness-engineering/skills/he-code-review/SKILL.md`

Required behavior by skill:

| Skill | Required First-Principles Hook |
|---|---|
| `he-brainstorm` | survivor selection must prefer ideas that prevent verified failures and reject ideas that only imitate another process |
| `he-strategy` | strategy must separate irreducible core from copied assumptions, false moat signals, and deletion/collapse candidates |
| `he-spec` | specs must name the verified failure, smallest effective mechanism, and assumption being challenged before expanding scope |
| `he-plan` | plans must choose the smallest proof-producing implementation slice and identify Type 1 vs Type 2 decisions |
| `he-linear-plan` | Linear work must be created only when execution state is needed, with `Do Not Create` used for cognition-only findings |
| `he-eval-report` | closure must prove the implemented work solved the original verified failure before recommending Linear completion |
| `he-code-review` | reviews must flag implementation that adds sophistication without reducing a verified failure, drift risk, or proof gap |

Hook placement guidance:

- add one procedure bullet where the behavior affects execution
- add one reference entry pointing to `Plugins/harness-engineering/references/first-principles-contract.md`
- avoid duplicating the full check fields in every skill
- keep examples unchanged unless an existing example would now contradict the contract
- preserve each skill's current side-effect boundary wording

Acceptance covered:

- `SA-003`
- `SA-004`
- `SA-006`
- `SA-007`
- `SA-008`
- `SA-009`
- `SA-010`
- `SA-011`
- `SA-012`
- `SA-013`

Validation:

- `python3 Plugins/harness-engineering/scripts/check_first_principles_contract_wiring.py`
- focused `./bin/ask skills explain <handle> --json --robot` checks for changed handles, where available
- no copied full contract blocks inside lifecycle `SKILL.md` files

Rollback:

- remove the short contract hooks and references from each lifecycle skill

### PU-004: Add Negative Eval Coverage

Objective: prove the contract changes behavior and prevents process expansion when evidence is weak.

Edit stage-local eval files:

- `Plugins/harness-engineering/skills/he-brainstorm/references/evals.yaml`
- `Plugins/harness-engineering/skills/he-strategy/references/evals.yaml`
- `Plugins/harness-engineering/skills/he-spec/references/evals.yaml`
- `Plugins/harness-engineering/skills/he-plan/references/evals.yaml`
- `Plugins/harness-engineering/skills/he-linear-plan/references/evals.yaml`
- `Plugins/harness-engineering/skills/he-eval-report/references/evals.yaml`
- `Plugins/harness-engineering/skills/he-code-review/references/evals.yaml`

Edit cross-stage eval file if supported by the existing structure:

- `Plugins/harness-engineering/references/lifecycle-tracer-evals.yaml`

Required eval case mapping:

| Eval Case | Primary File | Required Assertion |
|---|---|---|
| `first-principles-brainstorm-survivor-selection` | `he-brainstorm/references/evals.yaml` | ambiguous survivor selection asks or blocks instead of silently selecting analogy-driven ideas |
| `first-principles-rejects-template-copying` | `he-strategy/references/evals.yaml` | copied external process is rejected or deferred unless tied to a verified HE failure |
| `first-principles-spec-smallest-mechanism` | `he-spec/references/evals.yaml` | spec identifies the smallest evidence-backed mechanism before expanding scope |
| `first-principles-routes-type1-to-proof` | `he-plan/references/evals.yaml` | irreversible or architecture-sensitive work is routed through proof gates |
| `first-principles-allows-type2-fast-path` | `he-plan/references/evals.yaml` | reversible low-risk work avoids unnecessary lifecycle expansion |
| `first-principles-compresses-linear-noise` | `he-linear-plan/references/evals.yaml` | cognition-only findings remain in `.harness` or `Do Not Create` instead of becoming Linear issues |
| `first-principles-eval-closure-challenge` | `he-eval-report/references/evals.yaml` | eval closure asks accept/challenge/rework or blocks when proof is missing |
| `first-principles-review-flags-false-sophistication` | `he-code-review/references/evals.yaml` | review flags new abstraction/process that lacks verified-failure evidence |
| `first-principles-records-assumptions-headless` | `lifecycle-tracer-evals.yaml` | headless mode records assumptions instead of interactive questioning |

Eval authoring constraints:

- each stage-local case must include a behavioral assertion in `acceptance`, not only a keyword that proves the contract was mentioned
- negative cases should assert the skill rejects, defers, asks, records assumptions, or classifies as `Do Not Create`
- do not add evals that require network, GitHub, Linear mutation, or repository writes
- preserve each file's existing `deterministic_checks: *safe` convention where present
- if an eval needs a prompt mentioning first principles, ensure the expected output still proves Harness Engineering behavior rather than merely repeating the phrase

Acceptance covered:

- `SA-006`
- `SA-007`
- `SA-008`
- `SA-009`
- `SA-010`
- `SA-011`
- `SA-012`
- `SA-013`
- `SA-014`

Validation:

- `python3 Plugins/harness-engineering/scripts/check_first_principles_contract_wiring.py`
- existing eval parser or skill audit command, if available through `./bin/ask`
- manual inspection that evals assert negative behavior, not just happy-path presence

Rollback:

- remove the new eval cases from the touched eval files

### PU-005: Add Contract Wiring Validator

Objective: make the prompt/routing change testable.

Add:

- `Plugins/harness-engineering/scripts/check_first_principles_contract_wiring.py`

Required checks:

- `Plugins/harness-engineering/references/first-principles-contract.md` exists
- all required field names are present in the contract
- deferred context index references the contract in both the Runtime Reference Map and Conditional Loading Map
- each lifecycle skill listed in PU-003 references the contract
- every eval case listed in PU-004 exists in the expected file
- no `Plugins/harness-engineering/skills/he-first-principles` directory exists

Suggested validator structure:

```text
PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SNIPPETS = {...}
REQUIRED_EVAL_IDS = {...}
FORBIDDEN_PATHS = [...]
validate(root) -> list[str]
main() -> --root, --json
```

Failure text should identify the exact relative file and missing snippet or case ID. This keeps failures actionable when future skill edits drift from the contract.

Acceptance covered:

- `SA-003`
- `SA-004`
- `SA-006`
- `SA-007`
- `SA-013`
- `SA-014`

Validation:

- `python3 Plugins/harness-engineering/scripts/check_first_principles_contract_wiring.py`
- `python3 -m py_compile Plugins/harness-engineering/scripts/check_first_principles_contract_wiring.py`

Rollback:

- remove the validator and remove it from any documentation or validation command lists that were updated

### PU-006: Sync Projections And Validate Harness State

Objective: ensure canonical source, workspace projections, and skill discovery do not drift.

Commands to run after implementation:

```bash
./bin/ask skills sync --scope workspace --projection rooted --json --robot
./bin/ask skills handles --check --json --robot
python3 Plugins/harness-engineering/scripts/check_first_principles_contract_wiring.py
python3 Plugins/harness-engineering/scripts/check_gate_selection_wiring.py
python3 Plugins/harness-engineering/scripts/check_domain_contract_wiring.py
python3 Plugins/harness-engineering/scripts/check_xp_contract_wiring.py
python3 Infrastructure/scripts/lifecycle-and-sync/projection_integrity.py verify --scope all
```

Run focused skill audits for every changed lifecycle skill if the command is available:

```bash
./bin/ask skills audit Plugins/harness-engineering/skills/he-brainstorm --level strict --json --robot
./bin/ask skills audit Plugins/harness-engineering/skills/he-strategy --level strict --json --robot
./bin/ask skills audit Plugins/harness-engineering/skills/he-spec --level strict --json --robot
./bin/ask skills audit Plugins/harness-engineering/skills/he-plan --level strict --json --robot
./bin/ask skills audit Plugins/harness-engineering/skills/he-linear-plan --level strict --json --robot
./bin/ask skills audit Plugins/harness-engineering/skills/he-eval-report --level strict --json --robot
./bin/ask skills audit Plugins/harness-engineering/skills/he-code-review --level strict --json --robot
```

Fallback validation if `skills audit` does not accept these paths:

```bash
./bin/ask skills explain he-brainstorm --json --robot
./bin/ask skills explain he-strategy --json --robot
./bin/ask skills explain he-spec --json --robot
./bin/ask skills explain he-plan --json --robot
./bin/ask skills explain he-linear-plan --json --robot
./bin/ask skills explain he-eval-report --json --robot
./bin/ask skills explain he-code-review --json --robot
```

Record unsupported command behavior as blocked evidence rather than silently replacing a failed gate.

Acceptance covered:

- `SA-006`
- `SA-007`
- `SA-013`
- `SA-014`

Rollback:

- if sync produces unrelated projection churn, inspect diffs and keep only changes caused by the implementation
- if projection integrity fails, do not claim implementation completion

### PU-007: Generate Eval Report Before Linear Closure

Objective: after implementation and validation, produce proof before recommending any Linear closure.

Expected future artifact:

- `.harness/evals/2026-05-09-agent-skills-first-principles-contract-eval.md`

Required content:

- exact files changed
- validation commands and results
- first-principles eval coverage matrix
- drift validation
- Linear completion recommendation
- proof that no standalone `he-first-principles` skill was created

Acceptance covered:

- `SA-011`
- `SA-012`
- `SA-013`
- `SA-014`

Rollback:

- if eval report finds missing proof or drift, classify implementation as `Needs rework` and do not recommend Linear closure

## Acceptance Traceability Matrix

| Acceptance ID | Requirement Summary | Plan Unit(s) | Proof Method |
|---|---|---|---|
| `SA-001` | Add a reusable first-principles contract. | `PU-001` | Contract file exists and includes required Harness Engineering doctrine. |
| `SA-002` | Include required structured check fields. | `PU-001`, `PU-005` | Wiring validator checks required field names. |
| `SA-003` | Make contract discoverable through deferred context. | `PU-002`, `PU-003`, `PU-005` | Deferred index and lifecycle skills reference the contract. |
| `SA-004` | Prevent copied-process expansion. | `PU-001`, `PU-003`, `PU-004` | Negative evals reject or defer template copying without verified failure. |
| `SA-005` | Preserve smallest effective mechanism rule. | `PU-001`, `PU-003`, `PU-004` | Spec and plan evals require smallest mechanism evidence. |
| `SA-006` | Add negative eval coverage. | `PU-004`, `PU-005` | Eval cases exist in expected files. |
| `SA-007` | Add headless/autonomous assumption behavior. | `PU-001`, `PU-004` | Lifecycle tracer eval verifies assumptions are recorded instead of asking. |
| `SA-008` | Route Type 1 decisions to deeper proof. | `PU-001`, `PU-003`, `PU-004` | `he-plan` eval routes irreversible work through proof gates. |
| `SA-009` | Allow Type 2 fast path for reversible work. | `PU-001`, `PU-003`, `PU-004` | `he-plan` eval avoids unnecessary lifecycle expansion. |
| `SA-010` | Reduce Linear issue noise. | `PU-003`, `PU-004` | `he-linear-plan` eval uses `.harness` or `Do Not Create` where appropriate. |
| `SA-011` | Require closure proof against original failure. | `PU-003`, `PU-004`, `PU-007` | `he-eval-report` eval and future eval report block false closure. |
| `SA-012` | Preserve Harness Engineering philosophy. | `PU-001`, `PU-003`, `PU-007` | Contract and eval report show process prevents verified failures, not process for its own sake. |
| `SA-013` | Sync canonical and projected state. | `PU-006` | Sync and projection verification pass or are reported as blocked. |
| `SA-014` | Do not create standalone skill. | `PU-001`, `PU-005`, `PU-007` | Wiring validator checks absence of `he-first-principles` skill directory. |

## Dependency Map

| Unit | Depends On | Can Run In Parallel | Notes |
|---|---|---|---|
| `PU-001` | approved spec and review | no | Contract must exist before wiring. |
| `PU-002` | `PU-001` | yes, with `PU-003` after contract path is stable | Deferred route must point to final contract path. |
| `PU-003` | `PU-001` | partially | Skills can be updated independently once contract path is known. |
| `PU-004` | `PU-001`, `PU-003` | partially | Stage evals can be added independently but should match skill behavior. |
| `PU-005` | `PU-001` through `PU-004` shape | no | Validator should encode final expected file map. |
| `PU-006` | `PU-001` through `PU-005` | no | Sync and projection verification come after source edits. |
| `PU-007` | `PU-006` | no | Eval report must reflect actual validation results. |

## Validation Gates

| Gate | Command Or Method | Expected Result | Blocks Completion |
|---|---|---|---|
| Plan artifact identity | `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md` | pass | yes |
| Plan frontmatter safety | `python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md` | pass | yes |
| Plan traceability lint | `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md` | pass | yes |
| Contract wiring | `python3 Plugins/harness-engineering/scripts/check_first_principles_contract_wiring.py` | pass | yes |
| Validator syntax | `python3 -m py_compile Plugins/harness-engineering/scripts/check_first_principles_contract_wiring.py` | pass | yes |
| Existing gate-selection wiring | `python3 Plugins/harness-engineering/scripts/check_gate_selection_wiring.py` | pass | yes |
| Existing domain wiring | `python3 Plugins/harness-engineering/scripts/check_domain_contract_wiring.py` | pass | yes |
| Existing XP wiring | `python3 Plugins/harness-engineering/scripts/check_xp_contract_wiring.py` | pass | yes |
| Projection sync | `./bin/ask skills sync --scope workspace --projection rooted --json --robot` | pass or explicit blocked reason | yes |
| Handle check | `./bin/ask skills handles --check --json --robot` | pass | yes |
| Projection integrity | `python3 Infrastructure/scripts/lifecycle-and-sync/projection_integrity.py verify --scope all` | pass | yes |
| Focused skill audits | `./bin/ask skills audit <changed-skill-path> --level strict --json --robot` | pass or explicit unsupported command evidence | yes for changed skills |
| Explain fallback | `./bin/ask skills explain <handle> --json --robot` | pass if audit is unsupported | yes when audit is unsupported |
| Diff hygiene | `git diff --check` | pass | yes |
| Eval proof | future `.harness/evals/2026-05-09-agent-skills-first-principles-contract-eval.md` | complete or complete with justified exceptions | yes for Linear closure |

## Concrete Test Scenarios

| Scenario | Input | Action | Expected Outcome |
|---|---|---|---|
| Template copying | User asks to add a process from another plugin because it sounds useful. | Run `he-strategy` or `he-spec`. | Skill asks what verified HE failure it prevents or rejects/defer if none exists. |
| Brainstorm survivor ambiguity | Brainstorm produces multiple plausible ideas, some copied from external systems. | Run `he-brainstorm`. | Survivor selection blocks or asks instead of choosing analogy-driven ideas silently. |
| Type 1 decision | Proposed change affects lifecycle routing or Linear closure. | Run `he-plan`. | Plan routes through proof gates and eval before closure. |
| Type 2 decision | Proposed change is reversible, local, and low risk. | Run `he-plan`. | Plan allows a smaller fast path instead of invoking full lifecycle ceremony. |
| Linear noise | Architecture review yields cognition-only notes. | Run `he-linear-plan`. | Notes remain in `.harness` or `Do Not Create`; no issue explosion. |
| Missing closure proof | Implementation exists but validation or drift proof is missing. | Run `he-eval-report`. | Report recommends `Blocked`, `Needs rework`, or `Unsafe to close`, not `Complete`. |
| Headless mode | Interactive question would normally be useful but autonomous mode is active. | Run lifecycle tracer eval. | Assumptions are recorded with confidence and repair path instead of using `request_user_input`. |
| False sophistication in review | Implementation adds a new abstraction without verified failure evidence. | Run `he-code-review`. | Review flags the abstraction/process as drift or requires proof. |

## Loophole Closure Checks

| Possible Loophole | Required Fix In Plan | Verification |
|---|---|---|
| Contract is added to the deferred index but only discoverable in one map. | Add it to both Runtime Reference Map and Conditional Loading Map. | Wiring validator checks both contexts. |
| Skill edits begin without reading repo vocabulary guidance. | Read `UBIQUITOUS_LANGUAGE.md` before implementation. | Implementation closeout records the read as source evidence. |
| New eval cases parse but only prove keyword presence. | Require behavioral acceptances such as reject, defer, ask, record assumption, or `Do Not Create`. | Manual review plus future eval report. |
| New first-principles hook weakens prior domain, XP, or gate-selection contracts. | Run existing gate, domain, and XP wiring validators after implementation. | All three validators pass or block completion. |
| `skills audit` assumptions drift. | Use verified command shape from `./bin/ask skills audit --help`; fallback to `./bin/ask skills explain` only if audit is unsupported in the implementation context. | Validation log records exact command outcomes. |
| Projection output includes unrelated dirty state. | Sync only after canonical edits and inspect generated `.skillsets/**` diff against the touched HE source files. | Eval report classifies unrelated projection churn as blocked or excluded. |

## Readiness Checklist Before Implementation

- [ ] `UBIQUITOUS_LANGUAGE.md` has been read for skill/source vocabulary before source edits begin.
- [ ] The implementation edits only canonical Harness Engineering source files before sync.
- [ ] Each lifecycle skill hook is one short operational rule plus one reference entry.
- [ ] Eval cases preserve local file schema and are behavioral, not keyword-only.
- [ ] The validator encodes expected wiring without requiring plugin runtime state.
- [ ] No `he-first-principles` skill directory or public handle is added.
- [ ] Projection changes are generated by sync and reviewed against canonical source edits.
- [ ] A future eval report is planned before Linear completion is recommended.

## Proposed Linear Mapping

No Linear object exists yet for this work.

If the user later asks to create Linear work, use the already proposed destination from `.harness/linear/2026-05-09-agent-skills-first-principles-contract-linear-plan.md` and create a small execution slice only.

Recommended shape:

| Object | Proposed Value |
|---|---|
| Project | `agent-skills` |
| Milestone | `HE First-Principles Gate` |
| Parent issue | `[agent-skills] Add first-principles gate to HE lifecycle` |
| Priority | High |
| Execution route | Agent-assisted with human review required for lifecycle routing semantics |
| Labels | `Architecture`, `Agent-Native`, `Eval`, `Governance`, `Refactor` if these exist |

Do not recommend Linear completion until the future eval report exists and confirms closure safety.

## Rollback Strategy

Rollback order:

1. Remove new eval cases from touched eval files.
2. Remove lifecycle skill hooks.
3. Remove deferred context index row.
4. Remove `first-principles-contract.md`.
5. Remove `check_first_principles_contract_wiring.py`.
6. Re-run sync only if projections were changed.

Rollback triggers:

- contract wording materially increases hot-path context load
- lifecycle skills duplicate long contract prose
- evals only check presence and do not prove negative behavior
- sync creates unexplained projection churn
- validator requires files or handles that do not exist
- implementation creates a standalone `he-first-principles` skill

## Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Hot-path bloat | Skills become harder to load and use. | Keep detailed logic in the reference contract and use short skill hooks. |
| Process theater | Contract becomes another ritual instead of preventing failures. | Negative evals must reject copied additions without verified failure evidence. |
| Eval ambiguity | Cases pass by checking keywords only. | Include expected behavioral assertions and use a wiring validator for static coverage only. |
| Projection drift | Runtime skillsets diverge from canonical sources. | Run workspace sync and projection integrity verification after edits. |
| Linear noise | Work becomes a backlog expansion exercise. | Keep Linear objects proposed only, and classify cognition-only items as `Do Not Create`. |
| Unrelated worktree changes | Implementation accidentally includes prior unrelated edits. | Review `git diff --stat` and stage only files changed for this slice. |

## Execution Unknowns

| Unknown | Current Decision | Repair Path |
|---|---|---|
| Exact eval schema details per stage file | Preserve existing local eval file shape and add cases in the same style. | Inspect each `references/evals.yaml` before editing. |
| Whether `./bin/ask skills audit` accepts skill paths for all changed skills | Plan assumes available based on repo command contract. | If unsupported, record blocked command and use `./bin/ask skills explain <handle> --json --robot` as the narrow fallback already listed in the validation gates. |
| Whether lifecycle tracer eval file supports headless assumption case directly | Use it if shape supports cross-stage cases. | If not, place the case in the closest lifecycle/root eval file and document the reason in the eval report. |
| Whether Linear issue should be created | Not created in this plan. | Ask or wait for explicit user instruction before creating Linear objects. |

## Post-Plan Handoff

Recommended next phase: implementation with `he-phase-heartbeat` or the repository's normal execution workflow.

Do not proceed automatically from this plan into source edits unless the user explicitly says to proceed. The next phase should execute `PU-001` through `PU-006`, then produce the eval report in `PU-007` before recommending Linear closure.

If multiple valid next stages appear later, ask once before choosing. If running headless, record the selected assumption and why.
