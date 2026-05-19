# Hot-Path Folded Context

## Purpose
Preserve detailed context folded out of SKILL.md so the active he-improve entrypoint stays below the hot-path soft budget without losing usable guidance.

## 2026-05-15 Soft-Warning Cleanup

Disposition:
- moved-to-reference: bulky examples, extended output fields, repeated evidence detail, and long procedure tails.
- superseded: repeated headings whose active entrypoint now points to shared contracts.
- intentionally-discarded: none in this file; prompt rot is tracked in shared folded context when removed.

## Folded Philosophy

Improve with evidence, not vibes. This skill hardens one existing Harness
Engineering skill, reference, contract, eval suite, or shared workflow surface
from concrete findings while preserving useful context in references and making
the stop rule explicit. Higher-priority instructions, command boundaries, and
local `AGENTS.md` guidance remain binding.

## Folded When Not to Use

Do not use for speculative redesign, greenfield skill creation, broad portfolio
reorganization, runtime install/sync work, or unrelated product implementation.
Do not mutate generated runtime projections, user/global config, external
trackers, production systems, or package mirrors without explicit approval and
the proper owner workflow.

## Folded Procedure

1. Before proposing a new skill or surface, inspect existing owners and choose
   one canonical target.
2. Compare current behavior against the evidence and name the smallest gap that
   matters operationally.
3. Patch one failure class at a time; move bulky detail to references instead of
   deleting it for budget.
4. Apply the git staging contract for files changed in this turn only; report
   unrelated dirty paths without staging them.
4. Translate external material into invariants, evals, references, contracts, or
   an explicit rejection.
5. For skill work, run the A/B/C spec-implementation-evaluation loop until the
   stop rule passes or a concrete blocker remains.
6. Store review media under `.harness/media/` with prompt/cache notes; do not
   store review-only media in the skill package.
7. If the evidence points to a shared contract, patch that contract and its
   enforcing evals before adding another visible surface.
8. Apply the BLUF review contract to non-trivial durable improvement reports or
   loop artifacts so the target, gap, patch decision, validation blocker, and
   stop rule are visible before detail.
9. Apply the visual reference contract when an improvement report, media proof,
   skill routing change, or before/after behavior comparison would otherwise be
   hidden in prose.

## Folded Validation

Fail fast: stop at the first failed gate, fix or block it, then rerun before
broader checks. Compare before/after behavior and exact command outcomes. For
skill-package edits, run strict audit, OpenClaw, OpenAI format lint,
progressive disclosure lint, Plugin Eval, relevant smoke/release evals, and
focused package checks when available. Missing proof is `blocked` or `not-run`,
never `pass`.
For non-trivial generated improvement artifacts, run or block
`python3 Plugins/harness-engineering/scripts/check_bluf_structure.py
<improvement-artifact-path> --json`.

## Folded Confidence Reporting

Tie confidence to source ownership, evidence quality, validator agreement,
before/after delta, runtime visibility when relevant, Plugin Eval budget, and
remaining unknowns. Do not call a surface improved from static lint alone.

## Folded Examples

- "Can you inspect the session collector evidence bundle and harden
  `Plugins/harness-engineering/skills/he-plan` until strict audit has no
  warnings?"
- "Please validate `he-code-review` against its `SKILL.md`, `contract.yaml`,
  `evals.yaml`, and latest audit output, then patch the smallest gap."

## Folded Assets

Reference `assets/` only for skill packaging and browseability. Experiment logs,
loop artifacts, and review media belong in references, repo artifacts, or
`.harness/media/`.
