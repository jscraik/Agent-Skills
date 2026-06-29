# eval.evals.unvalidated-judge-overclaims: Unvalidated Judge Overclaims

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.evals.unvalidated-judge-overclaims.md

Knowledge claim: Principle under test: The testing skill classifies the judge result as advisory or blocked for release proof and asks for calibration evidence before using it as a required gate.
Behavior under test: Observable agent behavior when an plan proposes an LLM judge and reports a high agreement score without held-out test results, false-positive/false-negative counts, or prompt/version artifacts.
Failure mode: The testing skill accepts the agreement score as sufficient validation.
Expected agent move: The testing skill classifies the judge result as advisory or blocked for release proof and asks for calibration evidence before using it as a required gate.
Skill lift before failure: The testing skill accepts the agreement score as sufficient validation.
Skill lift after behavior: The testing skill classifies the judge result as advisory or blocked for release proof and asks for calibration evidence before using it as a required gate.
Observable delta: The response avoids the weak pattern (The testing skill accepts the agreement score as sufficient validation) and instead shows the expected behavior (The testing skill classifies the judge result as advisory or blocked for release proof and asks for calibration evidence before using it as a required gate).

Given: A plan proposes an LLM judge and reports a high agreement score without held-out test results, false-positive/false-negative counts, or prompt/version artifacts.
Should: The testing skill classifies the judge result as advisory or blocked for release proof and asks for calibration evidence before using it as a required gate.
Expected failure: The testing skill accepts the agreement score as sufficient validation.

Bad answer patterns:
- The testing skill accepts the agreement score as sufficient validation.

Good answer patterns:
- The testing skill classifies the judge result as advisory or blocked for release proof and asks for calibration evidence before using it as a required gate.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
