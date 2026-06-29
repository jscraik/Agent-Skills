# eval.harness.feedback-recurs-without-guardrail: Repeated Feedback Needs Durable Capture

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.feedback-recurs-without-guardrail.md

Knowledge claim: Principle under test: The agent classifies the repeated failure and proposes a durable guardrail, test, fixture, instruction route, or skip reason.
Behavior under test: Observable agent behavior when an reviewer repeats the same correction that appeared in an earlier agent task.
Failure mode: The agent applies another one-off fix without addressing recurrence.
Expected agent move: The agent classifies the repeated failure and proposes a durable guardrail, test, fixture, instruction route, or skip reason.
Skill lift before failure: The agent applies another one-off fix without addressing recurrence.
Skill lift after behavior: The agent classifies the repeated failure and proposes a durable guardrail, test, fixture, instruction route, or skip reason.
Observable delta: The response avoids the weak pattern (The agent applies another one-off fix without addressing recurrence) and instead shows the expected behavior (The agent classifies the repeated failure and proposes a durable guardrail, test, fixture, instruction route, or skip reason).

Given: A reviewer repeats the same correction that appeared in an earlier agent task.
Should: The agent classifies the repeated failure and proposes a durable guardrail, test, fixture, instruction route, or skip reason.
Expected failure: The agent applies another one-off fix without addressing recurrence.

Bad answer patterns:
- The agent applies another one-off fix without addressing recurrence.

Good answer patterns:
- The agent classifies the repeated failure and proposes a durable guardrail, test, fixture, instruction route, or skip reason.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
