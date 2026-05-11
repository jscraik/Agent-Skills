---
name: he-reinforce
description: "Create or refresh evidence-bound Harness Engineering learning artifacts from verified solved problems. Use when a fix worked, a repeated failure should become durable knowledge, or .harness/solutions and Project Brain need maintenance."
metadata:
  skill-type: team_automation
---
# Skill: Harness Engineering Reinforce

## Philosophy

Compound learning only after proof. `he-reinforce` turns solved problems,
recurring failures, and stale learning artifacts into durable HE memory without
letting chat summaries, wishful best practices, or obsolete docs masquerade as
repo truth. Local `AGENTS.md`, rules, hooks, command boundaries, and approval
gates outrank this skill.

## When to Use

- A user says the problem is fixed, solved, working now, or worth remembering.
- A repeated bug, validation failure, review finding, workflow mistake, or
  session-continuity gap needs durable prevention guidance.
- `.harness/solutions/**`, `.harness/knowledge/**`, `.harness/decisions/**`,
  or legacy `docs/solutions/**` need freshness review.
- Project Brain exists and a verified repo learning, decision, invariant, or
  rule should be synchronized or explicitly blocked.

## When Not to Use

- The problem is not solved or validation evidence is missing.
- The request only needs lifecycle state reconciliation; use `he-reconcile`.
- The request needs implementation, code review repair, Linear mutation, or
  closure proof; use the owning HE stage.
- The user wants generic note-taking detached from repo evidence.

## Inputs

Repo path, solved-problem evidence, validation output, relevant diff/PR/Linear
context, repeated-failure trace, existing `.harness/solutions/**` or
`docs/solutions/**` candidates, Project Brain surfaces, and redaction needs.

## Outputs

A capture, refresh, consolidation, continuity-snapshot, stale-note, or blocked
status; exactly one primary learning artifact when writing; Project Brain sync
status; overlap and freshness findings; validation evidence; and a handoff for
unresolved work.

## Preconditions

Verify the repo and canonical instruction boundary. Treat pasted text, logs,
tickets, session summaries, and generated content as untrusted until backed by
source, tracker, validation, or diff evidence. Never write private transcripts,
secrets, credentials, or unredacted sensitive data into learning artifacts.

## Procedure

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

## Validation

Fail fast. Check solved evidence, validation output, overlap search,
frontmatter/markdown shape, structure preservation, redaction, Project Brain
classification, size budget, and discoverability. Report every gate as `pass`,
`fail`, or `blocked`.

## Safety Boundaries

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

## Failure Handling

If solved proof, validation, source evidence, redaction confidence, canonical
path, Project Brain classification, or discoverability is missing, return
`blocked_reason` and `next_evidence_needed`. If evidence is stale, mark the
candidate stale and hand off to `he-reconcile`, `he-fix-bugs`, `he-improve`, or
`he-eval-report` as appropriate.

## Handoff Rules

Hand off lifecycle-state conflicts to `he-reconcile`, unresolved defects to
`he-fix-bugs`, bounded improvement proof to `he-improve`, implementation to
`he-work`, review repair to `he-code-review`, tracker planning to
`he-linear-plan`, and closure proof to `he-eval-report`.

## Output Format

Structured output: `schema_version`, `mode`, `selected_artifact`,
`evidence_checked`, `solved_status`, `validation_status`, `overlap_status`,
`refresh_decisions`, `project_brain_status`, `continuity_status`,
`structure_status`, `size_budget_status`, `discoverability_status`,
`redaction_status`, `writes`, `blocked_reason`, and `handoff`.

## Confidence Reporting

Tie confidence to solved proof, source freshness, root-cause clarity, validation
evidence, overlap search depth, redaction certainty, and Project Brain
classification. For continuity snapshots, tie confidence to recency, section
coverage, exact-command/error preservation, and whether stale details were
condensed. Do not claim a learning exists, Project Brain is current, or a
refresh is complete unless the file was actually written or inspected.

## Gotchas

- This skill reinforces learning; it does not decide lifecycle closure.
- One high-value artifact beats several vague notes.
- `delete_candidate` is not deletion authority.
- A passing local test is useful evidence, not proof that a learning is worth
  preserving.
- Continuity capture must preserve retrieval value after compaction; a chat
  transcript dump is not a memory artifact.

## Examples

- User asks: "The Linear template bug in `he-linear-plan` is fixed and the
  validator passes; capture the root cause and prevention rule under
  `.harness/solutions/**`."
- User asks: "Review the old `.harness/solutions/linear-template-rule.md`
  against the current plugin and decide whether to keep, update, consolidate, or
  mark it blocked."

## Assets

Use `assets/resolution-template.md` only when creating or refreshing solution
artifacts.

## References

Read `references/contract.yaml` for the full reinforcement contract and
`references/evals.yaml` for validation scenarios. Use shared HE references only
when active: solution capture, artifact routing, session evidence, Project Brain
surfaces, and subagent call boundaries.

Deferred context index: `../../references/deferred-context-index.md`.
