# Post-Plan Handoff

Read when: `he-plan` finishes a durable plan and the user has not explicitly
asked for plan-only output.

Planning is not completion. End every plan run with exactly one handoff state:

```yaml
post_plan_handoff:
  state: handoff_executed|explicit_stop|blocked|awaiting_user_choice
  selected_next_stage: he-work|he-eval-report|he-code-review|linear-update|none
  evidence: "<plan path, blocker, user stop, or route decision>"
  next_action: "<action already taken or smallest required recovery>"
```

## State Rules

- `handoff_executed`: the user asked to continue into an eligible next stage
  and the agent routed there in the same turn.
- `explicit_stop`: the user asked for a plan/review only, or the plan is the
  final requested artifact.
- `blocked`: missing source evidence, Linear linkage, validation gate, or
  safety condition prevents a safe next stage.
- `awaiting_user_choice`: multiple valid next stages exist and repo inspection
  cannot safely choose between them.

If the next stage is obvious and authorized, route there instead of only
recommending it. If the next stage would mutate code, tracker state, PR state,
or external systems and authorization is unclear, stop with `blocked` or
`awaiting_user_choice`.
