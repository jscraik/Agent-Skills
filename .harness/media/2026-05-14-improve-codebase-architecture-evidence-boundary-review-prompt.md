# Fallback Image Prompt: Improve Codebase Architecture

$imagegen

Use case: skill-review technical infographic
Asset type: review artifact / X technical explainer
Recommended size: 2048x1152
Aspect ratio: 16:9

Title:
"From Broad Architecture Heuristics -> Evidence-Bound Boundary Review"

Subtitle:
"A bespoke transformation map for improve-codebase-architecture"

Context:
The improve-codebase-architecture skill was reviewed and patched in the agent-skills repository. The patch fixed missing skill-gate headings, aligned the machine-readable contract, added realistic eval metadata, compressed the entrypoint back to an A-grade Plugin Eval cost profile, and preserved architecture lenses in routed references.

Before state:

* Missing skill-gate required headings for execution boundaries, failure mode, and gotchas
* Contract drift against the repo's legacy schema expectations
* Eval realism metadata was missing or under-declared
* Architecture reference omitted some supplied architecture lenses
* Entrypoint cost could regress if hardening details stayed always loaded

After state:

* Validator-compatible headings with explicit boundaries and failure behavior
* Contract.yaml aligned with required list-shaped fields and risk/non-goal keys
* Evals include realistic, why_realistic, expected_behavior, and anti_overfit_notes
* Architecture lenses consolidated in references without bloating SKILL.md
* Plugin Eval restored to A / 100 with no warnings

Evidence shown:

* strict skill audit: pass
* skill gate: pass with warnings
* OpenAI skill format: pass
* OpenClaw: pass via strict audit, 0 critical / 0 warn / 2 info
* Plugin Eval: pass, A / 100, no warnings
* smoke evals: fail/blocker due unavailable selection signal
* release evals: fail/blocker due unavailable selection signal and timeout/self-assessment failures
* package boundary checks: pass
* sync/projection proof: blocked by command-handle drift outside safe autonomous scope
* media persistence: fallback-only, no generated PNG

Composition:
Create a restrained professional engineering poster. Left panel shows the previous skill as a loose stack of broad heuristics, schema drift, and eval uncertainty. Center panel shows validator gates and a compact routing layer. Right panel shows the target state: evidence-bound boundary review with tracer proof, contract alignment, and routed architecture lenses. Include a bottom evidence strip with labelled pass/fail/blocked statuses. Leave clean zones for deterministic overlay text instead of relying on tiny generated text.

Style:
Professional engineering poster, dense but readable, restrained colour palette, crisp diagrammatic layout, no decorative orbs or fake dashboards.

Constraints:

* no fake dashboards
* no invented metrics
* no fake logos
* no unsupported claims
* no generic title unless accurate
* leave clean zones for deterministic overlay text
* use readable labels, not tiny filler text

Deterministic overlay text to add separately:

* improve-codebase-architecture
* From Broad Architecture Heuristics -> Evidence-Bound Boundary Review
* Main improvement: validator-compatible, proof-backed architecture workflow
* Evidence: strict audit pass; skill gate pass; OpenAI format pass; Plugin Eval A/100; eval runtime blocked
* Loop outcome: source fixes complete; runtime validation blocked by smoke/release eval selection-signal failures
