# CE Work Execution Modes

## Table of Contents
- [Purpose](#purpose)
- [Primary lanes](#primary-lanes)
- [Task strategies](#task-strategies)
- [External delegate mode](#external-delegate-mode)
- [Branch and worktree rules](#branch-and-worktree-rules)

## Purpose
This note captures how `ce-work` chooses an execution lane and task strategy without bloating the main skill body.

## Primary lanes
- `plan-led`
  - default for `docs/plans/*.md` and `docs/ui-plans/*.md`
  - safest path for multi-phase, high-risk, or cross-cutting work
- `todo-led`
  - allowed when the todo artifact already encodes the dependency structure and verification expectations
- `small-spec-direct`
  - only for genuinely small, low-risk, explicitly approved direct spec execution
  - if a raw spec is medium/high risk, route to `ce-plan` first

## Task strategies
- `inline`
  - 1-2 small tasks or work that needs frequent user decisions
- `serial-units`
  - default for several dependent implementation units
- `parallel-independent-units`
  - only for independent slices with non-overlapping files and clear acceptance boundaries
- `swarm-mode`
  - only when the user explicitly asks for agent-team orchestration and the platform supports it

If task-spawning is unavailable or disallowed, collapse back to serial execution in the main thread.

## External delegate mode
Use only when one of these is true:
- the user explicitly asks for delegation, Codex CLI delegation, or token-conserving implementation
- an implementation unit carries `Execution target: external-delegate`

Rules:
- treat delegation as a task-level modifier, not a separate planning stage
- use it only for well-scoped implementation slices with clear acceptance criteria
- keep research, contract updates, git operations, and final handoff in the parent agent
- fall back cleanly to standard execution if delegation is unavailable, unsafe, empty, or out of scope

Environment guard:
- if already inside a delegate sandbox, do not recurse; continue in standard mode

Failure handling:
- on repeated delegate failures, disable delegate mode for the remaining tasks and finish in standard mode

## Branch and worktree rules
- if already on a feature branch, confirm whether to continue or create a fresh branch/worktree
- if on the default branch, prefer a new branch or worktree
- never commit directly to the default branch without explicit user confirmation
- prefer worktrees for:
  - parallel efforts
  - risky experiments
  - long-running feature work
  - multiple active agent threads touching nearby code
