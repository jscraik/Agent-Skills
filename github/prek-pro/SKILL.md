---
name: prek-pro
description: "Provide docs-backed guidance for configuring and troubleshooting `prek` hooks when users need to edit `prek.toml`, install shims, validate hook behavior, or migrate from pre-commit."
metadata:
  skill-type: runbook
---

# Prek Pro

## Table of Contents

- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Validation](#validation)
- [Failure mode](#failure-mode)
- [Constraints](#constraints)
- [Gotchas](#gotchas)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [See also](#see-also)

Guide for repository-local `prek` operations: installing and validating git-hook shims, updating `prek.toml`, and debugging hook-stage behavior with current docs as source of truth.

## When to use

- Use when users ask to configure, fix, or review `prek.toml`.
- Use when users ask about `prek install`, `prek run`, `prek validate-config`, or cache operations.
- Use when migrating from `.pre-commit-config.yaml` to `prek`.
- Use when hook stages (`pre-commit`, `pre-push`, `commit-msg`) behave unexpectedly.
- Do not use for non-`prek` CI/CD systems (route to `circleci` or repo-specific CI skills).

## Required inputs

- Repository root and target config path (`prek.toml` unless overridden).
- Requested operation: `install`, `run`, `validate`, `migrate`, or `audit`.
- Hook scope (all hooks, specific hook type, or specific hook id).
- Whether destructive cache cleanup is allowed (`prek cache clean`).
- Current failure signal (exact stderr/log) when debugging.

## Deliverables

1. A minimal command plan with exact `prek` commands.
2. Any `prek.toml` edits with rationale tied to current docs.
3. Validation evidence: exact commands run plus pass/fail/blocked outcomes.
4. Explicit note of assumptions, inferred behavior, and unresolved risks.
5. For structured responses, include `schema_version`.

## Philosophy

- Prefer current docs over memory for drift-prone command semantics.
- Make the smallest safe config change, then verify immediately.
- Separate install-time issues (shim placement) from run-time issues (hook execution).
- Keep guidance command-first and reproducible.

## Workflow

### 1) Baseline local state

- Read `prek.toml` and adjacent hook entrypoints (`Makefile`, setup scripts).
- Check for conflicting legacy config such as `.pre-commit-config.yaml`.
- Determine if issue is install-time (shims), run-time (hook execution), or config-time (schema/stages).

### 2) Retrieve current docs with Context7

- Resolve library id via Context7 as `/j178/prek`.
- Pull focused docs for the active task:
  - install/run commands
  - config keys (`default_install_hook_types`, local hooks, `stages`)
  - validation and cache commands
- Treat docs as primary source for command flags and behavior.

### 3) Apply the smallest viable fix

- For install issues, use `prek install` with explicit hook type(s) when needed.
- For config issues, edit only the minimal keys/sections in `prek.toml`.
- For execution issues, use targeted `prek run` scope before `--all-files`.
- For cache issues, prefer `prek cache gc` before `prek cache clean`.

### 4) Verify and report

- Run config validation first, then hook execution checks.
- Report exact commands and outcomes.
- Highlight any required follow-up (for example: reinstall shims after config change).

## Validation

- Start with:
  - `prek validate-config prek.toml`
- Then choose one or more based on scope:
  - `prek run`
  - `prek run --all-files`
  - `prek run --stage pre-push`
  - `prek install`
  - `prek install --hook-type pre-commit --overwrite`
- Cache diagnostics/maintenance:
  - `prek cache dir`
  - `prek cache size --human`
  - `prek cache gc --dry-run`

Fail fast: stop at first failed gate, fix, and rerun.

## Failure mode

- If Context7 cannot resolve `/j178/prek`, pause and request clarification before applying edits.
- If `prek` binary is missing, report blocker and provide install-path guidance only.
- If config validation fails and schema intent is ambiguous, ask for explicit intended hook lifecycle before patching.

## Constraints

- Use Context7 docs (`/j178/prek`) before giving version-sensitive flag advice.
- Do not run destructive cache operations (`prek cache clean`) without explicit user approval.
- Do not claim validation success unless commands were actually executed.
- Avoid secret/credential handling entirely for this skill.

## Gotchas

- `default_install_hook_types` controls which shims are installed; `stages` controls when hooks are eligible to run.
- Updating `prek.toml` does not update `.git/hooks` shims until `prek install` runs.
- `prek run --all-files` can be expensive; start with targeted runs for faster diagnosis.
- `prek cache clean` is destructive; prefer `prek cache gc` first.
- During migration, keeping both `prek.toml` and `.pre-commit-config.yaml` can create operator confusion.

## Anti-patterns

- Guessing command flags without docs retrieval.
- Editing unrelated hook sections when one hook id is failing.
- Running destructive cache cleanup without explicit request.
- Reporting validation success without command evidence.

## Examples

- "Make our `pre-push` hooks install by default in `prek.toml` and verify."
- "Why does `hooks-pre-commit` pass but `pre-push` never runs?"
- "Migrate this repo from `.pre-commit-config.yaml` to `prek.toml` safely."
- "Audit our local hook entries and stage configuration for drift."

## See also

| Skill | When to use |
|---|---|
| [[toml]] | For fine-grained TOML editing discipline while changing `prek.toml`. |
| [[context7]] | For current external docs retrieval and version-sensitive flag behavior. |
| [[coding-harness]] | For repo bootstrap flows that include `prek` installation and checks. |

**Topic map:** [[agent-ops]]

## References and assets

- Command and behavior contract: `references/contract.yaml`
- Eval cases: `references/evals.yaml`
- Context7 doc basis and extracted command matrix: `references/doc-basis.md`
- UI metadata: `agents/openai.yaml`
