---
name: pnpm-manager
description: "Run pnpm workspace operations with recursive and filter selectors for scoped install, test, build, and publish flows. Use when a user needs pnpm monorepo command routing."
metadata:
  skill-type: runbook
---

# PNPM Manager

Use this skill for pnpm workspace orchestration, especially filter selectors, recursive execution, and multi-package command planning.

## When to use

- The repo uses pnpm workspaces/monorepo layout.
- The user asks to run commands across multiple workspace packages.
- The user needs change-based targeting (`changed since <commit>`).
- The user needs scoped installs/tests/builds with selector filters.

## Non-triggers

- Single-package npm-only release flows.
- Yarn/Bun migration asks without pnpm scope.

## Philosophy

- Scope first: preview targeted packages before broad execution.
- Prefer selective `--filter` commands over blanket recursive runs when possible.
- Treat recursive operations as high-impact and verify selectors early.

## Required inputs

- Workspace topology (root + package paths/names).
- Command target mode (`single`, `filtered`, `recursive`).
- Include/exclude root behavior requirements.
- Git ref context for changed-package selectors.

## Deliverables

- Exact pnpm command plan with selectors.
- Recursive/filtered execution rationale.
- Safety notes for broad workspace operations.
- Validation commands for package scope correctness.
- Structured outputs should include `schema_version` when a schema-bound contract is requested.

## Rules

**Use filter selectors for precise targeting**:

```bash
pnpm --filter <package_selector> <command>
pnpm --filter "...[<base-ref>]" test
pnpm --filter "{packages/**}[<base-ref>]" run build
```

**Use recursive mode for workspace-wide operations**:

```bash
pnpm -r install
pnpm -r exec jest
pnpm -r publish
```

**Confirm root-inclusion behavior per command class** before running scripts or releases.

## Workflow

1. Determine whether command should run on one package, a filtered subset, or all workspaces.
2. Prefer `--filter` for selective execution (by name/path/change set).
3. Use `-r` for full workspace orchestration when scope is intentional.
4. Validate selected package scope before destructive or release operations.
5. Execute and report per-package outcomes.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Avoid broad recursive destructive commands without explicit user confirmation.
- Do not assume changed-package selectors are valid without confirming git ref availability.

## Validation

- Scope preview: `pnpm -r list --depth 0`
- Filtered smoke check: `pnpm --filter <selector> run test`
- Recursive verification: `pnpm -r exec <cmd>` (non-destructive first)
- Stop on first blocker and report package selector + failing package.

## Failure mode

- If selector resolution is empty or invalid, stop and report resolved target set before running recursive commands.
- If one package fails under `-r`, report first failing package and command, then halt broad execution.

## Gotchas

- Recursive behavior differs by command class.
- Incorrect selectors can silently skip intended packages.
- Change-based selectors depend on valid git refs.

## Anti-patterns

- Running workspace-wide destructive commands without scope preview.
- Treating root-package behavior as uniform across commands.
- Using broad selectors when a precise package filter is available.

## Examples

- "Run tests only for workspace packages changed since our default branch (`<base-ref>`) with pnpm filters."
- "Build packages under `packages/**` changed in this branch and skip untouched projects."
- "Prepare a recursive publish plan for all workspaces and include preflight checks."

## References

- `references/contract.yaml`
- `references/evals.yaml`
- `references/context7-notes.md`

## See Also

| Skill | When to use together |
|---|---|
| [[npm-workflow-discipline]] | Keep workspace install/publish contracts deterministic |
| [[npm-release]] | Hand off package publish lanes after workspace validation |
| [[mise-tooling]] | Ensure runtime/tool versions are pinned before pnpm execution |
