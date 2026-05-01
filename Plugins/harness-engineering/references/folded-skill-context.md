# Folded Skill Context

## Purpose
Keep Harness Engineering stage routing compact without losing stage-specific context.

The folders below remain canonical preserved context. When a request uses a folded name, route to the parent stage and load the listed context before acting.

## Folded Stage Map

| Folded name | Parent stage | Mode | Preserved context |
| --- | --- | --- | --- |
| `he-ideate` | `he-brainstorm` | option generation and opportunity comparison | `Plugins/harness-engineering/skills/team_automation/he-ideate/SKILL.md` |
| `he-deepen-spec` | `he-spec` | deepen existing spec | `Plugins/harness-engineering/skills/team_automation/he-deepen-spec/SKILL.md` |
| `he-deepen-plan` | `he-plan` | deepen existing plan | `Plugins/harness-engineering/skills/team_automation/he-deepen-plan/SKILL.md` |
| `he-refine` | `he-improve` | refinement loop with browser or artifact evidence | `Plugins/harness-engineering/skills/team_automation/he-refine/SKILL.md` |
| `he-compound-refresh` | `he-compound` | refresh, resume, or re-check compound run state | `Plugins/harness-engineering/skills/team_automation/he-compound-refresh/SKILL.md` |
| `he-prune-branches` | `he-router` | hand off to `agent-ops` branch hygiene | `Plugins/harness-engineering/skills/team_automation/he-prune-branches/SKILL.md` |
| `he-tdd` | `he-work` | test-first execution posture | `Plugins/harness-engineering/skills/team_automation/he-tdd/SKILL.md` |
| `he-technical-review` | `he-code-review` | deep technical critique | `Plugins/harness-engineering/skills/code_quality_review/he-technical-review/SKILL.md` |
| `he-reliability-review` | `he-code-review` | reliability and resilience critique | `Plugins/harness-engineering/skills/code_quality_review/he-reliability-review/SKILL.md` |

## Calling Rules

- Direct user mentions of a folded name must route to the parent stage, not the folded skill.
- Parent stages must load the preserved context when the folded mode changes required inputs, validation, subagent coverage, or output shape.
- Do not summarize or trim away mode details for token budget reasons. Move long material into references and add it to this map or `deferred-context-index.md`.
- Keep branch pruning out of the HE parent-stage surface. Use `he-router` only to classify the request and hand off to `agent-ops` branch hygiene.
- Keep folded skills available as nested source context and compatibility picker entries, but treat parent stages as the active route.

## Parent Responsibilities

- `he-brainstorm`: load `he-ideate` context for option-generation, opportunity scanning, or "compare possible directions" requests.
- `he-spec`: load `he-deepen-spec` context when hardening an existing spec or resolving contract contradictions.
- `he-plan`: load `he-deepen-plan` context when hardening an existing plan or strengthening sequencing and gates.
- `he-work`: load `he-tdd` context when the user asks for RED/GREEN, failing-test-first, regression-first, or test-first execution.
- `he-improve`: load `he-refine` context for browser-first or iterative artifact refinement.
- `he-code-review`: load `he-technical-review` or `he-reliability-review` context when the request is deeper than package readiness.
- `he-compound`: load `he-compound-refresh` context when resuming stale lifecycle state or refreshing solution docs.
