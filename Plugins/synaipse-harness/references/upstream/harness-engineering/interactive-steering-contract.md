# Interactive Steering Contract

Use this contract when a Harness Engineering stage has inspected repo, Linear,
session, and `.harness` evidence and one remaining user choice materially
changes the route, scope, artifact identity, Linear destination, execution
authority, risk posture, or closure recommendation.

## Core Rule

Explore first. Ask second. Ask once per unresolved decision branch.

When the platform blocking question tool is available, use it
(`request_user_input`, `AskUserQuestion`, or `ask_user`). If no blocking
question tool is available, ask one concise chat question and stop. Do not bury
the choice in a long report.

In Codex sessions, `request_user_input` is the preferred blocking question tool
only when it is available in the current mode. Use it for one to three short
questions, each with two or three mutually exclusive choices. Put the recommended
choice first, label it `(Recommended)`, and use a short header. Do not emulate
the tool with a long textual multiple-choice form when the tool is available; if
the tool is unavailable, ask one concise plain-text question and stop.

## Ask When

- `he-router`: more than one lifecycle stage remains valid after deterministic
  routing and the missing source artifact or lifecycle state would change the
  selected stage.
- `he-brainstorm`: multiple warranted survivors remain and selecting one would
  shape the downstream spec, plan, Linear work, or implementation slice.
- `he-brainstorm` `domain_interview` mode: a repository language conflict,
  fuzzy term, scenario boundary, context selection, or ADR threshold decision
  remains after codebase exploration. This mode may ask multiple sequential
  questions across the session, but each turn asks only one branch question and
  waits for feedback before continuing.
- `he-strategy`: the requested cognition mode or full-pipeline extent is unclear
  and the choice changes artifact output.
- `he-reframe`: a finding is borderline between reframe program, Linear issue,
  ADR, or Do Not Create and the choice changes migration commitment.
- `he-linear-plan`: Linear destination, active set, initiative/project/milestone,
  or mutation authority cannot be proven from evidence.
- `he-spec`: behavior, scope boundary, acceptance authority, or selected slice is
  unresolved after source inspection.
- `he-plan`: the plan is complete but multiple valid next stages exist and the
  user has not already authorized one.
- `he-work`: branch, goal, plan, Linear issue, or selected slice conflicts before
  editing.
- `he-code-review`: review-only, readiness, autofix, or investigation mode is
  ambiguous and a mutation could occur.
- `he-eval-report`: closure could be Complete or Complete with follow-up; ask
  accept, challenge, or rework before recommending Linear completion.
- `he-reconcile`: earliest incomplete lifecycle stage, resume target, or refresh
  route conflicts across Linear, spec, plan, PR, or Project Brain evidence.

## Do Not Ask When

- repo, Linear, PR, or `.harness` evidence can answer the question safely;
- the user explicitly authorized the next stage in the same request;
- the stage is running headless, autonomous, or as an eval case;
- the ambiguity is low-impact preference that does not change route, scope,
  mutation, closure, or validation;
- required evidence is missing and the safe outcome is a blocker, not a choice.

## Question Shape

Ask one high-signal question with two or three mutually exclusive choices. Put
the recommended choice first, state the operational impact of each choice, and
allow a free-form correction when the UI supports it.

For `domain_interview` mode, make the recommendation explicit in the first
choice label and keep the question about a decision, not evidence lookup. Good
questions choose the canonical term, distinguish two concepts, settle whether an
edge scenario belongs in or out of the model, select the owning context, or
confirm whether an ADR candidate meets the hard-to-reverse / surprising /
real-trade-off threshold.

For spec and plan work, use `request_user_input` only after source inspection has
left one consequential decision open:

- whether inferred intent should become binding requirements, stay assumptions,
  or be excluded;
- which selected slice should be specified or planned;
- whether an ambiguous user-facing solution changes scope;
- whether a complete plan should hand off to implementation, Linear update,
  review, or stop.

Do not ask the user to supply file paths, prior-art tests, tracker facts, or repo
state that the agent can inspect. Do not ask optional preference questions before
drafting; record low-risk assumptions instead.

Good questions ask for a decision, not information archaeology. Prefer:

- "Which survivor should become the spec input?"
- "Should this plan hand off to implementation, review, or stop here?"
- "Which Linear destination should this work use?"
- "Do you accept this eval closure recommendation, challenge evidence, or send
  it back for rework?"

Avoid asking the user to perform evidence lookup that the agent can do.

## Autonomous / Headless Mode

Never block headless or autonomous execution with a user question. Record the
assumption and keep the route conservative:

```yaml
interactive_status: autonomous_assumption
assumption: "<decision assumed for this run>"
evidence: "<repo/Linear/.harness evidence used>"
risk: "<why this may be wrong>"
downstream_checkpoint: "<where a human or later stage must confirm>"
```

If the assumption could authorize mutation, closure, broad scope expansion, or
Linear changes, do not proceed with that mutation. Return a blocker or
ready-to-confirm payload instead.

## Trace Fields

When structured output is used, include:

```yaml
interactive_status: not_needed|asked|autonomous_assumption|blocked
question_id: "<stable id or not_applicable>"
choice: "<selected user choice or not_applicable>"
assumption: "<headless assumption or not_applicable>"
evidence: "<short evidence pointer>"
next_stage: "<selected HE stage or blocked>"
```

This keeps the steering decision searchable in `.harness` artifacts, handoffs,
evals, and session evidence.
