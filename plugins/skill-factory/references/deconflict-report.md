# Skill Factory Deconflict Report

## Candidate Package
- `plugins/skill-factory`

## Overlap Check
- Existing local plugin packages remain distinct by responsibility:
  - `plugin-factory`: plugin packaging and marketplace tooling
  - `skill-factory`: skill creation, hardening, routing, and lifecycle tooling

## Decision
- Keep `skill-factory` as a standalone package.
- Fold `skill-refactor` into `skill-factory` as a plugin-owned lane.
- Maintain `utilities/skill-refactor` as a compatibility alias to avoid dual-source drift.

## Follow-up Guardrails
- Require package validation before release.
- Keep marketplace metadata aligned with plugin package roots.
- Keep aliases as symlinks to canonical plugin-owned skill paths.
