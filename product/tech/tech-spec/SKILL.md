---
name: tech-spec
description: "Create implementation-ready technical planning artifacts from an existing tech spec. Use when you need one focused mode: data_spec, migration_plan, ops_spec, or performance_plan."
metadata:
  short-description: Canonical tech-spec transformer with mode routing.
---

# Tech Spec (Canonical)

This is the canonical skill for transforming a tech spec into specialized delivery artifacts.

## Philosophy

- Keep technical planning focused and mode-driven.
- Use one canonical source to avoid duplicated instructions.
- Prefer measurable, verifiable outputs over vague recommendations.
- Make assumptions explicit and call out risk early.

## Scope and triggers
Use this skill when you already have a tech spec and need one of these modes:

- `data_spec`: schema/contracts/lifecycle/retention/access controls.
- `migration_plan`: phased rollout, rollback, compatibility, validation.
- `ops_spec`: SLOs, alerts, runbooks, ownership, escalation.
- `performance_plan`: budgets, load testing, thresholds, monitoring.

Default mode: infer from user request keywords; ask one clarifier only if ambiguous.

## Required inputs
- Source tech spec path or pasted excerpt.
- Desired mode (`data_spec`, `migration_plan`, `ops_spec`, `performance_plan`).
- Known constraints: compliance/SLA/timeline/risk tolerance.

## Deliverables
Write outputs beside source tech spec (unless user overrides path):

- `data_spec` → `*-data-spec.md`
- `migration_plan` → `*-migration-plan.md`
- `ops_spec` → `*-ops-spec.md`
- `performance_plan` → `*-performance-plan.md`

All outputs should include assumptions, evidence quality, and explicit gaps.

## Procedure

1. Resolve mode and confirm source artifact.
2. Extract only relevant sections from source tech spec.
3. Apply mode-specific template below.
4. Produce concise artifact with checkable criteria.
5. Summarize unresolved risks and next validation step.

Mode templates:

### `data_spec`

Required sections:

1. Data entities and schema tables
2. Field constraints and indexes
3. Data sources and contracts
4. Lifecycle and retention
5. Migration/backfill strategy
6. Privacy and access controls

### `migration_plan`

Required sections:

1. Scope and assumptions
2. Schema/data changes
3. Phased rollout steps
4. Rollback triggers and recovery runbook
5. Validation checkpoints
6. Compatibility/deprecation policy

### `ops_spec`

Required sections:

1. Service overview and ownership
2. SLOs/error budget
3. Alerts and thresholds
4. Dashboards/signals
5. Incident response and rollback
6. On-call and escalation path

### `performance_plan`

Required sections:

1. Objectives (latency/throughput/availability)
2. Budgets per endpoint/component
3. Load + stress testing plan
4. Bottleneck risks/mitigations
5. Monitoring thresholds and alerts
6. Acceptance criteria

## Validation

Fail fast: **stop at the first failed gate and do not proceed**.

- Confirm chosen mode maps to output sections fully.
- Confirm thresholds/criteria are measurable (no vague adjectives).
- Confirm assumptions and unresolved risks are explicitly listed.
- For migration/performance/ops modes, include rollback/fallback language.

## Anti-patterns

- Mixing multiple modes in one unfocused artifact.
- Omitting rollback criteria for migration/ops/performance work.
- Producing unmeasurable goals (e.g., "fast", "reliable").
- Inventing source details not present in tech spec.

## Constraints

- Redact secrets/tokens/credentials/PII by default.
- Avoid destructive operations unless explicitly requested.
- Keep output tied to source-spec evidence; mark gaps explicitly.

## Examples

- "Generate migration plan from this tech spec" → `migration_plan`
- "Create data spec for this architecture draft" → `data_spec`
- "Need SLO/alerts/runbook from this design" → `ops_spec`
- "Need perf budgets and load tests from this spec" → `performance_plan`

## References

- `references/contract.yaml`
- `references/evals.yaml`
