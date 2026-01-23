---
name: release
description: "Create and publish a new project release (semver) when you need to cut a main-branch, clean-tree release via just release X.Y.Z for Cargo publish and git tag creation."
---

# Release

## Compliance
- Follow the Gold Industry Standard and repo release policies.

## When to Use
- You need to ship a new version using `just release X.Y.Z`.
- The release must be semver-valid, greater than current, and performed from `main`.
- The flow includes Cargo.toml version bumps, lockfile update, tag, and crates.io publish.

## Inputs
- Target version `X.Y.Z` (prompt if missing).
- Repo root and current version (read from `Cargo.toml`).
- Confirmation you are on `main` with a clean working tree.
- Cargo credentials available (`cargo login` or `CARGO_REGISTRY_TOKEN`).

## Outputs
- A completed release run (or a clear stop with error context).
- A new version commit + tag (created by `just release`).
- Confirmation that publish/tag steps were invoked.

## Principles
- Validate before action: semver and version ordering come first.
- Single-threaded, fail-fast: stop immediately on any error.
- Keep the release path minimal and reproducible.

## Procedure
1) Confirm branch and clean state.
   - `git branch --show-current` should be `main`.
   - `git status -sb` should be clean.
2) Determine current version and validate the target.
   - Read `Cargo.toml` current version.
   - Ensure target is valid semver and greater than current.
3) Confirm credentials are present (do not print secrets).
   - `cargo login` is configured OR `CARGO_REGISTRY_TOKEN` is set.
4) Run the release.
   - `just release X.Y.Z`
5) If any step fails, stop and report the error without retrying blindly.

## Examples
```bash
just release 1.4.2
```

## Validation
- Fail fast: stop at the first failed check or command.
- `git status -sb` shows clean tree and `main` before running.
- `git tag --list "vX.Y.Z"` returns nothing before release.
- `just release X.Y.Z` completes without errors.

## Anti-patterns
- Releasing from a dirty working tree or non-`main` branch.
- Skipping version validation or using a non-semver version.
- Re-running `just release` after a failure without fixing the root cause.

## Constraints
- Redact secrets/PII by default.
- Keep `name` and `description` single-line YAML scalars (quote if needed).
- Do not add new dependencies without explicit user approval.

## Resources (optional)
- `references/evals.yaml`
