# eval.evals.score-without-action: Score Without Action

Given: An eval run produces a score and failure list, but the closeout does not identify root cause, fix path, rerun command, or retained regression case.
Should: The testing skill reports the score as incomplete proof and asks for the improvement loop evidence before claiming behavior improved.
Expected failure: The testing skill treats the score alone as completion evidence.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
