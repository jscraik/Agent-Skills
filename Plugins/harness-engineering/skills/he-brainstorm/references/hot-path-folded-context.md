# Hot-Path Folded Context

## Purpose
Preserve detailed context folded out of SKILL.md so the active he-brainstorm entrypoint stays below the hot-path soft budget without losing usable guidance.

## 2026-05-15 Soft-Warning Cleanup

Disposition:
- moved-to-reference: bulky examples, extended output fields, repeated evidence detail, and long procedure tails.
- superseded: repeated headings whose active entrypoint now points to shared contracts.
- intentionally-discarded: none in this file; prompt rot is tracked in shared folded context when removed.

## Folded Procedure

1. Explore first and require an identifiable subject before dispatching ideation
   or writing artifacts.
2. If cited evidence cannot be read, still return the brainstorming frame with
   `validation: blocked`, `blocked_reason`, explicitly labeled assumptions, and
   the smallest safe recovery step; do not replace the output with a generic
   request for pasted content.
3. Resolve only the stage context fields needed for tracker, artifact route,
   evidence freshness, and coding-harness handoff.
4. Separate stated facts, interpretations, guesses, and out-of-scope work.
5. Keep scope tight: start with 2-3 focused surfaces and widen only when the
   ambiguity cannot be resolved from the initial evidence.
6. Route durable brainstorm artifacts to `.harness/brainstorm/**.md`; route
   explicit folded `he-ideate` artifacts to `.harness/ideate/**.md`.
7. Resolve or block the Linear tracker before durable handoff for tracked work.
8. In folded `he-ideate` mode, use `references/ideation-mode.md` for candidate
   generation, critique, coverage recovery, survivor selection, web research,
   and specialist-skill steering.
9. Apply the first-principles contract before survivor selection: prefer ideas
   that prevent verified HE failures or reduce ambiguity; defer copied patterns
   that lack HE-specific failure evidence.
10. Apply the BLUF review contract to non-trivial durable brainstorm or ideation
   artifacts so the selected survivor, uncertainty, risk consequence, and next
   HE stage are visible before option detail.
11. Ask before survivor selection when the chosen survivor would shape downstream
   spec, plan, Linear work, or implementation scope.

## Folded Failure Handling

If required evidence, Linear linkage, next-stage routing, artifact destination,
tool availability, or authority is missing, stop with the blocker and smallest
recovery step. In headless mode, record assumptions as assumptions; keep them out
of requirements and key decisions. When interaction is available and one answer
would unblock survivor selection, ask once; otherwise set
`autonomous_assumption` or `selection_evidence` so the next stage can audit the
choice.

## Folded Confidence Reporting

Tie confidence to evidence freshness, verified sources, domain-term stability,
survivor warrant strength, validation status, and remaining user choices. Do not
claim runtime availability, Linear status, web research, or artifact writes
without direct evidence.

## Folded Examples

- "Inspect JSC-246 and the QA notes in `Docs/qa/account-settings.md`; separate
  stated facts, inferred behavior, and out-of-scope work before Linear."
- "Compare the tracker-only option with the Project Brain option, and tell me
  which one should survive before we spec it."
- "Analyze whether the JSC-310 data-sync ambiguity is spec-ready; if not, hold
  the handoff until options are clear."

## Folded Assets

Reference `assets/` only for skill packaging and browseability; workflow source
of truth stays in this SKILL and references.

## Folded References

Read when detailed flow is needed: `references/brainstorm-workflow-details.md`.
Read when folded `he-ideate` mode is active: `references/ideation-mode.md`.
Read before writing durable requirements: `references/requirements-artifact-guide.md`.
Read before interactive questioning: `references/discovery-interview.md`.
Read before final handoff review: `references/document-review-pass.md`.
Read when visual output may help: `references/visual-communication.md`,
`../../references/visual-reference-contract.md`.
Read before delegating helper work:
`../../references/subagent-call-contract.md`.
Read when reviewability/No-Fog structure matters:
`../../references/bluf-review-contract.md`.
Use shared HE references only when their topic is active: subagent policy, stage
context, interactive steering, specialist steering, domain context/model,
OpenAI-style design, topic coverage, first principles, deferred context, Linear
tracker gate, coding-harness bridge, artifact routing/classification, pragmatic
invariants, and XP operating contract.

Deferred context index: `../../references/deferred-context-index.md`.
Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.
