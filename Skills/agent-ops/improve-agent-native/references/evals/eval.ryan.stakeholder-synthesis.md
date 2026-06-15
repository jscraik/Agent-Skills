# Eval Fixture: Stakeholder Synthesis

## Input

An agent has a raw log of commits, failing checks, fixed checks, review notes,
and generated artifacts. A product stakeholder asks whether the work is ready.

## Expected Response Requirements

- Summarize current state, decision relevance, and next action.
- Separate local validation, external CI, review, tracker, and merge readiness.
- Include risks and evidence boundaries.
- Avoid dumping raw activity.

## Failure Assertions

- Fails if the response lists command output without synthesis.
- Fails if one proof lane is claimed to prove another without evidence.

## Skill-Local Evidence Boundary

Failure category: seed eval requires behavioural scenario conversion.
Evidence boundary: this fixture is skill-local evidence at references/evals/eval.ryan.stakeholder-synthesis.md; it does not by itself prove repository, pull request, remote-check, merge-readiness, or Tessl-readiness outcomes.
Durable mechanism: use this fixture to generate scenario criteria that require the agent to compress activity into decision-relevant meaning, current state, risks, next action, and evidence boundary without flooding the stakeholder with raw logs.
Validation status: not_run_with_reason until the scenario is executed by the local pipeline and private Tessl eval lane.
