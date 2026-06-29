# Judge Calibration

Treat LLM judges as calibrated instruments that need labeled splits, TPR/TNR, reproducible artifacts, and uncertainty boundaries.

Pack id: pack.evals-testing
Facet id: judge_calibration
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.evals.judge-validation-needs-tpr-tnr: Judge Validation Needs TPR And TNR

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

LLM judges should be validated with separate true-positive and true-negative rates rather than agreement alone.

Interpretation notes:
- This claim prevents broad judge scores from being laundered into release evidence.

### claim.evals.corrected-rates-need-intervals: Corrected Rates Need Intervals

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

When judge predictions are used to estimate production quality, reports should account for judge error and include confidence intervals.

Interpretation notes:
- This claim supports uncertainty-aware eval reporting.

### claim.evals.experiments-need-valid-metrics: Experiments Need Valid Metrics

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Controlled experiments need a clear objective metric, proper randomization, instrumentation, and guardrail checks before their results are trustworthy.

Interpretation notes:
- Eval reports should name primary metrics and guardrails rather than reporting a single isolated score.

### claim.evals.ueq-separates-quality-dimensions: UEQ Separates Quality Dimensions

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

UEQ separates user experience into dimensions such as attractiveness, efficiency, perspicuity, dependability, stimulation, and novelty, with pragmatic and hedonic quality groups.

Interpretation notes:
- Broad quality judges should be split into narrower binary or dimensional checks before being used as release evidence.

### claim.evals.skill-review-is-not-behavior-proof: Skill Review Is Not Behavior Proof

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Skill review checks structure and quality, while task and repo evals test whether context improves behavior on scenarios or realistic repository changes.

Interpretation notes:
- Evals-router should not treat a static review score as proof that a skill improves behavior.

### claim.evals.scorers-need-obvious-case-calibration: Scorers Need Obvious Case Calibration

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Eval score trends are not trustworthy until the scorer passes obvious correct and incorrect cases.

Interpretation notes:
- Treat score changes without scorer calibration as diagnostic input, not readiness evidence.

### claim.evals.code-evals-are-deterministic: Code Evals Are Deterministic

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Code-based evaluators are fast, cheap, deterministic, and appropriate for objective checks.

Interpretation notes:
- The testing skill should prefer code or schema checks when the property is objective.

### claim.evals.evals-need-known-good-bad-cases: Evals Need Known Good And Bad Cases

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Evaluators themselves should be tested against known passing and failing cases before they are trusted.

Interpretation notes:
- Eval code should not become its own untested oracle.

### claim.evals.experimentation-discovers-unknowns: Experimentation Discovers Unknowns

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Tests assert known properties; experiments create new knowledge by challenging hypotheses about system behavior.

Interpretation notes:
- The testing skill should classify whether a proof path is checking a known property or exploring an unknown behavior.

### claim.evals.ux-measurement-needs-method-fit: UX Measurement Needs Method Fit

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

User-experience evaluation can combine qualitative and quantitative methods, and measurement should be chosen to fit the insight needed about user perception and system improvement.

Interpretation notes:
- {"Eval route selection should match the decision"=>"qualitative trace review, deterministic checks, calibrated judges, surveys, or online guardrails answer different questions."}

### claim.evals.context-impact-needs-baseline: Context Impact Needs Baseline

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Task evals for skill or context impact should compare behavior with and without the added context while holding the rest of the run constant.

Interpretation notes:
- Claims that a knowledge capsule, skill, or registry tile helped should keep baseline behavior, with-context behavior, and publication metadata separate.

### claim.evals.production-clusters-seed-targeted-datasets: Production Clusters Seed Targeted Datasets

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Production or production-like trace clusters should seed targeted eval datasets before a fix is scored.

Interpretation notes:
- Use this to resist writing generic synthetic edge cases before inspecting observed failure clusters.

### claim.evals.online-offline-loop-closes-coverage-gap: Online Offline Loop Closes Coverage Gap

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Offline evals and production monitoring should feed each other so test coverage follows live user behavior.

Interpretation notes:
- Use this when dashboard findings need to become durable dataset rows or regression cases.

### claim.evals.subjective-quality-needs-human-review: Subjective Quality Needs Human Review

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Subjective quality dimensions should use human review until their labels are stable enough to automate.

Interpretation notes:
- Use this to prevent brittle automation from replacing necessary human judgment.

## Principles

### principle.evals.evaluators-are-tested-artifacts: Evaluators Are Tested Artifacts

- Type: principle
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.evals.code-evals-are-deterministic, claim.evals.evals-need-known-good-bad-cases, claim.evals.experimentation-discovers-unknowns

Treat evaluator code, judge prompts, fixtures, and metrics as testable artifacts with their own proof requirements.

Rationale: An untested evaluator can create stronger false confidence than having no evaluator at all, and experiments that reveal new behavior should be translated into durable tests when the property becomes known.

Application notes:
- Include known passing and failing fixtures for evaluator behavior.
- Record judge prompt version, dataset split, run count, and calibration metrics.
- Do not use an evaluator as release proof until its own failure modes are checked.
- Preserve newly discovered properties as regression checks when they become stable expectations.

## Heuristics

### heuristic.evals.calibrate-judge-before-scale: Calibrate Judge Before Scale

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.evals.judge-validation-needs-tpr-tnr, claim.evals.corrected-rates-need-intervals

Before running an LLM judge at scale, validate it on held-out labels and require both failure-catching and false-alarm behavior to be acceptable.

Use when:
- A test plan proposes LLM-as-judge, reviewer-as-judge, or model-scored evals.
- The release claim depends on pass rates from unlabeled traces or generated outputs.

Avoid when:
- The judge is used only for exploratory triage and is clearly reported as advisory.
- No ground truth labels or held-out examples exist yet; first build the labeled set.

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

## Rubrics

### rubric.evals.judge-readiness: Judge Readiness Rubric

- Type: rubric
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.evals.judge-validation-needs-tpr-tnr, claim.evals.corrected-rates-need-intervals

- split-discipline: Did the judge use separate train, dev, and held-out test sets?
  - pass: Prompt iteration happened on train/dev material and final metrics used a held-out test set once.
  - fail: The same labels were used for prompt design and final readiness claims.
- confusion-matrix: Are false positives and false negatives visible?
  - pass: The report includes TP, TN, FP, FN or equivalent TPR/TNR evidence.
  - fail: The report relies on agreement, average score, or examples without error-rate breakdown.
- prompt-version: Can the judge run be reproduced?
  - pass: Prompt version, model, dataset, thresholds, command, and raw artifact path are recorded.
  - fail: The judge is described in prose without enough details to rerun.
- uncertainty: Does production reporting account for judge error?
  - pass: Reported rates include calibration limits, confidence intervals, or an explicit advisory-only boundary.
  - fail: Raw judge pass rate is presented as true production quality.

### rubric.evals.production-loop-readiness: Production Loop Readiness

- Type: rubric
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.evals.production-clusters-seed-targeted-datasets, claim.evals.scorers-need-obvious-case-calibration, claim.evals.online-offline-loop-closes-coverage-gap, claim.evals.subjective-quality-needs-human-review

- source-of-failures: Does the eval set come from observed or realistically simulated behavior with preserved trace context?
  - pass: The dataset is linked to trace clusters, logs, review labels, or a documented production-risk proxy.
  - fail: The dataset is mostly imagined examples with no connection to observed failures or live risk.
- scorer-calibration: Are scorer outputs validated before aggregate trends are trusted?
  - pass: Scorers have obvious pass and fail cases, bias checks, and a documented choice between code, judge, and human review.
  - fail: The report trusts score movement without proving that the scorer measures the intended behavior.
- baseline-comparison: Can the change be compared against a recorded baseline?
  - pass: The baseline run, dataset snapshot, model or prompt version, and changed variable are recorded.
  - fail: The improvement claim relies on memory, approximate before/after comparison, or multiple simultaneous changes.
- loop-closure: Do production findings feed future offline coverage?
  - pass: New live failures are promoted into datasets, regression cases, or documented follow-up scope.
  - fail: Production monitoring remains a dashboard-only signal that does not change the eval suite.

## Eval Scenarios

### eval.evals.unvalidated-judge-overclaims: Unvalidated Judge Overclaims

- Type: eval-scenario
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.evals.judge-validation-needs-tpr-tnr, claim.evals.corrected-rates-need-intervals

Knowledge claim: Principle under test: The testing skill classifies the judge result as advisory or blocked for release proof and asks for calibration evidence before using it as a required gate.
Behavior under test: Observable agent behavior when an plan proposes an LLM judge and reports a high agreement score without held-out test results, false-positive/false-negative counts, or prompt/version artifacts.
Failure mode: The testing skill accepts the agreement score as sufficient validation.
Expected agent move: The testing skill classifies the judge result as advisory or blocked for release proof and asks for calibration evidence before using it as a required gate.
Skill lift target: The response avoids the weak pattern (The testing skill accepts the agreement score as sufficient validation) and instead shows the expected behavior (The testing skill classifies the judge result as advisory or blocked for release proof and asks for calibration evidence before using it as a required gate).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.evals.unvalidated-judge-overclaims.md
Promotion status: candidate
Capsule refs: evals-testing
Weak eval flags: none

Given: A plan proposes an LLM judge and reports a high agreement score without held-out test results, false-positive/false-negative counts, or prompt/version artifacts.
Should: The testing skill classifies the judge result as advisory or blocked for release proof and asks for calibration evidence before using it as a required gate.
Expected failure: The testing skill accepts the agreement score as sufficient validation.
Reproduce with: references/evals/eval.evals.unvalidated-judge-overclaims.md
