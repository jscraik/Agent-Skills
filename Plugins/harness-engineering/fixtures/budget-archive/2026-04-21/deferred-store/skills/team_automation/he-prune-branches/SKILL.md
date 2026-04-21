---
name: he-prune-branches
description: Automate stale local git branch cleanup with worktree-aware deletion and explicit confirmation gates. Use this skill when the user asks to prune local branches whose remote tracking refs are gone.
metadata:
  skill-type: team_automation
---

# Harness Engineering Prune Branches

Progressive-disclosure entrypoint for the Harness Engineering branch-hygiene stage.

## Philosophy

- Discover first, delete second.
- Start with one repository as the smallest viable boundary and keep scope tight.
- Require one explicit yes/no confirmation for the full candidate branch set.
- Remove associated non-root worktrees before deleting their branches.
- Report cleanup outcomes branch by branch instead of only summarizing at the end.

## When to Use

- The user asks to prune local branches whose remote tracking refs are gone.
- The user asks to clean stale local branches before implementation or release work.
- Branch hygiene includes worktree cleanup in the same repository.
- Typical triggers include "clean up branches", "delete gone branches", "prune local branches", and "clean stale branches and worktrees".

## Inputs

- Target repository path.
- Permission to run git discovery commands in that repository.
- Yes/no confirmation posture for destructive cleanup.
- Permission to remove associated worktrees for stale branches.

## Outputs

Return a structured summary when needed:
- `schema_version: 1`
- `repo_path`
- `discovery_status` (`found|none|blocked`)
- `candidate_branches`
- `confirmation` (`approved|declined|not_asked`)
- `cleanup_results`
- `summary`

Each `cleanup_results` item should include:
- `branch`
- `worktree_removed` (`true|false`)
- `branch_deleted` (`true|false`)
- `error` (`string|null`)

## Failure Modes

- If the path is not a git repository, return blocked with the exact path issue.
- If discovery fails, return blocked with command/error output.
- If the user declines deletion, stop cleanly and report no changes.
- If one branch fails deletion, continue remaining branches and report partial completion.

## Procedure

1. Verify the target path is a git repository, then run stage-local discovery:

```bash
bash Plugins/harness-engineering/skills/team_automation/he-prune-branches/scripts/clean-gone
```

2. If output is `__NONE__`, report that no stale branches were found and stop.
3. Otherwise, capture the full candidate branch set and present it as one deletion batch.
4. Ask one yes/no confirmation question for deleting the entire set. Use the platform's blocking question tool when available; otherwise ask inline and wait before proceeding.
5. If the answer is no, stop without deleting anything.
6. On approval, for each branch:

```bash
git worktree list
git worktree remove --force "<worktree_path>"
git branch -D "<branch>"
```

7. Remove an associated worktree only when it exists and is not the main repository root.
8. Report each branch outcome as it happens, then report final cleanup totals and any partial failures.

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

- Redact secrets and sensitive filesystem details in shared output by default.
- Never delete branches without explicit user confirmation.
- Continue inline when helper-role delegation is unavailable; emit manual role guidance instead of blocking.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

Subagent routing contract:
- Stage policy source: [../../../references/routing-map.json](../../../references/routing-map.json)
- Human-readable routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Resolve role availability from `~/.codex/agents/manifest.json` before suggesting delegation.
- If required roles are missing, route creation/install to [../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md](../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md).

## Anti-Patterns

- Deleting branches before showing the full candidate set.
- Skipping confirmation for convenience.
- Ignoring associated worktrees and leaving stale worktree directories behind.
- Deleting branches one at a time behind separate confirmation prompts.
- Stopping on the first branch failure without reporting partial results.

## Examples

- "When the user asks, `Can you clean up my local branches whose remotes are gone, but show me the full list before deleting anything?`"
- "Please inspect the linked worktrees first, then remove the stale branch in the safe order and report what happened."
- "Validate whether this directory is even a git repo before attempting branch cleanup."

## References

- Active contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Active evals: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical script wrapper: [./scripts/clean-gone](./scripts/clean-gone)
- Assets: `assets/` ([./assets](./assets))
