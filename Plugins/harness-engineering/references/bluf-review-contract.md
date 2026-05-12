# BLUF Review Contract

Read when: writing, reviewing, or validating durable HE specs, plans, refactor
programs, Linear plans, eval reports, review artifacts, strategy artifacts,
reconcile reports, or other operator-facing `.harness/**` artifacts where
scanability matters.

## Purpose

BLUF means Bottom Line Up Front: one plain-English paragraph at the beginning of
an important artifact that lets a busy reader understand the intent, decision,
risk, and next action before reading the detail. It is an opening executive
summary, not a repeated section pattern.

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

- `BLUF:` one short paragraph, normally 2-5 sentences, that states the artifact
  intent, current recommendation or decision, most important risk or blocker,
  and next action.
- `Decision Needed:` approve, block, revise, split, threat-model, plan, work,
  Linear, or none.
- `Top Risks:` one to three plain-English risks with consequences.
- `Next Action:` exact next action or blocked recovery step.

Use exactly one `BLUF:` field in the artifact unless quoting source material.
Do not create a `BLUF-Only Summary`; that turns BLUF into a second document
instead of a single opening summary.

## Section Pattern

Major sections should be reader-first but should not repeat `BLUF:`. Use direct
headings, short opening prose, tables, examples, Mermaid diagrams, `Do`, `Do
Not`, review questions, and summaries where they clarify the artifact. Work
units or slices should state objective, source trace, allowed scope, validation,
stop condition, rollback, and handoff without using a BLUF label.

## BLUF Quality Rule

The single opening BLUF must:

- be one plain-English paragraph;
- state the artifact intent, recommendation or decision, major risk or blocker,
  and next action;
- be understandable without the rest of the artifact;
- avoid abstract filler such as "explores considerations";
- identify consequence when risk is the point.

If the opening BLUF cannot be written clearly, the artifact is not understood
well enough. Rewrite or block before handoff.

## No-Fog Gate

- The artifact has exactly one opening `BLUF:` field in `Command Summary`.
- The opening BLUF explains the artifact intent, decision or recommendation,
  major risk or blocker, and next action without requiring the body.
- No section repeats `BLUF:` as a heading or label.
- Every risk states a plain-English consequence.
- Every recommendation says what to do next.
- Every `Do Not` prevents a real failure mode.
- Every validation or closure claim links to evidence or is marked
  missing/blocked.
- Paragraphs stay short enough to scan.
- No section asks Jamie to infer the point from agent prose.

## Stage Adaptation

- `he-spec`: use one opening BLUF to summarize the feature intent, readiness,
  risk, and planning handoff; keep requirements and acceptance in normal spec
  sections.
- `he-plan`: use one opening BLUF to summarize the objective, execution
  strategy, readiness risk, and next handoff; keep work units in normal plan
  sections.
- `he-code-review`: keep findings first; use a single review BLUF only for
  durable `.harness/review/**` artifacts and do not bury severity findings under
  generic sections.
- `he-eval-report`: use one opening closure BLUF to say Complete, Complete with
  follow-up, Blocked, Needs rework, or Unsafe to close before proof detail.
- `he-refactor`, `he-linear-plan`, `he-reconcile`, `he-improve`, and
  `he-strategy`: use one opening BLUF where the artifact drives future work;
  use ordinary section summaries after that.

## Anti-Patterns

- Creating a full simplified duplicate after the full artifact.
- Letting BLUF become vague ceremony.
- Repeating `BLUF:` throughout the artifact as a section template.
- Moving validation, rollback, traceability, or Linear mutation status out of
  the artifact to make it shorter.
- Replacing HE stage contracts with BLUF prose.
- Calling every section summary a BLUF when it is not the opening bottom line.

## Validation

Run `python3 Plugins/harness-engineering/scripts/check_bluf_structure.py
<artifact.md> --json` for non-trivial generated artifacts when the repository
has the HE plugin available. If the script is unavailable, validate by reviewing
the generated artifact against the No-Fog Gate and record `pass`, `fail`, or
`blocked`.
