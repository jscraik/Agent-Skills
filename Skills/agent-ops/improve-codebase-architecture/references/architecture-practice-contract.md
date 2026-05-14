# Architecture Practice Contract

Use this when $improve-codebase-architecture needs more than entrypoint guidance. It turns architecture lenses from A Philosophy of Software Design, Five Lines of Code, Domain-Driven Design, Extreme Programming Explained, and The Pragmatic Programmer into repo-evidence checks.

Do not quote or import supplied books wholesale. Inspect only needed portions, treat them as heuristics, and ground every recommendation in current repo evidence.

## Complexity Triage

Name at least one symptom before recommending structure:

- change_amplification: one behavior change forces unrelated edits.
- cognitive_load: a maintainer must know too much hidden context.
- unknown_unknowns: the repo gives weak signals about what must be fresh or tested.
- information_leakage: private implementation facts leak through interfaces, config, docs, tests, or callers.
- shallow_abstraction: a wrapper renames or forwards without hiding behavior.
- temporal_coupling: callers must perform fragile ordered steps.
- language_drift: modules, docs, tests, or tickets use conflicting words for one concept.
- boundary_confusion: a module crosses bounded contexts or owns another domain's rule.
- decision_lock_in: a hard-to-reverse choice lacks proof, rollback, or a durable note.
- broken_window: repeated small defects have become background noise.

If no symptom is visible, ask for the missing surface or return a bounded observation.

## Architecture Lenses

- Deep module: make callers know less; hide coordination, defaulting, validation, and special cases behind the owner.
- Refactoring step: prefer behavior-preserving moves small enough for a targeted verifier; extract names only when they expose a real concept.
- Domain language: preserve ubiquitous language where it clarifies ownership; introduce bounded-context or anti-corruption language only from local evidence.
- XP cadence: intent, evidence, small move, feedback, learning.
- Pragmatic check: each rule has one owner, decisions are reversible or staged, and the decision surface is durable.

## Design It Twice

For non-trivial work, compare:

- patch_design: smallest local edit; cost; reversibility; risk.
- interface_design: deeper boundary or contract change; cost; reversibility; risk.
- choice: selected first move and why it reduces total cognitive load now.

The winner should make the next change easier, not just make the current diff smaller.

## Tracer Proof

Architecture recommendations need a thin route-to-output proof:

1. Identify the caller or workflow that exercises the boundary.
2. Use the smallest production-like path through real wiring.
3. Pair it with the narrowest test, validator, smoke command, or blocked reason.
4. Keep disposable prototypes separate from code meant to stay.
5. Stop if proof requires broad fixture invention before design is clear.

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
