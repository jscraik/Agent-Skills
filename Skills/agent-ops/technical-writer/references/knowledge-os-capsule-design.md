# Knowledge Capsule Design

Design portable capsules as behavior-shaping references with source models, relationship maps, downstream integration, failure recovery, and deterministic eval hooks.

Pack id: pack.knowledge-os-kernel-quality
Facet id: capsule_design
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: validated

## Claim Cards

### claim.knowledge-os.capsules-operational-references: Capsules Are Operational References

- Type: claim-card
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference

A knowledge capsule should be an operational reference that changes a consuming reader or skill's behavior, not a passive source summary.

Interpretation notes:
- This claim supports requiring active guidance, decision rules, examples, recovery, and validation ideas in portable handoffs.
- It does not claim the cited books define KnowledgeOS capsules directly.

### claim.knowledge-os.capsules-need-source-models: Capsules Need Source Models

- Type: claim-card
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference

A capsule needs an explicit source model that says whether each contribution is a principle, pattern, procedure, warning, example, counterexample, eval, relationship, or routing cue.

Interpretation notes:
- This claim supports rejecting undifferentiated digests when exporting capsules for Skills SDK, Jamie Brain, or other consumers.
- The source model is a KnowledgeOS design rule derived from the local corpus, not a direct quote.

### claim.knowledge-os.capsules-need-relationship-maps: Capsules Need Relationship Maps

- Type: claim-card
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference, article_source_note_paraphrase

A capsule should preserve relationships among concepts, decisions, failures, guardrails, outputs, and validations so downstream consumers can apply the knowledge in context.

Interpretation notes:
- This claim supports the capsule-design validator's relationship-map requirement.
- It does not require a graph database or UI in KnowledgeOS v1.

### claim.knowledge-os.capsules-need-eval-contracts: Capsules Need Eval Contracts

- Type: claim-card
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference

A capsule that claims to improve a skill or downstream project should include eval scenarios or deterministic validation ideas that expose the intended behavior change.

Interpretation notes:
- This claim supports requiring eval scenarios in capsule-design capsules and consumer handoffs.
- Producer-side eval intent remains separate from downstream runtime or release proof.

### claim.knowledge-os.capsules-route-by-downstream-job: Capsules Route By Downstream Job

- Type: claim-card
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference

A capsule should route by the downstream job it improves, such as skill behavior, Jamie Brain teaching, XWriter article drafting, or KnowledgeOS extraction quality.

Interpretation notes:
- This claim supports load_when guidance and downstream integration sections.
- It does not prove any named downstream project has consumed the capsule.

### claim.knowledge-os.permanent-notes-stand-alone-with-sources: Permanent Notes Stand Alone With Sources

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Durable notes should be written so they remain understandable outside the original reading context and should disclose the sources they draw from.

Interpretation notes:
- This claim supports claim-card authoring rules that require standalone statements, source refs, and interpretation notes.
- It also supports rejecting decontextualized quote dumps as canonical assets.

### claim.knowledge-os.visible-contribution-orients-exports: Visible Contribution Orients Exports

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Knowledge work gains practical value when it is made visible as a small contribution to a real goal, person, relationship, or network.

Interpretation notes:
- This claim supports pack purpose and export smoke checks that name a downstream user or workflow.
- It should improve publication readiness without turning KnowledgeOS into a social workflow tool.

### claim.knowledge-os.para-organizes-by-actionability: PARA Organizes By Actionability

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Knowledge organization becomes more useful when saved material is sorted by actionability and current use rather than by static topic alone.

Interpretation notes:
- This claim supports pack facets and exports organized around downstream jobs rather than broad subject categories.
- In KnowledgeOS, this maps most directly to pack facet design, not folder layout.

### claim.knowledge-os.progressive-summarization-improves-discoverability: Progressive Summarization Improves Discoverability

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Distilling source material in layers can make the most useful parts easier to rediscover and reuse without rereading the entire original source.

Interpretation notes:
- This claim supports bounded claim-card summaries and later canonical assets that preserve only reusable substance.
- KnowledgeOS should preserve source refs so distillation does not become provenance loss.

### claim.knowledge-os.distilled-notes-need-context-links: Distilled Notes Need Context Links

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Notes become more useful when they are written as standalone ideas, connected to other relevant notes, and placed into contexts where they can contribute to future work.

Interpretation notes:
- This claim supports claim-card and canonical-asset quality checks for standalone meaning and lineage-rich connections.
- In KnowledgeOS terms, the source-note versus idea-note split maps to source-bound claim cards versus reusable canonical assets.

### claim.knowledge-os.information-flows-hold-systems-together: Information Flows Hold Systems Together

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Information flows are key system interconnections because they carry the signals that shape decisions, actions, and system behavior.

Interpretation notes:
- This claim supports KnowledgeOS lineage, validation evidence, pack indexes, and extraction manifests as system control surfaces.
- It also supports treating missing metadata as a behavior risk, not clerical trivia.

### claim.knowledge-os.entry-links-create-reuse-contexts: Entry Links Create Reuse Contexts

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Links and entry points help the same idea become reusable in multiple contexts and make future lines of thought discoverable.

Interpretation notes:
- This claim supports asset lineage, related-asset links, and pack facet membership by stable ids.
- It should not imply that KnowledgeOS v1 needs a graph UI.

### claim.knowledge-os.forecasts-need-scoreable-terms: Forecasts Need Scoreable Terms

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Claims about future outcomes or expected behavior need clear terms before they can be scored, measured, revised, or learned from.

Interpretation notes:
- This claim supports making validation evidence and eval scenarios state expected behavior before a command runs.
- It is relevant to KnowledgeOS readiness claims that could otherwise be too vague to validate.

### claim.knowledge-os.feedback-delays-require-smoke-tests: Feedback Delays Require Smoke Tests

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Complex systems can hide delayed effects, so validation should include feedback checks that reveal whether an artifact remains usable after it leaves the authoring context.

Interpretation notes:
- This claim supports KnowledgeOS export smoke tests and downstream extraction smoke tests.
- The claim should stay focused on deterministic local checks in v1, not live telemetry.

### claim.knowledge-os.calibration-needs-many-clear-judgments: Calibration Needs Many Clear Judgments

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Calibration and scoring require many clearly defined judgments with known outcomes, not isolated vague predictions.

Interpretation notes:
- This claim supports eval-scenario design and validation-evidence records that are scoreable.
- It can help KnowledgeOS avoid overclaiming from a single passing smoke test.

## Principles

### principle.knowledge-os.behavioral-capsule-handoff: Behavioral Capsule Handoff

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference, article_source_note_paraphrase
- Derived from claims: claim.knowledge-os.capsules-operational-references, claim.knowledge-os.capsules-need-source-models, claim.knowledge-os.capsules-need-relationship-maps, claim.knowledge-os.capsules-need-eval-contracts, claim.knowledge-os.capsules-route-by-downstream-job

Design every portable knowledge capsule as a behavior-shaping handoff with source model, relationship map, downstream integration, failure modes, and eval scenarios.

Rationale: A capsule only improves Skills SDK, Jamie Brain, or another consumer when it changes decisions, output shape, recovery, validation, or eval coverage while preserving source lineage and proof boundaries.

Application notes:
- Start from the downstream job, then choose the smallest source-backed knowledge slice that changes that job.
- Preserve relationships such as concept-to-decision, failure-to-guardrail, output-to-validation, and source-to-eval.
- Keep KnowledgeOS producer proof separate from downstream acceptance, runtime sync, release, or teaching-quality proof.

## Anti-Patterns

### anti-pattern.knowledge-os.passive-capsule-design: Passive Capsule Design

- Type: anti-pattern
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.knowledge-os.capsules-operational-references, claim.knowledge-os.capsules-need-eval-contracts, claim.knowledge-os.capsules-route-by-downstream-job

Problem: A capsule reads like a polished summary but does not encode the source model, relationships, downstream integration, failure modes, or eval scenarios needed to change behavior.

Failure mode: Skills SDK, Jamie Brain, or another consumer can quote the capsule but cannot reliably improve routing, output shape, recovery, validation, or teaching behavior from it.

Avoidance: Require the operational playbook plus capsule-design sections, and reject capsule-design artifacts that lack relationship and eval surfaces.

## Checklists

### checklist.knowledge-os.operational-capsule-design: Operational Capsule Design Checklist

- Type: checklist
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference, article_source_note_paraphrase
- Derived from claims: claim.knowledge-os.capsules-operational-references, claim.knowledge-os.capsules-need-source-models, claim.knowledge-os.capsules-need-relationship-maps, claim.knowledge-os.capsules-need-eval-contracts, claim.knowledge-os.capsules-route-by-downstream-job

- [ ] Name the downstream job before writing the capsule.
- [ ] Classify each source contribution as a principle, pattern, procedure, warning, example, counterexample, eval, relationship, or routing cue.
- [ ] Include a source model that distinguishes direct claims, synthesized claims, interpretation notes, and proof boundaries.
- [ ] Include a relationship map that links concepts to decisions, failures to guardrails, outputs to validation, and source claims to eval scenarios.
- [ ] Include downstream integration guidance for Skills SDK, Jamie Brain, or the named consumer without claiming that the consumer accepted it.
- [ ] Include failure modes and recovery moves that tell the consumer what to do when the capsule is too vague, unsupported, over-broad, or misrouted.
- [ ] Include deterministic validation ideas or eval scenarios that can prove the intended behavior change.

## Rubrics

### rubric.knowledge-os.capsule-design-quality: Knowledge Capsule Design Quality Rubric

- Type: rubric
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference, article_source_note_paraphrase
- Derived from claims: claim.knowledge-os.capsules-operational-references, claim.knowledge-os.capsules-need-source-models, claim.knowledge-os.capsules-need-relationship-maps, claim.knowledge-os.capsules-need-eval-contracts, claim.knowledge-os.capsules-route-by-downstream-job

- downstream-job: Does the capsule name the consuming job and behavior it should improve?
  - pass: The capsule names the downstream consumer or job and states the decision, output, recovery, validation, or eval behavior it changes.
  - fail: The capsule is a topic summary without a consuming job or expected behavior change.
- source-model: Does the capsule classify source contributions instead of blending them into one digest?
  - pass: The capsule distinguishes principles, patterns, procedures, warnings, examples, counterexamples, evals, relationships, or routing cues.
  - fail: The capsule presents all source material as undifferentiated prose.
- relationship-map: Does the capsule preserve relationships needed for application?
  - pass: The capsule maps concepts to decisions, failures to guardrails, outputs to validation, and source claims to eval scenarios.
  - fail: The capsule lists ideas without explaining how they interact.
- operational-playbook: Can a consuming skill act differently after loading the capsule?
  - pass: The capsule includes decision rules, output shape, examples, recovery moves, and boundaries.
  - fail: The capsule only describes what was extracted or where it came from.
- eval-coverage: Can the claimed behavior change be tested?
  - pass: The capsule includes deterministic validation ideas or eval scenarios with expected failure and expected agent move.
  - fail: The capsule has no testable scenario or relies on reader confidence.

## Eval Scenarios

### eval.knowledge-os.capsule-design-without-relationships: Capsule Design Requires Relationships And Evals

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference, article_source_note_paraphrase
- Derived from claims: claim.knowledge-os.capsules-need-relationship-maps, claim.knowledge-os.capsules-need-eval-contracts, claim.knowledge-os.capsules-operational-references

Knowledge claim: Capsule design references must include relationship and eval surfaces, not only prose guidance.
Behavior under test: Observable KnowledgeOS validator behavior when a capsule-design artifact omits relationship mapping and eval coverage.
Failure mode: The validator accepts a polished but behavior-weak capsule-design reference.
Expected agent move: The validator rejects the capsule and points to the missing capsule-design sections.
Skill lift target: The negative fixture is rejected by the repo validator.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.knowledge-os.capsule-design-without-relationships.md
Promotion status: candidate
Capsule refs: knowledge-os
Weak eval flags: none

Given: A knowledge capsule design reference includes general guidance and ordinary operational headings but omits source model, relationship map, downstream integration, failure modes, and eval scenarios.
Should: The validator rejects the reference with capsule-design-missing-sections before the capsule can be treated as a portable handoff.
Expected failure: The handoff passes because it is readable and has generic headings, even though it cannot improve downstream skill or Jamie Brain behavior deterministically.
Reproduce with: references/evals/eval.knowledge-os.capsule-design-without-relationships.md

## Source Model

- Classify each contribution before synthesis: principle, pattern, procedure, warning, example, counterexample, eval, relationship, or routing cue.
- Keep direct claims, synthesized claims, interpretation notes, source lineage, and proof boundaries separate.
- Treat article and book material as evidence for reusable behavior only after it is represented by reviewed claim cards or derived assets.

## Relationship Map

- Map concept -> decision when a source idea changes what the consuming skill should choose.
- Map failure -> guardrail when repeated steering, vague prose, missing evidence, or weak routing should become a validator, fixture, schema, or eval.
- Map output -> validation when a capsule changes generated docs, skill references, Jamie Brain teaching material, or consumer receipts.
- Map source claim -> eval scenario so downstream behavior has a deterministic proof path.

## Downstream Integration

- For Skills SDK, use the capsule to update skill-local references, routing, eval scenarios, and package validation without requiring KnowledgeOS at runtime.
- For Jamie Brain, use the capsule to improve teaching, retrieval, and source-backed lesson material while keeping private source boundaries explicit.
- For any downstream project, name the capsule that changed a decision, output, recovery path, validation command, or eval case.
- Keep KnowledgeOS producer proof separate from downstream acceptance, runtime sync, release, CI, or teaching-quality proof.

## Failure Modes

- Passive summary: the capsule is readable but does not change decisions, outputs, recovery, validation, or eval coverage.
- Relationship loss: the capsule lists ideas but drops concept-to-decision, failure-to-guardrail, output-to-validation, or source-to-eval links.
- Overclaiming: producer validation is reported as Skills SDK, Jamie Brain, CI, release, or public-readiness proof.
- Source blending: book, article, doc, and skill evidence collapse into one digest without source model or claim lineage.

## Eval Scenarios

- Given a capsule-design reference lacks source model, relationship map, downstream integration, failure modes, or eval scenarios, the validator should reject it with capsule-design-missing-sections.
- Given a generated capsule changes skill behavior, the consumer should add or update an eval case that proves the changed decision, output, recovery path, or validation behavior.
- Given a Jamie Brain lesson uses the capsule, the consumer should preserve source-backed teaching boundaries and avoid claiming KnowledgeOS producer validation proves learner outcomes.
