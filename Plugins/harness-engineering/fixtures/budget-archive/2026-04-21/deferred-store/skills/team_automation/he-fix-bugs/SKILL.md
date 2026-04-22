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
- Investigate before proposing changes, and keep the causal chain from trigger to symptom explicit.

## When to use

- Use when regressions, runtime failures, or tracker defects require evidence-backed debugging.
- Use when issue reproduction and verification are required before coding changes.
- Use when prior fix attempts failed and the request needs disciplined root-cause analysis instead of more trial-and-error edits.

## Inputs

- Symptom report, repro context, and affected scope.
- Logs, traces, tests, and relevant code paths.
- Optional issue-tracker reference or pasted issue context.
- Execution permission: `diagnosis-only` or `diagnose-and-fix`.

## Outputs

- Reproduction evidence, root-cause analysis, fix scope, and verification outcome.
- Clear next action when blocked or when diagnosis is complete but remediation is not yet chosen.
- Regression test recommendation and why existing checks missed the issue when that is knowable.
- Include `schema_version: 1` when structured output is requested.

## Procedure

1. Parse intake first: symptom report, tracker context, expected behavior, and any prior failed attempts.
2. Reproduce and stabilize the failing behavior before proposing changes.
3. Trace backward from the symptom to the point where valid state first became invalid.
4. Test one hypothesis at a time, and for uncertain links require a prediction that can confirm or falsify the chain.
5. Present the root cause, proposed fix scope, and test recommendations before remediation when the request is diagnosis-first or confidence is still settling.
6. When remediation is in scope, check workspace safety, prefer failing-test-first validation, apply the minimal fix, and verify no regressions.

## Validation

- Confirm reproduction and post-fix verification are both recorded.
- Confirm the causal chain from trigger to symptom is explicit before fix work proceeds.
- Confirm fix addresses root cause instead of symptom masking.
- Confirm blocked or partial outcomes name the exact missing condition, evidence gap, or next safest route.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not mark issue fixed without successful verification evidence.
- Do not skip straight to edits when reproduction or root-cause evidence is still missing.
- Do not use shotgun debugging or bundle unrelated changes into one bug fix.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Skipping deterministic reproduction and guessing a fix.
- Shipping fixes that lack regression checks.
- Accepting a symptom fix when the causal chain prediction failed.
- Treating tracker intake, diagnosis, and issue management as one speculative step.

## Examples

- "When the user asks, `Can you inspect this regression that started after the auth refactor, reproduce it, and find the root cause before you fix anything?`"
- "Please investigate this crash, but stop at diagnosis and test recommendations because I do not want edits yet."
- "Help me validate why the last two quick patches failed and tell me what is actually broken."

## Full Context

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Assets: [./assets](./assets)
- Assets directory marker: `assets/`
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
