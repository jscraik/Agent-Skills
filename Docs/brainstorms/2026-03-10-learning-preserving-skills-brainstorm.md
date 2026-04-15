---
title: Learning-Preserving Skill Design Pilot
date: 2026-03-10
status: draft
spec_required: lite
risk_level: medium
complexity: medium
---

# Learning-Preserving Skill Design Pilot

## What We're Building

We are defining a pilot improvement for `agent-skills` that makes selected skills better at preserving human oversight and learning, not just finishing the task quickly.

The pilot should add a lightweight, explicit contract for learning-preserving interaction patterns across a small set of high-impact skills, starting with a few skills that already shape repo standards or high-autonomy workflows.

Recommended pilot set:
- `Skills/skill-builder`
- `frontend/tools/agentation`
- one debugging-heavy coding skill
- one interview or teaching-oriented skill

## Why It Matters

Current skill quality in this repo is strong on routing clarity, validation, promotion gates, and human oversight, but it is still mostly optimized around artifact quality and task completion.

That creates a gap: a skill can be operationally successful while still encouraging interaction patterns that weaken the human's ability to supervise the model later.

This idea also fits the repo's existing direction. The current skill graph, promotion, and task-profile materials already favor bounded autonomy, human-gated promotion, and `co-pilot` defaults, so this pilot extends an existing pattern instead of introducing a conflicting philosophy.

This pilot is motivated by January 2026 research from Anthropic showing that AI-assisted users learned a new library worse on debugging, code reading, and conceptual understanding, even when task completion was assisted. The same work suggested the better interaction patterns were conceptual inquiry, hybrid code-plus-explanation, and generation-then-comprehension, while full delegation was fastest but weakest for learning. Sources:
- [Anthropic research paper, January 2026](https://arxiv.org/abs/2601.20245)
- [Anthropic writeup, 2026](https://www.anthropic.com/research/AI-assistance-coding-skills)

## Problem Statement

The repo currently lacks an explicit way to distinguish:
- skills that maximize throughput
- skills that preserve learning and supervisory capability
- skills that should do both, depending on context

Without that distinction, high-quality skills can still push users toward over-delegation, weak debugging habits, and lower conceptual understanding in unfamiliar domains.

## Resolved Questions

- **Initial scope:** Start with a pilot subset, not a repo-wide mandate.
- **Rollout posture:** Improve a few high-leverage skills first, then expand based on evidence.
- **Migration constraint:** Preserve existing canonical runtime mode vocabulary (`autopilot | co-pilot | manual`) instead of replacing it outright.
- **Compatibility stance:** Build on the repo's existing bounded-autonomy and human-gated promotion model rather than introducing a separate control framework.

## Options Considered

### Option 1: Pilot a separate learning-posture layer on top of existing skill contracts

Add a small, reusable "Learning Posture" contract to a pilot set of skills and related evaluation artifacts. Keep runtime delegation modes as they are, and add a second dimension that describes how the skill should balance explanation, prediction, generation, and review.

Pros:
- Fits existing repo contracts and avoids rewriting current mode vocabulary.
- Small enough to test quickly on real skills.
- Lets the repo compare throughput-oriented and learning-preserving behavior explicitly.
- Works well with existing human-gated promotion and telemetry workflows.

Cons:
- Introduces another dimension to document and evaluate.
- Some temporary inconsistency is likely while only part of the repo adopts it.

Best fit:
- A controlled pilot that aims to prove value before broader standardization.

### Option 2: Eval-first instrumentation with no skill-contract changes yet

Leave skill prompts mostly unchanged and only extend evals, task profiles, and telemetry to measure learning-preserving behavior.

Pros:
- Lowest disruption.
- Useful if the main goal is diagnosis before design changes.
- Gives baseline data before touching many skills.

Cons:
- Weakest direct effect on actual skill behavior.
- Risks measuring a problem without improving it.
- Harder for authors to act consistently without prompt-level guidance.

Best fit:
- A repo that wants evidence first and is not ready to change skill scaffolds yet.

### Option 3: Repo-wide mode overhaul

Reframe the whole repo around new top-level modes such as `learn`, `co-pilot`, and `execute`, and update skills, profiles, docs, and evals across the board.

Pros:
- Most consistent long-term model.
- Makes the distinction between learning and delegation explicit everywhere.

Cons:
- High migration cost.
- Conflicts with current canonical mode vocabulary and onboarding artifacts.
- Too large for a first move and likely to blur brainstorm scope into implementation planning.

Best fit:
- A later standardization phase, only after a pilot proves the contract is worth adopting.

## Chosen Approach

Choose **Option 1: Pilot a separate learning-posture layer**.

This is the smallest approach that meaningfully changes behavior without destabilizing existing repo contracts.

The key idea is to add a new dimension that is orthogonal to runtime delegation mode:
- **delegation/runtime mode:** `autopilot | co-pilot | manual`
- **learning posture:** something like `learn | guided | execute`

That lets the repo preserve current recursive-skill-loop and promotion vocabulary while still teaching skills when to:
- ask for prediction before generation
- explain before patching in unfamiliar domains
- prefer diagnosis before AI-led debugging
- require explain-back or review after generated code
- warn when high-autonomy execution is optimizing for throughput rather than learning

## Recommended Approach

Start with a pilot contract that includes four pieces:

1. A reusable `Learning Posture` block for selected `SKILL.md` files.
2. A matching extension to pilot `Infrastructure/references/task-profile.json` and/or evaluation metadata.
3. Pilot eval cases that measure explanation, code-reading, debugging independence, and delegation risk alongside existing quality criteria.
4. Pilot telemetry tags that distinguish interaction patterns such as conceptual inquiry, hybrid explanation, full delegation, and AI-led debugging.

Recommended placement:
- repo-level definition in `docs/skill-graphs/index.md`
- contributor-facing summary in `README.md`
- pilot propagation through `Infrastructure/templates/SKILL.md.template` and selected pilot skills

## Key Decisions

- **Do not replace existing runtime mode vocabulary.**
  Add learning-preserving posture as a second layer instead.

- **Treat this as a product-quality improvement for skills, not just a documentation change.**
  The pilot should affect prompts, evals, and telemetry together.

- **Bias the pilot toward high-leverage skills.**
  Include one standards-setting skill, one high-autonomy execution skill, and one or two skills where explanation and diagnosis matter heavily.

- **Prefer behavior-shaping guidance over long philosophy sections.**
  The contract should encode practical patterns such as prediction checkpoints and explain-before-patch, not just ideals.

- **Define the concept once, then propagate it.**
  Put the repo-level contract in `docs/skill-graphs/index.md`, summarize it in `README.md`, and use the skill template plus pilot skills for adoption.

- **Keep the pilot human-gated.**
  Do not auto-promote repo-wide standards from this pilot without evidence from evals and real usage.

## Scope Boundaries

In scope:
- defining the pilot goal and repo-level contract shape
- choosing the pilot rollout posture
- deciding how this should relate to existing delegation/runtime modes
- identifying the kinds of evaluation and telemetry changes needed

Out of scope:
- detailed implementation sequencing
- exact file-level schema changes
- full repo-wide migration
- replacing existing skill-graph mode vocabulary
- redesigning the entire recursive skill loop

## Constraints / Non-Goals

- Do not turn every skill into a teaching tool.
- Do not degrade execution-first skills that are intentionally optimized for throughput.
- Do not create a repo-wide migration burden before the pilot proves value.
- Do not measure only output quality; the pilot needs some signal for preserved human understanding.
- Do not collapse learning posture into existing runtime mode fields if that muddies current contracts.

## Success Criteria

The pilot is successful if:
- pilot skills gain a clear, reusable learning-preserving contract
- the contract fits current repo structures without breaking canonical mode vocabulary
- skill authors can tell when to use learning-preserving behavior versus execution-first behavior
- pilot evals can distinguish at least some learning-preserving patterns from pure delegation
- the resulting proposal is concrete enough to guide a spec without reopening the core problem definition

## Open Questions

- Which exact pilot skills beyond `skill-builder` and `agentation` should be included first?
- Should pilot evaluation tooling read the learning-posture contract from `SKILL.md`, `Infrastructure/references/task-profile.json`, or both?
- What is the minimum telemetry needed to compare learning-preserving patterns without adding heavy runtime overhead?

## Recommended Next Step

Proceed to a **lite spec** before planning.

The spec should define:
- the learning-posture vocabulary
- how it relates to existing delegation/runtime modes
- the pilot skill set
- what new eval dimensions are required
- which telemetry signals are useful enough to collect in the pilot

## Recommendation Summary

- `spec_required: lite`
- `risk_level: medium`
- `complexity: medium`

This is medium complexity because it spans skill scaffolds, evals, and telemetry, but it does not yet require a repo-wide migration or new runtime system. A lite spec is the right next artifact because the idea is clear, the pilot shape is clear, and the remaining questions are mostly contract-definition questions rather than open-ended product ambiguity.
