# Brainstorm Workflow Details

Read when: you need the fuller scope rubric or product pressure-test prompts while running `ce-brainstorm`.

## Scope rubric

- `lightweight`: small, well-bounded, low ambiguity
- `standard`: normal feature or bounded refactor with some decisions to make
- `deep`: cross-cutting, strategic, or highly ambiguous

If scope is unclear, ask one targeted question to disambiguate and then continue.

## Product pressure test prompts

Use the lightest set that gives a trustworthy recommendation.

`lightweight`:
- Is this solving the real user problem?
- Are we duplicating something that already covers this?
- Is there a clearly better framing with near-zero extra cost?

`standard`:
- Is this the right problem, or a proxy for a more important one?
- What user or business outcome actually matters here?
- What happens if we do nothing?
- Is there a nearby framing that creates more user value without more carrying cost?
- Given the current project state, user goal, and constraints, what is the highest-leverage move right now: the request as framed, a reframing, one adjacent addition, a simplification, or doing nothing?

`deep`:
- ask the standard questions
- add: what durable capability should this create in 6-12 months?
- add: does this move the product toward that, or is it only a local patch?
