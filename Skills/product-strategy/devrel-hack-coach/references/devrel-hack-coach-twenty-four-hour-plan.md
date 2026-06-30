# DevRel Hack Coach: Twenty-Four-Hour Plan

Asset id: candidate.devcon-hack-coach.twenty-four-hour-plan

Use when a locked spec must become a one-day delivery plan.

## Core Thesis

A 24-hour hackathon plan is a sequence of proof checkpoints, not a full project
schedule. The coach should convert the locked spec into artifacts that keep the
demo alive: smoke test, golden path, second scenario, and pitch dry-run.

## Principles

### Artifacts Beat Intentions

Every checkpoint needs a visible artifact. "Work on backend" is not a plan;
"golden path reaches judged output with sample input" is.

### Protect The Golden Path

When time slips, cut secondary scenarios before cutting the path that proves the
main wedge.

### Pitch Prep Is Delivery Work

The pitch dry-run is not separate from building. It is the final integration
test for whether the prototype, story, and boundaries make sense together.

## Guidance

- Force four named checkpoint artifacts: smoke test, golden path, second
  scenario, and pitch dry-run.
- If a checkpoint cannot name an artifact, return to scope cutting.
- Prefer the smallest acceptable experiment over the biggest possible upside.
- Keep risky integrations and fragile dependencies visible.

## Decision Rules

- If the spec is not locked, refuse to build the plan and return to spec.
- If a checkpoint lacks an artifact, rewrite it until the artifact is visible.
- If a dependency can break the demo, add a fallback or remove the dependency.
- If the plan tries to optimize beyond the judged demo, cut back to the golden
  path.

## Output Shape

- Produce a 24-hour plan with checkpoint time, artifact, owner action, risk, and
  fallback.
- Include four required checkpoints: smoke test, golden path, second scenario,
  and pitch dry-run.
- End with the first hour's exact action list.

## Examples

- Smoke test artifact: "local command or manual path proves the app opens and
  reaches the demo screen."
- Golden path artifact: "recorded or repeatable path from input to judged
  output."
- Pitch dry-run artifact: "timed five-minute script with demo cues and Q&A."

## Recovery

- If the plan slips, cut the second scenario before cutting the golden path.
- If the smoke test fails, stop feature work until the demo shell is reachable.
- If pitch prep is missing near the end, freeze features and prepare the story
  with transparent limitations.

## Validation Ideas

- Given vague checkpoint deliverables, require a scope-cut loop.
- Given a dependency-heavy plan, require a fallback or smaller demo path.

## Boundaries

- This capsule gives planning constraints, not codebase-specific estimates.
- Do not require KnowledgeOS at runtime.
