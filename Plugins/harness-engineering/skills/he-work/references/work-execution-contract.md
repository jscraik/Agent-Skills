# Harness Engineering Work Execution Contract

- Lanes: `plan-led`, `todo-led`, or `small-spec-direct`. Route medium/high-risk raw specs, migrations, cross-service work, and vague bare requests to `he-plan`.
- Intake: read linked artifacts fully and extract active IDs, Linear issue, branch, PR target, invariants, non-goals, validation gates, deferred questions, execution notes, patterns, file paths, and any active thread goal.
- Execution slice: for coding-harness-managed work, load `Plugins/harness-engineering/references/execution-slice-contract.md` and verify the todo/plan maps to one selected milestone, parent issue, refactor phase, or execution slice before editing.
- Goal alignment: use `/goal` only as continuity state. If the active goal conflicts with the current tracker/artifact/branch/PR chain, stop before editing and resolve the mismatch.
- Current truth: do not assume the newest dated artifact is active. Resolve via status/frontmatter, Linear links, branch/PR metadata, and repo convention.
- Durable truth: `update_plan` is live run state only. The plan/spec/todo changes only for real contract drift or required final status.
- Slice loop: mark live task in progress, read code/tests, check already-landed work, honor posture, implement the smallest slice, validate, then mark complete.
- Behavior checks: trace callbacks, middleware, events, retries, persistence, alternative interfaces, and failure cleanup before calling a behavior-bearing unit done.
- Delegation overlap safety: before parallel or external delegation, list each intended worker's files/modules. If two workers may touch the same file, generated projection, migration, lockfile, `.harness` artifact, or shared validation script, either isolate them in separate worktrees with explicit merge ownership or run them serially/inline. Do not delegate overlapping edits on the same checkout and hope the coordinator can reconcile them later.
- Delegation handoff: each delegated unit must return changed files, validation evidence, blockers, and any file-overlap discovered during execution. The coordinator owns final integration and reruns the shared gates.
- Drift stop: changed boundaries, lifecycle states, rollout complexity, hidden scope, UI/prototype mismatch, or mismatched Linear/branch/PR metadata requires artifact update first.
- Secondary context stop: `.harness/strategy/*.md`, `.harness/triage/*.md`, `.harness/review/*.md`, and `.harness/features/*.md` cannot add implementation work unless the selected execution slice admits them.
- Review: default meaningful code changes to Tier 2 `he-code-review mode:autofix` with `plan:` when available.
- Handoff: changed areas, completed IDs, validation outcomes, Linear result, spec/plan paths, branch/PR, active goal status when relevant, drift updates, risks, rollback or monitoring notes, and UI screenshots when relevant.
