# Plan: Codex + Claude Worktree Alignment

## Table of Contents
- [Goal](#goal)
- [Tasks](#tasks)
- [Validation](#validation)

## Goal
Align `using-git-worktrees` guidance with current Codex app and Claude CLI worktree workflows while preserving safe defaults.

## Tasks
- [x] Update `SKILL.md` trigger boundary and workflow steps for Codex + Claude.
- [x] Expand `references/contract.yaml` to include environment-aware inputs/outputs.
- [x] Add evaluation coverage for Codex sync, Claude CLI flag flow, and negative prompts.
- [x] Add a platform alignment reference with shared constraints and decision matrix.

## Validation
- `quick_validate.py` on skill folder.
- `skill_gate.py` on skill folder.
- `openclaw_skill_guard.py --mode both` on skill folder.
