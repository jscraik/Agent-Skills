# Product Design Critic Compaction Context

Read when: you need expanded cognitive-load checks, additional examples, or full feedback-protocol detail moved from `SKILL.md` for line-budget governance.

## Cognitive load checks (expanded)
- Check whether users must remember information from another screen or prior step to complete the current decision.
- Check whether necessary context is hidden in another panel, modal, or tab.

## Additional examples
- "Use official standards, not opinion alone. Evaluate this healthcare consent UI and explain tradeoffs with references."
- "Inspect this permission-change flow and validate it against official standards before final build."
- "For a competitor teardown, recommend what we can migrate into our product this sprint."

## Decision feedback protocol (expanded)
- Question timing is runtime-owned; do not let the skill decide timing.
- If enabled, emit non-blocking `post_run_feedback` via `request_user_input` after result delivery.
- Capture `decision`, `outcome`, and `confidence`.
- Persist feedback with `python3 Infrastructure/scripts/record_skill_feedback.py`.
