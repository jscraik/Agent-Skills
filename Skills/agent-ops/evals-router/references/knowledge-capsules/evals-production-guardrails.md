# Production Guardrails

Separate offline measurement from online guardrails and monitor high-risk failures with explicit prevention paths.

Pack id: pack.evals-testing
Facet id: production_guardrails
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.evals.production-needs-online-guardrails: Production Needs Online Guardrails

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Production AI systems need online guardrails for high-risk failures in addition to offline eval trend measurement.

Interpretation notes:
- The testing skill should separate measurement evals from preventative guardrail checks.

### claim.evals.experiments-need-valid-metrics: Experiments Need Valid Metrics

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Controlled experiments need a clear objective metric, proper randomization, instrumentation, and guardrail checks before their results are trustworthy.

Interpretation notes:
- Eval reports should name primary metrics and guardrails rather than reporting a single isolated score.

### claim.evals.code-evals-are-deterministic: Code Evals Are Deterministic

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Code-based evaluators are fast, cheap, deterministic, and appropriate for objective checks.

Interpretation notes:
- The testing skill should prefer code or schema checks when the property is objective.

### claim.evals.skill-review-is-not-behavior-proof: Skill Review Is Not Behavior Proof

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Skill review checks structure and quality, while task and repo evals test whether context improves behavior on scenarios or realistic repository changes.

Interpretation notes:
- Evals-router should not treat a static review score as proof that a skill improves behavior.

### claim.evals.context-impact-needs-baseline: Context Impact Needs Baseline

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Task evals for skill or context impact should compare behavior with and without the added context while holding the rest of the run constant.

Interpretation notes:
- Claims that a knowledge capsule, skill, or registry tile helped should keep baseline behavior, with-context behavior, and publication metadata separate.

### claim.evals.testing-models-can-be-flawed: Testing Models Can Be Flawed

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Tests are designed from testers' models of the product, users, and expected behavior; flawed models produce flawed tests.

Interpretation notes:
- Test plans and evals should name the model or oracle they rely on and record what that model cannot see.

### claim.evals.ux-measurement-needs-method-fit: UX Measurement Needs Method Fit

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

User-experience evaluation can combine qualitative and quantitative methods, and measurement should be chosen to fit the insight needed about user perception and system improvement.

Interpretation notes:
- {"Eval route selection should match the decision"=>"qualitative trace review, deterministic checks, calibrated judges, surveys, or online guardrails answer different questions."}

### claim.evals.traces-before-evals: Traces Before Evals

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

AI evaluation work needs complete traces before evaluators can make trustworthy judgments.

Interpretation notes:
- Testing guidance should ask for trace or artifact capture before judge, dashboard, or metric design.

### claim.evals.judge-validation-needs-tpr-tnr: Judge Validation Needs TPR And TNR

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

LLM judges should be validated with separate true-positive and true-negative rates rather than agreement alone.

Interpretation notes:
- This claim prevents broad judge scores from being laundered into release evidence.

### claim.evals.evals-close-loop: Evals Must Close The Loop

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Eval results are useful only when they drive root-cause analysis, fixes, reruns, and regression checks.

Interpretation notes:
- Testing closeout should include what changed because of the eval result, not only the score.

### claim.evals.measurement-supports-decisions: Measurement Supports Decisions

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Measurement work should be framed around the decision it supports and the uncertainty it reduces.

Interpretation notes:
- Test selection should ask which decision will change if this evidence passes, fails, or remains blocked.

### claim.evals.productivity-requires-goal: Productivity Requires A Goal

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Activity is only productive when it moves the system toward its goal.

Interpretation notes:
- Running more tests is not automatically better; proof should map to the delivery or risk decision being made.

### claim.evals.intuition-needs-observable-justification: Intuition Needs Observable Justification

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Tester intuition is useful as a lead, but bug reports and quality claims need observable justification tied to requirements, client value, or other shared evidence.

Interpretation notes:
- Treat a hunch as a hypothesis to investigate, then report observations and the violated expectation.

### claim.evals.exploration-is-sampling: Exploration Is Sampling

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Testing is sampling, so exploratory thinking remains necessary throughout a test project because no sample can be complete.

Interpretation notes:
- A passing sample should leave an explicit coverage caveat and a next-sample idea when risk remains.

### claim.evals.abduction-guides-test-investigation: Abduction Guides Test Investigation

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Test investigation uses abductive reasoning: gather data, generate explanations, seek evidence that corroborates or refutes them, and continue searching when evidence is insufficient.

Interpretation notes:
- Failed evals should become hypotheses to test, not just scores to optimize.

### claim.evals.coverage-is-multidimensional: Coverage Is Multidimensional

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Coverage evidence is multidimensional; high coverage on one dimension can show incomplete testing, but it does not prove release readiness or broad adequacy.

Interpretation notes:
- Test closeout should report which coverage dimension was exercised and which independent dimensions remain unproven.

## Heuristics

### heuristic.evals.prefer-code-for-objective-checks: Prefer Code For Objective Checks

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.evals.code-evals-are-deterministic, claim.evals.testing-models-can-be-flawed

If the expected property can be checked with code, schema, regex, parser, or exact artifact inspection, choose that before an LLM judge.

Use when:
- The behavior involves format, required fields, prohibited strings, tool-call shape, length, file existence, schema validity, or deterministic state transitions.
- The test needs to be cheap, repeatable, and easy to debug.

Avoid when:
- The target behavior requires nuanced semantic judgment that cannot be reduced to stable rules.
- The deterministic check would merely restate the implementation as its own oracle.
- The deterministic check encodes a weak product model or ignores the user's actual success criteria.

### heuristic.evals.match-proof-method-to-question: Match Proof Method To Question

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.evals.ux-measurement-needs-method-fit, claim.evals.skill-review-is-not-behavior-proof, claim.evals.context-impact-needs-baseline

Pick the eval route from the proof question: structure review, trace error analysis, deterministic check, calibrated judge, baseline-vs-context task eval, repo eval, survey, or online guardrail are different evidence lanes.

Use when:
- A request asks whether an eval, scorer, skill, context package, or RAG answer is good enough.
- The available evidence mixes review scores, local validation, task results, registry metadata, and user perception.

Avoid when:
- The user only needs a narrow deterministic syntax or schema check.
- The decision does not depend on comparing evidence lanes.

## Lenses

### lens.evals.testing-proof-selection: Testing Proof Selection Lens

- Type: lens
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.evals.traces-before-evals, claim.evals.code-evals-are-deterministic, claim.evals.judge-validation-needs-tpr-tnr, claim.evals.evals-close-loop, claim.evals.production-needs-online-guardrails, claim.evals.measurement-supports-decisions, claim.evals.experiments-need-valid-metrics, claim.evals.productivity-requires-goal, claim.evals.testing-models-can-be-flawed, claim.evals.intuition-needs-observable-justification, claim.evals.exploration-is-sampling, claim.evals.abduction-guides-test-investigation, claim.evals.coverage-is-multidimensional

- Tie every proof path to the decision, risk, or goal it is meant to inform.
- Name the model, oracle, or expectation the test is using and what it cannot see.
- Start by asking what observed failure or behavior claim needs proof.
- Treat intuition as a lead; require observable evidence before closeout.
- Prefer deterministic checks for objective properties and calibrated judges for semantic properties.
- Require traces, fixtures, or artifacts before treating eval scores as evidence.
- For experiments, name the primary metric, guardrails, randomization or sampling basis, and instrumentation.
- Report coverage by dimension and preserve caveats when the sample is incomplete.
- Separate measurement evals from online guardrails that prevent high-risk responses.
- Turn fixed failures into regression cases, or record why retention would be unsafe or low-value.
