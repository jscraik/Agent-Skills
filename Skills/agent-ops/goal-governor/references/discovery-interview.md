# Goal Governor Discovery Interview

Use this only when the user has asked for governed goal work but the first safe
goal decision is underspecified. Ask one round at a time; do not dump the full
plan.

## Request user input mini-templates

Round 1 target question:

What should this skill help you do?

What exact goal board, target project, primary audit document, or runtime
blocker should Goal Governor inspect first?

Why this matters: Goal Governor changes behavior depending on whether the work
is prompt review, board creation, continuation, repair, runtime doctoring, or
validation-only closeout.

## Copy paste payload examples

Ambiguous target:

What exact goal board, target project, primary audit document, or runtime
blocker should Goal Governor inspect first?

Ambiguous authority:

Should I only review the goal prompt, or should I proceed with governed
implementation once the board contract is clear?

Ambiguous proof:

Which evidence should decide readiness: board validator output, native goal
state, receipts, PR checks, review threads, tracker state, or implementation
notes?

## Round 1: Target

What exact goal board, target project, primary audit document, or runtime
blocker should Goal Governor inspect first?

Why this matters: the mode changes depending on whether the first action is
review, create, continue, doctor, check, repair, or import.

## Round 2: Authority

Should this stay in prompt-review mode, or do you want governed implementation
to start after the board contract is clear?

Why this matters: review mode must avoid tools and side effects unless the user
explicitly authorizes governed implementation.

## Round 3: Runtime Truth

What runtime truth is available now: goal.md, state.yaml, receipts.jsonl,
native goal status, CI checks, review threads, tracker state, or Browser
implementation-notes preview?

Why this matters: completion and continuation claims require current evidence,
not conversation memory or stale board text.

## Round 4: Boundaries

Which files, modules, or Worker scopes are allowed to change, and which areas
are explicitly isolated?

Why this matters: Worker work must stay inside board-owned allowed files and
must not silently broaden the blast radius.

## Round 5: Confirmation

Does this capture the goal path, mode, authority, runtime truth, validation
surface, implementation-notes requirement, and allowed scope well enough for me
to proceed?

Anything to add or change before I implement it?
