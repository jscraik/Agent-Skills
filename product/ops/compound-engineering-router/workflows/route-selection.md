# Route Selection

## Table of Contents
- [Goal](#goal)
- [Route criteria](#route-criteria)
- [Review split](#review-split)
- [Meta-mode split](#meta-mode-split)
- [Output brief checklist](#output-brief-checklist)

## Goal
Choose the smallest correct workflow route for a compound-engineering request.

## Route criteria
| Route | Choose when | Packaged skill path | Legacy prompt alias (deprecated) | Typical agent fan-out |
|---|---|---|---|---|
| ideate | The user wants ranked improvement directions before choosing one to define in depth. | `.agents/skills/ce-ideate` | none | `repo-research-analyst`, `learnings-researcher`, optional issue-intelligence support |
| brainstorm | The request is still exploratory or has multiple valid shapes. | `.agents/skills/ce-brainstorm` | `codex/prompts/workflow-brainstorm.md` | `repo-research-analyst`, `learnings-researcher` |
| spec | The user needs an implementation-ready spec from a rough idea. | `.agents/skills/ce-spec` | `codex/prompts/workflow-spec.md` | `repo-research-analyst`, `learnings-researcher`, optional research roles |
| deepen-spec | A spec exists but lacks rigor, edge cases, or operational detail. | `.agents/skills/ce-deepen-spec` | `codex/prompts/deepen-spec.md` | `repo-research-analyst`, `learnings-researcher`, optional research roles |
| plan | A spec is ready and the next need is execution planning, including test mode, tracer-bullet-first decisions, and validation gates. | `.agents/skills/ce-plan` | `codex/prompts/workflow-plan.md` | research roles plus `spec-flow-analyzer` |
| deepen-plan | A plan exists but needs stronger sequencing, gates, TDD declarations, or validation coverage. | `.agents/skills/ce-deepen-plan` | `codex/prompts/deepen-plan.md` | research roles |
| tdd | The plan specifies test-first execution posture and the user wants vertical tracer bullet TDD discipline during `ce-work`. | `.agents/skills/ce-tdd` | none | none by default |
| work | The spec and plan are sufficiently ready for implementation, and the TDD/tracer-bullet contract is explicit enough to execute safely. Default to one supervisor agent owning the lane. | `.agents/skills/ce-work` | `codex/prompts/workflow-work.md` | usually none by default; bounded internal reviewers only if justified |
| review | The need is broad readiness, synthesis, go-no-go, or package-level review. | `.agents/skills/ce-review` | `codex/prompts/workflow-review.md` | reviewer mix based on risk areas |
| technical-review | The need is a deep engineering critique of code, diff, PR, or branch. | `.agents/skills/ce-technical-review` | `codex/prompts/technical_review.md` | specialist reviewers by language or risk area |
| compound | The user wants a multi-stage orchestration or is unsure but clearly needs coordinated workflow help. | `.agents/skills/ce-compound` | `codex/prompts/workflow-compound.md` | research roles plus optional specialized reviewers |
| compound-refresh | The user wants to refresh stale learnings or pattern docs in `docs/solutions/` against current code reality. | `.agents/skills/ce-compound-refresh` | none | usually none by default; bounded investigation support if scope is broad |

## UI routing

Retire the standalone `ui-workflow` route. Route UI-first requests by artifact maturity:

- Choose `spec` when the UI contract is still missing or incomplete:
  - new screens or flows without a defined UI contract
  - component inventory, states, accessibility, tokens, or `VAC` criteria are still unclear
  - the parent spec indicates `ui_required: true` but no companion UI spec exists yet
- Choose `plan` when the UI contract already exists and the next need is execution sequencing:
  - prototype-first planning
  - dedicated UI plan generation
  - build order, validation, rollout, or visual-verification planning
  - brownfield UI refinement that already has enough contract clarity to sequence implementation safely

When a UI request is ambiguous, ask the smallest clarifying question:
- "Do you need the UI contract defined first, or is the contract already clear and you want the build plan?"

## Review split
Use `review` when the user wants:
- readiness
- synthesis
- go or no-go
- a broad cross-functional review

Use `technical-review` when the user wants:
- architecture critique
- security, performance, data, or frontend-race analysis
- language-specific deep review
- diff, PR, or branch-level engineering critique

Do not collapse these routes.

## Meta-mode split
Use `context-compaction` when the job is continuity, summarization, or baton passing rather than workflow-stage selection.

Use `guardrail-extract` when the job is to convert a resolved failure or repeated confusion into a durable update recommendation.

Do not pretend meta-modes are prompt-backed routes.

## Output brief checklist
Every routed result should include:
- selected route or meta-mode
- packaged skill path when skill-backed
- legacy prompt alias when relevant, otherwise an explicit no-prompt-path note for meta-modes
- route rationale
- exact specialist agents if applicable
- execution posture: one supervisor agent by default, with any additional roles called out as bounded internal support
- safeguards
- validation gates
- TDD / tracer-bullet expectation when the route points toward implementation work
- next recommended action
