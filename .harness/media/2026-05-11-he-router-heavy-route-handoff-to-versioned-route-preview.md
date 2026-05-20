# From Heavy Route Handoff -> Versioned Route Preview

## Purpose

This sidecar records the review-media artifact for the `he-router` skill hardening pass. It exists to tie the requested infographic to the actual package changes, validator evidence, and residual blocked states without claiming unverifiable image persistence.

## Image Generation & Persistence Evidence

* media status: generation-blocked
* `$imagegen` invoked: blocked
* generated-image cache source path: blocked because the active image-generation tool does not expose a cache path that can be copied or verified in `.harness/media/`
* repository `.harness/media/` PNG path: blocked because no verifiable PNG was produced
* prompt metadata path: `.harness/media/2026-05-11-he-router-heavy-route-handoff-to-versioned-route-preview-prompt.md`
* sidecar path: `.harness/media/2026-05-11-he-router-heavy-route-handoff-to-versioned-route-preview.md`
* repository PNG existence verification: blocked
* persistence method: blocked
* final user-facing text after imagegen permitted: no
* residual risk: direct image generation cannot be both invoked and followed by the required 21-section final report under the active tool contract, and PNG persistence cannot be verified from the tool interface.

## Bespoke Framing

* skill name: he-router
* skill type: router / governance / validation-oriented
* original state: heavy route handoff with weaker versioned output and authority boundaries
* target state: versioned route-preview contract with explicit router-only authority
* main weakness: route output and contract did not make false continuation and generated-handle source confusion explicit enough
* main improvement: structured route-preview fields now carry schema version, authority limit, blocked reason, handoff payload, and safe continuation caveats
* validation evidence: strict audit pass with examples heuristic warning; skill gate pass with examples heuristic warning; OpenAI skill format pass; OpenClaw pass via strict audit; Plugin Eval 91/100 with static cost warnings; boundary check pass; proof reachable without outcome proof; routing samples pass; package hygiene pass; deferred index pass; smoke eval blocked by hung runner
* package alignment status: updated
* artifact impact: changed `SKILL.md`, `references/context-preservation.md`, `references/contract.yaml`, `references/evals.yaml`, and this `.harness/media/` sidecar/prompt pair
* confidence movement: 72% -> 88%
* loop outcome: optimal within available evidence

## Prompt Summary

See `.harness/media/2026-05-11-he-router-heavy-route-handoff-to-versioned-route-preview-prompt.md` for the full fallback `$imagegen` prompt.

## Linked Context

Reviewed canonical package: `Plugins/harness-engineering/skills/he-router/SKILL.md`

Generated handle checked but not edited: `.agents/skills/he-router/SKILL.md`
