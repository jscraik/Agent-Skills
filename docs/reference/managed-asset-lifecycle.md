# Managed Asset Lifecycle Reference

## Table of Contents
- [Purpose](#purpose)
- [Phase-One Scope](#phase-one-scope)
- [Authoritative Representation](#authoritative-representation)
- [Derived Views](#derived-views)
- [Packaged Skill Inheritance](#packaged-skill-inheritance)
- [Lifecycle Readiness States](#lifecycle-readiness-states)
- [docs/solutions Admission Minimum](#docssolutions-admission-minimum)
- [Phase-One Proof Targets](#phase-one-proof-targets)

## Purpose

This reference records the phase-one lifecycle governance defaults for managed assets in this repo so scaffolds, validators, and migration work reuse one contract instead of inventing parallel rules.

Canonical source artifacts:
- [2026-03-24-feat-skill-lifecycle-scaffold-memory-program-spec.md](/Users/jamiecraik/dev/Agent-Skills/docs/specs/2026-03-24-feat-skill-lifecycle-scaffold-memory-program-spec.md)
- [2026-03-24-feat-skill-lifecycle-scaffold-memory-program-plan.md](/Users/jamiecraik/dev/Agent-Skills/docs/plans/2026-03-24-feat-skill-lifecycle-scaffold-memory-program-plan.md)

## Phase-One Scope

Managed assets in phase one:
- canonical skills
- packaged skills
- plugin packages

Out of scope in phase one:
- general references with no lifecycle significance
- brainstorm-only artifacts
- transient generated artifacts under `artifacts/`

## Authoritative Representation

Use in-file metadata as the authoritative representation in phase one.

Asset-type rules:
- canonical Markdown-governed skills: frontmatter in the canonical `SKILL.md`
- packaged Markdown-governed skills: inherited from the canonical source skill when a one-to-one mapping exists
- plugin packages: native manifest fields in `.codex-plugin/plugin.json`

Source-of-truth rule:
- each managed asset category must have one readable canonical source
- sidecars and indexes may exist only as derived views
- equal-authority duplicates are not allowed

## Derived Views

Derived views are allowed only when they are mechanically regenerated from the authoritative in-file source.

Phase-one expectations:
- derived catalogs must not become alternate editors of lifecycle truth
- disagreement between authoritative and derived views is a degraded or blocked state, never silent success
- regeneration triggers must be documented by the validator or sync surface that owns the derived view

## Packaged Skill Inheritance

Packaged skills inherit lifecycle metadata from the canonical source skill when a one-to-one mapping exists.

Inheritance requirements:
- the mapping must be explicit and validator-visible
- inheritance must be lossless enough for governance use
- if the mapping is missing, ambiguous, or lossy, the packaged asset must declare the required lifecycle fields directly

Phase-one packaged proof target:
- [skill-factory packaged skill-builder](/Users/jamiecraik/dev/agent-skills/plugins/skill-factory/skills/skill-builder/SKILL.md)

## Lifecycle Readiness States

Phase-one readiness outcomes:
- `healthy`: required lifecycle fields exist in the authoritative representation and any derived views agree or are freshly regenerated
- `degraded`: the asset remains governable, but one or more required invariants are stale or incomplete
- `blocked`: representation, ownership, or validation ambiguity is too high for safe adoption or promotion-style workflows

Incubating asset policy:
- `blocked`
  - ownership missing
  - authoritative and derived representations disagree and regeneration cannot reconcile them
  - validator cannot tell where lifecycle truth lives
- `degraded`
  - review cadence overdue
  - `docs/solutions/` linkage or freshness stale while ownership remains attributable
  - non-critical lifecycle metadata incomplete, but authoritative representation is still readable

## docs/solutions Admission Minimum

A `docs/solutions` entry is valid only when it includes:
- a linked governed asset or asset family
- at least one concrete source artifact such as a spec, plan, review, validation result, task artifact, diff, or governed asset path
- a concise problem statement
- a concise resolution statement
- maintenance ownership context
- a freshness marker suitable for later review

Entries that are only short-lived execution notes or incident journals do not qualify.

## Phase-One Proof Targets

Use these seed targets when proving the baseline across asset categories:
- canonical skill: [coding-harness/SKILL.md](/Users/jamiecraik/dev/Agent-Skills/utilities/coding-harness/SKILL.md)
- packaged skill: [skill-factory packaged skill-builder](/Users/jamiecraik/dev/agent-skills/plugins/skill-factory/skills/skill-builder/SKILL.md)
- plugin package: [skill-factory plugin manifest](/Users/jamiecraik/dev/agent-skills/plugins/skill-factory/.codex-plugin/plugin.json)
