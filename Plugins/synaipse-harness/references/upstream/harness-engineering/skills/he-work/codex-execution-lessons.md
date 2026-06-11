# Harness Engineering Work Codex Execution Lessons

- Plan Mode is not execution mode. In Plan Mode, inspect repo truth but do not edit files, run mutating formatters, apply migrations, or commit.
- `update_plan` is not Plan Mode. It is live execution checklist state, not the durable contract.
- Explore first, ask second. Inspect files, tests, AGENTS, manifests, branch state, and artifact links before asking discoverable questions.
- Ask only for product intent, unresolved tradeoffs, or multiple plausible repo truths that cannot be safely chosen.
- Use short ordered `update_plan` steps, exactly one `in_progress`, and complete or defer all steps before handoff.
- Preserve unit IDs in live tasks, blocker notes, validation evidence, and handoff.
- Find adjacent tests before behavior changes, then supplement missing happy path, edge, failure, and integration scenarios.
- Use parallelism only with clear file ownership or worktree isolation.
- Delegate mode is opt-in and bounded; parent keeps research, contract updates, git, validation, review, and handoff.
- Meaningful UI work needs design/prototype decision and screenshot evidence before shipping.
