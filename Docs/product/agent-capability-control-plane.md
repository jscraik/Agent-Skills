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
5. Diagnose capability readiness from one namespace-first command.
6. Preserve proof that a capability is reachable and useful.

## Key Outcomes

| Outcome            | What It Means                                                                                                              | Current Proof Surface                                                                              |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Remember workflows | Agents can reuse local review, validation, delivery, and operating standards.                                              | `Skills/**`, `Plugins/**`, `.agents/skills/**`, `ask skills resolve`, `ask skills goal`            |
| Keep context small | Agents see routed front doors and command handles instead of every full workflow body.                                     | `ask runtime budget --json --robot`, rooted projection, generated `$handle` surfaces               |
| Prevent drift      | Canonical source, generated manifests, runtime projections, plugin caches, and artifacts have distinct ownership.          | `ask repo surface --json`, `ask repo doctor-catalog --json --robot`, repo surface ownership policy |
| Diagnose readiness | One capability can be checked for source ownership, handle resolution, runtime reachability, audit state, metadata gaps, and outcome-proof availability. | `ask skills doctor <handle-or-path> --json --robot` |
| Package safely     | Skill promotion can check version, compatible roles, runtime needs, maturity, provenance, and share readiness before install/share claims. | `ask skills package <handle-or-path> --json --robot` |
| Retrieve memory    | Agents can search repo learnings, wiki learnings, and skill lesson artifacts without prompt-stuffing the whole corpus. | `ask skills memory list/read/search --json --robot` |
| Prove quality      | A capability should have structural, security, projection, runtime, and outcome evidence before it is treated as reliable. | `ask skills audit`, `ask skills prove`, workouts, evals, validation logs, closeout evidence        |

## First Five Minutes

Use these commands to orient a human or coding agent:

```bash
./bin/ask repo status --json --robot
./bin/ask repo doctor --json --robot
./bin/ask skills improve "<goal>" --json --robot
./bin/ask skills explain <handle> --json --robot
./bin/ask skills doctor <handle> --json --robot
./bin/ask skills package <handle> --json --robot
./bin/ask skills memory search "<query>" --json --robot
./bin/ask skills prove <handle> --json --robot
./bin/ask repo closeout --changed --json --robot
```

These are deliberately namespace-first. New product commands should stay under
`repo` or `skills` until evidence proves a top-level alias reduces real
operator friction.

Use the diagnostic commands directly when investigating one surface:
`./bin/ask repo doctor-catalog --json --robot`,
`./bin/ask repo surface --json --robot`,
`./bin/ask runtime budget --json --robot`, and
`./bin/ask skills handles --check --json --robot`.

Use `./bin/ask skills doctor <handle-or-path> --json --robot` when one
capability is in question. It composes resolver, runtime-reachability,
canonical-source, compat/strict audit, metadata, package-readiness, and
outcome-proof signals without replacing `skills prove` as the outcome-proof
scorecard. The embedded package-readiness block uses the same contract fields as
`skills package`, so diagnostics and promotion checks do not drift apart.

Use `./bin/ask skills package <handle-or-path> --json --robot` before treating a
skill as installable, shareable, or role-compatible. It reports
`skill-package-readiness.v1` with version, compatible roles, runtime needs,
maturity, provenance, and share-readiness fields; `--strict` fails when those
package metadata fields are incomplete.

Use `./bin/ask skills profiles [profile] --json --robot` before work where the
agent needs an explicit runtime mode. Profiles currently cover `authoring`,
`package-review`, `plugin-share`, `eval`, and `live-mutation`, each with
allowed roots, write policy, permissions, required evidence, and stop
conditions.

Eval runs now expose `eval_status`, `blocker_class`, and
`blocker_taxonomy` in JSON output, so smoke-eval automation can distinguish
`blocked_user_input`, `blocked_auth`, `blocked_runtime`,
`timeout_no_output`, and `timeout_partial_output` from skill behavior
failures.

Use `./bin/ask skills memory list/read/search --json --robot` when an agent needs
durable repo learnings with provenance and freshness. The provider is read-only
and searches `.harness/memory`, wiki learnings, canonical learning docs, and
skill lesson artifacts without replacing the canonical wiki or Project Brain
mutation paths.

and searches `.harness/memory`, `Wiki/wiki/learnings`, `Docs/solutions`, and
skill lesson artifacts. These are the supported read roots; memory mutation
continues through Project Brain and canonical wiki workflows instead of the
read-only memory commands.

The next command contracts are specified in
[ask Product Golden Path Command Contracts](/Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md):

- `ask repo doctor`
- `ask repo onboard`
- `ask skills improve`
- `ask skills explain`
- `ask skills doctor`
- `ask skills package`
- `ask skills profiles`
- `ask skills memory`
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
  `advanced_visible_count: 173` and `first_level_default_count: 118` visible.
- `ask repo surface --json` reports tracked-surface policy debt without deleting
  files.
- `ask repo doctor-catalog --json --robot` verifies the canonical skill count
  `32` across README, `SKILL.md`, `ask skills list`, and route metadata.
- `ask skills handles --json --no-handles --robot` reports `108` generated
  command handles from rooted manifests with no command-surface violations.
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
