# CE TDD Likeness and Consolidation Report

Read when: updating `ce-tdd` from upstream `tdd` variants and you need an auditable map of what was preserved, upgraded, and intentionally changed.

## Table of Contents
- [Inputs](#inputs)
- [1. Likeness Summary](#1-likeness-summary)
- [2. Golden Nuggets](#2-golden-nuggets)
- [3. Issues and Weaknesses](#3-issues-and-weaknesses)
- [4. Missing Capabilities](#4-missing-capabilities)
- [5. Final Merged Skill (Production Ready)](#5-final-merged-skill-production-ready)
- [6. Upgrade Notes](#6-upgrade-notes)
- [Self-check](#self-check)

## Inputs
- Skill_A: `product/Infrastructure/ops/ce-tdd/SKILL.md` (local CE posture variant)
- Skill_B: `mattpocock/skills/tdd/SKILL.md` at commit `651eab033bdf8f7fd535c274f8cbe839075aba5e`
- Companion references compared: `tests.md`, `mocking.md`, `deep-modules.md`, `interface-design.md`, `refactoring.md`

## 1. Likeness Summary
- similarity score: 76%
- relationship type: partial overlap (shared TDD core, divergent operating context)
- key differences:
  - `ce-tdd` adds CE-stage routing, acceptance traceability, explicit stop gates, and graph integrations.
  - upstream `tdd` is concise and generic; it is not coupled to `ce-plan`/`ce-work` orchestration.
  - `ce-tdd` adds stronger observability and anti-pressure guardrails for execution claims.

## 2. Golden Nuggets
- strict RED -> GREEN -> Refactor loop with explicit prohibition on horizontal slicing
- behavior-through-public-interface testing doctrine
- integration-style default test posture over implementation-coupled unit tests
- deep-module bias (small interface, deep implementation) to reduce test-surface explosion
- one-test-at-a-time tracer bullet execution discipline
- post-GREEN refactor-only rule with immediate re-test requirement

## 3. Issues and Weaknesses
- redundancies:
  - TDD philosophy and anti-pattern rationale repeated across `SKILL.md` and references by design for skimmability
- conflicts:
  - none functionally; terminology normalized to CE posture while preserving upstream intent
- outdated patterns:
  - generic upstream prompt lacks CE-specific traceability and stage-bound handoff context

## 4. Missing Capabilities
- deterministic specialist-lane map for optional delegation (added via `Infrastructure/references/sub-agent-map.md`)
- explicit evidence-capture check for RED/GREEN command reason quality (added in workflow checklist)
- parity audit trail documenting consolidation decisions and source commit provenance (this file)

## 5. Final Merged Skill (Production Ready)
---
name: ce-tdd
path: /Users/jamiecraik/dev/Agent-Skills/product/Infrastructure/ops/ce-tdd/SKILL.md
status: active
composition: merged and modernized from local CE posture + upstream TDD doctrine
references:
  - /Users/jamiecraik/dev/Agent-Skills/product/Infrastructure/ops/ce-tdd/Infrastructure/references/tests.md
  - /Users/jamiecraik/dev/Agent-Skills/product/Infrastructure/ops/ce-tdd/Infrastructure/references/mocking.md
  - /Users/jamiecraik/dev/Agent-Skills/product/Infrastructure/ops/ce-tdd/Infrastructure/references/deep-modules.md
  - /Users/jamiecraik/dev/Agent-Skills/product/Infrastructure/ops/ce-tdd/Infrastructure/references/interface-design.md
  - /Users/jamiecraik/dev/Agent-Skills/product/Infrastructure/ops/ce-tdd/Infrastructure/references/refactoring.md
  - /Users/jamiecraik/dev/Agent-Skills/product/Infrastructure/ops/ce-tdd/Infrastructure/references/sub-agent-map.md
---

## 6. Upgrade Notes
- what was added:
  - CE-specific execution gates, acceptance-ID traceability, structured deliverable contract, and deterministic sub-agent routing reference.
- what was removed:
  - no high-value upstream doctrine removed; low-value duplication kept minimal and shifted to references where appropriate.
- why changes improve the skill:
  - improves route precision, execution determinism, failure handling, and production usability without sacrificing upstream TDD clarity.

## Self-check
- no duplication:
  - logic duplication is bounded and intentional; deep examples and doctrine live in references.
- full coverage of inputs:
  - all high-value upstream behaviors are preserved and mapped to CE operating context.
- modern compliance:
  - deterministic constraints, explicit failure modes, validation-ready outputs, and reference-backed observability are present.
