# Pragmatic Operating Invariants

Harness Engineering work should improve the next run, not only the current
artifact. Use these invariants when repeated review comments, route confusion,
stale evidence, or skill bloat appear across HE stages.

## Invariants

- Prefer the smallest durable repair surface that prevents recurrence.
- Preserve source-of-truth ownership; do not patch generated projections as the
  canonical fix.
- Convert repeated feedback into one of: skill instruction, eval fixture,
  validation contract, reference note, or explicit rejection.
- Keep evidence current. Stale session, PR, CI, or goal evidence must be
  refreshed or labeled as stale before it drives decisions.
- Avoid broad skill expansion when one precise contract or command wrapper would
  remove the failure mode.

## Design Complexity Red Flags

- A skill needs another skill to explain its basic output.
- The same blocker appears in two consecutive PRs without a captured learning.
- A generated artifact is treated as proof even though its status is failing,
  stale, or diagnostic-only.
- Multiple names describe the same workflow state without an explicit mapping.
- Operators are routed to raw scripts when a repo wrapper exists.

## Blackboard Delta

When a stage learns something durable, emit a compact `blackboard_delta`:

```yaml
blackboard_delta:
  status: added|updated|not_applicable
  learning: "<one sentence>"
  target_surface: skill|reference|eval|validator|plan|memory|not_applicable
  owner: "<skill or workflow owner>"
  follow_up: "<smallest next action or null>"
```

Use `not_applicable` when the run only applies an existing contract and creates
no new reusable learning.
