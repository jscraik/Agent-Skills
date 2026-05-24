# High-Signal Steering Feedback

Jamie steering is operating evidence. Treat it as a defect report against the
agent environment, not as ordinary conversation.

## Stop Rule

Stop the active delivery lane when Jamie says a correction is repeated,
high-signal, about your operating behavior, or evidence that the environment is
not absorbing feedback. Do not continue feature implementation until the uptake
loop below has a durable guardrail and validation evidence.

## Proof Before Proceeding

Before resuming ordinary implementation, produce repo-local proof that future
behavior changed. Acceptable proof is a durable artifact plus a validation
result, not an acknowledgement in chat. Prefer deterministic enforcement over
reminders: validators, schema checks, runtime checks, trace instrumentation,
workflow gates, skill-routing changes, retrieval improvements, recovery
handlers, CI gates, or other artifacts that make recurrence harder.

If no durable change is possible in the current environment, record the item as
`blocked` in the ledger with the concrete blocker and do not describe it as
fixed.

Do not resume ordinary implementation after repeated steering until the proof
artifact exists, the validation command has run, and the final report separates
the operational failure from the original delivery task. Treat prompt-only intent,
apologies, and conversational memory as insufficient proof.

A closeout caveat is also a steering candidate when it names a repeated failure,
validation blocker, stale runtime state, or workaround that still requires Jamie
to steer source-of-truth behavior. Before final closeout, rerun the blocked
command or record the blocker in the ledger, and either add a guardrail that
changes future behavior or leave the item explicitly blocked.

## Scope Closure Authority

When Jamie asks for full implementation, agents must not relabel unfinished
acceptance criteria as a smaller slice, follow-up, or future work unless Jamie
explicitly approves that scope change. The authority for narrowing scope must be
visible in the closeout evidence, not inferred from a local implementation plan.

Before marking an issue, goal, PR, or implementation plan `Done`, `complete`, or
equivalent, run a claim-vs-evidence closeout check:

- enumerate the original acceptance criteria or planned requirements.
- map each item to executable behavior, test evidence, artifact evidence, or a
  concrete blocker.
- classify every deferred or future-work item as either explicitly approved by
  Jamie, out of scope by the original plan, or blocking completion.
- leave the tracker or goal open when any planned current-scope item remains
  absent, blocked, or deferred without explicit user approval.

## Uptake Loop

For each high-signal steering item:

1. Classify the failure pattern in plain language.
2. Assign a failure category from the taxonomy below.
3. Decide whether the correction is local or systemic. Treat specific code
   feedback as a visible instance of a possible wider class until repository
   evidence proves otherwise.
4. Search for sibling patterns, structurally similar implementations, repeated
   anti-patterns, and convention drift before deciding scope.
5. Identify the underlying engineering preference or invariant: API philosophy,
   error-handling doctrine, validation expectation, runtime safety assumption,
   architecture intent, repository convention, or operational standard.
6. Identify the mechanism that allowed the failure to reach Jamie.
7. Choose the durable improvement type: validator, schema, trace event, runtime
   check, workflow rule, recovery handler, CI gate, repo artifact, skill
   improvement, context-routing improvement, governance rule, reusable
   primitive, or implementation note.
8. Add the smallest durable guardrail in docs, skills, scripts, validation, or
   memory surfaces.
9. Record the item in [steering-uptake.md](/.harness/quality/steering-uptake.md)
   with the guardrail path, failure category, improvement type, and validation
   command.
10. Run `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json`.
11. Report the exact pass/fail/blocked outcome before resuming the original lane.

## Failure Categories

Use one or more exact category names in each ledger row:

- missing context
- stale state
- weak validation
- hidden assumptions
- retrieval failure
- poor workflow design
- runtime ambiguity
- architecture drift
- lack of verification
- weak observability
- missing guardrails
- missing decomposition
- unclear authority boundaries
- excessive context noise
- poor task routing
- insufficient deterministic enforcement

## Durable Improvement Types

Use one or more exact improvement type names in each ledger row:

- validator
- schema
- trace event
- runtime check
- workflow rule
- recovery handler
- CI gate
- repo artifact
- skill improvement
- context-routing improvement
- governance rule
- reusable primitive
- implementation note
- retrieval improvement
- stale-state prevention
- claim-vs-evidence verification

## Systemic Scope Check

Before finalizing any corrective fix, answer these questions in the work notes
or final report:

- Is this issue likely isolated or systemic?
- Are there equivalent patterns elsewhere in the repository?
- Does this reveal an unstated engineering preference?
- Should this become an enforceable invariant?
- Should related implementations be aligned now?
- Should tooling or validation prevent this class of issue in the future?

Do not apply corrections mechanically to one line, function, file, or local code
path when the feedback plausibly describes a broader design principle.

## Required Evidence

Every ledger entry must include:

- the steering trigger or failure pattern.
- the failure category.
- the local-or-systemic scope decision and sibling-pattern search outcome.
- the inferred engineering preference or invariant.
- the durable improvement type.
- the durable guardrail path.
- the validation command or blocker.
- status: `open`, `validated`, or `blocked`.

Do not mark an item `validated` when the guardrail is only a promise, a chat
reply, or an untested local edit.

## Behavior Contract

- Prefer a narrow guardrail that prevents recurrence over broad process prose.
- Prefer validators over reminders, runtime truth over summaries, enforcement
  over intention, and structured evidence over conversational memory.
- Prefer systemic remediation when sibling patterns share the same mechanism.
- If a local fix is intentionally narrow, state why broader alignment,
  enforcement, or validation is not warranted.
- If the same feedback has appeared before, search `.harness/**`, `Docs/**`,
  `AGENTS.md`, and relevant skills before editing.
- If validation tooling is blocked, classify the blocker directly and leave the
  ledger status as `blocked`.
- If a steering item affects agent behavior outside this repo, add a memory
  update note only when Jamie explicitly asks for behavior/environment
  refinement.
