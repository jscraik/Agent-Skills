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
- Keep orchestration, evidence gathering, and durable learning capture explicit instead of collapsing them into generic advice.

## When to use

- Route/resume work from the correct Harness Engineering stage.
- Capture a verified fix in `docs/solutions/` and avoid duplicate docs by refreshing existing artifacts when overlap is high.
- Decide whether a request needs lifecycle orchestration, solved-problem capture, or a resume-from-stage handoff before downstream work starts.

## Inputs

- Problem statement or lifecycle context.
- Optional existing artifacts and solved-evidence references.
- Optional capture preference: `full` or `compact-safe`.
- Optional existing solution-doc path or suspected overlap target.

## Outputs

- Mode decision: `full-lifecycle`, `resume-from-stage`, or `learning-capture`.
- Explicit next stage decision with blocker/risk notes.
- For learning capture: capture mode (`full` or `compact-safe`) and one created or updated solution doc path.
- If a high-overlap solution already exists, explicit refresh/update recommendation instead of a duplicate-doc plan.
- Structured output includes `schema_version: 1` when requested.

## Procedure

1. Select lifecycle mode using artifact-first evidence.
2. For lifecycle routing, continue from the earliest incomplete or untrusted stage.
3. If the user intent is ambiguous between stage orchestration and solved-problem capture, ask one direct question before continuing.
4. For learning capture, preserve `full` as the default and treat `compact-safe` as explicit opt-in.
5. For learning capture, validate solved evidence, gather supporting inputs, and write exactly one durable solution artifact.
6. If past agent sessions are needed as evidence, route broad session inventory/extraction to `skill-refactor`; if the result is a reusable workflow, route skill creation to `skillify`.
7. If helpers are used during learning capture, they return text only; the orchestrator writes the final artifact.
8. If overlap with an existing solution is high, refresh the existing doc instead of creating a duplicate.
9. Recommend `he-compound-refresh` only when adjacent stale or overlapping docs need selective follow-up beyond the current artifact.

## Validation

- Confirm mode selection matches available evidence.
- Confirm stage recommendation names the exact next Harness Engineering command or stage.
- For learning capture, verify solved status before writing docs, keep the one-file-write contract explicit, and ensure duplicate-avoidance logic is explicit.
- Any refresh recommendation must be narrow and evidence-backed rather than a blanket cleanup suggestion.
- Fail fast: stop at first failed gate and do not continue.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not document unverified fixes as durable solutions.
- Do not treat `he-compound` as a substitute for implementation, debugging, review, or refresh stages that still need to happen.
- Do not turn generic session-history search into a Harness Engineering stage; consume `skill-refactor` or `skillify` outputs when session evidence is relevant.
- Do not let helper agents write intermediate files during learning capture.
- Do not recommend deleting or ignoring protected process artifacts just to simplify the handoff.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Guessing stage progression without checking existing artifacts.
- Recording unresolved incidents as solved knowledge.
- Creating a duplicate solution doc when a high-overlap artifact should be refreshed.
- Returning broad "use Harness Engineering" guidance without naming the exact mode and next stage.

## Examples

- "When the user asks, `Inspect the artifacts we already have and resume from the earliest incomplete Harness Engineering stage.`"
- "This bug is fixed and verified. Please capture the learning in `docs/solutions/` without creating a duplicate doc."
- "Help me decide whether this needs stage routing or direct learning capture, then validate the right mode first."

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
