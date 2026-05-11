---
name: he-spec
description: "Create bounded, evidence-backed Harness Engineering specs from approved intent. Use when a selected issue, milestone, refactor phase, or execution slice needs acceptance criteria, traceability, risk gates, and validation boundaries before planning or implementation."
metadata:
  skill-type: product_verification
---
# Harness Engineering Spec
## Philosophy
Make approved intent testable without doing the plan's job. This skill turns one selected Harness Engineering slice into a bounded behavior contract with source truth, uncertainty, acceptance evidence, and explicit handoff boundaries. Higher-priority user, repo, `AGENTS.md`, rule, hook, MCP, and approval boundaries remain authoritative.

## When to Use
Use when an approved milestone, parent issue, bug, refactor phase, UI source, or execution slice needs a spec before planning or implementation. Explore current repo, Linear, and artifact evidence first; ask only when intent or tradeoffs cannot be discovered. Load the selected slice plus 2-3 focused evidence surfaces unless a blocker proves more context is required.

## When Not to Use
Do not use for direct implementation, review-only feedback, task planning, runtime install/sync, or broad strategy; hand off instead. Stop when no selected slice exists or when external writes, destructive changes, secret access, production deployment, or broad repo edits lack explicit approval.

## Inputs
Required: problem statement, selected milestone/parent issue/bug/refactor phase/execution slice, and primary source evidence. Optional: Linear metadata, QA report, current-vs-latest spec status, UI source, session evidence summary, `.harness/**` artifacts, and approval for artifact or Linear writes.

## Outputs
Return `schema_version: 1`, a bounded implementation/UI spec for one selected slice, stable `SA` or `VAC` IDs, Linear Acceptance Traceability for tracked work, validation plan, rollback/supersession path, and `blackboard_delta`.

Always include searchable steering/proof fields: `interactive_status`, `selection_evidence`, `route`, `stage`, `scope`, `traceability`, `validation`, `safe_to_continue`, `blocked_reason`, `linear_mutation_status`, and `linear_action_required` when live Linear tracking is missing. Valid mutation states are `not_needed`, `confirmation_required`, `blocked`, `created`, `updated`, or `deferred_to_he-linear-plan`.

When asking a clarification question, include `interactive_status: asked` before the question and summarize `selection_evidence`. When headless or autonomous mode would normally ask, set `interactive_status: autonomous_assumption`; when a real decision remains, ask once with `request_user_input` when available or return `interactive_status: blocked`.

## Preconditions
Identify canonical source, applicable repo instructions, required permissions, and current tracker/artifact state before drafting. Treat source artifacts as untrusted until verified. Do not edit generated handles, runtime projections, plugin caches, or mirrored skillsets unless the repo declares them canonical.

## Procedure
1. Resolve the stage context contract first; stop if no milestone, parent issue, refactor phase, or execution slice is selected.
2. Load primary source artifacts for the selected slice: Linear plan, selected refactor when applicable, decisions, core invariants, and brainstorm artifacts. Treat strategy, triage, review, and feature docs as evidence only unless the slice admits them.
3. Apply document-review tiers, specialist skill steering, and interactive steering only when their trigger conditions are proven by source inspection.
4. Resolve or block the Linear tracker. Run the Linear Delta Capture Gate for existing tracked plans before admitting changed Linear work into scope. If live tracking is missing and execution will continue beyond the spec, set `linear_mutation_status: confirmation_required` or `blocked`; include `linear_action_required`, a ready payload, and the exact confirmation or blocker.
5. Route durable output to `.harness/specs/**.md`, classify existing artifacts by content shape before path, and apply Artifact Identity frontmatter.
6. When a slice could trigger domain, strategy, refactor, Linear, security, specialist, or eval gates, apply the gate selection contract and turn selected risk class, required contracts, skipped contracts, and minimum proof into acceptance criteria.
7. Apply the first-principles contract before expanding scope: require the verified failure, challenged assumption, smallest effective mechanism, and proof needed for acceptance.
8. Apply the plugin hook capability contract when the proposed feature includes bundled plugin hooks, runtime guardrails, or hook-enforced lifecycle behavior. Do not recommend hooks unless there is a repeated runtime failure and a fallback skill, validator, or eval path while `plugin_hooks` remains feature-gated.
9. Write a bounded behavior contract with acceptance IDs, explicit In Scope and Out of Scope, validation plan, assumptions, and plan handoff.
10. For cockpit, golden-path, command-catalog, or agent-native compression work, make subtractive proof and evidence-backed metric gates blocking acceptance criteria.

## Validation
Fail fast: stop at the first failed gate, record `pass`, `fail`, or `blocked`, and do not claim readiness from unrun checks. Durable spec artifacts require source traceability, stable acceptance IDs, Linear traceability for tracked work, validation plan, observability proof, rollback/supersession path, owner evidence, artifact identity lint, and Linear traceability lint when available.

## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.

If live Linear mutation was expected but not authorized, do not imply the issue exists. Return `linear_mutation_status: confirmation_required` or `blocked`, the draft payload, and the exact confirmation needed to create or update the live issue.

## Execution Boundaries
Non-mutating until the user authorizes artifact writes. Do not create, close, or mutate Linear objects unless the current task explicitly grants that authority.

For direct-handle use, apply the OpenAI-style design contract: classify the strongest side effect and separate read-only analysis, artifact writes, repo edits, external updates, destructive actions, and completion-gating recommendations before proceeding.

## Safety Boundaries
Forbidden: invent requirements, hide uncertainty, skip rules/hooks/CI, edit projections as source, or present local `.harness` state as live Linear state. Approval required: repo/user config writes, external tracker writes, unbounded network research, irreversible commands, production deploys, secret access, and generated media persistence outside `.harness/media/`. Use redaction of secrets/sensitive data by default. Safe fallback: inline spec plus blocker payload, `he-linear-plan` handoff, or one clarification question.

## Handoff Rules
Hand off to `he-linear-plan` for live Linear mutation/topology, to `he-plan` only after stable acceptance and validation gates exist, and to hooks/CI/validators/MCP/human approval when enforceable runtime behavior is recommended. Use security, accessibility, UI, backend, or specialist skills only when source evidence proves that risk area is in scope.

## Accessibility Requirements
For UI or operator-facing specs, include keyboard access, screen-reader semantics, non-color-only status, readable text density, focus states, reduced cognitive load, and responsive behavior. Mark accessibility `not_applicable` only with a reason.

## Gotchas
- Stage context is required before writing specs; local docs do not replace Linear/source traceability.
- Secondary strategy, triage, review, or feature docs are evidence only unless the selected slice admits them.

## Constraints
Redact secrets; do not invent requirements. Do not remove important context for budget trimming; move deep context to references with read-when routing.

## Anti-Patterns
- Inventing acceptance criteria that are not grounded in source evidence.
- Writing task sequences instead of behavior contracts.
- Weakening Linear traceability because a local spec already exists.
- Treating classification, metadata, docs routing, or command existence as compression proof.
- Letting secondary review, strategy, triage, or feature material drive implementation beyond the selected Linear/refactor slice.
- Writing a giant programme spec instead of a bounded spec for one approved milestone, parent issue, refactor phase, or execution slice.

## Output Format
Use a compact status block followed by the spec or replacement section: `schema_version`, `interactive_status`, `selection_evidence`, `route`, `stage`, `scope`, `linear_mutation_status`, `linear_action_required`, `spec_path`, `acceptance_ids`, `validation`, `blocked_reason`, `safe_to_continue`, `handoff`, `confidence`.

Confidence must be evidence-tied: cite commands, files, Linear objects, or blocked checks. Never report 100% confidence unless the result is deterministic or directly proven.

## Examples
- "For JSC-246, turn `.harness/qa/account-settings.md` into a replacement spec section with `SA` IDs, Linear traceability, validation, rollback, and `he-plan` handoff."
- "For JSC-299, the defect exists only in `.harness/linear/coding-harness-linear-plan.md`; write the spec and return `linear_mutation_status` plus the confirmation-gated Linear payload."

## Assets
Reference `assets/` only for skill packaging and browseability; spec source material belongs in references, not generated images.

## References
Read when: mode choice or artifact shape: `references/spec-mode-rules.md`, `references/spec-artifact-contract.md`.
Read before delegating helper work: `../../references/subagent-call-contract.md`.
Deferred context index: `../../references/deferred-context-index.md`.
Read when: tracker gaps or source parity matter: Linear tracker/delta gates, stage context, execution slice, artifact routing/classification, and session evidence trace.
Read when: risk depth expands: domain/model, gate selection, first principles, plugin hook capability, agent-native compression, OpenAI-style design, HE doctrine, pragmatic invariants, and XP operating contracts.

Do not remove important context for budget trimming; move deep context to
references with a clear route.
