---
schema_version: 1
artifact_type: sdk_strategy
status: implementation_ready
date: 2026-05-20
repo: agent-skills
primary_contract: Infrastructure/config/schemas/skill-doctor.v1.schema.json
---

# Agent Skills Kit SDK North Star

## BLUF

Agent Skills Kit should become a professional, agent-native SDK for Codex
skills. The first implementation boundary is additive: register
`./bin/ask skills doctor <handle> --json --robot` as the stable readiness
facade over existing `skills prove`, `skills proof`, `skills explain`,
audit, and future package signals. Do not move or deprecate existing
`prove`/`proof` semantics in RF-1.

## Source Of Truth

Implementation truth lives in executable surfaces, in this order:

1. `Infrastructure/config/schemas/skill-doctor.v1.schema.json`
2. `./bin/ask skills doctor <handle> --json --robot`
3. focused command/parser/help/guided-error parity tests
4. doctor fixtures for `context7` and one non-`context7` skill class
5. `.harness/evals/2026-05-17-agent-skills-skill-sdk-doctor-trust-eval.md`
6. closeout evidence with exact commands and pass/fail/blocked outcomes

Markdown and HTML artifacts are maps over those surfaces. They are not allowed
to create parallel requirements.

## Operating Shape

- Thin surface: one small public doctor command for readiness.
- Strong guardrails: schema, fixtures, status precedence, and rollback rules.
- Durable memory: eval feedback becomes classified deltas with rerun evidence.
- Professional output: every readiness claim names evidence and a safe next
  command.

## RF-1 Decision

RF-1 creates `skills doctor` as an additive facade. Existing `skills prove`
and `skills proof` remain valid comparison and compatibility surfaces.

RF-1 is green to implement only when the plan requires:

- parser/help/guided-error action parity;
- schema validation against `skill-doctor.v1`;
- phase A registration proof before phase B contract proof;
- `context7` plus one additional skill-class fixture;
- explicit unavailable/not_implemented state for package readiness;
- rollback that preserves the doctor seam after acceptance unless an emergency
  waiver reopens RF-1.
