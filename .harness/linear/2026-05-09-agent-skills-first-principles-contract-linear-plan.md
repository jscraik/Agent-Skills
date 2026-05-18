---
schema_version: 1
artifact_type: linear-plan
repo: agent-skills
canonical_slug: agent-skills-first-principles-contract
created: 2026-05-09
linear_project: agent-skills
linear_parent_issue: unknown
status: proposed
---

# First-Principles Contract Linear Plan

## Executive Linear Routing Summary

This plan routes one small execution slice for adding first-principles thinking
to the Harness Engineering plugin without turning it into another lifecycle
stage. The work is repo-specific and belongs in the existing `agent-skills`
Linear project. It should not create a new initiative, project, or large issue
set.

The execution objective is to add a compact HE reference contract, wire it into
the lifecycle only where it prevents real process bloat, and add negative evals
that prove HE rejects copied sophistication when no verified failure exists.

Payload status: ready-to-create plan only. No Linear objects have been created.

## Target Linear Destination

Target project: `agent-skills`

Parent initiative: `Dev Portfolio`

Milestone: `HE First-Principles Gate`

Destination classification: repo-specific work.

Reason: the slice changes Harness Engineering plugin source, HE lifecycle
references, and HE skill eval behavior in this repository. It is not a
cross-repo workflow hygiene change, so it should not route to `Portfolio Ops`.

## Existing Project Match

The matching repo project is `agent-skills`.

Project reactivation recommendation: keep the project active only for this
small slice if it is already active. Do not reactivate broader HE plugin
hardening unless a separate approved slice exists.

## Proposed Milestones

| Object type | Name/title | Target project | Parent initiative | Priority | Labels | Execution route | Source artifacts | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Milestone | HE First-Principles Gate | agent-skills | Dev Portfolio | 3 | Architecture, Agent-Native, Eval, Governance | Agent-assisted, human-review required | HE strategy discussion, `Plugins/harness-engineering/skills/he-strategy/SKILL.md`, `Plugins/harness-engineering/skills/he-linear-plan/references/linear-plan-output-contract.md` | Adds a restraint gate that prevents lifecycle/process expansion without verified HE failure evidence. |

Milestone scope:

- Add `Plugins/harness-engineering/references/first-principles-contract.md`.
- Add a conditional-loading row to
  `Plugins/harness-engineering/references/deferred-context-index.md`.
- Wire concise references into the smallest set of lifecycle skills.
- Add negative eval cases proving restraint.
- Sync projections and validate handles/audits.

Out of scope:

- Creating `he-first-principles` as a new skill.
- Creating Linear objects directly.
- Reworking the full HE lifecycle.
- Rewriting existing strategy/spec/plan/eval contracts beyond the smallest
  reference hooks.
- Adding broad philosophical prose to hot-path skill entrypoints.

Success criteria:

- HE can reject copied process when no verified failure exists.
- Reversible Type 2 changes keep a fast path.
- Type 1 architecture/governance changes route to proof.
- Linear issue explosion is explicitly resisted.
- Future agents can find the first-principles gate from the deferred context
  index.

## Proposed Parent Issues

### `[agent-skills] Add first-principles restraint gate to Harness Engineering`

```text
## Objective
Add a compact first-principles contract to Harness Engineering so lifecycle
skills challenge copied process, unproved governance, and artifact expansion
before creating new HE work.

## Source Artifacts
- Plugins/harness-engineering/skills/he-strategy/SKILL.md
- Plugins/harness-engineering/skills/he-linear-plan/SKILL.md
- Plugins/harness-engineering/skills/he-linear-plan/references/linear-plan-output-contract.md
- Plugins/harness-engineering/references/deferred-context-index.md
- .harness/linear/2026-05-09-agent-skills-first-principles-contract-linear-plan.md

## Why This Matters
Harness Engineering already has powerful lifecycle machinery. The risk is not
lack of process; the risk is copied sophistication. This issue adds a small
gate that asks what verified failure is being prevented and what the smallest
effective mechanism is before HE expands scope.

## Scope
- Create a first-principles HE reference contract.
- Add conditional-loading guidance.
- Wire concise references into he-strategy, he-spec, he-plan, he-linear-plan,
  he-eval-report, and he-code-review only where the gate changes routing,
  scope, or closure behavior.
- Add targeted negative eval cases.
- Sync projections.
- Validate handles, progressive disclosure, projection integrity, and targeted
  skill audits.

## Out of Scope
- New standalone `he-first-principles` skill.
- Broad plugin restructuring.
- Linear mutation.
- New governance layer.
- One issue per observation.

## Execution Notes
Treat first principles as the "should this exist?" filter. Gate selection then
decides how much rigor is needed. Eval proves the behavior. Keep active
entrypoints compact and move durable details to references.

## Validation Gates
- `./bin/ask skills sync --scope workspace --projection rooted --json --robot`
- `./bin/ask skills handles --check --json --robot`
- `./bin/ask skills audit Plugins/harness-engineering/skills/he-strategy --level strict --json --robot`
- `./bin/ask skills audit Plugins/harness-engineering/skills/he-linear-plan --level strict --json --robot`
- `bash Infrastructure/scripts/validation-and-linting/validate_he_progressive_disclosure.sh`
- `python3 Infrastructure/scripts/lifecycle-and-sync/projection_integrity.py verify --scope all`
- targeted lifecycle eval cases for first-principles restraint

## Rollback Conditions
- Skill entrypoints become materially longer without reducing context load.
- New evals cannot distinguish copied-process requests from valid HE
  improvements.
- Projection sync fails.
- The change creates new routing ambiguity or a new standalone stage.

## Linear Routing
Project: agent-skills
Milestone: HE First-Principles Gate
Labels: Architecture, Agent-Native, Eval, Governance
Priority: 3
Blocks: none
Blocked by: human approval of this Linear plan
```

## Proposed Sub-Issues

| Title | Scope | Execution route | Priority | Blocks closure |
| --- | --- | --- | --- | --- |
| `[agent-skills] Add HE first-principles contract reference` | Create the compact reference and deferred-context trigger. | Agent-safe | 3 | yes |
| `[agent-skills] Wire first-principles gate into HE lifecycle skills` | Add concise references to selected lifecycle skills without expanding hot-path prose. | Agent-assisted | 3 | yes |
| `[agent-skills] Add first-principles negative eval coverage` | Add eval cases for copied-template rejection, Type 1/Type 2 routing, Linear compression, and headless assumptions. | Agent-assisted | 3 | yes |
| `[agent-skills] Validate and sync first-principles HE projection` | Run sync, handle checks, audits, projection integrity, and targeted evals. | Agent-safe | 3 | yes |

Do not split further unless validation reveals independent failures.

## Now / Next / Later / Do Not Create

Now:

- Add the first-principles contract and minimal lifecycle wiring.
- Add negative eval coverage proving restraint.
- Sync and validate projections.

Next:

- If usage proves repeated demand, consider a dedicated first-principles
  decomposition mode inside `he-strategy`.

Later:

- Add a cross-repo first-principles operating pattern only if multiple repos
  show the same copied-process failure.

Do Not Create:

- New `he-first-principles` skill.
- New Linear initiative.
- One issue per lifecycle skill.
- Broad governance review requirement.
- Long philosophical prompt injected into every lifecycle stage.

## Dependency Map

| Item | Depends on | Dependency type | Can run in parallel | Human review |
| --- | --- | --- | --- | --- |
| Contract reference | approved plan | blocking | no | yes |
| Lifecycle wiring | contract reference | migration | partly | yes |
| Negative evals | contract reference and selected skill wiring | eval | partly | yes |
| Projection sync and validation | all source edits | release | no | no |

## Eval Gate Map

| Gate | Expected | Blocks closure |
| --- | --- | --- |
| Copied-template rejection | HE asks what verified failure is prevented and refuses/defer if absent. | yes |
| Type 1 routing | Architecture/governance changes require proof and do not fast-path. | yes |
| Type 2 fast path | Reversible low-risk changes avoid full strategy/refactor/eval ceremony. | yes |
| Linear compression | Observations collapse into minimal Linear objects or `Do Not Create`. | yes |
| Headless assumptions | Autonomous mode records assumptions instead of asking. | yes |
| Projection integrity | Runtime cache mirrors canonical HE source. | yes |

## Human vs Agent Execution Map

| Work | Route |
| --- | --- |
| Contract drafting | Agent-assisted |
| Lifecycle wiring | Agent-assisted |
| Eval case creation | Agent-assisted |
| Validation and projection sync | Agent-safe |
| Decision to create Linear objects | Human-review required |
| Decision to create a standalone skill | Human-review required, currently `Do Not Create` |

## Story / Value Basis

Story:

As a solo Codex-first builder, Jamie needs Harness Engineering to prevent
copied process and false sophistication so agent work stays traceable,
evidence-backed, and production-oriented without creating unnecessary
governance.

Expected feedback signal:

- HE can reject or defer a copied external workflow when no verified failure is
  named.
- HE can still fast-path small reversible work.
- HE can route high-risk process expansion to proof.

Risk reduction:

- Reduces issue explosion.
- Reduces context load.
- Reduces governance drift.
- Reduces future-agent over-routing.
- Protects HE's moat: intent preservation, deterministic routing, and honest
  closure proof.

## Recommended Labels

Use existing labels if present:

- Architecture
- Agent-Native
- Eval
- Governance

Do not create new labels for this slice unless these labels are unavailable
and the user approves label creation.

## Priority Mapping

Parent issue priority: `3` Normal.

Reason: the slice is strategically useful and reduces drift risk, but it is not
an active production outage, security incident, or merge blocker.

## Project Reactivation Recommendation

Do not broaden project activation. If `agent-skills` is already active, add
one milestone and one parent issue. If it is inactive, reactivate only for this
small milestone after human approval.

## Portfolio Ops Items

None.

This is repo-specific HE plugin work, not shared portfolio hygiene.

## Dev Portfolio Impact

This strengthens the `agent-skills` control plane by making HE less likely to
copy external process patterns without failure evidence. It supports Dev
Portfolio quality by reducing governance entropy and preserving a small active
execution set.

## Evidence & Traceability Matrix

| Conclusion | Evidence type | File paths | Confidence | Why it matters |
| --- | --- | --- | --- | --- |
| First principles should be a contract, not a standalone skill. | interpretation from HE strategy and lifecycle contracts | `Plugins/harness-engineering/skills/he-strategy/SKILL.md`, `Plugins/harness-engineering/references/deferred-context-index.md` | high | HE strategy already says strategy compresses choices and should avoid multiplying artifacts. |
| Linear should receive one small execution slice. | contract evidence | `Plugins/harness-engineering/skills/he-linear-plan/SKILL.md`, `Plugins/harness-engineering/skills/he-linear-plan/references/linear-plan-output-contract.md` | high | HE Linear Plan explicitly forbids issue explosion and Linear mutation from the planning skill. |
| The work is repo-specific. | repo ownership evidence | `Plugins/harness-engineering/**` | high | Proposed changes affect the local HE plugin source and projections in `agent-skills`. |
| Negative evals are required. | operational interpretation | prior HE eval strategy and current lifecycle eval pattern | medium | The behavior is only real if evals prove restraint under copied-template pressure. |
| Standalone `he-first-principles` is not justified yet. | anti-bloat interpretation | HE strategy anti-patterns and first-principles analysis | medium | A new skill would add routing surface before usage proves it deserves one. |

## Validation

Plan validation performed by inspection.

- Required sections from `linear-plan-output-contract.md`: pass
- Linear mutation avoided: pass
- Active set kept small: pass
- Low-value work classified as `Do Not Create`: pass

Blocked validation:

- No Linear connector mutation was run because this skill is planning-only.
- No implementation gates were run because no implementation source edits were
  made by this plan.
