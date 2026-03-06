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
| Route | Choose when | Prompt path | Typical agent fan-out |
|---|---|---|---|
| brainstorm | The request is still exploratory or has multiple valid shapes. | `codex/prompts/workflow-brainstorm.md` | `repo-research-analyst`, `learnings-researcher` |
| spec | The user needs an implementation-ready spec from a rough idea. | `codex/prompts/workflow-spec.md` | `repo-research-analyst`, `learnings-researcher`, optional research roles |
| deepen-spec | A spec exists but lacks rigor, edge cases, or operational detail. | `codex/prompts/deepen-spec.md` | `repo-research-analyst`, `learnings-researcher`, optional research roles |
| plan | A spec is ready and the next need is execution planning. | `codex/prompts/workflow-plan.md` | research roles plus `spec-flow-analyzer` |
| deepen-plan | A plan exists but needs stronger sequencing, gates, or validation coverage. | `codex/prompts/deepen-plan.md` | research roles |
| work | The spec and plan are sufficiently ready for implementation. | `codex/prompts/workflow-work.md` | usually none by default |
| review | The need is broad readiness, synthesis, go-no-go, or package-level review. | `codex/prompts/workflow-review.md` | reviewer mix based on risk areas |
| technical-review | The need is a deep engineering critique of code, diff, PR, or branch. | `codex/prompts/technical_review.md` | specialist reviewers by language or risk area |
| compound | The user wants a multi-stage orchestration or is unsure but clearly needs coordinated workflow help. | `codex/prompts/workflow-compound.md` | research roles plus optional specialized reviewers |

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
- prompt path when prompt-backed, otherwise an explicit no-prompt-path note
- route rationale
- exact specialist agents if applicable
- safeguards
- validation gates
- next recommended action
