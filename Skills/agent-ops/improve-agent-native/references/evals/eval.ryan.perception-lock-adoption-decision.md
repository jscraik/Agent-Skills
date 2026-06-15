# Perception Lock Adoption Decision Fixture

Users keep using a current coding agent as an interactive pair-programming
assistant and avoid delegated, longer-horizon work. A team asks whether the
problem is user education, stale market priors, or real product reliability.

Expected behavior:

- Check current capability evidence before making adoption claims.
- Distinguish stale priors from genuine product reliability gaps.
- Propose in-product examples, workflow education, or onboarding changes tied
  to the observed gap.
- Define adoption metrics that show whether users are moving to current
  capability patterns.
- Avoid overclaiming unsupported capability.

## Skill-Local Evidence Boundary

Failure category: seed eval requires behavioural scenario conversion.
Evidence boundary: this fixture is skill-local evidence at references/evals/eval.ryan.perception-lock-adoption-decision.md; it does not by itself prove repository, pull request, remote-check, merge-readiness, or Tessl-readiness outcomes.
Durable mechanism: use this fixture to generate scenario criteria that require the agent to distinguishes stale capability priors from current reliability evidence, proposes product examples or workflow education, defines adoption metrics, and avoids unsupported adoption claims.
Validation status: not_run_with_reason until the scenario is executed by the local pipeline and private Tessl eval lane.
