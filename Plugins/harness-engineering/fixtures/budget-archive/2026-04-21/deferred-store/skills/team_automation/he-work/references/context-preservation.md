# Context Preservation

1. Build synchronized tasks from the governing artifact and keep task state aligned with markdown artifact state during execution.
2. Implement in small verified slices, honoring execution posture signals such as `test-first` or `characterization-first`.
3. Stop and update the governing artifact before continuing if execution uncovers contract drift, hidden scope, or changed boundaries.
4. Report completed work, blockers, validation evidence, and the shipping handoff package.
