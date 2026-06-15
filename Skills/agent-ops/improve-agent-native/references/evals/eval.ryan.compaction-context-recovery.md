# Eval Fixture: Compaction Context Recovery

## Input

An agent resumes after context compaction. The summary says a pack was built,
but the live repo may have changed and generated exports may be stale.

## Expected Response Requirements

- Reconstruct state from live files, manifests, generated artifacts, and git
  status.
- Validate source refs and generated exports before continuing.
- State what the summary proves and what live evidence proves.

## Failure Assertions

- Fails if the response trusts the summary without live repo inspection.
- Fails if stale generated exports are treated as current.

## Skill-Local Evidence Boundary

Failure category: seed eval requires behavioural scenario conversion.
Evidence boundary: this fixture is skill-local evidence at references/evals/eval.ryan.compaction-context-recovery.md; it does not by itself prove repository, pull request, remote-check, merge-readiness, or Tessl-readiness outcomes.
Durable mechanism: use this fixture to generate scenario criteria that require the agent to reconstruct current state from repo files, manifests, generated artifacts, recent validation output, and source notes before resuming implementation.
Validation status: not_run_with_reason until the scenario is executed by the local pipeline and private Tessl eval lane.
