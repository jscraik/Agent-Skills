# Source Parity Notes

## Table of Contents
- [Source input](#source-input)
- [Preserved behaviors](#preserved-behaviors)
- [Intentional modernizations](#intentional-modernizations)
- [Known constraints](#known-constraints)

## Source input
This package was synthesized from the supplied `ce:ideate` prompt that defines the ideation stage preceding `ce:brainstorm`.

Pinned donor snapshot:
- repo: `EveryInc/compound-engineering-plugin`
- commit: `847ce3f156a5cdf75667d9802e95d68e6b3c53a4`
- path: `plugins/compound-engineering/skills/ce-ideate/SKILL.md`

## Preserved behaviors
- `ce:ideate` explicitly precedes `ce:brainstorm`
- the stage boundary:
  - ideate what is worth exploring
  - brainstorm what one chosen idea should mean
  - plan how to build it
- optional focus hint handling:
  - concept
  - path
  - constraint
  - volume hint
- recent-ideation resume flow with:
  - continue versus start fresh
  - status preservation
  - session-log preservation
- issue-tracker intent detection distinct from simple bug focus
- combined intent parsing order:
  - issue-tracker intent first
  - volume override second
  - remaining text treated as the focus hint
- codebase scan before idea generation
- learnings search as part of grounding
- conditional issue intelligence for issue-grounded ideation
- issue-theme titles, descriptions, counts, and trend directions preserved when issue intelligence is available
- many-ideas -> critique -> survivors mechanism
- explicit push past the safe obvious layer before filtering
- ideation frames as starting biases rather than hard constraints
- orchestrator merge, dedupe, and cross-cutting synthesis
- focus weighting that still allows stronger adjacent ideas to survive
- adversarial filtering with explicit rejection reasons
- structured survivor presentation before handoff
- durable ideation artifact in `docs/ideation/`
- refinement routes:
  - add more ideas
  - re-evaluate
  - deepen one idea
- handoff to `ce-brainstorm`, not directly to planning or implementation

## Intentional modernizations
- tightened the stage boundary so `ce-ideate` does not drift into generic brainstorming, planning, or implementation
- kept runtime ideation repo-first and non-web-research by default, while still building the package itself against current OpenAI and Codex guidance
- preserved AGENTS-first shallow grounding while keeping the runtime fallback order portable: `AGENTS.md`, then `CLAUDE.md`, then `README.md`
- resolved the prompt's artifact-timing tension by preparing preservation-ready content early, presenting survivors as a checkpoint, then requiring the durable write before handoff, sharing, or session end
- preserved the issue-intelligence lane while making it portable:
  - use a dedicated helper if available
  - otherwise fall back to a bounded direct issue-theme pass
- moved volume rules, frame logic, rejection rubric, and artifact template into `references/` to keep `SKILL.md` below hard gating limits
- aligned routing and evals to current Codex skill guidance with realistic positive and negative trigger coverage
- selectively borrowed the strongest transferable quality mechanisms from `project-improver`:
  - candid anti-weak-idea posture
  - stronger value-versus-complexity filtering rubric
  - `quick win | high leverage | strategic bet` survivor bucketing
  - stronger rejection language around novelty theater and template traps

These were adopted because they strengthen ideation quality without changing the stage boundary. Premortems, hybrid plan revision, and direct implementation were intentionally not imported because they belong to later or broader workflows, not ideation-before-brainstorm.

## Known constraints
- the source prompt assumed platform-specific blocking question tools. This package preserves the one-question-at-a-time behavior, but exact question tooling remains harness-dependent.
- the source prompt referenced helper roles such as `issue-intelligence-analyst`. That helper is now installed in the canonical Codex config used by this workspace. This package still preserves a bounded direct fallback so the workflow remains portable in runtimes that do not have the helper installed.
- the source prompt mentioned Proof sharing but did not define the Proof transport itself. This package preserves the workflow hook and assumes the environment already has a standard markdown-sharing path for Proof.
