---
name: he-improve
description: Analyze and improve an existing implementation through metric-driven, bounded iteration loops. Use when the user wants Harness Engineering optimization or tuning rather than one-shot implementation.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Use

- Use this skill as normal for this Harness Engineering stage.
- For full stage policy, workflow details, and examples, load the archived full guide.

## Philosophy

- Optimize with measurable evidence, not subjective preference.
- Keep experiments bounded and reversible.

## When to use

- Use when behavior exists and needs targeted quality, reliability, or performance improvement.
- Use after baseline implementation when iterative tuning is appropriate.

## Inputs

- Baseline behavior, metrics, and current constraints.
- Candidate improvement hypotheses and acceptable risk bounds.

## Outputs

- Prioritized improvement plan with measurable success criteria.
- Iteration outcomes and next-step recommendation.
- Include `schema_version: 1` when structured output is requested.

## Procedure

1. Analyze baseline behavior and identify improvement targets.
2. Run bounded iterations with explicit measurement gates.
3. Keep, revise, or discard changes based on measured outcomes.

## Validation

- Ensure each iteration has explicit metric target and rollback posture.
- Ensure accepted changes are justified by observed improvement.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not broaden scope beyond bounded optimization goals.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Tuning without baseline metrics.
- Keeping changes that do not improve target outcomes.

## Full Context

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
Read when: you need full workflow behavior, gating, and deliverable expectations.
Read when: you need schema contracts, eval cases, donor-parity notes, and prompt templates.
Read when: you need executable measurement or probe helpers.
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
