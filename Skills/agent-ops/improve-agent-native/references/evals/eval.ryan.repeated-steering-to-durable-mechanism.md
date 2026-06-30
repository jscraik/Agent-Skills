# eval.ryan.repeated-steering-to-durable-mechanism: Repeated Steering Becomes A Durable Mechanism

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.ryan.repeated-steering-to-durable-mechanism.md

Knowledge claim: Principle under test: The agent identifies the recurrence, names the failure class, proposes the smallest durable repo mechanism, and records either the patch or a bounded skip reason.
Behavior under test: Observable agent behavior when an user repeats the same correction across two agent tasks in a repository.
Failure mode: The agent applies another one-off fix and treats the repeated feedback as ordinary task steering.
Expected agent move: The agent identifies the recurrence, names the failure class, proposes the smallest durable repo mechanism, and records either the patch or a bounded skip reason.
Skill lift before failure: The agent applies another one-off fix and treats the repeated feedback as ordinary task steering.
Skill lift after behavior: The agent identifies the recurrence, names the failure class, proposes the smallest durable repo mechanism, and records either the patch or a bounded skip reason.
Observable delta: The response avoids the weak pattern (The agent applies another one-off fix and treats the repeated feedback as ordinary task steering) and instead shows the expected behavior (The agent identifies the recurrence, names the failure class, proposes the smallest durable repo mechanism, and records either the patch or a bounded skip reason).

Given: A user repeats the same correction across two agent tasks in a repository.
Should: The agent identifies the recurrence, names the failure class, proposes the smallest durable repo mechanism, and records either the patch or a bounded skip reason.
Expected failure: The agent applies another one-off fix and treats the repeated feedback as ordinary task steering.

Bad answer patterns:
- The agent applies another one-off fix and treats the repeated feedback as ordinary task steering.

Good answer patterns:
- The agent identifies the recurrence, names the failure class, proposes the smallest durable repo mechanism, and records either the patch or a bounded skip reason.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
