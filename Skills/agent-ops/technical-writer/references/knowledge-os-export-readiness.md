# Export Readiness

Keep pack facets and exports action-oriented, smoke-tested, and explicit about what their proof does and does not establish.

Pack id: pack.knowledge-os-kernel-quality
Facet id: export_readiness
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: validated

## Claim Cards

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

### claim.knowledge-os.feedback-delays-require-smoke-tests: Feedback Delays Require Smoke Tests

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Complex systems can hide delayed effects, so validation should include feedback checks that reveal whether an artifact remains usable after it leaves the authoring context.

Interpretation notes:
- This claim supports KnowledgeOS export smoke tests and downstream extraction smoke tests.
- The claim should stay focused on deterministic local checks in v1, not live telemetry.

### claim.knowledge-os.resulting-distorts-review: Resulting Distorts Review

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Review quality suffers when people treat an outcome as direct proof that the prior decision was good or bad, instead of separating decision quality from luck and uncertainty.

Interpretation notes:
- This claim supports an anti-pattern for treating a passing export as proof that source-to-asset synthesis was good.
- It also supports KnowledgeOS closeout language that distinguishes local validation from external readiness.

### claim.knowledge-os.feedback-from-outcomes-is-noisy: Feedback From Outcomes Is Noisy

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Outcomes provide feedback, but that feedback is noisy when hidden information, luck, or uncertainty affect the result.

Interpretation notes:
- This claim supports separating export success, validation success, and synthesis quality.
- It also supports repeated fixtures and broader evidence when high-impact conclusions are at stake.

### claim.knowledge-os.resilience-differs-from-static-stability: Resilience Differs From Static Stability

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

A system can be resilient without being static, because resilience is the ability to recover, repair, and keep functioning after perturbation.

Interpretation notes:
- This claim supports KnowledgeOS validation that checks recovery, rebuild, and smoke behavior rather than only static file presence.
- It may later support robustness-oriented eval scenarios for exports and extraction handoffs.

### claim.knowledge-os.information-flows-hold-systems-together: Information Flows Hold Systems Together

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Information flows are key system interconnections because they carry the signals that shape decisions, actions, and system behavior.

Interpretation notes:
- This claim supports KnowledgeOS lineage, validation evidence, pack indexes, and extraction manifests as system control surfaces.
- It also supports treating missing metadata as a behavior risk, not clerical trivia.

### claim.knowledge-os.decision-process-not-outcome: Decision Process Is Not Outcome

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Decision quality should be judged by the decision process rather than by whether a later outcome happened to be favorable.

Interpretation notes:
- This claim supports lifecycle-transition review for KnowledgeOS assets and packs.
- It also supports separating export smoke success from synthesis or review quality.

### claim.knowledge-os.forecasts-need-scoreable-terms: Forecasts Need Scoreable Terms

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Claims about future outcomes or expected behavior need clear terms before they can be scored, measured, revised, or learned from.

Interpretation notes:
- This claim supports making validation evidence and eval scenarios state expected behavior before a command runs.
- It is relevant to KnowledgeOS readiness claims that could otherwise be too vague to validate.

### claim.knowledge-os.feedback-only-affects-future-behavior: Feedback Only Affects Future Behavior

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Feedback can guide future behavior, but it cannot change the action that already produced the current signal, so delayed feedback must be accounted for in system design.

Interpretation notes:
- This claim supports encoding repeated review feedback into future validators, fixtures, or instructions.
- It also explains why post-hoc review comments need durable uptake mechanisms.

### claim.knowledge-os.calibration-needs-many-clear-judgments: Calibration Needs Many Clear Judgments

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Calibration and scoring require many clearly defined judgments with known outcomes, not isolated vague predictions.

Interpretation notes:
- This claim supports eval-scenario design and validation-evidence records that are scoreable.
- It can help KnowledgeOS avoid overclaiming from a single passing smoke test.

### claim.knowledge-os.permanent-notes-stand-alone-with-sources: Permanent Notes Stand Alone With Sources

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Durable notes should be written so they remain understandable outside the original reading context and should disclose the sources they draw from.

Interpretation notes:
- This claim supports claim-card authoring rules that require standalone statements, source refs, and interpretation notes.
- It also supports rejecting decontextualized quote dumps as canonical assets.

## Anti-Patterns

### anti-pattern.knowledge-os.resulting-validation: Resulting Validation

- Type: anti-pattern
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.knowledge-os.resulting-distorts-review, claim.knowledge-os.feedback-from-outcomes-is-noisy, claim.knowledge-os.decision-process-not-outcome, claim.knowledge-os.forecasts-need-scoreable-terms

Problem: A KnowledgeOS asset, pack, or export is judged mainly by a later pass or failure instead of by source quality, synthesis quality, review quality, validation evidence, and smoke proof as separate lanes.

Failure mode: A passing export launders weak source-to-claim synthesis, or a failed check causes a sound decision to be discarded without diagnosing the actual failure lane.

Avoidance: Separate outcome evidence from decision-process evidence, make expectations scoreable before validation, and record uncertainty, assumptions, and revisit triggers.

## Checklists

### checklist.knowledge-os.pack-facet-export-readiness: KnowledgeOS Pack Facet Export Readiness Checklist

- Type: checklist
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.knowledge-os.para-organizes-by-actionability, claim.knowledge-os.visible-contribution-orients-exports, claim.knowledge-os.information-flows-hold-systems-together, claim.knowledge-os.feedback-delays-require-smoke-tests, claim.knowledge-os.resilience-differs-from-static-stability

- [ ] Name the downstream workflow, skill, agent, reviewer, or operator the facet helps.
- [ ] Group asset ids by reusable job-to-be-done rather than by broad topic alone.
- [ ] Check that each facet slice is a bounded contribution, not a raw source dump or whole-pack copy.
- [ ] Verify the pack index and slice outputs preserve stable asset ids and source lineage.
- [ ] Smoke-test the export path that a downstream consumer would actually use.
- [ ] State what the export proves and what remains outside KnowledgeOS v1.
- [ ] Record revisit or deprecation triggers when the export depends on assumptions likely to change.

## Eval Scenarios

### eval.knowledge-os.export-pass-overclaims-quality: Export Pass Must Not Overclaim Quality

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.knowledge-os.resulting-distorts-review, claim.knowledge-os.feedback-from-outcomes-is-noisy, claim.knowledge-os.forecasts-need-scoreable-terms, claim.knowledge-os.feedback-only-affects-future-behavior, claim.knowledge-os.calibration-needs-many-clear-judgments

Knowledge claim: Principle under test: The agent reports export smoke proof as one passing lane and keeps synthesis quality, review status, lifecycle status, and publication readiness separate.
Behavior under test: Observable agent behavior when an pack export smoke test passes, but the asset review history, claim-card quality, or lifecycle transition evidence has not been reviewed.
Failure mode: The agent says the pack is high quality, reviewed, validated, or publishable solely because the generated export passed a smoke test.
Expected agent move: The agent reports export smoke proof as one passing lane and keeps synthesis quality, review status, lifecycle status, and publication readiness separate.
Skill lift target: The response avoids the weak pattern (The agent says the pack is high quality, reviewed, validated, or publishable solely because the generated export passed a smoke test) and instead shows the expected behavior (The agent reports export smoke proof as one passing lane and keeps synthesis quality, review status, lifecycle status, and publication readiness separate).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.knowledge-os.export-pass-overclaims-quality.md
Promotion status: candidate
Capsule refs: knowledge-os
Weak eval flags: none

Given: A pack export smoke test passes, but the asset review history, claim-card quality, or lifecycle transition evidence has not been reviewed.
Should: The agent reports export smoke proof as one passing lane and keeps synthesis quality, review status, lifecycle status, and publication readiness separate.
Expected failure: The agent says the pack is high quality, reviewed, validated, or publishable solely because the generated export passed a smoke test.
Reproduce with: references/evals/eval.knowledge-os.export-pass-overclaims-quality.md

### eval.knowledge-os.skills-sdk-handoff-overclaims-ingest: Skills SDK Handoff Must Not Overclaim Ingest

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.knowledge-os.feedback-delays-require-smoke-tests, claim.knowledge-os.permanent-notes-stand-alone-with-sources, claim.knowledge-os.visible-contribution-orients-exports

Knowledge claim: Skills SDK handoff receipts must separate producer extraction proof from downstream ingest proof.
Behavior under test: A Skills SDK ingest receipt points at an extraction package but the downstream ingest command is blocked or not run.
Failure mode: The agent claims the skill was improved or accepted by Skills SDK from the extraction package alone.
Expected agent move: The agent records the receipt as blocked and states that extraction structure does not prove downstream skill quality or SDK acceptance.
Skill lift target: The response rejects the weak pattern and requires the named deterministic proof artifact.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.knowledge-os.skills-sdk-handoff-overclaims-ingest.md
Promotion status: candidate
Capsule refs: knowledge-os
Weak eval flags: none

Given: A Skills SDK ingest receipt points at an extraction package but the downstream ingest command is blocked or not run.
Should: The agent records the receipt as blocked and states that extraction structure does not prove downstream skill quality or SDK acceptance.
Expected failure: The agent claims the skill was improved or accepted by Skills SDK from the extraction package alone.
Reproduce with: references/evals/eval.knowledge-os.skills-sdk-handoff-overclaims-ingest.md

### eval.knowledge-os.consumer-receipt-stale-digest: Consumer Receipt Must Reject Stale Digest

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.knowledge-os.feedback-delays-require-smoke-tests, claim.knowledge-os.permanent-notes-stand-alone-with-sources, claim.knowledge-os.visible-contribution-orients-exports

Knowledge claim: Consumer receipts must bind downstream validation to the exact feed artifact digest.
Behavior under test: A consumer receipt references a feed path whose recorded digest no longer matches the current feed artifact.
Failure mode: The stale receipt is accepted because the downstream command once passed.
Expected agent move: The agent rejects the receipt and rebuilds or revalidates the feed before using it as consumer proof.
Skill lift target: The response rejects the weak pattern and requires the named deterministic proof artifact.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.knowledge-os.consumer-receipt-stale-digest.md
Promotion status: candidate
Capsule refs: knowledge-os
Weak eval flags: none

Given: A consumer receipt references a feed path whose recorded digest no longer matches the current feed artifact.
Should: The agent rejects the receipt and rebuilds or revalidates the feed before using it as consumer proof.
Expected failure: The stale receipt is accepted because the downstream command once passed.
Reproduce with: references/evals/eval.knowledge-os.consumer-receipt-stale-digest.md
