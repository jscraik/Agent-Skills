# From Overloaded Spec Entrypoint -> Evidence-Bound Spec Contract

## Purpose

This review artifact records the intended image-generation framing for the he-spec hardening pass. It exists to make the skill-specific transformation, validation evidence, and media persistence status auditable without storing review-only media inside the skill package.

## Image Generation & Persistence Evidence

* media status: generation-blocked
* `$imagegen` invoked: blocked
* generated-image cache source path: blocked because the active image-generation tool contract does not expose a discoverable local PNG/cache path and forbids post-generation text needed to report persistence evidence
* repository `.harness/media/` PNG path: blocked because no verifiable generated PNG was available to copy
* prompt metadata path: /Users/jamiecraik/dev/agent-skills/.harness/media/2026-05-11-he-spec-overloaded-spec-entrypoint-to-evidence-bound-spec-contract-prompt.md
* sidecar path: /Users/jamiecraik/dev/agent-skills/.harness/media/2026-05-11-he-spec-overloaded-spec-entrypoint-to-evidence-bound-spec-contract.md
* repository PNG existence verification: blocked
* persistence method: blocked
* final user-facing text after imagegen permitted: no
* residual risk: A production bitmap still needs generation through a tool that exposes a stable source path or writes directly to `.harness/media/`.

## Bespoke Framing

* skill name: he-spec
* skill type: governance / documentation / validation-oriented / orchestration-adjacent
* original state: validator-clean but heavy spec entrypoint with synthetic eval prompts and missing realistic eval metadata
* target state: compact evidence-bound spec contract with realistic eval metadata and explicit tracker, validation, rollback, and handoff boundaries
* main weakness: eval realism warnings and heavy active context obscured spec authority boundaries
* main improvement: strict audit and skill gate warnings were removed while Plugin Eval improved from 91/B to 95/A and active invoke cost moved from heavy to moderate
* validation evidence: strict audit pass; skill gate pass; OpenAI skill format pass; OpenClaw pass via strict audit; Plugin Eval 95/A with one deferred-cost warning; package boundary check pass; he-spec proof reachable without outcome proof; smoke eval blocked by timeout
* package alignment status: updated
* artifact impact: updated SKILL.md, updated references/evals.yaml, added review media prompt metadata, added review media sidecar
* confidence movement: 72% -> 88%
* loop outcome: optimal within available evidence

## Prompt Summary

Prompt metadata is stored at `/Users/jamiecraik/dev/agent-skills/.harness/media/2026-05-11-he-spec-overloaded-spec-entrypoint-to-evidence-bound-spec-contract-prompt.md`. It asks for a three-lane engineering poster showing the before state, patch lane, after state, and evidence strip for he-spec.

## Linked Context

* canonical skill source: /Users/jamiecraik/dev/agent-skills/Plugins/harness-engineering/skills/he-spec/SKILL.md
* eval metadata: /Users/jamiecraik/dev/agent-skills/Plugins/harness-engineering/skills/he-spec/references/evals.yaml
* generated command handle, not edited: /Users/jamiecraik/dev/agent-skills/.agents/skills/he-spec/SKILL.md

## Fallback `$imagegen` Prompt Output Contract

$imagegen

Use case: skill-review technical infographic
Asset type: review artifact / Harness Engineering skill hardening explainer
Recommended size: 2048x1152
Aspect ratio: 16:9

Title:
"From Overloaded Spec Entrypoint -> Evidence-Bound Spec Contract"

Subtitle:
"A bespoke transformation map for he-spec"

Context:
The he-spec skill was reviewed as a Harness Engineering specification workflow. The patch compressed its always-loaded entrypoint, tightened source-traceability and live tracker boundaries, added realistic eval metadata, and preserved validator-compatible headings while keeping detailed mode and artifact rules in references.

Before state:

* Validator-clean structure, but heavy active context made routing and authority harder to scan.
* Evals missed realistic-field metadata and used synthetic prompt shapes that triggered validation warnings.
* Spec authority, live Linear truth, artifact-write permission, and handoff boundaries were present but too diffuse.

After state:

* Compact evidence-bound spec contract with clear status fields, safety boundaries, and handoff rules.
* Realistic eval prompts and metadata remove strict audit and skill-gate warnings.
* Validation evidence links strict audit, skill gate, OpenAI format, OpenClaw, boundary proof, Plugin Eval score movement, and blocked smoke/release evals.

Evidence shown:

* strict audit: pass
* skill gate: pass
* OpenAI skill format: pass
* OpenClaw: pass via strict audit
* Plugin Eval: 95/A, deferred-cost warning remains
* media persistence: generation-blocked

Composition:
Create a precise engineering poster with three lanes. Left lane shows "Before" as an overlong entrypoint, synthetic eval cards, and diffuse authority arrows. Center lane shows "Patch" as focused edits to SKILL.md and evals.yaml, with source-traceability, tracker truth, validation gates, and handoff boundaries. Right lane shows "After" as a compact spec contract with status block, stable acceptance IDs, evidence gates, rollback, and plan handoff. Use deterministic label zones so the evidence strip can be read without relying on tiny filler text.

Style:
Professional engineering poster, dense but readable, restrained colour palette, crisp diagrammatic layout.

Constraints:

* no fake dashboards
* no invented metrics
* no fake logos
* no unsupported claims
* no generic title unless accurate
* leave clean zones for deterministic overlay text
* use readable labels, not tiny filler text

Deterministic overlay text to add separately:

* he-spec
* From Overloaded Spec Entrypoint -> Evidence-Bound Spec Contract
* Compact spec contract plus realistic eval metadata
* strict audit pass / skill gate pass / OpenAI format pass / Plugin Eval 95A / smoke blocked
* optimal within available evidence
