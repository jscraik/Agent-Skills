# Unslopify Discovery Interview

Use this only when the request is underspecified and interaction is available.
Ask one round at a time; do not dump the full plan.

## Request user input mini-templates

Round 1 target question:

What should this skill help you do?

What exact repo path, diff, PR, skill, or artifact should this skill inspect?

Why this matters: the skill must stay scoped to canonical source and avoid editing projections, caches, generated output, or unrelated surfaces.

## Copy paste payload examples

Ambiguous target:

What exact repo path, diff, PR, skill, or artifact should this skill inspect?

Ambiguous evidence:

Which finding, score, validator, or proof should we fix first?

## Round 1: Target

What exact repo path, diff, PR, skill, or artifact should this skill inspect?

Why this matters: the skill must stay scoped to canonical source and avoid editing projections, caches, generated output, or unrelated surfaces.

## Round 2: Success

What outcome should count as done: review only, patch, eval repair, validation evidence, or a handoff?

Why this matters: the skill chooses different safety boundaries for read-only work, repo writes, external writes, and validation-only runs.

## Round 3: Proof

Which validator, test, command, or evidence source should prove the result?

Why this matters: completion claims need pass, fail, or blocked evidence rather than confidence from prose.

## Round 6: Confirmation

Does this capture the target, boundary, and proof well enough for me to proceed?

Anything to add or change before implementation?

