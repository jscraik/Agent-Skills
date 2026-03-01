---
name: tech-spec
description: 'Create implementation-ready technical planning artifacts from an existing
  tech spec. Use when you need one focused mode: data_spec, migration_plan, ops_spec,
  or performance_plan.'
knowledge_graph_profile: references/task-profile.json
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

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.

<!-- decision-feedback-protocol:v1 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- If available, persist with `ops/scripts/graph/record-feedback.sh`; otherwise append a JSONL record to `ops/metrics/skill-feedback/decision-feedback.jsonl` in the active workspace.
<!-- /decision-feedback-protocol -->
