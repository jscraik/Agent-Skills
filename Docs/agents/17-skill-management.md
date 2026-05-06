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

Do not delete important context just to reduce line count. Context is preserved
by relocation, not removed.

See [Tooling and Command Policy](/Docs/agents/02-tooling-policy.md#skill-line-budget-policy)
for the detailed policy.
