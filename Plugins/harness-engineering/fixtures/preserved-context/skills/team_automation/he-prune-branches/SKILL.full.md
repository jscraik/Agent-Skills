---
name: he-prune-branches
description: Clean up stale local branches whose remote tracking branch is gone, including associated worktree cleanup and explicit user confirmation. Use when the user asks to prune gone branches or delete local branches removed from remote.
metadata:
  skill-type: team_automation
---

# Harness Engineering Prune Branches

**Note: The current year is 2026.** Use this when validating recency-sensitive branch and worktree state before destructive cleanup.

`he-plan` and `he-work` cover implementation delivery. `he-prune-branches` is the Harness Engineering maintenance stage for removing stale local branches after upstream deletion.

## Table of Contents
- [Working agreement](#working-agreement)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Interaction Method](#interaction-method)
- [Workflow](#workflow)
- [Subagent policy](#subagent-policy)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Output contract](#output-contract)
- [References](#references)

## Working agreement
- Discover first, delete second.
- Always show the full candidate branch list and wait for explicit yes/no confirmation.
- Treat associated worktrees as first-class cleanup targets before branch deletion.
- Keep deletion reporting explicit and per-branch.
- Never delete the currently checked-out branch.

## When to use
Use this stage when:
- the user asks to clean stale local branches,
- the repo has local branches whose remote tracking branch was removed,
- branch hygiene is needed before further implementation or release work,
- worktrees tied to stale branches may also need cleanup.

Typical triggers:
- "clean gone branches"
- "prune local branches"
- "delete branches that no longer exist on origin"
- "clean up stale branches and worktrees"

## When not to use
Route elsewhere when:
- the user needs lifecycle routing (`he-compound` or `he-router`),
- the user needs implementation work (`he-work`),
- the user needs debugging/root-cause analysis (`he-fix-bugs`),
- the user requests multi-repo branch governance policy authoring instead of one-repo cleanup.

## Required inputs
- target repository path,
- confirmation posture (interactive yes/no),
- permission to remove associated worktrees for stale branches.

If critical context is missing, ask one blocking question before any deletion.

## Deliverables
- discovered gone-branch list (or explicit none-found result),
- explicit user confirmation checkpoint outcome,
- per-branch cleanup report (worktree removed, branch deleted, or skipped/error),
- final summary count of cleaned branches,
- `schema_version: 1` when structured output is requested.

## Failure mode
- If not in a git repository, return blocked with the exact path issue.
- If discovery fails, return blocked with command/error output.
- If user declines deletion, stop cleanly and report no changes.
- If some branches fail deletion, continue remaining branches and report partial completion with reasons.

## Interaction Method

Use the platform's blocking question tool when available (`AskUserQuestion` in Codex, `request_user_input` in Codex, `ask_user` in OpenAI). Otherwise, present numbered options in chat and wait for the user's reply before proceeding.

Ask one question at a time. For this stage, ask one yes/no question for the complete discovered branch set.

## Workflow

### Phase 0: Preconditions
1. Confirm current path is a git repository.
2. Ensure branch discovery can run safely from the current repository root.

### Phase 1: Discover gone branches
1. Run:

```bash
bash Plugins/harness-engineering/skills/team_automation/he-prune-branches/scripts/clean-gone
```

2. If output is `__NONE__`, report that no stale local branches were found and stop.
3. Otherwise, capture each discovered branch name.

### Phase 2: Confirm deletion set
1. Present the discovered list as one set.
2. Ask one yes/no confirmation question for deleting all listed branches.
3. If no, stop without deleting anything.

### Phase 3: Delete confirmed branches
For each confirmed branch:
1. Check for associated worktree entry in `git worktree list`.
2. If an associated non-root worktree exists, remove it first:

```bash
git worktree remove --force "<worktree_path>"
```

3. Delete the local branch:

```bash
git branch -D "<branch>"
```

4. Report each outcome immediately.

### Phase 4: Final summary
1. Report total cleaned branch count.
2. Report partial failures (if any) with exact branch-level reasons.
3. Recommend next stage only when requested (for example route back to `he-work`).

## Subagent policy
- Stage policy source: `../../../../../references/routing-map.json` under `he-prune-branches`.
- Resolve role availability from `~/.codex/agents/manifest.json`.
- This stage is `manual-only`; run inline by default.
- If the manifest is unavailable, continue inline and emit manual mapped-role guidance without blocking.
- If delegation is requested, provide manual launch guidance only.
- If required roles are missing, route creation/install to `[[codex-agent-creator]]`.

## Validation
- Verify discovery command output is captured.
- Verify `__NONE__` path exits without deletions.
- Verify explicit yes/no confirmation before destructive actions.
- Verify active branch is never queued for deletion.
- Verify worktree removal precedes branch deletion when applicable.
- Verify final report matches actual deletion outcomes.

## Anti-patterns
- deleting branches without showing the candidate set first,
- deleting per-branch without a whole-set confirmation checkpoint,
- ignoring associated worktrees and leaving stale filesystem artifacts,
- stopping entire cleanup on one branch failure without continuing/reporting,
- silently dropping failures from the final summary.

## Output contract
Use this schema when structured output is requested:

```json
{
  "schema_version": 1,
  "repo_path": "string",
  "discovery_status": "found|none|blocked",
  "candidate_branches": ["string"],
  "confirmation": "approved|declined|not_asked",
  "cleanup_results": [
    {
      "branch": "string",
      "worktree_removed": true,
      "branch_deleted": true,
      "error": "string|null"
    }
  ],
  "summary": "string"
}
```

## References
- [Contract](./references/contract.yaml)
- [Evals](./references/evals.yaml)
- [Source Parity](./references/source-parity.md)
- [Task Profile](./references/task-profile.json)
- [Script: clean-gone](./scripts/clean-gone)

## See Also
| Skill | When to use |
|---|---|
| [[he-router]] | Choose the right Harness Engineering stage when intent is ambiguous |
| [[he-work]] | Continue implementation delivery after hygiene cleanup is complete |
| [[he-fix-bugs]] | Diagnose regressions when branch cleanup uncovers breakage |

**Topic map:** [[agent-ops]]

## Deferred Context Preservation

Do not remove important context for budget trimming. See [deferred-context-index.md](../../../../references/deferred-context-index.md) for preserved Harness Engineering context.
