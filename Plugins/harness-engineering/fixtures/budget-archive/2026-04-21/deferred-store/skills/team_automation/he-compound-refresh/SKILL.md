---
name: he-compound-refresh
description: Use when Harness Engineering needs to review and refresh stale `docs/solutions/` learnings and pattern docs against the current codebase, including overlap consolidation after refactors, migrations, or dependency upgrades.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Use

- Use this skill as normal for this Harness Engineering stage.
- For full stage policy, workflow details, and examples, load the archived full guide.

## Philosophy

- Refresh durable knowledge from evidence, not intuition.
- Prefer minimal targeted updates over broad speculative rewrites.

## When to use

- Use when `docs/solutions/` entries may be stale after refactors, migrations, or dependency changes.
- Use when overlapping solution docs should be consolidated with explicit evidence.

## Inputs

- Target solution docs, changed code context, and recent validation evidence.
- Scope constraints for refresh depth and ownership boundaries.

## Outputs

- Refresh decision with exact files updated or deferred.
- Consolidation guidance with overlap rationale.
- Include `schema_version: 1` when structured output is requested.

## Procedure

1. Identify candidate stale docs and collect current-code evidence.
2. Evaluate overlap and staleness risk for each candidate.
3. Apply narrow refresh updates and record rationale.

## Validation

- Ensure each refresh claim is backed by current repository evidence.
- Ensure changed docs stay aligned with active behavior and constraints.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not rewrite unrelated solution areas outside validated scope.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Performing broad doc rewrites without evidence-backed stale signals.
- Creating conflicting guidance across overlapping solution docs.

## Full Context

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
