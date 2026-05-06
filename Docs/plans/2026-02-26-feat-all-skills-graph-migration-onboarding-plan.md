---
plan_id: ASK-ALL-SKILLS-GRAPH-20260226
title: feat: All-Skills Knowledge Graph Migration + Onboarding
type: feat
status: completed
date: 2026-02-26
completed: 2026-03-02
origin: docs/brainstorms/2026-02-24-skill-graph-live-auto-learning-brainstorm.md
---

# feat: All-Skills Knowledge Graph Migration + Onboarding

## Table of Contents
- [Overview](#overview)
- [Closeout addendum (2026-03-30)](#closeout-addendum-2026-03-30)
- [Goals and scope](#goals-and-scope)
- [Public interface and contract changes](#public-interface-and-contract-changes)
- [Wave model](#wave-model)
- [Task graph (id / depends_on)](#task-graph-id--depends_on)
- [Acceptance criteria](#acceptance-criteria)
- [Test scenarios](#test-scenarios)
- [Risks and mitigations](#risks-and-mitigations)
- [Sources](#sources)

## Overview

Migrate the skill graph from pilot-only onboarding to all active skills with deterministic profile contracts, required SKILL bindings, wave-gated rollout controls, and machine-validated readiness artifacts.

This carries forward the brainstorm decisions to:
- capture every run,
- inject lessons at start-of-run,
- retain confidence scoring,
- enforce kill-switch-first safety.

(see brainstorm: `docs/brainstorms/2026-02-24-skill-graph-live-auto-learning-brainstorm.md`)

## Closeout Addendum (2026-03-30)

Historical migration delivery remains complete, but post-migration readiness drift (event-envelope blocker accounting and checklist placeholder ownership fields) was tracked in:

- `Docs/plans/2026-03-29-fix-outstanding-onboarding-readiness-closeout-plan.md`

That closeout plan is now completed with current evidence in:

- `Infrastructure/artifacts/skill-graphs/onboarding/wave-readiness.json`
- `Infrastructure/artifacts/skill-graphs/onboarding/skill-onboarding-checklist-2026-03-29.md`
- `docs/skill-graphs/telemetry/daily-skill-health.md`

## Goals and scope

### In scope
- Generate and validate `Infrastructure/references/task-profile.json` for every active in-scope skill.
- Add `knowledge_graph_profile` frontmatter binding to each in-scope `SKILL.md`.
- Publish onboarding artifacts:
  - `Infrastructure/artifacts/skill-graphs/onboarding/baseline-2026-02-26.json`
  - `Infrastructure/artifacts/skill-graphs/onboarding/profile-index.json`
  - `Infrastructure/artifacts/skill-graphs/onboarding/wave-readiness.json`
  - `Infrastructure/artifacts/skill-graphs/onboarding/skill-onboarding-checklist-2026-02-26.md`
- Encode wave gates:
  - Wave 0 controls verification
  - Wave 1 manual-skill onboarding
  - Wave 2 co-pilot-skill onboarding

### Exclusions
- Root index skill: `SKILL.md`
- Internal system skills: `skills/.system/*`
- Template-only skill paths:
  `Skills/recon-workbench/assets/template/.codex/skills/*`

## Public interface and contract changes

1. **Per-skill profile contract (required)**
   - File: `<skill>/Infrastructure/references/task-profile.json`
   - Required fields: `schema_version`, `profile_id`, `scope_skill`, `scope_profile`,
     `criteria[]`, `thresholds`, `delegation`.
2. **SKILL metadata binding**
   - Add frontmatter key:
     `knowledge_graph_profile: Infrastructure/references/task-profile.json`
3. **Readiness artifacts**
   - `profile-index.json` (per-skill validation status)
   - `wave-readiness.json` (wave gates + blocker ownership SLA fields)
4. **Governance policy**
   - Require at least two approvers for wave promotion readiness.

## Wave model

- **Wave 0 (controls):**
  - kill-switch precedence verified
  - rollout-mode precedence verified
  - telemetry envelope integrity (`events.jsonl`) verified
- **Wave 1 (manual):**
  - manual-mode skills onboarded first
  - rollout mode remains `observe_only`
  - reviewer signoff required for candidate promotions
- **Wave 2 (co-pilot):**
  - remaining co-pilot skills onboarded by domain cohorts
  - auto-apply stays off until uplift + non-regression gates pass

## Task graph (id / depends_on)

```yaml
tasks:
  - id: T1
    title: Freeze active-skill inventory and write baseline artifact
    depends_on: []
  - id: T2
    title: Align schema/docs on required delegation + escalation threshold
    depends_on: [T1]
  - id: T3
    title: Build generator for per-skill profiles + SKILL frontmatter binding
    depends_on: [T2]
  - id: T4
    title: Build validator for profile-index + wave-readiness outputs
    depends_on: [T3]
  - id: T5
    title: Generate profiles and bindings across all active skills
    depends_on: [T3]
  - id: T6
    title: Validate onboarding state and emit readiness artifacts
    depends_on: [T4, T5]
  - id: T7
    title: Update governance policy for >=2 approvers
    depends_on: [T2]
  - id: T8
    title: Add observe-only smoke runner for all profiles
    depends_on: [T4]
  - id: T9
    title: Execute smoke runs and persist smoke report
    depends_on: [T6, T8]
  - id: T10
    title: Verify and publish go/no-go readiness summary
    depends_on: [T6, T7, T9]
```

## Acceptance criteria

- [ ] AC1: Every in-scope active skill has valid `Infrastructure/references/task-profile.json`.
- [ ] AC2: Every in-scope active `SKILL.md` has `knowledge_graph_profile` binding.
- [ ] AC3: `profile-index.json` and `wave-readiness.json` are generated and machine-validated.
- [ ] AC4: Approver policy includes >=2 approvers.
- [ ] AC5: `.agents/PLANS.md` includes migration DAG tasks and dependencies.
- [ ] AC6: Wave promotion remains blocked when telemetry envelope errors are non-zero.

## Test scenarios

1. Missing profile file fails validator.
2. Invalid schema field fails with explicit field-level error.
3. Invalid delegation mode fails validator (`collaboration` rejected for new profiles).
4. Missing SKILL binding fails validator.
5. Wave readiness blocks on missing controls or event envelope errors.
6. Wave readiness blocks when approver count < 2.
7. Generator rerun is idempotent for unchanged skills.
8. Smoke runner reports per-profile pass/fail with run metadata.

## Risks and mitigations

- **Risk:** telemetry inconsistency blocks wave progression.
  - **Mitigation:** enforce zero event-envelope errors in readiness gate.
- **Risk:** governance bottleneck with single approver.
  - **Mitigation:** enforce policy with >=2 approvers.
- **Risk:** large batch onboarding drift.
  - **Mitigation:** deterministic profile IDs + repeatable validator artifacts.

## Sources

- **Origin brainstorm:** [docs/brainstorms/2026-02-24-skill-graph-live-auto-learning-brainstorm.md](/docs/brainstorms/2026-02-24-skill-graph-live-auto-learning-brainstorm.md)
- Existing plan baseline:
  [Docs/plans/2026-02-24-feat-skill-graph-live-auto-learning-plan.md](/Docs/plans/2026-02-24-feat-skill-graph-live-auto-learning-plan.md)
- Skill graph index:
  [docs/skill-graphs/index.md](/docs/skill-graphs/index.md)
