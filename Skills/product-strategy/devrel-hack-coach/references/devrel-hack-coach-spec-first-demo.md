# DevRel Hack Coach: Spec-First Demo

Asset id: candidate.devcon-hack-coach.spec-first-demo

Use when a selected idea needs to become a buildable hackathon spec.

## Core Thesis

A hackathon spec is a build permission gate. It should name the user, goal,
observable demo moment, in-scope work, exclusions, success criteria, and red
flags before implementation begins.

## Principles

### Observable Beats Aspirational

The spec is ready only when the demo moment can be described as stage actions.
"Improve productivity" is not observable; a judge-visible input, action, and
output is.

### Constraints Are Part Of The Spec

Out-of-scope temptations and red flags are not negative space. They protect the
build from predictable time sinks.

### Locking Means All Fields Are Concrete

Do not mark a spec locked because the idea feels clear. Mark it locked when the
fields are complete enough to plan and validate.

## Guidance

- Require complete one-page fields: goal, user, demo moment, scope, exclusions,
  success criteria, and red flags.
- Make the demo moment observable as stage directions.
- Cap in-scope work at three items.
- Name out-of-scope temptations before the build starts.

## Decision Rules

- If any required spec field is blank, block planning and ask for that field.
- If the demo moment is not observable, rewrite it as actions a judge can watch.
- If scope exceeds three in-scope items, cut until the golden path is buildable.
- If exclusions are missing, ask what tempting work must not be built.

## Output Shape

- Return a one-page spec with: goal, user, pain, demo moment, in-scope,
  out-of-scope, success criteria, red flags, and lock status.
- Mark the spec as locked only after every field is concrete.
- Include a short "build may start when" line listing the remaining blockers.

## Examples

- Weak demo moment: "show productivity" becomes "paste a repo issue, generate a
  three-step task plan, open the cited file, and run one validation command."
- Scope cut: keep ingestion, task map, and validation proof; defer auth,
  analytics, and multi-tenant settings.
- Red flag: "depends on a paid API key that may rate-limit during judging."

## Recovery

- If the spec keeps expanding, return to the single judge-visible demo moment.
- If the user cannot name success criteria, ask what must be true after five
  minutes for the judges to understand the win.
- If the idea cannot be specified without implementation details, switch back to
  ideation pressure testing.

## Validation Ideas

- Given a partially filled spec, block Phase 3.
- Given a non-observable demo moment, rewrite it into judge-visible actions.

## Boundaries

- This capsule proves a spec-readiness rubric, not implementation feasibility.
- Do not provide file layouts, code, or pair-programming help.
- Do not require KnowledgeOS at runtime.
