$imagegen

Use case: skill-review technical infographic
Asset type: review artifact / X technical explainer
Recommended size: 2048x1152
Aspect ratio: 16:9

Title:
“From Accurate But Heavy Docs Auditor → Evidence-Backed Reader-Testing Skill”

Subtitle:
“A bespoke transformation map for docs-expert”

Context:
The docs-expert skill package was reviewed and patched inside .. The canonical source is Skills/agent-ops/docs-expert, not the generated .agents handle. The patch integrated documentation-quality guidance and a Claude-oriented co-authoring workflow as Codex-safe context, added reader-testing and safety/handoff semantics, aligned contract/evals, then compressed SKILL.md after Plugin Eval flagged active-token cost.

Before state:
* Accurate evidence-backed documentation auditor, but active entrypoint had grown too heavy
* Reader-testing and substantial-doc co-authoring guidance was under-specified
* Package contract/evals did not fully encode the new documentation-quality criteria

After state:
* Compact 130-line active entrypoint with detailed guidance deferred to references/documentation-quality.md
* Contract and evals include skimmability, prose, reader-testing, approval gates, and co-authoring handoff
* Plugin Eval improved from B / high risk / 3276 active tokens to A / low risk / 1405 active tokens

Evidence shown:
* strict skill audit: pass
* skill gate: pass
* OpenAI skill format: pass
* OpenClaw: pass through strict audit
* package boundary checks: pass
* docs/prose lint: pass
* Plugin Eval: A, low risk
* smoke evals: blocked by timeout
* runtime outcome proof: missing/manual session gate
* media generation: fallback-only, no image_gen tool available

Composition:
Create a crisp engineering transformation map with three vertical columns: “Original Pressure”, “Patch Applied”, and “Evidence / Remaining Risk”. Show docs-expert as a documentation skill, not a generic prompt. Include small visual motifs for canonical source, generated handle boundary, reader questions, validation gates, and token budget compression. Use a bottom evidence strip with green pass chips and amber blocked chips. Leave clean zones for deterministic overlay text.

Style:
Professional engineering poster, dense but readable, restrained neutral palette with green pass and amber blocked accents, crisp diagrammatic layout.

Constraints:
* no fake dashboards
* no invented metrics
* no fake logos
* no unsupported claims
* no generic title unless accurate
* leave clean zones for deterministic overlay text
* use readable labels, not tiny filler text

Deterministic overlay text to add separately:
* docs-expert
* From Accurate But Heavy Docs Auditor → Evidence-Backed Reader-Testing Skill
* Main improvement: compact active skill plus deferred documentation-quality reference
* Evidence: strict audit / skill gate / OpenAI format / Plugin Eval A pass; smoke eval blocked
* Loop outcome: optimal within available evidence
