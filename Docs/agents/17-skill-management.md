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

Skill setup must follow the [Zero-Setup Agent Workspace](/Docs/agents/21-zero-setup-agent-workspace.md)
product rule. A skill is not professionally ready if it requires the customer
to manually stitch together install, projection, runtime, and validation steps
before an agent can discover and report readiness.

High-level workflow skills whose truth lives in UI or app state need
[CTF Workflow Evals](/Docs/agents/23-ctf-workflow-evals.md) before a
release-readiness claim. Examples include login, upload-and-chat, access grants,
and other workflows where capturing a planted flag is the practical proof of
success.

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

## Reference Quality

References are part of the Skills SDK package contract, not spare notes. Treat
them like scripts: if a skill uses `references/**`, those files must work for
future agents at package-readiness time.

The SDK package contract reports `values.reference_quality` and
`./bin/ask skills package verify <skill> --json --robot` blocks broken reference
sets. The minimum enforced floor is:

- every file under `references/` is readable and non-empty;
- structured references (`.json`, `.yaml`, `.yml`) parse successfully;
- `references/contract.yaml`, when present, declares purpose, inputs, and
  outputs;
- `references/evals.yaml`, when present, declares claims and cases.

Passing this floor does not prove that a reference is great; it prevents known
low-quality reference packages from being promoted as ready. When a reference
drives execution, evals, rollback, validation, or policy, keep it specific,
current, and runnable enough that an agent can use it without re-deriving the
contract from chat history.

See [Tooling and Command Policy](/Docs/agents/02-tooling-policy.md#skill-line-budget-policy)
for the detailed policy.
