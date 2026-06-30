# Regression Loop

Turn eval failures into root-cause fixes, reruns, and retained regression cases before claiming improvement.

Pack id: pack.evals-testing
Facet id: regression_loop
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.evals.evals-close-loop: Evals Must Close The Loop

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Eval results are useful only when they drive root-cause analysis, fixes, reruns, and regression checks.

Interpretation notes:
- Testing closeout should include what changed because of the eval result, not only the score.

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

### claim.evals.exploration-is-rapid-experimentation: Exploration Is Rapid Experimentation

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Exploratory testing designs and executes small experiments, then uses what was just learned to shape the next experiment.

Interpretation notes:
- {"Eval routing should preserve learning loops"=>"a failed trace or surprising output should shape the next targeted probe rather than trigger a generic metric dashboard."}

### claim.evals.charters-focus-exploration: Charters Focus Exploration

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Exploration charters focus a session by naming what to explore, the resources or constraints to use, and the information to discover.

Interpretation notes:
- Synthetic eval cases should be chartered by a named gap, constraint, and discovery target instead of generated as broad representative coverage.

### claim.evals.input-variation-exposes-failures: Input Variation Exposes Failures

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Targeted input variation can expose failures by forcing error handling, default reset paths, buffer limits, repeated inputs, and interacting input combinations.

Interpretation notes:
- Synthetic cases are most useful when they vary one named failure surface or interaction, then keep the generated probes separate from representative production traces.

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

### claim.evals.scorers-need-obvious-case-calibration: Scorers Need Obvious Case Calibration

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Eval score trends are not trustworthy until the scorer passes obvious correct and incorrect cases.

Interpretation notes:
- Treat score changes without scorer calibration as diagnostic input, not readiness evidence.

### claim.evals.subjective-quality-needs-human-review: Subjective Quality Needs Human Review

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Subjective quality dimensions should use human review until their labels are stable enough to automate.

Interpretation notes:
- Use this to prevent brittle automation from replacing necessary human judgment.

### claim.evals.ux-measurement-needs-method-fit: UX Measurement Needs Method Fit

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

User-experience evaluation can combine qualitative and quantitative methods, and measurement should be chosen to fit the insight needed about user perception and system improvement.

Interpretation notes:
- {"Eval route selection should match the decision"=>"qualitative trace review, deterministic checks, calibrated judges, surveys, or online guardrails answer different questions."}

### claim.evals.skill-review-is-not-behavior-proof: Skill Review Is Not Behavior Proof

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Skill review checks structure and quality, while task and repo evals test whether context improves behavior on scenarios or realistic repository changes.

Interpretation notes:
- Evals-router should not treat a static review score as proof that a skill improves behavior.

## Principles

### principle.evals.production-failure-loop: Production Failure Loop

- Type: principle
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.evals.production-clusters-seed-targeted-datasets, claim.evals.scorers-need-obvious-case-calibration, claim.evals.online-offline-loop-closes-coverage-gap, claim.evals.subjective-quality-needs-human-review

Treat eval quality as a loop from observed traces to targeted datasets, calibrated scorers, baseline comparisons, focused fixes, and post-deploy monitoring.

Rationale: This keeps eval work attached to real behavior, separates scorer validity from model quality, and prevents a one-off offline score from becoming an overclaimed production-readiness signal.

Application notes:
- Start from traces or a clearly stated production-risk proxy.
- Convert clusters into replayable datasets before scoring a fix.
- Validate scorers before trusting score trends.
- Feed post-deploy failures back into the offline suite.

## Heuristics

### heuristic.evals.close-loop-through-regressions: Close Loop Through Regressions

- Type: heuristic
- Status: draft
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

### heuristic.evals.cluster-to-dataset-before-fix: Cluster To Dataset Before Fix

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.evals.production-clusters-seed-targeted-datasets, claim.evals.online-offline-loop-closes-coverage-gap

When a production issue appears in traces, first name the cluster and preserve representative cases as a replayable dataset; then score the targeted fix against a recorded baseline.

Use when:
- A dashboard, trace search, topic cluster, support queue, or reviewer note reveals repeated AI behavior failures.
- The team is tempted to patch a prompt or scorer directly from a few memorable examples.

Avoid when:
- The failure is a single deterministic code defect with an existing unit-test route.
- No trace, log, or reproducible interaction can be preserved without exposing sensitive data.

## Checklists

### checklist.evals.production-failure-to-regression: Production Failure To Regression Checklist

- Type: checklist
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.evals.production-clusters-seed-targeted-datasets, claim.evals.scorers-need-obvious-case-calibration, claim.evals.online-offline-loop-closes-coverage-gap, claim.evals.subjective-quality-needs-human-review

- [ ] Identify the live trace, log query, review note, or production-risk proxy that exposed the issue.
- [ ] Cluster similar failures by task, intent, sentiment, issue, or domain-specific facet.
- [ ] Manually inspect a bounded sample and write concrete failure modes before automating.
- [ ] Convert representative failures into a small replayable dataset with sensitive data removed.
- [ ] Choose deterministic code checks for objective requirements and human review for subjective dimensions.
- [ ] Validate each scorer on obvious pass and fail cases before trusting aggregate movement.
- [ ] Record the baseline run, experiment, commit, prompt version, model, and dataset snapshot.
- [ ] Make one targeted change when causal understanding matters.
- [ ] Compare the new run against the baseline for target improvement and unrelated regressions.
- [ ] Preserve unresolved failures as regression cases or explicitly document why they are out of scope.
- [ ] After deployment, monitor fresh production traces and feed new failures back into the dataset.

## Eval Scenarios

### eval.evals.score-without-action: Score Without Action

- Type: eval-scenario
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.evals.evals-close-loop

Knowledge claim: Principle under test: The testing skill reports the score as incomplete proof and asks for the improvement loop evidence before claiming behavior improved.
Behavior under test: Observable agent behavior when an eval run produces a score and failure list, but the closeout does not identify root cause, fix path, rerun command, or retained regression case.
Failure mode: The testing skill treats the score alone as completion evidence.
Expected agent move: The testing skill reports the score as incomplete proof and asks for the improvement loop evidence before claiming behavior improved.
Skill lift target: The response avoids the weak pattern (The testing skill treats the score alone as completion evidence) and instead shows the expected behavior (The testing skill reports the score as incomplete proof and asks for the improvement loop evidence before claiming behavior improved).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.evals.score-without-action.md
Promotion status: candidate
Capsule refs: evals-testing
Weak eval flags: none

Given: An eval run produces a score and failure list, but the closeout does not identify root cause, fix path, rerun command, or retained regression case.
Should: The testing skill reports the score as incomplete proof and asks for the improvement loop evidence before claiming behavior improved.
Expected failure: The testing skill treats the score alone as completion evidence.
Reproduce with: references/evals/eval.evals.score-without-action.md
