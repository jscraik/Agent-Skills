# System Prompt Design for Agent-Native Behavior

## Goal

Define agent behavior as outcome-oriented policy rather than brittle procedural scripts.

## Structure template

1. Identity and operating scope.
2. Core behavior constraints.
3. Capability usage guidance.
4. Decision criteria for ambiguous cases.
5. Completion and blocked-state policy.
6. Safety boundaries and escalation rules.

## Prompt design principles

- Specify outcomes and quality criteria.
- Provide decision criteria instead of hard if/else matrices where possible.
- Keep constraints testable.
- Prefer concise, explicit language over narrative prose.

## Capability framing

Document tools in user-language terms:

- What can be done.
- What cannot be done.
- What requires approval.

This reduces avoidable clarification loops.

## Guardrail placement

Put high-risk rules directly in top-level prompt sections:

- destructive actions
- privacy/secrets handling
- irreversible operations

Do not bury critical safety logic in optional appendices.

## Prompt maintenance

Evolve prompts using observed failure modes:

- capture failure pattern
- propose minimal prompt delta
- validate against regression evals
- keep a changelog of behavioral shifts
