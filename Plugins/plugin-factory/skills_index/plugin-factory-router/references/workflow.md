# Plugin Factory Router Entrypoint Workflow

## Metadata

- owner: Agent Skills Team
- max_duration: 15m
- escalation_path: plugin-factory maintainers
- change_class: routing-only

## Execution Modes

- STRICT: fail closed when lane confidence is low or required inputs are missing.
- ADVISORY: return best-fit lane plus explicit assumptions and risk notes.

## Invariants

- test_mode: deterministic
- test_tier: lane-routing
- tracer_bullet_first: true
- red_evidence_required: true

## Route Map

- create scaffolds -> `Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/SKILL.md`
- harden or convert packages -> `Plugins/plugin-factory/skills/code_quality_review/plugin-builder/SKILL.md`
- install or repair plugin visibility -> `Plugins/plugin-factory/skills/infrastructure_ops/plugin-installer/SKILL.md`
- classify mixed requests first -> `Plugins/plugin-factory/skills/team_automation/plugin-router/SKILL.md`

## Procedure

1. Classify intent (`create|harden|convert|install|troubleshoot`).
2. Hand off to exactly one lane.
3. Ask one clarification question only when lane choice is ambiguous.
4. Stop after routing handoff.

## State Machine

- S0 intake -> S1 classify -> S2 route -> S3 handoff (terminal)
- S1 -> S4 clarification (when intent is ambiguous)
- S4 -> S1 classify (after clarification)
- S1 -> S5 blocked (terminal) when required inputs are unavailable

## Transition Table

| S | E | G | A | N |
|---|---|---|---|---|
| S0 | request_received | payload present | normalize request | S1 |
| S1 | lane_resolved | confidence high | select lane and rationale | S2 |
| S1 | lane_ambiguous | confidence low | emit one clarification question | S4 |
| S1 | missing_required_input | required input absent | emit blocked response | S5 |
| S4 | clarification_received | answer complete | reclassify intent | S1 |
| S2 | handoff_ready | next command formed | emit handoff payload | S3 |

## Error Handling

- VALIDATION_ERROR: malformed input payload, return blocked with correction hint.
- BLOCKED_DEPENDENCY: missing repository/source context, return blocked with required field.
- POLICY_FAIL: routing rules conflict detected, stop and escalate.
- SYSTEM_ERROR: runtime/tool failure, preserve context and return blocker.

## Idempotency

- idempotency_key: `plugin-factory-router|{request_hash}|{lane}|{mode}`
- Repeated requests with identical key should return the same lane and next command.
