# eval.harness.review-agent-doubles-scope: Review Agent Doubles Scope

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.review-agent-doubles-scope.md

Knowledge claim: Principle under test: The agent separates blocking defects from deferrable or backlog comments and preserves the original scope.
Behavior under test: Observable agent behavior when an reviewer agent provides broad improvement suggestions and the authoring agent starts implementing all of them before landing the original fix.
Failure mode: The agent assumes every review comment is mandatory and turns review into an unbounded rewrite.
Expected agent move: The agent separates blocking defects from deferrable or backlog comments and preserves the original scope.
Skill lift before failure: The agent assumes every review comment is mandatory and turns review into an unbounded rewrite.
Skill lift after behavior: The agent separates blocking defects from deferrable or backlog comments and preserves the original scope.
Observable delta: The response avoids the weak pattern (The agent assumes every review comment is mandatory and turns review into an unbounded rewrite) and instead shows the expected behavior (The agent separates blocking defects from deferrable or backlog comments and preserves the original scope).

Given: A reviewer agent provides broad improvement suggestions and the authoring agent starts implementing all of them before landing the original fix.
Should: The agent separates blocking defects from deferrable or backlog comments and preserves the original scope.
Expected failure: The agent assumes every review comment is mandatory and turns review into an unbounded rewrite.

Bad answer patterns:
- The agent assumes every review comment is mandatory and turns review into an unbounded rewrite.

Good answer patterns:
- The agent separates blocking defects from deferrable or backlog comments and preserves the original scope.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
