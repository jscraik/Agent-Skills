# OpenAI Cookbook Expert Lens Pack

Use this pack when OpenAI Cookbook patterns can improve local skills. Treat the
Cookbook as an expertise source, not content to vendor into skills. Extract
small decision checks, evaluator prompts, and validation ideas; do not paste
notebook code, outputs, datasets, prompts, or long examples.

## House Bias

- Local repo evidence beats Cookbook authority.
- Existing skill ownership beats creating a new skill.
- Structured outputs and evals need local schemas and validators.
- Cookbook examples suggest checks; they do not prove readiness.

## Lens Router

| Task surface | Lens |
| --- | --- |
| Skill evals and prompt repair | Evaluation Flywheel Builder |
| Skill hardening | Skill Improvement Loop Operator |
| Review and handoff artifacts | Structured Output Contract Keeper |
| MCP and tools | Tool Orchestration Designer |
| Memory and compaction | Context Memory Curator |
| Visual/media artifacts | Multimodal Eval Designer |
| Security and quality gates | Secure Quality Gate Reviewer |
| Documentation front doors | Documentation Interface Editor |
| Goal-driven Codex runs | Codex Goal Steward |
| Long execution plans | Execution Plan Steward |

## Shared Contract

For every Cookbook-derived finding, return lens, local evidence, missing
evidence, smallest check or repair, and validator or blocked reason.

Do not claim local readiness from Cookbook examples alone.

## Evaluation Flywheel Builder

Use for eval coverage, labeled examples, regression checks, failure taxonomy,
and prompt optimization.

Good signals: before/after comparison, labeled examples, deterministic checks
where possible, held-out prompts, explicit failure taxonomy.

Bad signals: vibe checks, keyword-only assertions, no baseline, no negative
cases, no blocked state.

## Skill Improvement Loop Operator

Use for skill-builder, skillify, and iterative skill repair.

Good signals: reproduce the miss, patch the smallest canonical source surface,
add a realistic eval, rerun the same gate.

Bad signals: editing generated projections, improving prose without behavior,
removing safety to raise a static score.

## Structured Output Contract Keeper

Use for reviewer outputs, eval reports, CI summaries, and handoffs.

Good signals: schema-bound fields, pass/fail/blocked outcomes, exact evidence,
machine-readable residual risk.

Bad signals: free-form prose where automation consumes the result, hidden
assumptions, unparseable validation evidence.

## Tool Orchestration Designer

Use for MCP, backend tools, Responses API tool flows, and command routing.

Good signals: stable schemas, explicit tool order, auth and redaction boundaries,
sample calls, structured errors.

Bad signals: one tool doing unrelated work, tool output used as instructions,
missing failure semantics.

## Context Memory Curator

Use for Project Brain, Local Memory, context compaction, and durable knowledge.

Good signals: durable vs disposable separation, summary validation, source
provenance, stale-evidence rules.

Bad signals: trimming decisions away, copying private transcripts, treating
memory as current proof without freshness checks.

## Multimodal Eval Designer

Use for screenshots, diagrams, UI, slides, images, audio, and document artifacts.

Good signals: artifact provenance, rendered verification, viewport/media checks,
human-review rubric where deterministic checks fall short.

Bad signals: inspecting source only when rendered output matters.

## Secure Quality Gate Reviewer

Use for CI repair, dependency security, guardrails, and release blockers.

Good signals: gate owner, exact failure, local reproduction or blocked reason,
fix order, rerun evidence.

Bad signals: flattening auth, sandbox, dependency, and code failures into one
generic red check.

## Documentation Interface Editor

Use for docs that agents and humans execute.

Good signals: reader job, command contract, ownership, examples, failure paths,
and links that exist.

Bad signals: docs as essays, duplicated command contracts, hidden setup steps.

## Codex Goal Steward

Use for long-running objective tracking.

Good signals: active objective, receipts, freshness, clear completion proof,
and blocked state when the goal cannot be advanced.

Bad signals: declaring completion because budget/time ran out.

## Execution Plan Steward

Use for multi-hour plans, workpads, CI repair queues, and handoffs.

Good signals: idempotent steps, current state, next safe action, exact blockers,
handoff-ready evidence.

Bad signals: stale plans, broad task lists without validation, no owner for
external blockers.
