---
source: https://docs.coderabbit.ai/finishing-touches/resolve-merge-conflict
---

# Resolve Merge Conflicts

Automatically detect and resolve merge conflicts in pull requests with a single click or comment.

Open Beta
Pro Plan
Merge conflicts interrupt review momentum and often require context-switching between branches to understand what each side was trying to accomplish. CodeRabbit detects conflicts during PR review and can resolve them automatically: it analyzes the intent behind both sets of changes and commits the result as a proper merge commit to your branch.

## Platform support

Merge conflict resolution is available on the following platforms:

### GitHub

### GitLab

## Usage

When CodeRabbit detects conflicts, it adds a resolution option to the PR summary comment.

### PR comment command

Comment `@coderabbitai resolve merge conflict` in any PR or merge request to trigger resolution on GitHub and GitLab

### Finishing Touches checkbox

On GitHub, check the **Resolve merge conflicts** box in the CodeRabbit Walkthrough for one-click resolution

Both methods commit the resolved changes directly to your branch.

## How it works

**1. Detection**

During PR review, CodeRabbit simulates the merge in a sandbox without modifying your working tree. If conflicts are found, they are listed in the summary comment alongside the resolution trigger.

**2. Intent analysis**

When resolution is triggered, CodeRabbit clones the repository and examines each conflicting file. For each file, it determines what problem the changes on each branch were solving (not just what changed, but why), so the resolution reflects the actual goals of both sides.

**3. Resolution**

CodeRabbit uses an AI agent that reasons through each conflict from first principles. Rather than applying rules, it reads both versions of the conflicting code alongside the full context of what each branch was trying to accomplish, then makes a judgment call about what the correct unified outcome should be. The agent works directly inside the repository: inspecting git state, reading files, running git commands, and editing code. It can make changes beyond the conflict hunks themselves if the resolution requires it, for example, restructuring code to accommodate both sets of changes rather than just picking one. Where the correct resolution is genuinely ambiguous or involves security-critical logic, the agent explicitly declines and flags the conflict for manual review instead of guessing.

**4. Validation**

CodeRabbit verifies that no conflict markers remain, that the merge index is fully cleared, and runs the repository's build and lint commands to surface any errors introduced by the resolution.

**5. Commit**

The resolved changes are committed to your branch as a proper merge commit with two parents (your branch and the base branch), so git history accurately reflects the merge.

## When CodeRabbit won't auto-resolve

CodeRabbit will decline to resolve a conflict if doing so incorrectly could cause serious harm:

- **Security-critical code:** authentication logic, encryption, secrets handling, or access control
- **Fundamentally incompatible business logic:** where both changes make mutually exclusive architectural decisions that a human needs to decide

When this happens, the entire resolution attempt is aborted and no commit is created for any files. CodeRabbit posts a comment identifying which file it declined and the specific reason.

The bar for declining is intentionally high. CodeRabbit will attempt to resolve the vast majority of conflicts automatically.

## Command reference

```
@coderabbitai resolve merge conflict
```

## Troubleshooting

**Resolution failed: branch was updated during the process**

If your branch receives a new commit while resolution is running, CodeRabbit aborts to avoid overwriting the incoming changes. Wait for the branch to stabilize, then trigger resolution again.

**Some conflicts were not resolved**

If CodeRabbit declines to resolve any file, no commit is created, not even for the files it could resolve. Check the resolution comment for the declined files and the specific reason for each. Resolve those files manually, push the changes, then trigger resolution again for the remaining conflicts.

**Resolution ran but nothing was committed**

This can occur if the agent could not produce a clean staged result. Try triggering resolution again. If it happens repeatedly, resolve the conflicts manually.

## What's next

- **Finishing Touches overview** - See all available finishing touches and how to trigger them from any PR
- **Autofix** - Automatically implement fixes for unresolved CodeRabbit review findings
- **Custom recipes** - Define reusable, named recipes that encode your team's repeated tasks into one-click agentic actions
