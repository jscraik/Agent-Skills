---
schema_version: 1
artifact_type: linear-plan
repo: agent-skills
canonical_slug: agent-skills-first-principles-factory-gate
created: 2026-05-09
linear_project: agent-skills
linear_parent_issue: unknown
status: proposed
payload_status: ready-to-create-plan-only
---

# First-Principles Factory Gate Linear Plan

## Executive Linear Routing Summary

This plan routes one small execution program for adding a first-principles
factory gate to `skill-factory` and `plugin-factory`.

The work is repo-specific and belongs in the `agent-skills` project. It should
not create a new initiative, project, or one-issue-per-observation backlog.

The execution objective is to make the factories choose the smallest
proof-backed artifact before building: skill, plugin, hook, MCP tool, app, eval,
existing improvement, docs-only, or do-not-build.

No Linear objects have been created. The eval closure artifact requested by the
user does not exist yet and is treated as a required future proof target:

`.harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md`

## Target Linear Destination

Target project: `agent-skills`

Parent initiative: `Dev Portfolio`

Milestone: `First-Principles Factory Gate`

Destination classification: repo-specific work.

Reason: the selected work changes local factory plugin source, hooks,
validation, and eval evidence inside this repository. It is not cross-repo
workflow hygiene and should not route to `Portfolio Ops`.

Mutation status: none. This plan contains ready-to-create payloads only.

## Existing Project Match

The matching repo project is `agent-skills`.

Existing nearby artifact:

- `.harness/linear/2026-05-09-agent-skills-first-principles-contract-linear-plan.md`

Relationship to existing plan:

- Existing plan: adds the first-principles contract to Harness Engineering.
- This plan: applies the same restraint logic specifically to the factory
  plugins so they choose the right artifact before creating or hardening skills
  and plugins.

Do not merge these plans automatically. They share philosophy, but they affect
different source surfaces and have different eval closure proof.

## Proposed Milestones

| Object type | Name/title | Target project | Parent initiative | Priority | Labels | Execution route | Source artifacts | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Milestone | First-Principles Factory Gate | agent-skills | Dev Portfolio | 2 | Architecture, Agent-Native, Eval, Factory, Governance | Agent-assisted, human-review required | Strategy and refactor artifacts listed below | Adds the artifact-selection gate that prevents factory output from becoming valid but low-value package volume. |

Milestone scope:

- Add compact gate checkpoint to factory routers and existing factory
  SessionStart hooks.
- Add a reference schema and procedure wiring.
- Add validator/test enforcement for new factory output.
- Add eval proof that the gate changes factory decisions.

Out of scope:

- Creating Linear objects directly.
- Creating a standalone first-principles skill.
- Adding MCP tools or apps before the gate schema proves useful.
- Rewriting all factory skills.
- One issue per observation.

## Proposed Parent Issues

### `[agent-skills] Add first-principles gate to Skill and Plugin Factory`

```text
## Objective
Add a first-principles factory gate so skill-factory and plugin-factory choose
the smallest proof-backed artifact before creating, hardening, refactoring, or
packaging skills/plugins.

## Source Artifacts
- .harness/strategy/2026-05-09-agent-skills-first-principles-factory-strategy.md
- .harness/refactors/2026-05-09-agent-skills-first-principles-factory-gate.md
- .harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md
- Plugins/skill-factory/skills/skill-factory-router/SKILL.md
- Plugins/plugin-factory/skills/plugin-factory-router/SKILL.md
- Plugins/skill-factory/hooks/session_start_routing.py
- Plugins/plugin-factory/hooks/session_start_contract.py

## Why This Matters
Factory value should come from lower agent decision load and better validated
behavior, not from creating more package files. This issue adds the gate that
forces artifact selection before build work.

## Scope
- Add compact first-principles checkpoint text to both factory routers.
- Extend both factory SessionStart hooks with the compact checkpoint.
- Add a reference schema for gate output.
- Add validator/test coverage for missing or malformed gate evidence.
- Add eval proof where the gate chooses build and non-build outcomes.

## Out of Scope
- MCP tools or apps before schema proof.
- New standalone first-principles skill.
- Broad factory rewrite.
- Linear mutation.
- One issue per observation.

## Execution Notes
Use the refactor program as the selected migration source. Implement Phase 1
first. Do not consume the entire strategy stack as implementation scope.

## Validation Gates
- `python3 -m py_compile` for changed hook/test scripts
- focused pytest for factory bundled hook/gate tests
- `git diff --check`
- `bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh --changed-files ...`
- write closure proof to .harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md

## Rollback Conditions
- Gate language increases context load or ambiguity.
- Validator enforcement creates broad false positives.
- Evals only prove wording is present, not that artifact selection changed.
- Hook context becomes noisy while plugin_hooks remains gated.

## Linear Routing
Project: agent-skills
Milestone: First-Principles Factory Gate
Labels: Architecture, Agent-Native, Eval, Factory, Governance
Priority: 2
Blocks: none
Blocked by: human approval of this Linear plan
```

## Proposed Sub-Issues

| Title | Scope | Execution route | Priority | Blocks closure |
| --- | --- | --- | --- | --- |
| `[agent-skills] Add factory first-principles checkpoint to routers and hooks` | Implement Phase 1 only: compact router and hook checkpoint, plus focused tests. | Agent-safe | 2 | yes |
| `[agent-skills] Add factory gate schema and procedure wiring` | Add reference schema and wire create/harden/refactor procedures without bloating entrypoints. | Agent-assisted | 2 | yes |
| `[agent-skills] Enforce factory gate evidence in validation` | Add deterministic warning/failure checks for new factory output. | Agent-assisted, human-review required | 2 | yes |
| `[agent-skills] Prove factory gate changes artifact decisions` | Add eval cases and closure proof artifact. | Agent-assisted, human-review required | 2 | yes |

Do not split further unless validation reveals independent failures.

## Now / Next / Later / Do Not Create

Now:

- Phase 1: add compact factory gate checkpoint to routers and hooks.
- Add focused tests proving hook output remains valid and includes decision
  terms.

Next:

- Phase 2: add gate schema and procedure references.
- Phase 3: add validation checks for new factory output.
- Phase 4: add eval cases and closure proof.

Later:

- MCP wrapper for gate decisions, only after schema and eval proof show useful
  repeated structure.
- App/UI surface for visual factory review, only if human inspection becomes a
  repeated bottleneck.

Do Not Create:

- New standalone first-principles skill for this slice.
- Separate Linear issue for each affected skill file.
- New project or initiative.
- Hook enforcement that bypasses validators/evals.
- MCP/app implementation before the gate proves it changes decisions.

## Dependency Map

| Item | Depends on | Dependency type | Can run in parallel | Human review |
| --- | --- | --- | --- | --- |
| Phase 1 router/hook checkpoint | approved Linear plan | blocking | no | no |
| Phase 2 schema/procedure wiring | Phase 1 | migration | partly | no |
| Phase 3 validator enforcement | Phase 2 | validation | no | yes |
| Phase 4 eval proof | Phase 2 and selected validation behavior | eval closure | no | yes |
| Closure recommendation | `.harness/evals/**` proof artifact | completion-gating | no | yes |

## Eval Gate Map

| Gate | Expected | Blocks closure |
| --- | --- | --- |
| Build-skill positive case | Gate chooses `BUILD_SKILL` only when a reusable cognitive move and validation proof exist. | yes |
| Plugin/runtime positive case | Gate chooses `BUILD_PLUGIN` or `ADD_HOOK` only when runtime behavior should travel with the plugin. | yes |
| Non-build negative case | Gate chooses `DO_NOT_BUILD`, `DOCS_ONLY`, or `IMPROVE_EXISTING` for copied-template requests. | yes |
| Hook drift case | Hooks are rejected when added only because hooks are available. | yes |
| Validator behavior | Missing/malformed gate evidence is caught for new factory output. | yes |
| Closure artifact | `.harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md` exists and records pass/fail/blocked proof. | yes |

## Human vs Agent Execution Map

| Work | Route |
| --- | --- |
| Phase 1 router/hook checkpoint | Agent-safe |
| Focused hook/test updates | Agent-safe |
| Schema/procedure wiring | Agent-assisted |
| Validator strictness decision | Human-review required |
| Eval interpretation | Human-review required |
| Linear object creation | Human-review required |
| Readiness/closure recommendation | Human-review required after eval proof |

## Story / Value Basis

Story:

As a Codex-first builder improving local agent capabilities, Jamie needs the
factory plugins to reject copied templates and choose the smallest useful
artifact so new skills/plugins improve behavior instead of growing catalog
volume.

Expected feedback signal:

- Factory output records a gate decision before build work.
- At least one test proves the gate appears in runtime hook context.
- At least one eval proves the gate changes artifact selection.

Risk reduction:

- Reduces low-value skill/plugin creation.
- Reduces always-loaded prompt bloat.
- Reduces plugin hook misuse.
- Improves validation and closure proof.
- Keeps MCP/app automation deferred until justified.

## Recommended Labels

Use existing labels if present:

- Architecture
- Agent-Native
- Eval
- Factory
- Governance

Do not create new labels from this skill. If `Factory` does not exist, omit it
or ask for approval before creating it.

## Priority Mapping

Parent issue priority: `2` High.

Reason: this is not an outage, but it protects the repo's stated moat and
blocks confident readiness for first-principles factory behavior until eval
proof exists.

Sub-issue priorities:

- Phase 1 checkpoint: `2`
- Phase 2 schema/procedure wiring: `2`
- Phase 3 validation enforcement: `2`
- Phase 4 eval proof: `2`

## Project Reactivation Recommendation

Do not broaden project activation.

If `agent-skills` is active, add one milestone and one parent issue. If it is
inactive, reactivate only for this milestone after human approval.

## Portfolio Ops Items

None.

This is repo-specific factory plugin work.

## Dev Portfolio Impact

This strengthens the Dev Portfolio by making `agent-skills` better at deciding
what should exist before producing agent-facing artifacts.

Expected portfolio impact:

- Better agent capability quality.
- Less prompt/catalog sprawl.
- More reliable proof before readiness claims.
- Cleaner future handoff from strategy/refactor into implementation.

## Evidence & Traceability Matrix

| Claim | Evidence | Classification | Confidence | Linear impact |
| --- | --- | --- | ---: | --- |
| The work belongs in `agent-skills` | Strategy/refactor artifacts target `skill-factory`, `plugin-factory`, local hooks, validators, and evals | Fact | High | Route to `agent-skills` |
| Active set should stay small | Refactor program names Phase 1 as the first selected slice and defers MCP/app work | Fact | High | One milestone, one parent, four sub-issues |
| Eval proof is required but missing | `stat` on the requested eval path returned missing file | Fact | High | Closure blocked until eval artifact exists |
| Hooks should not enforce readiness | Strategy says hooks inject context while validators/evals enforce readiness | Fact | High | Eval and validation sub-issues required |
| MCP/app work is premature | Refactor program says defer until schema proves useful | Interpretation | High | Classify as Later |
| Linear should not be mutated here | `he-linear-plan` execution boundary forbids creating issues without post-plan approval | Fact | High | Ready-to-create payloads only |
