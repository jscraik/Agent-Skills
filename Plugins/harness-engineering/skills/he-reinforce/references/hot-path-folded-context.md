# Hot-Path Folded Context

## Purpose
Preserve detailed context folded out of SKILL.md so the active he-reinforce entrypoint stays below the hot-path soft budget without losing usable guidance.

## 2026-05-15 Soft-Warning Cleanup

Disposition:
- moved-to-reference: bulky examples, extended output fields, repeated evidence detail, and long procedure tails.
- superseded: repeated headings whose active entrypoint now points to shared contracts.
- intentionally-discarded: none in this file; prompt rot is tracked in shared folded context when removed.

## Folded Philosophy

Compound learning only after proof. `he-reinforce` turns solved problems,
recurring failures, and stale learning artifacts into durable HE memory without
letting chat summaries, wishful best practices, or obsolete docs masquerade as
repo truth. Local `AGENTS.md`, rules, hooks, command boundaries, and approval
gates outrank this skill.

## Folded When to Use

- A user says the problem is fixed, solved, working now, or worth remembering.
- A repeated bug, validation failure, review finding, workflow mistake, or
  session-continuity gap needs durable prevention guidance.
- `.harness/solutions/**`, `.harness/knowledge/**`, `.harness/decisions/**`,
  or legacy `docs/solutions/**` need freshness review.
- Project Brain exists and a verified repo learning, decision, invariant, or
  rule should be synchronized or explicitly blocked.

## Folded When Not to Use

- The problem is not solved or validation evidence is missing.
- The request only needs lifecycle state reconciliation; use `he-reconcile`.
- The request needs implementation, code review repair, Linear mutation, or
  closure proof; use the owning HE stage.
- The user wants generic note-taking detached from repo evidence.

## Folded Procedure

1. Select mode: `capture_solved_problem`, `refresh_learning`,
   `consolidate_overlap`, `project_brain_sync`, `continuity_snapshot`, or
   `blocked`.
2. Prove eligibility. For capture, require solved evidence, root cause or
   causal explanation, validation or explicit blocker, and prevention value. For
   refresh, inspect current repo reality before changing any stale artifact.
3. Keep scope tight: start with 2-3 focused learning surfaces first, such as
   `.harness/solutions/**`, Project Brain paths, active `AGENTS.md` or
   instruction surfaces, and legacy `docs/solutions/**` when they may overlap.
4. Avoid duplicate memory. Update an existing high-overlap artifact; create a
   new artifact only when it adds retrieval value. Consolidate overlap only when
   one canonical artifact can clearly replace weaker duplicates.
5. Write at most one primary artifact per run unless the user explicitly asks
   for a broader maintenance batch. The orchestrating agent owns final writes;
   helper agents may return text evidence only.
6. Store new HE solution captures under `.harness/solutions/**`. Treat legacy
   `docs/solutions/**` as source evidence unless the repo declares it canonical.
7. When Project Brain is active, route stable facts into the correct surface:
   `.harness/knowledge/**`, `.harness/decisions/**`, `.harness/rules/**`, or
   `.harness/memory/LEARNINGS.md`. If unsure, block with the exact missing
   classification rather than guessing.
8. For continuity snapshots, preserve a fixed section structure if one exists.
   Prioritize current state, pending next action, important files/functions,
   commands and output interpretation, errors and corrections, learnings, key
   results, and terse worklog. Do not rewrite headings, template guidance, or
   generated scaffolding unless the repo declares the template itself stale.
9. Keep continuity artifacts bounded. Condense old or duplicated details before
   adding new ones; preserve exact error strings, commands, user corrections,
   and output requested by the user ahead of narrative filler.
10. For refresh, classify each candidate as `keep`, `update`, `consolidate`,
   `replace`, `delete_candidate`, or `blocked`. Do not delete without explicit
   authority, inbound-link review, and a replacement/obsolescence note.
11. Confirm discoverability: active instruction or routing surfaces must tell
   future agents where to look, or the output must include a discoverability
   blocker.
12. Apply the BLUF review contract to non-trivial learning, decision,
    continuity, or stale-note artifacts so the learning value, proof status,
    refresh decision, and next action are visible before detail.
13. Apply the visual reference contract only when a durable learning artifact
    explains a repeated causal chain, source-of-truth drift, rollback path, or
    prevention loop more clearly as a small diagram or comparison table.

## Folded Safety Boundaries

- Forbidden: learning capture from unsolved issues, private transcript dumps,
  secret exposure, broad stale-doc rewrites, or destructive deletion without
  explicit authority.
- Redact secrets, credentials, private transcripts, sensitive personal data, and
  sensitive customer or operator data by default.
- Approval required: deleting or replacing learning artifacts, writing outside
  repo-owned `.harness/**`, external tracker mutation, broad maintenance sweeps,
  or changing canonical instruction policy.
- Safe fallback: write no artifact and return the smallest evidence gap or
  refresh scope needed.

## Folded Confidence Reporting

Tie confidence to solved proof, source freshness, root-cause clarity, validation
evidence, overlap search depth, redaction certainty, and Project Brain
classification. For continuity snapshots, tie confidence to recency, section
coverage, exact-command/error preservation, and whether stale details were
condensed. Do not claim a learning exists, Project Brain is current, or a
refresh is complete unless the file was actually written or inspected.

## Folded Gotchas

- This skill reinforces learning; it does not decide lifecycle closure.
- One high-value artifact beats several vague notes.
- `delete_candidate` is not deletion authority.
- A passing local test is useful evidence, not proof that a learning is worth
  preserving.
- Continuity capture must preserve retrieval value after compaction; a chat
  transcript dump is not a memory artifact.

## Folded Examples

- When the user says "The Linear template bug in `he-linear-plan` is fixed and the
  validator passes; capture the root cause and prevention rule under
  `.harness/solutions/**`."
- When the user asks to validate durable learning, review the old
  `.harness/solutions/linear-template-rule.md`
  against the current plugin and decide whether to keep, update, consolidate, or
  mark it blocked."

## Folded Assets

Use `assets/resolution-template.md` only when creating or refreshing solution
artifacts.

## Folded References

Read `references/contract.yaml` for the full reinforcement contract and
`references/evals.yaml` for validation scenarios. Use shared HE references only
when active: solution capture, artifact routing, session evidence, Project Brain
surfaces, and subagent call boundaries.
Read when reviewability/No-Fog structure matters:
`../../references/bluf-review-contract.md`.
Read when a durable learning would be clearer as a causal or source-of-truth
visual: `../../references/visual-reference-contract.md`.
Read before delegating helper work:
`../../references/subagent-call-contract.md`.

Deferred context index: `../../references/deferred-context-index.md`.
Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.
