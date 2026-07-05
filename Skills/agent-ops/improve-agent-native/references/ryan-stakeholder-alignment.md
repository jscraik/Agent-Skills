# Ryan Stakeholder Alignment

Build consensus, shared data, and synthesized communication so principal engineering changes become adopted defaults.

Pack id: pack.ryan-lopopolo-principal-engineering
Facet id: stakeholder_alignment
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: reviewed

## Claim Cards

### claim.ryan.consensus-builds-leverage: Senior Engineers Build Leverage Through Consensus

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Senior engineering impact comes from shaping team and organizational output, not only from direct technical output.

Interpretation notes:
- This adds the non-code principal-engineering dimension missing from a pure harness pack.

### claim.ryan.shared-cross-functional-data: Cross-Functional Partnership Needs Shared Data

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Productive cross-functional engineering partnerships need shared terms, shared data access, and shared goals.

Interpretation notes:
- This should inform principal engineer skills that touch platform economics, cost, or business trade-offs.

### claim.ryan.synthesis-step: Communication Needs A Synthesis Step

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Stakeholder communication should synthesize meaning, relevance, audience, and next action instead of dumping raw activity or notes.

Interpretation notes:
- This is central to a principal engineer skill that produces review summaries, plans, or decision memos.

## Principles

### principle.ryan.principal-engineer-builds-consensus: Principal Engineer Builds Consensus Before The Proposal

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase
- Derived from claims: claim.ryan.consensus-builds-leverage

A principal engineer creates strategic change by building stakeholder understanding before asking the formal system to approve the change.

Rationale: Consensus work exposes fears, allies, constraints, and roadblocks early enough that the final technical change can be small and self-reinforcing.

Application notes:
- Map affected stakeholders before proposing a broad architectural or platform change.
- Learn objections directly instead of treating disagreement as resistance.
- Design the change so teams can make the right decision by default.

### principle.ryan.shared-data-before-shared-decisions: Shared Data Before Shared Decisions

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase
- Derived from claims: claim.ryan.shared-cross-functional-data

Cross-functional engineering decisions should start from shared terms, shared data access, and an agreed operating cadence.

Rationale: Shared data lets engineering and partner functions find quality gaps, compare forecasts with reality, and rank opportunities from the same evidence.

Application notes:
- Define units, slices, ownership, and freshness before debating decisions.
- Give each function a DRI and a regular sync surface.
- Use the partnership to improve both the engineering system and the partner workflow.

## Heuristics

### heuristic.ryan.synthesize-for-stakeholders: Synthesize For Stakeholders

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase
- Derived from claims: claim.ryan.synthesis-step

Before sending an update, state what changed, why it matters, who should care, and what action or decision is needed.

Use when:
- Summarizing plans, reviews, incidents, meetings, or delivery status.
- Different stakeholders need different levels of detail.
- Raw activity would force readers to infer the point.

Avoid when:
- The audience explicitly asked for raw notes or transcript detail.
- The synthesis would hide uncertainty, dissent, or unresolved decisions.

## Anti-Patterns

### anti-pattern.ryan.raw-activity-dump: Raw Activity Dump

- Type: anti-pattern
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase
- Derived from claims: claim.ryan.synthesis-step

Problem: A technical update lists meetings, messages, commits, or notes without explaining what the audience should understand or do.

Failure mode: Stakeholders must perform the synthesis themselves, so decisions stall, the wrong audience gets overloaded, and important meaning is lost.

Avoidance: Convert activity into audience-specific takeaways, decisions, ownership, timing, and next actions.

## Checklists

### checklist.ryan.stakeholder-alignment: Stakeholder Alignment

- Type: checklist
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase
- Derived from claims: claim.ryan.consensus-builds-leverage, claim.ryan.shared-cross-functional-data, claim.ryan.synthesis-step

- [ ] Name the stakeholders affected by the proposed technical change.
- [ ] Identify each stakeholder's concern, data need, and decision authority.
- [ ] Establish shared terms and shared data before optimizing the solution.
- [ ] Find allies and real objections before the formal proposal.
- [ ] Translate raw work into audience-specific takeaways and next actions.
- [ ] Remove roadblocks so the right behavior becomes self-serve.

## Eval Scenarios

### eval.ryan.stakeholder-synthesis: Stakeholder Update Synthesizes Raw Activity

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase
- Derived from claims: claim.ryan.synthesis-step, claim.ryan.consensus-builds-leverage

Knowledge claim: Principle under test: The agent compresses the activity into decision-relevant meaning, current state, risks, next action, and the evidence boundary.
Behavior under test: Observable agent behavior when an agent has a long log of commits, tests, and review notes and must brief a cross-functional stakeholder.
Failure mode: The agent dumps raw activity or validation output without explaining why it matters to the audience.
Expected agent move: The agent compresses the activity into decision-relevant meaning, current state, risks, next action, and the evidence boundary.
Skill lift target: The response avoids the weak pattern (The agent dumps raw activity or validation output without explaining why it matters to the audience) and instead shows the expected behavior (The agent compresses the activity into decision-relevant meaning, current state, risks, next action, and the evidence boundary).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.ryan.stakeholder-synthesis.md
Promotion status: candidate
Capsule refs: principal-engineering
Weak eval flags: none

Given: An agent has a long log of commits, tests, and review notes and must brief a cross-functional stakeholder.
Should: The agent compresses the activity into decision-relevant meaning, current state, risks, next action, and the evidence boundary.
Expected failure: The agent dumps raw activity or validation output without explaining why it matters to the audience.
Reproduce with: references/evals/eval.ryan.stakeholder-synthesis.md
