# Orchestrating Subagents Overlap Matrix

Use this matrix to keep `orchestrating-subagents` focused on Codex-native delegation design and execution, not every related setup task around it.

## Table of Contents
- [Boundary rule](#boundary-rule)
- [Matrix](#matrix)
- [Notes](#notes)

## Boundary rule
- Trigger `orchestrating-subagents` when the user explicitly wants Codex subagents, parallel delegation, or a legacy swarm workflow translated into Codex-native collaboration.
- If the real blocker is a missing role, unsafe shared writes, or a generic Codex product question, route to the narrower owner and keep this skill as the orchestration companion only if needed.

## Matrix

| Request shape | Primary outcome | Owner |
|---|---|---|
| "Use Codex subagents to review this branch in parallel." | Delegation plan and execution with current role roster | `orchestrating-subagents` |
| "Convert this old orchestrating-swarms prompt into Codex subagents." | Legacy workflow translation into Codex-native orchestration | `orchestrating-subagents` |
| "Create a new reviewer role for my Codex config." | Role creation or update | `codex-agent-builder` |
| "Set up worktrees so multiple agents can edit safely." | Checkout isolation strategy and worktree operations | `using-git-worktrees` |
| "I just need to know how Codex subagents work." | Product guidance and docs-backed explanation | `openai-docs` |
| "Resolve all review comments on this PR in parallel." | PR-thread remediation workflow | `resolve-pr-parallel` |
| "Implement the approved plan end to end." | Execution of the underlying feature or fix | `ce-work` |
| "Design or harden a recurring Codex automation." | Automation architecture, not one-off orchestration | `codex-automation-architect` |

## Notes
- `orchestrating-subagents` may co-trigger with `codex-agent-builder` when a real role gap is discovered during roster design.
- `orchestrating-subagents` may route to `using-git-worktrees` when same-checkout parallel writes are unsafe.
- This skill translates older Codex concepts into Codex behavior, but it should not recreate Codex teammate infrastructure in documents or prompts.
