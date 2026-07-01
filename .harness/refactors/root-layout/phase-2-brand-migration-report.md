# Phase 2 Brand Migration Report

Date: 2026-07-01

## Purpose

Record the first physical Skills SDK layout migration bucket:
`brand/` -> `skills-sdk/brand/`.

This report covers only the brand bucket. It does not move `Infrastructure/`,
`Docs/`, `Skills/`, `Plugins/`, `plugins/`, or `skills-system/`, and it
does not retire `scripts`, `GOVERNANCE`, or `docs-policy.json`.

## Source Move

Moved with git history preservation:

- `brand/AGENTS.md` -> `skills-sdk/brand/AGENTS.md`
- `brand/README.md` -> `skills-sdk/brand/README.md`
- `brand/brand-mark.png` -> `skills-sdk/brand/brand-mark.png`
- `brand/brand-mark.webp` -> `skills-sdk/brand/brand-mark.webp`
- `brand/brand-mark@2x.png` -> `skills-sdk/brand/brand-mark@2x.png`
- `brand/brand-mark@2x.webp` -> `skills-sdk/brand/brand-mark@2x.webp`

## Contract Updates

- `Infrastructure/config/repo-layout.v1.json` now treats `skills-sdk/brand`
  as the canonical Skills SDK brand path and no longer allows root `brand` as
  a legacy path.
- `Infrastructure/tests/test_repo_layout.py` proves `skills-sdk/brand`
  classifies through the `skills_sdk` layout section and revived root
  `brand/` blocks.
- `skills-sdk/brand/AGENTS.md` now points to the correct repository-root
  instruction and vocabulary paths.
- `skills-sdk/brand/README.md` now uses `./skills-sdk/brand/...` in the root
  README footer snippet.

## Reference Policy

Some deferred skill-context files still mention `brand/` as an example path
inside target repositories. Those are not repo-root layout references and should
not be rewritten in this bucket unless their owning skill is migrated or
refreshed.

## Required Validation

Run after this bucket:

- `UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest -q tests/test_repo_layout.py`
- `python3 Infrastructure/scripts/validation-and-linting/validate_repo_layout.py --json`
- `python3 Infrastructure/scripts/validation-and-linting/generate_repo_layout_caller_inventory.py --actionable-only --output-json .harness/refactors/root-layout/caller-inventory.current.json --output-md .harness/refactors/root-layout/caller-inventory.current.md`
- `git diff --check -- brand/AGENTS.md brand/README.md brand/brand-mark.png brand/brand-mark.webp brand/brand-mark@2x.png brand/brand-mark@2x.webp skills-sdk/brand/AGENTS.md skills-sdk/brand/README.md skills-sdk/brand/brand-mark.png skills-sdk/brand/brand-mark.webp skills-sdk/brand/brand-mark@2x.png skills-sdk/brand/brand-mark@2x.webp`
