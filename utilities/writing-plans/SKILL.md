---
name: writing-plans
description: "Create execution-ready implementation plans with task sequencing and checks. Use when requirements are known but implementation is multi-step."
---

# Writing Plans

Create execution-ready plans that another agent can run without guessing.

## Standards snapshot (March 2026)
- Planning is a delivery tool, not ceremony.
- Every task should have a concrete outcome, target files, and a verification step.
- Keep the plan small enough to execute in batches but explicit enough to survive handoff.
- Surface hidden assumptions before implementation starts.

## When to use
- Scope is clear enough to plan but too large for one-step implementation.
- Work needs deterministic sequencing, checkpoints, or handoff to another agent or later session.
- Requirements exist, but execution order and verification still need to be made explicit.

## When not to use
- The problem is still ambiguous and needs discovery or brainstorming first.
- The task is small enough to execute directly without a plan artifact.
- The user needs a product spec or research memo rather than an implementation sequence.

## Required inputs
- Requirements, spec, or explicit user goal.
- Repository context and likely impacted areas.
- Constraints such as timeline, rollout risk, approvals, or compatibility expectations.

## Deliverables
- An implementation plan with ordered tasks.
- Per-task target files or work areas.
- Per-task verification commands or checks.
- Clear handoff notes covering assumptions, checkpoints, and the next execution mode.
- When a structured status report is requested, include a `schema_version` field in the returned payload.

## Failure mode
- If critical scope decisions are still unresolved, stop and name them instead of pretending the sequence is settled.
- If a task cannot be tied to a file target or verification step, the plan is not ready.
- If the user only needs exploration, route to brainstorming or interview work instead of overcommitting to execution detail.

## Workflow
1. Frame the goal, boundary, and assumptions in a short opening summary.
2. Decompose the work into the smallest safe tasks, usually 2-15 minute execution steps.
3. Attach concrete file targets, systems, or work areas to each task.
4. Add the command or check that proves each task is done.
5. Insert checkpoints where feedback, rollout approval, or risk review should happen.
6. End with a clear handoff: execute now, execute later, or revisit scope first.

## Validation
- Every task maps to a clear outcome.
- Every task has at least one verification command or check.
- The plan has no hidden prerequisites.
- The execution or handoff path is explicit.
- Fail fast at the first missing task outcome, target, or verification step.

## Anti-patterns
- Vague tasks like "improve" or "clean up" with no acceptance criteria.
- Missing file paths or missing verification commands.
- Oversized tasks that bundle multiple behavior changes.
- Padding the plan with generic steps that add no signal.
- Hiding assumptions the executor needs to know.

## Constraints
- Redact secrets, tokens, and sensitive material in examples and artifacts.
- Keep scope canonical by default and add compatibility work only when requested.
- Do not execute destructive commands while planning.

## Philosophy
- Planning is risk reduction, not ceremony.
- High-signal steps beat long prose.
- A plan should be executable by someone with zero local context.
- Good plans expose uncertainty before implementation cost grows.

## Variation
- Use tighter, shorter tasks for risky migrations and looser batching for low-risk cleanup.
- Increase checkpoint density when rollout, compliance, or coordination risk is high.
- Adapt the evidence format to the executor: command-focused for engineers, milestone-focused for broader stakeholders.

## Examples
- Create a task-by-task plan to add optimistic UI updates to this feature.
- Break this migration spec into implementation steps with checks.
- Turn this approved PRD into an execution plan with file targets and validation commands.

## References
- `references/contract.yaml`
- `references/evals.yaml`
- `references/folded-legacy-modes-core60.md`
- `references/folded-legacy-modes-phase4.md`

## Folded legacy mode
This skill also owns legacy execution-planning behavior from retired folds.

- `execute` from `utilities/executing-plans`: use when a plan already exists and the immediate job is to validate and execute it in verified batches with checkpoints.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
