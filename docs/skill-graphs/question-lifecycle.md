# Question Lifecycle Contract

Defines the canonical timing, ownership, payload, and evaluation rules for all user-facing questions in the skill graph runtime.

## Table of Contents
- [Why this contract exists](#why-this-contract-exists)
- [Goals](#goals)
- [Non-goals](#non-goals)
- [Core principle](#core-principle)
- [Question types](#question-types)
- [Runtime phases](#runtime-phases)
- [Ownership model](#ownership-model)
- [Timing policy](#timing-policy)
- [Blocking policy](#blocking-policy)
- [Question payload contract](#question-payload-contract)
- [Persistence and telemetry](#persistence-and-telemetry)
- [Decision rules](#decision-rules)
- [State machine](#state-machine)
- [UX rules](#ux-rules)
- [Evaluation contract](#evaluation-contract)
- [Migration guidance](#migration-guidance)
- [Examples](#examples)
- [Validation checklist](#validation-checklist)

## Why this contract exists

The repository currently has three valid but separate question mechanisms:
- **routing clarification** when intent confidence is low,
- **discovery / approval questions** before execution,
- **post-run feedback capture** for learning and quality telemetry.

Without one canonical lifecycle, skills can ask at the wrong point, duplicate asks, or mix implementation-time questions with post-run feedback.

This contract makes question timing a **runtime policy** instead of a prose convention scattered across individual `SKILL.md` files.

## Goals

- Make question timing deterministic and auditable.
- Separate clarification, approval, and feedback into different runtime phases.
- Keep user interruption low by asking only for missing or decision-critical information.
- Make question events machine-readable so timing quality can be evaluated.
- Preserve compatibility with the skill router and recursive skill graph capture model.

## Non-goals

- This contract does not redefine skill routing confidence thresholds.
- This contract does not replace domain-specific interview logic.
- This contract does not require every skill to ask questions.
- This contract does not make feedback mandatory when the runtime is operating in silent or system-only capture mode.

## Core principle

**Questions are phase-typed runtime events, not generic prompt behavior.**

A skill may declare that it needs clarification, approval, or feedback support, but the runtime owns:
- whether a question is needed,
- when it is asked,
- whether it blocks execution,
- how it is persisted.

## Question types

All question events MUST declare exactly one `question_type`:

1. `route_clarification`
   - Purpose: disambiguate which skill or route should handle the request.
   - Typical trigger: top candidates are too close, or required route confidence is not met.

2. `preflight_clarification`
   - Purpose: collect missing required inputs after a route is chosen but before execution begins.
   - Typical trigger: a required field is missing and cannot be inferred safely.

3. `approval_checkpoint`
   - Purpose: obtain explicit consent before risky, destructive, expensive, or irreversible actions.
   - Typical trigger: a run crosses a policy or safety boundary.

4. `post_run_feedback`
   - Purpose: capture lightweight outcome telemetry after a result, recommendation, or failure is shown.
   - Typical trigger: terminal run state with feedback capture enabled.

No other user-facing question types are canonical in v1.

## Runtime phases

Question events MUST occur in one of these phases:

1. `route`
2. `hydrate_context`
3. `preflight`
4. `execution`
5. `approval_gate`
6. `terminal`
7. `feedback_capture`

Allowed mapping:

| Question type | Allowed phases |
| --- | --- |
| `route_clarification` | `route` |
| `preflight_clarification` | `hydrate_context`, `preflight` |
| `approval_checkpoint` | `approval_gate` |
| `post_run_feedback` | `terminal`, `feedback_capture` |

A question asked outside its allowed phase is a contract violation.

## Ownership model

Ownership is by runtime layer, not by individual skill prose.

| Layer | Owns | Must not own |
| --- | --- | --- |
| Skill router | `route_clarification` | post-run feedback |
| Skill executor | `preflight_clarification` | route disambiguation |
| Guardrail / policy gate | `approval_checkpoint` | routine discovery |
| Skill graph capture runtime | `post_run_feedback` | implementation-time clarification |

Skills may provide metadata for these layers, but they MUST NOT unilaterally decide timing.

## Timing policy

### 1) Route phase
Ask only when routing confidence is below policy threshold or ambiguity is explicitly detected.

If the router can safely choose a route, do not ask.

### 2) Hydrate context / preflight
Ask only for information that is both:
- required for correct execution, and
- unavailable from thread, files, tools, or safe defaults.

Prefer inference, retrieval, or explicit assumptions over asking when risk is low.

### 3) Execution
No new clarification questions during normal execution.

Execution-time questions are allowed only when the run hits a policy boundary and is converted into an `approval_checkpoint`.

### 4) Terminal / feedback capture
Feedback questions belong after:
- result delivery,
- recommendation review,
- or a failed / aborted run.

Feedback MUST NOT appear as a precondition for normal execution.

## Blocking policy

Each question event MUST declare `blocking: true | false`.

Canonical defaults:

| Question type | Default blocking |
| --- | --- |
| `route_clarification` | `true` |
| `preflight_clarification` | `true` |
| `approval_checkpoint` | `true` |
| `post_run_feedback` | `false` |

Rules:
- Non-blocking questions must never stall run completion.
- Post-run feedback must be skippable and should degrade to `status=missing` when unanswered.
- A blocking question requires a documented `required_for` field.

## Question payload contract

Every question event MUST include:

```yaml
schema_version: "1.0"
question_id: string
run_id: string
skill_id: string
question_type: route_clarification | preflight_clarification | approval_checkpoint | post_run_feedback
phase: route | hydrate_context | preflight | execution | approval_gate | terminal | feedback_capture
origin_layer: router | executor | guardrail | graph_capture
blocking: boolean
required_for: string
prompt_style: multiple_choice | binary | one_tap_feedback
header: string
question: string
options:
  - id: string
    label: string
    description: string
recommended_option_id: string
confidence_trigger: number | null
risk_tier: low | medium | high | null
supersedes_question_id: string | null
created_at: string
expires_at: string | null
```

### Tool contract

Canonical Codex interaction tool: `request_user_input`.

Legacy references to `askquestiontool` or `default_mode_request_user_input` should be treated as compatibility aliases in documentation only, not as the preferred contract language.

Machine-readable payload shape:
- `/Users/jamiecraik/dev/agent-skills/docs/skill-graphs/schemas/question-event.schema.md`

## Persistence and telemetry

Question events SHOULD be persisted as structured telemetry alongside skill-graph artifacts.

Minimum fields to record per question event:
- question payload,
- answer payload or `missing`,
- answered_at,
- answer_latency_ms,
- question_outcome:
  - `answered`
  - `skipped`
  - `timed_out`
  - `superseded`
- downstream_effect:
  - `route_selected`
  - `execution_started`
  - `approval_granted`
  - `feedback_recorded`
  - `no_effect`

Recommended derived metrics:
- unnecessary question rate,
- duplicate question rate,
- wrong-phase question rate,
- answer-to-action latency,
- post-run feedback completion rate,
- avoidable interruption rate.

## Decision rules

### Rule 1: Prefer retrieval over asking
If code, docs, thread state, or trusted context can answer the question cheaply, retrieve first.

### Rule 2: Prefer assumptions over low-value questions
If the missing detail does not materially change the path and a safe default exists, proceed with an explicit assumption.

### Rule 3: Ask only branch-changing questions
A question should change one of:
- route,
- required inputs,
- policy permission,
- outcome telemetry.

If it changes none of those, do not ask.

### Rule 4: Do not mix question types
A single question event must not combine:
- route clarification plus feedback,
- approval plus general discovery,
- preflight clarification plus retrospective rating.

### Rule 5: Current user intent wins
Injected memory, prior lessons, or historical preferences are advisory. If they conflict with the current request, prefer the current request and ask a clarifying question only when the conflict is materially blocking.

## State machine

```text
route
  -> route_clarification?
  -> hydrate_context
  -> preflight_clarification?
  -> preflight
  -> execution
  -> approval_checkpoint?
  -> terminal
  -> post_run_feedback?
  -> feedback_capture
```

Rules:
- `route_clarification` may only send control back to `route`.
- `preflight_clarification` may only send control back to `hydrate_context` or `preflight`.
- `approval_checkpoint` may only resume into `execution` or finalize at `terminal`.
- `post_run_feedback` must never reopen routing or preflight.

## UX rules

- Prefer one question at a time unless the runtime explicitly supports a bounded batch and the current phase benefits from it.
- Use concise headers and short options.
- For feedback capture, prefer one-tap choices with optional note.
- Preserve low cognitive load: ask for missing decisions, not narrative essays.
- If a question is non-blocking, say so implicitly by allowing the run to complete without waiting.

## Evaluation contract

Question timing quality MUST be evaluated, not assumed.

Required eval categories:
1. **Asked too early**
2. **Asked too late**
3. **Asked unnecessarily**
4. **Failed to ask when required**
5. **Wrong question type**
6. **Wrong blocking behavior**
7. **Duplicate / repeated ask**
8. **Feedback asked before result delivery**

Recommended harnesses:
- transcript replay,
- baseline vs delta timing comparison,
- ambiguous-route fixtures,
- terminal feedback completion tracking,
- regression tests for wrong-phase asks.

## Migration guidance

### Immediate repo guidance
- Keep interview skills for deliberate discovery flows.
- Keep router clarification in router/runtime policy.
- Keep post-run graph feedback in capture/runtime policy.
- Remove wording that implies every non-trivial skill must ask for feedback before completion.

### Recommended wording replacement
Replace:
- “collect user feedback before closing the run”

With:
- “if post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event after result delivery.”

### Compatibility note
Existing docs that mention `default_mode_request_user_input` or `askquestiontool` should be updated to prefer Codex `request_user_input` while preserving a brief alias note where historical parity matters.

## Examples

### Correct sequence: ambiguous route
1. router detects low confidence
2. emit `route_clarification`
3. select skill
4. continue to context hydration

### Correct sequence: missing required repo path
1. route selected
2. executor detects missing required path
3. emit `preflight_clarification`
4. start execution after answer

### Correct sequence: risky action
1. execution plans destructive change
2. guardrail emits `approval_checkpoint`
3. on approval, execution resumes

### Correct sequence: graph recommendation review
1. recommendation report is shown
2. runtime emits `post_run_feedback`
3. unanswered feedback persists as `missing`
4. run remains terminal regardless

### Incorrect sequence
- asking worked / partly / didn’t work before output is shown;
- asking route questions after execution starts;
- asking an approval question that is really just discovery;
- reopening implementation because a post-run feedback prompt was skipped.

## Validation checklist

- `question_type` matches allowed phase.
- `blocking` matches canonical default or includes rationale.
- `post_run_feedback` is non-blocking.
- runtime uses `request_user_input` as the canonical Codex tool name.
- no skill-level prose claims ownership of question timing.
- transcript replay confirms no wrong-phase prompts on benchmark fixtures.
- feedback capture degrades cleanly to `missing` without stalling completion.
