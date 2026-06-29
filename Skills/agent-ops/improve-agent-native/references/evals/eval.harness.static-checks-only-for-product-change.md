# eval.harness.static-checks-only-for-product-change: Static Checks Only For Product Change

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.static-checks-only-for-product-change.md

Knowledge claim: Principle under test: The agent reports static checks as partial proof and names the missing product-facing evidence.
Behavior under test: Observable agent behavior when an UI or API behavior changes and static tests pass, but no product-facing smoke, screenshot, API call, log, or generated artifact is inspected.
Failure mode: The agent claims user-visible behavior is verified because lint and unit tests passed.
Expected agent move: The agent reports static checks as partial proof and names the missing product-facing evidence.
Skill lift before failure: The agent claims user-visible behavior is verified because lint and unit tests passed.
Skill lift after behavior: The agent reports static checks as partial proof and names the missing product-facing evidence.
Observable delta: The response avoids the weak pattern (The agent claims user-visible behavior is verified because lint and unit tests passed) and instead shows the expected behavior (The agent reports static checks as partial proof and names the missing product-facing evidence).

Given: A UI or API behavior changes and static tests pass, but no product-facing smoke, screenshot, API call, log, or generated artifact is inspected.
Should: The agent reports static checks as partial proof and names the missing product-facing evidence.
Expected failure: The agent claims user-visible behavior is verified because lint and unit tests passed.

Bad answer patterns:
- The agent claims user-visible behavior is verified because lint and unit tests passed.

Good answer patterns:
- The agent reports static checks as partial proof and names the missing product-facing evidence.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
