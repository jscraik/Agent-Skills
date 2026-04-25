---
name: he-compound-refresh
description: Analyze and validate compound Harness Engineering run state, blockers, validation status, and Linear context. Use when lifecycle runs drift, gates fail, blockers appear, or compound work needs refresh.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Philosophy

- Refresh durable knowledge from evidence, not intuition.
- Prefer minimal targeted updates over broad speculative rewrites.
- Review individual learnings before derived pattern docs.
- Prefer no-write `Keep` decisions over churn when a doc is still trustworthy.

## When to use

- Use when `docs/solutions/` entries may be stale after refactors, migrations, or dependency changes.
- Use when overlapping solution docs should be consolidated with explicit evidence.
- Use when a specific learning or pattern doc is called stale, overlapping, drifted, or superseded.

## Failure Modes

- If no candidate docs exist under `docs/solutions/`, stop and report that no refresh targets were found.
- If a scope hint finds no matches, report the miss clearly; in autonomous mode, stop without guessing.
- If replacement evidence is insufficient, do not invent a successor doc. Mark the artifact stale when possible and report what evidence is missing.

## Inputs

- Request, artifacts, repo context, and linked Linear issues.

## Outputs

- `schema_version: 1` when structured; result, validation, blockers, and next Harness Engineering action.

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
- Do not remove important context for budget trimming; move it to references and index it in `../../../references/deferred-context-index.md`.

## Anti-patterns

- Performing broad doc rewrites without evidence-backed stale signals.
- Creating conflicting guidance across overlapping solution docs.
- Treating age alone as a stale signal.
- Updating solution prose when the real solution changed materially and should be replaced instead.
- Turning autonomous mode into silent guesswork.
## Examples

Read when: examples or role-routing details are needed, open the archived references for this skill.
