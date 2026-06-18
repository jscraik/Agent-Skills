# eval.arch.integration-boundary-without-failure-contract: Integration Boundary Without Failure Contract

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.arch.integration-boundary-without-failure-contract.md

Knowledge claim: The reviewer refuses to call the boundary stable and asks for a message contract, failure contract, and deterministic contract fixture.
Behavior under test: The reviewer refuses to call the boundary stable and asks for a message contract, failure contract, and deterministic contract fixture.
Failure mode: The reviewer treats a successful local tool call as enough proof that the integration design is sound.
Expected agent move: The reviewer refuses to call the boundary stable and asks for a message contract, failure contract, and deterministic contract fixture.
Skill lift before failure: The reviewer treats a successful local tool call as enough proof that the integration design is sound.
Skill lift after behavior: The reviewer refuses to call the boundary stable and asks for a message contract, failure contract, and deterministic contract fixture.
Observable delta: The reviewer refuses to call the boundary stable and asks for a message contract, failure contract, and deterministic contract fixture.

Given: A proposed MCP, plugin, hook, API, or queue boundary forwards payloads successfully on the happy path but has no schema owner, idempotency rule, retry behavior, correlation id, or classified failure output.
Should: The reviewer refuses to call the boundary stable and asks for a message contract, failure contract, and deterministic contract fixture.
Expected failure: The reviewer treats a successful local tool call as enough proof that the integration design is sound.

Bad answer patterns:
- The reviewer treats a successful local tool call as enough proof that the integration design is sound.

Good answer patterns:
- The reviewer refuses to call the boundary stable and asks for a message contract, failure contract, and deterministic contract fixture.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
