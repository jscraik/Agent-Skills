# Agent-Safe Boundary Proof

Classify a code boundary as safe, risky, or blocked from public interface, caller, hidden-complexity, and regression-proof evidence.

Pack id: pack.codebase-architecture
Facet id: agent_safe_boundary_proof
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.arch.agent-safe-boundaries-need-seams: Agent-Safe Boundaries Need Seams

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

A code boundary is safe for delegated agent work only when the public interface hides coordination complexity and behavior is protected by a seam, characterization test, or equivalent regression proof.

Interpretation notes:
- This claim supports classifying architecture boundaries as safe, risky, or blocked.
- It should be applied only after checking local callers, public interfaces, and test evidence.

## Rubrics

### rubric.arch.agent-safe-boundary-proof: Agent-Safe Boundary Proof Rubric

- Type: rubric
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.arch.agent-safe-boundaries-need-seams

- public-interface: Is the public interface stable and named with the owner that can change it?
  - pass: The review cites the interface, owner, callers, and compatibility expectation.
  - fail: The review calls a folder or helper safe without naming the consumed interface.
- hidden-complexity: Does the boundary hide coordination, defaults, ordering, validation, or special cases from callers?
  - pass: Callers need less implementation knowledge after the boundary is respected or changed.
  - fail: Callers still need hidden setup, ordering, or implementation facts.
- regression-proof: Is behavior protected by a seam, characterization test, contract test, or tracer path?
  - pass: The review names the exact proof path and what behavior it protects.
  - fail: The review relies on shape, naming, or confidence without behavior proof.
- agent-classification: Is the boundary classified safe, risky, or blocked from evidence?
  - pass: The classification cites interface stability, caller evidence, tests, and missing proof.
  - fail: The classification is implied by preference or broad architecture language.

## Eval Scenarios

### eval.arch.agent-safe-boundary-without-regression-proof: Agent-Safe Boundary Without Regression Proof

- Type: eval-scenario
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.arch.agent-safe-boundaries-need-seams

Knowledge claim: The reviewer classifies the boundary as risky or blocked, names the missing proof, and recommends a seam or tracer before autonomous agent edits.
Behavior under test: The reviewer classifies the boundary as risky or blocked, names the missing proof, and recommends a seam or tracer before autonomous agent edits.
Failure mode: The reviewer calls the boundary agent-safe because the module looks clean and the implementation is small.
Expected agent move: The reviewer classifies the boundary as risky or blocked, names the missing proof, and recommends a seam or tracer before autonomous agent edits.
Skill lift target: The reviewer classifies the boundary as risky or blocked, names the missing proof, and recommends a seam or tracer before autonomous agent edits.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.arch.agent-safe-boundary-without-regression-proof.md
Promotion status: candidate
Capsule refs: codebase-architecture
Weak eval flags: none

Given: An architecture review sees a tidy module boundary and clear names, but no caller evidence, contract test, characterization test, or tracer path protects behavior.
Should: The reviewer classifies the boundary as risky or blocked, names the missing proof, and recommends a seam or tracer before autonomous agent edits.
Expected failure: The reviewer calls the boundary agent-safe because the module looks clean and the implementation is small.
Reproduce with: references/evals/eval.arch.agent-safe-boundary-without-regression-proof.md
