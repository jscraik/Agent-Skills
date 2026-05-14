# Skill Management

## Purpose

Keep skill authoring and lifecycle details out of the always-loaded root
instructions while preserving the commands agents need when working on skills.

Before changing skills, sync policy, runtime projections, or agent-facing docs,
read [UBIQUITOUS_LANGUAGE.md](/UBIQUITOUS_LANGUAGE.md).

## Install Failure Recovery

```bash
./bin/ask skills install <url> --remediate --robot
./bin/ask skills audit <path> --level strict --robot
```

Use `--remediate` to scaffold missing files during install recovery, then run a
strict audit before treating the skill as ready.

## Folding Strategy

If `./bin/ask skills fold source target --robot` returns confidence `>= 0.2`, fold
rather than duplicate unless the user explicitly wants a separate skill.

## Line Budget

Keep `SKILL.md` bodies at or below the 360-line split budget. When a skill
exceeds that budget, move bulk detail to a focused reference file and leave a
clear link in the `SKILL.md`.

Do not delete important, still-valid context just to reduce line count. Preserve
that context by relocation, not by leaving it in the entrypoint.

Removed context must have a disposition:

- `moved-to-reference`: still valid, reusable, and too bulky for `SKILL.md`.
- `superseded`: replaced by a newer compressed rule or reference.
- `intentionally-discarded`: stale, duplicated, unsafe, inappropriate,
  contradicted by newer guidance, or no longer part of the skill contract.
- `not-context`: formatting, navigation, repetition, or low-signal prose.

Do not create context landfills. Deferred references should protect useful
knowledge, not preserve stale or inappropriate text for its own sake.

See [Tooling and Command Policy](/Docs/agents/02-tooling-policy.md#skill-line-budget-policy)
for the detailed policy.
