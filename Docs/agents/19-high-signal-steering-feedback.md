# High-Signal Steering Feedback

Jamie steering is operating evidence. Treat it as a defect report against the
agent environment, not as ordinary conversation.

## Stop Rule

Stop the active delivery lane when Jamie says a correction is repeated,
high-signal, about your operating behavior, or evidence that the environment is
not absorbing feedback. Do not continue feature implementation until the uptake
loop below has a durable guardrail and validation evidence.

Runtime recovery is part of this stop rule. Do not call a wait, resume, poll, or
closeout action with a guessed or stale runtime identifier. A runtime handle is
usable only when the immediately preceding tool result returned it as active.
Otherwise, rediscover state with a direct repo command and record repeated
handle misuse as steering uptake before resuming implementation.

Do not parallelize runtime-recovery calls. Wait/poll/resume actions are
stateful and must be single-threaded against one real active handle. Never call
them to test whether a guessed identifier is valid; invalid-handle probing is a
failure of claim-vs-evidence discipline, not a discovery mechanism.
This applies equally through direct wait tools and multi-tool wrappers: a
synthetic, placeholder, or known-invalid handle is never acceptable as a probe,
even when the expected result is a harmless failure.

For repository implementation, review, status, or file-inspection work, prefer
direct repo commands over runtime wait or poll actions. A wait action is not a
general status check. It is allowed only to resume a live asynchronous operation
whose handle was returned by the immediately preceding tool result. If this rule
is violated in the same turn, stop the feature lane again, record a fresh
steering-uptake row, validate the steering surfaces, and continue using direct
repo commands only.

After a fabricated or stale wait-handle call occurs in a turn, do not call any
wait/poll/resume action again for the rest of that turn unless a new asynchronous
tool call in that same turn first returns a real live handle. Repeated invalid
wait calls in the same turn are not additional discovery; they are evidence that
the recovery lane must be constrained to direct repo commands until the next
operator turn.

Post-compaction recovery checklist:

- If the continuation summary does not include a concrete active runtime handle
  from the immediately preceding visible tool result, treat all prior handles as
  unusable.
- Start with direct repository commands such as `git status`, `stat`, `tail`,
  `jq`, or the repo wrapper that re-discovers state from disk.
- Do not use multi-tool wrappers for wait, poll, resume, or closeout recovery.
  Wrapper calls do not weaken the handle-evidence requirement.
- If an invalid wait/poll/resume call happens anyway, stop the delivery lane,
  record the recurrence in this ledger, validate steering uptake, and continue
  with single direct repo commands only for the rest of that turn.

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

If the durable change has started but proof is not complete, keep the ledger row
`open` and state the remaining proof explicitly. An open row must name the
pending, blocked, in-progress, after-push, next-proof, or not-claimed condition
in its validation evidence so future agents cannot mistake an unresolved uptake
lane for a completed guardrail.

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

1. Identify the feedback signal in plain language.
2. Identify the root operational failure that let the signal reach Jamie.
3. Classify the failure pattern in plain language.
4. Assign a failure category from the taxonomy below.
5. Decide whether the correction is local or systemic. Treat specific code
   feedback as a visible instance of a possible wider class until repository
   evidence proves otherwise.
6. Search for sibling patterns, structurally similar implementations, repeated
   anti-patterns, and convention drift before deciding scope.
7. Identify the underlying engineering preference or invariant: API philosophy,
   error-handling doctrine, validation expectation, runtime safety assumption,
   architecture intent, repository convention, or operational standard.
8. Identify the mechanism that allowed the failure to reach Jamie.
9. Choose the durable system improvement type: validator, schema, trace event, runtime
   check, workflow rule, recovery handler, lint rule, schema constraint,
   style rule, CI check, shared utility, repo artifact, skill improvement,
   context-routing improvement, governance rule, reusable abstraction,
   reusable primitive, architectural policy, or implementation note.
10. Add the smallest durable guardrail in docs, skills, scripts, validation, or
    memory surfaces.
11. Record the item in [steering-uptake.md](/.harness/quality/steering-uptake.md)
    with the guardrail path, failure category, improvement type, and validation
    command.
12. Run `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json`.
13. Report the exact pass/fail/blocked outcome before resuming the original lane.

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
- schema contract
- schema constraint
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
- generated runtime guardrail
- runtime projection guardrail
- runtime persistence guardrail
- doctor blocker
- selection policy
- eval contract

Ledger rows must use known taxonomy values from the Failure Categories and
Durable Improvement Types lists. The validator rejects unknown category or
improvement-type labels so steering uptake cannot pass as vague ceremony.

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
When a correction says the implementation is not doing what Jamie wants, treat
the named example as evidence of possible wider misalignment before assuming it
is a local defect.

## Required Evidence

Every ledger entry must include:

- the feedback signal or steering trigger.
- the root operational failure that let the signal reach Jamie.
- the steering trigger or failure pattern.
- the failure category.
- the local-or-systemic scope decision and sibling-pattern search outcome.
- the inferred engineering preference or invariant.
- the durable improvement type.
- the durable guardrail path.
- the validation command or blocker, including evidence that the improvement
  changes future behavior.
- for `open` status, the explicit remaining proof or blocker condition.
- the repo artifact, implementation note, or other documented surface that
  preserves the rule for future agents.
- status: `open`, `validated`, or `blocked`.

Do not mark an item `validated` when the guardrail is only a promise, a chat
reply, or an untested local edit.

## Behavior Contract

- Prefer a narrow guardrail that prevents recurrence over broad process prose.
- Prefer validators over reminders, runtime truth over summaries, enforcement
  over intention, and structured evidence over conversational memory.
- Never fabricate command, tool, session, cell, or placeholder identifiers to
  satisfy a workflow shape. A wait, resume, retry, or closeout action must point
  at a real handle returned by the runtime in the current lane; otherwise run
  the direct command, re-discover the live state, or classify the blocker.
- After any fabricated runtime handle is attempted, stop using wait or resume
  actions until a real runtime-returned handle is visible in the immediately preceding tool result.
  Recover by re-discovering live state with a direct
  command, recording the failure in this ledger, and validating the steering
  surfaces before ordinary implementation resumes.
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
