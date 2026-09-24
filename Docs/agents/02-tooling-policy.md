# Tooling and Command Policy

## Table of Contents

- [Tools](#tools)
- [Command preflight](#command-preflight)
- [Verified command style](#verified-command-style)
- [Package command map](#package-command-map)
- [Useful checks](#useful-checks)
- [Skill line-budget policy](#skill-line-budget-policy)

## Tools

- Use `rg`, `fd`, `jq` from repo workflow.
- Read `~/.codex/instructions/tooling.md` for the current authoritative tool stack.
- Use the tool's configured non-login shell; invoke Bash scripts explicitly
  with `bash`. Use a login shell only for an authorized, bounded investigation
  of shell startup behavior.

## Command preflight

- Run `bash Infrastructure/scripts/codex-preflight/codex-preflight.sh --stack auto --mode required` before multi-step, destructive, or path-sensitive work.
- The verified optional overrides are `--repo-fragment`, `--bins`, and `--paths`.
- Confirm the repository root with `git rev-parse --show-toplevel` and use
  `pwd -P` when the physical checkout path matters. Do not depend on path casing
  or a personal absolute checkout path.
- Verify required binaries with `which` before running installs.
- Confirm target paths with `fd` before destructive operations.
- Do not source `Infrastructure/scripts/codex-preflight/codex-preflight.sh` or call `preflight_repo`; the current script is a bash CLI, not a shell function library.

## Verified command style

- Keep command snippets backed by repo files before documenting them.
- Prefer one-shot, reproducible commands.
- For ad hoc YAML inspection, do not run bare system Python imports because
  system Python may not have PyYAML. Use the repo wrapper instead:
  `./bin/ask repo yaml-inspect <repo-relative-yaml> --json --robot`, with
  `--query <dotted.path>` when only one nested value is needed. The mise task
  `mise run yaml-inspect -- <repo-relative-yaml>` must route to that same
  wrapper. Treat a bare `python3 -c "import yaml"` failure as evidence to use
  the wrapper, not as permission to install or bypass dependencies.

## Package command map

- Repository root is configuration-oriented and has no package manager install step.
- Verified Python project roots from lockfiles:
  - `Infrastructure/`
- Use the Infrastructure Python project for SDK contract validation and repo-local Python dependency checks:
  - `uv run --project Infrastructure --group test python -m pytest <target>`
  - `uv run --project Infrastructure --group lint ruff check <target>`
- Skill directories are not npm package roots. Run package-manager commands
  only after verifying an active package manifest and lockfile at the target.
  Archived manifests under `Infrastructure/references/deferred-skill-context/`
  do not establish active package roots.

## Useful checks

- `bash Infrastructure/scripts/codex-preflight/codex-preflight.sh --stack auto --mode required`
- Projection refresh is a mutation, not a check. Use
  [the authorized refresh lane](/Docs/agents/04-validation.md#authorized-projection-refresh-only)
  only when that action and scope are explicitly selected.
- `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json`
- `python3 Infrastructure/scripts/skill-graph/plan_graph_lint.py .agents/PLANS.md`
- `bash Infrastructure/scripts/validation-and-linting/verify-work.sh` (repo-local wrapper preferred over `~/.codex` version)

## Skill line-budget policy

When a `SKILL.md` exceeds the 360-line split budget (`PD_SKILLMD_TOO_LONG`), do not delete important, still-valid context just to bring it under the limit. Move meaningful reusable detail to a focused reference under the skill directory and replace it with a one-line `Read when:` signpost.

Context removed during compression must be classified:

- `moved-to-reference`: still valid, reusable, and too bulky for `SKILL.md`.
- `superseded`: replaced by a newer compressed rule or reference.
- `intentionally-discarded`: stale, duplicated, unsafe, inappropriate, contradicted by newer guidance, or no longer part of the skill contract.
- `not-context`: formatting, navigation, repetition, or low-signal prose.

Blank lines, navigation-only TOC entries, repetition, and stale or inappropriate prose do not need preservation references. Owner rule: preserve knowledge, not word count.
