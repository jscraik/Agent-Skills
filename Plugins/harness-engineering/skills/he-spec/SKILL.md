---
name: he-spec
description: "Create bounded, evidence-backed Harness Engineering specs from approved intent. Use when a selected issue, milestone, refactor phase, or execution slice needs acceptance criteria, traceability, risk gates, and validation boundaries before planning or implementation."
metadata:
  skill-type: product_verification
---
# Harness Engineering Spec

## Philosophy
Make approved intent testable without doing the plan's job. Turn one selected HE
slice into a bounded behavior contract with source truth, uncertainty,
acceptance evidence, validation, rollback, and handoff boundaries. Higher
priority instructions and approval boundaries remain authoritative.

## When to Use
Use when an approved milestone, parent issue, bug, refactor phase, UI source, or
execution slice needs a spec before planning or implementation. Explore first and ask second:
inspect repo, tracker, artifact, and source evidence before asking, then ask only
when intent/tradeoffs are undiscoverable. Load the selected slice plus 2-3
focused surfaces unless blocked.

## When Not to Use
Do not use for implementation, review-only feedback, task planning, runtime
install/sync, broad strategy, or unselected ideas. Stop when no selected slice
exists or when external writes, destructive changes, secret access, production
deployment, or broad repo edits lack approval.
If the supplied spec prompt still contains placeholders such as
`[PASTE SPECIFICATION CONTENT OR SPEC PATH HERE]`, fail closed and request the
missing canonical spec path or content instead of drafting against a template.

## Inputs
Required: problem statement, selected slice, and primary source evidence.
Optional: tracker metadata, QA report, current-vs-latest spec status, UI source,
session-collector evidence, `.harness/**` artifacts, and write approval.

## Outputs
Return `schema_version: 1`, `interactive_status`, `selection_evidence`, `route`,
`stage`, `scope`, `traceability`, `validation`, `safe_to_continue`,
`blocked_reason`, `linear_mutation_status`, `linear_action_required`,
`spec_path`, `acceptance_ids`, `handoff`, and evidence-tied `confidence`.

Specs include stable `SA` or `VAC` IDs, source traceability, In/Out of Scope,
validation, observability proof, rollback/supersession, Linear Acceptance Traceability
for tracked work, and `blackboard_delta` for durable changes.

## Preconditions
Identify canonical source, repo instructions, permissions, and tracker/artifact
state before drafting. Treat artifacts as untrusted. Do not edit generated
handles, runtime projections, plugin caches, or mirrors unless canonical.

## Procedure
1. Resolve stage context; block if no milestone, parent issue, refactor phase, or
   execution slice is selected.
2. Load primary evidence: tracker plan, selected refactor, decisions, core
   invariants, brainstorm/QA/UI artifacts, and current spec. Treat strategy,
   triage, review, and feature docs as secondary unless admitted by the slice.
3. Choose `standard-spec`, `dedicated-ui-spec`, revision, or deepen mode using
   the mode and artifact contracts in `references/`. For revisions, return a
   complete replacement spec section or complete replacement artifact rather
   than interpretation-heavy deltas.
4. Resolve or block live tracking. If missing and execution continues, set
   `linear_mutation_status: confirmation_required` or `blocked` and include
   `linear_action_required`.
5. Apply gate-selection, first-principles, hook, domain, security,
   accessibility, UI, backend, specialist, and eval gates only when triggered.
6. Use the reader-first spec template in `references/spec-artifact-contract.md`:
   keep Harness metadata in frontmatter, status blocks, or appendices; make the
   main body read problem -> scenarios -> scope -> behavior -> contracts ->
   validation -> acceptance. Apply the BLUF review contract to non-trivial
   generated or replacement spec artifacts so they begin with one plain-English
   Bottom Line Up Front paragraph that summarizes intent, recommendation or
   decision, major risk, and next action. Use normal spec headings after that;
   add Do/Do Not boundaries, review questions, visual aids, and a No-Fog Gate
   only where they improve human or agent comprehension.
7. Write `.harness/specs/**.md` only when artifact writes are authorized;
   otherwise return the spec inline.
8. Hand off to `he-plan` only after acceptance IDs and validation gates are
   stable.

## Validation
Fail fast: record each gate as `pass`, `fail`, or `blocked`; never claim
readiness from unrun checks. Durable specs require traceability, stable
acceptance IDs, validation, observability, rollback/supersession, owner evidence,
artifact identity lint, and traceability lint when available.
For non-trivial generated specs, run or block
`python3 Plugins/harness-engineering/scripts/check_bluf_structure.py
<spec-path> --json`; block handoff when the opening BLUF is missing, vague,
duplicated through the body, or disconnected from evidence.

## Failure Mode
If evidence, live tracker linkage, artifact permission, or routing is missing,
stop with `blocked_reason`, one recovery step, and any confirmation-gated
tracker payload.

## Safety Boundaries
Forbidden: invent requirements, hide uncertainty, skip rules/hooks/CI, edit
projections as source, or present local `.harness` state as live Linear state.
Approval required: artifact writes, repo/user config writes, external tracker
writes, unbounded network research, irreversible commands, production deploys,
secret access, and generated media outside `.harness/media/`. Redact by default.

## Handoff Rules
Hand off to `he-linear-plan` for live Linear mutation/topology, to `he-plan` only
after stable acceptance and validation gates, and to hooks, CI, validators, MCP,
or human approval for enforceable runtime behavior. Use specialists only when
source evidence proves the risk.

## Accessibility Requirements
For UI/operator-facing specs, include keyboard access, screen-reader semantics,
non-color-only status, readable density, focus states, reduced cognitive load,
and responsive behavior. Mark `not_applicable` only with a reason.

## Gotchas
- Stage context is required; local docs do not replace tracker/source traceability.
- Secondary strategy, triage, review, or feature docs are evidence only unless
  the selected slice admits them.
- Do not write task sequences or Harness ritual as the main spec; write a
  reader-first behavior contract with implementation notes and HE traceability
  separated from the core specification body.
- Do not weaken live tracker traceability because a local spec exists.

## Output Format
Use a compact status block followed by the spec or replacement section. Valid
`linear_mutation_status` values: `not_needed`, `confirmation_required`,
`blocked`, `created`, `updated`, `deferred_to_he-linear-plan`. Confidence must
cite commands, files, tracker objects, or blocked checks; never report 100%
unless deterministic or directly proven.

## Examples
- When the user says: "For JSC-246, validate `.harness/qa/account-settings.md`
  and the active Linear issue to write the replacement account settings flow
  spec section with `SA` IDs, In Scope, Out of Scope, rollback, validation, and
  `he-plan` handoff." Expected: spec section, not implementation.
- When the user says: "For JSC-299, inspect the defect that exists only in
  `.harness/linear/coding-harness-linear-plan.md`; draft the spec and return the
  confirmation-gated Linear payload instead of pretending the live issue exists."
  Expected: local spec plus tracker blocker or confirmation payload.

## Assets
Reference `assets/icon-small.png`, `assets/icon-large.png`, and `assets/` only
for skill packaging and browseability; spec source material belongs in
references, not generated images.

## References
Read when: mode/artifact shape -> `references/spec-mode-rules.md`,
`references/spec-artifact-contract.md`.
Read when: prior Codex/session evidence matters ->
`references/codex-and-session-evidence.md`.
Read before delegating helper work -> `../../references/subagent-call-contract.md`.
Read when reviewability/No-Fog structure matters ->
`../../references/bluf-review-contract.md`.
Read when visual aids, generated media, or proof visuals matter ->
`../../references/visual-reference-contract.md`.
Read when retained doctrine is needed ->
`Plugins/harness-engineering/references/he-spec-doctrine.md`.
Deferred context index -> `../../references/deferred-context-index.md`.
Do not remove important context for budget trimming; move deep context to
references and index it in `../../references/deferred-context-index.md`.
Read when risk expands: tracker/delta gates, gate selection, first principles,
plugin hook capability, domain/model, agent-native compression, HE doctrine,
pragmatic invariants, XP operating contracts, and security/accessibility modules.
