# Codex + Claude Worktree Alignment

## Table of Contents
- [Purpose](#purpose)
- [Canonical defaults](#canonical-defaults)
- [Codex app workflow facts](#codex-app-workflow-facts)
- [Claude CLI workflow facts](#claude-cli-workflow-facts)
- [Shared git constraints](#shared-git-constraints)
- [Decision matrix](#decision-matrix)

## Purpose
This reference keeps `using-git-worktrees` aligned across Codex app and Claude CLI behavior so routing and guidance stay consistent.

## Canonical defaults
- Prefer Codex-native terminology and controls for Codex threads.
- Prefer CLI-first commands for Claude sessions.
- Always state branch exclusivity and cleanup implications.

## Codex app workflow facts
- Codex worktrees are created under `$CODEX_HOME/worktrees`.
- Worktrees start from selected branch `HEAD` and default to detached `HEAD`.
- Verification path options:
  - **Create branch here** (keep working on the worktree)
  - **Sync with local** with **Apply** or **Overwrite**
- In non-git repos, automations run in the project directory (no git worktree).

## Claude CLI workflow facts
- `claude --worktree <name>` creates `.claude/worktrees/<name>`.
- Worktree branch default is `worktree-<name>`.
- If name omitted, Claude generates one automatically.
- Subagents can isolate with `isolation: worktree`.
- Recommend ignoring `.claude/worktrees/` in `.gitignore`.

## Shared git constraints
- A branch can be checked out in only one worktree at a time.
- Worktree removal can discard uncommitted work; require explicit confirmation.
- Initialize dependencies/tooling per worktree for reproducible verification.

## Decision matrix
| Need | Codex recommendation | Claude recommendation |
| --- | --- | --- |
| Start isolated task | Create thread in **Worktree** mode | `claude --worktree <name>` |
| Keep commit history local branch intact | **Sync with local → Apply** | Use `git worktree` + patch/cherry-pick workflow |
| Exact mirror of source workspace | **Sync with local → Overwrite** | Reset destination carefully after confirmation |
| Parallel agents | Multiple Codex worktree threads | Subagents with `isolation: worktree` |
| Non-git project | Run in project dir (automation default) | Configure `WorktreeCreate/WorktreeRemove` hooks |
