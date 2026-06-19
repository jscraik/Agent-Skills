# Judge Calibration

Treat LLM judges as calibrated instruments that need labeled splits, TPR/TNR, reproducible artifacts, and uncertainty boundaries.

Pack id: pack.evals-testing
Facet id: judge_calibration
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: reviewed

## Claim Cards

### claim.evals.judge-validation-needs-tpr-tnr: Judge Validation Needs TPR And TNR

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

LLM judges should be validated with separate true-positive and true-negative rates rather than agreement alone.

Interpretation notes:
- This claim prevents broad judge scores from being laundered into release evidence.

### claim.evals.corrected-rates-need-intervals: Corrected Rates Need Intervals

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

When judge predictions are used to estimate production quality, reports should account for judge error and include confidence intervals.

Interpretation notes:
- This claim supports uncertainty-aware eval reporting.

### claim.evals.experiments-need-valid-metrics: Experiments Need Valid Metrics

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Controlled experiments need a clear objective metric, proper randomization, instrumentation, and guardrail checks before their results are trustworthy.

Interpretation notes:
- Eval reports should name primary metrics and guardrails rather than reporting a single isolated score.

### claim.evals.code-evals-are-deterministic: Code Evals Are Deterministic

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Code-based evaluators are fast, cheap, deterministic, and appropriate for objective checks.

Interpretation notes:
- The testing skill should prefer code or schema checks when the property is objective.

### claim.evals.evals-need-known-good-bad-cases: Evals Need Known Good And Bad Cases

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Evaluators themselves should be tested against known passing and failing cases before they are trusted.

Interpretation notes:
- Eval code should not become its own untested oracle.

### claim.evals.experimentation-discovers-unknowns: Experimentation Discovers Unknowns

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Tests assert known properties; experiments create new knowledge by challenging hypotheses about system behavior.

Interpretation notes:
- The testing skill should classify whether a proof path is checking a known property or exploring an unknown behavior.

## Principles

### principle.evals.evaluators-are-tested-artifacts: Evaluators Are Tested Artifacts

- Type: principle
- Status: reviewed
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
- Status: reviewed
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

## Rubrics

### rubric.evals.judge-readiness: Judge Readiness Rubric

- Type: rubric
- Status: reviewed
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

## Eval Scenarios

### eval.evals.unvalidated-judge-overclaims: Unvalidated Judge Overclaims

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.evals.judge-validation-needs-tpr-tnr, claim.evals.corrected-rates-need-intervals

Given: A plan proposes an LLM judge and reports a high agreement score without held-out test results, false-positive/false-negative counts, or prompt/version artifacts.
Should: The testing skill classifies the judge result as advisory or blocked for release proof and asks for calibration evidence before using it as a required gate.
Expected failure: The testing skill accepts the agreement score as sufficient validation.
Reproduce with: references/evals/eval.evals.unvalidated-judge-overclaims.md
