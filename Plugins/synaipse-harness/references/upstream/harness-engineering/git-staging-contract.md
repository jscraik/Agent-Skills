# Git Staging Contract

Read when: an HE stage writes or updates repo files, durable `.harness/**`
artifacts, review reports, generated media references, or validation artifacts.

## Intent

HE stages should not leave their own new artifacts untracked after a completed
turn. Staging is a handoff hygiene step, not a commit step.

## Required Closeout Flow

- Capture the dirty state before writing when possible with `git status --short`.
- After artifact writes and validation finish, identify only files created or
  modified by the current HE stage.
- Run `git add -- <path>...` for those files only.
- Re-check `git status --short` and report `git_staging_status`,
  `staged_paths`, `unstaged_unrelated_paths`, and `blocked_reason`.
- If staging fails because `.git` write access, permissions, hooks, or repo
  state are blocked, preserve artifact paths in the handoff and explain the
  smallest recovery step.

## Safety Rules

- Do not run `git add .`, `git add -A`, or broad path globs from a dirty repo.
- Leave unrelated user edits, generated cache churn, secrets, credentials, local
  env files, and files outside the selected HE scope unstaged.
- Do not commit unless the user explicitly asks for commit/push/PR.
- Do not use staging as validation proof. Validation still needs commands,
  artifact checks, review evidence, or explicit blockers.
- If the stage writes outside `.harness/**`, name why that path belongs to the
  selected slice before staging it.
- If multiple agents worked in the same repo, stage only the paths this stage can
  attribute to its own turn.

## Closeout Example

```text
git add -- .harness/specs/2026-05-13-JSC-313-ledger-spec.md
git_staging_status: staged
staged_paths:
  - .harness/specs/2026-05-13-JSC-313-ledger-spec.md
unstaged_unrelated_paths:
  - src/user-local-experiment.ts
```

## Non-Goals

- This contract does not require committing, pushing, opening a PR, or cleaning
  unrelated dirty work.
- This contract does not replace repo-specific closeout or validation commands.
