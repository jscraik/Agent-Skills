# Ready-to-Use Prompts for Spec Development

## Prompt 1: Socratic Spec Reviewer (Foundation)
Use to interrogate and clarify a Foundation Spec before writing.

```
Act as a skeptical senior PM.
Read my Foundation Spec below and do NOT rewrite it yet.

1) Ask the 15 most important clarifying questions that would materially change scope, UX, or architecture.
2) Identify the single most ambiguous part of the problem statement and propose 3 alternate interpretations.
3) Propose a primary metric + 2 guardrails and explain why.
4) Confirm the JTBD-lite job framing, in-scope/out-of-scope, and primary journey (happy path only).
5) List hidden assumptions and risks (top 3–5).

Spec:
<paste>
```

## Prompt 2: UX Ambiguity Killer (PRD → UX spec)
Convert a Foundation Spec into a UX specification with explicit mental model and states.

```
Convert this PRD/Foundation Spec into a UX specification with:
- Mental model alignment
- Information architecture (entities + where they appear)
- Affordances & actions (what is clickable/editable/destructive)
- System feedback states (empty/loading/error/partial/auth)
- UX acceptance criteria in Gherkin (Given/When/Then)

Input:
<paste>
```

## Prompt 3: Build Plan Decomposer (UX spec → epics/stories)
Turn a UX spec into an executable build plan with epics and stories.

```
Turn this UX spec into:
1) Outcome → opportunities → solution (with rejected alternatives)
2) Top 3–5 assumptions/risks with mitigations
3) A sequenced list of epics (smallest coherent order)
4) Stories per epic with acceptance criteria
5) A minimal telemetry plan (events + properties)
6) A minimal test plan (unit/integration/e2e + failure modes)

UX spec:
<paste>
```
