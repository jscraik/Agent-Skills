# eval.evals.score-without-action: Score Without Action

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.evals.score-without-action.md

Knowledge claim: The testing skill reports the score as incomplete proof and asks for the improvement loop evidence before claiming behavior improved.
Behavior under test: The testing skill reports the score as incomplete proof and asks for the improvement loop evidence before claiming behavior improved.
Failure mode: The testing skill treats the score alone as completion evidence.
Expected agent move: The testing skill reports the score as incomplete proof and asks for the improvement loop evidence before claiming behavior improved.
Skill lift before failure: The testing skill treats the score alone as completion evidence.
Skill lift after behavior: The testing skill reports the score as incomplete proof and asks for the improvement loop evidence before claiming behavior improved.
Observable delta: The testing skill reports the score as incomplete proof and asks for the improvement loop evidence before claiming behavior improved.

Given: An eval run produces a score and failure list, but the closeout does not identify root cause, fix path, rerun command, or retained regression case.
Should: The testing skill reports the score as incomplete proof and asks for the improvement loop evidence before claiming behavior improved.
Expected failure: The testing skill treats the score alone as completion evidence.

Bad answer patterns:
- The testing skill treats the score alone as completion evidence.

Good answer patterns:
- The testing skill reports the score as incomplete proof and asks for the improvement loop evidence before claiming behavior improved.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
