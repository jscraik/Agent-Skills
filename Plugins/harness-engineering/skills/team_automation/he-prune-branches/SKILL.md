---
name: he-prune-branches
description: Review and prune stale branches safely. Use when branch cleanup needs evidence, protected-branch caution, PR awareness, and non-destructive recommendations.
metadata:
  skill-type: team_automation
---

# Harness Engineering Prune Branches

## Philosophy

- Discover first, delete second.
- Start with one repository as the smallest viable boundary and keep scope tight.
- Require one explicit yes/no confirmation for the full candidate branch set.
- Remove associated non-root worktrees before deleting branches.

## When to Use

- The user asks to prune local branches whose remote tracking refs are gone.
- The user asks to clean stale local branches before implementation or release work.
- Branch hygiene includes worktree cleanup in the same repository.

## Failure Modes

- If the path is not a git repository, return blocked with the exact path issue.
- If discovery fails, return blocked with command/error output.
- If the user declines deletion, stop cleanly and report no changes.
- If one branch fails deletion, continue remaining branches and report partial completion.

## Inputs

- Request, artifacts, repo context, and linked Linear issues.

## Outputs

- `schema_version: 1` when structured; result, validation, blockers, and next Harness Engineering action.

## Procedure

1. Verify the target path is a git repository, then run stage-local discovery:

```bash
bash Plugins/harness-engineering/skills/team_automation/he-prune-branches/scripts/clean-gone
```

2. If output is `__NONE__`, report that no stale branches were found and stop.
3. Present the full candidate branch set as one deletion batch.
4. Ask one yes/no confirmation for deleting the entire set.
5. If the answer is no, stop without deleting anything.
6. On approval, for each branch:

```bash
git worktree list
git worktree remove --force "<worktree_path>"
git branch -D "<branch>"
```

7. Remove associated worktrees only when they are not the main repository root.
8. Report each branch outcome, final totals, and partial failures.

Use references only when additional edge handling is needed.

## Validation

- Verify discovery output is captured.
- Verify `__NONE__` path exits without deletion.
- Verify explicit yes/no confirmation before any destructive action.
- Verify worktree removal happens before branch deletion when applicable.
- Verify active branch is never queued for deletion.
- Verify root repository worktree is never removed as part of cleanup.
- Fail fast: stop at the first failed validation gate and do not proceed with deletion.

## Constraints

- Redact secrets and sensitive filesystem details in shared output.
- Never delete branches without explicit user confirmation.
- Continue inline when helper-role delegation is unavailable; emit manual role guidance instead of blocking.
- Do not remove important context for budget trimming; move it to references and index it in `../../../references/deferred-context-index.md`.

## Anti-Patterns

- Deleting branches before showing the full candidate set.
- Skipping confirmation for convenience.
- Ignoring associated worktrees and leaving stale worktree directories behind.
- Deleting branches one at a time behind separate confirmation prompts.
- Stopping on the first branch failure without reporting partial results.

## Full Context

- Assets: [icon-small.png](./assets/icon-small.png), [icon-large.png](./assets/icon-large.png)
- Subagent call contract: [../../../references/subagent-call-contract.md](../../../references/subagent-call-contract.md)

## Examples

- "Can you inspect local branches whose remotes are gone and show me the exact deletion batch before removing anything?"
- "Help me clean stale worktrees and branches in this repo, but ask once before any destructive action."
- "Review my local branch list and tell me which branches are safe candidates to prune after checking PR status."
