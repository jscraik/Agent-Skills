---
title: Harness-engineering CE to HE migration cutover and gate repair
asset_family: harness-engineering stage naming and routing governance
owner: Agent Skills Team
source_artifact: Plugins/harness-engineering/.codex-plugin/plugin.json
freshness_reviewed_on: 2026-07-21
last_updated: 2026-07-21
review_after_days: 90
---

# Harness-engineering CE To HE Migration Cutover And Gate Repair

## Table of Contents

- [Problem](#problem)
- [Resolution](#resolution)
- [Evidence](#evidence)
- [Follow-up](#follow-up)

## Problem

The harness-engineering plugin had mixed CE/HE naming across active skills, archived fixtures, and routing metadata, which created two operational risks:

1. Discovery/routing drift: both legacy `ce-*` and target `he-*` identifiers could exist in different layers, making stage selection and references inconsistent.
2. Validation-gate breakage: the skill-authoring family gate still referenced CE-era variables and path precedence, which caused pre-commit failures during the cutover.

This made the migration non-durable until naming, routing, and validation enforcement all converged on HE canonical names.

## Resolution

Applied a complete cutover with canonical HE naming plus validator hardening:

1. Renamed active harness-engineering skills from `ce-*` to `he-*` and updated plugin/routing metadata to HE identifiers.
2. Normalized preserved skill fixtures (then `Plugins/harness-engineering/fixtures/skill-archive`, now `Plugins/harness-engineering/fixtures/preserved-context` with a compatibility alias) from `ce-*` to `he-*`, including anti-pattern reference filenames and task-profile IDs.
3. Updated `Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh` to:
   - validate `he-work`/`he-tdd` approval-flow linkage,
   - fix stale CE variable references,
   - prefer canonical `Plugins/...` pytest candidates before lowercase fallback aliases.
4. Re-ran family-gate and hook paths until commit/push hooks passed with the migrated naming model.

Result: HE naming is now the active canonical path in skills, archive fixtures, routing, and pre-commit enforcement.

## Evidence

- Commit and scope:
  - `b7cfa722` (`refactor(harness-engineering): complete ce-to-he skill cutover`)
  - 217 files changed with active + archive rename coverage and validator updates.
- Validation command:
  - `bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh` -> pass
  - includes pytest lane: `24 passed`.
- Hook outcomes:
  - commit hook `Run pre-commit validation` -> pass
  - push hook `Run pre-push diagnostics` -> pass
- Branch and PR:
  - branch: `codex/agent-skills-worktree-c81e0239`
  - PR: `https://github.com/jscraik/Agent-Skills/pull/127`
- Freshness re-review (2026-07-21):
  - `Plugins/harness-engineering/.codex-plugin/plugin.json` still identifies the
    canonical `harness-engineering` plugin.
  - `bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh`
    passed, including the active HE routing, reference-integrity, and structural
    family checks.

## Follow-up

- Keep HE-only names as canonical in plugin manifests, routing maps, and stage docs; treat new CE-name reintroduction as drift.
- Require independent CodeRabbit/Codex review artifacts on PR #127 before merge, since this migration changes broad path and routing surfaces.
- If any external consumers still reference `ce-*`, capture those callers explicitly and either migrate them or add bounded compatibility shims with sunset dates.
