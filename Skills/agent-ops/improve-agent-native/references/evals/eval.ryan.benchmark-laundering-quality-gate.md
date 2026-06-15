# Benchmark Laundering Quality Gate Fixture

Review a proposal for an agent benchmark that counts tasks completed and
lines of code generated. The benchmark does not inspect accessibility,
maintainability, misuse resistance, synthesis quality, stakeholder usefulness,
or whether the resulting artifacts support future engineering work.

Expected behavior:

- Identify that the benchmark measures code output rather than software
  engineering behavior.
- Name the missing full-loop quality dimensions.
- Propose a gate that checks artifact usefulness, synthesis clarity,
  accessibility or misuse resistance when relevant, and durable maintainability.
- Avoid treating benchmark pass rate as sufficient proof of engineering quality.

## Skill-Local Evidence Boundary

Failure category: seed eval requires behavioural scenario conversion.
Evidence boundary: this fixture is skill-local evidence at references/evals/eval.ryan.benchmark-laundering-quality-gate.md; it does not by itself prove repository, pull request, remote-check, merge-readiness, or Tessl-readiness outcomes.
Durable mechanism: use this fixture to generate scenario criteria that require the agent to identify benchmark laundering, names missing full-loop quality checks, and proposes a gate for artifact usefulness, synthesis clarity, accessibility or misuse resistance, and durable engineering behavior.
Validation status: not_run_with_reason until the scenario is executed by the local pipeline and private Tessl eval lane.
