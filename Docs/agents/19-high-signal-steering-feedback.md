# High-Signal Steering Feedback

Jamie steering is operating evidence. Treat it as a defect report against the
agent environment, not as ordinary conversation.

## Stop Rule

Stop the active delivery lane when Jamie says a correction is repeated,
high-signal, about your operating behavior, or evidence that the environment is
not absorbing feedback. Do not continue feature implementation until the uptake
loop below has a durable guardrail and validation evidence.

## Uptake Loop

For each high-signal steering item:

1. Classify the failure pattern in plain language.
2. Identify the mechanism that allowed the failure to reach Jamie.
3. Add the smallest durable guardrail in docs, skills, scripts, validation, or
   memory surfaces.
4. Record the item in [steering-uptake.md](/.harness/quality/steering-uptake.md)
   with the guardrail path and validation command.
5. Run `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json`.
6. Report the exact pass/fail/blocked outcome before resuming the original lane.

## Required Evidence

Every ledger entry must include:

- the steering trigger or failure pattern.
- the durable guardrail path.
- the validation command or blocker.
- status: `open`, `validated`, or `blocked`.

Do not mark an item `validated` when the guardrail is only a promise, a chat
reply, or an untested local edit.

## Behavior Contract

- Prefer a narrow guardrail that prevents recurrence over broad process prose.
- If the same feedback has appeared before, search `.harness/**`, `Docs/**`,
  `AGENTS.md`, and relevant skills before editing.
- If validation tooling is blocked, classify the blocker directly and leave the
  ledger status as `blocked`.
- If a steering item affects agent behavior outside this repo, add a memory
  update note only when Jamie explicitly asks for behavior/environment
  refinement.
