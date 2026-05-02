---
name: he-work
description: "Use when implementing approved Harness Engineering plans, todo lists, or tiny low-risk specs that need traceable slices, validation, Linear, and PR handoff."
metadata:
  skill-type: team_automation
---

# he-work Entry

Use when the user expects implementation from an approved plan, todo list, or tiny low-risk spec. Keep Harness Engineering naming consistent.

Context preservation: Do not remove important context for budget trimming; move it to references and index it in `Plugins/harness-engineering/references/deferred-context-index.md`.

## Philosophy

Ship verified slices. Keep code, artifacts, Linear, branch/PR, and validation evidence aligned.

## When to use

Use for approved implementation work. Route fuzzy ideas to `he-brainstorm`, raw plans to `he-plan`, and medium/high-risk raw specs to planning first.

## Inputs

Approved plan/todo/small spec, Linear key when tracked, acceptance IDs, invariants, non-goals, validation gates, branch/PR context, and execution notes.

## Outputs

Implemented slices, synced task state, validation evidence, Linear result or blocker, PR handoff, drift notes, and `schema_version: 1` for structured status when requested.

## Contract

- Pick the lane before editing: `plan-led`, `todo-led`, folded `he-tdd`, or narrow `small-spec-direct`.
- Read the governing artifact fully; extract IDs, Linear issue, branch/PR, invariants, non-goals, validation gates, execution notes, and scope.
- Confirm the artifact is current active truth, not merely the newest dated file.
- Resolve Linear for non-trivial tracked work; stop if required tracker context is missing.
- `update_plan` is live checklist only. Durable truth remains the plan/spec/todo.
- Preserve dirty worktrees and stage only approved-slice files.
- Stop on contract drift, hidden scope, domain drift, failed gates, or missing traceability.

If the thread is still in Codex Plan Mode, do not mutate files. Inspect repo truth only and explain the execution plan.

## Procedure

1. Explore first, ask second: inspect repo guidance, artifact links, branch/PR/Linear state, and validation commands.
2. Build a short live checklist from implementation units or todo IDs.
3. Ship one verified slice at a time; honor `test-first`, `characterization-first`, or `external-delegate` notes.
4. Broaden validation as risk grows, then run the required review tier.
5. Update durable artifacts only for real drift or required final status.

Use external delegation only for bounded implementation units explicitly marked for it. Parent keeps research, contract updates, git, validation, review, and handoff.

## Validation

Validate each slice before marking it complete. Stop at the first failed gate; do not proceed until it is fixed or reported as a blocker. For tracked artifacts, run `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py <artifact-path>`.

## Handoff

Final handoff records current active state, changed areas, completed IDs, validation outcomes, Linear result or blocker, spec/plan paths, branch/PR state, drift updates, rollback or monitoring notes, and UI screenshots when relevant.

Default meaningful code changes to `he-code-review mode:autofix` before handoff unless the slice clearly qualifies for inline self-review.

## Constraints

Redact secrets. Preserve dirty worktrees. Do not expand approved scope, mutate during Codex Plan Mode, or use unbounded delegation.

## Anti-patterns

- Expand scope beyond approved IDs.
- Mark tasks complete before validation exists.
- Ask for facts repo inspection can answer.
- Treat prototype HTML as production unless the real stack is static HTML/CSS/JS.
- Accept delegate output without parent diff review and validation.
- Dump secrets or continue past validation/security blockers.

## Examples

- User says: "Please use $he-work on Docs/plans/2026-05-02-jsc-246-linear-routing.md; implement U1 and U2, validate the traceability lint, and leave JSC-246 ready for PR handoff."
- User says: "Can you work through Docs/todos/jsc-251-review-cleanup.md in verified slices, preserve my unrelated edits, and only mark tasks complete after validation passes?"
- User says: "Inspect the JSC-263 plan and use delegate mode only for units tagged Execution target: external-delegate; review the diff yourself before handoff."
- User says: "Build the account settings UI slice with screenshot evidence, completed VAC IDs, Linear comment result, and rollback notes."

## References

- Work execution contract: `Plugins/harness-engineering/skills/team_automation/he-work/references/work-execution-contract.md`
- Codex execution lessons: `Plugins/harness-engineering/skills/team_automation/he-work/references/codex-execution-lessons.md`
- Handoff and shipping: `Plugins/harness-engineering/skills/team_automation/he-work/references/handoff-and-shipping.md`
- Execution modes: `Plugins/harness-engineering/skills/team_automation/he-work/references/execution-modes.md`
- Approval flow: `repo:Plugins/harness-engineering/skills/shared/references/approval-flow.md`
- Folded `he-tdd` context: `Plugins/harness-engineering/references/folded-skill-context.md`
- Session evidence contract: `Plugins/harness-engineering/references/session-evidence-contract.md`
- Subagent call contract: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Skill assets: `Plugins/harness-engineering/skills/team_automation/he-work/assets/icon-small.png`, `Plugins/harness-engineering/skills/team_automation/he-work/assets/icon-large.png`
