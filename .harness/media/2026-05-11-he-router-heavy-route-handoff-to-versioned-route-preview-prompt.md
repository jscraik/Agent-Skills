# $imagegen Prompt: From Heavy Route Handoff -> Versioned Route Preview

Use case: skill-review technical infographic
Asset type: review artifact / Harness Engineering router explainer
Recommended size: 2048x1152
Aspect ratio: 16:9

Title:
"From Heavy Route Handoff -> Versioned Route Preview"

Subtitle:
"A bespoke transformation map for he-router"

Context:
Review artifact for `he-router`, a Harness Engineering routing skill that selects one next lifecycle stage without doing the stage work. The review patched the canonical package to clarify generated-handle boundaries, add versioned route-preview output fields, align contract/evals with router-only authority, improve adversarial eval metadata, and validate deterministic routing checks. Remaining risk is static Plugin Eval cost pressure and unavailable smoke runtime evidence.

Before state:
- Router entrypoint exposed weaker route-preview semantics.
- Contract did not explicitly bound `safe_to_continue` or external mutation authority.
- Evals lacked realistic metadata and adversarial injection classification.
- Generated `.agents/skills/he-router` handle could be mistaken for source.
- Smoke eval runtime did not return within the active session.

After state:
- Structured route-preview contract includes `route_preview_version` and `schema_version`.
- Router-only authority now blocks implementation, external mutation, sync/install, branch pruning, and closure claims.
- Contract observability tracks authority limits and blocked reasons.
- Evals include realistic fields, with destructive injection marked adversarial rather than realistic traffic.
- Validation evidence ties the patch to strict audit, skill gate, OpenAI format, boundary proof, routing samples, package hygiene, deferred index, and Plugin Eval.

Evidence shown:
- strict audit: pass with examples heuristic warning
- skill gate: pass with examples heuristic warning
- OpenAI skill format: pass
- OpenClaw: pass via strict audit evidence
- Plugin Eval: 91/100, B, medium risk, static cost warnings
- package boundary checks: pass
- sync/projection checks: pass, generated handle is not source
- routing samples: pass
- smoke evals: blocked by no output/hung runner
- media persistence: generation blocked because active image tool does not expose a verifiable local PNG path under `.harness/media/`

Composition:
Create a precise engineering poster with a left-to-right flow. Left column: "Before" as an overloaded router card with unlabeled handoff fields and a red boundary-warning rail for generated handle confusion. Center: a decision spine labelled "canonical source -> route preview -> selected stage". Right column: "After" with versioned route-preview fields, authority-limit shield, blocked-reason ledger, and validation evidence strip. Include a small bottom strip showing "Smoke: blocked" and "Plugin Eval cost: residual risk" as honest non-pass states.

Style:
Professional engineering poster, dense but readable, restrained colour palette, crisp diagrammatic layout, no fake product logos, no fake dashboards, no invented metrics.

Constraints:
- no fake dashboards
- no invented metrics
- no fake logos
- no unsupported claims
- no generic title unless accurate
- leave clean zones for deterministic overlay text
- use readable labels, not tiny filler text
- represent blocked validation as blocked, not passed

Deterministic overlay text to add separately:
- he-router
- From Heavy Route Handoff -> Versioned Route Preview
- Versioned route previews with explicit authority limits
- strict audit pass; skill gate pass; OpenAI format pass; Plugin Eval B with cost warnings; smoke blocked
- optimal within available evidence
