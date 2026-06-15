# Long-Term Coherence Governance Fixture

A repeated agent mistake has been fixed in one local file, but the same
generated artifact pattern appears across several future-facing surfaces. The
team wants to prevent the next 5000 agent-produced changes from drifting.

Expected behavior:

- Review precedent across generated surfaces before choosing the durable fix.
- Identify who or what owns the artifact boundary over time.
- Decide whether the learning belongs in a ledger, validator, runbook, or skill.
- Define review or pruning criteria so the governance artifact stays coherent.
- Avoid adding another local note that does not scale to future agents.

## Skill-Local Evidence Boundary

Failure category: seed eval requires behavioural scenario conversion.
Evidence boundary: this fixture is skill-local evidence at references/evals/eval.ryan.long-term-coherence-governance.md; it does not by itself prove repository, pull request, remote-check, merge-readiness, or Tessl-readiness outcomes.
Durable mechanism: use this fixture to generate scenario criteria that require the agent to review precedent across generated surfaces, names the durable ownership boundary, chooses ledger/validator/runbook/skill promotion only when warranted, and defines pruning criteria.
Validation status: not_run_with_reason until the scenario is executed by the local pipeline and private Tessl eval lane.
