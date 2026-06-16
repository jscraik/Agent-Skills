# eval.harness.context-dump-instead-of-slice: Context Dump Instead Of Slice

Given: A task needs one validation rule, but the harness loads an entire doctrine corpus and several unrelated skill files.
Should: The agent uses the narrow rule locator or clause ID and follows deeper references only if the task requires them.
Expected failure: The agent treats maximum context as safer even though it crowds out task reasoning and leaves repeated rules unenforced.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.

## Skill-Local Evidence Boundary

Failure category: context-overload validation gap.
Assessment: narrow rule locator first. For this scenario, the relevant evidence is the single validation-rule clause or clause ID that governs the requested check, not broad doctrine corpora, unrelated skill files, or historical notes.
Evidence boundary: this fixture is skill-local evidence at references/evals/eval.harness.context-dump-instead-of-slice.md; it does not by itself prove repository, pull request, remote-check, merge-readiness, or Tessl-readiness outcomes.
Narrow-slice decision: use the rule locator, clause ID, or directly relevant reference first; follow deeper references only when the clause itself requires them or when the first slice is insufficient.
Durable mechanism: add or refresh a rule-locator checklist that records selected clause, searched scope, siblings intentionally skipped, and the reason any deeper references were loaded.
Validation status: blocked until the narrow clause is inspected and the selected scope is recorded; broad repository or Tessl readiness remains outside this fixture's evidence boundary.
