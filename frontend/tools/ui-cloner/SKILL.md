---
name: ui-cloner
description: Plan a branded UI clone from a target website URL with implementation-ready guidance. Use when the user wants a site's visual system recreated or adapted, not raw crawling or deployment work.
metadata:
  skill-type: scaffolding_templates
---

# UI Cloner

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Discovery interview](#discovery-interview)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Workflow](#workflow)
- [Validation](#validation)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [References](#references)
- [Decision feedback protocol](#decision-feedback-protocol)
- [Remember](#remember)

## Standards snapshot
- Keep this skill focused on visual replication planning, not raw crawl orchestration.
- Use `cf-crawl` as an optional upstream helper to generate URL manifests and markdown corpus before visual audit.
- Produce implementation-ready output that another engineer can execute without hidden assumptions.
- Vary deliverable shape based on intent: quick inspiration clone, high-fidelity replica plan, or adaptation blueprint.

## Working agreement
- Follow the repo's `AGENTS.md` (map, not a megadoc).
- For long runs, also follow `~/.codex/instructions/shell-skills-compaction.md` if present.
- Artifact boundary:
  - Local CLI: write deliverables to `./artifacts/`
  - Hosted shell: write deliverables to `/mnt/data/`

## When to use
- Primary triggers:
  - User provides a URL and asks to clone or recreate the visual style/layout.
  - User asks for a structured “site DNA” or style system extraction from an existing site.
  - User wants implementation guidance to adapt a reference site's UI to their own brand.
- Non-triggers (route elsewhere):
  - Crawl-only operations (start/status/export Cloudflare jobs) with no replication ask: use `cf-crawl`.
  - Browser automation/testing flows (click paths, login scripts): use Playwright or `agent-browser`.
  - Deployment/infrastructure asks: use deployment-focused skills.

## Required inputs
- Assumptions:
  - User has rights to analyze the target URL and reuse design patterns.
- Required:
  - Target URL.
  - Replication objective: inspiration-level, high-fidelity, or adapted clone.
  - Target stack/context for implementation guidance (for example React/Tailwind, plain HTML/CSS).
- Optional:
  - Brand constraints (colors, voice, typography, logos, accessibility targets).
  - Scope limits (specific pages/sections only).
- Useful upstream helper:
  - `cf-crawl` output (URL/page manifest + markdown corpus) when site structure is large or unclear.
- Ask clarifying questions only for genuine gaps.

## Discovery interview
- Ask one round at a time when critical inputs are missing.
- Use plain-language questions with 2-3 concrete options when possible.
- Include "why this matters" in one short sentence for each round.
- Do not dump a full interview plan in one message ("no full-plan dump").
- Explain why the round matters in one short sentence before moving on.
- Avoid dumping the whole interview plan at once.
- Stop discovery once URL, mode, target stack, and brand constraints are sufficiently clear to proceed safely.
- Use `references/discovery-interview.md` for a compact question flow.

## Deliverables
- `artifacts/ui-cloner/site-dna.md`: visual system extraction (layout, tokens, hierarchy, motion patterns).
- `artifacts/ui-cloner/replication-plan.md`: implementation-oriented section-by-section build plan.
- `artifacts/ui-cloner/adaptation-map.json`: structured token/section mapping for adapting source UI to user brand (`schema_version: 1`).
- Optional: `artifacts/ui-cloner/prompt.md` for one-shot generation in the user’s preferred builder workflow.
- Always write artifacts to `./artifacts/` (local) or `/mnt/data/` (hosted).

## Output contract
Use this shape for `adaptation-map.json`:

```json
{
  "schema_version": 1,
  "source_url": "string",
  "mode": "fast|high_fidelity|adaptation",
  "sections": [
    {
      "source_section": "string",
      "target_section": "string",
      "layout_mapping": "string",
      "risk_notes": ["string"]
    }
  ],
  "token_mapping": {
    "color": [{"source": "string", "target": "string"}],
    "typography": [{"source": "string", "target": "string"}],
    "spacing": [{"source": "string", "target": "string"}]
  }
}
```

## Deliverable shape
- Fast path: concise site DNA + top 5 replication priorities.
- High-fidelity path: section wireframes, precise spacing/typography notes, animation timing checklist.
- Adaptation path: source-to-brand mapping table and non-negotiable fidelity constraints.

## Failure mode
- If URL is missing or inaccessible, stop with a minimal input request.
- If request is actually crawl-only, route to `cf-crawl` and do not force replication output.
- If legal or policy scope is unclear (private target, unauthorized content), pause and report constraints.

## Constraints and safety
- Redact secrets/PII by default.
- If networking is required: specify a minimal domain allowlist and gate it behind explicit opt-in.
- Destructive actions require explicit confirmation; prefer dry-run first.
- Do not copy proprietary assets verbatim (logos, copyrighted illustrations, protected media) unless user confirms rights.

## Principles
- Capture intent before details: identify what visual qualities must survive adaptation.
- Preserve structure, then style: layout hierarchy and interaction model come before color/token swaps.
- Prefer evidence-backed extraction over vague style adjectives.
- Keep replication auditable with explicit section and token mappings.
- Adapt execution and output shape to context; avoid rigid one-size-fits-all responses.

## Workflow
1) Confirm replication mode (fast inspiration, high fidelity, brand adaptation) and target stack.
2) Optional crawl handoff:
   - For multi-page or unclear structures, invoke `cf-crawl` first to produce URL/page manifests and markdown corpus.
   - Use crawl output as context for prioritizing sections before visual audit.
3) Run visual audit on requested pages/sections:
   - Capture layout architecture, token candidates, typography hierarchy, interaction/motion behavior, and component patterns.
4) Build adaptation artifacts:
   - `site-dna.md`, `replication-plan.md`, and `adaptation-map.json`.
5) Produce execution-ready summary:
   - ordered build steps, fidelity risks, and what to verify first in implementation.
6) Prefer progressive disclosure:
   - Put deep docs in `references/` and link to them.
   - Put reusable automation in `scripts/` and reference it here.
   - Put templates/boilerplate in `assets/`.
7) End by writing artifacts + listing changed files/commands.

## Validation
- `~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/quick_validate.py frontend/tools/ui-cloner`
- `~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/skill_gate.py frontend/tools/ui-cloner`
- `~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/analyze_skill.py frontend/tools/ui-cloner`
- `~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/openclaw_skill_guard.py frontend/tools/ui-cloner --mode both`
- Fail fast: if a gate fails, stop and report the failure before continuing.
- For non-trivial skills, add `references/evals.yaml` with at least:
  - happy-path
  - edge-case
  - failure-mode

## Anti-patterns
- Treating this skill as a pure crawl/export utility.
- Returning style adjectives without concrete layout/token evidence.
- Producing generic “modern UI” guidance with no section-level mapping.
- Skipping adaptation constraints and overwriting user brand requirements.

## Examples
- Triggering prompt: "Clone the feel of https://example.com for my SaaS homepage and adapt it to our brand colors."
- Triggering prompt: "Audit this reference URL and give me a high-fidelity replication plan in React + Tailwind."
- Non-triggering prompt: "Start a Cloudflare crawl job for this URL and export markdown."

## References
- `references/contract.yaml`
- `references/evals.yaml`
- `references/discovery-interview.md`
- `references/plan.md`

## Decision feedback protocol

## See Also

| Skill | When to use together |
|---|---|
| [[stitch-loop]] | Feed cloned UI design into Stitch for iterative generation |
| [[frontend-ui-design]] | Adapt the cloned design system to your brand |
| [[design-system]] | Map cloned design tokens into your design system |
| [[figma]] | Use Figma as the intermediate for cloned designs |

**Topic map:** [[product-strategy]]

<!-- decision-feedback-protocol:v3 -->
**Decision feedback protocol (always run):**
After delivering results, ask the user directly:
> "Quick feedback — decision: accepted/partial/rejected/deferred? outcome: good/neutral/bad? confidence: high/medium/low?"
Then record it immediately:
`python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <decision> --outcome <outcome> --confidence <confidence> --notes "<optional notes>"`
Do not skip this step. Record even if the outcome is good.
<!-- /decision-feedback-protocol -->
## Remember
- Use `cf-crawl` as an upstream helper, not as this skill's core behavior.
- Keep outputs implementation-ready and evidence-backed.
- Enable bold replication quality without losing user brand constraints.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
