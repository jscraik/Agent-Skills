# Knowledge Capsules

Load the smallest relevant capsule set for the testing proof question.

- [Trace error analysis](evals-trace-error-analysis.md): use before dashboards, judges, or aggregate claims when traces, failure taxonomy, sampling, or coverage dimensions are missing.
- [Deterministic evaluator design](evals-deterministic-evaluator-design.md): use when a behavior can be checked by code, schemas, parsers, fixtures, invariants, or artifact comparison.
- [Judge calibration](evals-judge-calibration.md): use before treating LLM or reviewer judge scores as release evidence.
- [Regression loop](evals-regression-loop.md): use when eval failures need root cause, fix path, rerun proof, and retained regression cases.
- [Production guardrails](evals-production-guardrails.md): use when proof must extend to production monitoring, online guardrails, primary metrics, or experiment safety.

Keep the manifest and demand files as the source inventory:

- [Knowledge capsule manifest](knowledge-capsule.manifest.yaml)
- [Knowledge demand](knowledge-demand.yaml)
