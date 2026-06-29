# Deterministic Evaluator Design

Prefer code, schemas, parsers, and known good/bad fixtures for objective behavior checks.

Pack id: pack.evals-testing
Facet id: deterministic_evaluator_design
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

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

### claim.evals.testing-models-can-be-flawed: Testing Models Can Be Flawed

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Tests are designed from testers' models of the product, users, and expected behavior; flawed models produce flawed tests.

Interpretation notes:
- Test plans and evals should name the model or oracle they rely on and record what that model cannot see.

### claim.evals.attack-patterns-exercise-interfaces: Attack Patterns Exercise Interfaces

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Testing attacks can be organized around user-interface black-box inputs and outputs, open-box stored data and feature interactions, and system interfaces such as files and operating systems.

Interpretation notes:
- Eval coverage audits should ask which interface or evidence boundary is being exercised, not just whether a single aggregate score exists.

### claim.evals.input-variation-exposes-failures: Input Variation Exposes Failures

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Targeted input variation can expose failures by forcing error handling, default reset paths, buffer limits, repeated inputs, and interacting input combinations.

Interpretation notes:
- Synthetic cases are most useful when they vary one named failure surface or interaction, then keep the generated probes separate from representative production traces.

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

## Eval Scenarios

### eval.evals.objective-check-sent-to-judge: Objective Check Sent To Judge

- Type: eval-scenario
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.evals.code-evals-are-deterministic, claim.evals.evals-need-known-good-bad-cases

Knowledge claim: Principle under test: The testing skill recommends deterministic code or schema checks and asks for known good and bad evaluator fixtures.
Behavior under test: Observable agent behavior when an test plan sends JSON schema validity, markdown-in-SMS detection, or required-field presence to an LLM judge.
Failure mode: The testing skill accepts a judge where a stable parser or assertion would be cheaper and more reliable.
Expected agent move: The testing skill recommends deterministic code or schema checks and asks for known good and bad evaluator fixtures.
Skill lift target: The response avoids the weak pattern (The testing skill accepts a judge where a stable parser or assertion would be cheaper and more reliable) and instead shows the expected behavior (The testing skill recommends deterministic code or schema checks and asks for known good and bad evaluator fixtures).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.evals.objective-check-sent-to-judge.md
Promotion status: candidate
Capsule refs: evals-testing
Weak eval flags: none

Given: A test plan sends JSON schema validity, markdown-in-SMS detection, or required-field presence to an LLM judge.
Should: The testing skill recommends deterministic code or schema checks and asks for known good and bad evaluator fixtures.
Expected failure: The testing skill accepts a judge where a stable parser or assertion would be cheaper and more reliable.
Reproduce with: references/evals/eval.evals.objective-check-sent-to-judge.md
