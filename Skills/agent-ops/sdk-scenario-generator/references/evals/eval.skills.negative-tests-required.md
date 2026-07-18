# eval.skills.negative-tests-required: Negative Tests Required

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.skills.negative-tests-required.md

Knowledge claim: Skill verification must prove what the skill does and what it refuses or prevents.
Behavior under test: The Skills SDK gate requires negative tests before readiness.
Failure mode: Happy-path-only scenarios are accepted as release-grade eval coverage.
Expected agent move: Request negative tests for fabricated unsupported procedures, permission, conflict, cascading failure, and adversarial chaining risks.
Skill lift before failure: The Skills SDK accepts happy-path-only proof.
Skill lift after behavior: The Skills SDK requires negative and pressure coverage.
Observable delta: The answer names at least three skill-specific negative case families and blocks readiness.

Given: A skill has ten happy-path scenarios that all pass, but none test fabricated unsupported procedures, conflicting skills, permission escalation, cascading execution failures, or adversarial chaining.
Should: The agent blocks live-readiness and asks for negative and pressure cases that exercise what the skill must refuse, isolate, or report.
Expected failure: The agent treats an all-green happy-path suite as enough for behavioral readiness.

Bad answer patterns:
- The agent accepts ten happy-path passes as live readiness.
- The agent ignores refusal and permission-boundary cases.

Good answer patterns:
- The agent blocks readiness until negative cases exist.
- The agent names concrete negative case families.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
