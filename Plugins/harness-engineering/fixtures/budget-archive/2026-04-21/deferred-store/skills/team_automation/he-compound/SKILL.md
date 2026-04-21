---
name: he-compound
description: "Analyze Harness Engineering lifecycle state, plan the correct stage routing, and capture verified solved problems into durable docs/solutions knowledge. Use when the user asks to start or resume from the correct stage, or to document a verified fix as reusable team guidance."
metadata:
  skill-type: team_automation
---

# Harness Engineering Compound

Progressive-disclosure entrypoint for stage orchestration and durable learning capture in Harness Engineering.

## Philosophy

- Route to the correct stage before acting.
- Capture verified outcomes as reusable team knowledge.

## When to use

- Route/resume work from the correct Harness Engineering stage.
- Capture a verified fix in `docs/solutions/` and avoid duplicate docs by refreshing existing artifacts when overlap is high.

## Inputs

- Problem statement or lifecycle context.
- Optional existing artifacts and solved-evidence references.

## Outputs

- Mode decision: `full-lifecycle`, `resume-from-stage`, or `learning-capture`.
- Explicit next stage decision with blocker/risk notes.
- For learning capture: one created or updated solution doc path.
- Structured output includes `schema_version: 1` when requested.

## Procedure

1. Select lifecycle mode using artifact-first evidence.
2. For lifecycle routing, continue from the earliest incomplete or untrusted stage.
3. For learning capture, validate solved evidence and write exactly one durable solution artifact.
4. If overlap with an existing solution is high, refresh the existing doc instead of creating a duplicate.

## Validation

- Confirm mode selection matches available evidence.
- Confirm stage recommendation names the exact next Harness Engineering command or stage.
- For learning capture, verify solved status before writing docs and ensure duplicate-avoidance logic is explicit.
- Fail fast: stop at first failed gate and do not continue.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not document unverified fixes as durable solutions.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Guessing stage progression without checking existing artifacts.
- Recording unresolved incidents as solved knowledge.

## Full Context

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Template/assets: [./assets/resolution-template.md](./assets/resolution-template.md), [./assets/icon-small.png](./assets/icon-small.png), [./assets/icon-large.png](./assets/icon-large.png)
Read when: detailed policy or templates are required.

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
- If required roles are missing from the manifest, create or install them with [[codex-agent-creator]] before rerunning delegated coverage.
