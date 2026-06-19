---
schema_version: evals-router.knowledge-capsules.v1
source_manifest: references/knowledge-capsule.manifest.yaml
archived_detail_root: Infrastructure/references/deferred-skill-context/agent-ops-evals-router/references/knowledge-capsules
---

# Knowledge Capsule Summary

Use this file when eval design needs KnowledgeOS-derived grounding but the
full capsules would add unnecessary context. Load archived detail only when the
summary is insufficient for a concrete decision.

## Trace Error Analysis

- Start with traces and failure examples before writing new judges.
- Build a taxonomy from observed failures, not from generic quality labels.
- Keep coverage multidimensional: task, user intent, evidence source, failure
  class, and recovery behavior.

## Deterministic Evaluator Design

- Prefer code, schema, regex, fixture, and command checks for objective facts.
- Use LLM judges only for subjective dimensions that deterministic checks
  cannot prove.
- Treat evaluators as tested artifacts with known good and bad examples.

## Judge Calibration

- Validate judges against labeled examples before using scores as release
  evidence.
- Track true positives, true negatives, false positives, and false negatives.
- Keep precision/recall or TPR/TNR evidence separate from aggregate pass rates.

## Regression Loop

- Convert fixed failures into retained regression cases.
- Pair score changes with root cause, patch path, and rerun evidence.
- Do not stop at a dashboard score without the next action or guardrail.

## Production Guardrails

- Separate offline eval quality from production monitoring and online guardrail
  behavior.
- Redact sensitive data in trace, scorer, and observability artifacts.
- Treat exporter, collector, and credential failures as lane blockers, not as
  proof that the underlying skill failed.
