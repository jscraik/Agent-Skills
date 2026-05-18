# Skills SDK Apparatus Lens

Source status: user-provided excerpts from Hugo Venturini, "The apparatus, not the artifact" and "Treat Agent Output Like Compiler Output". This reference is not a web-verified citation. Use it as an internal design lens for Agent Skills Kit planning, review, and skill hardening.

## Mantra

Thin surface. Strong guardrails. Durable memory. Professional output.

This is the Skills SDK version of the apparatus argument. Keep the agent-facing surface small and easy to use. Put the trust in guardrails that verify the output. Preserve what the system learned so the same correction is not needed twice. Emit output that is structured, traceable, and honest about blocked or missing evidence.

## Core Thesis

Do not make trust live in the artifact an agent produced. Make trust live in the apparatus that constrains, validates, observes, and can roll back that artifact.

For Agent Skills Kit, the artifact is usually a SKILL.md file, a generated runtime projection, a package summary, a review note, or an agent-authored patch. The apparatus is the stack around it: typed command contracts, doctor/prove/eval checks, structural audits, package gates, runtime probes, lifecycle evidence, representativeness checks, closeout validation, and rollback evidence.

The model is stochastic. The Skill SDK pipe must be robust enough that stochastic output cannot silently become a release-readiness claim.

## How To Apply The Lens

Use this lens when a skill, SDK command, or planning artifact is being treated as ready because it looks coherent, has prose coverage, or passed one local check.

Ask these questions:

- What is the thin surface the agent or operator should use?
- Which guardrail signs off the claim: schema, test, eval, audit, probe, command, or closeout gate?
- Which durable memory should capture the learned rule so this failure does not recur?
- What makes the output professional: named status, blocker class, exact command, evidence path, next action, or rollback?
- Which claim is being made: source presence, structural validity, runtime reachability, package readiness, outcome proof, release readiness, or production safety?
- Which failure classes remain visible when another class blocks?
- Where does the system reject hallucinated or nonexistent references before a human reads the artifact?
- What counterexample, negative fixture, or representativeness probe would break an overfitted green result?

## Practical Enforcement Pattern

Use this pattern before asking an agent to write or change code from a spec, plan, or skill.

| Field | Purpose | Example |
| --- | --- | --- |
| Essential decisions | Decisions the agent must not invent or reinterpret. | Public API shape, status enum, error taxonomy, persistence model, security boundary, package ownership. |
| Fillable gaps | Low-risk code the agent may generate inside the locked boundaries. | Boilerplate adapters, repetitive mappings, straightforward tests, docs wiring, simple UI states. |
| Guardrails | Independent checks that prove the generated code stayed inside the boundary. | Type checks, schema validation, negative fixtures, doctor/prove/eval, focused tests, lint, structural audit. |
| Refusal triggers | Conditions where the agent must stop instead of filling the gap. | New public API decision, ambiguous data model, missing validator, risky migration, security/auth uncertainty. |
| Durable memory | Where the learned rule is recorded after failure or review feedback. | Steering uptake, eval artifact, reference lens, closeout note, test fixture, learned-fix doc. |
| Professional output | Evidence the agent must return before claiming done. | Files changed, exact commands, pass/fail, blocker class, warning class, next action, rollback. |

A practical spec should include this short contract:

~~~yaml
essential_decisions:
  - "Locked public result shape: data.skill_doctor.status is pass|warning|blocked."
fillable_gaps:
  - "Agent may add helper-level tests and fixture dictionaries inside the existing test file."
guardrails:
  - "python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q"
refusal_triggers:
  - "Stop if a public schema, migration, auth behavior, or runtime projection edit is required."
durable_memory:
  - "Record transferable feedback in the closeout artifact and update the reference lens or validator."
professional_output:
  - "Report exact command outcomes, readiness status, blockers, warnings, and rollback path."
~~~

This is how English intent becomes enforceable: the intent narrows the decision space, the fillable gaps declare where generation is allowed, and the guardrails reject drift.

## Code Enforcement Checklist

Before implementation, require all five answers:

1. What code decisions are locked?
2. What gaps may the agent fill?
3. What checks will fail if the agent guesses wrong?
4. What feedback becomes durable memory if this fails?
5. What professional output proves the work is done?

During review, reject the change if any of these are true:

- The agent invented an essential decision that was not delegated.
- Tests only cover the generated happy path.
- The same class of issue exists elsewhere in the touched boundary and was not swept.
- The result depends on prose, source presence, or AI review without command evidence.
- The closeout reports success without blocker/warning/skip/not-run distinctions.

## Skills SDK Mapping

| Mantra element | Skills SDK expression | Required posture |
| --- | --- | --- |
| Thin surface | handles, typed robot JSON, small CLI verbs, public result objects | Agents should use the smallest stable contract rather than parse internals or prose. |
| Strong guardrails | doctor/prove/eval, structural audit, schema validation, negative fixtures, status precedence, next_command rules | Missing handles, missing fields, wrong enum values, skipped critical checks, and placeholder schemas are contract failures, not review comments. |
| Durable memory | steering uptake, learnings, eval artifacts, closeout evidence, lifecycle traces, pattern-sweep disposition | High-signal feedback becomes a reusable rule with proof, not a one-line local patch. |
| Professional output | pass/warning/blocked semantics, exact command evidence, blocker classes, warnings, traceability, rollback | Output preserves uncertainty and evidence instead of smoothing it into green prose. |

## Apparatus Mapping

| Apparatus idea | Skills SDK expression | Required posture |
| --- | --- | --- |
| Type checking and name resolution | handle resolution, schema-versioned robot payloads, required fields, enum validation | Missing handles, missing fields, wrong enum values, and placeholder schemas are contract failures, not review comments. |
| Static analysis | structural audit, path ownership checks, projection drift checks, manifest/package checks | The audit must report exact blocker classes and source paths instead of smoothing findings into prose. |
| Counterexample testing | negative fixtures, skipped/not-run critical check tests, malformed payload cases, CTF-style evals | Green paths do not prove the contract until obvious counterexamples fail in the expected class. |
| Bounded model checking | representativeness probes across a second skill class, fixture matrices for pass/warning/blocked states | A single skill fixture is a proof point, not a general SDK guarantee. |
| CI gates | changed-file validation, closeout gates, review artifacts, live tracker traceability | The closeout must cite exact commands and classify blockers by ownership. |
| Runtime monitoring and rollback | lifecycle evidence, eval artifacts, event traces, rollback notes, supersession records | The apparatus should preserve what happened, what failed, and how to undo or supersede it. |

## Design Rules

- Treat AI review as advisory unless it is backed by command output, schema evidence, tests, evals, or a concrete artifact.
- Treat package readiness as distribution readiness, not outcome proof.
- Treat runtime reachability as adapter evidence, not proof that the skill delivers the requested outcome.
- Treat outcome proof as eval, proof, smoke, or artifact evidence, not as prose confidence.
- Treat skipped, not-run, missing, unavailable, or blocked checks as explicit readiness states. Do not fold them into pass.
- Preserve original failure classes when adding higher-level SDK layers. A layer label must help route ownership, not hide the actionable blocker.
- Prefer typed result objects and robot JSON contracts over terminal prose as the consumer surface.
- Require a bounded pattern sweep when feedback names a general rule through one local symptom.
- Require a representativeness probe before turning one fixture into SDK confidence.
- Keep rollback and supersession evidence attached to the claim being made.

## Review Prompts

Use these prompts as a persona-like lens during skill review:

- "What is the thin surface here, and is it small enough for agents to use reliably?"
- "What guardrail signs off this claim, and what artifact is merely being inspected?"
- "What durable memory records the rule this feedback points to?"
- "What makes this output professional rather than just polished?"
- "Could this pass because it is coherent prose rather than verified behavior?"
- "Which critical check could be skipped while the report still looks green?"
- "Does the next command fix the highest-priority blocker, or does it chase a lower-risk warning?"
- "What would a second skill class reveal about this fixture?"

## When Not To Use This Lens

Do not use this lens to justify broad verification theater. The goal is not to add every possible analyzer to every skill. The goal is to make the specific readiness claim resistant to known failure modes with the smallest credible apparatus.

For narrow docs-only work, this may mean a structural lint and source traceability check. For SDK command contracts, it usually means typed robot JSON assertions, negative fixtures, representativeness, changed-file validation, and closeout evidence.
