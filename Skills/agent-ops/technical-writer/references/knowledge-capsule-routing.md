# Knowledge Capsule Routing

This first-party index promotes vendored capsule routing into the skill package.
Use it before opening generated capsule bodies so capsule guidance is not hidden
inside second-order references.

## Capsules

- `references/technical-writer-devrel-communication-devrel-role-and-audience.md`
  - facet: devrel_role_and_audience
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 11
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/technical-writer-devrel-communication-technical-documentation.md`
  - facet: technical_documentation
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 13
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/technical-writer-devrel-communication-developer-education.md`
  - facet: developer_education
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 11
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/technical-writer-devrel-communication-content-design-and-service-docs.md`
  - facet: content_design_and_service_docs
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 13
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/technical-writer-devrel-communication-articles-and-long-form.md`
  - facet: articles_and_long_form
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 12
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/technical-writer-devrel-communication-voice-signal-and-taste.md`
  - facet: voice_signal_and_taste
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 11
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/technical-writer-devrel-communication-storytelling-and-explanation.md`
  - facet: storytelling_and_explanation
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 14
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/technical-writer-devrel-communication-presentations-and-visual-docs.md`
  - facet: presentations_and_visual_docs
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 13
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/technical-writer-devrel-communication-short-form-and-content-creation.md`
  - facet: short_form_and_content_creation
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 9
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/technical-writer-devrel-communication-clarity-style-and-revision.md`
  - facet: clarity_style_and_revision
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 14
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/technical-writer-devrel-communication-accessible-and-inclusive-writing.md`
  - facet: accessible_and_inclusive_writing
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 10
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/technical-writer-devrel-communication-error-messages-and-recovery.md`
  - facet: error_messages_and_recovery
  - pack: pack.developer-advocate-writing
  - selected_asset_count: 11
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/knowledge-os-capsule-design.md`
  - facet: capsule_design
  - pack: pack.knowledge-os-kernel-quality
  - selected_asset_count: 20
  - load_when: task signals match this facet; load only this capsule before adding more.
- `references/knowledge-os-export-readiness.md`
  - facet: export_readiness
  - pack: pack.knowledge-os-kernel-quality
  - selected_asset_count: 17
  - load_when: task signals match this facet; load only this capsule before adding more.

## Package Context

- `references/source-context.yaml`
  - kind: package source-context map
  - load_when: checking vendored KnowledgeOS reference provenance or package-local capsule routing.

## Legacy Nested Capsules

These legacy package-local capsule bodies remain routed for compatibility.
Prefer top-level capsule references for new KnowledgeOS exports.

- `references/knowledge-capsules/clarity-mechanics.md`
  - facet: clarity mechanics
  - load_when: a writing task specifically needs low-search-cost sentence, structure, or brevity mechanics not covered by the top-level clarity capsule.
- `references/knowledge-capsules/revision-and-structure.md`
  - facet: revision and structure
  - load_when: a writing task specifically needs rewrite sequencing, hierarchy, or revision-pass guidance not covered by the top-level clarity capsule.
- `references/knowledge-capsules/technical-explanation.md`
  - facet: technical explanation
  - load_when: a writing task specifically needs explanation scaffolding, concept progression, or analogy boundaries not covered by the top-level technical-documentation capsule.
