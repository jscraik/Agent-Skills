---
title: Skill Authoring Family — Boundary Decision Record
type: reference
status: active
date: 2026-04-05
authority: scripts/validate_skill_authoring_family.sh
---

# Skill Authoring Family — Boundary Decision Record

## Table of Contents
- [Decision](#decision)
- [Active Gate Family](#active-gate-family)
- [Adjacent Surface](#adjacent-surface)
- [Authority Order](#authority-order)
- [Reconciled Sources](#reconciled-sources)
- [Layered Ownership Model](#layered-ownership-model)
- [Compatibility Notes](#compatibility-notes)
- [Rollback Condition](#rollback-condition)

## Decision

Effective 2026-04-05, the active skill-authoring gate family consists of four members:

- `skills-system/skill-creator`
- `utilities/skill-builder`
- `skills-system/skill-installer`
- `skills-system/plugin-creator`

`utilities/plugin-builder` is an **adjacent handoff surface**, not an active gate-family member. It remains a valid downstream target for full plugin packaging after lifecycle validity is established.

This decision closes the boundary drift where the gate script used `plugin-creator` but the governing spec and maturity matrix still named `plugin-builder` as a core family member.

## Active Gate Family

| Skill | Layer | Primary job |
|---|---|---|
| `skill-creator` | First-layer scaffolding | Starter authoring; creates first-draft skills and scaffold-bound edits |
| `plugin-creator` | First-layer scaffolding | Plugin scaffolding; generates `plugin.json` and companion folder structure |
| `skill-builder` | Enhancement layer | Lifecycle hardening; validators, evals, baseline comparison, and packaging |
| `skill-installer` | Downstream lifecycle | Install and import of already-valid skill packages |

Enforced by: `scripts/validate_skill_authoring_family.sh`

## Adjacent Surface

| Skill | Role | When to use |
|---|---|---|
| `plugin-builder` | Full plugin packaging and governance | Downstream handoff from `skill-builder` once `ContractValidityEvidence` exists and remaining work is full plugin packaging |

`plugin-builder` is **not validated** by the family gate script. It is a legitimate handoff target described in the governing spec for plugin packaging workflows.

## Authority Order

When family membership language conflicts across surfaces, use this resolution order (highest to lowest):

1. **Gate enforcement script** — `scripts/validate_skill_authoring_family.sh` (runtime truth)
2. **Active spec** — `docs/specs/2026-04-03-feat-skill-authoring-family-contract-spec.md`
3. **Reference matrix** — `docs/reference/skill-authoring-validation-maturity-matrix.md`
4. **This document** — boundary decision record

Historical/completed plan artifacts (e.g., `docs/plans/2026-04-04-*`) are preserved as-is and do not govern current membership.

## Reconciled Sources

The following sources were updated on 2026-04-05 to reflect the canonical boundary:

| File | Change |
|---|---|
| `docs/reference/skill-authoring-validation-maturity-matrix.md` | Purpose section: replaced `utilities/plugin-builder` with `skills-system/plugin-creator`; added boundary note |
| `docs/specs/2026-04-03-feat-skill-authoring-family-contract-spec.md` | System Boundary, Core Domain Model, role table, invariant, and SA1: distinguish active gate family from adjacent surface |

The gate script `scripts/validate_skill_authoring_family.sh` already used the correct membership — no change required.

## Layered Ownership Model

Two-layer parity model (Decision 2a from the gold-standard upgrade plan):

**First-layer scaffolding** (create the skeleton):
- Skills: `skill-creator` (skill authoring), `plugin-creator` (plugin scaffolding)
- Entry point for new work; produces starter artifacts before hardening

**Enhancement layer** (harden and package):
- Skills: `skill-builder` (skill lifecycle), `plugin-builder` (full plugin packaging)
- Requires valid starter artifacts from the first layer before beginning

This parallel structure keeps skill workflows and plugin workflows mentally symmetric while preserving current gate ownership.

## Compatibility Notes

- All handoff references to `plugin-builder` in specs, SKILL files, and evals remain valid. The adjacency designation changes its **gate-membership status**, not its usefulness as a downstream surface.
- `skill-builder` may still hand off to `plugin-builder` when `ContractValidityEvidence` exists. This path is unchanged.
- `plugin-creator`'s `evals.yaml` and `agents/openai.yaml` are gate-validated as of this upgrade pass.

## Scorecard Link

This decision record is linked from the governance scorecard at:
`docs/reference/skill-authoring-family-gold-scorecard.md`

## Rollback Condition

If a downstream contract consumer breaks because `plugin-creator` was promoted into a gate it cannot yet satisfy, the rollback is:

1. Remove `skills-system/plugin-creator` from the `skill_dirs` array in `scripts/validate_skill_authoring_family.sh`.
2. Revert the boundary-membership changes in the spec and matrix (restore `plugin-builder` as the gate member).
3. Record the regression in `.harness/memory/LEARNINGS.md` with root cause.
4. Open a follow-up issue before re-attempting the promotion.

Rollback does not require updating this decision record — its `status` field should be changed to `superseded` and a new record written for the reverted state.
