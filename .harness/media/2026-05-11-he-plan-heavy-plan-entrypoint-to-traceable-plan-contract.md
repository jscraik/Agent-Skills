# From Heavy Plan Entrypoint -> Traceable Plan Contract

## Purpose

This review artifact records the intended image-generation framing for the he-plan hardening pass. It exists to make the skill-specific transformation, validation evidence, and media persistence status auditable without storing review-only media inside the skill package.

## Image Generation & Persistence Evidence

* media status: generation-blocked
* `$imagegen` invoked: blocked
* generated-image cache source path: blocked because the active image-generation tool contract does not expose a discoverable local PNG/cache path and forbids post-generation text needed to report persistence evidence
* repository `.harness/media/` PNG path: blocked because no verifiable generated PNG was available to copy
* prompt metadata path: .harness/media/2026-05-11-he-plan-heavy-plan-entrypoint-to-traceable-plan-contract-prompt.md
* sidecar path: .harness/media/2026-05-11-he-plan-heavy-plan-entrypoint-to-traceable-plan-contract.md
* repository PNG existence verification: blocked
* persistence method: blocked
* final user-facing text after imagegen permitted: no
* residual risk: A production bitmap still needs generation through a tool that exposes a stable source path or writes directly to `.harness/media/`.

## Bespoke Framing

* skill name: he-plan
* skill type: governance / documentation / validation-oriented / orchestration-adjacent
* original state: structurally valid but heavy plan entrypoint with missing eval realism metadata and synthetic eval prompts
* target state: compact traceable plan contract with realistic eval metadata and explicit plan-only safety, validation, rollback, and handoff boundaries
* main weakness: heavy active context plus weak eval realism reduced confidence in routing and validation signal
* main improvement: strict audit and skill gate warnings were removed while Plugin Eval improved from 91/B to 95/A and active invoke cost moved from heavy to moderate
* validation evidence: strict audit pass; skill gate pass; OpenAI skill format pass; OpenClaw pass via strict audit; Plugin Eval 95/A with one deferred-cost warning; package boundary check pass; he-plan proof reachable without outcome proof; smoke eval blocked by timeout
* package alignment status: updated
* artifact impact: updated SKILL.md, updated references/evals.yaml, added review media prompt metadata, added review media sidecar
* confidence movement: 72% -> 88%
* loop outcome: optimal within available evidence

## Prompt Summary

Prompt metadata is stored at `.harness/media/2026-05-11-he-plan-heavy-plan-entrypoint-to-traceable-plan-contract-prompt.md`. It asks for a three-lane engineering poster showing the before state, patch lane, after state, and evidence strip for he-plan.

## Linked Context

* canonical skill source: Plugins/harness-engineering/skills/he-plan/SKILL.md
* eval metadata: Plugins/harness-engineering/skills/he-plan/references/evals.yaml
* generated command handle, not edited: .agents/skills/he-plan/SKILL.md

## Fallback `$imagegen` Prompt Output Contract

$imagegen

Use case: skill-review technical infographic
Asset type: review artifact / Harness Engineering skill hardening explainer
Recommended size: 2048x1152
Aspect ratio: 16:9

Title:
"From Heavy Plan Entrypoint -> Traceable Plan Contract"

Subtitle:
"A bespoke transformation map for he-plan"

Context:
The he-plan skill was reviewed as a Harness Engineering planning workflow. The patch compressed its always-loaded entrypoint, preserved planning-only safety boundaries, made eval prompts concrete, added explicit eval realism metadata, and kept detailed planning-depth, handoff, test, and visual guidance deferred in references.

Before state:

* Active entrypoint was structurally valid but heavy.
* All eval trigger cases lacked explicit realistic true/false metadata.
* Several eval prompts were synthetic or malformed, weakening validation realism.

After state:

* Compact planning contract with explicit status fields, handoff state, traceability, validation, rollback, and non-mutation boundaries.
* Realistic eval metadata and concrete HE planning scenarios remove strict audit and skill gate warnings.
* Plugin Eval improved from 91/B with heavy invoke cost to 95/A with moderate invoke cost; deferred-cost warning remains.

Evidence shown:

* strict audit: pass
* skill gate: pass
* OpenAI skill format: pass
* OpenClaw: pass via strict audit
* Plugin Eval: 95/A, deferred-cost warning remains
* media persistence: generation-blocked

Composition:
Create a precise engineering poster with three lanes. Left lane shows "Before" as a heavy plan entrypoint, missing eval-realism tags, and synthetic eval cards. Center lane shows "Patch" as focused edits to SKILL.md and evals.yaml, with traceability, plan-only boundaries, handoff state, and validation gates. Right lane shows "After" as a traceable plan contract: selected slice, plan IDs, acceptance IDs, validation, rollback, Linear/spec/plan/PR matrix, and post-plan handoff. Include an evidence strip with only the statuses listed above.

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

* he-plan
* From Heavy Plan Entrypoint -> Traceable Plan Contract
* Compact plan contract plus realistic eval metadata
* strict audit pass / skill gate pass / OpenAI format pass / Plugin Eval 95A / smoke blocked
* optimal within available evidence
