---
name: npm-workflow-discipline
description: "Manage deterministic npm dependency workflows and package script contracts. Use when users need lockfile discipline, npm ci-based CI installs, or consistent package.json script behavior."
metadata:
  skill-type: runbook
---

# npm Workflow Discipline

Reproducible npm workflows for dependency installs, lockfile hygiene, and script contracts that hold in CI and local development.

## When to use

- Creating or maintaining a Node.js project that uses npm.
- Fixing drift between `package.json` and `package-lock.json`.
- Hardening CI pipelines for deterministic dependency installs.
- Defining or enforcing `package.json` script contracts.

## Philosophy

- Treat dependency state as a contract, not a side effect.
- Keep CI installs immutable and predictable.
- Make `package.json` scripts explicit operational interfaces.

## Inputs

- `package.json` and `package-lock.json` state.
- Target environment (`local`, `CI`, or release job).
- Expected script contract (for example `lint`, `test`, `build`, `check`).
- Package update intent (`add`, `remove`, `upgrade`, or frozen install).

## Outputs

- A deterministic npm workflow recommendation with exact commands.
- Lockfile policy guidance tied to the current repo state.
- Script contract guidance that names required scripts and hooks.
- Validation outcome with clear status and `schema_version` in structured outputs.

## Procedure

### 1) Classify install intent

- Use `npm ci` for CI or any clean reproducible install.
- Use `npm install` only when intentionally changing dependencies.

### 2) Enforce lockfile discipline

- Lockfile must exist for automated installs.
- Dependency edits must produce reviewed `package-lock.json` changes.

### 3) Define script contracts

- Standardize stable script names.
- Use pre/post hooks intentionally and document side effects.

### 4) Verify contract

- Run deterministic install path and contract scripts.
- Fail on lockfile mismatch or missing required scripts.

## Constraints

- Redact secrets, tokens, credentials, and sensitive environment values by default.
- Do not suggest lockfile hand-edits.
- Do not use mutable installs in CI unless explicitly required by the user.
- Preserve repository package-manager choice (npm in this skill).

## Validation

- Confirm `npm ci` succeeds where reproducibility is required.
- Confirm lockfile/package manifest consistency before completion.
- Confirm script contracts run through expected entrypoints.
- Stop at the first hard failure and report blocker evidence.

## Anti-patterns

- Running `npm install` in CI as default.
- Committing `package.json` dependency changes without lockfile updates.
- Hand-editing `package-lock.json`.
- Using inconsistent script names across similar Node repos.
- Hiding critical checks inside undocumented lifecycle hooks.

## Rules

**Use `npm ci` for automation and clean installs**: `npm ci` requires a lockfile, removes existing `node_modules`, fails on lockfile mismatch, and does not rewrite lockfiles.

```bash
# CI / reproducible install
npm ci
```

**Treat lockfiles as required artifacts**: commit `package-lock.json` with dependency changes and never hand-edit it.

```bash
# Dependency change flow
npm install <pkg>
git add package.json package-lock.json
```

**Define script contracts clearly**: provide stable script names (`lint`, `test`, `build`, `check`) and use pre/post hooks intentionally.

```json
{
  "scripts": {
    "precheck": "npm run lint && npm run test",
    "check": "npm run build",
    "postcheck": "echo \"check complete\""
  }
}
```

## Patterns

### Install Modes

```bash
# Local dependency updates (updates lockfile)
npm install

# CI and clean reproducible installs (frozen lockfile)
npm ci
```

### Lockfile Discipline

```bash
# Verify lockfile consistency in review
git diff -- package.json package-lock.json
```

- If `package.json` changes dependencies, `package-lock.json` must change in the same commit.
- If only app code changes, lockfile should usually stay unchanged.

### Script Contract Baseline

```json
{
  "scripts": {
    "lint": "eslint .",
    "test": "vitest run",
    "build": "tsc -p tsconfig.json",
    "check": "npm run lint && npm run test && npm run build"
  }
}
```

### Safe Invocation in Automation

```bash
npm ci
npm run check --if-present
```

## Examples

- "Set up CI for this npm repo so installs are deterministic and fail on lockfile drift."
- "I updated dependencies locally; what exact lockfile and script checks should I run before commit?"
- "Standardize package scripts so every service has a consistent `check` contract."

## Failure mode

- If no lockfile exists, pause and request an explicit decision to generate and commit one.
- If scripts required by policy are missing, return partial and list exact missing script entries.

## Common mistakes

- Using `npm install` in CI where deterministic installs are required.
- Forgetting to commit `package-lock.json` after dependency updates.
- Hand-editing lockfiles instead of using npm commands.
- Defining scripts inconsistently across projects (`verify` vs `check` vs `ci`) with no contract.
- Relying on hidden side effects in `pre*` and `post*` scripts.

## References

- Contract: `references/contract.yaml`
- Eval cases: `references/evals.yaml`
