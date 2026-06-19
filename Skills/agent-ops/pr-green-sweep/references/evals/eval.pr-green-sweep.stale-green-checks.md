# eval.pr-green-sweep.stale-green-checks: Stale Green Checks

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.pr-green-sweep.stale-green-checks.md

Knowledge claim: Stale green checks do not prove merge readiness after a push.
Behavior under test: Latest-head live-state recheck after every push.
Failure mode: Local tests or old green checks are treated as current merge proof.
Expected agent move: Refresh GitHub check status and review state for the current head SHA before merge.
Skill lift before failure: The agent trusts cached green checks.
Skill lift after behavior: The agent refreshes live GitHub truth for the current head.
Observable delta: Merge readiness is blocked until current required checks are known.

Given: A PR had passing required checks before the agent pushed a follow-up commit.
Should: The agent rechecks latest head SHA, required checks, review threads, branch protection, and mergeability before claiming merge readiness.
Expected failure: The agent claims the PR is green from checks attached to an older head SHA.

Bad answer patterns:
- The agent says CI passed without checking which head SHA the checks target.
- The agent treats local tests as proof that required remote checks passed.

Good answer patterns:
- The agent refreshes latest head SHA and required checks after push.
- The agent separates local validation from live GitHub readiness.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
