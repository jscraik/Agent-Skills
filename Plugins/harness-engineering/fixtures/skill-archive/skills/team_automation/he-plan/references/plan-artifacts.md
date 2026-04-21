# Harness Engineering Plan Artifact Templates

Read when: you are writing or verifying the actual plan artifact selected by `he-plan`.

## Table of Contents
- [General plan template](#general-plan-template)
- [Template scaffold workflow](#template-scaffold-workflow)
- [Plan depth guidance](#plan-depth-guidance)
- [Deep-plan extensions](#deep-plan-extensions)
- [Dedicated UI plan template](#dedicated-ui-plan-template)
- [Execution Ledger](#execution-ledger)
- [Verification matrix](#verification-matrix)
- [Handoff options](#handoff-options)

## Template scaffold workflow

Canonical scaffold files for this skill:
- `plan.md.tmpl`
- rendered baseline: `Infrastructure/references/plan-template.md`

Render / refresh:

```bash
python3 Plugins/harness-engineering/skills/team_automation/he-plan/Infrastructure/scripts/render_plan_template.py
python3 Plugins/harness-engineering/skills/team_automation/he-plan/Infrastructure/scripts/check_plan_template_drift.py --update
```

Verify no drift:

```bash
python3 Plugins/harness-engineering/skills/team_automation/he-plan/Infrastructure/scripts/check_plan_template_drift.py
```

## General plan template
Preferred path:
- `Docs/plans/YYYY-MM-DD-<type>-<descriptive-name>-plan.md`

Suggested frontmatter:

```yaml
---
title: <plan title>
type: feat|fix|refactor
status: active
date: YYYY-MM-DD
origin: docs/brainstorms/YYYY-MM-DD-<topic>-brainstorm.md   # if applicable
requirements: docs/brainstorms/YYYY-MM-DD-<topic>-requirements.md  # if applicable
spec: Docs/specs/YYYY-MM-DD-<topic>-spec.md                 # if applicable
ui_spec: docs/ui-specs/YYYY-MM-DD-<name>-ui-spec.md         # if applicable
parent_plan: Docs/plans/YYYY-MM-DD-<name>-plan.md           # if applicable
deepened: YYYY-MM-DD                                        # if applicable
---
```

Required sections:
- Overview
- Problem Frame
- Requirements Trace
- Scope Boundaries
- Context & Research
- Key Technical Decisions
- Open Questions
- Implementation Units
- System-Wide Impact
- Risks & Dependencies
- Documentation / Operational Notes
- Execution Ledger (Planning Mode)
- Sources & References

Optional when materially useful:
- High-Level Technical Design
- Alternative Approaches Considered
- Success Metrics
- Dependencies / Prerequisites
- Risk Analysis & Mitigation
- Phased Delivery
- Documentation Plan
- Operational / Rollout Notes
- Future Considerations

General-plan rules:
- every phase heading carries a stable `P`-ID prefix
- every acceptance item carries a stable `AC`-ID prefix
- every phase has explicit exit criteria
- every `AC` item maps to a governing spec constraint, brainstorm decision, or invariant
- every feature-bearing implementation unit names exact file paths and test-file paths
- pseudo-code and diagrams are allowed only as directional design guidance, not implementation code

Suggested core template:

```md
---
title: <plan title>
type: feat|fix|refactor
status: active
date: YYYY-MM-DD
origin: docs/brainstorms/YYYY-MM-DD-<topic>-requirements.md
spec: Docs/specs/YYYY-MM-DD-<topic>-spec.md
ui_spec: docs/ui-specs/YYYY-MM-DD-<name>-ui-spec.md
deepened: YYYY-MM-DD
---

# <Plan Title>

## Overview

<what is changing and why>

## Problem Frame

<user / business / operational problem and current context>

## Requirements Trace

- R1. <requirement or success criterion>
- R2. <requirement or success criterion>

## Scope Boundaries

- <explicit non-goal>

## Context & Research

### Relevant Code and Patterns
- <existing file, class, component, or workflow to mirror>

### Institutional Learnings
- <relevant docs/solutions or .harness/memory finding>

### External References
- <only when used>

## Key Technical Decisions

- <decision>: <rationale and tradeoff>

## Open Questions

### Resolved During Planning
- <question>: <resolution>

### Deferred to Implementation
- <unknown>: <why it is intentionally deferred>

## High-Level Technical Design

> *This illustrates the intended approach and is directional guidance for review, not implementation specification. The implementing agent should treat it as context, not code to reproduce.*

<optional pseudo-code, mermaid, state flow, contract sketch, or data flow>

## Implementation Units

- [ ] **P0 / Unit 1: <name>**

**Goal:** <what this unit accomplishes>

**Requirements:** <R1, R2>

**Dependencies:** <None / earlier unit / prerequisite>

**Files:**
- Create: `path/to/new_file`
- Modify: `path/to/existing_file`
- Test: `path/to/test_file`

**Approach:**
- <key design or sequencing decision>

**Execution note:** <optional test-first / characterization-first / external-delegate signal>

**Technical design:** <optional pseudo-code or diagram, directional only>

**Patterns to follow:**
- <existing file / class / pattern>

**Test scenarios:**
- <specific success path>
- <edge case or failure path>

**Verification:**
- <observable outcome when complete>

## System-Wide Impact

- **Interaction graph:** <callbacks, middleware, entry points, or cross-surface touchpoints>
- **Error propagation:** <how failures should travel>
- **State lifecycle risks:** <partial write, cache, duplicate, cleanup, migration>
- **API surface parity:** <other interfaces or surfaces that need matching treatment>
- **Integration coverage:** <cross-layer cases unit tests alone will not prove>

## Risks & Dependencies

- <meaningful risk or sequencing concern>

## Documentation / Operational Notes

- <docs, rollout, migration, support, or monitoring impacts when relevant>

## Execution Ledger (Planning Mode)

STEP_ID | status (pending|in_progress|completed) | owner | evidence

## Sources & References

- Origin document: <path>
- Related code: <path or symbol>
- Related issues/PRs: <refs>
- External docs: <URLs>
```

## Plan depth guidance
- `Lightweight`: usually 2-4 implementation units; omit optional sections that add little value.
- `Standard`: use the full core template, adding optional sections only when they improve execution quality.
- `Deep`: usually 4-8 implementation units; group into phases when helpful and add deeper risk, rollout, or alternatives analysis when warranted.

## Deep-plan extensions
Use these only when they materially improve execution quality or stakeholder alignment.

```md
## Alternative Approaches Considered
- <approach>: <why not chosen>

## Success Metrics
- <how the team will know this solved the intended problem>

## Dependencies / Prerequisites
- <technical, organizational, or rollout dependency>

## Risk Analysis & Mitigation
- <risk>: <mitigation>

## Phased Delivery
### Phase 1
- <what lands first and why>
### Phase 2
- <what follows and why>

## Documentation Plan
- <docs or runbooks to update>

## Operational / Rollout Notes
- <monitoring, migration, feature flag, or rollback considerations>
```

## Dedicated UI plan template
Preferred path:
- `docs/ui-plans/YYYY-MM-DD-<descriptive-name>-ui-plan.md`

Compatibility path:
- `Docs/plans/YYYY-MM-DD-<topic>-ui-plan.md`

Suggested frontmatter:

```yaml
---
title: <ui plan title>
type: feat|fix|refactor
status: active
date: YYYY-MM-DD
ui_spec: docs/ui-specs/YYYY-MM-DD-<name>-ui-spec.md  # if applicable
parent_plan: Docs/plans/YYYY-MM-DD-<name>-plan.md    # if applicable
---
```

Required sections:
- Overview
- Component Dependency Map
- Implementation Phases
- Visual Testing Strategy
- Accessibility Validation Checklist
- Acceptance Checklist
- Risks and Mitigations
- Sources & References

Dedicated-UI rules:
- every phase heading carries a `UP`-ID prefix
- every acceptance item carries a `UAC`-ID prefix
- every `UAC` item references its source `VAC` criterion when applicable
- include prototype planning, accessibility validation, and visual testing
- use `UP0` through `UP5` style sequencing unless the scope clearly justifies a variant
- when the parent delivery plan already exists, keep the UI plan focused on build order, contract fidelity, accessibility, and visual verification rather than re-explaining product behavior

## Execution Ledger
Use rows like:

```text
STEP_ID | status (pending|in_progress|completed) | owner | evidence
```

Rules:
- exactly one `in_progress` step at a time
- do not mark `completed` without validation evidence
- if blocked, record the blocker and fallback or next action

## Verification matrix
For general plans, verify:
- every phase has a `P`-ID
- every acceptance item has an `AC`-ID
- the requirements trace exists
- the implementation units section exists
- feature-bearing units include exact test-file paths
- internal references and source links are not obviously broken
- deferred implementation unknowns are explicit rather than hidden as certainty
- any High-Level Technical Design section is clearly directional and non-prescriptive

For dedicated UI plans, verify:
- every phase heading has a `UP`-ID
- every acceptance item has a `UAC`-ID
- every `UAC` references its `VAC` source when applicable
- prototype planning is present

If the repo has additional plan-graph or structural linting, run it as an extra non-blocking quality check before handoff.

## Handoff options
Offer the clearest next-step options that fit the mode:
1. Open the plan in an editor for review
2. Run `he-code-review`
3. Review and refine
4. Proceed to `he-deepen-plan`
5. Run `he-technical-review`
6. Generate or merge a companion UI plan when UI work is in scope
7. Start `he-work`
8. Create an issue in the tracker

Stable-skill note:
- `he-plan` keeps issue mutation out of the planning skill itself; prefer handing off the finished plan to `[[gh-workflow]]` when available, falling back to another installed tracker workflow only when GitHub is not the governing tracker.
