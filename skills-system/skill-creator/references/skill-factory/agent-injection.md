# Agent Injection

Use this reference only when a new skill explicitly needs a dedicated Codex
agent role, subagent handoff, or installed role wiring.

## Role Creation Path

1. Decide whether the skill needs a role at all. Prefer no role for ordinary
   authoring, review, or refactor skills.
2. Reuse an existing role when its model, permissions, and output contract
   already match the skill.
3. Create a purpose-built role only when the skill needs a distinct stance,
   bounded tool permissions, artifact-first output, or repeatable review lane.
4. Keep the role contract narrow: trigger, inputs, allowed actions, forbidden
   actions, output artifact, and validation owner.

## Closeout

Report exactly one role mode:

- `none`: no agent role needed.
- `reuse-existing`: existing role selected, with path/name.
- `create-purpose-built`: new role proposed or installed, with path/name.
