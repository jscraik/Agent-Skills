# From State Router With False-Closure Gaps -> Authority-Bound Lifecycle Reconcile

## Purpose

This artifact documents the required media plan for the `he-reconcile` skill-review hardening pass. It exists to preserve the image framing, evidence status, and persistence limits without storing review-only media inside the skill package.

## Image Generation & Persistence Evidence

* media status: generation-blocked
* `$imagegen` invoked: no
* generated-image cache source path: blocked - the active image tool does not expose a repository-copyable generated-image cache path in the callable interface, and invoking it would prevent the required post-generation evidence report under the active tool contract
* repository `.harness/media/` PNG path: blocked - no generated bitmap path was available to copy and verify
* prompt metadata path: `/Users/jamiecraik/dev/agent-skills/.harness/media/2026-05-11-he-reconcile-state-router-to-authority-bound-reconcile-prompt.md`
* sidecar path: `/Users/jamiecraik/dev/agent-skills/.harness/media/2026-05-11-he-reconcile-state-router-to-authority-bound-reconcile.md`
* repository PNG existence verification: blocked
* persistence method: blocked
* final user-facing text after imagegen permitted: no
* residual risk: direct bitmap generation and `.harness/media/` PNG persistence remain unverified; prompt metadata is ready for a tool surface that returns a local image path

## Bespoke Framing

* skill name: `he-reconcile`
* skill type: mixed governance / orchestration / routing
* original state: state router with false-closure gaps
* target state: authority-bound lifecycle reconcile
* main weakness: route recommendations did not loudly enough prevent implementation, external mutation, sync/install, destructive cleanup, or closure authority leakage
* main improvement: explicit authority boundary, degraded evidence handling, closure-proof handoff, and eval coverage for closure and projection pressure
* validation evidence: strict audit pass; skill gate pass; OpenAI skill format pass; OpenClaw pass through strict audit; Plugin Eval A/100; package boundary pass; packaging hygiene pass; deferred context index pass; smoke eval blocked
* package alignment status: updated
* artifact impact: updated `SKILL.md`, `references/contract.yaml`, `references/evals.yaml`, prompt metadata, and sidecar
* confidence movement: 82% -> 91%
* loop outcome: optimal within available evidence

## Prompt Summary

See `/Users/jamiecraik/dev/agent-skills/.harness/media/2026-05-11-he-reconcile-state-router-to-authority-bound-reconcile-prompt.md`.

## Linked Context

Canonical skill package: `/Users/jamiecraik/dev/agent-skills/Plugins/harness-engineering/skills/he-reconcile`.

Generated command handle projection: `/Users/jamiecraik/dev/agent-skills/.agents/skills/he-reconcile/SKILL.md`.
