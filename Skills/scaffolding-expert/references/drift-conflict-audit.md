# Drift and Conflict Audit

Use this checklist to detect scaffolding drift and ownership conflict.

## Intake checklist

- locate instruction precedence files (`AGENTS.md` chain)
- when personal-style alignment is requested, run `bash Infrastructure/scripts/profile-dev-repos.sh --root ~/dev`
- identify canonical command entrypoints (`Infrastructure/scripts/*`, `justfile`, package scripts)
- identify policy contracts (environment file, check contract, CI required checks)
- identify generated-vs-source surfaces

## Drift classes

1. Ownership drift
- same policy represented in multiple non-generated files
- docs and scripts disagree on canonical command

2. Validation drift
- local validation wrappers differ from CI check names
- fast path claims success while deeper required checks fail

3. Toolchain drift
- mixed package-manager instructions (`npm` and `pnpm`) with no policy
- shell scripts declare `sh` but use Bash-only constructs
- Python flows bypass `uv` lock/sync contract

4. Projection drift
- generated docs or mirrored files no longer match source contract scripts

5. Over-structure drift
- strict controls in small repos with no operator upkeep
- policy layers that exist but are never executed

## Conflict resolution order

1. choose canonical source of truth
2. update projection/generation path, not just rendered outputs
3. align validation wrappers with CI required checks
4. remove or merge duplicate policy surfaces
5. rerun minimal lane validations

## Evidence template

For each finding include:
- `severity`: `critical|high|medium|low`
- `surface`: `instructions|validation|toolchain|projection|governance`
- `files`: concrete paths
- `symptom`: observable mismatch
- `fix`: smallest corrective action
