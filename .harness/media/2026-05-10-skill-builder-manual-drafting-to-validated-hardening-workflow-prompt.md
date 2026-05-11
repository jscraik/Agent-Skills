# Skill Builder Transformation Prompt

Use case: skill-specific technical infographic
Asset type: review artifact / X technical explainer
Recommended size: 2048x1152
Aspect ratio: 16:9

Title:
"Skill Builder: From Manual Drafting -> Validated Hardening Workflow"

Subtitle:
"A bespoke transformation map for skill-builder"

Context:
The skill-builder package was reviewed as a Skill Factory hardening lane. The patch folded a large Codex-harness review and media-artifact contract into a routed reference, kept SKILL.md compact, added canonical-source and media-persistence behavior, repaired eval metadata, and improved the interface description. Validation evidence: strict audit pass, OpenAI format pass, progressive disclosure pass, OpenClaw pass through strict audit, Plugin Eval A/95 with residual heavy invoke-cost warning, smoke eval fail in isolated Codex runner.

Before state:

- Long review workflow lived in user prompt, not durable skill behavior.
- Entrypoint risked growing into a prompt blob.
- Eval metadata had weak realism declarations and low deterministic coverage.
- Media persistence rules were absent from the skill contract.
- Interface description ended with an ellipsis.

After state:

- `SKILL.md` routes heavy review/media workflow to `references/harness-hardening-workflow.md`.
- Canonical-source, runtime-projection, validator-matrix, confidence-ceiling, and media-persistence rules are durable.
- `evals.yaml` includes realistic fields, safer deterministic checks, and new hardening/media cases.
- `contract.yaml` records long-workflow and media-artifact behavior.
- Plugin Eval improved from B/86 failure-level cost to A/95 warning-level cost.

Evidence shown:

- strict audit: pass
- OpenClaw: pass
- OpenAI skill format: pass
- progressive disclosure lint: pass
- Plugin Eval: pass with invoke-cost warning
- smoke evals: fail
- release evals: not run
- media persistence: blocked until generated bitmap path is available

Composition:
Builder/factory skill layout. Left panel "before": manual hardening prompt, bloated entrypoint risk, weak eval realism, no media persistence contract. Center panel "skill-builder package anatomy": SKILL.md compact router, harness-hardening-workflow reference, evals.yaml, contract.yaml, openai.yaml. Right panel "after": validated hardening workflow, canonical source detection, validator alignment, evidence capture, media artifact plan. Bottom evidence strip with status chips. Include a small confidence movement annotation: 68% -> 82% capped by failed smoke evals.

Style:
Professional engineering poster, warm off-white technical-paper background, charcoal ink, restrained amber/green/red status accents, dense but readable scientific reference layout, clean leader lines and callouts.

Constraints:

- no fake dashboards
- no invented metrics
- no fake logos
- no generic "Codex Harness Skill" title
- no claims unsupported by the review
- no sci-fi visuals
- no glowing orbs
- no abstract decorative blobs
- leave clean zones for deterministic overlay text
- use readable labels, not tiny filler text

Deterministic overlay text to add separately:

- Skill Builder
- From Manual Drafting -> Validated Hardening Workflow
- Durable routed reference + eval/contract coverage
- Evidence: strict pass, format pass, progressive pass, Plugin Eval A/95 warn, smoke fail
