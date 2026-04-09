---
name: resolve-todo-parallel
description: "WHAT: Resolve file-based `todos/` items with dependency-aware serial or bounded-parallel execution, verification, and cleanup controls. WHEN: Use when a todo-sweep is the primary task, not generic single-feature implementation."
metadata:
  skill-type: team_automation
---

# Resolve Todo Parallel

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Output contract](#output-contract)
- [Protected artifacts](#protected-artifacts)
- [Workflow](#workflow)
- [Validation](#validation)
- [Philosophy](#philosophy)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [References](#references)
- [Gotchas](#gotchas)

## Standards snapshot
- Treat file-based `todos/` artifacts as the source of truth for this workflow.
- Resolve dependency order before parallelizing work.
- Use bounded parallelism only for independent todo items.
- Preserve upstream todo-resolution nuance in references instead of flattening it away.
- Hand off non-trivial learnings to `ce-compound` so repeated fixes become durable docs.
- Keep commit, push, and destructive cleanup behind local repo rules and explicit user approval.

## When to use
- The repo uses a `todos/` directory and the user wants multiple pending todo items resolved.
- The user asks for a bounded parallel todo sweep rather than ad hoc implementation.
- Todo items need dependency-aware ordering, execution, verification, and cleanup.
- The user wants learnings from resolved todos captured after the implementation work lands.

## When not to use
- The user wants to execute one plan, one spec, or one small todo file; use `ce-work`.
- The repo needs local task tooling installed; use `ce-work`.
- The user wants review findings turned into todo files rather than resolved; use `ce-review`.
- The user wants broad parallel agent orchestration unrelated to file-based todo cleanup.

## Required inputs
- A repo with a `todos/` directory.
- Optional todo selector:
  - specific todo ID
  - filename pattern
  - \"all pending\"
- Any explicit execution constraint:
  - serial only
  - parallel allowed
  - no delegation
  - no cleanup
- Any approval boundary for:
  - deleting completed todo files
  - committing changes
  - pushing changes

## Deliverables
- A discovered set of unresolved todo items with dependency notes.
- An execution plan showing serial versus parallel groups.
- Implemented changes or explicit blockers per todo.
- Verification evidence per resolved todo.
- Optional compounded learnings routed to `ce-compound`.
- Cleanup results for resolved todo artifacts when approved.

## Failure mode
- If the repo has no `todos/` workflow, stop and route to `ce-work`.
- If todo dependencies overlap too heavily for safe parallelism, fall back to serial execution and say why.
- If commit, push, or deletion approval is missing, stop at a verified local result and leave the final mutation step pending.
- If the todo artifacts are stale, contradictory, or underspecified, summarize the blocker and ask for the smallest clarification needed.

## Output contract
Use this shape when the user asks for structured output:

```json
{
  "schema_version": 1,
  "todo_scope": "string",
  "todos_found": 0,
  "execution_mode": "serial|bounded-parallel",
  "resolved": ["string"],
  "blocked": ["string"],
  "lessons_documented": "string|null",
  "todos_cleaned_up": 0,
  "next_step": "string"
}
```

Contract rules:
- Always include `schema_version`.
- Use `lessons_documented: null` when no solution doc was created.
- Count cleanup only after the file deletion or archival step actually happened.

## Protected artifacts
- If a todo recommends deleting, removing, or gitignoring files in `docs/brainstorms/`, `docs/plans/`, or `docs/solutions/`, do not perform that cleanup automatically.
- Treat those compound-engineering artifacts as intentional and permanent unless the user explicitly overrides the protection.
- Use `references/todo-resolution-and-cleanup.md` for the preserved upstream protected-artifact and cleanup rules.

## Workflow
1. Discover the todo set from `todos/`, applying any user-supplied selector first.
2. Read each candidate todo before executing anything:
   - status
   - dependencies
   - acceptance criteria
   - work log
   - any protected-artifact cleanup suggestions
3. Group todos by dependency and execution risk.
4. Choose the execution lane:
   - `bounded-parallel` only when independent items qualify, runtime delegation support is available, and the user explicitly requested parallel delegation via the `orchestrating-subagents` gate
   - `serial` for all other cases, including overlap, missing runtime delegation support, or missing explicit parallel delegation request
5. Resolve each todo using the narrowest appropriate implementation workflow.
6. Verify each resolved todo before marking it done.
7. Present results before any commit, push, or destructive cleanup.
8. If the work produced non-trivial learnings, route to `ce-compound`.
9. If approved, clean up completed todo files or update their status so the backlog stays actionable.

## Validation
- fail fast: stop at the first failed gate, fix or report it, rerun that gate, then continue
- Verify the repo actually has a `todos/` directory before using this skill.
- Verify the chosen execution mode matches dependency reality and runtime permission.
- Verify every resolved todo has implementation evidence and explicit validation.
- Verify protected compound-engineering artifacts were not deleted by a cleanup pass.
- Verify cleanup only happens after resolution, not as a speculative tidy-up step.

## Philosophy
- Keep execution evidence-backed and dependency-aware before parallelism.
- Favor correctness and traceability over raw throughput in todo sweeps.
- Preserve project artifacts and user approval boundaries over automatic cleanup.

## Constraints
- Do not assume subagents or parallel delegation are allowed; respect the runtime and the user's request.
- Do not commit or push automatically just because the upstream workflow did.
- Do not delete todo files or mark them resolved without evidence.
- Do not collapse todo-specific execution into a vague generic work summary.
- Redact secrets, credentials, and sensitive data from todo artifacts, logs, and summaries.

## Anti-patterns
- Treating every todo sweep as safely parallel.
- Cleaning up completed todos before validation is complete.
- Importing the upstream commit-and-push posture without adapting it to local repo rules.
- Ignoring `ce-compound` when repeated fixes surface durable lessons.

## Examples
- \"Resolve all pending todo files in `todos/` and tell me which ones can run in parallel.\"
- \"Work through todo `014` and any independent siblings, but do not commit or delete anything yet.\"
- \"Run a bounded parallel todo sweep, then capture any non-trivial learnings before cleanup.\"
- \"Take the ready todos, respect dependencies, and leave blocked items clearly marked.\"

## References
- `references/contract.yaml`
- `references/evals.yaml`
- `references/todo-resolution-and-cleanup.md`

## Gotchas
- Symptom: A todo sweep deletes planning or solution docs during cleanup.
  Cause: Upstream cleanup logic was imported without local CE artifact protection.
  Do instead: Keep `docs/brainstorms/`, `docs/plans/`, and `docs/solutions/` protected by default.
  Check: Cleanup summary shows no protected-artifact deletions.
- Symptom: Parallel execution creates merge collisions or duplicate work.
  Cause: Dependency analysis was skipped or items were not actually independent.
  Do instead: Fall back to serial execution unless independence is clear.
  Check: Execution summary explains why the chosen parallel groups were safe.

## See Also

| Skill | When to use together |
|---|---|
| [[triage]] | Review pending todo findings before execution begins |
| [[ce-work]] | Execute a single scoped implementation path instead of a todo sweep |
| [[ce-compound]] | Capture durable learnings that emerge from repeated todo fixes |
| [[orchestrating-subagents]] | Coordinate explicit subagent fan-out when runtime and an explicit user delegation request allow it |

**Topic map:** [[agent-ops]]
