# Context Preservation

3. Build synchronized tasks from the governing artifact and keep task state aligned with markdown artifact state during execution.
4. Implement in small verified slices, honoring execution posture signals such as `test-first` or `characterization-first`.
5. Stop and update the governing artifact before continuing if execution uncovers contract drift, hidden scope, or changed boundaries.
6. Report completed work, blockers, validation evidence, and the shipping handoff package.
