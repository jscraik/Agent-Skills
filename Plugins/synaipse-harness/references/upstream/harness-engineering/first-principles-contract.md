# First Principles Contract

Harness Engineering exists to preserve intent through execution. Do not add
process, artifacts, Linear work, skill routing, evals, or governance because
serious systems usually have them. Add or preserve them only when they prevent a
verified HE failure, reduce drift, improve proof, or make future-agent reasoning
cheaper.

## Load When

- A stage would copy a pattern from another plugin, process, book, or prior
  workflow.
- A recommendation adds a new artifact, stage, skill, eval, Linear object,
  governance rule, or lifecycle gate.
- Multiple plausible routes exist and one route would shape downstream scope.
- A strategy, refactor, Linear plan, eval, or review could reward sophistication
  instead of evidence-backed leverage.
- Headless or autonomous mode would normally ask a clarification question.

## Required Check

Record the check compactly in the stage output when it changes routing, scope,
or closure confidence.

```yaml
first_principles_check:
  verified_failure: ""
  fundamental_constraint: ""
  assumption_being_challenged: ""
  smallest_effective_mechanism: ""
  analogy_or_template_rejected: ""
  proof_required: ""
  context_load_effect: reduced|neutral|increased|unknown
  routing_effect: clearer|neutral|worse|unknown
  decision_type: Type 1|Type 2
  outcome: proceed|ask|defer|reject|delete_or_collapse
```

## Decision Rules

- If the reason is "good systems usually have this", reject or defer.
- If the failure is real, repeated, high-risk, or moat-critical, look for the
  smallest proof-producing mechanism before adding a new surface.
- If the decision is irreversible, architecture-shaping, closure-sensitive, or
  expensive to unwind, treat it as Type 1 and require stronger proof.
- If the decision is reversible, local, low-risk, and easy to validate, treat it
  as Type 2 and prefer a fast feedback slice.
- If an eval can catch the failure, prefer eval coverage over new process.
- If routing can solve the failure, prefer routing clarity over another skill.
- If a reference contract can solve the failure, prefer the reference over a new
  stage or standalone skill.
- If the mechanism increases context load, it must provide matching proof,
  routing clarity, or drift reduction.

## Headless Mode

When user input is unavailable, do not ask optional questions. Record:

- the assumption selected
- why it is the smallest safe assumption
- the confidence level
- what evidence would overturn it
- the recovery path if the assumption is wrong

Blocking questions remain blocking when the wrong answer could create
irreversible work, external mutation, unsafe closure, or broad scope expansion.

## Lifecycle Hooks

- Brainstorm: survivor ideas must prevent a real failure or reduce ambiguity;
  copied patterns without HE-specific evidence become `Do Not Create`.
- Spec: requirements must name the verified failure, smallest mechanism,
  assumptions, and proof needed before implementation.
- Plan: implementation units should prove the smallest useful slice first and
  defer broad migrations until evidence warrants them.
- Strategy: compress to irreducible core, actual moat, false moat signals,
  deletion candidates, and safe rewrite zones.
- Linear plan: Linear is execution state, not cognition storage; create only the
  smallest active tracked work needed for execution.
- Eval report: closure depends on whether the change solved the original
  verified failure with evidence, not whether implementation status looks done.
- Code review: flag false sophistication, shallow abstraction, or process growth
  that lacks verified-failure and proof impact.

## Anti-Patterns

- Adding a skill because another plugin has one.
- Creating Linear objects for every observation.
- Treating artifact count, routing metadata, or process detail as proof.
- Preserving complexity because it looks mature.
- Expanding prompt/context size without eval or routing improvement.
- Replacing a small validation gate with a large governance layer.
