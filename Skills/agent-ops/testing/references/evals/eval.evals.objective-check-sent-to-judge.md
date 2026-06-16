# eval.evals.objective-check-sent-to-judge: Objective Check Sent To Judge

Given: A test plan sends JSON schema validity, markdown-in-SMS detection, or required-field presence to an LLM judge.
Should: The testing skill recommends deterministic code or schema checks and asks for known good and bad evaluator fixtures.
Expected failure: The testing skill accepts a judge where a stable parser or assertion would be cheaper and more reliable.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
