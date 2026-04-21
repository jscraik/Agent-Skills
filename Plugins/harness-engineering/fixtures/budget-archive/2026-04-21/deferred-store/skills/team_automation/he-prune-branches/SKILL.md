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
- Require one explicit yes/no confirmation for the full candidate branch set.
- Remove associated worktrees before deleting their branches.

## When to Use

- The user asks to prune local branches whose remote tracking refs are gone.
- The user asks to clean stale local branches before implementation or release work.
- Branch hygiene includes worktree cleanup in the same repository.

## Inputs

- Target repository path.
- Permission to run git discovery commands in that repository.
- Yes/no confirmation posture for destructive cleanup.

## Outputs

Return a structured summary when needed:
- `schema_version: 1`
- `repo_path`
- `discovery_status` (`found|none|blocked`)
- `candidate_branches`
- `confirmation` (`approved|declined|not_asked`)
- `cleanup_results`
- `summary`

## Procedure

1. Run stage-local discovery:

```bash
bash Plugins/harness-engineering/skills/team_automation/he-prune-branches/scripts/clean-gone
```

2. If output is `__NONE__`, report that no stale branches were found and stop.
3. Otherwise, show the full candidate set and ask one yes/no confirmation question.
4. On approval, remove any associated worktrees first, then delete each branch.
5. Report per-branch outcomes and final cleanup totals.

Use references only when additional edge handling is needed.

## Validation

- Verify discovery output is captured.
- Verify `__NONE__` path exits without deletion.
- Verify explicit yes/no confirmation before any destructive action.
- Verify worktree removal happens before branch deletion when applicable.
- Verify active branch is never queued for deletion.
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
- Stopping on the first branch failure without reporting partial results.

## References

- Active contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Active evals: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical script wrapper: [./scripts/clean-gone](./scripts/clean-gone)
- Assets: `assets/` ([./assets](./assets))
