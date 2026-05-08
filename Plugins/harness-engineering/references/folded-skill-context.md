# Folded Skill Context

## Purpose
Keep HE routing compact without losing folded stage context. Folded names are compatibility and mode selectors, not default picker entries. Route folded names to the parent stage and load preserved context only if the mode changes inputs, validation, subagents, or output shape.

## Folded Stage Map

| Folded name | Parent stage | Mode | Preserved context |
| --- | --- | --- | --- |
| `he-ideate` | `he-brainstorm` | options | `fixtures/preserved-context/skills/team_automation/he-ideate/` |
| `he-deepen-spec` | `he-spec` | deepen spec | `fixtures/preserved-context/skills/team_automation/he-deepen-spec/` |
| `he-deepen-plan` | `he-plan` | deepen plan | `fixtures/preserved-context/skills/team_automation/he-deepen-plan/` |
| `he-refine` | `he-improve` | refinement | `fixtures/preserved-context/skills/team_automation/he-refine/` |
| `he-compound-refresh` | `he-compound` | refresh state | `fixtures/preserved-context/skills/team_automation/he-compound-refresh/` |
| `he-prune-branches` | `he-router` | `agent-ops` branch hygiene | `fixtures/preserved-context/skills/team_automation/he-prune-branches/` |
| `he-tdd` | `he-work` | test-first | `fixtures/preserved-context/skills/team_automation/he-tdd/` |
| `he-technical-review` | `he-code-review` | technical critique | `fixtures/preserved-context/skills/code_quality_review/he-technical-review/` |
| `he-reliability-review` | `he-code-review` | reliability critique | `fixtures/preserved-context/skills/code_quality_review/he-reliability-review/` |

## Calling Rules

- Direct user mentions of a folded name must route to the parent stage, not the folded skill.
- Prefer the parent-stage command plus `mode: <folded mode>` unless the user needs a compatibility entrypoint.
- Do not summarize or trim away mode details for token budget reasons. Move long material into references and add it to this map or `deferred-context-index.md`.
- Keep branch pruning out of the HE parent-stage surface. Use `he-router` only to classify the request and hand off to `agent-ops` branch hygiene.
- Keep folded names available through router aliases and parent modes. Re-add a picker entry only for a concrete standalone use case.
- Preserve valid `ce-docs-review` behavior inside `he-spec` and `he-plan` as a
  lightweight document review/deepening pass. It should strengthen source
  coverage, contradictions, acceptance IDs, validation, sequencing, and handoff
  evidence without creating another default stage.

## Parent Responsibilities

- `he-brainstorm`: load `he-ideate` context for options, opportunity scanning, or direction comparison.
- `he-spec`: load `he-deepen-spec` context when hardening an existing spec or resolving contract contradictions.
- `he-plan`: load `he-deepen-plan` context when hardening an existing plan or strengthening sequencing and gates.
- `he-work`: load `he-tdd` context when the user asks for RED/GREEN, failing-test-first, regression-first, or test-first execution.
- `he-improve`: load `he-refine` context for browser-first or iterative artifact refinement.
- `he-code-review`: load `he-technical-review` or `he-reliability-review` context for deeper-than-readiness review.
- `he-compound`: load `he-compound-refresh` context when resuming stale lifecycle state or refreshing solution docs.
