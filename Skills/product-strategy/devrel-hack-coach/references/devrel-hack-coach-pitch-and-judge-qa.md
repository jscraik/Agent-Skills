# DevRel Hack Coach: Pitch And Judge Q&A

Asset id: candidate.devcon-hack-coach.pitch-qa

Use when the user has a spec and needs a judge-ready demo pitch.

## Core Thesis

A hackathon pitch should make the judge understand the pain, believe the live
demo, and trust the boundaries quickly. The coach improves the pitch by cutting
generic trend language and preparing skeptical answers that stay inside the
prototype's actual evidence.

## Principles

### The Pitch Serves The Spec

The pitch should not invent a different product than the locked spec. If the
demo moment changes, reconcile the spec before polishing the story.

### Skepticism Is Expected

Judges will ask about scale, alternatives, reliability, users, and defensibility.
Prepare bounded answers instead of trying to hide unfinished work.

### Claims Need A Visible Anchor

Every claim in the pitch should be shown, measured, bounded, or removed. A
five-minute pitch cannot carry unsupported platform ambition.

## Guidance

- Compress the story into pain, built move, live moment, and skeptical answers.
- Use one concrete wedge instead of generic trend language.
- Make the live demo match the spec's demo moment.
- Prepare one-line answers for scale, alternatives, hallucination, buyer, and
  moat questions.

## Decision Rules

- If the pitch does not name a user pain in the first beat, rewrite the opening.
- If the demo moment differs from the locked spec, reconcile the spec before
  writing the pitch.
- If the answer to a judge question depends on unbuilt work, mark it as future
  work and return to evidence from the demo.
- If a claim cannot be shown, measured, or bounded, remove it from the pitch.

## Output Shape

- Produce a pitch with: pain, insight, solution, live demo cue, evidence
  boundary, why-now, and close.
- Produce Q&A rows with question, short answer, proof boundary, and risk.
- Keep answers concise enough to speak without reading.

## Examples

- Scale answer: "The hack proves the workflow on one repo path; scaling requires
  indexing and permission work that is outside this build."
- Alternative answer: "The difference from a generic chat interface is the
  evidence-bound task map and explicit validation step."
- Hallucination answer: "The assistant must cite file evidence and the user
  verifies the generated action before using it."

## Recovery

- If the pitch becomes a feature list, rewrite around before, live moment, and
  after.
- If judge Q&A reveals a weak moat, answer with workflow specificity, evidence,
  and next proof rather than grand defensibility.
- If the user wants to hide mocked work, refuse and add a transparent boundary
  line.

## Validation Ideas

- Given a pitch over the word limit, compress before closeout.
- Given a demo moment that differs from the spec, reconcile the spec and pitch.

## Boundaries

- This capsule supports pitch structure and risk checks, not judge preference
  certainty.
- Do not require KnowledgeOS at runtime.
