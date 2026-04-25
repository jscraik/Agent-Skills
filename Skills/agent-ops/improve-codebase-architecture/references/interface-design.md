# Interface Design

Use this only after the user chooses an architecture opportunity to explore.

## Step 1: Frame the Problem

Summarize:

- the module or context that should own the behavior;
- callers and workflows that depend on it;
- dependency categories involved;
- constraints from tests, performance, rollout, data ownership, or Linear decisions;
- what must stay stable.

Include a tiny illustrative code sketch only to show the shape of the problem. Do not present it as the answer.

## Step 2: Generate Alternatives

For broad or risky work, produce at least three materially different interface options:

1. **Minimal interface**: one to three entry points, optimized for a small stable surface.
2. **Flexible interface**: supports known variants without leaking implementation detail.
3. **Caller-optimized interface**: shaped around the most common or highest-value caller.
4. **Ports-and-adapters interface**: use only when dependency categories justify real adapters.

Use subagents only when the design space is large enough to benefit from separate perspectives. Give each reviewer a narrow, different interface goal.

## Step 3: Compare

For each option, compare:

- caller clarity;
- hidden implementation complexity;
- test surface;
- migration cost;
- reversibility;
- likely future pressure;
- fit with `CONTEXT.md` terms.

## Step 4: Recommend

Pick one option. Be opinionated and explain the trade-off.

Avoid recommendations that:

- add an interface for a hypothetical future implementation;
- require every caller to learn more concepts;
- preserve shallow helper tests as the main confidence surface;
- invent vocabulary that is not present in code, docs, or user language.
