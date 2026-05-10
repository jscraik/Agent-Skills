# Routing Invariants

Purpose: keep execution routing deterministic, explainable, and low-context.

## Proven Invariants

- Agents should start from `repo doctor`, not repo archaeology.
- The golden path is the strategic product spine:
  - `repo doctor`
  - `skills improve`
  - `skills explain`
  - `skills prove`
  - `repo closeout`
- Skill routing must preserve canonical source pointers.
- Routing must distinguish experimental breadth from trusted core.
- Default-visible promotion requires proof status.

## Strategic Assumptions

- One primary route is better than a buffet unless ambiguity is real.
- Skill/plugin breadth is useful only when routing quality scales faster than catalog size.
- Routing ambiguity is architectural drift.

## Operating Principles

- Every blocker should expose one exact next command or file.
- `skills improve` should return one primary recommendation when possible.
- `skills explain` should show canonical source, visibility, limits, and smallest validation.
- `skills prove` should label proof level.
- Generated handles must route, not teach.

## Forbidden Regressions

- Multiple competing "first" commands.
- Hidden execution paths.
- Unranked skill recommendations where one route is clearly better.
- Plugin or skill routes promoted without proof or ownership.
- Routing prose replaces executable command output.

## Evidence Basis

- `.harness/strategy/agent-skills-strategy.md`
- `.harness/triage/agent-skills-triage.md`
- `.harness/features/agent-skills-intent.md`
