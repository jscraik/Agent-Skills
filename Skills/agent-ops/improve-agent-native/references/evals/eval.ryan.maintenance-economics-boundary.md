# Eval Fixture: Maintenance Economics Boundary

## Input

An agent proposes a new dependency because it can implement the requested
feature quickly and code generation is cheap.

## Expected Response Requirements

- Evaluate maintenance burden, supply-chain risk, pinning, cooldown policy, and
  toolchain surface area.
- Consider removal, internalization, or avoiding the dependency.
- Tie the recommendation to validation and ownership boundaries.

## Failure Assertions

- Fails if the response treats cheap implementation as sufficient.
- Fails if it expands dependency surface without risk review.

## Skill-Local Evidence Boundary

Failure category: seed eval requires behavioural scenario conversion.
Evidence boundary: this fixture is skill-local evidence at references/evals/eval.ryan.maintenance-economics-boundary.md; it does not by itself prove repository, pull request, remote-check, merge-readiness, or Tessl-readiness outcomes.
Durable mechanism: use this fixture to generate scenario criteria that require the agent to balances maintenance burden, supply-chain risk, pinning, cooldown policy, and replacement options before adding or retaining a dependency.
Validation status: not_run_with_reason until the scenario is executed by the local pipeline and private Tessl eval lane.
