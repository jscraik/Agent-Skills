# DevRel Hack Coach: Track-Aware Selection

Asset id: candidate.devcon-hack-coach.track-aware-selection

Use when a hack idea could fit multiple tracks or needs a judging frame.

## Core Thesis

Track selection is a positioning decision, not a label. The coach should choose
the judging frame that makes the idea easiest to evaluate, then shape the
problem, demo, and pitch around that frame.

## Principles

### One Track Sharpens The Story

Multi-track positioning usually weakens the pitch. One judging frame lets the
user choose examples, metrics, and Q&A that match evaluator expectations.

### The User Can Veto, But The Trade-Off Must Be Named

Offer a reasoned track recommendation and let the user veto it. If they switch,
state what changes about the pitch and success criteria.

### Weak Fit Means Weak Ideation

If no track fits cleanly, the idea probably needs a sharper user pain or wedge
before spec work starts.

## Guidance

- Pick one judging track whose evaluators will care most.
- Frame every idea angle around that track's concern.
- Avoid multi-track positioning because it weakens the pitch.
- Let the user veto the chosen track after a short reason.

## Decision Rules

- If the idea fits multiple tracks, choose the track with the clearest judge
  value and name the trade-off.
- If the user vetoes the track, choose the next strongest track and reframe the
  pitch accordingly.
- If no track clearly fits, return to ideation and sharpen the user pain.
- If the pitch uses multi-track language, rewrite it around the selected track.

## Output Shape

- Return: selected track, why this track, rejected alternatives, judging frame,
  and veto question.
- Keep the judging frame to one sentence.
- Include the pitch implication of the track choice.

## Examples

- Developer tooling track: emphasize workflow friction, repo evidence, and
  validation.
- AI track: emphasize model-assisted behavior, boundaries, and verification.
- Social impact track: emphasize affected user, access barrier, and measurable
  improvement.

## Recovery

- If track choice stalls, pick the track with the strongest demo proof rather
  than the broadest possible relevance.
- If the selected track weakens the story, return to the idea card and update
  the wedge.
- If the user wants all tracks, explain that a single judging frame improves
  clarity under time pressure.

## Validation Ideas

- Given an ambiguous itch, choose one track with a reason and veto option.
- Given a multi-track pitch, cut it to the strongest judging frame.

## Boundaries

- This capsule depends on the observed DevCon-style track taxonomy.
- Remap it before using it for a different hackathon.
- Do not require KnowledgeOS at runtime.
