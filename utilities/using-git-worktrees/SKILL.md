---
name: using-git-worktrees
description: "Create and validate Codex app and Claude CLI git worktree workflows with safe branch/sync strategy and cleanup guidance. Use when users request isolated checkouts; do not use for explicit in-place same-branch edits."
---

# Using Git Worktrees

## Table of Contents
- [Usage triggers](#usage-triggers)
- [Required context and assumptions](#required-context-and-assumptions)
- [Deliverables and results](#deliverables-and-results)
- [Workflow](#workflow)
- [Validation](#validation)
- [Constraints and safety](#constraints-and-safety)
- [Anti-patterns](#anti-patterns)
- [Philosophy](#philosophy)
- [Variation and adaptation](#variation-and-adaptation)
- [Empowering execution style](#empowering-execution-style)
- [Examples](#examples)
- [References](#references)

## Usage triggers
Use this skill when:
- The user asks to start isolated work in **Codex app** worktrees.
- The user asks for **Claude CLI** worktree setup (`claude --worktree`).
- The user needs branch/sync guidance between local checkout and worktree.

Do not use when:
- The user explicitly wants to keep all edits in the current checkout/branch.
- The task is only documentation summarization with no workspace isolation need.

## Required context and assumptions
- Environment: `codex`, `claude`, or `manual git` fallback.
- Repository root path and target starting branch/commit.
- Desired verification flow:
  - Stay on worktree, or
  - Sync to local checkout.
- Baseline verification command(s) for the repo.

## Deliverables and results
- Recommended isolation path (Codex app, Claude CLI, or manual git worktree).
- Worktree path + branch/detached-head status.
- Verification and sync instructions for the chosen flow.
- Cleanup and retention recommendation (keep vs remove).

## Workflow
1. **Classify platform + intent first**
   - Codex app thread/automation flow.
   - Claude CLI session/subagent flow.
   - Manual `git worktree` flow when user requests direct git control.

2. **Codex app flow (default for Codex requests)**
   - Start a thread using **Worktree** and choose the starting branch.
   - Assume detached `HEAD` by default until user chooses **Create branch here**.
   - If user wants local verification, guide **Sync with local**:
     - **Apply** to preserve destination history while applying source changes.
     - **Overwrite** to make destination exactly match source.
   - Warn that one branch cannot be checked out in two worktrees at once.

3. **Claude CLI flow (default for Claude requests)**
   - Use `claude --worktree <name>` (or omit `<name>` for auto-generated name).
   - Expect worktree at `.claude/worktrees/<name>` with branch `worktree-<name>`.
   - Remind user to initialize dependencies inside each new worktree.
   - Recommend `.claude/worktrees/` in `.gitignore`.
   - For subagents, use worktree isolation when requested (`isolation: worktree`).

4. **Manual git worktree fallback**
   - New branch: `git worktree add <path> -b <branch>`
   - Existing branch: `git worktree add <path> <branch>`
   - List/remove: `git worktree list`, `git worktree remove <path>`

5. **Handle non-git edge cases safely**
   - Codex: explain automations in non-git projects run directly in project directory.
   - Claude: explain non-git VCS requires `WorktreeCreate` / `WorktreeRemove` hooks.

6. **Run baseline checks and report state**
   - Run agreed verification command(s).
   - Report location, branch state, sync option, and cleanup recommendation.

## Validation
Fail fast: **stop at first failed gate**.

Required gates:
1. Platform and isolation path selected.
2. Git/non-git capability check completed.
3. Worktree created or explicit blocker documented.
4. Baseline verification completed or explicitly deferred by user.
5. Cleanup strategy documented (auto-cleanup vs keep).

## Constraints and safety
- Redact secrets/tokens/PII from logs and summaries.
- Never force-delete branches/worktrees without explicit confirmation.
- Call out branch exclusivity: same branch cannot be checked out in two worktrees.
- Keep actions single-threaded unless user explicitly asks for parallel execution.

## Anti-patterns
- Creating worktrees without clarifying Codex vs Claude flow.
- Telling users to check out the same branch in local + worktree simultaneously.
- Using **Overwrite** sync without warning it rewrites destination history/files.
- Skipping per-worktree environment setup then blaming tooling drift.
- **NEVER** claim worktree behavior applies to non-git repos without caveats.

## Philosophy
- Isolation first, then implementation.
- Platform-aware guidance prevents branch/sync confusion.
- Baseline verification is mandatory before feature iteration.
- Small setup rigor avoids expensive merge/recovery work later.

## Variation and adaptation
- Adapt recommendations to the active environment (Codex app UI vs Claude CLI).
- Prefer Codex-native operations for Codex threads; CLI commands for Claude.
- Tune cleanup strictness by branch importance and session longevity.
- Keep guidance minimal for routine tasks; add detail only when conflicts arise.

## Empowering execution style
- You can safely run parallel streams without branch collisions.
- You can switch between Codex and Claude worktree models without losing clarity.
- You can explain tradeoffs (Apply vs Overwrite, keep vs cleanup) with confidence.

## Examples
- "Start a Codex worktree from my feature branch and tell me whether I should use Apply or Overwrite when syncing."
- "Run Claude in a worktree called feature-auth and explain cleanup behavior when I exit."
- "Use manual git worktree commands to create a checkout for bugfix-123 and list cleanup steps."

## References
- `references/contract.yaml` (`schema_version: "1.0"`)
- `references/evals.yaml`
- `references/codex-claude-alignment.md`

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
