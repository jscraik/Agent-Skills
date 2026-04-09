# Document Review Pass

Read when: a brainstorm-produced requirements document mostly needs refinement before spec or planning rather than deeper contract expansion.

Imported from the upstream `ce-brainstorm` workflow in `EveryInc/compound-engineering-plugin` commit `847ce3f156a5cdf75667d9802e95d68e6b3c53a4`, adapted for local `ce-brainstorm`.

## Purpose

Improve requirements documents through a lightweight structured review.

Use this pass when the document already exists and the main question is:
- is it clear enough?
- is it specific enough for the next stage?
- is it carrying unnecessary ambiguity or bulk?

## Review flow

### 1. Get the document

If a document path is provided, read it.

If no document is specified, ask for the target file or look for the most recent relevant file under `docs/brainstorms/`, preferring `*-requirements.md` and falling back to legacy `*-brainstorm.md` when needed.

### 2. Assess before fixing

Read the document and ask:
- What is unclear?
- What is unnecessary?
- What decision is being avoided?
- What assumptions are unstated?
- Where could scope accidentally expand?
- Would planning still have to invent behavior, boundaries, or success criteria?

Do not fix yet. Note the issues first.

### 3. Evaluate the document

Score the document against:
- Clarity: the problem frame is clear and vague language is minimized.
- Completeness: required sections are present and open questions are clearly marked as blocking or deferred.
- Specificity: the requirements are concrete enough for the next stage.
- Appropriate level: the document stays at product-definition level and does not drift into implementation detail without reason.
- YAGNI: speculative complexity is removed when its carrying cost outweighs its value.
- User-intent fidelity: the document still reflects the discussed intent and validated assumptions.

### 4. Identify the critical improvement

If one issue would materially improve the document more than the others, highlight it as the must-address item.

### 5. Make changes

Rules:
- auto-fix minor issues such as vague wording, formatting, or small structure cleanups
- ask approval before substantive restructuring, removing sections, or changing meaning
- update the document inline
- do not create separate review files or metadata blocks

### 6. Offer next action

After changes:
1. refine again
2. review complete

After two refinement passes, recommend completion unless the user explicitly wants another round.

## Simplification guidance

Simplification means purposeful removal of unnecessary complexity, not shortening for its own sake.

Simplify when:
- content serves hypothetical future needs without enough current value
- sections repeat information already covered elsewhere
- detail exceeds what is needed to move into spec or planning
- abstractions or structure add overhead without clarity

Do not simplify away:
- constraints or edge cases that affect the next stage
- rationale for rejected alternatives
- open questions that still need resolution
- intentionally deferred technical or research questions the next stage needs to carry forward

Also remove when inappropriate:
- implementation details that do not belong in a non-implementation requirements document

## What not to do

- do not rewrite the entire document
- do not add new requirements the user did not discuss
- do not over-engineer or add complexity
- do not create separate review artifacts
