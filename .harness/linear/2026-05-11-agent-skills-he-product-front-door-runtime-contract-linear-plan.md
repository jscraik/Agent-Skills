# HE Product Front Door And Runtime Contract Linear Plan

schema_version: 1
selected_stage: he-linear-plan
subagent_policy: not_used
roles_used: []
roles_recommended: []
roles_missing: []
linear_mutation_status: created
required_confirmation: User explicitly requested Linear issue creation after he-refactor and he-linear-plan; apply only the small confirmed issue set below.
live_linear_blocker: null
live_linear_checked_at: 2026-05-18
live_linear_current_project: HE front door and runtime contract
live_linear_current_status: Todo
live_linear_current_assignee: null
created_parent_issue: JSC-305
created_child_issues:
  - JSC-306
  - JSC-307
  - JSC-308
  - JSC-309
  - JSC-310

## Executive Linear Routing Summary

Created one parent issue and five child issues for applying the useful
compound-engineering lessons to HE without broadening HE into a generic
productivity suite.

Live reconciliation, 2026-05-18: JSC-305 and children JSC-306 through JSC-310
exist in Linear under the project `HE front door and runtime contract`; all are
unstarted. The local plan remains an adjacent HE runtime/front-door lane, not
the primary Skill SDK RF-1 execution handle.

## Target Linear Destination

- Team: `Jscraik`
- Project: `HE front door and runtime contract`
- Canonical project ID: not recorded in this local artifact
- Status: `Todo`
- Assignee: empty in live Linear as of 2026-05-18

## Existing Project Match

The live issues are currently routed to `HE front door and runtime contract`.
Do not reroute them to a generic `agent-skills` project from this local plan
without first confirming the intended Linear destination.

## Proposed Milestones

No new Linear milestone. This is a small productization slice under the active
`agent-skills` project.

## Proposed Parent Issues

### Ready-to-create payload: parent

```yaml
title: "Productize HE front door and runtime contract from compound-engineering lessons"
team: "Jscraik"
project: "agent-skills"
state: "Todo"
assignee: "me"
priority: 2
labels:
  - Agent-Native
  - Developer Experience
  - Governance
  - Routing
```

Created as: `JSC-305`

## Proposed Sub-Issues

### 1. Add HE setup/status front door

```yaml
title: "Add HE setup/status front door for readiness and projection drift"
team: "Jscraik"
project: "agent-skills"
state: "Todo"
assignee: "me"
priority: 2
labels:
  - Agent-Native
  - Reliability
  - Developer Experience
```

Created as: `JSC-306`

### 2. Productize HE README and plugin default prompts

```yaml
title: "Productize HE README and plugin default prompts around plain user intents"
team: "Jscraik"
project: "agent-skills"
state: "Todo"
assignee: "me"
priority: 2
labels:
  - Developer Experience
  - Agent-Native
  - Docs
```

Created as: `JSC-307`

### 3. Add runtime-authoring and process-exhaust doctrine

```yaml
title: "Add HE runtime-authoring boundary and process-exhaust artifact policy"
team: "Jscraik"
project: "agent-skills"
state: "Todo"
assignee: "me"
priority: 3
labels:
  - Governance
  - Context
  - Docs
```

Created as: `JSC-308`

### 4. Enforce HE route, naming, and authority consistency

```yaml
title: "Enforce HE route, naming, authority, and product-doc consistency"
team: "Jscraik"
project: "agent-skills"
state: "Todo"
assignee: "me"
priority: 2
labels:
  - Routing
  - Reliability
  - Governance
```

Created as: `JSC-309`

### 5. Add HE observed usage pulse without unsupported quality claims

```yaml
title: "Add HE observed usage pulse with truth-set-safe metric boundaries"
team: "Jscraik"
project: "agent-skills"
state: "Todo"
assignee: "me"
priority: 3
labels:
  - Eval
  - Governance
  - Developer Experience
```

Created as: `JSC-310`

## Now / Next / Later / Do Not Create

| Bucket | Work | Rationale |
| --- | --- | --- |
| Now | Parent issue plus five children | Smallest useful Linear slice; captures productization without one issue per observation. |
| Next | Generated per-stage docs | Useful after canonical intent/authority validation is stable. |
| Later | Cross-platform tool-equivalence support | Valuable only if HE targets non-Codex runtimes. |
| Do Not Create | Separate git, Slack, imagegen, or worktree utility issues copied from compound-engineering | Would broaden HE beyond its harness thesis. |

## Dependency Map

1. README/default prompts can start immediately.
2. `he-doctor` can start in parallel but must respect existing `./bin/ask`
   command ownership.
3. Runtime/artifact doctrine should land before generated per-stage docs.
4. Consistency validation depends on canonical route/authority data.
5. Observed usage pulse depends on telemetry/truth-set boundaries.

## Eval Gate Map

- Packaging hygiene.
- Routing map validation.
- Deferred context index check.
- Plugin validation.
- Focused script tests for new doctor/checker behavior.
- Strict audits for materially changed HE skills.
- Plugin Eval only for materially changed entrypoints.

## Human vs Agent Execution Map

- Agent-safe: README/default prompt edits, doctrine draft, checker draft.
- Assisted: setup/status command and route consistency enforcement.
- Human review required: release-blocking gate changes and any metric language
  that could imply route quality.

## Story / Value Basis

As a human or agent using HE, I want one obvious first action and one reliable
runtime/source boundary so that I can route, recover, and close work without
learning HE vocabulary first or trusting stale projections.

## Recommended Labels

Use existing labels only: `Agent-Native`, `Developer Experience`,
`Governance`, `Routing`, `Reliability`, `Docs`, `Context`, `Eval`.

## Priority Mapping

- Parent: High (`2`)
- Front door/status: High (`2`)
- README/default prompts: High (`2`)
- Runtime/artifact doctrine: Medium (`3`)
- Consistency validation: High (`2`)
- Observed usage pulse: Medium (`3`)

## Project Reactivation Recommendation

Not applicable. The canonical `agent-skills` project is already active.

## Portfolio Ops Items

None. Keep this repo-specific unless later cross-plugin product doctrine is
needed.

## Dev Portfolio Impact

Improves the HE plugin as an agent-native operating layer and reduces risk that
local-only HE artifacts are mistaken for live tracker or closure state.

## Evidence & Traceability Matrix

| Claim | Evidence |
| --- | --- |
| HE needs a first-contact surface | Local HE README and EveryInc README comparison |
| Runtime behavior must live in shipped plugin surfaces | EveryInc `AGENTS.md` authoring/runtime warning and local projection model |
| Default prompts improve discoverability | EveryInc `.codex-plugin/plugin.json` |
| HE should not copy compound-engineering breadth | Local HE closure-proof thesis and active skill set |
| Canonical Linear destination is `agent-skills` | Linear project lookup: `791c2f12-5ffb-4644-8421-f4216ac6d805` |
