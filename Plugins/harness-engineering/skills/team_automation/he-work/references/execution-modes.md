# Harness Engineering Work Execution Modes

- Lanes: `plan-led` for approved plans/UI plans, `todo-led` for ordered task artifacts, `small-spec-direct` for tiny low-risk approved direct work.
- Strategies: `inline`, `serial-units`, `parallel-independent-units`, or explicit `swarm-mode`.
- If spawning is unavailable or unsafe, execute serially in the parent while preserving task and contract mapping.
- External delegate mode requires explicit user intent or `Execution target: external-delegate`.
- Delegate only scoped implementation slices. Parent keeps research, contract updates, git operations, broad validation, review, and handoff.
- Do not recurse inside delegate sandboxes. Fall back to standard execution if delegation is unavailable, unsafe, empty, or out of scope.
- Delegate prompt includes artifact path, unit goal, files, execution note, patterns, tests, verification, and resolved questions.
- Parallel safety requires a file-to-unit map. Overlap without worktree isolation means serial execution.
- Shared-directory delegates must not stage, commit, or run broad suites; parent reviews diffs, checks collisions, stages unit files, and validates sequentially.
