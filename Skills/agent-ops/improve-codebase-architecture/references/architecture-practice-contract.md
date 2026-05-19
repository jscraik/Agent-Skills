# Architecture Practice Contract

Use this when $improve-codebase-architecture needs more than entrypoint guidance. Treat architecture literature as heuristics only; ground every recommendation in current repo evidence.

## Complexity Triage

Name at least one symptom before recommending structure:

- change_amplification: one behavior change forces unrelated edits.
- cognitive_load: maintainers must know hidden context.
- unknown_unknowns: weak signals about what must be fresh or tested.
- information_leakage: implementation facts leak through interfaces, config, docs, tests, or callers.
- shallow_abstraction: a wrapper renames or forwards without hiding behavior.
- temporal_coupling: callers must perform fragile ordered steps.
- language_drift: conflicting words for one concept.
- boundary_confusion: a module crosses bounded contexts or owns another domain's rule.
- decision_lock_in: a hard-to-reverse choice lacks proof, rollback, or durable note.
- broken_window: repeated small defects have become background noise.

If no symptom is visible, ask for the missing surface or return a bounded observation.

## Architecture Lenses

- Deep module: make callers know less; hide coordination, defaults, validation, and special cases behind the owner.
- Refactoring step: prefer behavior-preserving moves small enough for a targeted verifier.
- Domain language: preserve local ubiquitous language and bounded contexts from evidence.
- XP cadence: intent, evidence, small move, feedback, learning.
- Pragmatic check: one owner per rule, staged decisions, durable decision surface.

## Design It Twice

For non-trivial work, compare:

- patch_design: smallest local edit; cost; reversibility; risk.
- interface_design: deeper boundary or contract change; cost; reversibility; risk.
- choice: selected first move and why it reduces total cognitive load now.

The winner should make the next change easier, not just make the current diff smaller.

## Tracer Proof

Architecture recommendations need a thin route-to-output proof:

Identify the caller/workflow, smallest production-like path, narrowest verifier or blocked reason, and whether proof would require broad fixture invention before design is clear.

## Output Shape

Return:

- schema_version
- complexity_symptoms
- fresh_evidence and missing_evidence
- patch_design and interface_design
- recommended_first_move with risk, reversibility, and rollback
- tracer_proof with path, verifier, and status
- decision_surface
- validation outcomes
- confidence and open questions
