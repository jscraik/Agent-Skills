<!-- markdownlint-disable MD013 -->

# HE Compound: From Eval Drift and Hidden Boundaries -> Evidence-Bound Routing

## Purpose

Review media sidecar for the `he-compound` skill hardening pass. The image is a bespoke technical infographic tied to the actual patch, validation evidence, and remaining quota-limited runtime risk.

## Image Generation & Persistence Evidence

- `$imagegen` invoked: planned as final action after this sidecar because the active image tool forbids user-facing text after generation
- generated-image cache source path: blocked until the active image tool returns or exposes a cache path
- repository `.harness/media/` PNG path: blocked; `/Users/jamiecraik/dev/agent-skills/.harness/media/2026-05-10-he-compound-evidence-bound-routing.png` not claimed
- prompt metadata path: `/Users/jamiecraik/dev/agent-skills/.harness/media/2026-05-10-he-compound-evidence-bound-routing-prompt.md`
- sidecar path: `/Users/jamiecraik/dev/agent-skills/.harness/media/2026-05-10-he-compound-evidence-bound-routing.md`
- repository PNG existence verification: blocked
- persistence method: blocked
- final user-facing text after imagegen permitted: no
- residual risk: direct generation can be invoked as the final action, but repository-local PNG copy cannot be verified in the same turn without violating the image tool narration contract.

## Bespoke Framing

- skill name: `he-compound`
- original state: eval-realism drift and hidden lifecycle boundaries
- target state: evidence-bound compound routing
- main weakness: realistic eval claims lacked enough concrete task context, and lifecycle safety/failure/handoff contracts were too implicit.
- main improvement: explicit compound routing, source-prompt coverage, repeated-failure state, solution-capture boundaries, failure handling, and confidence reporting.
- validation evidence: strict audit pass; `skill_gate.py` pass; OpenClaw pass; OpenAI format lint pass; progressive disclosure lint pass; Plugin Eval 95/A with deferred-cost warning; smoke/release blocked by Codex quota.
- artifact impact: canonical `SKILL.md`, `references/evals.yaml`, and `assets/resolution-template.md` changed; runtime projection untouched.
- confidence movement: 78% -> 88%, capped by smoke/release runtime quota and runtime outcome-proof gaps.

## Prompt Summary

See `/Users/jamiecraik/dev/agent-skills/.harness/media/2026-05-10-he-compound-evidence-bound-routing-prompt.md`.

## Linked Context

- Skill: `/Users/jamiecraik/dev/agent-skills/Plugins/harness-engineering/skills/he-compound/SKILL.md`
- Smoke eval artifact: `/Users/jamiecraik/dev/agent-skills/Infrastructure/artifacts/skills/he-compound/20260510-205359-309104/scorecard.json`
