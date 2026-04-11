# CE Deepen Plan Compaction Context

Read when: you need the expanded standards snapshot, philosophy prompts, and additional example scenarios that were moved out of `SKILL.md` for line-budget governance.

## Standards snapshot (expanded)
- Keep each skill scoped to one reusable job and make the description say what it does and when to use it.
- Prefer explicit routing, realistic examples, negative examples, and validation over prompt-only procedures.
- For multi-step agentic work, plan the workflow, keep one current step in focus, and use bounded research instead of unconstrained fan-out by default.
- Use repo guidance, origin context, and prior learnings before external research, and add external research only when it materially changes planning confidence.
- When a legacy prompt relied on broad parallelism, preserve that behavior as an explicit mode rather than forcing it as the default.

## Philosophy prompts (expanded)
- Does this plan need another pass at all?
- Which sections are weakest relative to the risk of the work?
- What evidence would actually change planning quality?
- Should this run as targeted-confidence or max-coverage?
- Can the plan be strengthened without changing product intent?

## Additional examples
- "Stress-test this migration plan before implementation and focus only on the genuinely weak sections."
- "Before we start `ce-work`, tighten sequencing and risk treatment in this plan without rewriting the whole document."
