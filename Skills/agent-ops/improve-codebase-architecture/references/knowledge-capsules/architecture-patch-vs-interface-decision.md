# Patch Versus Interface Decision

Compare the smallest patch against a deeper interface change through options, constraints, reversibility, assumptions, tripwires, and tracer proof.

Pack id: pack.codebase-architecture
Facet id: patch_vs_interface_decision
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.arch.reversible-architecture-decisions-need-tests: Reversible Architecture Decisions Need Tests

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Architecture choices are safer when options, assumptions, reversibility, constraints, and fitness checks are explicit before the team commits to a deeper interface change.

Interpretation notes:
- This claim supports comparing patch design against interface design.
- It keeps architecture decisions tied to proof and rollback instead of preference.

## Checklists

### checklist.arch.patch-vs-interface-decision: Patch Versus Interface Decision Checklist

- Type: checklist
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.arch.reversible-architecture-decisions-need-tests

- [ ] Name the current pain as change amplification, cognitive load, temporal coupling, leaky abstraction, language drift, validation gap, or ownership confusion.
- [ ] Describe the smallest patch design and the deeper interface design in terms of changed files, callers, and public contract.
- [ ] State the constraint or bottleneck each option addresses.
- [ ] List assumptions each option depends on and the quickest local check for each material assumption.
- [ ] Compare reversibility, migration cost, blast radius, compatibility risk, and expected future change.
- [ ] Define the tracer proof that would make the preferred option credible.
- [ ] Add a tripwire for revisiting or rolling back the decision.
- [ ] Record the decision in the repo-approved decision surface when the choice is structural or surprising.

## Eval Scenarios

### eval.arch.patch-vs-interface-without-shared-decision: Patch Versus Interface Without Shared Decision

- Type: eval-scenario
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.arch.reversible-architecture-decisions-need-tests

Knowledge claim: The reviewer presents both options with cost, reversibility, blast radius, assumptions, tracer proof, and asks the shared decision question before selecting the structural path.
Behavior under test: The reviewer presents both options with cost, reversibility, blast radius, assumptions, tracer proof, and asks the shared decision question before selecting the structural path.
Failure mode: The reviewer chooses the deeper interface design because it sounds cleaner, without a user decision or tripwire.
Expected agent move: The reviewer presents both options with cost, reversibility, blast radius, assumptions, tracer proof, and asks the shared decision question before selecting the structural path.
Skill lift target: The reviewer presents both options with cost, reversibility, blast radius, assumptions, tracer proof, and asks the shared decision question before selecting the structural path.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.arch.patch-vs-interface-without-shared-decision.md
Promotion status: candidate
Capsule refs: codebase-architecture
Weak eval flags: none

Given: A requested refactor could be solved by a small compatibility patch or by changing a public interface used by several callers, and request_user_input is available.
Should: The reviewer presents both options with cost, reversibility, blast radius, assumptions, tracer proof, and asks the shared decision question before selecting the structural path.
Expected failure: The reviewer chooses the deeper interface design because it sounds cleaner, without a user decision or tripwire.
Reproduce with: references/evals/eval.arch.patch-vs-interface-without-shared-decision.md
