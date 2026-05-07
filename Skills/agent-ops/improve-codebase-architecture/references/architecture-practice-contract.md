# Architecture Practice Contract

Use this reference when `$improve-codebase-architecture` needs more than a surface review. It translates practical design lessons from *A Philosophy of Software Design*, *Extreme Programming Explained*, and *The Pragmatic Programmer* into an agent-native architecture workflow.

## Complexity Triage

Name at least one complexity symptom before recommending a structural change:

- `change_amplification`: one behavior change forces edits across unrelated files.
- `cognitive_load`: the next maintainer must know too much hidden context to make a safe change.
- `unknown_unknowns`: the repo gives no clear signal about what must be fresh or tested before action.
- `information_leakage`: private implementation facts leak through interfaces, config, docs, tests, or caller responsibilities.
- `shallow_abstraction`: the abstraction mostly forwards calls or renames concepts without hiding meaningful behavior.
- `temporal_coupling`: callers must perform steps in a fragile order that the module could own.
- `decision_lock_in`: a hard-to-reverse choice is being made without a tracer proof, rollback path, or durable decision note.
- `broken_window`: repeated small defects, review comments, or awkward workarounds have become accepted background noise.

If no symptom is visible in live evidence, return a bounded observation or ask for the missing surface instead of inventing an architecture problem.

## Deep Module Checks

Prefer changes that make callers know less:

- Push hard coordination, validation, defaulting, and special-case handling down behind the owning module boundary.
- Keep interfaces smaller than their implementations whenever the module can hide real behavior.
- Separate layers by abstraction, not by file size or ceremony.
- Remove pass-through functions, pass-through variables, and duplicate ownership unless they add a distinct policy boundary.
- Define errors and special cases out of existence when a better interface can make invalid states unrepresentable.
- Use precise shared language so names carry design intent instead of requiring side-channel explanation.

## Design It Twice

For non-trivial architecture work, sketch two options before choosing:

```yaml
design_options:
  patch_design:
    summary: "smallest local edit"
    cost: low|medium|high
    reversibility: easy|managed|hard
  interface_design:
    summary: "deeper boundary or contract change"
    cost: low|medium|high
    reversibility: easy|managed|hard
  choice:
    selected: patch_design|interface_design
    reason: "why this reduces total cognitive load now"
```

The winning option should make the next change easier, not just make the current diff smaller.

## Tracer Proof

Architecture recommendations need a thin route-to-output proof:

1. Identify the caller or workflow that will exercise the new boundary.
2. Include the smallest production-like path through real wiring.
3. Pair the path with the narrowest test, validator, smoke command, or blocked reason.
4. Keep disposable prototypes separate from tracer code that is meant to stay.
5. Stop if the proof requires broad fixture invention before the design is clear.

## XP Change Cadence

Use a small feedback loop:

1. Intent: what user, maintainer, or agent pain is being reduced.
2. Evidence: files, callers, tests, docs, and tracker state read fresh.
3. Small move: the smallest behavior-preserving change that improves the boundary.
4. Feedback: exact validation command or explicit blocker.
5. Learning: update context language, evals, tests, or tracker notes when the same issue will recur.

Do not optimize for minimum design. Optimize for design investment in proportion to current evidence and future change pressure.

## Pragmatic Decision Checks

Before closeout, answer these checks when relevant:

- `orthogonality`: can this change vary independently from adjacent policies?
- `dry_ownership`: is each rule owned in one canonical surface?
- `contract`: what does the new boundary require, guarantee, refuse, and report when blocked?
- `reversibility`: can the decision be undone or staged without data loss or broad rewrites?
- `blackboard`: which durable surface carries the decision, validation, and next-reader state?
- `broken_window`: did the change remove a repeated local irritation or merely route around it?

## Output Shape

For deep-dive reviews, prefer this compact shape:

```yaml
schema_version: 1
complexity_symptoms: []
evidence:
  fresh: []
  missing: []
design_options:
  patch_design: {}
  interface_design: {}
recommended_first_move:
  summary: ""
  why_now: ""
  reversibility: easy|managed|hard
tracer_proof:
  path: ""
  verifier: ""
  status: pass|fail|blocked|not_run
decision_surface:
  linear_or_repo_note: ""
  status: needed|not_needed|blocked
validation:
  commands: []
  outcomes: []
```

Keep the final recommendation short enough to act on immediately. Preserve larger rationale here, in tests, or in the repo's durable decision surface rather than bloating the skill entrypoint.
