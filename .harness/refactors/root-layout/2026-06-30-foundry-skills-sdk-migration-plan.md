# Foundry And Skills SDK Layout Migration Plan

Date: 2026-06-30

## Purpose

Move the repository toward the accepted foundry/ and skills-sdk/ target layout
without breaking existing skill, plugin, SDK, Tessl, PR, or runtime projection
lanes.

This plan is a migration control artifact. It does not authorize a mass move.
Each phase must pass the repo layout validator before and after path changes.

## Current State

The repo currently keeps canonical source, SDK lifecycle implementation,
runtime projections, evidence, generated artifacts, and compatibility aliases
in the same top-level namespace.

The accepted target architecture is recorded in:

- .harness/decisions/2026-06-30-repo-shape-foundry-skills-sdk-layout-adr.md
- Infrastructure/config/repo-layout.v1.json

The current validator accepts the legacy-compatible layout with three expected
deprecated compatibility aliases:

- GOVERNANCE
- docs-policy.json
- scripts

## Target Shape

    foundry/
      skills/
      plugins/
      system-skills/

    skills-sdk/
      Infrastructure/
      docs/
      artifacts/
      brand/

    .harness/
      decisions/
      evidence/
      plan/
      quality/
      reports/
      research/

    .agents/
      runtime projections only

    ROOT
      governance, bootstrap, and compatibility wrappers only

## Migration Principles

1. Contract first, movement second.
2. Preserve package internals. Do not reshape SKILL.md package layout while
   moving repository roots.
3. Preserve runtime projections. .agents/ remains runtime-facing and must not
   become the editable source root.
4. Preserve compatibility entrypoints until wrappers and callers prove the new
   path.
5. Regenerate generated artifacts instead of choosing stale conflict sides when
   a generator exists.
6. Do one owner bucket per commit. Do not mix foundry moves with Skills SDK
   engine moves, evidence moves, or PR cleanup.
7. Keep local proof, hosted PR proof, Tessl proof, and runtime installed proof
   separate.

## Phase 0: Stabilize Current Branch

Exit criteria:

- Current PR stabilization is either landed or explicitly parked.
- Dirty worktree buckets are triaged by owner.
- No unresolved merge conflict strategy remains for the active PR branch.
- The layout validator passes on current HEAD.

Required command:

    python3 Infrastructure/scripts/validation-and-linting/validate_repo_layout.py --json

## Phase 1: Add Compatibility Wrappers And Call-Site Inventory

Do not move files yet.

Inventory every caller for the legacy roots:

- Skills/
- Plugins/
- plugins/
- skills-system/
- Infrastructure/
- Docs/
- artifacts/
- brand/
- scripts
- GOVERNANCE
- docs-policy.json

Classify each caller:

- internal Python import
- shell command
- ask CLI route
- CI workflow
- pre-commit or hook
- docs/reference link
- generated artifact input
- runtime projection input
- Tessl staging input
- external operator entrypoint

Add wrappers only where an existing public entrypoint must survive the move.

Exit criteria:

- Caller inventory exists as a repo artifact.
- Wrapper policy is recorded.
- Layout validator still passes.
- No physical root move has happened.

Phase 1 checkpoint artifacts:

- .harness/refactors/root-layout/caller-inventory.current.json
- .harness/refactors/root-layout/caller-inventory.current.md
- .harness/refactors/root-layout/compatibility-wrapper-policy.md
- .harness/refactors/root-layout/phase-1-first-bucket-selection.md

Completed first-bucket decision:

- First physical migration bucket: `brand/` -> `skills-sdk/brand/`, completed
  by `ed9d3fd840e540b2e1a5b625bfaf5e8993b6c16f` with receipt
  `.harness/refactors/root-layout/phase-2-brand-migration-report.md`.
- First compatibility-alias retirement candidate: scripts.

## Phase 2: Foundry Source Migration

Move source package roots one bucket at a time:

1. Skills/ -> foundry/skills/
2. Plugins/ -> foundry/plugins/
3. plugins/ -> foundry/plugins-runtime-compat/ or another explicitly named
   compatibility surface if the links are runtime cache/projection state.
4. skills-system/ -> foundry/system-skills/

For each bucket:

- Move with git history preservation.
- Update ask CLI path resolution.
- Update skillset manifest generation.
- Update Skill Factory routing and overlays.
- Update runtime projection sync.
- Update package verification fixtures.
- Preserve old public entrypoints with wrappers or classified compatibility
  aliases until callers are migrated.

Exit criteria per bucket:

- Layout validator passes.
- Package verification passes for at least one representative moved package.
- Runtime projection proof shows .agents links point at the new canonical source
  or documented compatibility alias.
- No unclassified symlink exists.

## Phase 3: Remaining Skills SDK Lifecycle Migration

Move SDK lifecycle surfaces one bucket at a time:

1. Infrastructure/ -> skills-sdk/Infrastructure/
2. Docs/ -> skills-sdk/docs/
3. artifacts/ -> skills-sdk/artifacts/

The `brand/` bucket is already complete and must not be selected again. The
Phase 0 layout baseline remains a prerequisite for selecting any remaining
bucket.

For each bucket:

- Update ./bin/ask wrapper resolution.
- Update CI and repo validation scripts.
- Update schemas and capability matrix references.
- Update HTML Atlas generation source paths.
- Update Tessl staging wrappers and evidence paths only if they are SDK-owned.
- Preserve root wrappers for public commands until proof shows callers have
  moved.

Exit criteria per bucket:

- Layout validator passes before and after.
- Repo closeout or equivalent wrapper gate passes.
- A representative Skills SDK command path runs from the root.
- HTML Atlas generation consumes the new path or records a compatibility source.

## Phase 4: Compatibility Alias Retirement

Retire root compatibility aliases only after caller evidence is clean.

Retirement order:

1. scripts
2. docs-policy.json
3. GOVERNANCE

For each alias:

- Prove no active caller requires the alias.
- Remove or replace the alias.
- Update repo-layout.v1.json to remove the deprecated allowance.
- Add a regression test that an unknown replacement alias blocks.

Exit criteria:

- Layout validator passes with fewer deprecated warnings.
- The warning count ratchets down and never increases without an ADR.

## Phase 5: CI Ratchet

After the migration is proven locally, add the layout validator to the repo's
normal validation surface.

Recommended gate placement:

- repo closeout changed-files lane for layout-sensitive changes;
- PR structure gate for top-level paths and symlinks;
- pre-migration checklist for root moves.

Exit criteria:

- The validator runs in at least one deterministic CI or wrapper lane.
- Unknown top-level tracked surfaces and unknown symlinks fail before review.

## Explicit Non-Goals

- Do not redesign skill package internals.
- Do not collapse Tessl registry shape into repository source shape.
- Do not make .agents canonical source.
- Do not move dirty worktree buckets as part of this plan.
- Do not treat layout validator pass as PR merge readiness.

## Pre-Migration Gate

Before any physical move, run:

    python3 Infrastructure/scripts/validation-and-linting/validate_repo_layout.py --json
    bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest -q tests/test_repo_layout.py

The move can start only when both commands pass and the active branch has a
clean, intentional migration scope.
