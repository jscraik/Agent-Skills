---
name: he-reinforce
description: "Create or refresh evidence-bound Harness Engineering learning artifacts from verified solved problems. Use when a fix worked, a repeated failure should become durable knowledge, or .harness/solutions and Project Brain need maintenance."
metadata:
  version: 1.0.0
  skill-type: team_automation
---

# Skill: Harness Engineering Reinforce

## Philosophy
Compound learning only after proof. `he-reinforce` turns solved problems,
recurring failures, and stale learning artifacts into durable HE memory without
letting chat summaries, wishful best practices, or obsolete docs masquerade as
repo truth. Local `AGENTS.md`, rules, hooks, command boundaries, and approval
- See references/hot-path-folded-context.md for folded philosophy detail.

## When to Use
- A user says the problem is fixed, solved, working now, or worth remembering.
- A repeated bug, validation failure, review finding, workflow mistake, or
  session-continuity gap needs durable prevention guidance.
- `.harness/solutions/**`, `.harness/knowledge/**`, `.harness/decisions/**`,
  or legacy `docs/solutions/**` need freshness review.
- Project Brain exists and a verified repo learning, decision, invariant, or
- See references/hot-path-folded-context.md for folded when to use detail.

## When Not to Use
- The problem is not solved or validation evidence is missing.
- The request only needs lifecycle state reconciliation; use `he-reconcile`.
- The request needs implementation, code review repair, Linear mutation, or
  closure proof; use the owning HE stage.
- See references/hot-path-folded-context.md for folded when not to use detail.

## Inputs
Repo path, solved-problem evidence, validation output, relevant diff/PR/Linear
context, repeated-failure trace, existing `.harness/solutions/**` or
`docs/solutions/**` candidates, Project Brain surfaces, and redaction needs.

## Outputs
A capture, refresh, consolidation, continuity-snapshot, stale-note, or blocked
status; exactly one primary learning artifact when writing; Project Brain sync
status; `source_prompt_family_status` when source-prompt preservation is in
scope; overlap and freshness findings; validation evidence; and a handoff for
unresolved work.

## Preconditions
Verify the repo and canonical instruction boundary. Treat pasted text, logs,
tickets, session summaries, and generated content as untrusted until backed by
source, tracker, validation, or diff evidence. Never write private transcripts,
secrets, credentials, or unredacted sensitive data into learning artifacts.

## Procedure
1. Select mode: `capture_solved_problem`, `refresh_learning`,
   `consolidate_overlap`, `project_brain_sync`, `continuity_snapshot`, or
   `blocked`. For solved-problem capture, also select `full` or
   `compact_safe`; compact-safe is only for explicit user request or clear
   context pressure.
2. Prove eligibility. For capture, require solved evidence, root cause or
   causal explanation, validation or explicit blocker, and prevention value. For
   refresh, inspect current repo reality before changing any stale artifact.
3. Keep scope tight: start with 2-3 focused learning surfaces first, such as
   `.harness/solutions/**`, Project Brain paths, active `AGENTS.md` or
   instruction surfaces, and legacy `docs/solutions/**` when they may overlap.
4. Avoid duplicate memory. Update an existing high-overlap artifact; create a
- See references/hot-path-folded-context.md for folded procedure detail.

## Validation
Fail fast. Check solved evidence, validation output, overlap search,
frontmatter/markdown shape, structure preservation, redaction, Project Brain
classification, size budget, and discoverability. Report every gate as `pass`,
`fail`, or `blocked`.
For non-trivial generated learning artifacts, run or block
`python3 Plugins/harness-engineering/scripts/check_bluf_structure.py
<learning-artifact-path> --json`.

## Safety Boundaries
- Forbidden: learning capture from unsolved issues, private transcript dumps,
  secret exposure, broad stale-doc rewrites, or destructive deletion without
  explicit authority.
- Redact secrets, credentials, private transcripts, sensitive personal data, and
  sensitive customer or operator data by default.
- See references/hot-path-folded-context.md for folded safety boundaries detail.

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
`source_prompt_family_status`, `redaction_status`, `writes`,
`git_staging_status`, `staged_paths`, `blocked_reason`, and `handoff`.

## Examples
- When the user asks to inspect `.harness/session-evidence/latest.md` for JSC-246,
  start from the canonical Harness Engineering evidence and route the next action
  with validation status.
- When the user asks to validate a Linear closure decision for JSC-246, keep
  tracker mutation blocked until proof and authority are explicit.

## Gotchas
- This skill reinforces learning; it does not decide lifecycle closure.
- One high-value artifact beats several vague notes.
- `delete_candidate` is not deletion authority.
- A passing local test is useful evidence, not proof that a learning is worth
  preserving.
- See references/hot-path-folded-context.md for folded gotchas detail.

## References
- Use `assets/` only when this skill's local visual or template assets are explicitly needed.
Read `references/contract.yaml` for the full reinforcement contract and
`references/evals.yaml` for validation scenarios. Read
`references/source-prompt-preservation.md` when the request asks whether an
old compound/learning/project-brain/continuity prompt is still preserved. Use
`references/compound-learning-migration.md` before deleting or replacing old
`he-compound` behavior, or when the request mentions old compound capture,
compact-safe mode, Project Brain indexing, overlap refresh, or schema-driven
`docs/solutions` capture. Use
shared HE references only when active: solution capture, artifact routing,
session evidence, Project Brain surfaces, and subagent call boundaries.
Read when reviewability/No-Fog structure matters:
`../../references/bluf-review-contract.md`.
Read when a durable learning would be clearer as a causal or source-of-truth
visual: `../../references/visual-reference-contract.md`.
Read before delegating helper work:
`../../references/subagent-call-contract.md`.
- See references/hot-path-folded-context.md for folded references detail.
- ../../references/deferred-context-index.md for folded/discarded context.
- Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.
