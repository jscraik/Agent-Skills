# eval.harness.context-dump-instead-of-slice: Context Dump Instead Of Slice

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.context-dump-instead-of-slice.md

Knowledge claim: Principle under test: The agent uses the narrow rule locator or clause ID and follows deeper references only if the task requires them.
Behavior under test: Observable agent behavior when an task needs one validation rule, but the harness loads an entire doctrine corpus and several unrelated skill files.
Failure mode: The agent treats maximum context as safer even though it crowds out task reasoning and leaves repeated rules unenforced.
Expected agent move: The agent uses the narrow rule locator or clause ID and follows deeper references only if the task requires them.
Skill lift before failure: The agent treats maximum context as safer even though it crowds out task reasoning and leaves repeated rules unenforced.
Skill lift after behavior: The agent uses the narrow rule locator or clause ID and follows deeper references only if the task requires them.
Observable delta: The response avoids the weak pattern (The agent treats maximum context as safer even though it crowds out task reasoning and leaves repeated rules unenforced) and instead shows the expected behavior (The agent uses the narrow rule locator or clause ID and follows deeper references only if the task requires them).

Given: A task needs one validation rule, but the harness loads an entire doctrine corpus and several unrelated skill files.
Should: The agent uses the narrow rule locator or clause ID and follows deeper references only if the task requires them.
Expected failure: The agent treats maximum context as safer even though it crowds out task reasoning and leaves repeated rules unenforced.

Bad answer patterns:
- The agent treats maximum context as safer even though it crowds out task reasoning and leaves repeated rules unenforced.

Good answer patterns:
- The agent uses the narrow rule locator or clause ID and follows deeper references only if the task requires them.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
