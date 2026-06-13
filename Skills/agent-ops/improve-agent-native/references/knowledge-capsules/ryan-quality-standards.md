# Quality Standards

Convert exemplary engineering practice, accessibility expectations, and full-loop evals into quality bars for generated work.

Pack id: pack.ryan-lopopolo-principal-engineering
Facet id: quality_standards
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: reviewed

## Claim Cards

### claim.ryan.distilled-quality-exemplars: Quality Exemplars Should Be Distilled Into Standards

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Teams should distill collective experience and exemplary codebases into standards that generated code can follow consistently.

Interpretation notes:
- This supports quality rubrics and exemplar-based guardrails.

### claim.ryan.code-free-accessibility: Cheap Code Raises Accessibility Expectations

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

The source raises accessibility quality as a comparison point for AI products and generated interfaces when code becomes cheap.

Interpretation notes:
- This preserves the source-bound question; the stronger quality-bar guidance is carried by the derived accessibility heuristic.

### claim.ryan.benchmarks-produce-code-not-engineers: Code Benchmarks Do Not Make Software Engineers

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Coding benchmarks can improve code production without measuring whether a model behaves like a software engineer.

Interpretation notes:
- This supports evals that include iteration, judgment, context, validation, and ownership.

### claim.ryan.synthesis-failure-guardrail: Models Can Explain Synthesis Failure Without Synthesizing

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

A model may be able to articulate why a document is poor while still failing to synthesize the correct durable abstraction.

Interpretation notes:
- This supports stronger artifact templates and synthesis checks for durable docs.

### claim.ryan.misuse-resistant-interface-design: Interfaces Should Carry Authority Ownership And Invariants

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Secure interfaces should make correct use natural and unsafe use hard to express by carrying authority, ownership, and invariants in their shape.

Interpretation notes:
- This is a concrete principal-engineering guardrail for API and platform review.

### claim.ryan.contextual-affordance-judgment: Product Affordances Need Contextual Judgment

- Type: claim-card
- Status: reviewed
- Claim strength: inferred
- Source boundaries: user_provided_excerpt_not_independently_verified, article_source_note_paraphrase

AI product surfaces should use contextual judgment to decide whether an affordance is appropriate for the current task and medium.

Interpretation notes:
- This is inferred from the tool-discovery affordance claim and a product-behavior joke, and should remain lower strength than direct harness claims.

### claim.ryan.tool-discovery: Agents Need Tool Discovery

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Agent-first tools need machine-readable discovery surfaces that expose names, descriptions, schemas, and examples.

Interpretation notes:
- This is a principal-engineering review concern for internal platform tools and CLIs.

### claim.ryan.work-is-iterative-game: Work Is An Iterative Game

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Work should be treated as iterative rather than a single-pass production act.

Interpretation notes:
- This short claim anchors OODA and evaluation-loop assets.

## Principles

### principle.ryan.distill-exemplars-into-quality-standards: Distill Exemplars Into Quality Standards

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.distilled-quality-exemplars

Use exemplary codebases and hard-won collective expertise as inputs to explicit quality standards for generated work.

Rationale: If agents can generate code cheaply, teams can afford to make high-quality defaults more universal through rubrics, lints, examples, and review checks.

Application notes:
- Choose exemplars whose constraints match the target system.
- Convert taste into checkable examples, standards, and tests.
- Avoid vague exhortations to write better code.

### principle.ryan.misuse-resistant-interface-design: Design Misuse-Resistant Interfaces

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.misuse-resistant-interface-design

Prefer API shapes that grant narrow authority, encode ownership, and make invalid or unsafe use hard to express.

Rationale: Secure behavior is more reliable when authority and invariants are represented by types, boundaries, and operations instead of caller memory.

Application notes:
- Keep host paths, environment discovery, and compatibility glue behind small boundaries.
- Parse fixed config into typed fields at the boundary.
- Return errors with operation context and original cause.

## Heuristics

### heuristic.ryan.evaluate-ai-products-on-accessibility: Evaluate AI Products On Accessibility

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.code-free-accessibility

Treat WCAG behavior, focus order, tabindex discipline, screen reader support, and semantic structure as standard AI-product comparison criteria.

Use when:
- Reviewing generated UI, AI product surfaces, or agent-built frontend work.
- Code generation makes accessibility fixes cheap enough to expect by default.
- A product claims quality or production readiness.

Avoid when:
- The artifact is a noninteractive internal prototype clearly outside user-facing scope.
- The review lacks a way to inspect rendered behavior or semantics.

### heuristic.ryan.use-ai-to-judge-contextual-affordances: Use AI To Judge Contextual Affordances

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified, article_source_note_paraphrase
- Derived from claims: claim.ryan.contextual-affordance-judgment

Before rendering an intelligent affordance, ask whether the current user task, object type, and medium make that affordance useful or distracting.

Use when:
- A product surface can render AI-generated previews, annotations, enrichments, or transformations.
- The same data can mean different things in different workflows.
- Poor affordance choice would confuse the user or imply false relevance.

Avoid when:
- The affordance is purely deterministic and universally expected.
- The judgment step would slow a critical path without changing behavior.

### heuristic.ryan.measure-engineering-not-code-output: Measure Engineering Not Code Output

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.benchmarks-produce-code-not-engineers, claim.ryan.work-is-iterative-game

Evaluate agents on the full engineering loop: context gathering, judgment, iteration, validation, communication, and ownership, not just code diff success.

Use when:
- Designing evals for software-engineering agents.
- Comparing benchmark performance with real delivery readiness.
- Reviewing whether an agent can own a task over time.

Avoid when:
- The only goal is measuring a narrow code-generation primitive.
- The benchmark intentionally excludes process, judgment, and validation.

### heuristic.ryan.force-synthesis-into-artifact-shape: Force Synthesis Into Artifact Shape

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.synthesis-failure-guardrail

When a model can critique a doc but not synthesize it, constrain the output with a target abstraction, audience, policy surface, and examples.

Use when:
- Repeated rewrites preserve local detail but miss the governing principle.
- The desired artifact should steer many future changes.
- The model is explaining failure instead of producing the durable shape.

Avoid when:
- The task is simple copy editing with no abstraction gap.
- The user has not identified the target policy or audience.

## Anti-Patterns

### anti-pattern.ryan.code-output-benchmark-laundering: Code Output Benchmark Laundering

- Type: anti-pattern
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.benchmarks-produce-code-not-engineers

Problem: A model's code-benchmark score is treated as proof that it can operate like a software engineer.

Failure mode: Teams over-trust code production while missing context gathering, iteration, validation, stakeholder communication, and ownership gaps.

Avoidance: Pair code-output benchmarks with evals that test the full software-engineering loop and task ownership over time.

## Eval Scenarios

### eval.ryan.benchmark-laundering-quality-gate: Benchmark Laundering Quality Gate

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.benchmarks-produce-code-not-engineers, claim.ryan.synthesis-failure-guardrail

Given: A proposed agent eval rewards code output volume or benchmark pass rate while ignoring synthesis quality, accessibility, maintainability, and whether the work behaves like software engineering.
Should: The agent identifies benchmark laundering risk, names the missing full-loop quality checks, and proposes a quality gate that evaluates artifact usefulness, synthesis clarity, accessibility or misuse resistance when relevant, and durable engineering behavior.
Expected failure: The agent accepts the benchmark result as sufficient proof that the model or harness behaves like a software engineer.
Reproduce with: references/evals/eval.ryan.benchmark-laundering-quality-gate.md
