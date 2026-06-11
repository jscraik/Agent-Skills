# BLUF Review Contract

Read when: writing, reviewing, or validating durable HE specs, plans, reframe
programs, Linear plans, eval reports, review artifacts, strategy artifacts,
reconcile reports, or other operator-facing `.harness/**` artifacts where
scanability matters.

## Purpose

BLUF means Bottom Line Up Front: one plain-English paragraph at the beginning of
an important artifact that lets a busy non-technical reader and a developer who
does not know the project understand what the document is for, why it exists,
what decision or recommendation it makes, what matters most, and what should
happen next before reading the detail. It follows the same practical shape as
plain-language and inverted-pyramid guidance: put the most important conclusion
first, then add only the context needed to decide what to do. It is an opening
executive summary, not a repeated section pattern.

## When to Apply

Apply the full contract to non-trivial durable artifacts, especially:

- `.harness/specs/**`
- `.harness/plan/**`
- `.harness/evals/**`
- `.harness/review/**`
- `.harness/reframes/**`
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

- `BLUF:` one substantive paragraph, normally 4-7 sentences, that explains
  the artifact's job to a busy non-technical reader and to a developer who is
  new to the project. It must state what the document covers, why the work
  matters, what decision or recommendation is being made, what risk or
  constraint matters most, and what happens next.
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

- be one plain-English paragraph, not a headline or slogan;
- be detailed enough for a non-technical reader to understand the document's
  job without knowing the repository;
- be specific enough for a developer unfamiliar with the project to understand
  the affected system, expected direction, and next step;
- state the artifact intent, recommendation or decision, major risk or blocker,
  and next action;
- be understandable without the rest of the artifact;
- avoid abstract filler such as "explores considerations";
- identify consequence when risk is the point.

Use this paragraph shape:

1. Start with the answer: what this document is deciding, recommending, or
   proving.
2. Name the thing in plain English: the feature, plan, report, system, or
   workflow being covered.
3. Explain why the reader should care: the user, operator, safety, delivery, or
   review problem it addresses.
4. State the practical consequence: what is allowed, blocked, narrowed,
   approved, unsafe, or ready.
5. Name the most important risk, constraint, or missing proof.
6. End with the exact next action.

Good BLUFs explain the whole document in miniature:

```text
BLUF: This spec defines a read-only dry-run coverage ledger for X-writer so Jamie
can inspect whether a Birdclaw backup is complete before any private or
moderated content is imported. The document exists to turn a vague import idea
into a safe implementation contract: it says which backup files are inspected,
which JSON ledger fields must be produced, which private shards must be blocked,
and which validation commands prove the result. The recommendation is to build
only the dry-run ledger now, because live auth, raw post import, and source-note
generation would increase privacy risk before the boundary is proven. The main
risk is accidental data exposure, so the spec requires redacted outputs,
path-safety checks, and failing tests for private-message leakage. The next step
is for `he-plan` to create bounded implementation units that preserve those
safety checks and acceptance IDs.
```

Bad BLUFs are too thin to orient either audience:

```text
BLUF: Build the coverage ledger and validate it.
```

If the opening BLUF cannot be written clearly, the artifact is not understood
well enough. Rewrite or block before handoff.

## No-Fog Gate

- The artifact has exactly one opening `BLUF:` field in `Command Summary`.
- The opening BLUF is a real paragraph that explains the document's job,
  affected system, decision or recommendation, major risk or blocker, and next
  action without requiring the body.
- No section repeats `BLUF:` as a heading or label.
- Every risk states a plain-English consequence.
- Every recommendation says what to do next.
- Every `Do Not` prevents a real failure mode.
- Every validation or closure claim links to evidence or is marked
  missing/blocked.
- Paragraphs stay short enough to scan.
- No section asks Jamie to infer the point from agent prose.

## Stage Adaptation

- `he-spec`: use one opening BLUF to explain what the spec is specifying, why
  the feature matters, what decision the spec makes, what risk constrains the
  feature, and what `he-plan` should do next; keep requirements and acceptance
  in normal spec sections.
- `he-plan`: use one opening BLUF to explain what the plan will change, why
  that work matters, how execution is bounded, what risk could stop it, and
  what handoff follows; keep work units in normal plan sections.
- `he-code-review`: keep findings first; use a single review BLUF only for
  durable `.harness/review/**` artifacts and do not bury severity findings under
  generic sections.
- `he-eval-report`: use one opening closure BLUF to say Complete, Complete with
  follow-up, Blocked, Needs rework, or Unsafe to close before proof detail.
- `he-reframe`, `he-linear-plan`, `he-reconcile`, `he-improve`, and
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

## External Writing Guidance Applied

The HE BLUF contract applies these public writing patterns:

- Put the most important information first, as recommended by the U.S. plain
  language guidance for organizing content:
  https://www.plainlanguage.gov/guidelines/organize/put-the-most-important-information-first/.
- Use inverted-pyramid ordering: lead with the conclusion, then provide
  supporting detail in decreasing order of importance, as described by Nielsen
  Norman Group:
  https://www.nngroup.com/articles/inverted-pyramid/.
- Treat the BLUF like a compact project poster or executive summary:
  audience-aware, standalone, focused on the recommendation, reason, evidence,
  and action rather than a teaser for the body. Atlassian's project poster
  pattern is a useful product-development analogue because it asks teams to
  make the problem, value, and direction explicit before execution:
  https://www.atlassian.com/team-playbook/plays/project-poster.

## Validation

Run `python3 Plugins/synaipse-harness/scripts/check_bluf_structure.py
<artifact.md> --json` for non-trivial generated artifacts when the repository
has the HE plugin available. If the script is unavailable, validate by reviewing
the generated artifact against the No-Fog Gate and record `pass`, `fail`, or
`blocked`.
