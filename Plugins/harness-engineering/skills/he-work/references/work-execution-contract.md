# Harness Engineering Work Execution Contract

- Lanes: `plan-led`, `todo-led`, or `small-spec-direct`. Route medium/high-risk raw specs, migrations, cross-service work, and vague bare requests to `he-plan`.
- Intake: read linked artifacts fully and extract active IDs, Linear issue, branch, PR target, invariants, non-goals, validation gates, deferred questions, execution notes, patterns, file paths, and any active thread goal.
- Goal alignment: use `/goal` only as continuity state. If the active goal conflicts with the current tracker/artifact/branch/PR chain, stop before editing and resolve the mismatch.
- Current truth: do not assume the newest dated artifact is active. Resolve via status/frontmatter, Linear links, branch/PR metadata, and repo convention.
- Durable truth: `update_plan` is live run state only. The plan/spec/todo changes only for real contract drift or required final status.
- Slice loop: mark live task in progress, read code/tests, check already-landed work, honor posture, implement the smallest slice, validate, then mark complete.
- Behavior checks: trace callbacks, middleware, events, retries, persistence, alternative interfaces, and failure cleanup before calling a behavior-bearing unit done.
- Drift stop: changed boundaries, lifecycle states, rollout complexity, hidden scope, UI/prototype mismatch, or mismatched Linear/branch/PR metadata requires artifact update first.
- Review: default meaningful code changes to Tier 2 `he-code-review mode:autofix` with `plan:` when available.
- Handoff: changed areas, completed IDs, validation outcomes, Linear result, spec/plan paths, branch/PR, active goal status when relevant, drift updates, risks, rollback or monitoring notes, and UI screenshots when relevant.
