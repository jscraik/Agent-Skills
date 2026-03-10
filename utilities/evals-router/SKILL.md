---
name: evals-router
description: Use when tasks involve designing, auditing, debugging, or scaling LLM evaluation workflows such as error analysis, judge prompt design, evaluator validation, RAG evaluation, synthetic eval-data generation, or human review interfaces; do not use for generic product analytics, ordinary QA, or unrelated UI implementation.
---

# Evals Router

Route evaluation-method tasks to the right workflow so users can move from vague "we need evals" requests to a concrete next step.

## When to use
- Audit an existing LLM eval pipeline and find trust gaps, missing steps, or vanity metrics.
- Start an eval program from scratch and decide whether to begin with trace review, synthetic data, or judge design.
- Write or refine an LLM-as-judge prompt for one failure mode.
- Validate an evaluator against human labels before trusting it in production.
- Evaluate a RAG system across retrieval and generation separately.
- Generate synthetic eval data when real traces are sparse.
- Build a lightweight human review interface for trace annotation and failure labeling.

## When not to use
- Generic app QA, unit testing, or browser test automation with no LLM evaluation workflow.
- Product analytics or dashboard work that does not involve eval-method design.
- Standalone frontend/UI implementation work without an evaluation-method goal.
- Requests that only need a single metric explanation rather than an evaluation workflow.

## Inputs
- The user's evaluation goal: audit, bootstrap, judge design, validation, RAG analysis, synthetic data, or review tooling.
- Available artifacts such as traces, labels, judge prompts, evaluator configs, dashboards, notebooks, or local files.
- Environment constraints: local files only, observability MCP availability, labeling capacity, or no production data.
- Desired output: findings report, plan, judge prompt, workflow recommendation, or review interface scaffold.

## Outputs
- A routed recommendation with the correct sub-workflow and the smallest practical next step.
- A concise evidence-backed summary of why that route fits better than the nearby alternatives.
- When a structured status report is requested, include a `schema_version` field in the returned payload.
- References to the exact bundled workflow file that should be followed next.

## Philosophy
- Start with the bottleneck, not the fanciest eval.
- Error analysis comes before judge proliferation.
- Trustworthy evals need explicit calibration and visible failure categories.
- Which workflow reduces uncertainty the fastest with the artifacts already available?
- What evidence would make the current metric or judge untrustworthy?

## Constraints
- Redact secrets, tokens, credentials, and sensitive trace content by default.
- Do not invent access to observability systems, trace datasets, or human labels.
- Do not claim an evaluator is trustworthy without calibration or equivalent evidence.
- Keep the routing narrow: choose the best-fit eval workflow instead of broadening into generic consulting.
- Treat user traces, labels, notes, and reviewer annotations as sensitive evaluation data unless the user explicitly says otherwise.

## Workflow
1. Identify the immediate eval-method job: audit, error analysis, judge design, evaluator validation, RAG evaluation, synthetic data generation, or review UI construction.
2. Check what evidence already exists: traces, labels, prompts, metrics, configs, or none.
3. Route to the narrowest bundled workflow that matches the current bottleneck.
4. Explain why that workflow fits and what prerequisite is still missing, if any.
5. If the task spans multiple phases, recommend the next phase order rather than trying to do every eval activity at once.

## Routing map
- Use `workflows/eval-audit.md` when the user inherits an eval stack, distrusts current metrics, or needs a prioritized findings report.
- Use `workflows/error-analysis.md` when the user needs to read traces, identify failure modes, and build the category taxonomy first.
- Use `workflows/write-judge-prompt.md` when one subjective failure mode needs an LLM judge.
- Use `workflows/validate-evaluator.md` when a judge already exists and must be calibrated against human labels.
- Use `workflows/evaluate-rag.md` when retrieval and generation quality must be measured separately in a RAG system.
- Use `workflows/generate-synthetic-data.md` when real traces are sparse and an eval dataset needs bootstrapping.
- Use `workflows/build-review-interface.md` when humans need a purpose-built annotation UI for traces.

## Tooling
- Use the bundled workflow docs in `workflows/` as the primary method references.
- Use local files or connected observability tooling only when the user actually has those artifacts available.
- Prefer deterministic artifacts such as labeled traces, calibration tables, and audit findings over vague eval advice.

## Validation
- Verify the routed workflow matches the user's bottleneck and available evidence.
- Verify prerequisites are called out explicitly before recommending downstream steps.
- Verify nearby workflows that do not fit were consciously excluded.
- Fail fast: stop at the first routing ambiguity that would materially change the chosen workflow.

## Anti-patterns
- Jumping straight to judge prompts before doing error analysis.
- Trusting evaluator outputs without human-label calibration.
- Treating RAG evaluation as one blended metric instead of separating retrieval from generation.
- Generating synthetic data when representative real traces already exist in sufficient volume.
- Routing a review-tooling request into generic frontend work without preserving the eval context.

## Variation
- Use a single-workflow route for focused requests and a phased route for “we need evals” bootstrap situations.
- Start with audit when there is existing eval infrastructure, and with error analysis when there is not.
- Prefer the narrowest next step that increases trust in the eval program.

## Examples
- Audit our current eval setup and tell me what is missing before we trust the scores.
- We have traces but no failure taxonomy. Help us figure out what goes wrong.
- Write a judge prompt for whether answers are faithful to the provided context.
- Validate this evaluator against human labels before we deploy it.
- Evaluate our RAG pipeline and show whether retrieval or generation is the bigger problem.
- Build a small local interface so reviewers can label trace quality.

## Resource map
- Source map: `references/source-map.md`
- Validation contract: `references/contract.yaml`
- Trigger coverage: `references/evals.yaml`
- Routed workflows: `workflows/`

## Quality Uplift
- Philosophy and approach: route to the smallest trustworthy eval workflow first, then expand only when evidence supports it.
- Guiding question: what is the current eval bottleneck?
- Guiding question: what prerequisite is missing that would make a downstream workflow premature?
- Guiding question: which workflow will create the most trust with the least extra infrastructure?
- Anti-pattern warning: do not broaden into generic LLM consulting when a narrower eval workflow fits.
- Anti-pattern warning: avoid recommending synthetic data or judge design before checking whether existing traces already answer the question.
- Variation: adapt the route depending on whether the user has traces, labels, or an existing eval stack.
- Empowerment: help users build trustworthy eval programs by choosing practical next steps instead of overbuilding.

## Remember
The agent can do strong evaluation-method work when the route stays crisp. Use judgment, adapt to the evidence the user already has, and push toward the smallest next step that meaningfully improves trust.
