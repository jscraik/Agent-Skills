# Architecture Practice Contract

Use this when $improve-codebase-architecture needs more than entrypoint guidance. It turns architecture lenses from A Philosophy of Software Design, Five Lines of Code, Domain-Driven Design, Extreme Programming Explained, The Pragmatic Programmer, and agent-ready codebase research into repo-evidence checks.

Do not quote or import supplied books or research wholesale. Inspect only needed portions, treat them as heuristics, and ground every recommendation in current repo evidence.

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
- Agent work boundary: humans apply taste at public module interfaces; implementation work is safer inside the gray-box module only when boundary tests preserve behavior.
- Interface-as-contract: include invariants, ordering, error modes, required config, performance expectations, and test surface; do not reduce the interface to a type signature.
- Depth/leverage/locality: a deep module gives callers more behavior per concept learned and concentrates change, bugs, and verification in one place.
- Seam discipline: a seam is where behavior can vary without editing in place; one adapter is hypothetical, two adapters make the seam real.
- Dependency category: classify the candidate as in-process, local-substitutable, remote-but-owned, or true external before proposing ports, mocks, or adapters.
- Refactoring step: prefer behavior-preserving moves small enough for a targeted verifier; extract names only when they expose a real concept.
- Domain language: preserve ubiquitous language where it clarifies ownership; introduce bounded-context or anti-corruption language only from local evidence.
- XP cadence: intent, evidence, small move, feedback, learning.
- Agent-readiness check: keep hot-path context thin, make file/module structure navigable to a new agent, and back deepened interfaces with fast feedback.
- Pragmatic check: each rule has one owner, decisions are reversible or staged, and the decision surface is durable.

## Agent-Safe Boundary Classification

Classify each candidate boundary before recommending implementation work:

- safe: stable public interface, behavior hidden behind the module, seam/regression tests or executable checks cover the caller-observable contract, and the edit stays mostly inside one owner layer.
- risky: interface is plausible but tests are weak, callers depend on hidden behavior, imports route around the public surface, or file/folder/layer shape does not match the mental map.
- blocked: no public interface, no tracer path, unknown callers, missing test command, or unresolved ownership.

Deep modules are useful agent work areas only when both halves exist: simple
public interface plus executable seam proof. Without tests, depth can hide
change risk from both humans and agents.

When useful, map the local architecture as layers with explicit cross-cutting
boundaries, for example: types/config/repo, providers, service/domain logic,
runtime/app wiring, UI, and utilities. Name which layer owns the rule, which
layers depend on it, and which dependencies cross through adapters.

## Design It Twice

For non-trivial work, compare:

- patch_design: smallest local edit; cost; reversibility; risk.
- interface_design: deeper boundary or contract change; cost; reversibility; risk.
- choice: selected first move and why it reduces total cognitive load now.

The winner should make the next change easier, not just make the current diff smaller.

Use references/deepening-workflow.md when the user asks for deepening
opportunities, architecture search, candidate exploration, or grilling before
implementation.

## Collaboration Gate

Design decisions are shared operator choices, not autonomous agent taste calls.
Use request_user_input before selecting or applying the design path when the
choice would change any of these surfaces:

- public or semi-public interfaces, seams, adapters, dependency injection, or module ownership.
- durable terminology, context/glossary files, ADRs, Linear decisions, or repo-approved decision records.
- validation strategy, test seam, tracer proof, or rollback path for a deepening move.
- any broad refactor, cross-module move, external write, or choice that would make future agents inherit the decision.

The question should present 2-3 concrete choices, put the recommended option
first, and explain the tradeoff in plain language. If the tool is unavailable,
return the normal output contract with request_user_input: blocked and name
the exact design decision that must be made together.

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
- capability_surface
- complexity_symptoms
- fresh_evidence and missing_evidence
- reviewer_coverage
- agent_safe_boundary with status, public_interface, seam_tests, blast_radius, and blocker
- patch_design and interface_design
- request_user_input checkpoint and selected_design_decision
- recommended_first_move with risk, reversibility, and rollback
- tracer_proof with path, verifier, and status
- decision_surface with location, write_status, and blocker
- validation outcomes
- confidence and open questions
