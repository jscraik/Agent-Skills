---
name: he-plan
description: Plan execution work from specs, brainstorm outputs, bugs, or feature requests into an implementation-ready sequence. Use when the user needs the Harness Engineering planning stage before execution.
metadata:
  skill-type: team_automation
---

# he-plan Entry

Use when requirements, defects, specs, brainstorms, or Linear QA issues need an implementation-ready plan before `he-work`.

Context preservation: Do not remove important context for budget trimming; move it to references and index it in `Plugins/harness-engineering/references/deferred-context-index.md`.

## Philosophy

- Make plans executable, testable, and traceable.
- Resolve sequencing risk before coding starts.

## When to use

Use `he-plan` when the user needs execution sequencing, validation strategy, risk controls, and tracker traceability before implementation.

## Required inputs

- A Linear issue, spec, brainstorm, bug report, feature request, or existing plan to revise.
- Known constraints, source acceptance IDs, relevant repo paths, and required validation evidence.
- Branch or PR context when the work is already in flight.

## Deliverables

- A plan-mode decision: `fresh`, `resume`, or `deepen`.
- Stable plan phase IDs, acceptance IDs, dependencies, validation, rollback notes, and the first `he-work` handoff.
- For tracked work, Linear traceability frontmatter and a Linear/spec/plan/PR matrix.

## Core Contract

- Resolve the active Linear issue first for non-trivial tracked work; if none exists, stop and request or create one before planning.
- Plan from the most authoritative source: Linear issue, existing plan, requirements doc, spec, brainstorm, or direct request.
- Choose `fresh`, `resume`, or `deepen`; avoid duplicating a current plan.
- Route back to `he-deepen-spec` when a required caller-facing interface, domain term, or expected behavior is not specified.
- Sequence blockers first and mark independent Linear QA defects as parallelizable instead of blending them into one broad task.
- Produce stable phase IDs (`P` or `UP`) and acceptance IDs (`AC` or `UAC`) with validation intent, rollback notes, dependencies, and one actionable first handoff step.

## Procedure

1. Resolve the authoritative source and active Linear issue.
2. Choose `fresh`, `resume`, or `deepen`.
3. Decompose work into ordered, verifiable units with acceptance IDs and validation.
4. Add traceability and one next handoff step.

## Traceability

Written tracked plans must include Linear Work Item Contract frontmatter for issue, status, branch, PR or pending PR, and `traceability_required: true`.

Add a Linear/spec/plan/PR matrix mapping:

`Linear issue -> source acceptance IDs -> plan units -> acceptance IDs -> PR evidence`

Keep GitHub PRs as delivery evidence linked back to Linear; Linear remains the tracker of record.

## Validation

- Verify source requirements were not dropped.
- Verify tasks are executable and independently testable.
- Verify stable IDs and the traceability matrix connect source, plan, Linear, and PR evidence.
- For written tracked plans, run `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py <plan-path>` as a required gate.
- Stop at the first failed gate.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not implement code in the planning stage.
- Keep GitHub PRs as delivery evidence, not the tracker of record.

## Anti-patterns

- Producing abstract plans without executable task boundaries.
- Planning implementation around an unspecified interface.
- Treating Linear as background context instead of the required work item.

## Examples

- "Turn this approved spec into an implementation-ready plan."
- "Sequence these related Linear QA issues so blockers go first."

## Failure mode

If the planning source is too vague, the Linear issue cannot be resolved for tracked work, or acceptance IDs cannot be mapped, stop and ask for the missing source instead of fabricating a plan.

## Gotchas

- Do not implement code from this skill.
- Do not mutate Linear directly from the plan body; hand off to the installed Linear workflow when issue creation or update is requested.
- Keep GitHub PRs as delivery evidence, not the tracker of record.

## References

- Full guide: `Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-plan/SKILL.full.md`
- Plan artifact contract: `Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-plan/references/plan-artifacts.md`
- Verification-first planning: `Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-plan/references/verification-first.md`
- Production controls: `Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-plan/references/production-considerations.md`
- Subagent routing: `Plugins/harness-engineering/references/subagent-routing.md`
- Domain and QA routing: `Plugins/harness-engineering/references/domain-model-routing.md`, `Plugins/harness-engineering/references/qa-intake-routing.md`
