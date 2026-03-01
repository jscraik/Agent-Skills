---
name: writing-plans
description: "Create execution-ready implementation plans with task sequencing and checks. Use when requirements are known but implementation is multi-step."
knowledge_graph_profile: references/task-profile.json
---

# Writing Plans

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
- Scope is clear enough to plan but too large for one-step implementation.
- You need deterministic task sequencing and checkpoints.
- Another agent or session may execute from your plan.

Do not use when problem framing is still ambiguous (use a discovery/interview skill first).

## Required context and assumptions
- Requirements/spec or explicit user goal.
- Repository context and likely impacted areas.
- Constraints (timeline, risk tolerance, rollout expectations).

## Deliverables and results
- Implementation plan with ordered tasks.
- Per-task file targets and expected checks.
- Explicit handoff notes for execution.

## Workflow
1. **Frame objective and assumptions**
   - One-paragraph goal and boundaries.
2. **Decompose into smallest safe tasks**
   - Prefer 2-15 minute steps.
3. **Attach concrete file targets**
   - Create/modify/test paths for each task.
4. **Embed verification per task**
   - What command proves task completion.
5. **Define checkpoints**
   - Where to pause for feedback before continuing.
6. **Prepare execution handoff**
   - Clarify next mode: execute now or execute later.

## Validation
Fail fast: **stop at the first failed gate** and revise the plan.

Required gates:
1. Every task maps to a clear outcome.
2. Every task has at least one verification command.
3. Plan has no hidden prerequisites.
4. Handoff path is explicit (executor can run without guessing).

## Anti-patterns
- Vague tasks like "improve" or "clean up" without acceptance criteria.
- Missing file paths or missing verification commands.
- Oversized tasks that bundle multiple behavioral changes.
- Planning compatibility work that was not requested.
- **NEVER** leave a task without a verification command.
- **DO NOT** hide assumptions that executors need to know.
- **DON'T** pad plans with generic steps that add no signal.

## Constraints and safety
- Redact secrets/tokens/PII in examples and artifacts.
- Keep scope canonical by default; add compatibility only when requested.
- Do not execute destructive commands while planning.

## Philosophy
- Planning is risk reduction, not ceremony.
- High-signal steps outperform long prose.
- Plans should be executable by someone with zero local context.
- Why this method? It exposes uncertainty before implementation cost grows.
- What tradeoff matters most: planning depth or delivery speed?
- Which dependency assumption could break execution first?

## Variation and adaptation
- Vary task granularity by risk: different step sizes for migrations, bugfixes, and UI tweaks.
- Adapt plan shape to context-specific constraints such as compliance, rollout windows, or team size.
- Customize checkpoint cadence to user preference rather than using one repetitive cadence.
- Use different evidence formats for technical implementers versus product stakeholders.
- Avoid generic cookie-cutter plans when repo conventions require unique sequencing.

## Empowering execution style
- You are capable of turning ambiguity into clear, actionable sequences.
- This process unlocks faster execution because decisions are front-loaded.
- Explore alternative breakdowns when a different structure reduces risk.
- Enable confident handoff by making every task explicit and verifiable.

## Examples
- "Create a task-by-task plan to add optimistic UI updates to this feature."
- "Break this migration spec into implementation steps with checks."

## References
- `references/contract.yaml`
- `references/evals.yaml`

<!-- decision-feedback-protocol:v1 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- If available, persist with `ops/scripts/graph/record-feedback.sh`; otherwise append a JSONL record to `ops/metrics/skill-feedback/decision-feedback.jsonl` in the active workspace.
<!-- /decision-feedback-protocol -->
