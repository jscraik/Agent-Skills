# Production Guardrails

Separate offline measurement from online guardrails and monitor high-risk failures with explicit prevention paths.

Pack id: pack.evals-testing
Facet id: production_guardrails
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Core Guidance

Production AI systems need online guardrails for high-risk failures in addition to offline eval trend measurement. Controlled experiments need a clear objective metric, proper randomization, instrumentation, and guardrail checks before their results are trustworthy.

Prefer code, schema, parser, regex, or exact artifact checks for objective properties. Use human review for subjective quality until labels are stable enough to automate. A static skill review is not behavior proof: task and repository evals must test whether the context improves behavior on realistic scenarios.

Offline evals and production monitoring should feed each other. Start from production or production-like trace clusters, inspect a bounded sample, convert representative failures into replayable datasets, calibrate scorers against obvious pass and fail cases, and retain resolved failures as regressions.

## Production Failure Loop

1. Identify the trace, review note, log query, or production-risk proxy.
2. Cluster similar failures and inspect a bounded sample before automating.
3. Convert representative failures into a privacy-safe replayable dataset.
4. Use deterministic checks for objective requirements and human review for subjective dimensions.
5. Record the baseline, change, evaluator version, model or prompt version, and dataset snapshot.
6. Compare target improvement and unrelated regressions.
7. Monitor fresh production traces after deployment and feed new failures back into the suite.

## Boundary

An improving offline score does not prove production readiness. Name the primary metric, instrumentation, high-risk failure modes, and online prevention or rollback checks before making that claim.
