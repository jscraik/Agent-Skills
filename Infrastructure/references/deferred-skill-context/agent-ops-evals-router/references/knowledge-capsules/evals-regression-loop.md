# Regression Loop

Turn eval failures into root-cause fixes, reruns, and retained regression cases before claiming improvement.

Pack id: pack.evals-testing
Facet id: regression_loop
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: reviewed

## Claim Cards

### claim.evals.evals-close-loop: Evals Must Close The Loop

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Eval results are useful only when they drive root-cause analysis, fixes, reruns, and regression checks.

Interpretation notes:
- Testing closeout should include what changed because of the eval result, not only the score.

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

### claim.evals.abduction-guides-test-investigation: Abduction Guides Test Investigation

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Test investigation uses abductive reasoning: gather data, generate explanations, seek evidence that corroborates or refutes them, and continue searching when evidence is insufficient.

Interpretation notes:
- Failed evals should become hypotheses to test, not just scores to optimize.

### claim.evals.coverage-is-multidimensional: Coverage Is Multidimensional

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Coverage evidence is multidimensional; high coverage on one dimension can show incomplete testing, but it does not prove release readiness or broad adequacy.

Interpretation notes:
- Test closeout should report which coverage dimension was exercised and which independent dimensions remain unproven.

## Heuristics

### heuristic.evals.close-loop-through-regressions: Close Loop Through Regressions

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.evals.evals-close-loop, claim.evals.experimentation-discovers-unknowns

Every fixed eval failure or disproven experiment hypothesis should leave behind a regression case or an explicit reason why a durable case is not viable.

Use when:
- A bug, prompt failure, model regression, retrieval defect, or tool-call mismatch has just been fixed.
- An experiment revealed a stable system property that future changes should preserve.
- A closeout report claims an eval-driven improvement.

Avoid when:
- The failure was caused solely by a transient environment outage and has no product behavior to retain.
- The retained case would expose secrets, private traces, or sensitive user content without redaction.

## Eval Scenarios

### eval.evals.score-without-action: Score Without Action

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.evals.evals-close-loop

Given: An eval run produces a score and failure list, but the closeout does not identify root cause, fix path, rerun command, or retained regression case.
Should: The testing skill reports the score as incomplete proof and asks for the improvement loop evidence before claiming behavior improved.
Expected failure: The testing skill treats the score alone as completion evidence.
Reproduce with: references/evals/eval.evals.score-without-action.md
