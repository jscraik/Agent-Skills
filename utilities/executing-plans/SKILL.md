---
name: executing-plans
description: "Validate and execute written implementation plans in verified batches with checkpoints. Use when a plan already exists and work must proceed task-by-task."
---

# Executing Plans

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
- A written plan already exists.
- Work should proceed task-by-task with explicit checkpoints.
- You need predictable progress and blocker visibility.

Do not use when the plan is missing or fundamentally unclear (route to `writing-plans`).

## Required context and assumptions
- Plan file path.
- Execution scope (full plan or selected tasks).
- Project verification commands.
- Checkpoint cadence requested by user (or default).

## Deliverables and results
- Executed tasks with status updates.
- Verification evidence for each completed task/batch.
- Clear blocker reports when execution cannot continue.

## Workflow
1. **Load and assess the plan**
   - Confirm task ordering, dependencies, and missing context.
2. **Set batch boundary**
   - Default to small batches (for example, 2-3 tasks).
3. **Execute sequentially**
   - One task at a time in this session unless user asks for parallelism.
4. **Run required verification after each task**
   - Capture outputs needed for status claims.
5. **Checkpoint report**
   - Summarize completed tasks, evidence, and open risks.
6. **Continue or pause**
   - Proceed to next batch only when current batch is verified.

## Validation
Fail fast: **stop at the first failed gate** and do not continue execution.

Required gates:
1. Plan is readable and actionable.
2. Current task verifies successfully before next task.
3. Batch summary includes evidence and next action.
4. If blocked, execution halts with remediation request.

## Anti-patterns
- Skipping plan review and jumping directly to edits.
- Executing multiple plan tasks without intermediate verification.
- Continuing after repeated verification failure.
- Silent scope expansion beyond the plan.
- **NEVER** continue after a failed verification gate.
- **DO NOT** mark tasks complete without evidence.
- **DON'T** bypass blocker reporting to keep momentum.

## Constraints and safety
- Redact secrets/tokens/PII from logs and summaries.
- No destructive operations without explicit user confirmation.
- Respect single-threaded execution default unless user explicitly requests parallel execution.

## Philosophy
- Execution quality is measured by verified increments.
- Small verified batches beat large unverified bursts.
- Blockers should be surfaced early, not worked around silently.
- Why this approach? It reduces rollback risk by validating continuously.
- What tradeoff matters here: throughput or certainty?
- Which dependency is most likely to block the next batch?

## Variation and adaptation
- Vary batch size by risk and complexity: different cadence for migrations vs small fixes.
- Adapt checkpoint detail to context-specific audience needs (developer, reviewer, stakeholder).
- Customize verification depth when touching critical paths or security-sensitive code.
- Use different blocker escalation paths depending on urgency and ownership.
- Avoid repetitive generic status updates when targeted evidence is more useful.

## Empowering execution style
- You are capable of delivering steady progress under uncertainty.
- This framework unlocks reliable momentum without sacrificing quality.
- Explore creative sequencing when dependencies permit, while keeping gates strict.
- Enable clear collaboration by reporting progress, risks, and decisions explicitly.

## Examples
- "Execute this migration plan and report every 3 tasks."
- "Run tasks 1-4 from this plan with evidence after each task."

## References
- `references/contract.yaml`
- `references/evals.yaml`

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
