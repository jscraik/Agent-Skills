# Eval Fixture: Repeated Steering To Durable Mechanism

## Input

A reviewer says: "This is the third time I have told agents not to hand-edit
generated exports. Fix this instance."

## Expected Response Requirements

- Identify the repeated steering as an environment failure.
- Name the durable surface that should change.
- Propose or apply the smallest guardrail, validator, instruction, or fixture.
- Preserve unrelated work and state any skip reason if no durable change is safe.

## Failure Assertions

- Fails if the response only edits the current file.
- Fails if the response treats repeated feedback as ordinary one-off steering.

## Skill-Local Evidence Boundary

Failure category: seed eval requires behavioural scenario conversion.
Evidence boundary: this fixture is skill-local evidence at references/evals/eval.ryan.repeated-steering-to-durable-mechanism.md; it does not by itself prove repository, pull request, remote-check, merge-readiness, or Tessl-readiness outcomes.
Durable mechanism: use this fixture to generate scenario criteria that require the agent to identifies recurrence, classifies the failure, recommends the smallest repo mechanism, and records either the concrete patch or a bounded skip reason.
Validation status: not_run_with_reason until the scenario is executed by the local pipeline and private Tessl eval lane.
