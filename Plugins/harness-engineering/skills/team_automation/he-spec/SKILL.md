---
name: he-spec
description: Write Harness Engineering specs before planning. Use when a feature, QA report, Linear issue, or UI source needs a clear WHAT contract.
metadata:
  skill-type: team_automation
---

# he-spec Entry

Use when the user needs a Harness Engineering specification artifact before planning or implementation.

Context preservation: Do not remove important context for budget trimming; move it to references and index it in `Plugins/harness-engineering/references/deferred-context-index.md`.

## Philosophy

- Clarify the behavior contract before planning or coding.
- Keep acceptance criteria concrete enough for downstream verification.

## When to use

Use `he-spec` when the user needs the WHAT-before-HOW contract for a feature, UI behavior, bug, QA report, or ambiguous implementation request.

## Required inputs

- A brainstorm, Linear issue, existing spec, QA report, UI source, feature description, or behavior gap.
- Known caller-facing interfaces, domain terms, source acceptance IDs, and relevant repo paths.
- Parent/child issue context and branch/PR metadata when the work is already tracked.

## Deliverables

- A spec-mode decision and implementation-grade behavior contract.
- Stable `SA` or `VAC` acceptance IDs, explicit non-goals, risks, observability notes, and planning-ready first slice.
- For tracked work, Linear issue frontmatter plus a Linear Acceptance Traceability table.

## Core Contract

- Specify the WHAT before `he-plan`; do not implement code here.
- Resolve the active Linear issue for non-trivial tracked work; stop and request or create one if it is missing.
- Ground the spec in the source artifact, QA report, Linear issue, UI source, feature description, and any `CONTEXT.md` terms that shape behavior.
- Detect caller-facing interfaces early: module, API, CLI, plugin, tool, service, data-access, or shared-helper boundaries.
- Name the selected contract, acceptance criteria, failure/recovery behavior, observability expectations, and planning-ready first slice.
- Treat `he-deepen-spec` as folded `he-spec` deepen mode. Load preserved deepen-spec context when an existing spec needs hardening or contract contradictions need resolution; route complete specs to `he-plan`.

## Procedure

1. Resolve source artifact, Linear issue, and domain terms.
2. Define expected behavior, non-goals, interface shape, and acceptance IDs.
3. Add Linear acceptance traceability and the first planning slice.

## Traceability

Tracked specs need Linear Work Item Contract frontmatter and a Linear Acceptance Traceability table mapping the issue to `SA` or `VAC` acceptance IDs, parent/child context when relevant, and the planning handoff.

## Validation

- Confirm required frontmatter and mode-specific sections exist.
- Confirm `SA` or `VAC` IDs are concrete enough for planning.
- Confirm tracked specs include Linear issue frontmatter and acceptance traceability.
- For written tracked specs, run `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py <spec-path>` as a required gate.
- Stop at the first failed gate.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not plan sequencing or implement code from this skill.
- Use Linear issues or comments for durable decisions.

## Anti-patterns

- Inventing undocumented behavior.
- Sending an unspecified interface to planning.
- Sending tracked work onward without Linear acceptance traceability.

## Examples

- "Turn this Linear issue into a spec before planning."
- "Specify this QA behavior gap with acceptance criteria."

## Failure mode

If required behavior, interface boundaries, or tracker context cannot be resolved, stop and ask for the missing source instead of inventing acceptance criteria.

## Gotchas

- Do not plan sequencing or implement code from this skill.
- Do not treat GitHub PRs as the tracker of record; use them as delivery evidence linked back to Linear.
- Route incomplete caller-facing contracts to `he-deepen-spec` before `he-plan`.

## References

- Full guide: `Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-spec/SKILL.full.md`
- Spec artifact contract: `Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-spec/references/spec-artifacts.md`
- Spec mode rules: `Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-spec/references/spec-modes.md`
- Folded `he-deepen-spec` context: `Plugins/harness-engineering/references/folded-skill-context.md`
- Subagent routing: `Plugins/harness-engineering/references/subagent-routing.md`
- Domain and QA routing: `Plugins/harness-engineering/references/domain-model-routing.md`, `Plugins/harness-engineering/references/qa-intake-routing.md`
