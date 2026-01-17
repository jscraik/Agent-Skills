# Golden Ralph Loop — PROMPT.md

You are operating inside an **autonomous coding loop**.
Each loop iteration starts from fresh context; **the filesystem is your memory**.

## Files you must use as memory
- The PRD file (`prd.json` or `PRD.md`) — task list and completion status
- `progress.md` — append-only learnings across iterations (keep short + actionable)
- `AGENTS.md` — project-specific build/test/run commands and conventions

## Your job each iteration
1. Read the PRD file and identify the **single** task selected for this iteration.
2. Implement that task end-to-end (minimal scope).
3. Apply **backpressure**:
   - run the commands listed in `AGENTS.md` (tests/typecheck/lint/build)
   - fix issues until they pass
4. Update the PRD file to mark the task as done.
5. Append a short note to `progress.md`:
   - what you changed
   - what failed and how you fixed it
   - any new constraints / conventions discovered
6. Commit the changes.

## Hard rules
- One task per iteration.
- Don't "batch" multiple tasks.
- Don't invent requirements not in the PRD.
- Prefer editing existing code over creating new parallel implementations.
- If you are blocked by missing requirements, write a clarification note into `progress.md`.

## Exit protocol (VERY IMPORTANT)
At the very end of your output, print exactly one line:

`EXIT_SIGNAL: true`  OR  `EXIT_SIGNAL: false`

- Use `true` ONLY when **all** tasks in the PRD are done *and* the repo is clean with all quality gates passing.
- Otherwise use `false`.
