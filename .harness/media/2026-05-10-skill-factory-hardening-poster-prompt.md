---
schema_version: 1
artifact_id: skill-factory-hardening-poster
artifact_type: imagegen-prompt-metadata
canonical_slug: skill-factory-hardening-poster
title: Skill Factory Hardening Poster
harness_stage: he-media
status: generated_prompt
date: 2026-05-10
local_bitmap_persistence: unsupported-by-active-image-tool
target_directory: .harness/media/
---

# Skill Factory Hardening Poster

This prompt is for a more explanatory infographic in the style of a dense
scientific reference poster, using the attached human-liver reference as a
layout direction rather than as subject matter.

The active image generation tool in this session does not expose a local output
path argument, so this metadata file is stored under `.harness/media/` before
direct image generation. The generated bitmap is not claimed to be locally saved
unless separately copied from the image cache.

## Prompt

Create a production-grade technical infographic poster titled:

`CODEX SKILL HARDENING: From Prompt Blob to Harness Component`

Use the visual grammar of a dense scientific anatomy wall chart: one large
central illustrated system, many small labeled side panels, compact scorecards,
 callout leader lines, badge-like section headers, and a bottom fact strip. The
subject is not biology. The subject is a Codex skill package being hardened by
Skill Factory validators.

The central illustration should show a layered "skill package anatomy" diagram:
a central `SKILL.md` document as the main body, surrounded by connected organs
or modules labeled with readable text: `Philosophy`, `Validation`, `When to
Use`, `Safety Boundaries`, `References`, `Scripts`, `Assets`, `evals.yaml`,
`contract.yaml`, and `.harness/media`. Use clean technical iconography rather
than cute characters. Leader lines should connect these modules to validation
gates.

Layout:

- Top-left large title zone: `CODEX SKILL HARDENING`.
- Subtitle below title: `From Prompt Blob to Harness Component`.
- Top-right compact scorecard titled `READINESS SCORE`, with rows:
  `Strict Audit`, `OpenClaw`, `openai_skill.py`, `Plugin Eval`, `Smoke Eval`,
  `Release Eval`, `Runtime Visibility`. Use checkmarks, warning triangles, and
  blocked markers rather than fake numeric metrics.
- Left sidebar titled `BEFORE`, with five concise failure cards:
  `Prompt-only review`, `Hidden assumptions`, `Validator heading drift`,
  `Bloated SKILL.md`, `Image prompt only`.
- Right sidebar titled `AFTER`, with five concise fix cards:
  `Compatibility aliases`, `Evidence gates`, `Progressive disclosure`,
  `Package-wide review`, `Generated media stored in .harness/media`.
- Bottom row titled `VALIDATION LOOP`, showing a left-to-right process:
  `Canonical source` -> `Patch smallest surface` -> `Run strict audit` ->
  `Run OpenClaw + openai_skill.py` -> `Run Plugin Eval` -> `Smoke/release eval`
  -> `Confidence report`.
- Include a small box titled `GOTCHAS` with:
  `Source is not runtime visibility`, `Cost warning is real`, `Blocked is not
  pass`, `Legacy headings may still be required`.
- Include a small box titled `PACKAGE SCOPE` with:
  `SKILL.md`, `references/`, `scripts/`, `assets/`, `examples/`, `templates/`,
  `fixtures/`.
- Include a bottom fact strip reading:
  `DID YOU KNOW? A passing audit is evidence, not proof of runtime behavior.`

Style:

- Professional engineering poster, dark ink and warm off-white technical-paper
  background.
- High-density but readable, like an illustrated reference chart.
- Use restrained amber, green, red, charcoal, and cream.
- Rounded panels with thin borders, not oversized empty cards.
- Crisp typography, clear hierarchy, no tiny unreadable filler.
- Include technical icons, document layers, gates, checkmarks, warning symbols,
  and trace arrows.
- Avoid fake dashboards, fake logos, fake metrics, sci-fi styling, glowing orbs,
  vague abstract blobs, or generic corporate gradients.
- 16:9 landscape, suitable for X/Twitter technical content.
- Make the infographic feel like a complete explanatory artifact, not a simple
  before/after slide.
