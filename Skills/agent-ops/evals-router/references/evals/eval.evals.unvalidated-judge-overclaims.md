# eval.evals.unvalidated-judge-overclaims: Unvalidated Judge Overclaims

Given: A plan proposes an LLM judge and reports a high agreement score without held-out test results, false-positive/false-negative counts, or prompt/version artifacts.
Should: The testing skill classifies the judge result as advisory or blocked for release proof and asks for calibration evidence before using it as a required gate.
Expected failure: The testing skill accepts the agreement score as sufficient validation.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
