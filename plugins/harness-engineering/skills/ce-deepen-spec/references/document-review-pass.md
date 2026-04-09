# Document Review Pass

Read when: an existing requirements document, system spec, or UI spec mostly needs refinement before planning rather than deeper contract expansion.

Imported from the upstream `document-review` skill in `EveryInc/compound-engineering-plugin` commit `0ae91dcc298721e5b2c4ab6d1fc6f76a13b6f67c`, adapted for `ce-deepen-spec`.

## Purpose

Improve requirements or spec documents through a lightweight structured review.

Use this pass when the document already exists and the main question is:
- is it clear enough?
- is it specific enough for the next step?
- is it carrying unnecessary ambiguity or bulk?

## Review flow

### 1. Get the document

If a document path is provided, read it.

If no document is specified, ask for the target file or look for the most recent relevant file under `docs/specs/` or `docs/ui-specs/`.

### 2. Assess before fixing

Read the document and ask:
- What is unclear?
- What is unnecessary?
- What decision is being avoided?
- What assumptions are unstated?
- Where could scope accidentally expand?

Do not fix yet. Note the issues first.

### 3. Evaluate the document

Score the document against:
- Clarity: the problem statement is clear and vague language is minimized.
- Completeness: required sections are present and open questions are clearly marked as blocking or deferred.
- Specificity: the document is concrete enough for the next step.
- Appropriate level: a requirements or spec document stays at the right contract level and does not drift into implementation without reason.
- YAGNI: speculative complexity is removed when its carrying cost outweighs its value.
- User-intent fidelity: the document still reflects the actual discussed intent and validated assumptions.

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
- detail exceeds what is needed to move into planning
- abstractions or structure add overhead without clarity

Do not simplify away:
- constraints or edge cases that affect implementation
- rationale for rejected alternatives
- open questions that still need resolution
- intentionally deferred technical or research questions that the next stage needs to carry forward

Also remove when inappropriate:
- implementation details that do not belong in a non-implementation requirements/spec document

## What not to do

- do not rewrite the entire document
- do not add new requirements the user did not discuss
- do not over-engineer or add complexity
- do not create separate review artifacts
