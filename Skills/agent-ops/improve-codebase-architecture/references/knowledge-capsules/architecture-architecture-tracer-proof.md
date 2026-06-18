# Architecture Tracer Proof

Prove an architecture recommendation through one realistic caller or workflow and state exactly what uncertainty remains.

Pack id: pack.codebase-architecture
Facet id: architecture_tracer_proof
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.arch.architecture-change-needs-tracer-proof: Architecture Change Needs Tracer Proof

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

An architecture recommendation should include a thin tracer proof that exercises one realistic caller or workflow and reduces the most important uncertainty.

Interpretation notes:
- This claim supports the improve-codebase-architecture tracer_proof output.
- It should state what the proof does and does not establish.

### claim.arch.agent-safe-boundaries-need-seams: Agent-Safe Boundaries Need Seams

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

A code boundary is safe for delegated agent work only when the public interface hides coordination complexity and behavior is protected by a seam, characterization test, or equivalent regression proof.

Interpretation notes:
- This claim supports classifying architecture boundaries as safe, risky, or blocked.
- It should be applied only after checking local callers, public interfaces, and test evidence.

### claim.arch.deep-modules-hide-coordination: Deep Modules Hide Coordination

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

A module is architecturally valuable when its interface is simpler than its implementation and when it reduces caller knowledge, coordination burden, and change amplification.

Interpretation notes:
- This claim supports rejecting shallow wrappers that do not hide behavior.
- It should be tested against caller simplification, not directory layout alone.

## Principles

### principle.arch.evidence-backed-boundary-decisions: Evidence-Backed Boundary Decisions

- Type: principle
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.arch.agent-safe-boundaries-need-seams, claim.arch.deep-modules-hide-coordination, claim.arch.architecture-change-needs-tracer-proof

Treat architecture work as a boundary decision that must cite local evidence, hide real complexity, and name the smallest tracer proof before claiming safety.

Rationale: Codebase architecture advice becomes agent-useful only when it separates interface stability, hidden complexity, caller impact, validation evidence, and remaining uncertainty.

Application notes:
- Use this principle to connect the pack's checklists, rubrics, lens, heuristic, anti-pattern, and eval scenarios.
- Do not cite this principle as proof that a concrete repo boundary is safe; require local interface, caller, and validation evidence.
- Keep export smoke proof separate from lifecycle validation and runtime availability.

## Checklists

### checklist.arch.architecture-tracer-proof: Architecture Tracer Proof Checklist

- Type: checklist
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.arch.architecture-change-needs-tracer-proof

- [ ] Name the production-like caller, workflow, or command the tracer represents.
- [ ] State the architecture claim the tracer is meant to reduce uncertainty about.
- [ ] Include one representative input, one expected behavior, and one expected failure.
- [ ] Use the narrowest verifier that exercises the boundary rather than only static shape.
- [ ] Record exact command, artifact, fixture, or trace evidence.
- [ ] State what the tracer proves and what it does not prove.
- [ ] Stop or downgrade confidence when the tracer cannot run.
