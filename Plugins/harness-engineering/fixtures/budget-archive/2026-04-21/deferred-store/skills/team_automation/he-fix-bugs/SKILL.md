---
name: he-fix-bugs
description: Restore broken behavior by reproducing failures, identifying root cause, and delivering verified fixes. Use when the user needs regression debugging, incident triage, or bug repair from tracker or direct reports.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Use

- Use this skill as the canonical Harness Engineering bug-fixing stage.
- For full stage policy, workflow details, and examples, load the archived full guide.

## Philosophy

- Reproduce first, then diagnose, then fix.
- Root-cause clarity beats patch velocity.

## When to use

- Use when regressions, runtime failures, or tracker defects require evidence-backed debugging.
- Use when issue reproduction and verification are required before coding changes.

## Inputs

- Symptom report, repro context, and affected scope.
- Logs, traces, tests, and relevant code paths.

## Outputs

- Reproduction evidence, root-cause analysis, fix scope, and verification outcome.
- Clear next action when blocked.
- Include `schema_version: 1` when structured output is requested.

## Procedure

1. Reproduce and stabilize the failing behavior.
2. Diagnose root cause with minimal-change hypothesis testing.
3. Apply fix and verify no regressions.

## Validation

- Confirm reproduction and post-fix verification are both recorded.
- Confirm fix addresses root cause instead of symptom masking.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not mark issue fixed without successful verification evidence.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Skipping deterministic reproduction and guessing a fix.
- Shipping fixes that lack regression checks.

## Full Context

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
Read when: you need full workflow behavior, diagnosis gates, and fix sequencing.
Read when: you need contracts, eval fixtures, anti-patterns, or tracker-intake details.
Read when: you need icon/display metadata and invocation policy.
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
Read when: you need canonical stage policy and fallback behavior.

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
- If required roles are missing from the manifest, create or install them with [../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md](../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md) before rerunning delegated coverage.
