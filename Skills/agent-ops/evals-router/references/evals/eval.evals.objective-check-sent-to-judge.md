# eval.evals.objective-check-sent-to-judge: Objective Check Sent To Judge

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.evals.objective-check-sent-to-judge.md

Knowledge claim: The testing skill recommends deterministic code or schema checks and asks for known good and bad evaluator fixtures.
Behavior under test: The testing skill recommends deterministic code or schema checks and asks for known good and bad evaluator fixtures.
Failure mode: The testing skill accepts a judge where a stable parser or assertion would be cheaper and more reliable.
Expected agent move: The testing skill recommends deterministic code or schema checks and asks for known good and bad evaluator fixtures.
Skill lift before failure: The testing skill accepts a judge where a stable parser or assertion would be cheaper and more reliable.
Skill lift after behavior: The testing skill recommends deterministic code or schema checks and asks for known good and bad evaluator fixtures.
Observable delta: The testing skill recommends deterministic code or schema checks and asks for known good and bad evaluator fixtures.

Given: A test plan sends JSON schema validity, markdown-in-SMS detection, or required-field presence to an LLM judge.
Should: The testing skill recommends deterministic code or schema checks and asks for known good and bad evaluator fixtures.
Expected failure: The testing skill accepts a judge where a stable parser or assertion would be cheaper and more reliable.

Bad answer patterns:
- The testing skill accepts a judge where a stable parser or assertion would be cheaper and more reliable.

Good answer patterns:
- The testing skill recommends deterministic code or schema checks and asks for known good and bad evaluator fixtures.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
