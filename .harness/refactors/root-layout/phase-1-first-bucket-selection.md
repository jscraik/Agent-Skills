# Phase 1 First Migration Bucket Selection

Date: 2026-07-01

## Purpose

Choose the first layout-migration bucket from the Phase 1 caller inventory,
after proving the current layout policy passes. This artifact selects the next
bounded migration target; it does not authorize moving files in this slice.

## Current Gate Evidence

- Command: `UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest -q tests/test_repo_layout.py` -> pass, 12 passed.
- Command: `python3 Infrastructure/scripts/validation-and-linting/validate_repo_layout.py --json | jq '{status, summary, blockers: [.findings[] | select(.blocking) | {code,path,message}], warnings: [.findings[] | select(.severity=="warning") | {code,path,classification}]}'` -> pass, status=pass, blocking_count=0, warning_count=3.
- Command: `python3 Infrastructure/scripts/validation-and-linting/generate_repo_layout_caller_inventory.py --actionable-only --output-json .harness/refactors/root-layout/caller-inventory.current.json --output-md .harness/refactors/root-layout/caller-inventory.current.md` -> pass.
- Command: `git diff --check -- Infrastructure/config/repo-layout.v1.json Infrastructure/tests/test_repo_layout.py Infrastructure/scripts/validation-and-linting/generate_repo_layout_caller_inventory.py .harness/refactors/root-layout/compatibility-wrapper-policy.md .harness/refactors/root-layout/caller-inventory.current.md .harness/refactors/root-layout/caller-inventory.current.json` -> pass.

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

## Selected First Physical Migration Bucket

Move `brand/` to `skills-sdk/brand/` first.

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

## Required Next Bucket Plan

Before moving `brand/`:

1. Confirm whether all `brand/` references should become `skills-sdk/brand/`
   or whether external examples intentionally describe target repositories that
   still use `brand/`.
2. Move `brand/` with git history preservation.
3. Update `Infrastructure/config/repo-layout.v1.json` so `brand` no longer
   appears as a legacy root once the move is complete.
4. Add or update tests proving `skills-sdk/brand` classifies under
   `skills_sdk` and a revived root `brand/` blocks unless explicitly
   reintroduced by ADR.
5. Regenerate the caller inventory after the move.
6. Run the pre/post migration gate:
   `python3 Infrastructure/scripts/validation-and-linting/validate_repo_layout.py --json`
   and
   `UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest -q tests/test_repo_layout.py`.

## Non-Goals

- Do not move `Skills/`, `Plugins/`, `Infrastructure/`, or `Docs/` as part
  of the first bucket.
- Do not retire `scripts`, `GOVERNANCE`, or `docs-policy.json` in the same
  commit as the first physical move.
- Do not treat this bucket selection as PR, CI, Tessl, or runtime readiness.
