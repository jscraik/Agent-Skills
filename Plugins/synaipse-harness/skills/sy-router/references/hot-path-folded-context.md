# Hot-Path Folded Context

## Purpose
Preserve detailed context folded out of SKILL.md so the active sy-router entrypoint stays below the hot-path soft budget without losing usable guidance.

## 2026-05-15 Soft-Warning Cleanup

Disposition:
- moved-to-reference: bulky examples, extended output fields, repeated evidence detail, and long procedure tails.
- superseded: repeated headings whose active entrypoint now points to shared contracts.
- intentionally-discarded: none in this file; prompt rot is tracked in shared folded context when removed.

## Folded When to Use

- Stage choice is unclear, mixed, or asks which SynAIpse stage to use.
- A folded alias appears, such as `sy-tdd`, `sy-refine`,
  `sy-technical-review`, `sy-compound`, `sy-compound-refresh`, or
  `sy-prune-branches`.
- The request mentions SynAIpse artifacts, tracker lifecycle state, prior sessions,
  waits, closure proof, specialist steering, or gate selection before a stage is
  chosen.

## Folded When Not to Use

- A valid non-router SynAIpse stage is explicitly requested and no correctness
  question is being asked.
- The task is outside SynAIpse routing, such as pure image generation, spreadsheets,
  generic repo edits, or external tracker work.
- A selected stage already has authority for implementation, review repair,
  tracker mutation, or cleanup.

## Folded Codex Harness Placement

- Skill Factory: this package is canonical; `.agents/skills/sy-router` is a
  generated handle.
- Rules/hooks: router work is read-only; validators prove structure, not runtime
  outcome quality.
- MCP/tools: use local evidence first; external tools require selected-stage
  need and permission.
- Human approval: ask once before consequential ambiguity or risky action.

## Folded Safety Boundaries

- Forbidden from router-only authority: code edits, artifact writes,
  tracker/GitHub updates, installs, deploys, secret reads, branch pruning, and
  completion claims.
- Redact secrets, credentials, tokens, private transcripts, and sensitive
  personal data by default.
- Approval required for destructive cleanup, broad edits, external writes,
  credential access, expensive network work, or irreversible recommendations.
- Safe fallback: return a blocked route with the smallest recovery step.

## Folded Examples

- Request: "JSC-244 has a draft spec, a Linear plan note, and an open PR; choose
  whether the next SynAIpse step is plan, work, review, or eval, and name the missing
  proof." Expected: one route plus `missing_input`, not implementation.
- Request: "PR 153 merged but Linear is still In Review; route the closure-proof
  step without closing Linear or inventing validation." Expected: eval/closure
  proof handoff with external mutation blocked.

## Folded Accessibility Requirements

Use plain text, stable field names, one recovery action for blockers, and no
color-only status.

## Folded Context Routes

- Read when: deterministic stage choice is needed ->
  `Plugins/synaipse-harness/references/routing-map.json`
- Read when: route priority or folded aliases are unclear ->
  `Plugins/synaipse-harness/references/deterministic-stage-routing.md`
- Read when: broad gates could over-route ->
  `Plugins/synaipse-harness/references/gate-selection-contract.md`
- Read when: preserved router rules are needed ->
  `references/context-preservation.md`
- Read when: role names are involved -> `references/role-resolution-fallback.md`
- Read when: recurring waits appear -> `references/heartbeat-routing-preservation.md`

## Folded Confidence Reporting

Use `high` for deterministic rule plus required evidence, `medium` for
reversible inference, and `blocked` for missing input, conflict, unavailable
resolver, or unsafe authority gap.

Deferred context index: `../../references/deferred-context-index.md`.
Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.
Read when closure proof could be mistaken for live tracker mutation:
`../../references/closure-mutation-contract.md`.
