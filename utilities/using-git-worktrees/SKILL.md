---
name: using-git-worktrees
description: "Create isolated git worktrees with baseline checks and cleanup safety. Use when starting feature work or plan execution in a dedicated worktree."
---

# Using Git Worktrees

## Table of Contents
- [Usage triggers](#usage-triggers)
- [Required context and assumptions](#required-context-and-assumptions)
- [Deliverables and results](#deliverables-and-results)
- [Workflow](#workflow)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Constraints and safety](#constraints-and-safety)
- [Philosophy](#philosophy)
- [Variation and adaptation](#variation-and-adaptation)
- [Empowering execution style](#empowering-execution-style)
- [Examples](#examples)
- [References](#references)

## Usage triggers
Use this skill when:
- Starting a feature that should not contaminate current workspace.
- Executing a multi-step plan in an isolated branch path.
- You need parallel branch isolation without context switching main checkout.

Do not use when work must remain in the current branch by explicit request.

## Required context and assumptions
- Target branch name.
- Repository root path.
- Preferred worktree location (project-local or global).
- Baseline verification command(s).

## Deliverables and results
- Created worktree path and branch.
- Baseline setup + verification status.
- Cleanup recommendation for end-of-work lifecycle.

## Workflow
1. **Choose location deterministically**
   - Prefer existing `.worktrees/` then `worktrees/`.
   - If neither exists, ask once or use repo convention.
2. **Verify ignore safety** for project-local directories.
3. **Create worktree and branch**
   - `git worktree add <path> -b <branch>`
4. **Run project bootstrap**
   - Install deps only if needed for verification.
5. **Run baseline checks**
   - Confirm clean starting state before feature work.
6. **Report context**
   - Provide worktree path, branch, and current status.

## Validation
Fail fast: **stop at the first failed gate** and do not continue setup.

Required gates:
1. Worktree directory policy resolved.
2. Ignore safety confirmed for project-local worktrees.
3. Worktree creation command succeeded.
4. Baseline verification command completed (or blocker documented).

## Anti-patterns
- Creating project-local worktrees without ignore checks.
- Starting implementation with failing baseline tests and no explicit approval.
- Mixing unrelated tasks in the same worktree.
- Deleting worktree/branch without confirmation.
- **NEVER** skip ignore safety checks for project-local worktrees.
- **DO NOT** begin coding before baseline verification status is known.
- **DON'T** force-delete branches unless the user explicitly confirms.

## Constraints and safety
- Redact secrets/tokens/PII from logs.
- Do not force-delete branches or worktrees without explicit user confirmation.
- Keep actions single-threaded by default unless user requests parallel execution.

## Philosophy
- Isolation first, then implementation.
- Baseline clarity prevents misleading debug loops.
- Small setup rigor reduces large integration risk.
- Why this approach? It prevents hidden branch-state contamination.
- What tradeoff matters: faster setup now or safer recovery later?
- Which assumption about repo policy should be confirmed first?

## Variation and adaptation
- Vary directory strategy by environment: different defaults for local project paths vs global worktree folders.
- Adapt bootstrap depth to context-specific repo size and dependency weight.
- Customize baseline checks by stack; do not repeat a generic one-command strategy everywhere.
- Use different cleanup strictness for experimental branches versus release-critical work.
- Avoid cookie-cutter setup when repository conventions require a unique path policy.

## Empowering execution style
- You are capable of creating clean, reversible workspaces that unlock safer iteration.
- This skill enables fast context switches without sacrificing repository integrity.
- Explore workflow improvements while preserving baseline verification discipline.
- Enable teammates by reporting branch/worktree state clearly and reproducibly.

## Examples
- "Create a worktree for feature/auth-refresh and verify baseline tests."
- "Set up isolated branch workspace before executing this plan."

## References
- `references/contract.yaml`
- `references/evals.yaml`
