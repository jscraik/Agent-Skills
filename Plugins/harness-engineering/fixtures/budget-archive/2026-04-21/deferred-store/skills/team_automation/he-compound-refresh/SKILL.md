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
- Review individual learnings before derived pattern docs.
- Prefer no-write `Keep` decisions over churn when a doc is still trustworthy.

## When to use

- Use when `docs/solutions/` entries may be stale after refactors, migrations, or dependency changes.
- Use when overlapping solution docs should be consolidated with explicit evidence.
- Use when a specific learning or pattern doc is called stale, overlapping, drifted, or superseded.

## Inputs

- Target solution docs, changed code context, and recent validation evidence.
- Scope constraints for refresh depth and ownership boundaries.
- Optional mode modifiers such as `mode:autonomous` and the compatibility alias `mode:autofix`.

## Outputs

- Refresh decision with exact files updated or deferred.
- Consolidation guidance with overlap rationale.
- One maintenance outcome per processed artifact or overlap cluster: `Keep`, `Update`, `Consolidate`, `Replace`, `Archive`, or `Stale`.
- Full markdown report with `Applied` and `Recommended` sections when the run changes or proposes changes.
- Include `schema_version: 1` when structured output is requested.

## Failure Modes

- If no candidate docs exist under `docs/solutions/`, stop and report that no refresh targets were found.
- If a scope hint finds no matches, report the miss clearly; in autonomous mode, stop without guessing.
- If replacement evidence is insufficient, do not invent a successor doc. Mark the artifact stale when possible and report what evidence is missing.

## Procedure

1. Resolve mode first. Normalize `mode:autofix` to the same autonomous behavior as `mode:autonomous`.
2. Discover candidate docs under `docs/solutions/`, excluding `README.md` and legacy `_archived/` content.
3. Match the narrowest successful scope first: directory, frontmatter, filename, then content search.
4. Investigate individual learnings before dependent pattern docs.
5. Analyze the document set for overlap, contradictions, and canonical-doc opportunities before leaving duplicates in place.
6. Classify each artifact or overlap cluster into exactly one maintenance outcome: `Keep`, `Update`, `Consolidate`, `Replace`, `Archive`, or `Stale`.
7. In autonomous mode, apply unambiguous actions directly and stale-mark ambiguous cases instead of guessing through them.
8. Finish with a full markdown report covering evidence, actions applied, and recommendations when writes could not be completed.

## Validation

- Ensure each refresh claim is backed by current repository evidence.
- Ensure changed docs stay aligned with active behavior and constraints.
- Ensure learnings are reviewed before dependent patterns.
- Ensure overlap analysis happens before duplicate docs are left in place.
- Ensure `Update` is not used when the underlying solution changed materially.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not rewrite unrelated solution areas outside validated scope.
- Do not ask whether current code drift is "intentional"; this stage matches docs to current repository reality.
- Do not use external docs when repository evidence is sufficient.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Performing broad doc rewrites without evidence-backed stale signals.
- Creating conflicting guidance across overlapping solution docs.
- Treating age alone as a stale signal.
- Updating solution prose when the real solution changed materially and should be replaced instead.
- Turning autonomous mode into silent guesswork.

## Examples

- "When the user asks to refresh the payment solution docs after a migration and keep only evidence-backed updates."
- "Please inspect the auth learnings and consolidate any overlap instead of leaving multiple stale answers behind."
- "Validate a narrow stale-doc pass on `docs/solutions/` and tell me what was applied versus what still needs a person."

## Full Context

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Assets: [./assets](./assets)
- Assets directory marker: `assets/`
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
