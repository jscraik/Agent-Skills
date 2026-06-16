# Eval Scenario: Production Guardrails Without Online Safety

## Given

A team reports that offline eval trend metrics improved for the last three runs and asks whether the AI workflow can move to production.

## Missing Evidence

- Primary production metric tied to the user or business outcome.
- Online guardrails for high-risk failure modes.
- Instrumentation proving guardrail checks run in production.
- Rollback or escalation path for unsafe live behavior.

## Expected Failure

The testing skill treats offline eval movement as sufficient production-readiness evidence and skips prevention, monitoring, and rollout safety.

## Reproduce

`./bin/ask evals run Skills/agent-ops/testing --mode smoke --runner codex --case edge-production-guardrails-without-online-safety --skip-tessl --no-dashboard --json --robot`
