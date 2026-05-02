---
title: Agent Capability Control Plane
status: active
date: 2026-05-01
agent_compatible: true
schema_version: 1
linear_issue: JSC-246
governing_spec: Docs/specs/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-spec.md
governing_plan: Docs/plans/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-plan.md
---

# Agent Capability Control Plane

## Promise

Teach your coding agents how your work actually works, then prove they
remembered.

Agent Skills Kit is not just a repo of prompt files. It is a control plane for
agent capabilities:

1. Author capabilities once in canonical source.
2. Route user intent to the right skill, plugin, or runtime surface.
3. Keep context small with root routers and generated command handles.
4. Validate quality, drift, runtime projection, and repo surface ownership.
5. Preserve proof that a capability is reachable and useful.

## Four Outcomes

| Outcome            | What It Means                                                                                                              | Current Proof Surface                                                                              |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Remember workflows | Agents can reuse local review, validation, delivery, and operating standards.                                              | `Skills/**`, `Plugins/**`, `.agents/skills/**`, `ask skills resolve`, `ask skills goal`            |
| Keep context small | Agents see routed front doors and command handles instead of every full workflow body.                                     | `ask runtime budget --json --robot`, rooted projection, generated `$handle` surfaces               |
| Prevent drift      | Canonical source, generated manifests, runtime projections, plugin caches, and artifacts have distinct ownership.          | `ask repo surface --json`, `ask repo doctor-catalog --json --robot`, repo surface ownership policy |
| Prove quality      | A capability should have structural, security, projection, runtime, and outcome evidence before it is treated as reliable. | `ask skills audit`, `ask skills prove`, workouts, evals, validation logs, closeout evidence        |

## First Five Minutes

Use these commands to orient a human or coding agent:

```bash
./bin/ask repo status --json --robot
./bin/ask repo doctor-catalog --json --robot
./bin/ask repo surface --json
./bin/ask runtime budget --json --robot
./bin/ask skills handles --check --json
```

These are deliberately namespace-first. New product commands should stay under
`repo` or `skills` until evidence proves a top-level alias reduces real
operator friction.

The next command contracts are specified in
[ask Product Golden Path Command Contracts](/Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md):

- `ask repo doctor`
- `ask repo onboard`
- `ask skills improve`
- `ask skills explain`
- `ask skills prove`
- `ask repo next`
- `ask repo closeout`

## Minimum Outcome Proof

Validation is necessary, but it is not the same as outcome proof. Outcome proof
should show that a capability changed agent behavior on a realistic task.

Minimum proof format:

```json
{
  "proof_id": "skill-or-goal-date",
  "capability": "he-code-review",
  "goal": "review a tracked delivery slice against Linear/spec/plan evidence",
  "before": {
    "failure": "Agent could not identify missing traceability or validation evidence.",
    "evidence": "transcript, workout, eval, or reviewer finding"
  },
  "after": {
    "result": "Agent produced severity-ranked readiness findings with exact artifact evidence.",
    "evidence": "workout run, eval result, validation log, or transcript artifact"
  },
  "commands": [
    "./bin/ask skills audit <path> --level strict",
    "./bin/ask runtime budget --json --robot",
    "./bin/ask skills prove <handle> --json --robot"
  ],
  "status": "proven"
}
```

Rules:

- Separate reachability proof from quality proof.
- Do not claim outcome proof from a structural audit alone.
- Keep long transcripts and logs in generated artifacts or indexed references.
- Link the proof back to the skill, plugin, Linear issue, plan acceptance ID, or
  workout scenario that caused it.
- Record the next command an agent should run when proof is incomplete.

## Current Evidence From JSC-246

The repo surface control-plane plan established the first infrastructure slice:

- Surface ownership policy:
  [Docs/agents/15-repo-surface-ownership.md](/Docs/agents/15-repo-surface-ownership.md)
- Non-destructive inventory:
  `Infrastructure/scripts/validation-and-linting/check_repo_surface_inventory.py`
- Public report route:
  `./bin/ask repo surface --json`
- Cleanup preparation:
  `Infrastructure/scripts/validation-and-linting/prepare_repo_surface_cleanup.py`
- Product command contracts:
  [Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md](/Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md)

Baseline facts from the implementation:

- `ask runtime budget --json --robot` passes while keeping
  `advanced_visible_count` and first-level handle count visible.
- `ask repo surface --json` reports tracked-surface policy debt without deleting
  files.
- `ask repo doctor-catalog --json --robot` verifies the canonical skill count
  across README, `SKILL.md`, `ask skills list`, and route metadata.
- `ask skills goal "use he-work to implement P5 product framing and outcome
  proof documentation for JSC-246" --json --robot` resolves to `he-work`.

## Product Direction

The durable product shape is:

```text
goal -> candidate capability -> explanation -> proof -> sync/closeout
```

That is why the next executable surface should prefer namespace-first commands
such as `ask repo doctor`, `ask skills improve`, and `ask repo closeout` instead
of exposing more one-off top-level commands.

The product should feel simple even when the infrastructure is serious:

- Humans ask what they want agents to get better at.
- Agents receive one recommended next command.
- Maintainers can trace every runtime surface back to canonical source.
- Quality claims are backed by audit, projection, runtime, and outcome
  evidence.
