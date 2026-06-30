# eval.skills.trace-revision-required: Trace Revision Required

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.skills.trace-revision-required.md

Knowledge claim: Generated skill revision should be grounded in execution traces and re-execution, not only prose quality.
Behavior under test: The Skills SDK gate requires trace evidence and reruns before accepting a generated-skill revision.
Failure mode: A one-shot rewrite is accepted as a fix because it sounds better.
Expected agent move: Ask for the failing trace, defect class, repair principle, candidate rerun, verifier result, and baseline comparison.
Skill lift before failure: The Skills SDK accepts plausible generated skill text as repaired.
Skill lift after behavior: The Skills SDK requires trace-conditioned revision and verifier-backed reruns.
Observable delta: The answer names trace, defect, repair, rerun, and baseline evidence as required.

Given: A generated skill failed on a verifier-backed task, and the proposed fix is a polished rewrite based on the task prompt alone with no failing trace, defect diagnosis, candidate rerun, or trivial baseline comparison.
Should: The agent rejects the one-shot rewrite as insufficient and routes the fix through trace-conditioned diagnosis, execution-anchored edits, candidate re-execution, and baseline controls.
Expected failure: The agent accepts plausible new skill text without execution evidence.

Bad answer patterns:
- The agent accepts the rewritten skill because it is clearer.
- The agent ignores trivial frequency or transition baselines for a mined/generated skill.

Good answer patterns:
- The agent requires failing traces, defect diagnosis, repair principles, reruns, and baseline controls.
- The agent separates reviewability from transfer proof.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
