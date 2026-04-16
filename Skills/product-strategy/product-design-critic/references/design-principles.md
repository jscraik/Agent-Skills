# Design Principles

Use these principles when critiquing or shaping product surfaces.

## Job before interface
- Start from the user moment, not from component ideas.
- Confirm the high-cost mistake first, then design to reduce it.
- If the job is unclear, call that out before proposing polish.

## Surface ownership
- Assign one owning surface for intent and action.
- Keep slower context in supporting surfaces.
- Treat ambient status as lightweight signals, not competing UI blocks.

## Hierarchy discipline
- One primary action per moment.
- One primary object per decision point.
- Delay secondary details until needed.

## Trust and governance
- Show actor, permission scope, and consequence at the decision moment.
- Make reversibility obvious for high-stakes operations.
- Prefer explicit provenance over implied system magic.

## State completeness
- Always critique empty, loading, partial, error, interrupted, and revoked states.
- Evaluate whether recovery paths are clear and humane.
- Penalize designs that only succeed on the happy path.

## Competitor adaptation
- Extract reusable pattern logic.
- Explain why the pattern works.
- Adapt to the target product's model and constraints.
- Do not copy visual language by default.

## Anti-patterns
- Dashboard sprawl where every panel has equal visual weight.
- Hidden approvals or silent side effects.
- Styling upgrades presented as product strategy.
