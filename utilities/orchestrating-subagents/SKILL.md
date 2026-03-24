---
name: orchestrating-subagents
description: Plan and run Codex subagent workflows using installed roles and Codex-native delegation tools. Use when the user explicitly wants subagents, parallel delegation, or swarm-style orchestration, not ordinary single-agent work or role creation.
metadata:
  skill-type: team_automation
---

# Orchestrating Subagents

Plan, translate, and run Codex-native subagent workflows without carrying over Claude-specific swarm mechanics that do not exist in Codex.

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
- [See Also](#see-also)
- [Execution quality](#execution-quality)
- [Gotchas](#gotchas)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)

## Usage triggers
Use this skill when:
- The user explicitly asks for subagents, delegation, parallel agent work, or a swarm-style workflow.
- The user wants an older Claude Code team/task workflow translated into Codex-native orchestration.
- The task benefits from multiple narrow sidecar agents, such as read-only review fan-out, codebase mapping, docs verification, or long-running monitoring.
- The user wants help choosing which installed Codex agent roles should participate in a delegated workflow.

Do not use this skill when:
- The user wants a normal single-agent implementation with no delegation.
- The user only wants to create, install, or update a role definition. Route that part to `codex-agent-builder`.
- The main need is isolated checkouts or parallel write safety via worktrees. Route to `using-git-worktrees`.
- The task is a generic Codex product question with no orchestration design need. Route to `codex-guide` or `openai-docs`.

## Required context and assumptions
- The user has explicitly permitted subagent or parallel-agent work.
- The current repo or project path is known.
- The desired outcome is clear enough to split into bounded subtasks.
- If code edits are in scope, the orchestrator can determine whether writes are read-only, disjoint-by-file, or unsafe-in-shared-checkout.
- Existing installed roles are preferred over inventing new ones. If a genuinely missing role blocks the design, co-trigger `codex-agent-builder`.

## Deliverables and results
- A Codex-native orchestration plan or execution flow.
- A recommended role roster using installed agents first.
- A write strategy decision:
  - shared read-only
  - shared disjoint writes
  - isolated worktrees
  - stay single-agent
- A concise explanation of any translation from legacy swarm concepts into Codex concepts.
- Escalation guidance when a new role or worktree isolation is required.

## Workflow
1. **Translate the runtime first**
   - Treat the root Codex thread as the orchestrator because Codex subagents do not use Claude-style teams, inbox files, or shared task JSON queues.
   - Coordinate through the parent agent using `spawn_agent`, `wait_agent`, `send_input`, and `close_agent` because Codex subagents report back through the parent workflow.
   - Read `references/upstream-orchestrating-swarms.md` when translating older `Task`, `Teammate`, `team_name`, or inbox concepts into Codex-native behavior.

2. **Decide whether subagents are actually warranted**
   - Use subagents only when the user explicitly asked for delegation or when the work can proceed in parallel without blocking the immediate next local step.
   - Keep simple or tightly coupled tasks local because unnecessary fan-out adds latency, token cost, and coordination risk.
   - Prefer read-heavy fan-out first because it reduces shared-write conflicts and context pollution.

3. **Choose the smallest useful roster**
   - Use `explorer` for read-only codebase mapping and file discovery.
   - Use `reviewer` for general correctness, regression, and missing-test review when no narrower reviewer is already the clear fit.
   - Use `framework-docs-researcher` for official docs and version-specific API verification.
   - Use specialist reviewers such as `security-sentinel`, `performance-oracle`, `architecture-strategist`, or language reviewers when the request is clearly specialized.
   - Use `worker` for bounded implementation tasks with explicit file ownership.
   - Use `monitor` for long-running polling, waits, and status checks that should stay off the main thread.
   - If a required role truly does not exist, stop broadening the skill and route the role-creation part to `codex-agent-builder`.

4. **Choose a write strategy before spawning**
   - Default to shared-checkout read-only work for review, exploration, docs lookup, and evidence gathering.
   - Allow shared-checkout writes only when ownership is explicitly split by file or directory and the subtasks are materially independent.
   - If multiple agents would touch the same files, the same schema/config surface, or a broad feature slice, route to `using-git-worktrees` or keep execution single-threaded.
   - Keep recursion off by default because the current Codex guidance favors shallow delegation and your config keeps `agents.max_depth = 1`.

5. **Spawn with precise briefs**
   - Tell every worker it operates in a shared environment and must not revert, overwrite, or interfere with other agents' work.
   - State whether subagents are forbidden for that worker because recursive delegation should remain opt-in.
   - Include the exact deliverable shape you want back: findings list, files changed, validation run, blocker report, or summary.
   - For write-capable workers, include the allowed write boundary and anything explicitly out of scope.

6. **Monitor and steer correctly**
   - Use `wait_agent` with long timeouts because monitoring is event-driven, not chatty.
   - While sidecar agents run, do useful non-overlapping work locally instead of busy-waiting.
   - Do not use `send_input` to ask for progress because queued follow-ups only affect the next phase of work.
   - Use `send_input(interrupt=true)` only when you must redirect or stop the current task.

7. **Integrate, verify, and close**
   - Review each finished agent's output before acting on it because the parent owns integration quality.
   - Reassign only the remaining gaps, not the entire task again.
   - Close completed agents once no more work is required from them.
   - Return to the user only after the delegated work has been integrated, verified, and summarized clearly.

8. **Use modern Codex defaults**
   - Prefer a `gpt-5.4` main planner or reviewer-of-reviews for the parent thread when the task is complex.
   - Prefer `gpt-5.4-mini` subagents for narrower supporting work because that matches current OpenAI guidance for responsive, cost-efficient Codex subagent workflows.
   - Read `references/codex-subagents-2026.md` when you need the current OpenAI-backed rationale and configuration guidance.

## Validation
Fail fast: stop at the first failed gate.

Required gates:
1. Explicit user permission for subagents or parallel agent work is present.
2. The selected subtasks are genuinely parallel or sidecar-safe.
3. The write strategy is classified before any write-capable worker is spawned.
4. The chosen roster uses installed roles first and only escalates to `codex-agent-builder` when a real gap exists.
5. Worker briefs include shared-environment, non-overwrite, and deliverable constraints.
6. Finished outputs are reviewed and integrated before completion is reported.

## Constraints and safety
- Start read-only unless the delegated work genuinely requires edits.
- Subagents inherit the parent sandbox and approvals posture; keep least privilege unless there is a clear reason to widen it.
- Never run same-file or same-surface write fan-out in one checkout.
- Never assume Claude-style shared task queues, inboxes, tmux panes, or teammate messaging exist in Codex.
- Prefer installed specialist roles over generic workers when the user has already named the specialty.
- Close completed agents so stale threads do not accumulate.

## Anti-patterns
- Copying old Claude Code `Teammate`, `TaskCreate`, `TaskUpdate`, or inbox instructions directly into Codex.
- Spawning agents for straightforward blocking work that should stay local.
- Using `send_input` as a status ping instead of a deliberate next-phase instruction.
- Letting multiple write-capable agents edit the same files in one checkout.
- Raising delegation depth or breadth casually just because many roles are available.
- Leaving the root agent with no synthesis or verification responsibility.

## Philosophy
- Keep the main thread focused on decisions, constraints, synthesis, and verification.
- Use subagents to absorb noisy sidecar work, not to dodge ownership.
- Prefer a small, opinionated roster to a novelty swarm.
- Preserve the useful doctrine from upstream skills, but translate it into the real Codex runtime rather than emulating another tool's internals.

## Variation and adaptation
- For PR review, prefer a read-only roster such as `explorer` + `reviewer` + one or two specialists.
- For docs-backed implementation, pair `explorer` or `worker` with `framework-docs-researcher`.
- For long-running checks, add `monitor` instead of tying up the main thread.
- For write-heavy multi-slice implementation, either partition file ownership tightly or route to `using-git-worktrees`.
- For legacy swarm prompts, translate the concepts first and only then execute.

## Empowering execution style
- You can keep the main thread clean while still covering a large search or review surface.
- You can delegate aggressively on read-only work without losing control of the outcome.
- You can keep parallel edits safe by choosing worktrees or narrower ownership when needed.

## Examples
- "Spawn one agent per review concern on this branch, wait for all of them, and summarize the findings."
- "Translate this old swarm workflow into Codex subagents and use the roles we already have installed."
- "Use explorer, reviewer, and framework-docs-researcher to audit this PR against main."
- "Fan out implementation across two independent directories, but only if the write boundaries are safe; otherwise tell me to use worktrees."
- "Design the smallest useful Codex subagent roster for a flaky UI bug and a long-running verification loop."

## References
- `references/codex-subagents-2026.md`
  Read when: you need current OpenAI docs, March 2026 model guidance, or the manager-versus-handoff decision.
- `references/upstream-orchestrating-swarms.md`
  Read when: the user provides an older Claude swarm prompt or wants to preserve upstream orchestration doctrine during migration.
- `references/overlap-matrix.md`
  Read when: you need to decide whether this skill, `codex-agent-builder`, `using-git-worktrees`, or another workflow owner should lead.
- `references/contract.yaml`
- `references/evals.yaml`

## See Also
| Skill | When to use |
|---|---|
| [[codex-agent-creator]] | Create or update the agent roles that the orchestration plan needs |
| [[using-git-worktrees]] | Split write-heavy parallel work into isolated worktrees instead of a shared checkout |
| [[ce-work]] | Execute a plan once the orchestration decision is made and the task is implementation-ready |
| [[resolve-pr-parallel]] | Apply bounded parallelism to PR review resolution rather than general subagent orchestration |

## Execution quality
- Philosophy: keep orchestration shallow, explicit, and evidence-backed.
- Approach: choose the smallest useful roster, keep write boundaries explicit, and make the parent agent own synthesis.
- Guiding question: Is this subtask genuinely parallel, or am I just moving the same work elsewhere?
- Guiding question: What is the safest write strategy for this task?
- Guiding question: Which installed role already matches the job before I invent a new one?

## Gotchas
- Codex subagents are parent-mediated. There is no direct equivalent of Claude inbox messaging between workers.
- `send_input` queues follow-up work; it is not a live status channel.
- Shared-checkout parallel writes are only safe when ownership is clearly split.

## When to use
- Use this skill when the user explicitly wants Codex subagents, parallel delegation, or an older swarm workflow converted into current Codex collaboration patterns.
- Do not use it for pure role creation, generic Codex how-to questions, or worktree-only setup.

## Required inputs
- The task or workflow to parallelize.
- Whether the work is read-only, disjoint-write, or likely to need isolated worktrees.
- Any preferred or required roles if the user already named them.
- Whether the request is translating an older workflow or executing a new one directly.

## Deliverables
- A Codex-native orchestration plan or execution path.
- A recommended roster and write strategy.
- Clear routing to `codex-agent-builder` or `using-git-worktrees` when those are the right companion owners.

## Failure mode
- If the user did not explicitly ask for subagents, keep the task local and say so.
- If the write surface is unsafe for same-checkout parallelism, stop and route to `using-git-worktrees` or a single-agent plan.
- If the workflow depends on a missing role, stop broadening the skill and route the role-creation step to `codex-agent-builder`.

**Topic map:** [[agent-ops]]
