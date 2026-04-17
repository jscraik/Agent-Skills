# Todo Resolution And Cleanup

Read when: the repo uses file-based `todos/` artifacts and the run needs detailed dependency grouping, bounded parallel execution, scratch-artifact handling, learning capture, or cleanup sequencing.

Imported from the upstream `resolve-todo-parallel` skill in `EveryInc/compound-engineering-plugin` commit `0fdc25a36cabea4ce9e2ae47ff69c1a9a2de8f0b`, adapted to local repo rules and Codex delegation constraints.

## Purpose

Resolve multiple todo artifacts in a coordinated sweep rather than handling each one as an unrelated ad hoc task.

## Todo discovery

Start by listing unresolved todo files from `todos/`.

Preserve the upstream protection rule:
- if a todo recommends deleting, removing, or gitignoring files in `docs/brainstorms/`, `Docs/plans/`, or `docs/solutions/`, skip that cleanup action and keep the item blocked or `wont_fix` unless the user explicitly overrides it

For each todo, extract:
- identifier
- status
- priority
- dependencies
- acceptance criteria
- work-log context

## Dependency planning

Build a task graph before implementation.

Group items by:
- independent and safe to run in parallel
- dependent and must run in order
- blocked and should not be started yet

When useful, show a Mermaid diagram of:
- what runs first
- what can run in parallel
- what remains blocked

## Execution modes

### Bounded parallel

Use bounded parallel execution only when:
- todo items are genuinely independent
- file overlap is low
- the runtime supports delegation
- the user has explicitly allowed delegation or parallel work

Preferred batching:
- 1-4 independent items: direct parallel handling is fine
- 5+ items: work in batches of at most 4

Each resolver should return only:
- todo handled
- files changed
- tests run or skipped
- blocker still open

### Serial fallback

Use serial execution when:
- items share files or system boundaries
- delegation is unavailable
- the user asked for no parallelism
- dependency ordering is not yet trustworthy

## Scratch-artifact pattern

If the todo set is large enough that parallel return summaries will get noisy, use a task-local scratch directory such as:

`.context/compound-engineering/resolve-todo-parallel/<run-id>/`

Each resolver writes a compact artifact there, and the parent flow reads back only what is needed for:
- final summary
- lesson capture
- blocked-item triage

Clean up the scratch directory after success unless the user wants to inspect it.

## Resolution and status updates

Once a todo is resolved:
- verify the implementation first
- then update the todo artifact state
- only then consider cleanup of completed files

Local adaptation:
- the upstream flow said to commit changes, remove the todo, mark it resolved, and push
- in this repo, keep commit and push behind explicit user approval and current git policy
- if approval is not present, stop at a verified working tree plus a clear summary of what remains

## Learning capture

After meaningful todo resolutions, route to `ce-compound`.

This preserves the upstream idea that repeated todo fixes often reveal:
- patterns
- recurring regressions
- architectural learnings
- missing documentation

If `ce-compound` produces a solution doc in `docs/solutions/`, include that path in the final summary.

## Cleanup

After resolution succeeds, identify todos with `done`, `resolved`, or equivalent completed status.

Cleanup options:
- delete completed todo files when the repo convention and user approval both allow it
- keep the files but mark them complete when retention is preferred

Never clean up:
- blocked todos
- partially resolved todos
- protected CE artifacts referenced by an overreaching todo cleanup instruction

## Final summary

A good closeout should include:
- todos resolved
- blocked or deferred todos
- lessons documented path or `skipped`
- todos cleaned up count
- any pending approval required for commit, push, or deletion

## Local adaptation notes

- This repo already has a file-based `todos/` convention, so the skill remains dedicated rather than being folded into generic execution.
- Git push is not an automatic outcome here.
- Cleanup is explicit and evidence-gated, not implicit.
- Parallel fan-out is preserved as a mode, not forced as the default.
