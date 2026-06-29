# Knowledge Capsule Routing

This first-party index promotes vendored capsule routing into the skill package.
Use it before opening generated capsule bodies so capsule guidance is not hidden
inside second-order references.

## Writing Type Selector

Choose one primary writing type before opening a capsule. Add another capsule
only when the first one cannot answer the specific gap.

| Writing type | Use when the reader needs | Primary facet |
| --- | --- | --- |
| Technical documentation | API, README, runbook, config, command, code-doc, or proof-backed repo guidance | technical_documentation |
| Developer education | Tutorial, lesson, learning path, concept introduction, or example-led teaching | developer_education |
| Content design and service docs | Task-oriented service content, acceptance criteria, vocabulary, maintenance, or support docs | content_design_and_service_docs |
| Article or long-form | Argument, essay, narrative explanation, long-form technical article, or public post | articles_and_long_form |
| Talk or visual doc | Talk outline, slide deck, visual explanation, diagram-led doc, screenshot-led doc, or standalone slidedoc | presentations_and_visual_docs |
| Short-form or content creation | Social post, short update, concise announcement, content hook, or compact public artifact | short_form_and_content_creation |
| DevRel/community interface | Community-facing docs, trust surface, feedback loop, support boundary, or audience-positioning work | devrel_role_and_audience |
| Voice, signal, and taste | Tone, positioning, credibility, signal density, or brand consistency work | voice_signal_and_taste |
| Storytelling and explanation | Narrative structure, analogy, conceptual explanation, or sticky framing | storytelling_and_explanation |
| Clarity and revision | Style pass, clarity pass, structural revision, or concise rewrite | clarity_style_and_revision |
| Accessible and inclusive writing | Inclusive language, nonvisual support, accessible formatting, or broad-reader support | accessible_and_inclusive_writing |
| Error or recovery text | Error message, blocker explanation, recovery path, warning, or troubleshooting guidance | error_messages_and_recovery |

## Capsules

## Package Context And Eval Assets

- `references/source-context.yaml`
  - facet: provenance_and_runtime_boundary
  - load_when: checking KnowledgeOS snapshot provenance, allowed claims,
    freshness, or the no-runtime-KnowledgeOS boundary.
- `references/eval-regression-plan.json`
  - facet: eval_regression_tracking
  - load_when: repairing scenario regressions, release-lane failure clusters, or
    oss-local/Tessl parity drift.
- `references/evals/eval.glossary-workspace-authority.md`
  - facet: eval_case_review
  - load_when: reviewing glossary and ubiquitous-language authority behavior.
- `references/evals/eval.reader-state-citation-map.md`
  - facet: eval_case_review
  - load_when: reviewing reader-state maps, citations, and evidence grounding.
- `references/evals/eval.validation-lane-separation.md`
  - facet: eval_case_review
  - load_when: reviewing local, hosted, registry, or external validation lanes.
- `references/evals/eval.visual-evidence-decision.md`
  - facet: eval_case_review
  - load_when: reviewing screenshot, diagram, image, or visual-evidence choices.
- `references/evals/eval.writer-gap-gathering.md`
  - facet: eval_case_review
  - load_when: reviewing writer-facing gap handling and missing-information
    questions.
- `references/scorer-calibration/manifest.json`
  - facet: scorer_calibration
  - load_when: calibrating evaluator labels or checking scorer example coverage.
- `references/scorer-calibration/examples.jsonl`
  - facet: scorer_calibration
  - load_when: comparing concise correct outputs with verbose alternatives.
- `references/scorer-calibration/raw/concise-correct-vs-verbose-wrong.json`
  - facet: scorer_calibration
  - load_when: checking concise-correct versus verbose-wrong scorer behavior.
- `references/scorer-calibration/raw/copied-rubric-no-evidence.json`
  - facet: scorer_calibration
  - load_when: checking copied rubric text without artifact evidence.
- `references/scorer-calibration/raw/local-proof-overclaim.json`
  - facet: scorer_calibration
  - load_when: checking local-proof overclaims and validation-lane boundaries.
- `references/scorer-calibration/raw/obvious-correct-doc-evidence.json`
  - facet: scorer_calibration
  - load_when: checking clearly grounded documentation evidence.
- `references/scorer-calibration/raw/obvious-wrong-invented-command.json`
  - facet: scorer_calibration
  - load_when: checking invented command examples and hallucinated proof.
- `references/scorer-calibration/raw/skill-name-only.json`
  - facet: scorer_calibration
  - load_when: checking that skill-name mentions alone do not satisfy behavior.
- `references/knowledge-capsules/clarity-mechanics.md`
  - facet: clarity_style_and_revision
  - load_when: task needs sentence-level clarity, active voice, plain language,
    terminology, brevity, or one-idea-per-unit revision.
- `references/knowledge-capsules/revision-and-structure.md`
  - facet: clarity_style_and_revision
  - load_when: task needs section order, answer-first structure, skimmability,
    multi-pass revision, or existing-doc restructuring.
- `references/knowledge-capsules/technical-explanation.md`
  - facet: storytelling_and_explanation
  - load_when: task needs concept explanation, mental model, causal chain,
    architecture explanation, or example-led technical explanation.

## Pack-Specific Capsules

## Package Context And General Writing Capsules

- `references/source-context.yaml`
  - facet: provenance_and_runtime_boundary
  - load_when: checking KnowledgeOS snapshot provenance, allowed claims,
    freshness, or the no-runtime-KnowledgeOS boundary.
  - do_not_use_for: target repo readiness, raw source completeness, or loading
    every capsule by default.
- `references/knowledge-capsules/clarity-mechanics.md`
  - facet: clarity_style_and_revision
  - load_when: task needs sentence-level clarity, active voice, plain language,
    terminology, brevity, or one-idea-per-unit revision.
- `references/knowledge-capsules/revision-and-structure.md`
  - facet: clarity_style_and_revision
  - load_when: task needs section order, answer-first structure, skimmability,
    multi-pass revision, or existing-doc restructuring.
- `references/knowledge-capsules/technical-explanation.md`
  - facet: storytelling_and_explanation
  - load_when: task needs concept explanation, mental model, causal chain,
    architecture explanation, or example-led technical explanation.

## Pack-Specific Capsules

- `references/knowledge-capsules/technical-writer-devrel-communication-devrel-role-and-audience.md`
  - facet: devrel_role_and_audience
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 11
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/knowledge-capsules/technical-writer-devrel-communication-technical-documentation.md`
  - facet: technical_documentation
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 13
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/knowledge-capsules/technical-writer-devrel-communication-developer-education.md`
  - facet: developer_education
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 11
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/knowledge-capsules/technical-writer-devrel-communication-content-design-and-service-docs.md`
  - facet: content_design_and_service_docs
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 13
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/knowledge-capsules/technical-writer-devrel-communication-articles-and-long-form.md`
  - facet: articles_and_long_form
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 12
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/knowledge-capsules/technical-writer-devrel-communication-voice-signal-and-taste.md`
  - facet: voice_signal_and_taste
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 11
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/knowledge-capsules/technical-writer-devrel-communication-storytelling-and-explanation.md`
  - facet: storytelling_and_explanation
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 14
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/knowledge-capsules/technical-writer-devrel-communication-presentations-and-visual-docs.md`
  - facet: presentations_and_visual_docs
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 13
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/knowledge-capsules/technical-writer-devrel-communication-short-form-and-content-creation.md`
  - facet: short_form_and_content_creation
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 9
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/knowledge-capsules/technical-writer-devrel-communication-clarity-style-and-revision.md`
  - facet: clarity_style_and_revision
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 14
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/knowledge-capsules/technical-writer-devrel-communication-accessible-and-inclusive-writing.md`
  - facet: accessible_and_inclusive_writing
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 10
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/knowledge-capsules/technical-writer-devrel-communication-error-messages-and-recovery.md`
  - facet: error_messages_and_recovery
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 11
  - load_when: task signals match this facet; load only this capsule before adding more.
