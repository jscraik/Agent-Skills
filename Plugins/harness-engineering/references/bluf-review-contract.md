# BLUF Review Contract

Read when: writing, reviewing, or validating durable HE specs, plans, refactor
programs, Linear plans, eval reports, review artifacts, strategy artifacts,
reconcile reports, or other operator-facing `.harness/**` artifacts where
scanability matters.

## Purpose

BLUF is the review interface for HE artifacts, not a new lifecycle stage. It
makes the point visible before the reasoning so Jamie can scan decisions without
decoding agent prose.

## When to Apply

Apply the full contract to non-trivial durable artifacts, especially:

- `.harness/specs/**`
- `.harness/plan/**`
- `.harness/evals/**`
- `.harness/review/**`
- `.harness/refactors/**`
- `.harness/linear/**`
- `.harness/strategy/**`, `.harness/decisions/**`, and `.harness/core/**` when
  they drive later work

Use the compact form for small replacement sections, tactical notes, or review
findings.

Do not apply the full contract to terse status messages, inline code-review
findings, command output, raw evidence logs, or artifacts where the local
template is stricter.

## Document Scan Surface

Non-trivial specs, plans, and reports should start with:

### Command Summary

- `BLUF:` one plain-English sentence saying build, block, revise, split, close,
  do not close, or hand off.
- `Decision Needed:` approve, block, revise, split, threat-model, plan, work,
  Linear, or none.
- `Top Risks:` one to three plain-English risks with consequences.
- `Next Action:` exact next action or blocked recovery step.

### BLUF-Only Summary

List the major section BLUF lines in order. This must be extracted from the
section BLUFs, not rewritten as a second document.

## Section Pattern

Major sections use:

- `BLUF` with a line that starts `BLUF:`
- `Reasoning`
- `Examples` when examples reduce ambiguity
- `Do`
- `Do Not`
- `Review Questions` when a human decision or reviewer check matters
- `Summary`

For small sections, use compressed form: `BLUF`, `Reasoning`, `Do`, `Do Not`,
and `Summary`.

## BLUF Quality Rule

Every BLUF must:

- be one plain-English sentence;
- state the decision, risk, action, or finding;
- be understandable without the rest of the section;
- avoid abstract filler such as "explores considerations";
- identify consequence when risk is the point.

If the BLUF cannot be written clearly, the section is not understood well enough.
Rewrite or block before handoff.

## No-Fog Gate

- Every major section starts with a clear `BLUF:`.
- The BLUF-only summary explains the document without the body.
- Every risk states a plain-English consequence.
- Every recommendation says what to do next.
- Every `Do Not` prevents a real failure mode.
- Every validation or closure claim links to evidence or is marked
  missing/blocked.
- Paragraphs stay short enough to scan.
- No section asks Jamie to infer the point from agent prose.

## Stage Adaptation

- `he-spec`: preserve spec substance; apply BLUF to intent, scope,
  requirements, risk, acceptance, validation, open questions, and decision
  sections.
- `he-plan`: apply BLUF at document, implementation strategy, boundary,
  work-unit or slice, validation, rollback, handoff, and final-decision levels.
- `he-code-review`: keep findings first; use a single review BLUF for durable
  `.harness/review/**` artifacts and do not bury severity findings under
  generic sections.
- `he-eval-report`: use closure BLUF to say Complete, Complete with follow-up,
  Blocked, Needs rework, or Unsafe to close before proof detail.
- `he-refactor`, `he-linear-plan`, `he-reconcile`, `he-improve`, and
  `he-strategy`: use BLUF for phase, decision, and status summaries where the
  artifact drives future work.

## Anti-Patterns

- Creating a full simplified duplicate after the full artifact.
- Letting BLUF become vague ceremony.
- Moving validation, rollback, traceability, or Linear mutation status out of
  the artifact to make it shorter.
- Replacing HE stage contracts with BLUF prose.
- Applying full BLUF blocks to every tiny finding when a compact finding format
  is clearer.

## Validation

Run `python3 Plugins/harness-engineering/scripts/check_bluf_structure.py
<artifact.md> --json` for non-trivial generated artifacts when the repository
has the HE plugin available. If the script is unavailable, validate by reviewing
the generated artifact against the No-Fog Gate and record `pass`, `fail`, or
`blocked`.
