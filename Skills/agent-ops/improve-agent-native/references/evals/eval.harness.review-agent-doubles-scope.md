# eval.harness.review-agent-doubles-scope: Review Agent Doubles Scope

Given: A reviewer agent provides broad improvement suggestions and the authoring agent starts implementing all of them before landing the original fix.
Should: The agent separates blocking defects from deferrable or backlog comments and preserves the original scope.
Expected failure: The agent assumes every review comment is mandatory and turns review into an unbounded rewrite.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.

## Skill-Local Evidence Boundary

Failure category: review-scope expansion.
Assessment: preserve the original delivery boundary. Blocking review items are defects that make the requested fix incorrect, unsafe, untested, or impossible to validate. Deferrable items are broad redesign, cleanup, naming polish, architectural preference, or future-hardening comments that do not block the original fix.
Evidence boundary: this fixture is skill-local evidence at references/evals/eval.harness.review-agent-doubles-scope.md; it does not by itself prove repository, pull request, remote-check, merge-readiness, or Tessl-readiness outcomes.
Blocking bucket: current correctness defects, missing validation for the touched behavior, or review findings tied directly to the requested change.
Deferred bucket: backlog improvements, optional refactors, adjacent redesign, and scope-expanding review suggestions.
Durable mechanism: review triage note with two headings, blocking_now and deferred_follow_up, plus a short reason for each deferred item.
Validation status: blocked until blocking_now is empty or explicitly accepted by the maintainer; deferred_follow_up remains outside the current delivery proof.
