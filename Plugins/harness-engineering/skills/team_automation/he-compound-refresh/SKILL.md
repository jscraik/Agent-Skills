---
name: he-compound-refresh
description: Analyze and validate compound Harness Engineering run state, blockers, validation status, and Linear context. Use when lifecycle runs drift, gates fail, blockers appear, or compound work needs refresh.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Philosophy

- Refresh lifecycle state from evidence, not intuition.
- Prefer minimal targeted updates over broad speculative rewrites.
- Review live branch, PR, Linear, validation, review-thread, and session evidence before choosing the next HE stage.
- Prefer a blocked or no-write decision over guessing when state is missing.

## When to use

- Use when a compound Harness Engineering run has drifted after CI, review, Linear, branch, validation, or handoff changes.
- Use when the user says continue, resume, refresh, re-check, or asks where an active HE workflow is blocked.
- Use when session evidence shows repeated lifecycle loops that need a refreshed next-stage decision.
- Use when `docs/solutions/` entries may be stale after refactors, migrations, or dependency changes.

## Failure Modes

- If no live target or evidence source exists, stop and report the missing surface instead of continuing from stale chat context.
- If session evidence is requested but the collector or archive paths are unavailable, report the exact missing path or command failure.
- If replacement evidence is insufficient, do not invent a next stage or successor doc. Mark the artifact stale when possible and report what evidence is missing.

## Inputs

- Request, artifacts, repo context, linked Linear issues, branch/PR state, validation output, review-thread state, and optional session evidence.

## Outputs

- `schema_version: 1` when structured; refreshed state, evidence sources, blockers, and next Harness Engineering action.

## Procedure

1. Resolve mode first. Normalize `mode:autofix` to the same autonomous behavior as `mode:autonomous`.
2. Inventory the active lifecycle targets: governing plan/spec, branch, PR, CI checks, review threads, Linear issue, validation commands, and previous handoff notes.
3. If prior sessions or repeated failures are part of the request, read [../../../references/session-evidence-contract.md](../../../references/session-evidence-contract.md) and prefer `~/.agents/session-collector` before raw archive scans.
4. Re-run or inspect the smallest safe live-state checks needed to classify the current blocker.
5. Classify each target into exactly one maintenance outcome: `Continue`, `Review`, `Fix`, `Plan`, `Heartbeat`, `Blocked`, `Done`, `Keep`, `Update`, `Consolidate`, `Replace`, `Archive`, or `Stale`.
6. Route the next action to one HE stage and explain why earlier stages are not being skipped.
7. In autonomous mode, apply unambiguous refresh actions directly and stale-mark ambiguous cases instead of guessing through them.
8. Finish with a markdown report covering evidence, actions applied, blockers, and the exact next HE invocation.

## Validation

- Ensure each refresh claim is backed by current repository, tracker, review, validation, or session evidence.
- Ensure session-derived claims cite the collector output, archived path, session index count, or exact sample used.
- Ensure changed docs stay aligned with active behavior and constraints.
- Ensure active lifecycle drift is resolved before duplicate docs are left in place.
- Ensure `Update` is not used when the underlying solution changed materially.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not rewrite unrelated solution areas outside validated scope.
- Do not continue from stale thread memory when live state or session evidence is available.
- Do not ask whether current code drift is "intentional"; this stage matches docs to current repository reality.
- Do not use external docs when repository evidence is sufficient.
- Do not remove important context for budget trimming; move it to references and index it in `../../../references/deferred-context-index.md`.

## Anti-patterns

- Performing broad refreshes without evidence-backed drift signals.
- Creating conflicting guidance across overlapping solution docs.
- Treating age alone as a stale signal.
- Updating solution prose when the real solution changed materially and should be replaced instead.
- Treating `continue` as permission to skip review, validation, or heartbeat gates.
- Turning autonomous mode into silent guesswork.

## Full Context

- Assets: [icon-small.png](./assets/icon-small.png), [icon-large.png](./assets/icon-large.png)
- Subagent call contract: [../../../references/subagent-call-contract.md](../../../references/subagent-call-contract.md)

## Examples

- "Can you inspect the compound run state and tell me which HE stage should resume after CI and review changed?"
- "Help me check whether these overlapping solution notes should be kept, updated, consolidated, or archived."
- "This lifecycle run drifted after CI failed. Re-read the artifacts and report the exact blocker before we continue."
- "Use archived sessions and the collector to find the repeated blocker in this HE workflow before we continue."
