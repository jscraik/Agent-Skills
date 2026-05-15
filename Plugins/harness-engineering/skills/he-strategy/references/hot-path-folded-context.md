# Hot-Path Folded Context

## Purpose
Preserve detailed context folded out of SKILL.md so the active he-strategy entrypoint stays below the hot-path soft budget without losing usable guidance.

## 2026-05-15 Soft-Warning Cleanup

Disposition:
- moved-to-reference: bulky examples, extended output fields, repeated evidence detail, and long procedure tails.
- superseded: repeated headings whose active entrypoint now points to shared contracts.
- intentionally-discarded: none in this file; prompt rot is tracked in shared folded context when removed.

## Folded Philosophy

Strategy artifacts are cognition compression, not execution permission. Turn
verified repo evidence and prior `.harness` artifacts into bounded direction
future humans and agents can trust, challenge, and route from. Local
`AGENTS.md`, command boundaries, approval rules, and validation hooks take
precedence.

## Folded Procedure

1. Select exactly one mode unless the user explicitly requests the full repo
   cognition pipeline; ask once only when ambiguity changes artifact sequence or
   authority.
2. Load the matching mode contract from `references/strategy-output-contract.md`;
   load deeper references only when their read-when trigger applies.
3. Start with 2-3 focused evidence surfaces; widen only when conclusions cannot
   be proven from the selected set.
4. Separate facts, interpretations, assumptions, confidence, authority limits,
   and validation status. Mark sampled, stale, or narrow evidence as authority
   limited.
5. Keep strategy advisory unless admitted by `.harness/linear/**`,
   `.harness/reframes/**`, `.harness/specs/**`, or `.harness/plan/**`.
6. Compress conclusions to decisions that change routing, deletion, investment,
   anti-drift behavior, or the smallest feedback-producing next slice.
7. Validate the artifact against the selected contract and record each gate as
   `pass`, `fail`, or `blocked`.

## Folded Handoff Rules

- Hand off to execution skills only when strategy exposes an admitted execution
  slice.
- Hand off to humans for ADRs, core invariant changes, strategic deletion, or
  unresolved instruction conflicts.
- Use hooks, CI, MCP tools, or validators for enforcement; this skill does not
  replace those gates.

## Folded Accessibility Requirements

Use plain Markdown, short sections, descriptive links, and non-color-only tables.

## Folded Examples

- When the user asks: "Inspect the current agent-skills checkout and create
  `.harness/features/2026-05-13-agent-skills-intent.md` from live `Plugins/`,
  `Skills/`, `.skillsets/`, validator, and projection-sync evidence."
- When the user asks: "Read `.harness/review/agent-skills-architecture-review.md`
  and `.harness/triage/agent-skills-triage.md`; compress them into strategy or
  return `Do Not Create` for low-value governance."
- When the user asks: "Compare `$he-strategy` against my original repo cognition
  prompt and report covered requirements, missing requirements, evidence depth,
  not-inspected surfaces, and downstream confidence."

## Folded References

- Mode paths, guardrails, output fields -> `references/strategy-output-contract.md`
- Full intent + architecture review + triage pipeline -> `references/repo-cognition-pipeline.md`
- Default architecture/refactoring lenses without fresh attachments -> `references/architecture-lens-canon.md`
- Source-prompt equivalence -> `references/source-prompt-preservation.md`
- Package contract and evals -> `references/contract.yaml`, `references/evals.yaml`
- Read before delegation -> `../../references/subagent-call-contract.md`
- Shared HE routing and BLUF/visual/subagent/first-principles/XP contracts ->
  `../../references/deferred-context-index.md`
- Pragmatic Programmer review lens ->
  `../../references/pragmatic-programmer-review-contract.md`

Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.
move deep context behind a clear reference route.
