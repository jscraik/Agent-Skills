---
source: https://docs.coderabbit.ai/finishing-touches/autofix
---

# Autofix

Automatically implement fixes for unresolved CodeRabbit review findings.

Open Beta | Pro Plan

Autofix helps you resolve review feedback faster by applying code changes for unresolved CodeRabbit findings in your pull request. Use Autofix when you want CodeRabbit to implement fixes automatically, then review the resulting commit or stacked PR.

## Usage

You can trigger Autofix using Pull Request comments or with `Finishing Touches` Autofix checkbox in CodeRabbit's PR Walkthrough.

Open a separate PR with fixes:

```
@coderabbitai autofix stacked pr
```

Apply fixes to your current PR branch:

```
@coderabbitai autofix
```

### Pull request review checkbox triggers

On supported GitHub PR flows, CodeRabbit renders an expanded **Autofix (Beta)** section with interactive checkboxes in the pull request review comment (alongside actionable comments).

- **Push a commit to this branch:** Runs Autofix and commits fixes to the current PR branch.
- **Create a new PR with the fixes:** Runs Autofix and opens a stacked PR with the generated changes.

These checkbox actions map to the same Autofix execution paths as the PR comment commands.

## How it works

1. **Trigger autofix** - Comment `@coderabbitai autofix` or `@coderabbitai autofix stacked pr` in a PR thread. On supported GitHub flows, you can also use the **Autofix (Beta)** checkbox section in the pull request review comment.

2. **Collect fix instructions** - CodeRabbit scans unresolved review threads started by CodeRabbit and gathers fix instructions from the **Prompt for AI Agents** blocks.

3. **Generate and verify fixes** - The coding agent applies fixes, then runs a repository setup + build verification step. Even if verification fails, the generated changes are still delivered so you can continue iterating.

4. **Deliver the result** - CodeRabbit either pushes a commit to the current branch or opens a stacked PR, depending on which command or checkbox option you selected.

## Output options

### Commit to current branch

Use `@coderabbitai autofix` to push a commit directly to your PR branch. This is the fastest path when you want fixes in the same review.

### Create stacked PR

Use `@coderabbitai autofix stacked pr` to open a new branch off your working branch and submit a separate PR targeting it. This lets you review the autofix changes independently.

## Scope and limitations

- Autofix runs only on pull request events.
- Autofix only processes unresolved CodeRabbit review threads with valid fix instructions.
- The feature is currently in beta and is rolled out progressively.
- If no valid unresolved instructions are found, Autofix skips execution and reports that no fixes were applied.
- Autofix may be rate-limited. If limits are exceeded, CodeRabbit responds with a wait time before retrying.

## Command reference

```
@coderabbitai autofix
@coderabbitai autofix stacked pr
```

Also supported aliases include `auto-fix` and `auto fix` forms, with or without `stacked pr`.

## Troubleshooting

**Autofix says no fixes were found:** Autofix only acts on unresolved CodeRabbit review comments that include structured fix instructions. Resolve state, missing instruction blocks, or non-CodeRabbit threads can lead to no-op runs.

**Autofix completed but verification failed:** Build/verification can fail after code edits. In this case, CodeRabbit still keeps and delivers the generated autofix changes so you can continue iteration.

**Stacked PR option failed:** Stacked PR creation depends on platform/API support. If unsupported, use `@coderabbitai autofix` to push fixes to the current branch.
