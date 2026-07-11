# Phase 1 First Migration Bucket Selection

Date: 2026-07-01

## Purpose

Record the first layout-migration bucket selected from the Phase 1 caller
inventory. The brand bucket is complete; this artifact does not authorize
another physical move.

## Reconciled Gate Evidence

- Command: `python3 Infrastructure/scripts/validation-and-linting/validate_repo_layout.py --json` -> baseline fail before Phase 0 repair with five tracked unclassified roots: `AI`, `codestyle`, `codex`, `coding-policy.json`, and `contracts`.
- Command: `UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest -q tests/test_repo_layout.py` -> baseline fail before Phase 0 repair because the current-repository policy test exposed those five blockers.
- Phase 0 repair explicitly classifies those roots and only the two known ignored Swift build-output links. A source symlink or an arbitrary ignored output remains blocking.
- Command: `python3 Infrastructure/scripts/validation-and-linting/generate_repo_layout_caller_inventory.py --actionable-only --output-json .harness/refactors/root-layout/caller-inventory.current.json --output-md .harness/refactors/root-layout/caller-inventory.current.md` -> pass.
- Command: `git diff --check -- Infrastructure/config/repo-layout.v1.json Infrastructure/tests/test_repo_layout.py .harness/refactors/root-layout/phase-1-first-bucket-selection.md` -> required after the repair.

## Inventory Snapshot

The actionable inventory reports these legacy-root counts:

| Root | References | Initial disposition |
| --- | ---: | --- |
| Infrastructure/ | 4905 | Too broad for first physical move. Requires SDK lifecycle wrapper planning. |
| scripts | 3376 | First compatibility-alias retirement candidate, not first physical root move. |
| Skills/ | 2596 | Foundry source move; too runtime-entangled for first bucket. |
| Plugins/ | 2230 | Foundry/plugin move; too route/runtime-entangled for first bucket. |
| Docs/ | 738 | SDK docs move; many atlas/plan/doc-link call sites. |
| GOVERNANCE | 214 | Compatibility alias retirement candidate after scripts. |
| plugins/ | 124 | Runtime/plugin compatibility surface; depends on plugin-root policy. |
| skills-system/ | 122 | Foundry/system-skills move; depends on Skill Factory overlays. |
| docs-policy.json | 63 | Compatibility alias retirement candidate after scripts/GOVERNANCE analysis. |
| brand/ | 38 | First physical migration bucket. |

## Completed First Physical Migration Bucket

`brand/` moved to `skills-sdk/brand/` in commit `ed9d3fd840e540b2e1a5b625bfaf5e8993b6c16f`.

Why:

- It is the smallest actionable legacy root in the inventory.
- Live source surface is small: `AGENTS.md`, `README.md`, and four brand mark assets.
- References are mostly docs/reference examples and deferred skill-context material.
- It exercises the `skills-sdk/` target layout with low blast radius before moving
  `Infrastructure/` or `Docs/`.

## First Compatibility-Alias Ratchet

Audit `scripts` first for compatibility retirement.

Why:

- It is an explicit deprecated compatibility alias in `repo-layout.v1.json`.
- The inventory shows public operator, CI, and hook references that must be
  classified before removal.
- It is not a source-root move, so it should be tracked as wrapper retirement,
  not mixed into the `brand/` physical migration.

## Brand Completion Record

The completed bucket established the following evidence:

1. `skills-sdk/brand` is the canonical Skills SDK brand path; a revived root
   `brand/` blocks unless an ADR explicitly reintroduces it.
2. `phase-2-brand-migration-report.md` is the authoritative bucket receipt.
3. The caller inventory is historical evidence for selecting later work; it
   does not reopen the completed brand move.
4. A future migration bucket requires a separate PM selection after the Phase 0
   repair gate passes.

## Non-Goals

- Do not move `Skills/`, `Plugins/`, `Infrastructure/`, or `Docs/` as part
  of the first bucket.
- Do not retire `scripts`, `GOVERNANCE`, or `docs-policy.json` in the same
  commit as the first physical move.
- Do not treat this bucket selection as PR, CI, Tessl, or runtime readiness.
