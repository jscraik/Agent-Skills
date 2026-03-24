---
name: evals-router
description: Route and guide LLM evaluation work such as evaluator design, error analysis, RAG evals, and synthetic eval data. Use when the user wants eval-specific workflow help, not product analytics or ordinary QA.
metadata:
  skill-type: code_quality_review
---

# Evals Router

Route evaluation-method work to the smallest trustworthy workflow so users can move from "we need evals" to an evidence-backed next step.

## Standards snapshot (March 2026)
- Start with the current trust bottleneck, not the most sophisticated evaluator.
- Prefer trace review, calibration evidence, and failure taxonomies over vanity dashboards.
- Treat evaluator validation and review operations as production work, not notebook-side experimentation.
- Separate retrieval quality, generation quality, reviewer quality, and judge quality instead of blending them into one score.

## When to use
- Auditing an existing LLM eval stack to find trust gaps, missing controls, or misleading metrics.
- Bootstrapping an eval program and deciding whether to begin with traces, labels, judge prompts, or review tooling.
- Writing or refining an LLM-as-judge prompt for a specific failure mode.
- Validating an evaluator against human labels before trusting it in production.
- Evaluating a RAG system across retrieval and generation separately.
- Generating synthetic eval data when representative real traces are sparse.
- Designing a lightweight human review interface for annotation or disagreement analysis.

## When not to use
- The task is generic QA, browser automation, or product analytics without an LLM evaluation question.
- The user only needs a metric explanation rather than an evaluation workflow.
- The task is ordinary UI implementation with no judge, trace, or review-method component.

## Required inputs
- The evaluation goal: audit, bootstrap, error analysis, judge design, evaluator validation, RAG analysis, synthetic data, or review tooling.
- Available evidence: traces, labels, prompts, configs, dashboards, notebooks, or local files.
- Environment constraints such as local-only access, observability tooling, reviewer capacity, or no production data.
- Desired output: findings report, route recommendation, judge prompt, plan, or review-interface scaffold.

## Deliverables
- A routed recommendation pointing to the correct bundled workflow.
- A short evidence-backed explanation of why that route fits better than adjacent options.
- Explicit prerequisites or blockers that must be resolved before downstream work is trustworthy.
- References to the exact workflow file that should be followed next.

## Failure mode
- If the task spans multiple evaluation phases, return the correct sequence instead of pretending one workflow covers everything.
- If the current bottleneck is ambiguous and would materially change the route, stop and ask for the missing evidence rather than guessing.
- If no evaluation artifact exists yet, route to bootstrap analysis instead of overfitting to an arbitrary evaluator design.

## Workflow
1. Identify the immediate job: audit, error analysis, judge design, evaluator validation, RAG evaluation, synthetic-data generation, or review tooling.
2. Inventory the evidence that already exists: traces, labels, prompts, metrics, configs, or none.
3. Choose the narrowest bundled workflow that addresses the current trust bottleneck.
4. Explain why that route fits and name the first prerequisite still missing, if any.
5. If the request spans multiple phases, recommend the execution order instead of broadening into generic eval consulting.

## Routing map
- Use `workflows/eval-audit.md` when the user inherits an eval stack, distrusts current metrics, or needs a prioritized findings report.
- Use `workflows/error-analysis.md` when the user needs to read traces, identify failure modes, and build the category taxonomy first.
- Use `workflows/write-judge-prompt.md` when one subjective failure mode needs an LLM judge.
- Use `workflows/validate-evaluator.md` when a judge already exists and must be calibrated against human labels.
- Use `workflows/evaluate-rag.md` when retrieval and generation quality must be measured separately in a RAG system.
- Use `workflows/generate-synthetic-data.md` when real traces are sparse and an eval dataset needs bootstrapping.
- Use `workflows/build-review-interface.md` when humans need a purpose-built annotation UI for traces.

## Tooling and references
- Treat `workflows/` as the primary method reference, not optional reading.
- Use local files or observability tooling only when the user actually has those artifacts.
- Prefer concrete deliverables such as labeled traces, calibration tables, or audit findings over generic eval advice.
- Reference files:
  - `references/source-map.md`
  - `references/contract.yaml`
  - `references/evals.yaml`

## Validation
- Verify the chosen workflow matches the user’s bottleneck and the evidence actually available.
- Verify prerequisites are called out before recommending downstream steps.
- Verify the nearby workflows that do not fit were consciously excluded.
- Fail fast at the first routing ambiguity that would change the selected workflow.

## Anti-patterns
- Jumping straight to judge prompts before doing error analysis.
- Trusting evaluator outputs without human-label calibration or equivalent evidence.
- Treating RAG evaluation as one blended metric instead of separating retrieval from generation.
- Generating synthetic data when sufficient representative traces already exist.
- Routing review-tooling requests into generic frontend work without preserving the eval context.

## Variation
- Use a single-workflow route for focused requests and a phased route for broad "we need evals" bootstrap requests.
- Start with audit when eval infrastructure already exists, and with error analysis when it does not.
- Increase emphasis on calibration and disagreement analysis when the evaluator is already influencing product decisions.

## Examples
- Audit our current eval setup and tell me what is missing before we trust the scores.
- We have traces but no failure taxonomy. Help us figure out what goes wrong.
- Write a judge prompt for whether answers are faithful to the provided context.
- Validate this evaluator against human labels before we deploy it.
- Evaluate our RAG pipeline and show whether retrieval or generation is the bigger problem.
- Build a small local interface so reviewers can label trace quality.

## Remember
Keep the route crisp. The goal is not to explain all of evaluation; it is to pick the smallest next workflow that meaningfully increases trust.

## See Also

| Skill | When to use together |
|---|---|
| [[systematic-debugging]] | When eval pipeline bugs emerge — debug root cause before redesigning the eval |
| [[verification-before-completion]] | Gate "eval is ready" claims with concrete calibration or human-label evidence |
| [[skill-builder]] | When the eval workflow should be packaged as a reusable Codex skill |
| [[test-driven-development]] | For the implementation layer of the review tooling or judge prompt validation tests |

**Topic map:** [[agent-ops]]


## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
